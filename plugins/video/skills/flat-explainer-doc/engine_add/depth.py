"""2.5D camera for SVG sets: perspective dolly, depth of field (with rack focus) - installed over film.draw_scene.

Camera dict extras (all optional; without them the original flat parallax camera is used):
    dolly=(c0, c1)        camera travels forward from c0 to c1 (depth units, 0..~0.9). Each layer sits at distance
                          D = 1 + (1 - depth) * SPREAD; its scale is D / (D - c), so near layers rush toward the
                          lens while far ones barely move. Layers closer than ~0.25 fade out as they pass the camera.
    dof=(focus, px)       depth of field: layers blur by px * |depth - focus|   (focus = a layer depth 0..1)
    dof=(f0, f1, px)      rack focus from depth f0 to f1 over the shot
Use with cam(...) in script_src.py:  cam((1200, 700, 1.0), (1200, 700, 1.0), dolly=(0, 0.55), dof=(0.7, 22))
"""
import math

import cairocffi as cairo
import numpy as np

from core import H, SH, SW, W, clamp, ease

SPREAD = 6.0
LEVELS = [0, 2, 4, 7, 11, 16, 23, 32]
_BLUR = {}
STATE = {"blur": 0}


def _q(r):
    return min(LEVELS, key=lambda v: abs(v - r))


def blurred(surf, r, key):
    """Gaussian-blurred copy of a premultiplied ARGB surface (cached per key & radius)."""
    r = _q(r)
    if r <= 0:
        return surf
    k = (key, r)
    if k in _BLUR:
        return _BLUR[k]
    from scipy.ndimage import gaussian_filter, zoom
    surf.flush()
    w, h, st = surf.get_width(), surf.get_height(), surf.get_stride()
    a = np.frombuffer(surf.get_data(), np.uint8).reshape(h, st // 4, 4)[:, :w, :].astype(np.float32)
    small = a[::2, ::2]                       # blur at half resolution: fast and plenty for out-of-focus layers
    b = np.stack([gaussian_filter(small[..., c], r / 2.0) for c in range(4)], -1)
    b = zoom(b, (h / b.shape[0], w / b.shape[1], 1), order=1)[:h, :w]
    out = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ost = out.get_stride()
    buf = np.zeros((h, ost // 4, 4), np.uint8)
    buf[:, :w] = np.clip(b, 0, 255).astype(np.uint8)
    np.frombuffer(out.get_data(), np.uint8)[:] = buf.reshape(-1)
    out.mark_dirty()
    if len(_BLUR) > 60:
        _BLUR.clear()
    _BLUR[k] = out
    return out


def blurred_pad(surf, r, key):
    """Blurred copy of a cropped sprite surface with room for the blur to spread. -> (surface, pad)."""
    r = _q(r)
    pad = int(r * 2) + 2
    k = ("pad", key, r)
    if k in _BLUR:
        return _BLUR[k], pad
    w, h = surf.get_width() + 2 * pad, surf.get_height() + 2 * pad
    big = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    c = cairo.Context(big)
    c.set_source_surface(surf, pad, pad)
    c.paint()
    out = blurred(big, r, ("padsrc", key))
    _BLUR[k] = out
    return out, pad


def _cam(cam, p):
    a, b = cam.get("a", (SW / 2, SH / 2, 1.0)), cam.get("b", cam.get("a", (SW / 2, SH / 2, 1.0)))
    q = ease(p) if cam.get("ease", "io") == "io" else p
    cx, cy = a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q
    z = a[2] * (b[2] / a[2]) ** q
    dl = cam.get("dolly") or (0.0, 0.0)
    c = dl[0] + (dl[1] - dl[0]) * q
    dof = cam.get("dof")
    if dof and len(dof) == 3:
        focus, px = dof[0] + (dof[1] - dof[0]) * q, dof[2]
    elif dof:
        focus, px = dof
    else:
        focus, px = None, 0
    return cx, cy, z, c, focus, px


def apply_cam25(ctx, cx, cy, z, c, depth):
    """Perspective layer transform. Returns alpha (fade as the layer passes the camera)."""
    D = 1.0 + (1.0 - depth) * SPREAD
    gap = D - c
    rel = D / max(gap, 0.08)
    k = W / SW * 1.25
    par = 0.35 + 0.65 * depth
    zz = z ** (0.55 + 0.45 * depth)
    s = k * zz * rel
    fx = SW / 2 + (cx - SW / 2) * par
    fy = SH / 2 + (cy - SH / 2) * par
    half_w, half_h = W / (2 * s), H / (2 * s)
    if half_w < SW / 2:
        fx = min(max(fx, half_w), SW - half_w)
    if half_h < SH / 2:
        fy = min(max(fy, half_h), SH - half_h)
    ctx.translate(W / 2, H / 2)
    ctx.scale(s, s)
    ctx.translate(-fx, -fy)
    return clamp((gap - 0.12) / 0.3)


def install(film):
    if getattr(film, "_depth_installed", False):
        return
    orig = film.draw_scene

    def draw_scene(ctx, scene, t, d, cam):
        if not (cam.get("dolly") or cam.get("dof")):
            STATE["blur"] = 0
            return orig(ctx, scene, t, d, cam)
        p = clamp(t / d) if d > 0 else 0
        cx, cy, z, c, focus, px = _cam(cam, p)
        layers = scene.get("layers", [])
        depths = sorted(set([dp for (_, _, dp) in layers] + list(scene.get("dyn_depths", []))))
        for dp in depths:
            r = px * abs(dp - focus) if focus is not None else 0
            ctx.save()
            al = apply_cam25(ctx, cx, cy, z, c, dp)
            if al > 0.002:
                if al < 0.999:
                    ctx.push_group()
                for (key, painter, ld) in layers:
                    if ld == dp:
                        s = blurred(film.layer_surface(key, painter), r, key)
                        ctx.set_source_surface(s, 0, 0)
                        ctx.get_source().set_filter(cairo.FILTER_GOOD)
                        ctx.paint()
                if scene.get("dyn"):
                    STATE["blur"] = r
                    scene["dyn"](ctx, t, d, dp)
                    STATE["blur"] = 0
                if al < 0.999:
                    ctx.pop_group_to_source()
                    ctx.paint_with_alpha(al)
            ctx.restore()
        if scene.get("over"):
            scene["over"](ctx, t, d)
    film.draw_scene = draw_scene
    film._depth_installed = True
