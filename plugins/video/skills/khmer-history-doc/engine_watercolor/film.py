"""Timeline + renderer.

A Scene exposes:
  layers : list of (cache_key, painter(ctx), depth)  painted once at SW x SH, cached as PNG
  dyn    : optional fn(ctx, t, d, depth) drawn after the layer of that depth, in set coordinates
  over   : optional fn(ctx, t, d) drawn in screen space (1920x1080) after the camera
Camera: dict(a=(cx, cy, z), b=(cx, cy, z), ease="io"); z=1 shows 1920 px of the 2400-wide set.
Transitions into a shot (shot["trans"]): "fade" (default), "ripple" (water rings), "lotus" (petals unfolding),
"ink" (spreading ink), "cut".
"""
import math
import os
import subprocess
import sys
import time

import cairocffi as cairo
import numpy as np

from core import CACHE, FPS, H, ROOT, SH, SW, W, clamp, ease, surface, np_to_surface, rng, src, value_noise

LAYER_DIR = os.path.join(CACHE, "layers")
_LAYERS = {}


def layer_surface(key, painter):
    if key in _LAYERS:
        return _LAYERS[key]
    os.makedirs(LAYER_DIR, exist_ok=True)
    path = os.path.join(LAYER_DIR, key + ".png")
    if os.path.exists(path):
        s = cairo.ImageSurface.create_from_png(path)
    else:
        s = surface(SW, SH)
        ctx = cairo.Context(s)
        painter(ctx)
        s.flush()
        tmp = path + ".%d.png" % os.getpid()
        s.write_to_png(tmp)
        os.replace(tmp, path)
    if len(_LAYERS) > 28:
        _LAYERS.clear()
    _LAYERS[key] = s
    return s


def cam_at(cam, p):
    a, b = cam.get("a", (SW / 2, SH / 2, 1.0)), cam.get("b", cam.get("a", (SW / 2, SH / 2, 1.0)))
    e = cam.get("ease", "io")
    q = ease(p) if e == "io" else (p if e == "lin" else 1 - (1 - p) ** 2)
    cx = a[0] + (b[0] - a[0]) * q
    cy = a[1] + (b[1] - a[1]) * q
    z = a[2] * (b[2] / a[2]) ** q
    return cx, cy, z


def apply_cam(ctx, cx, cy, z, depth):
    """Screen transform for a layer at depth (0 far .. 1 near)."""
    k = W / SW * 1.25
    par = 0.35 + 0.65 * depth
    zz = z ** (0.55 + 0.45 * depth)
    fx = SW / 2 + (cx - SW / 2) * par
    fy = SH / 2 + (cy - SH / 2) * par
    s = k * zz
    half_w, half_h = W / (2 * s), H / (2 * s)
    fx = min(max(fx, half_w), SW - half_w)
    fy = min(max(fy, half_h), SH - half_h)
    ctx.translate(W / 2, H / 2)
    ctx.scale(s, s)
    ctx.translate(-fx, -fy)


# ------------------------------------------------------------------ post FX (vignette, paper grain)
_POST = {}


