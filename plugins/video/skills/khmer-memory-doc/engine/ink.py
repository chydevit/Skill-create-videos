"""Graphic-novel look for 'The Khmer Republic: Cambodia 1970-1975'.

* inkify(): turns a rendered scene into charcoal-and-ink artwork: muted ash / olive / khaki / sepia tones, hand-drawn
  ink outlines (edge detection with a wobbly threshold), cross-hatching in the shadows, paper fibre, and ONE warm
  accent (soft orange-gold) kept only where the scene paints vivid orange (lamps, incense, monks' robes, family).
* Archive frames for authentic photos: pinned press photo, newspaper front page, radio broadcast, archive card.
  Photos are only scaled, panned and framed: their content is never altered.
* Chapter cards styled as 1970s newspaper headlines (Khmer + English), and the title card.
* Transitions: newspaper page turn ("page"), radio static ("static"), ink wash ("ink", from film.trans_mask),
  plus a headline newspaper that drops onto the frame ("news").
* post(): paper grain, vignette, darkening over the years (LOOK(t)["dark"]) and the final fade to grey.
"""
import math

import cairocffi as cairo
import numpy as np

from core import (H, W, clamp, draw_text, ease, load_image, np_to_surface, poly, rng, smooth, src, text_surface,
                  KM_SANS)

# palette: ash grey, olive green, dusty khaki, faded sepia; one warm accent
ASH, ASH_D, OLIVE, OLIVE_D, KHAKI, SEPIA, PAPER, INK = ("#8d8d86", "#4a4a46", "#6b6e4a", "#3f4230", "#a89a74",
                                                        "#b89c72", "#e6dcc2", "#1b1a17")
GOLD = "#e8a04a"          # the single warm accent (hope, family, faith)
GOLD_PAINT = "#ff9a2a"    # paint new accent props in this vivid orange: inkify keeps it as GOLD
KM_HEAD = "Koulen"
KM_SUB = "Dangrek"
EN_HEAD = "Futura"
EN_TYPE = "American Typewriter"
EN_HAND = "Chalkboard SE"

_A = {}


