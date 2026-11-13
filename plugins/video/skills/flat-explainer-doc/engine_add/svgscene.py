"""SVG scenes for the flat explainer look.

An SVG set is 2400x1350 (viewBox "0 0 2400 1350", same as SW x SH). Top-level <g> groups are parallax layers:

    <g id="bg">   depth 0.00   sky, gradients, stars
    <g id="far">  depth 0.25   distant hills, sun/moon
    <g id="mid">  depth 0.50   architecture, the story setting
    <g id="near"> depth 0.60   ground the characters stand on
    <g id="char"> depth 0.70   characters
    <g id="front">depth 0.92   dark foreground framing (plants, rocks)
    <g id="fx">   depth 1.00   sparks, particles, light beams
  any other top-level group needs data-depth="0..1".

Animated sprites: any element with data-anim="..." (space-separated, combinable) is cut out of its layer, rendered
once, and moved every frame:
    bob      data-amp=8 data-period=1.6          up/down
    sway     data-deg=4 data-period=3            rotate around the pivot (default: bottom-centre)
    pulse    data-amp=0.05 data-period=1.2       scale around the pivot (default: centre)
    flicker  data-amp=0.25                        fire / torch light: alpha + scale jitter
    spin     data-speed=20                        degrees per second
    drift    data-dx=0 data-dy=0                  move by (dx, dy) over the shot
    walk     data-dx=300                          drift + footstep bob
    appear   data-at=0.4                          pop in (overshoot) at t seconds
    fadein   data-at=0.4                          fade in at t seconds
    fadeout  data-at=3.0                          fade out at t seconds
    window   data-t0=0 data-t1=2.5                visible only between t0 and t1 (0.12 s cross-fade)
    emit     data-n=14 data-life=1.6 data-vy=160 data-spread=40   particle emitter: copies of the element rise,
             drift and fade in a loop (torch / fire sparks, dust, bubbles)
  data-pivot="x,y" (canvas px) overrides the pivot. data-phase=0..1 offsets cycles.
  Nested data-anim elements move with their parent and are not animated on their own.

Reusable characters / props: <g data-include="chars/guide.svg" data-x=1200 data-y=1100 data-h=420
    data-pose="point" data-flip="1" data-swap="#aa0000:#00aa00,#111:#222" data-anim="bob"/>
  data-poses="back@0 torch@1.2 point@3" sequences poses over the shot (cut-out animation, 0.12 s cross-fades).
  The file is inlined, bottom-centre anchored at (x, y), scaled to height h.  Children with id "pose-*" are
  alternatives: only data-pose is kept (default: the first).  Same for "face-*" with data-face.

Look effects (any element; it becomes its own cached sprite, motion optional):
    data-blur="18"                     soft edge (Gaussian, set px)  - glows, light pools, cast shadows
    data-blend="add|screen|multiply|overlay"   how it combines with what is below (glow = add/screen)
    data-rim="#ffb347" data-rim-w="6"  rim light: a coloured band on the silhouette edge facing the light
    data-rim-a="0.95"                  rim opacity
  2.5D:  data-depth="0.8" on any element puts it on its own parallax plane (crowds at many depths);
         root data-haze="#c9b8ff 0.5" tints far layers toward the sky (atmospheric perspective);
         root data-light-depth="0.7" is the plane the key light lives on (darkness hole follows it).
  Root attributes:  data-dark="#0b0418 0.78 1200"  local-light darkness: everything beyond `radius` set-px from
                    the light sinks into colour at alpha (the reference's torch/fire night look)
                    data-dark-lights="570,560,700@1.4"  extra light holes (x,y,radius@start s)
                    data-dark-reveal="1.8"  opening reveal: darkness starts total and opens over N seconds
                    data-light="x,y"  key light position (default: top-left 300,0) for all rims
                    data-rim-chars="#ffb347"  give every data-include character this rim automatically

svg_scene(path, swap=None, over=None) returns the engine scene dict.  `swap` recolours the whole file
({"#hex": "#hex"}) which is how one set gets day / dusk / night variants.
"""
import copy
import hashlib
import io
import json
import math
import os
import re
import xml.etree.ElementTree as ET

import cairocffi as cairo
import numpy as np

from core import CACHE, ROOT, SH, SW, clamp, np_to_surface