def _post_assets():
    if _POST:
        return _POST
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    a = np.clip((d - 0.55) * 0.9, 0, 0.5)
    _POST["vig"] = np_to_surface(np.dstack([np.full((H, W, 3), 0.08, np.float32), a]))
    grains = []
    r = rng(5)
    for i in range(6):
        g = r.standard_normal((H // 2, W // 2)).astype(np.float32)
        al = np.clip(np.abs(g) * 0.04, 0, 0.1)
        col = (g > 0).astype(np.float32)
        grains.append(np_to_surface(np.dstack([col, col, col, al])))
    _POST["grain"] = grains
    # transition fields (half resolution)
    hh, ww = H // 2, W // 2
    y2, x2 = np.mgrid[0:hh, 0:ww].astype(np.float32)
    dx, dy = (x2 - ww / 2) / (ww / 2), (y2 - hh / 2) / (ww / 2)
    _POST["r"] = np.sqrt(dx * dx + dy * dy) / 1.16
    _POST["th"] = np.arctan2(dy, dx)
    n = value_noise(ww, hh, 5, 77, 5)
    n = (n - n.min()) / (n.max() - n.min())
    _POST["ink"] = np.clip(n * 0.75 + _POST["r"] * 0.25, 0, 1)
    R = rng(91)
    pts = np.concatenate([R.random((26, 2)) * [ww, hh], [[ww / 2, hh / 2]]])
    dd = np.sort(np.stack([np.hypot(x2 - px, y2 - py) for px, py in pts]), axis=0)
    edge = (dd[1] - dd[0]) / (ww * 0.06)
    _POST["crack"] = np.clip(_POST["r"] * 0.85 + np.clip(edge, 0, 1.4) * 0.55 + n * 0.12, 0, 2)
    _POST["crack_n"] = edge
    col = value_noise(ww, 1, 60, 33, 3)[0]
    col = (col - col.min()) / (col.max() - col.min())
    _POST["rain"] = np.clip(y2 / hh * 0.62 + col[None, :] * 0.42 + n * 0.08, 0, 1.2)
    # river current: a left-to-right flow front with wavy horizontal streaks
    row = value_noise(1, hh, 30, 44, 3)[:, 0]
    row = (row - row.min()) / (row.max() - row.min())
    lv = value_noise(1, hh, 18, 55, 3)[:, 0]
    lv = (lv - lv.min()) / (lv.max() - lv.min())
    _POST["bamboo"] = np.clip((1 - x2 / ww) * 0.72 + lv[:, None] * 0.22 + np.abs(np.sin(y2 / hh * 26)) * 0.05 + n * 0.04,
                              0, 1.2)
    # incense smoke: soft curling plumes rising from the bottom edge
    sw = np.abs(np.sin(x2 / ww * 7.5 + n * 5.0 + y2 / hh * 2.2))
    _POST["incense"] = np.clip((1 - y2 / hh) * 0.6 + sw * 0.24 + n * 0.22, 0, 1.2)
    _POST["river"] = np.clip(x2 / ww * 0.7 + row[:, None] * 0.25 + np.sin(y2 / hh * 40) * 0.02 + n * 0.06, 0, 1.2)
    return _POST


def post(ctx, fi, grain=1.0, vignette=1.0, paper=1.0):
    A = _post_assets()
    if paper:
        import wc
        wc.paper_overlay(ctx, paper)
    if vignette:
        ctx.set_source_surface(A["vig"], 0, 0)
        ctx.paint_with_alpha(vignette)
    if grain:
        ctx.save()
        ctx.scale(2, 2)
        ctx.set_source_surface(A["grain"][fi % 6], 0, 0)
        ctx.paint_with_alpha(grain)
        ctx.restore()


def trans_mask(kind, p):
    """Half-resolution alpha mask surface for transition progress p (0..1)."""
    A = _post_assets()
    if kind == "ripple":
        f = A["r"] - p * 1.15
        m = np.clip(-f / 0.05, 0, 1)
    elif kind == "lotus":
        th = A["th"]
        petal = 0.55 + 0.45 * np.abs(np.cos(4 * (th + p * 0.8))) ** 0.6
        f = A["r"] / np.maximum(petal, 1e-3) - p * 1.25
        m = np.clip(-f / 0.04, 0, 1)
    elif kind == "ink":
        f = A["ink"] - p * 1.1
        m = np.clip(-f / 0.03, 0, 1)
    elif kind == "crack":
        f = A["crack"] - p * 1.75
        m = np.clip(-f / 0.025, 0, 1)
    elif kind in ("rain", "river", "bamboo", "incense"):
        f = A[kind] - p * 1.3
        m = np.clip(-f / 0.05, 0, 1)
    else:
        m = np.full(A["r"].shape, p, np.float32)
    z = np.zeros(m.shape + (3,), np.float32)
    return np_to_surface(np.dstack([z, m.astype(np.float32)]))


def _edge_surface(kind, p, color, width):
    A = _post_assets()
    f = A[kind] - p * (1.75 if kind == "crack" else 1.3)
    a = np.clip(1 - np.abs(f) / width, 0, 1) ** 1.5
    if kind == "bamboo":   # leafy fringe: dark-green bands along the sweep front
        a = np.clip(1 - np.abs(f - 0.03) / width, 0, 1) * (0.6 + 0.4 * np.abs(np.sin(A["th"] * 9 + f * 60)))
    if kind == "crack":
        seam = np.clip(1 - A["crack_n"] / 0.05, 0, 1) * np.clip(1 - np.abs(f - 0.12) / 0.2, 0, 1)
        a = np.maximum(a * 0.8, seam)
    c = np.ones(a.shape + (3,), np.float32) * np.array(color, np.float32)
    return np_to_surface(np.dstack([c, (a * (1 - p) ** 0.5).astype(np.float32)]))


def _trans_fx(ctx, kind, p):
    """Decoration on the transition edge (ripple rings, crack seams, rain or river fringe)."""
    if kind in ("crack", "rain", "river", "bamboo", "incense"):
        col = {"crack": (0.95, 0.78, 0.36), "rain": (0.80, 0.86, 0.90), "river": (0.80, 0.68, 0.42),
               "bamboo": (0.30, 0.42, 0.18), "incense": (0.90, 0.87, 0.82)}[kind]
        ctx.save()
        ctx.scale(2, 2)
        ctx.set_source_surface(_edge_surface(kind, p, col, 0.02 if kind == "crack" else 0.08 if kind == "bamboo" else 0.12 if kind == "incense" else 0.05),
                               0, 0)
        ctx.paint_with_alpha(0.95 if kind in ("crack", "bamboo") else 0.6)
        ctx.restore()
        return
    if kind == "ripple":
        for k in range(3):
            r = (p * 1.15 - k * 0.06) * W * 0.58
            if r <= 0:
                continue
            src(ctx, "#f4e6c8", 0.35 * (1 - p) * (1 - k * 0.3))
            ctx.set_line_width(6 - k * 1.5)
            ctx.save()
            ctx.translate(W / 2, H / 2)
            ctx.scale(1, 0.98)
            ctx.arc(0, 0, r, 0, 2 * math.pi)
            ctx.restore()
            ctx.stroke()


# ------------------------------------------------------------------ shot drawing
def draw_scene(ctx, scene, t, d, cam):
    p = clamp(t / d) if d > 0 else 0
    cx, cy, z = cam_at(cam, p)
    layers = scene.get("layers", [])
    depths = sorted(set([dp for (_, _, dp) in layers] + list(scene.get("dyn_depths", []))))
    for dp in depths:
        ctx.save()
        apply_cam(ctx, cx, cy, z, dp)
        for (key, painter, ld) in layers:
            if ld == dp:
                s = layer_surface(key, painter)
                ctx.set_source_surface(s, 0, 0)
                ctx.get_source().set_filter(cairo.FILTER_GOOD)
                ctx.paint()
        if scene.get("dyn"):
            scene["dyn"](ctx, t, d, dp)
        ctx.restore()
    if scene.get("over"):
        scene["over"](ctx, t, d)


class Timeline:
    def __init__(self, shots, cues=None, burn=True, mouth=None):
        self.shots = shots
        self.cues = cues or []
        self.burn = burn
        self.total = max(s["start"] + s["dur"] for s in shots)
        self._scene_cache = {}

    def scene(self, i):
        if i not in self._scene_cache:
            if len(self._scene_cache) > 3:
                self._scene_cache.clear()
            self._scene_cache[i] = self.shots[i]["make"]()
        return self._scene_cache[i]

    def active(self, t):
        return [i for i, s in enumerate(self.shots) if s["start"] - s.get("xin", 0) <= t < s["start"] + s["dur"]]

    def render_frame(self, ctx, fi):
        from cards import draw_badge, draw_subtitle, black
        t = fi / FPS
        black(ctx)
        for i in self.active(t):
            s = self.shots[i]
            lt = t - s["start"]
            kind = s.get("trans") or "fade"
            alpha = 1.0
            masked = None
            if lt < 0:
                p = clamp((lt + s["xin"]) / s["xin"])
                if kind in ("ripple", "lotus", "ink", "crack", "rain", "river", "bamboo", "incense"):
                    masked = ease(p)
                else:
                    alpha = p
            elif s.get("fade_in") and lt < s["fade_in"]:
                alpha = clamp(lt / s["fade_in"])
            if s.get("fade_out") and s["dur"] - lt < s["fade_out"]:
                alpha = min(alpha, clamp((s["dur"] - lt) / s["fade_out"]))
            sc = self.scene(i)
            grouped = alpha < 0.999 or masked is not None
            if grouped:
                ctx.push_group()
            draw_scene(ctx, sc, max(lt, 0), s["dur"], s["cam"])
            if s.get("badge"):
                draw_badge(ctx, s["badge"], lt, s["dur"], s.get("badge_note"))
            if grouped:
                ctx.pop_group_to_source()
                if masked is not None:
                    m = trans_mask(kind, masked)
                    ctx.save()
                    ctx.scale(2, 2)
                    ctx.mask_surface(m, 0, 0)
                    ctx.restore()
                    _trans_fx(ctx, kind, masked)
                else:
                    ctx.paint_with_alpha(alpha)
        post(ctx, fi, grain=0.35, vignette=0.6, paper=1.0)
        if self.burn:
            for c in self.cues:
                if c["start"] <= t < c["end"]:
                    draw_subtitle(ctx, c, t)


# ------------------------------------------------------------------ parallel encode
def _render_chunk(args):
    script_mod, f0, f1, out, burn = args
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    sys.path.insert(0, ROOT)
    import importlib
    mod = importlib.import_module(script_mod)
    tl = mod.timeline(burn=burn)
    s = surface(W, H)
    ctx = cairo.Context(s)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", "%dx%d" % (W, H),
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
           "-tune", "film", out + ".tmp.mp4"]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        ctx.save()
        tl.render_frame(ctx, fi)
        ctx.restore()
        s.flush()
        p.stdin.write(bytes(s.get_data()))
    p.stdin.close()
    p.wait()
    os.replace(out + ".tmp.mp4", out)
    return out


def render(script_mod, out_path, chunk_dir, total_frames, workers=8, chunk=240, burn=True):
    from multiprocessing import Pool
    os.makedirs(chunk_dir, exist_ok=True)
    jobs = []
    for f0 in range(0, total_frames, chunk):
        f1 = min(total_frames, f0 + chunk)
        jobs.append((script_mod, f0, f1, os.path.join(chunk_dir, "c%06d_%06d.mp4" % (f0, f1)), burn))
    todo = [j for j in jobs if not os.path.exists(j[3])]
    t0 = time.time()
    print("chunks: %d (%d to render)" % (len(jobs), len(todo)), flush=True)
    with Pool(workers) as pool:
        for k, o in enumerate(pool.imap_unordered(_render_chunk, todo)):
            print("  [%d/%d] %s  %.0fs" % (k + 1, len(todo), os.path.basename(o), time.time() - t0), flush=True)
    lst = os.path.join(chunk_dir, "list.txt")
    with open(lst, "w") as f:
        for j in jobs:
            f.write("file '%s'\n" % os.path.abspath(j[3]))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    out_path], check=True)
    return out_path


def still(script_mod, t, out_png, burn=True):
    sys.path.insert(0, ROOT)
    import importlib
    mod = importlib.import_module(script_mod)
    tl = mod.timeline(burn=burn)
    s = surface(W, H)
    ctx = cairo.Context(s)
    tl.render_frame(ctx, int(t * FPS))
    s.write_to_png(out_png)
