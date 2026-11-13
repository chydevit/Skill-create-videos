#!/usr/bin/env python3
"""Assemble rendered 3D shots into the finished film: flat-explainer post look, blob transitions, 2D overlays
(tags, portal), then mux with the narration/music mix and subtitle tracks of a 2D project.

  compose3d.py --project ~/Animation-new/<2d_project> --frames DIR --out film.mp4 [--fps 60]
      --shot fire_night 0 4.8 [--shot village_day 4.0 5.9 ...]   (name, start s, duration s; frames in DIR/<name>/)
      [--trans blob] [--xin 0.8] [--tag 1 "First Villages" 960 330 0.9]   (shot index, text, x, y, at s)
      [--portal 1 0 430 300 175 0.4]                                     (shot, inner shot, cx, cy, r, at)

The 2D project supplies: engine/explainer.py (labels, portal), build/mix.wav, subtitles/*.srt.
"""
import argparse
import glob
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image

W, H = 1920, 1080


def load(path, cache={}):
    if path not in cache:
        if len(cache) > 12:
            cache.clear()
        cache[path] = np.asarray(Image.open(path).convert("RGB")).astype(np.float32) / 255.0
    return cache[path]


_F = {}


def fields():
    if not _F:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dx, dy = (xx - W / 2) / (W / 2), (yy - H / 2) / (W / 2)
        _F["r"] = np.sqrt(dx * dx + dy * dy) / 1.16
        _F["th"] = np.arctan2(dy, dx)
        d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        _F["vig"] = 1 - np.clip((d - 0.6) * 0.55, 0, 0.32)[..., None]
        _F["grain"] = [np.random.default_rng(i).standard_normal((H, W, 1)).astype(np.float32) * 0.012
                       for i in range(4)]
    return _F


def blob_mask(p):
    F = fields()
    th = F["th"]
    wob = 1 + 0.16 * np.sin(5 * th + 7 * p) + 0.09 * np.sin(9 * th - 11 * p) + 0.05 * np.sin(17 * th + 3 * p)
    return np.clip((p * 1.3 * wob - F["r"]) / 0.01, 0, 1)[..., None]


def bloom(img, k=0.45):
    from scipy.ndimage import gaussian_filter
    lum = img @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    mask = np.clip((lum - 0.6) / 0.3, 0, 1)[..., None]
    small = (img * mask)[::4, ::4]
    g = np.stack([gaussian_filter(small[..., c], 6) for c in range(3)], -1)
    g = np.repeat(np.repeat(g, 4, 0), 4, 1)[:H, :W]
    return 1 - (1 - img) * (1 - np.clip(g * k, 0, 1))


def post(img, fi):
    F = fields()
    out = bloom(img) * F["vig"] + F["grain"][fi % 4]
    return np.clip(out, 0, 1)