def _hex(c):
    c = c.lstrip("#")
    return np.array([int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def _assets():
    if _A:
        return _A
    from scipy.ndimage import gaussian_filter
    r = rng(70)
    # tone ramp (luma -> muted palette)
    stops = [(0.0, "#14130f"), (0.16, "#2b2a25"), (0.34, "#474a3a"), (0.52, "#6f6f55"), (0.68, "#958c6c"),
             (0.82, "#bdb08c"), (0.93, "#d9cdac"), (1.0, "#ebe2c8")]
    xs = np.linspace(0, 1, 256)
    lut = np.zeros((256, 3), np.float32)
    for c in range(3):
        lut[:, c] = np.interp(xs, [s[0] for s in stops], [_hex(s[1])[c] for s in stops])
    _A["lut"] = lut
    # wobbly threshold field for hand-drawn lines (low frequency) + charcoal tooth (high frequency)
    lo = gaussian_filter(r.standard_normal((H // 8, W // 8)).astype(np.float32), 3.0)
    lo = np.kron(lo / (np.abs(lo).max() + 1e-6), np.ones((8, 8), np.float32))[:H, :W]
    _A["wob"] = lo
    tooth = gaussian_filter(r.standard_normal((H, W)).astype(np.float32), 0.7)
    _A["tooth"] = tooth / (np.abs(tooth).max() + 1e-6)
    # paper fibres (multiplicative, ~ +-4 %)
    fib = gaussian_filter(r.standard_normal((H, W)).astype(np.float32), (0.6, 6.0))
    fib = fib / (np.abs(fib).max() + 1e-6)
    blot = gaussian_filter(r.standard_normal((H // 4, W // 4)).astype(np.float32), 12)
    blot = np.kron(blot / (np.abs(blot).max() + 1e-6), np.ones((4, 4), np.float32))[:H, :W]
    _A["paper"] = (1.0 + 0.035 * fib + 0.05 * blot)[..., None]
    _A["clump"] = np.clip(0.5 + 0.9 * blot, 0.1, 1.0)
    # hatching: two diagonal line sets with a slight wobble
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    w1 = np.sin((xx + yy + 6 * lo) * (2 * np.pi / 7.0))
    w2 = np.sin((xx - yy + 6 * lo) * (2 * np.pi / 9.0))
    _A["h1"] = np.clip((w1 - 0.55) * 3.0, 0, 1)
    _A["h2"] = np.clip((w2 - 0.6) * 3.0, 0, 1)
    # vignette (darker corners, like a charcoal drawing's smudged edges)
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    _A["vig"] = np.clip(1.0 - np.clip(d - 0.55, 0, 1) * 0.55, 0.55, 1.0)[..., None]
    # charcoal strokes: thousands of short directional marks (drawn once at half size)
    from core import surface, surface_to_np
    hs = surface(W // 2, H // 2)
    c = cairo.Context(hs)
    c.set_source_rgb(1, 1, 1)
    c.paint()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for _ in range(9000):
        x, y = r.random() * W / 2, r.random() * H / 2
        L = 6 + r.random() * 26
        ang = -0.85 + r.normal() * 0.18
        c.set_source_rgba(0, 0, 0, 0.05 + 0.13 * r.random())
        c.set_line_width(0.6 + r.random() * 1.6)
        c.move_to(x, y)
        c.line_to(x + L * math.cos(ang), y + L * math.sin(ang))
        c.stroke()
    st = surface_to_np(hs)[..., 0].astype(np.float32) / 255.0
    st = np.kron(st, np.ones((2, 2), np.float32))[:H, :W]
    _A["strokes"] = gaussian_filter(st, 0.6)
    return _A


def _smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def inkify(s, mode="full", dark=0.0, accent=1.0):
    """In-place graphic-novel filter on a cairo ARGB32 ImageSurface of size W x H.
    mode 'full': tones + ink lines + hatching + paper;  'tone': tones + paper only (text cards, maps)."""
    A = _assets()
    s.flush()
    buf = np.ndarray((H, W, 4), np.uint8, buffer=s.get_data())
    bgr = buf[..., :3].astype(np.float32) * (1 / 255)
    b, g, r = bgr[..., 0], bgr[..., 1], bgr[..., 2]
    L = 0.3 * r + 0.59 * g + 0.11 * b
    # accent mask: vivid orange-gold (hue ~20-50 deg, high saturation)
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    ch = mx - mn
    sat = ch / (mx + 1e-4)
    ratio = (g - b) / (ch + 1e-4)
    acc = (r >= mx - 1e-4) * _smoothstep(0.74, 0.86, sat) * _smoothstep(0.42, 0.55, mx) * \
        _smoothstep(0.25, 0.38, ratio) * (1 - _smoothstep(0.82, 0.95, ratio)) * accent
    # tone curve: darker and flatter as the war goes on
    Lc = np.clip(L * (1.0 - 0.28 * dark), 0, 1) ** (0.78 + 0.5 * dark)
    tone = A["lut"][(Lc * 255).astype(np.int32)]
    tone += 0.16 * (1 - 0.6 * dark) * (bgr[..., ::-1] - L[..., None])   # a whisper of the original hue
    # skin and wood: warm, moderately saturated browns become faded sepia instead of olive
    warm = (r > g) * (g > b) * _smoothstep(0.12, 0.25, sat) * (1 - _smoothstep(0.66, 0.76, sat)) * \
        _smoothstep(0.18, 0.3, ratio)
    sep = (np.clip(Lc * 1.12 + 0.06, 0, 1))[..., None] * np.array([1.0, 0.86, 0.68], np.float32)[None, None, :]
    w3 = (0.55 * warm * (1 - 0.5 * dark))[..., None]
    tone = tone * (1 - w3) + sep * w3
    if mode == "full":
        # ink outlines: gradient magnitude on luma, wobbly threshold, thickened by one pixel
        gx = np.zeros_like(L)
        gy = np.zeros_like(L)
        gx[:, 1:-1] = L[:, 2:] - L[:, :-2]
        gy[1:-1, :] = L[2:, :] - L[:-2, :]
        mag = np.sqrt(gx * gx + gy * gy)
        thr = 0.06 + 0.03 * A["wob"]
        line = _smoothstep(thr, thr + 0.05, mag)
        for sh in ((1, 1), (-1, 1), (1, 0), (-1, 0)):   # thicken to a ~3 px brush line
            line = np.maximum(line, np.roll(line, sh[0], sh[1]) * 0.9)
        line *= 0.7 + 0.3 * (A["tooth"] > -0.4)
        # hatching in the shadows, charcoal strokes everywhere (stronger in the mid-tones and darks)
        hat = A["h1"] * (1 - _smoothstep(0.25, 0.48, Lc)) * 0.7 + A["h2"] * (1 - _smoothstep(0.1, 0.28, Lc)) * 0.6
        strk = (1 - A["strokes"]) * (0.35 + 0.8 * (1 - Lc)) * A["clump"]
        tone *= (1 - 0.92 * line)[..., None] * (1 - 0.45 * hat)[..., None] * (1 - 0.55 * strk)[..., None]
        tone *= (1 + 0.07 * A["tooth"])[..., None]   # charcoal tooth
    else:
        tone *= (1 - 0.3 * (1 - A["strokes"]) * A["clump"])[..., None]
    tone *= A["paper"]
    # the warm accent, kept with its own light
    gold = _hex(GOLD)[None, None, :] * (0.55 + 0.6 * L[..., None])
    a3 = (acc * 0.9)[..., None]
    tone = tone * (1 - a3) + gold * a3
    out = np.clip(tone[..., ::-1] * 255, 0, 255).astype(np.uint8)
    buf[..., :3] = out
    s.mark_dirty()


def post(ctx, s, fi, dark=0.0, grey=0.0):
    """Whole-frame finish after compositing: vignette, darkness over the years, fade to grey, paper grain."""
    A = _assets()
    s.flush()
    buf = np.ndarray((H, W, 4), np.uint8, buffer=s.get_data())
    f = buf[..., :3].astype(np.float32)
    f *= A["vig"] * (1.0 - 0.18 * dark)
    if grey > 0:
        Lg = (0.114 * f[..., 0] + 0.587 * f[..., 1] + 0.299 * f[..., 2])[..., None]
        f = f * (1 - grey) + Lg * grey
    R = rng(fi // 2)   # grain holds two frames (compresses better)
    off = int(R.integers(0, 64)), int(R.integers(0, 64))
    gr = np.roll(A["tooth"], off, (0, 1))[..., None]
    f += gr * (6.0 + 4.0 * dark)
    buf[..., :3] = np.clip(f, 0, 255).astype(np.uint8)
    s.mark_dirty()


# ------------------------------------------------------------------ drawing helpers
def scribble_rect(ctx, x, y, w, h, col=INK, lw=3.0, seed=0, a=1.0, passes=2):
    """A hand-inked rectangle: each side drawn twice with slight overshoot and wobble."""
    R = rng(seed)
    src(ctx, col, a)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for _ in range(passes):
        ctx.set_line_width(lw * (0.7 + 0.5 * R.random()))
        pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
        for i in range(4):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            j = lambda: R.normal() * 2.2   # noqa: E731
            ctx.move_to(x0 + j() - (x1 - x0) * 0.01, y0 + j() - (y1 - y0) * 0.01)
            ctx.curve_to(x0 + (x1 - x0) * 0.33 + j(), y0 + (y1 - y0) * 0.33 + j(),
                         x0 + (x1 - x0) * 0.66 + j(), y0 + (y1 - y0) * 0.66 + j(),
                         x1 + j() + (x1 - x0) * 0.01, y1 + j() + (y1 - y0) * 0.01)
        ctx.stroke()


def charcoal_fill(ctx, x, y, w, h, col, a=1.0, seed=0, strokes=90):
    """Rough charcoal shading: a flat tone plus loose diagonal strokes."""
    R = rng(seed)
    src(ctx, col, a)
    ctx.rectangle(x, y, w, h)
    ctx.fill()
    ctx.save()
    ctx.rectangle(x, y, w, h)
    ctx.clip()
    for _ in range(strokes):
        x0 = x + R.random() * w
        y0 = y + R.random() * h
        L = 40 + R.random() * 160
        src(ctx, INK, 0.05 + 0.07 * R.random())
        ctx.set_line_width(1 + R.random() * 3)
        ctx.move_to(x0, y0)
        ctx.line_to(x0 + L * 0.7, y0 - L * 0.7)
        ctx.stroke()
    ctx.restore()


def _wall(ctx, tone=PAPER, seed=3):
    """Plaster wall / board behind pinned photos."""
    charcoal_fill(ctx, 0, 0, W, H, tone, 1.0, seed, 220)
    g = cairo.RadialGradient(W / 2, H / 2, 200, W / 2, H / 2, W * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0.05, 0.04, 0.03, 0.55)
    ctx.set_source(g)
    ctx.paint()


def pin(ctx, x, y, col="#9a3a2a", a=1.0):
    src(ctx, "#000000", 0.35 * a)
    ctx.arc(x + 4, y + 6, 11, 0, 6.283)
    ctx.fill()
    src(ctx, col, a)
    ctx.arc(x, y, 11, 0, 6.283)
    ctx.fill()
    src(ctx, "#ffffff", 0.45 * a)
    ctx.arc(x - 3, y - 4, 3.5, 0, 6.283)
    ctx.fill()


def tape(ctx, x, y, w, ang, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    src(ctx, "#e9dfc0", 0.72 * a)
    ctx.rectangle(-w / 2, -16, w, 32)
    ctx.fill()
    ctx.restore()


def _photo(ctx, path, x, y, w, h, z=1.0, fx=0.5, fy=0.5, a=1.0, contain=True):
    """Draw an authentic image unaltered inside a box (contain or cover), with a zoom/pan."""
    s = load_image(path)
    iw, ih = s.get_width(), s.get_height()
    k = (min if contain else max)(w / iw, h / ih) * z
    dw, dh = iw * k, ih * k
    ctx.save()
    ctx.rectangle(x, y, w, h)
    ctx.clip()
    ox = x + (w - dw) * fx if dw > w else x + (w - dw) / 2
    oy = y + (h - dh) * fy if dh > h else y + (h - dh) / 2
    ctx.translate(ox, oy)
    ctx.scale(k, k)
    ctx.set_source_surface(s, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint_with_alpha(a)
    ctx.restore()


def fit_box(path, bw, bh):
    s = load_image(path)
    iw, ih = s.get_width(), s.get_height()
    k = min(bw / iw, bh / ih)
    return iw * k, ih * k


def caption_slip(ctx, card, x, y, w, a=1.0, seed=0, ang=0.0):
    """Typed caption slip pinned under a press photo: title (km + en), date, source, credit."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    lines = []
    if card.get("km"):
        lines.append((card["km"], 32, INK, KM_SANS, "Bold"))
    lines.append((card.get("en") or "", 27, INK, EN_TYPE, ""))
    meta = " · ".join(v for v in (card.get("date"), card.get("inst")) if v)
    if meta:
        lines.append((meta, 20, "#4a4436", EN_TYPE, ""))
    if card.get("note"):
        lines.append((card["note"], 19, "#4a4436", EN_TYPE, ""))
    if card.get("credit"):
        lines.append((card["credit"], 17, "#5a5446", EN_TYPE, ""))
    sur = [text_surface(t, sz, c, f, wt, width=w - 40) for (t, sz, c, f, wt) in lines if t]
    hh = sum(s_.get_height() + 6 for s_ in sur) + 34
    src(ctx, "#000000", 0.3 * a)
    ctx.rectangle(8, 9, w, hh)
    ctx.fill()
    src(ctx, "#efe6cf", a)
    ctx.rectangle(0, 0, w, hh)
    ctx.fill()
    src(ctx, "#8a3a2a", a)
    ctx.rectangle(0, 0, w, 6)
    ctx.fill()
    draw_text(ctx, "ឯកសារពិត · ARCHIVE", 20, 14, 14, "#8a3a2a", "tl", a, font=EN_HEAD, weight="Bold")
    yy = 36
    for s_ in sur:
        ctx.set_source_surface(s_, 20, yy)
        ctx.paint_with_alpha(a)
        yy += s_.get_height() + 6
    ctx.restore()
    return hh


# ------------------------------------------------------------------ archive frames (authentic images)
def pinned(path, card, tilt=-0.025, z=(1.0, 1.06), wall=PAPER, seed=0, side="r"):
    """Press photo pinned to a plaster wall, typed caption slip beside it; slow push-in."""
    def over(ctx, t, d):
        q = ease(clamp(t / d))
        zz = 1.0 + 0.05 * q
        ctx.save()
        ctx.translate(W / 2, H / 2)
        ctx.scale(zz, zz)
        ctx.translate(-W / 2, -H / 2)
        _wall(ctx, wall, seed + 5)
        a = smooth(t / 0.6)
        bw, bh = 1120, 820
        dw, dh = fit_box(path, bw, bh)
        x0 = (70 if side == "r" else W - 70 - bw) + (bw - dw) / 2
        y0 = 120 + (bh - dh) / 2
        ctx.save()
        ctx.translate(x0 + dw / 2, y0 + dh / 2)
        ctx.rotate(tilt)
        ctx.translate(-dw / 2, -dh / 2)
        src(ctx, "#000000", 0.4 * a)
        ctx.rectangle(14, 18, dw + 28, dh + 28)
        ctx.fill()
        src(ctx, "#f2ecdc", a)
        ctx.rectangle(-14, -14, dw + 28, dh + 28)
        ctx.fill()
        _photo(ctx, path, 0, 0, dw, dh, z[0] + (z[1] - z[0]) * q, 0.5, 0.5, a)
        pin(ctx, dw / 2, -2, a=a)
        tape(ctx, dw - 10, dh, 120, -0.6, a)
        ctx.restore()
        b = smooth((t - 0.5) / 0.6)
        cx = W - 620 if side == "r" else 60
        caption_slip(ctx, card, cx, 330 + (1 - b) * 30, 560, b, seed, 0.02)
        pin(ctx, cx + 280, 330 + (1 - b) * 30, "#3a4a3a", b)
        ctx.restore()
    return dict(layers=[], over=over, ink=None)


def front_page(path, card, km, en, date, z=(1.0, 1.05), seed=0, masthead_km="ព័ត៌មានប្រចាំថ្ងៃ",
               masthead_en="THE DAILY NEWS"):
    """An illustrative 1970s newspaper front page (marked as such) carrying an authentic photo."""
    def over(ctx, t, d):
        q = ease(clamp(t / d))
        _wall(ctx, "#5a5a52", seed + 9)
        a = smooth(t / 0.5)
        ctx.save()
        ctx.translate(W / 2, H / 2 + (1 - a) * 60)
        ctx.rotate(-0.018 + 0.01 * q)
        sc = 1.0 + 0.06 * q
        ctx.scale(sc, sc)
        pw, ph = 1360, 1000
        ctx.translate(-pw / 2, -ph / 2)
        src(ctx, "#000000", 0.45 * a)
        ctx.rectangle(18, 22, pw, ph)
        ctx.fill()
        src(ctx, "#e8e0c8", a)
        ctx.rectangle(0, 0, pw, ph)
        ctx.fill()
        src(ctx, INK, a)
        ctx.rectangle(40, 36, pw - 80, 5)
        ctx.fill()
        draw_text(ctx, masthead_km, pw / 2, 52, 70, INK, "tc", a, font=KM_HEAD)
        draw_text(ctx, masthead_en + "  ·  ILLUSTRATIVE FRONT PAGE  ·  " + (date or ""), pw / 2, 150, 18, "#4a4436",
                  "tc", a, font=EN_TYPE)
        ctx.rectangle(40, 182, pw - 80, 3)
        ctx.fill()
        _, hh = draw_text(ctx, km, pw / 2, 200, 64, INK, "tc", a, font=KM_HEAD, width=pw - 100, align="center",
                          spacing=0.85)
        _, eh = draw_text(ctx, en.upper(), pw / 2, 212 + hh, 34, "#2a2a26", "tc", a, font=EN_HEAD, weight="Bold",
                          width=pw - 100, align="center")
        y0 = 236 + hh + eh
        bw, bh = 820, ph - y0 - 60
        dw, dh = fit_box(path, bw, bh)
        _photo(ctx, path, 50 + (bw - dw) / 2, y0, dw, dh, z[0] + (z[1] - z[0]) * q, 0.5, 0.5, a)
        cap = card.get("en") or ""
        draw_text(ctx, cap, 50, y0 + dh + 10, 16, "#3a3a34", "tl", a, font=EN_TYPE, width=bw, italic=True)
        if card.get("credit"):
            draw_text(ctx, "Photo: " + card["credit"], 50, y0 + dh + 34, 13, "#5a5446", "tl", a, font=EN_TYPE, width=bw)
        R = rng(seed + len(en))
        for col in range(2):
            x = 900 + col * 215
            for ln in range(int((ph - y0 - 60) / 20)):
                src(ctx, "#7a7466", 0.5 * a)
                ctx.rectangle(x, y0 + ln * 20, 190 - R.random() * 50 * (ln % 6 == 5), 8)
                ctx.fill()
        ctx.restore()
    return dict(layers=[], over=over, ink=None)


def radio_scene(under, quote_km, quote_en, date, seed=0):
    """A transistor radio on a table, broadcast waves, the quoted words typing out (scene underneath is inked)."""
    sc = dict(under)
    base = sc.get("over")

    def over(ctx, t, d):
        if base:
            base(ctx, t, d)
        a = smooth(t / 0.6) * clamp((d - t) / 0.5)
        x, y = 1460, 760
        # radio body
        src(ctx, "#000000", 0.35 * a)
        ctx.rectangle(x - 190 + 10, y - 120 + 12, 380, 240)
        ctx.fill()
        src(ctx, "#5b4a36", a)
        ctx.rectangle(x - 190, y - 120, 380, 240)
        ctx.fill()
        src(ctx, "#2e2a24", a)
        ctx.rectangle(x - 170, y - 100, 200, 200)
        ctx.fill()
        for i in range(9):
            src(ctx, "#4a443a", a)
            ctx.rectangle(x - 160, y - 90 + i * 21, 180, 9)
            ctx.fill()
        src(ctx, "#d9cfb2", a)
        ctx.rectangle(x + 50, y - 90, 120, 50)
        ctx.fill()
        src(ctx, GOLD_PAINT, a)
        ctx.rectangle(x + 60 + 90 * (0.5 + 0.5 * math.sin(t * 0.3)), y - 86, 3, 42)
        ctx.fill()
        for k in range(2):
            src(ctx, "#1e1c18", a)
            ctx.arc(x + 85 + k * 50, y + 40, 18, 0, 6.283)
            ctx.fill()
        src(ctx, "#9a9a92", a)
        ctx.set_line_width(4)
        ctx.move_to(x + 150, y - 120)
        ctx.line_to(x + 260, y - 330)
        ctx.stroke()
        # broadcast waves
        for k in range(4):
            r = ((t * 70 + k * 60) % 240) + 40
            src(ctx, "#efe6cf", a * 0.5 * (1 - r / 280))
            ctx.set_line_width(3)
            ctx.arc(x + 260, y - 330, r, -2.4, -0.7)
            ctx.stroke()
        # the quote types out on a strip of paper
        n = int(len(quote_en) * clamp((t - 0.8) / max(1.0, d * 0.55)))
        bx, by, bw = 120, 120, 1180
        src(ctx, "#000000", 0.3 * a)
        ctx.rectangle(bx + 8, by + 10, bw, 230)
        ctx.fill()
        src(ctx, "#ece3c9", a * 0.97)
        ctx.rectangle(bx, by, bw, 230)
        ctx.fill()
        draw_text(ctx, "វិទ្យុ · RADIO  ·  " + (date or ""), bx + 26, by + 18, 18, "#8a3a2a", "tl", a, font=EN_HEAD,
                  weight="Bold")
        draw_text(ctx, quote_km, bx + 26, by + 52, 34, INK, "tl", a * smooth((t - 0.5) / 0.6), font=KM_SANS,
                  weight="Bold", width=bw - 52)
        draw_text(ctx, quote_en[:n], bx + 26, by + 150, 26, "#2a2a26", "tl", a, font=EN_TYPE, width=bw - 52)
    sc["over"] = over
    return sc


def archive_card(path, card, z=(1.0, 1.06), focus=(0.5, 0.5)):
    """Photo on the left, archive index card on the right (title, date, source, licence), on charcoal paper."""
    def over(ctx, t, d):
        q = ease(clamp(t / d))
        _wall(ctx, "#4c4c46", 11)
        a = smooth(t / 0.6)
        bw, bh = 1100, 850
        dw, dh = fit_box(path, bw, bh)
        x0, y0 = 90 + (bw - dw) / 2, 115 + (bh - dh) / 2
        src(ctx, "#000000", 0.4 * a)
        ctx.rectangle(x0 + 14, y0 + 16, dw + 24, dh + 24)
        ctx.fill()
        src(ctx, "#efe8d6", a)
        ctx.rectangle(x0 - 12, y0 - 12, dw + 24, dh + 24)
        ctx.fill()
        _photo(ctx, path, x0, y0, dw, dh, z[0] + (z[1] - z[0]) * q, focus[0], focus[1], a)
        b = smooth((t - 0.5) / 0.7)
        cx, cy, cw = 1270, 190 + (1 - b) * 30, 580
        caption_slip(ctx, card, cx, cy, cw, b, 0, 0.0)
        pin(ctx, cx + cw / 2, cy, a=b)
    return dict(layers=[], over=over, ink=None)


# ------------------------------------------------------------------ chapter and title cards (1970s newspapers)
def _khnum(n):
    return "".join("០១២៣៤៥៦៧៨៩"[int(c)] if c.isdigit() else c for c in str(n))


def headline_chapter(num, km, en, years, under=None, date_km=None):
    """Chapter card as a 1970s newspaper front page: masthead, chapter number, the headline in Khmer and English,
    the dateline, and the chapter's scene printed as the lead picture."""
    sc = dict(under or dict(layers=[]))
    base = sc.get("over")

    def over(ctx, t, d):
        if base:
            base(ctx, t, d)
        a_in = ease(clamp(t / 0.8))
        a_out = clamp((d - t) / 0.7)
        ctx.save()
        # paper sheet with a window on the scene (lead picture)
        ox = (1 - a_in) * -W * 0.3
        ctx.translate(ox, 0)
        PX, PY, PW, PH = 1010, 300, 830, 600
        ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        ctx.rectangle(-W, 0, W * 3, H)
        ctx.rectangle(PX, PY, PW, PH)
        src(ctx, "#e4dbc1", a_out)
        ctx.fill()
        ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
        scribble_rect(ctx, PX, PY, PW, PH, INK, 3.5, num or 0, a_out)
        # masthead
        src(ctx, INK, a_out)
        ctx.rectangle(70, 60, W - 140, 6)
        ctx.fill()
        draw_text(ctx, "ព័ត៌មាន សាធារណរដ្ឋ", 90, 84, 54, INK, "tl", a_out, font=KM_HEAD)
        draw_text(ctx, "THE REPUBLIC DAILY  ·  ILLUSTRATIVE", W - 90, 100, 22, "#4a4436", "tr", a_out, font=EN_TYPE)
        if years:
            draw_text(ctx, years, W - 90, 134, 30, INK, "tr", a_out, font=EN_HEAD, weight="Bold")
        ctx.rectangle(70, 188, W - 140, 3)
        ctx.fill()
        # chapter number block
        b = smooth((t - 0.3) / 0.6) * a_out
        if num:
            src(ctx, INK, b)
            ctx.rectangle(90, 230, 180, 180)
            ctx.fill()
            draw_text(ctx, "ជំពូកទី", 180, 262, 30, "#e4dbc1", "tc", b, font=KM_SUB)
            draw_text(ctx, _khnum(num), 180, 300, 84, "#e4dbc1", "tc", b, font=KM_HEAD)
            draw_text(ctx, "CHAPTER %d" % num, 180, 420, 20, INK, "tc", b, font=EN_HEAD, weight="Bold")
        # headline
        c = smooth((t - 0.5) / 0.7) * a_out
        ks = 100
        while ks > 54 and text_surface(km, ks, INK, KM_HEAD).get_width() > 600:
            ks -= 4
        _, kh = draw_text(ctx, km, 310, 230, ks, INK, "tl", c, font=KM_HEAD, width=660, spacing=0.85)
        e2 = smooth((t - 0.9) / 0.7) * a_out
        es = 54
        while es > 28 and text_surface(en.upper(), es, INK, EN_HEAD, "Bold").get_width() > 880:
            es -= 2
        draw_text(ctx, en.upper(), 90, max(480, 250 + kh), es, "#2a2a26", "tl", e2, font=EN_HEAD, weight="Bold",
                  width=880)
        R = rng(num or 7)
        for col in range(3):
            x = 90 + col * 300
            for ln in range(11):
                src(ctx, "#8a8274", 0.55 * e2)
                ctx.rectangle(x, 640 + ln * 22, 270 - R.random() * 60 * (ln % 4 == 3), 9)
                ctx.fill()
        draw_text(ctx, "ព្រឹត្តិការណ៍ពិត · គំនូរ​ឡើងវិញ  ·  EVENTS ARE REAL · PICTURE IS A RECONSTRUCTION", PX + PW,
                  PY + PH + 14, 14, "#4a4436", "tr", a_out, font=EN_TYPE)
        ctx.restore()
    sc["over"] = over
    sc["ink_over"] = True   # the newspaper is drawn after inking (crisp print), the lead picture is inked
    return sc


def title_card(km, en, sub_km, sub_en, under=None):
    sc = dict(under or dict(layers=[]))
    base = sc.get("over")

    def over(ctx, t, d):
        if base:
            base(ctx, t, d)
        a = smooth((t - 0.3) / 1.0) * clamp((d - t) / 0.8)
        g = cairo.LinearGradient(0, H * 0.35, 0, H)
        g.add_color_stop_rgba(0, 0, 0, 0, 0)
        g.add_color_stop_rgba(1, 0.05, 0.05, 0.04, 0.8 * a)
        ctx.set_source(g)
        ctx.paint()
        draw_text(ctx, km, W / 2, 610, 110, "#ece3c9", "mc", a, shadow=0.8, font=KM_HEAD)
        draw_text(ctx, en.upper(), W / 2, 730, 54, "#ece3c9", "mc", a, shadow=0.8, font=EN_HEAD, weight="Bold")
        b = smooth((t - 1.2) / 0.8) * clamp((d - t) / 0.8)
        draw_text(ctx, sub_km + "   ·   " + sub_en, W / 2, 820, 34, GOLD, "mc", b, shadow=0.8, font=KM_SUB)
    sc["over"] = over
    sc["ink_over"] = True
    return sc


# ------------------------------------------------------------------ headline newspaper (transition "news")
_NEWS = {}


def newspaper_surface(km, en, date):
    key = (km, en, date)
    if key in _NEWS:
        return _NEWS[key]
    from core import surface
    w, h = 1400, 960
    s = surface(w, h)
    ctx = cairo.Context(s)
    src(ctx, "#e6ddc4")
    ctx.paint()
    R = rng(len(km))
    for _ in range(160):   # handling smudges
        src(ctx, "#5a5040", 0.025)
        ctx.arc(R.random() * w, R.random() * h, 20 + R.random() * 90, 0, 6.283)
        ctx.fill()
    src(ctx, INK)
    ctx.rectangle(40, 40, w - 80, 6)
    ctx.fill()
    draw_text(ctx, "ព័ត៌មាន សាធារណរដ្ឋ", w / 2, 58, 72, INK, "tc", font=KM_HEAD)
    draw_text(ctx, "THE REPUBLIC DAILY  ·  ILLUSTRATIVE FRONT PAGE  ·  " + (date or ""), w / 2, 166, 20, "#4a4436",
              "tc", font=EN_TYPE)
    ctx.rectangle(40, 204, w - 80, 3)
    ctx.fill()
    _, hh = draw_text(ctx, km, w / 2, 232, 84, INK, "tc", font=KM_HEAD, width=w - 120, align="center", spacing=0.85)
    draw_text(ctx, en.upper(), w / 2, 250 + hh, 42, "#2a2a26", "tc", font=EN_HEAD, weight="Bold", width=w - 120,
              align="center")
    y0 = 420 + hh
    for col in range(4):
        x = 60 + col * (w - 120) / 4
        for ln in range(int((h - y0 - 50) / 22)):
            src(ctx, "#7a7466", 0.5)
            ctx.rectangle(x, y0 + ln * 22, (w - 120) / 4 - 30 - R.random() * 60 * (ln % 5 == 4), 9)
            ctx.fill()
    _NEWS[key] = s
    return s


def news_overlay(ctx, p, km, en, date):
    """The paper slides in and lands with a small bounce (p 0..0.45), holds, then is pulled away (p 0.78..1)."""
    s = newspaper_surface(km, en, date)
    if p < 0.45:
        q = ease(p / 0.45)
        dx, dy, rot, a = (1 - q) * W * 0.9, (1 - q) * 120, -0.05 + (1 - q) * 0.25, 1.0
    elif p < 0.78:
        dx, dy, rot, a = 0, 0, -0.05, 1.0
    else:
        q = ease((p - 0.78) / 0.22)
        dx, dy, rot, a = -q * W * 1.1, -q * 80, -0.05 - q * 0.2, 1.0
    k = min(W * 0.8 / s.get_width(), H * 0.88 / s.get_height())
    ctx.save()
    ctx.translate(W / 2 + dx, H / 2 + dy)
    ctx.rotate(rot)
    ctx.scale(k, k)
    src(ctx, "#000000", 0.45 * a)
    ctx.rectangle(-s.get_width() / 2 + 22, -s.get_height() / 2 + 26, s.get_width(), s.get_height())
    ctx.fill()
    ctx.set_source_surface(s, -s.get_width() / 2, -s.get_height() / 2)
    ctx.paint_with_alpha(a)
    ctx.restore()


# ------------------------------------------------------------------ transitions
def page_clip(ctx, p):
    """Newspaper page turn: the new shot is revealed behind a diagonal fold sweeping right-to-left."""
    x = W * 1.25 - p * W * 1.6
    ctx.new_path()
    poly(ctx, [(x, -10), (W + 10, -10), (W + 10, H + 10), (x + 360, H + 10)])
    ctx.clip()


def page_fx(ctx, p):
    if p <= 0 or p >= 1:
        return
    x = W * 1.25 - p * W * 1.6
    # the turning leaf (back of the old page), with a soft shadow on the new page
    w = 220 * math.sin(p * math.pi)
    g = cairo.LinearGradient(x, 0, x + w * 1.6, 0)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.45)
    g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(g)
    poly(ctx, [(x, -10), (x + w * 1.6, -10), (x + 360 + w * 1.6, H + 10), (x + 360, H + 10)])
    ctx.fill()
    src(ctx, "#ddd3b8", 1.0)
    poly(ctx, [(x, -10), (x - w, -10), (x + 360 - w * 0.7, H + 10), (x + 360, H + 10)])
    ctx.fill()
    R = rng(int(p * 40))
    for i in range(14):   # print showing through the leaf
        yy = 40 + i * 70
        xx = x - w * 0.8 + yy * 360 / H
        src(ctx, "#8a8274", 0.35)
        ctx.rectangle(xx, yy, w * 0.6 * (0.6 + 0.4 * R.random()), 8)
        ctx.fill()
    src(ctx, INK, 0.7)
    ctx.set_line_width(2.5)
    ctx.move_to(x, -10)
    ctx.line_to(x + 360, H + 10)
    ctx.stroke()


def static_fx(ctx, p, seed=0):
    """Radio static between shots: noise and rolling bands peaking mid-transition."""
    k = math.sin(p * math.pi)
    if k <= 0.02:
        return
    R = rng(int(p * 997) + seed)
    from core import surface
    n = (R.random((H // 6, W // 6)) * 255).astype(np.uint8)
    rgba = np.dstack([n, n, n, np.full_like(n, int(255 * min(1.0, k * 1.1)))]).astype(np.float32) / 255
    s = np_to_surface(rgba)
    ctx.save()
    ctx.scale(6, 6)
    ctx.set_source_surface(s, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_NEAREST)
    ctx.paint_with_alpha(0.85 * k)
    ctx.restore()
    for _ in range(int(3 + 6 * k)):
        y = R.random() * H
        src(ctx, "#e8e4d8" if R.random() < 0.5 else "#101010", 0.25 * k)
        ctx.rectangle(0, y, W, 4 + R.random() * 30)
        ctx.fill()
