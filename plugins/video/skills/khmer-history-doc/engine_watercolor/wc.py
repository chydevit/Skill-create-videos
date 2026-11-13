"""Watercolor + ink + gold-leaf look (rebuilt for the Chaktomuk film; first written for Chenla/Angkor).

paper.py rebinds sheet() and sky() to the versions here, so every set builder that paints "paper sheets" paints
transparent pigment washes with wet edges, granulation and a fine ink line instead.

  wash(ctx, path_fn, color, shadow, seed, texture, edge, grad, alpha)   drop-in replacement for paper.sheet
  wc_sky(ctx, P, hor, sun, sun_r, bands, seed)                          graded wash sky with soft blooms
  gold_line / gold_leaf                                                 gold-leaf highlights
  rain(ctx, t, amount, seed)                                            monsoon rain streaks (dyn, set coords)
  paper_overlay(ctx, a)                                                 cold-press paper grain over the frame
"""
import math

import cairocffi as cairo
import numpy as np

from core import H, SH, SW, W, lin, mix, np_to_surface, rad, rng, shade, src, value_noise

INK = "#1e1a17"
GOLD = "#c9a34a"
GOLD_L = "#f1d98c"
WC = dict(brick="#a4442e", brick_d="#7a2e1e", laterite="#c9743a", forest="#3f5e3a", forest_l="#6f8a56",
          monsoon="#5e7286", monsoon_l="#9fb0bd", gold=GOLD, ink=INK, paper="#efe6d2", sand="#c8b48e",
          sand_d="#8f7a5a", stone="#9a9282", stone_d="#5e584e", river="#a88a4e", saffron="#e08a2e",
          lotus="#e3a1a8", teak="#8a5a32", teak_l="#b07a46", leaf="#d9c39a", lacquer="#2a120c")

_TX = {}


def _pattern(kind, size=1024, seed=1):
    key = (kind, size, seed)
    if key in _TX:
        return _TX[key]
    n1 = value_noise(size, size, 8, seed, 5)
    n2 = value_noise(size, size, 60, seed + 5, 2)
    if kind == "gran":      # pigment granulation
        g = rng(seed).random((size, size)).astype(np.float32)
        a = np.clip((g - 0.62) * 1.4, 0, 1) * np.clip(0.9 - n1, 0, 1) * 0.55 + np.abs(n2 - 0.5) * 0.25
        rgba = np.dstack([np.zeros((size, size, 3), np.float32), np.clip(a, 0, 0.6)])
    elif kind == "bloom":   # back-runs: pale islands with darker rims
        v = (n1 - n1.min()) / (n1.max() - n1.min() + 1e-6)
        light = np.clip((v - 0.6) * 3.0, 0, 1)
        rim = np.clip(1 - np.abs(v - 0.58) / 0.025, 0, 1) * 0.5
        col = np.where(light[..., None] > rim[..., None], 1.0, 0.0) * np.ones(3, np.float32)
        a = np.maximum(light * 0.35, rim * 0.28)
        rgba = np.dstack([col, a.astype(np.float32)])
    elif kind == "grain":   # wood grain: long wavy lines
        yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
        w = np.sin((yy + n1 * 160) * 0.18) * 0.5 + 0.5
        a = np.clip((w - 0.82) * 4, 0, 1) * 0.45 + np.abs(n2 - 0.5) * 0.15
        rgba = np.dstack([np.zeros((size, size, 3), np.float32), a.astype(np.float32)])
    else:                    # "paper": cold-press grain heightfield (grey, for soft-light compositing)
        from scipy.ndimage import gaussian_filter
        g = rng(seed).standard_normal((size, size)).astype(np.float32)
        h = gaussian_filter(g, 1.1, mode="wrap") * 0.5 + gaussian_filter(g, 3.0, mode="wrap") * 1.2
        sx = np.roll(h, -1, 1) - h
        sy = np.roll(h, -1, 0) - h
        lit = np.clip(0.5 + (sx * -0.7 + sy * -0.7) * 1.1, 0, 1)
        rgba = np.dstack([lit, lit, lit, np.full((size, size), 1.0, np.float32)])
    s = np_to_surface(rgba.astype(np.float32))
    p = cairo.SurfacePattern(s)
    p.set_extend(cairo.EXTEND_REPEAT if kind == "paper" else cairo.EXTEND_REFLECT)
    _TX[key] = (s, p)
    return s, p


def _tex(ctx, kind, a, seed=1, scale=1.0):
    s, p = _pattern(kind, seed=seed)
    ctx.save()
    ctx.scale(scale, scale)
    ctx.set_source(p)
    ctx.paint_with_alpha(a)
    ctx.restore()


def wash(ctx, path_fn, color, shadow=1.0, seed=0, texture=True, edge=True, grad=None, alpha=1.0):
    """One watercolor shape: transparent pigment slightly off-register, granulation, bloom, a darker wet edge and,
    when edge=True, a fine broken ink line."""
    R = rng(seed + 991)
    dx, dy = (R.random() - 0.5) * 3.0, (R.random() - 0.5) * 3.0
    a0 = alpha * (0.9 if edge else 0.82)
    ctx.save()
    ctx.translate(dx, dy)
    path_fn(ctx)
    if grad:
        ctx.set_source(lin(0, grad[0], 0, grad[1], [(0, grad[2], a0), (1, grad[3], a0)]))
    else:
        src(ctx, color, a0)
    ctx.fill_preserve()
    ctx.clip()
    if texture:
        _tex(ctx, "bloom", 0.55 * alpha, seed % 4 + 1, 1.0 + (seed % 3) * 0.3)
        _tex(ctx, "gran", 0.45 * alpha, seed % 3 + 7, 1.0)
    base = color if not grad else grad[3]
    path_fn(ctx)
    src(ctx, shade(base, -0.38), 0.32 * alpha)
    ctx.set_line_width(9 if edge else 14)
    ctx.stroke()
    path_fn(ctx)
    src(ctx, shade(base, -0.45), 0.30 * alpha)
    ctx.set_line_width(2.6)
    ctx.stroke()
    ctx.restore()
    if edge and shadow:
        path_fn(ctx)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        src(ctx, INK, 0.72 * alpha)
        ctx.set_line_width(1.7)
        ctx.set_dash([60 + R.random() * 90, 3 + R.random() * 5], R.random() * 40)
        ctx.stroke()
        ctx.set_dash([])
    ctx.new_path()