SVG_NS = "http://www.w3.org/2000/svg"
XL_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XL_NS)
DEPTH = {"bg": 0.0, "far": 0.25, "mid": 0.5, "near": 0.6, "char": 0.7, "front": 0.92, "fx": 1.0}
SVG_DIR = os.path.join(CACHE, "svg")
try:
    import depth as _DEPTH   # 2.5D camera state (depth of field radius for the layer being drawn)
except ImportError:
    _DEPTH = None
FX_VERSION = "fx5"   # bump when rendering code changes so cached layers are rebuilt


def _tag(e):
    return e.tag.split("}")[-1]


def _resolve(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def recolor(text, swap):
    if not swap:
        return text
    for a, b in swap.items():
        text = re.sub(re.escape(a) + r"(?![0-9a-fA-F])", b, text, flags=re.I)
    return text


def _parse_swap(s):
    out = {}
    for pair in (s or "").split(","):
        if ":" in pair:
            a, b = pair.split(":", 1)
            out[a.strip()] = b.strip()
    return out


def _expand_poses(el):
    """data-poses="a@0 b@1.5" -> one include per pose, each with a visibility window."""
    for i, child in reversed(list(enumerate(list(el)))):
        seq = child.get("data-poses")
        if not seq:
            continue
        keys = []
        for tok in seq.split():
            name, _, at = tok.partition("@")
            keys.append((name, float(at or 0)))
        el.remove(child)
        for j, (name, t0) in enumerate(keys):
            c = copy.deepcopy(child)
            c.attrib.pop("data-poses", None)
            c.set("data-pose", name)
            c.set("data-anim", ((c.get("data-anim") or "") + " window").strip())
            c.set("data-t0", "%g" % t0)
            c.set("data-t1", "%g" % (keys[j + 1][1] if j + 1 < len(keys) else 1e9))
            el.insert(i + j, c)


def _include(el, depth=0):
    """Inline data-include files (recursively)."""
    _expand_poses(el)
    for child in list(el):
        _include(child, depth)
        inc = child.get("data-include")
        if not inc or depth > 4:
            continue
        txt = recolor(open(_resolve(inc)).read(), _parse_swap(child.get("data-swap")))
        sub = ET.fromstring(txt)
        vb = [float(v) for v in sub.get("viewBox", "0 0 1000 1000").split()]
        vw, vh = vb[2], vb[3]
        x, y = float(child.get("data-x", 0)), float(child.get("data-y", 0))
        h = float(child.get("data-h", vh))
        s = h / vh
        flip = child.get("data-flip") in ("1", "true", "yes")
        sx = -s if flip else s
        tx = x + (vw * s / 2 if flip else -vw * s / 2) - vb[0] * sx
        ty = y - vh * s - vb[1] * s
        tr = "translate(%.2f %.2f) scale(%.4f %.4f)" % (tx, ty, sx, s)
        if child.get("transform"):
            tr = child.get("transform") + " " + tr
        pose, face = child.get("data-pose"), child.get("data-face")
        kids = list(sub)
        for prefix, want in (("pose-", pose), ("face-", face)):
            alts = [k for k in kids if (k.get("id") or "").startswith(prefix)]
            if alts:
                keep = next((k for k in alts if k.get("id") == prefix + (want or "")), alts[0])
                kids = [k for k in kids if k not in alts or k is keep]
        for k in ("data-include", "data-x", "data-y", "data-h", "data-pose", "data-face", "data-flip", "data-swap"):
            child.attrib.pop(k, None)
        child.tag = "{%s}g" % SVG_NS
        child.set("data-included", "1")
        child.set("transform", tr)
        for k in kids:
            child.append(copy.deepcopy(k))
        _include(child, depth + 1)


FX_KEYS = ("data-anim", "data-blur", "data-blend", "data-rim", "data-depth")


def _is_sprite(e):
    return any(e.get(k) for k in FX_KEYS)


def _anim_nodes(layer):
    """sprite elements (motion or look effects) that are not inside another sprite element."""
    out = []

    def walk(e):
        for c in e:
            if _is_sprite(c):
                out.append(c)
            else:
                walk(c)
    walk(layer)
    return out


def _hex_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def _apply_fx(im, bb, fx):
    """im: full-canvas RGBA PIL image. Returns (cropped image, bbox) with rim / blur applied."""
    from PIL import ImageFilter
    blur = float(fx.get("blur") or 0)
    rim = fx.get("rim")
    pad = int(blur * 3 + (float(fx.get("rim_w", 6)) + 2 if rim else 0)) + 2
    x0, y0 = max(0, bb[0] - pad), max(0, bb[1] - pad)
    x1, y1 = min(SW, bb[2] + pad), min(SH, bb[3] + pad)
    im = im.crop((x0, y0, x1, y1))
    if rim:
        a = np.asarray(im).astype(np.float32) / 255.0
        al = a[..., 3]
        w = float(fx.get("rim_w", 6))
        lx, ly = fx["light"]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = lx - cx, ly - cy
        n = math.hypot(dx, dy) or 1.0
        sx, sy = int(round(dx / n * w)), int(round(dy / n * w))
        sh = np.zeros_like(al)
        hh, ww = al.shape
        ys, yd = (slice(sy, hh), slice(0, hh - sy)) if sy >= 0 else (slice(0, hh + sy), slice(-sy, hh))
        xs, xd = (slice(sx, ww), slice(0, ww - sx)) if sx >= 0 else (slice(0, ww + sx), slice(-sx, ww))
        sh[yd, xd] = al[ys, xs]           # alpha of the neighbour toward the light
        band = np.clip(al - sh, 0, 1) * float(fx.get("rim_a", 0.95))
        col = _hex_rgb(rim) / 255.0
        a[..., :3] = a[..., :3] * (1 - band[..., None]) + col * band[..., None]
        from PIL import Image
        im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), "RGBA")
    if fx.get("haze"):
        from PIL import Image
        hc, amt = fx["haze"]
        a = np.asarray(im).astype(np.float32) / 255.0
        a[..., :3] = a[..., :3] * (1 - amt) + (_hex_rgb(hc) / 255.0) * amt
        im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), "RGBA")
    if blur:
        # blur premultiplied colour so edges do not darken
        a = np.asarray(im).astype(np.float32) / 255.0
        from PIL import Image
        pm = np.dstack([a[..., :3] * a[..., 3:4], a[..., 3]])
        chans = [Image.fromarray((pm[..., i] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
                 for i in range(4)]
        pm = np.dstack([np.asarray(c).astype(np.float32) / 255.0 for c in chans])
        al = pm[..., 3:4]
        rgb = np.where(al > 1e-4, pm[..., :3] / np.maximum(al, 1e-4), 0)
        im = Image.fromarray((np.clip(np.dstack([rgb, al]), 0, 1) * 255).astype(np.uint8), "RGBA")
    return im, (x0, y0, x1, y1)


def _render(root, key, fx=None):
    """Render an ElementTree root to an RGBA surface cropped to its alpha bbox (+ look effects). Cached on disk."""
    os.makedirs(SVG_DIR, exist_ok=True)
    png, meta = os.path.join(SVG_DIR, key + ".png"), os.path.join(SVG_DIR, key + ".json")
    if not (os.path.exists(png) and os.path.exists(meta)):
        import cairosvg
        from PIL import Image
        data = ET.tostring(root)
        raw = cairosvg.svg2png(bytestring=data, output_width=SW, output_height=SH)
        im = Image.open(io.BytesIO(raw)).convert("RGBA")
        bb = im.getchannel("A").getbbox() or (0, 0, 1, 1)
        if fx and (fx.get("blur") or fx.get("rim") or fx.get("haze")):
            im, bb = _apply_fx(im, bb, fx)
        else:
            im = im.crop(bb)
        tmp = png + ".%d.png" % os.getpid()
        im.save(tmp)
        os.replace(tmp, png)
        json.dump(dict(x=bb[0], y=bb[1], w=bb[2] - bb[0], h=bb[3] - bb[1]), open(meta, "w"))
    m = json.load(open(meta))
    return cairo.ImageSurface.create_from_png(png), m


def _prune_to(root, target_id):
    """Copy of root keeping <defs>, and only the ancestor chain + subtree of the element with data-sid=target_id."""
    r = copy.deepcopy(root)

    def keep(e):
        if e.get("data-sid") == target_id:
            return True
        hit = False
        for c in list(e):
            if _tag(c) == "defs":
                continue
            if keep(c):
                hit = True
            else:
                e.remove(c)
        return hit
    keep(r)
    return r


def _strip_anims(e):
    for c in list(e):
        if _is_sprite(c):
            e.remove(c)
        else:
            _strip_anims(c)


def _f(e, k, d):
    try:
        return float(e.get(k, d))
    except ValueError:
        return d


def _back_out(p):
    p = clamp(p)
    c = 1.70158
    return 1 + (c + 1) * (p - 1) ** 3 + c * (p - 1) ** 2


def _motion(spec, t, d):
    """-> dx, dy, rot (deg), scale, alpha."""
    dx = dy = rot = 0.0
    sc, al = 1.0, 1.0
    ph = spec["phase"] * 2 * math.pi
    p = clamp(t / d) if d > 0 else 0.0
    for kind in spec["kinds"]:
        e = spec["el"]
        if kind == "bob":
            dy += math.sin(2 * math.pi * t / _f(e, "data-period", 1.6) + ph) * _f(e, "data-amp", 8)
        elif kind == "sway":
            rot += math.sin(2 * math.pi * t / _f(e, "data-period", 3.0) + ph) * _f(e, "data-deg", 4)
        elif kind == "pulse":
            sc *= 1 + math.sin(2 * math.pi * t / _f(e, "data-period", 1.2) + ph) * _f(e, "data-amp", 0.05)
        elif kind == "flicker":
            a = _f(e, "data-amp", 0.25)
            n = (math.sin(t * 13.1 + ph) + math.sin(t * 7.3 + 2 * ph) * 0.6 + math.sin(t * 23.7) * 0.3) / 1.9
            al *= 1 - a * (0.5 + 0.5 * n)
            sc *= 1 + 0.05 * n
        elif kind == "spin":
            rot += _f(e, "data-speed", 20) * t
        elif kind == "drift":
            dx += _f(e, "data-dx", 0) * p
            dy += _f(e, "data-dy", 0) * p
        elif kind == "walk":
            dx += _f(e, "data-dx", 300) * p
            dy -= abs(math.sin(2 * math.pi * t / _f(e, "data-period", 0.9) + ph)) * _f(e, "data-amp", 6)
        elif kind == "appear":
            q = (t - _f(e, "data-at", 0.3)) / 0.45
            sc *= max(0.0, _back_out(q)) if q < 1 else 1.0
            al *= clamp(q * 3)
        elif kind == "fadein":
            al *= clamp((t - _f(e, "data-at", 0.3)) / 0.5)
        elif kind == "fadeout":
            al *= 1 - clamp((t - _f(e, "data-at", 3.0)) / 0.5)
        elif kind == "window":
            t0, t1 = _f(e, "data-t0", 0), _f(e, "data-t1", 1e9)
            al *= (clamp((t - t0) / 0.12 + 0.5) if t0 > 0 else 1.0) * (1 - clamp((t - t1) / 0.12 + 0.5))
    return dx, dy, rot, sc, al


def _fx_of(e, light, haze=None):
    lt = e.get("data-light")
    return dict(blur=e.get("data-blur"), rim=e.get("data-rim"), rim_w=_f(e, "data-rim-w", 6),
                rim_a=_f(e, "data-rim-a", 0.95), blend=e.get("data-blend"), haze=haze,
                light=tuple(float(v) for v in lt.split(",")) if lt else light)


def _haze_for(root, depth):
    """Atmospheric perspective: data-haze="#c9b8ff 0.55" tints far layers toward the sky colour."""
    spec = root.get("data-haze")
    if not spec:
        return None
    col, _, k = spec.partition(" ")
    amt = float(k or 0.5) * (1 - depth) ** 1.6
    return (col, amt) if amt > 0.01 else None


BLEND = {"add": cairo.OPERATOR_ADD, "screen": cairo.OPERATOR_SCREEN, "multiply": cairo.OPERATOR_MULTIPLY,
         "overlay": cairo.OPERATOR_OVERLAY, "soft": cairo.OPERATOR_SOFT_LIGHT}


def _emit(ctx, sp, s, m, t, al):
    e = sp["el"]
    n, life = int(_f(e, "data-n", 14)), _f(e, "data-life", 1.6)
    vy, spread = _f(e, "data-vy", 160), _f(e, "data-spread", 40)
    cx, cy = m["x"] + m["w"] / 2, m["y"] + m["h"] / 2
    for i in range(n):
        age = (t / life + i / n + sp["phase"]) % 1.0
        hx = math.sin(i * 12.9898) * 0.5 + math.sin(i * 4.1414) * 0.5
        x = cx + hx * spread * (0.3 + age) + math.sin(t * 3 + i) * 6
        y = cy - vy * life * age
        a = al * (1 - age) * min(1.0, age * 6)
        k = 1 - 0.55 * age
        if a <= 0.01:
            continue
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(k, k)
        ctx.translate(-cx, -cy)
        ctx.set_source_surface(s, m["x"], m["y"])
        if sp["fx"].get("blend") in BLEND:
            ctx.set_operator(BLEND[sp["fx"]["blend"]])
        ctx.paint_with_alpha(a)
        ctx.restore()


def _darkness(root, light):
    """Local-light darkness: a dark veil with soft holes at the key light and any data-dark-lights
    ("x,y,radius[@t0] ..." - e.g. a torch that lights at 1.4 s)."""
    spec = root.get("data-dark")
    if not spec:
        return None
    parts = spec.split()
    col = _hex_rgb(parts[0]) / 255.0
    alpha = float(parts[1]) if len(parts) > 1 else 0.75
    rad = float(parts[2]) if len(parts) > 2 else 1100
    reveal = float(root.get("data-dark-reveal") or 0)
    lights = [(light[0], light[1], rad, 0.0)]
    for tok in (root.get("data-dark-lights") or "").split():
        xyz, _, t0 = tok.partition("@")
        x, y, r = (float(v) for v in xyz.split(","))
        lights.append((x, y, r, float(t0 or 0)))

    def draw(ctx, t):
        q = clamp(t / reveal) if reveal else 1.0
        q = q * q * (3 - 2 * q)
        a_out = alpha + (1 - alpha) * (1 - q)
        ctx.push_group()
        ctx.set_source_rgba(col[0], col[1], col[2], a_out)
        ctx.rectangle(-SW, -SH, SW * 3, SH * 3)
        ctx.fill()
        ctx.set_operator(cairo.OPERATOR_DEST_OUT)
        for i, (x, y, r0, t0) in enumerate(lights):
            on = clamp((t - t0) / 0.5) if t0 > 0 else 1.0
            if on <= 0:
                continue
            grow = (0.08 + 0.92 * q) if i == 0 else (0.3 + 0.7 * on)
            r = r0 * grow * (1 + 0.015 * math.sin(t * 11 + i) + 0.01 * math.sin(t * 17 + 2 * i))
            g = cairo.RadialGradient(x, y, r * 0.1, x, y, r)
            g.add_color_stop_rgba(0, 0, 0, 0, on)
            g.add_color_stop_rgba(0.5, 0, 0, 0, 0.65 * on)
            g.add_color_stop_rgba(1, 0, 0, 0, 0)
            ctx.set_source(g)
            ctx.arc(x, y, r, 0, 2 * math.pi)
            ctx.fill()
        ctx.pop_group_to_source()
        ctx.paint()
    return draw


def svg_scene(path, swap=None, over=None, dyn=None):
    """Load an SVG set -> scene dict (layers cached per group, animated sprites drawn in dyn)."""
    txt = recolor(open(_resolve(path)).read(), swap)
    root = ET.fromstring(txt)
    _include(root)
    lt = root.get("data-light")
    light = tuple(float(v) for v in lt.split(",")) if lt else (300.0, 0.0)
    rc = root.get("data-rim-chars")
    if rc:
        for e in root.iter():
            if e.get("data-included") and not e.get("data-rim") and e.get("data-rim-off") is None:
                e.set("data-rim", rc)
    base = hashlib.sha1(ET.tostring(root) + FX_VERSION.encode()).hexdigest()[:16]
    groups = [c for c in root if _tag(c) == "g"]
    sid = 0
    plan = []
    for g in groups:
        gid = g.get("id", "")
        depth = float(g.get("data-depth", DEPTH.get(gid, 0.5)))
        anims = _anim_nodes(g)
        for a in anims:
            sid += 1
            a.set("data-sid", "s%d" % sid)
        plan.append((g, gid, depth, anims))

    layers, sprites = [], {}
    for li, (g, gid, depth, anims) in enumerate(plan):
        # static part of this layer
        r = copy.deepcopy(root)
        keep_idx = list(root).index(g)
        kept = list(r)[keep_idx]
        for i, c in reversed(list(enumerate(list(r)))):
            if _tag(c) == "g" and i != keep_idx:
                r.remove(c)
        _strip_anims(kept)      # nested sprites only; the layer's own fx (blur/blend/rim) apply to the layer
        key = "%s_L%d" % (base, li)
        lfx = _fx_of(g, light, _haze_for(root, depth))

        def painter(ctx, r=r, key=key, lfx=lfx):
            s, m = _render(r, key, lfx)
            ctx.set_source_surface(s, m["x"], m["y"])
            if lfx.get("blend") in BLEND:
                ctx.set_operator(BLEND[lfx["blend"]])
            ctx.paint()
        layers.append(("svg_" + key, painter, depth))
        for a in anims:
            kinds = (a.get("data-anim") or "").split()
            ph = a.get("data-phase")
            phase = float(ph) if ph else (int(hashlib.md5(a.get("data-sid").encode()).hexdigest()[:4], 16) % 1000) / 1000
            sd = float(a.get("data-depth", depth))     # per-object depth (2.5D): its own parallax plane
            sprites.setdefault(sd, []).append(dict(
                el=a, kinds=kinds, phase=phase, key="%s_%s" % (base, a.get("data-sid")),
                root=_prune_to(root, a.get("data-sid")), pivot=a.get("data-pivot"),
                fx=_fx_of(a, light, _haze_for(root, sd))))

    dark = _darkness(root, light)
    top_depth = max([p[2] for p in plan] + list(sprites.keys()) + [0.0])

    light_depth = float(root.get("data-light-depth", 0.7))
    mats = {}

    def _dyn(ctx, t, d, depth):
        mats[depth] = ctx.get_matrix()
        _dyn_sprites(ctx, t, d, depth)
        if dark and depth == top_depth:
            # draw the veil in the light's own plane so the hole stays on the fire during dolly / parallax moves
            near = min(mats, key=lambda k: abs(k - light_depth))
            ctx.save()
            ctx.set_matrix(mats[near])
            dark(ctx, t)
            ctx.restore()

    def _dyn_sprites(ctx, t, d, depth):
        for sp in sprites.get(depth, []):
            if "surf" not in sp:
                sp["surf"], sp["m"] = _render(sp["root"], sp["key"], sp["fx"])
            s, m = sp["surf"], sp["m"]
            dx, dy, rot, sc, al = _motion(sp, t, d)
            if al <= 0.003 or sc <= 0.001:
                continue
            if "emit" in sp["kinds"]:
                _emit(ctx, sp, s, m, t, al)
                continue
            if sp["pivot"]:
                px, py = [float(v) for v in sp["pivot"].split(",")]
            elif any(k in sp["kinds"] for k in ("pulse", "spin", "appear", "flicker")):
                px, py = m["x"] + m["w"] / 2, m["y"] + m["h"] / 2
            else:
                px, py = m["x"] + m["w"] / 2, m["y"] + m["h"]
            ctx.save()
            ctx.translate(px + dx, py + dy)
            if rot:
                ctx.rotate(math.radians(rot))
            if sc != 1.0:
                ctx.scale(sc, sc)
            ctx.translate(-px, -py)
            br = _DEPTH.STATE["blur"] if _DEPTH else 0
            if br:
                s2, pad = _DEPTH.blurred_pad(s, br, sp["key"])
                ctx.set_source_surface(s2, m["x"] - pad, m["y"] - pad)
            else:
                ctx.set_source_surface(s, m["x"], m["y"])
            ctx.get_source().set_filter(cairo.FILTER_GOOD)
            if sp["fx"].get("blend") in BLEND:
                ctx.set_operator(BLEND[sp["fx"]["blend"]])
            ctx.paint_with_alpha(al)
            ctx.restore()
        if dyn:
            dyn(ctx, t, d, depth)

    sc = dict(layers=layers, dyn=_dyn, dyn_depths=sorted(set(list(sprites.keys()) + [p[2] for p in plan])))
    if over:
        sc["over"] = over
    return sc


_IMGS = {}


def svg_image(path, width, swap=None):
    """Render a whole SVG file (any viewBox) to a surface `width` px wide (icons, maps, inserts). Cached."""
    mk = (path, int(width), tuple(sorted((swap or {}).items())))
    if mk not in _IMGS:
        _IMGS[mk] = _svg_image(path, width, swap)
    return _IMGS[mk]


def _svg_image(path, width, swap=None):
    txt = recolor(open(_resolve(path)).read(), swap)
    root = ET.fromstring(txt)
    _include(root)
    key = hashlib.sha1(ET.tostring(root) + str(width).encode()).hexdigest()[:18]
    os.makedirs(SVG_DIR, exist_ok=True)
    png = os.path.join(SVG_DIR, "img_" + key + ".png")
    if not os.path.exists(png):
        import cairosvg
        cairosvg.svg2png(bytestring=ET.tostring(root), write_to=png + ".tmp", output_width=int(width))
        os.replace(png + ".tmp", png)
    return cairo.ImageSurface.create_from_png(png)


def svg_attr(path, name, default=None):
    m = re.search(r'%s="([^"]*)"' % re.escape(name), open(_resolve(path)).read())
    return m.group(1) if m else default