def to_surface(img):
    import cairocffi as cairo
    a = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    buf = np.frombuffer(s.get_data(), np.uint8).reshape(H, s.get_stride() // 4, 4)
    buf[:, :W, 0], buf[:, :W, 1], buf[:, :W, 2], buf[:, :W, 3] = a[..., 2], a[..., 1], a[..., 0], 255
    s.mark_dirty()
    return s


def from_surface(s):
    s.flush()
    buf = np.frombuffer(s.get_data(), np.uint8).reshape(H, s.get_stride() // 4, 4)[:, :W]
    return np.dstack([buf[..., 2], buf[..., 1], buf[..., 0]]).astype(np.float32) / 255.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--frames", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--shot", nargs=3, action="append", required=True)
    ap.add_argument("--trans", default="blob")
    ap.add_argument("--xin", type=float, default=0.8)
    ap.add_argument("--fade-in", type=float, default=0.3)
    ap.add_argument("--fade-out", type=float, default=0.9)
    ap.add_argument("--tag", nargs=5, action="append", default=[])
    ap.add_argument("--portal", nargs=6, action="append", default=[])
    a = ap.parse_args()
    proj = os.path.abspath(os.path.expanduser(a.project))
    sys.path.insert(0, os.path.join(proj, "engine"))
    import cairocffi as cairo
    import explainer as E
    from film import draw_scene  # noqa: F401  (explainer.portal imports it lazily)

    shots = []
    for name, st, du in a.shot:
        fr = sorted(glob.glob(os.path.join(a.frames, name, "f_*.png")))
        if not fr:
            sys.exit("no frames for %s" % name)
        shots.append(dict(name=name, start=float(st), dur=float(du), frames=fr))
    total = max(s["start"] + s["dur"] for s in shots)
    nf = int(round(total * a.fps))

    def frame_of(s, t):
        i = int(round((t - s["start"]) * a.fps))
        return s["frames"][max(0, min(len(s["frames"]) - 1, i))]

    overs = {}
    for sh, text, x, y, at in a.tag:
        overs.setdefault(int(sh), []).append(E.tag(text, float(x), float(y), E.COL["magenta"], at=float(at), size=34))
    for sh, inner, cx, cy, r, at in a.portal:
        src = shots[int(inner)]
        loop = src["frames"][-int(2 * a.fps):]

        def inner_scene(src=src, loop=loop):
            def over(ctx, t, d):
                img = load(loop[int(t * a.fps) % len(loop)])
                ctx.set_source_surface(to_surface(img), 0, 0)
                ctx.paint()
            return dict(layers=[], over=over)
        overs.setdefault(int(sh), []).append(E.portal(inner_scene, float(cx), float(cy), float(r), at=float(at)))

    tmp = a.out + ".video.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", "%dx%d" % (W, H), "-r", str(a.fps), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "17", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for fi in range(nf):
        t = fi / a.fps
        img = None
        for k, s in enumerate(shots):
            if not (s["start"] - (a.xin if k else 0) <= t < s["start"] + s["dur"]):
                continue
            cur = load(frame_of(s, t))
            if overs.get(k):
                surf = to_surface(cur)
                ctx = cairo.Context(surf)
                for o in overs[k]:
                    ctx.save()
                    o(ctx, max(0.0, t - s["start"]), s["dur"])
                    ctx.restore()
                cur = from_surface(surf)
            if img is None or k == 0:
                img = cur
            else:
                p = (t - (s["start"] - a.xin)) / a.xin
                m = blob_mask(min(1.0, max(0.0, p))) if a.trans == "blob" else min(1.0, max(0.0, p))
                img = img * (1 - m) + cur * m
        if img is None:
            img = np.zeros((H, W, 3), np.float32)
        img = post(img, fi)
        if t < a.fade_in:
            img *= t / a.fade_in
        if total - t < a.fade_out:
            img *= max(0.0, (total - t) / a.fade_out)
        ff.stdin.write((np.clip(img, 0, 1) * 255).astype(np.uint8).tobytes())
        if fi % 60 == 0:
            print("  frame %d/%d" % (fi, nf), flush=True)
    ff.stdin.close()
    ff.wait()
    # mux: picture + the 2D project's mix + subtitle tracks
    mix = os.path.join(proj, "build", "mix.wav")
    subs = sorted(glob.glob(os.path.join(proj, "subtitles", "*.srt")))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-i", mix]
    for sp in subs:
        cmd += ["-i", sp]
    cmd += ["-map", "0:v", "-map", "1:a"] + sum([["-map", "%d:s" % (i + 2)] for i in range(len(subs))], [])
    cmd += ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-c:s", "mov_text"]
    for i, sp in enumerate(subs):
        lang = "khm" if sp.endswith("_km.srt") else "eng"
        cmd += ["-metadata:s:s:%d" % i, "language=%s" % lang]
    cmd += [a.out]
    subprocess.run(cmd, check=True)
    os.remove(tmp)
    print("[3d] %s  %.1fs  %d frames" % (a.out, total, nf))


if __name__ == "__main__":
    main()