def wc_sky(ctx, P, hor=0.62, sun=(0.5, 0.5), sun_r=70, bands=7, seed=0):
    hy = SH * hor
    ctx.set_source(lin(0, 0, 0, hy + 200, [(0, P["sky0"]), (0.75, mix(P["sky0"], P["sky1"], 0.75)), (1, P["sky1"])]))
    ctx.paint()
    R = rng(seed + 31)
    for i in range(9):
        cx, cy = R.random() * SW, hy * (0.1 + 0.7 * R.random())
        rx, ry = 280 + R.random() * 520, 60 + R.random() * 120
        c = mix(P["sky1"], "#ffffff", 0.35) if i % 3 else mix(P["sky0"], P["shadow"], 0.25)
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(rx, ry)
        ctx.set_source(rad(0, 0, 0, 1, [(0, c, 0.42), (0.7, c, 0.18), (1, c, 0)]))
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()
    _tex(ctx, "bloom", 0.4, seed % 4 + 1, 2.2)
    _tex(ctx, "gran", 0.18, 3, 1.4)
    sx, sy = SW * sun[0], SH * sun[1]
    ctx.set_source(rad(sx, sy, 0, sun_r * 6, [(0, P["sun"], 0.55), (0.25, P["sun"], 0.25), (1, P["sun"], 0)]))
    ctx.paint()
    ctx.new_path()
    ctx.arc(sx, sy, sun_r, 0, 2 * math.pi)
    src(ctx, mix(P["sun"], "#ffffff", 0.3), 0.85)
    ctx.fill()


def gold_line(ctx, path_fn, w=2.2, a=1.0):
    path_fn(ctx)
    src(ctx, GOLD, 0.9 * a)
    ctx.set_line_width(w)
    ctx.stroke()
    path_fn(ctx)
    src(ctx, GOLD_L, 0.6 * a)
    ctx.set_line_width(w * 0.4)
    ctx.stroke()


def gold_leaf(ctx, path_fn, a=1.0, seed=0, glint=0.0):
    path_fn(ctx)
    x0, y0, x1, y1 = ctx.fill_extents()
    ctx.set_source(lin(x0, y0, x1, y1, [(0, "#8a6a2a", a), (0.45, GOLD, a), (0.55, GOLD_L, a), (1, "#a8843a", a)]))
    ctx.fill_preserve()
    ctx.save()
    ctx.clip()
    _tex(ctx, "gran", 0.5 * a, seed % 3 + 7)
    if glint > 0:
        gx = x0 + (x1 - x0 + 200) * glint - 100
        ctx.set_source(lin(gx - 80, y0, gx + 80, y1, [(0, "#ffffff", 0), (0.5, "#fff6d8", 0.8 * a), (1, "#ffffff", 0)]))
        ctx.paint()
    ctx.restore()
    ctx.new_path()


def rain(ctx, t, amount=1.0, seed=0, col="#dfe6ee", w=SW, h=SH, slant=0.18, speed=1500):
    if amount <= 0:
        return
    R = rng(seed)
    n = int(260 * amount)
    xs = R.random(n) * (w + 400) - 200
    ys = R.random(n) * h
    ls = 30 + R.random(n) * 70
    sp = speed * (0.7 + 0.6 * R.random(n))
    ctx.save()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(n):
        y = (ys[i] + t * sp[i]) % (h + 200) - 100
        x = xs[i] + (y * slant)
        src(ctx, col, (0.18 + 0.22 * ((i * 37) % 10) / 10) * min(1.0, amount))
        ctx.set_line_width(1.2 + (i % 3) * 0.6)
        ctx.move_to(x, y)
        ctx.line_to(x + ls[i] * slant, y + ls[i])
        ctx.stroke()
    ctx.restore()


_PAPER = {}


def paper_overlay(ctx, a=1.0):
    if "s" not in _PAPER:
        s, p = _pattern("paper", 1024, 4)
        _PAPER["p"] = p
        yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
        d = np.sqrt(((xx - W / 8) / (W / 8)) ** 2 + ((yy - H / 8) / (H / 8)) ** 2)
        edge = np.clip((d - 0.75) * 0.9, 0, 0.35)
        rgba = np.dstack([np.full(d.shape, 0.42, np.float32), np.full(d.shape, 0.30, np.float32),
                          np.full(d.shape, 0.2, np.float32), edge.astype(np.float32)])
        _PAPER["s"] = np_to_surface(rgba)
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_SOFT_LIGHT)
    ctx.set_source(_PAPER["p"])
    ctx.paint_with_alpha(0.32 * a)
    ctx.restore()
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_MULTIPLY)
    ctx.scale(4, 4)
    ctx.set_source_surface(_PAPER["s"], 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_BILINEAR)
    ctx.paint_with_alpha(a)
    ctx.restore()
