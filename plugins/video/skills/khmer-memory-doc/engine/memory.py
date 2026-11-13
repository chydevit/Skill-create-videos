"""'Memory drawing' look for 'Democratic Kampuchea 1975-1979: We Remember'.

* inkify(): soft pencil and charcoal on rough, aged paper.  color=0 is memory (graphite greys with smudges, faint
  stains); color=1 is the present day (warm, gentle coloured pencil over the same paper).  Values in between are
  used as colour slowly returns at the end of the film.  Two accents survive even in memory: a candle-flame orange
  (paint props in GOLD_PAINT) and a faded blue (paint in BLUE_PAINT; used only for the 1978 East Zone scarves).
* Archive frames: album_photo (an old print in a family album) and memorial_frame (a framed print beside a candle).
  Photographs are only scaled, panned and framed: their content is never altered or animated.
* Hand-written pencil chapter cards (Khmer + English), the title card, the content advisory, the dedication.
* Transitions: "smoke" (incense smoke drifts across), "page" (notebook page turns; from ink.py), "redraw" (pencil
  lines fade and redraw; the noise wipe from film.trans_mask "ink").
"""
import math

import cairocffi as cairo
import numpy as np

from core import H, W, clamp, draw_text, ease, load_image, np_to_surface, rng, src, text_surface, KM_SANS

GOLD = "#e8a04a"          # candle flame
GOLD_PAINT = "#ff9a2a"
BLUE = "#6f8fb4"          # faded blue (East Zone scarves)
BLUE_PAINT = "#1f5cff"
GRAPHITE = "#2b2925"
PAPER = "#ebe3cf"
PAPER_D = "#cfc4a8"
KM_HAND = "Battambang"
EN_HAND = "Noteworthy"
EN_PRINT = "Cormorant Garamond"

_A = {}


def _hex(c):
    c = c.lstrip("#")
    return np.array([int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def _smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def _assets():
    if _A:
        return _A
    import ink
    base = ink._assets()          # wobble field, tooth, paper fibres, hatching, charcoal strokes
    _A.update(base)
    from scipy.ndimage import gaussian_filter
    r = rng(1975)
    stops = [(0.0, "#1d1c19"), (0.18, "#353330"), (0.4, "#5f5c55"), (0.62, "#908b80"), (0.8, "#bdb6a6"),
             (0.92, "#dcd4c1"), (1.0, "#eee7d4")]
    xs = np.linspace(0, 1, 256)
    lut = np.zeros((256, 3), np.float32)
    for c in range(3):
        lut[:, c] = np.interp(xs, [s[0] for s in stops], [_hex(s[1])[c] for s in stops])
    _A["glut"] = lut
    # age stains (tea-coloured blotches) and foxing dots, multiplicative
    st = gaussian_filter(r.standard_normal((H // 6, W // 6)).astype(np.float32), 9)
    st = np.kron(st / (np.abs(st).max() + 1e-6), np.ones((6, 6), np.float32))[:H, :W]
    stain = np.clip(st - 0.35, 0, 1) * 0.22
    fox = np.zeros((H, W), np.float32)
    for _ in range(140):
        x, y, rr = int(r.random() * W), int(r.random() * H), 2 + r.random() * 7
        y0, y1, x0, x1 = max(0, int(y - rr * 2)), min(H, int(y + rr * 2)), max(0, int(x - rr * 2)), min(W, int(x + rr * 2))
        yy, xx = np.mgrid[y0:y1, x0:x1]
        fox[y0:y1, x0:x1] += np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (rr * rr)) * (0.05 + 0.08 * r.random())
    _A["age"] = np.clip(1.0 - stain - fox, 0.7, 1.0)[..., None] * np.array([1.0, 0.97, 0.9], np.float32)
    # smudge mask: where the graphite is rubbed (low-frequency)
    sm = gaussian_filter(r.standard_normal((H // 8, W // 8)).astype(np.float32), 5)
    sm = np.kron(sm / (np.abs(sm).max() + 1e-6), np.ones((8, 8), np.float32))[:H, :W]
    _A["smudge"] = np.clip(0.35 + 0.65 * sm, 0, 1)
    # edge darkening (rubbed edges of a sketchbook page)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.maximum(np.abs(xx - W / 2) / (W / 2), np.abs(yy - H / 2) / (H / 2))
    _A["edge"] = (1.0 - 0.22 * _smoothstep(0.78, 1.0, d))[..., None]
    # raw hatching fields in [0, 1] (two directions, hand wobble) for tonal pencil hatching
    lo = base["wob"]
    _A["w1"] = 0.5 + 0.5 * np.sin((xx * 0.94 + yy * 0.34 + 7 * lo) * (2 * np.pi / 6.0))
    _A["w2"] = 0.5 + 0.5 * np.sin((xx * 0.5 - yy * 0.87 + 7 * lo) * (2 * np.pi / 7.5))
    _A["w3"] = 0.5 + 0.5 * np.sin((xx * 0.17 + yy * 0.98 + 9 * lo) * (2 * np.pi / 5.0))
    return _A


def _blur_small(img, k=4, sigma=1.6):
    """Cheap blur of an H x W x 3 image: downsample by k, gaussian, upsample."""
    from scipy.ndimage import gaussian_filter
    h, w = H // k, W // k
    small = img[:h * k, :w * k].reshape(h, k, w, k, 3).mean((1, 3))
    small = gaussian_filter(small, (sigma, sigma, 0))
    return np.repeat(np.repeat(small, k, 0), k, 1)


def inkify(s, mode="full", dark=0.0, accent=1.0, color=0.0):
    """In-place pencil/charcoal filter on a W x H ARGB32 cairo surface.
    mode 'full': tone + pencil lines + hatching + smudge + paper; 'tone': tone + paper only (cards, maps)."""
    A = _assets()
    s.flush()
    buf = np.ndarray((H, W, 4), np.uint8, buffer=s.get_data())
    bgr = buf[..., :3].astype(np.float32) * (1 / 255)
    b, g, r = bgr[..., 0], bgr[..., 1], bgr[..., 2]
    L = 0.3 * r + 0.59 * g + 0.11 * b
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    ch = mx - mn
    sat = ch / (mx + 1e-4)
    ratio = (g - b) / (ch + 1e-4)
    acc = (r >= mx - 1e-4) * _smoothstep(0.74, 0.86, sat) * _smoothstep(0.42, 0.55, mx) * \
        _smoothstep(0.25, 0.38, ratio) * (1 - _smoothstep(0.82, 0.95, ratio)) * accent
    accb = (b >= mx - 1e-4) * _smoothstep(0.7, 0.85, sat) * _smoothstep(0.5, 0.65, b) * (r < 0.35) * accent
    # memory: graphite greys
    Lc = np.clip(L * (1.0 - 0.3 * dark), 0, 1) ** (0.85 + 0.45 * dark)
    grey = A["glut"][(Lc * 255).astype(np.int32)]
    if color > 0:
        rgb = bgr[..., ::-1]
        soft = L[..., None] + (rgb - L[..., None]) * 0.8
        soft = soft * np.array([1.05, 1.0, 0.9], np.float32) + 0.03
        soft = 0.1 + 0.88 * np.clip(soft, 0, 1)                    # lifted, like coloured pencil on paper
        tone = grey * (1 - color) + soft * color
    else:
        tone = grey
    if mode == "full":
        # tonal pencil hatching: a light graphite wash on paper, darkened by hatch lines whose weight follows the tone
        dk = 1.0 - Lc
        paperc = np.array([0.93, 0.9, 0.83], np.float32)
        wash = 0.5 + 0.1 * color
        tone = paperc * (1 - wash) + tone * wash if color < 1 else tone
        e1 = dk - 0.32
        h1 = _smoothstep(1.0 - 1.5 * e1, 1.18 - 1.5 * e1, A["w1"]) * _smoothstep(0.0, 0.08, e1)
        h2 = _smoothstep(1.0 - 1.3 * (dk - 0.5), 1.18 - 1.3 * (dk - 0.5), A["w2"]) * _smoothstep(0.5, 0.58, dk)
        h3 = _smoothstep(1.0 - 1.2 * (dk - 0.68), 1.18 - 1.2 * (dk - 0.68), A["w3"]) * _smoothstep(0.68, 0.75, dk)
        hk = (0.5 - 0.25 * color)
        patchy = 0.45 + 0.55 * A["smudge"]
        tone = tone * (1 - hk * (0.6 * h1 + 0.55 * h2 + 0.6 * h3) * patchy)[..., None]
        deep = _smoothstep(0.3, 0.08, Lc)[..., None]                 # true blacks stay solid charcoal
        tone = tone * (1 - deep) + grey * deep
        gx = np.zeros_like(L)
        gy = np.zeros_like(L)
        gx[:, 1:-1] = L[:, 2:] - L[:, :-2]
        gy[1:-1, :] = L[2:, :] - L[:-2, :]
        mag = np.sqrt(gx * gx + gy * gy)
        thr = 0.05 + 0.03 * A["wob"]
        line = _smoothstep(thr, thr + 0.06, mag)
        line = np.maximum(line, np.roll(line, 1, 1) * 0.8)
        line = np.maximum(line, np.roll(line, 1, 0) * 0.7)
        line = np.maximum(line, np.roll(np.roll(line, 2, 1), -2, 0) * 0.45 * (A["wob"] > -0.2))   # sketchy re-stroke
        line *= 0.55 + 0.45 * (A["tooth"] > -0.3)                    # broken, grainy pencil line
        hat = 0.0 * Lc
        strk = (1 - A["strokes"]) * (0.3 + 0.7 * (1 - Lc)) * A["clump"]
        lc = 0.78 - 0.18 * color                                     # pencil lines get lighter in colour
        tone = tone * (1 - lc * line)[..., None] * (1 - 0.38 * hat)[..., None] * (1 - 0.42 * strk)[..., None]
        tone *= (1 + 0.09 * A["tooth"])[..., None]
        k = 0.42 * (1 - 0.7 * color)
        if k > 0.01:                                                 # rubbed graphite: smudge into soft greys
            bl = _blur_small(tone)
            m = (A["smudge"] * k)[..., None]
            tone = tone * (1 - m) + bl * m
    else:
        tone *= (1 - 0.25 * (1 - A["strokes"]) * A["clump"])[..., None]
    tone *= A["paper"]
    tone *= A["age"] * (1 - 0.5 * color) + (0.5 * color)
    tone *= A["edge"]
    gold = _hex(GOLD)[None, None, :] * (0.6 + 0.55 * L[..., None])
    a3 = (acc * 0.92)[..., None]
    tone = tone * (1 - a3) + gold * a3
    if accb.any():
        blue = _hex(BLUE)[None, None, :] * (0.7 + 0.4 * L[..., None])
        a4 = (accb * 0.85)[..., None]
        tone = tone * (1 - a4) + blue * a4
    buf[..., :3] = np.clip(tone[..., ::-1] * 255, 0, 255).astype(np.uint8)
    s.mark_dirty()


def post(ctx, s, fi, dark=0.0):
    import ink
    ink.post(ctx, s, fi, dark, 0.0)


# ------------------------------------------------------------------ paper and pencil helpers
def paper(ctx, tone=PAPER, seed=0, lines=False, margin=False):
    """Aged sketchbook / notebook paper, with optional ruled lines and a margin."""
    import ink
    ink.charcoal_fill(ctx, 0, 0, W, H, tone, 1.0, seed, 60)
    if lines:
        for k in range(26):
            y = 120 + k * 38
            src(ctx, "#7f8fa6", 0.18)
            ctx.rectangle(0, y, W, 1.5)
            ctx.fill()
    if margin:
        src(ctx, "#b0524a", 0.25)
        ctx.rectangle(170, 0, 2, H)
        ctx.fill()
    g = cairo.RadialGradient(W / 2, H / 2, 300, W / 2, H / 2, W * 0.72)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0.2, 0.15, 0.08, 0.35)
    ctx.set_source(g)
    ctx.paint()


def write_on(ctx, surf, x, y, p, a=1.0):
    """Reveal a text surface left-to-right like a hand writing it (p 0..1)."""
    if surf is None or p <= 0:
        return
    w, h = surf.get_width(), surf.get_height()
    ctx.save()
    ctx.rectangle(x, y - 4, w * clamp(p * 1.04), h + 8)
    ctx.clip()
    ctx.set_source_surface(surf, x, y)
    ctx.paint_with_alpha(a)
    ctx.restore()


def pencil_underline(ctx, x, y, w, p, seed=0, col=GRAPHITE, a=0.75):
    R = rng(seed)
    src(ctx, col, a)
    ctx.set_line_width(3)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(2):
        ctx.move_to(x, y + k * 5 + R.normal() * 1.5)
        n = 12
        for i in range(1, n + 1):
            q = i / n
            if q > p:
                break
            ctx.line_to(x + w * q, y + k * 5 + R.normal() * 1.8)
        ctx.stroke()


def candle(ctx, x, y, s, t, a=1.0, lit=1.0):
    """A small white candle with a flickering flame (flame painted in GOLD so it reads warm)."""
    from core import glow
    src(ctx, "#efe9dc", a)
    ctx.rectangle(x - 9 * s, y - 70 * s, 18 * s, 70 * s)
    ctx.fill()
    src(ctx, "#cfc6b0", a)
    ctx.rectangle(x + 3 * s, y - 70 * s, 6 * s, 70 * s)
    ctx.fill()
    if lit <= 0:
        return
    fl = 1 + 0.08 * math.sin(t * 11) + 0.05 * math.sin(t * 17 + 1)
    sw = 2.5 * math.sin(t * 5)
    glow(ctx, x, y - 92 * s, 90 * s * fl, "#ffb060", 0.30 * a * lit)
    ctx.save()
    ctx.translate(x + sw * s, y - 76 * s)
    ctx.scale(s, s * fl)
    ctx.move_to(0, 0)
    ctx.curve_to(-11, -8, -7, -26, 0, -42)
    ctx.curve_to(7, -26, 11, -8, 0, 0)
    src(ctx, GOLD, a * lit)
    ctx.fill()
    ctx.move_to(0, -2)
    ctx.curve_to(-5, -8, -3, -18, 0, -26)
    ctx.curve_to(3, -18, 5, -8, 0, -2)
    src(ctx, "#fff2c8", a * lit)
    ctx.fill()
    ctx.restore()


def _caption(ctx, card, x, y, w, a=1.0, dark_bg=False):
    """Hand-written album caption: Khmer, English, date / holder / licence."""
    col = "#efe7d2" if dark_bg else GRAPHITE
    sub = "#cfc6b0" if dark_bg else "#5a554c"
    yy = y
    if card.get("km"):
        s = text_surface(card["km"], 27, col, KM_HAND, "", width=w)
        ctx.set_source_surface(s, x, yy)
        ctx.paint_with_alpha(a)
        yy += s.get_height() + 2
    if card.get("en"):
        s = text_surface(card["en"], 26, col, EN_HAND, "", width=w)
        ctx.set_source_surface(s, x, yy)
        ctx.paint_with_alpha(a)
        yy += s.get_height() + 4
    info = " · ".join(v for v in (card.get("date"), card.get("note")) if v)
    if info:
        s = text_surface(info, 19, sub, "Helvetica Neue", "", width=w)
        ctx.set_source_surface(s, x, yy)
        ctx.paint_with_alpha(a * 0.95)
        yy += s.get_height() + 2
    if card.get("credit"):
        s = text_surface(card["credit"], 16, sub, "Helvetica Neue", "", width=w)
        ctx.set_source_surface(s, x, yy)
        ctx.paint_with_alpha(a * 0.9)
        yy += s.get_height()
    return yy - y


def _fit(path, bw, bh):
    s = load_image(path)
    k = min(bw / s.get_width(), bh / s.get_height())
    return s.get_width() * k, s.get_height() * k


def _draw_photo(ctx, path, x, y, w, h, z=1.0, fx=0.5, fy=0.5):
    s = load_image(path)
    iw, ih = s.get_width(), s.get_height()
    k = min(w / iw, h / ih) * z
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
    ctx.paint()
    ctx.restore()


def album_photo(path, card, tilt=-0.015, z=(1.0, 1.07), focus=(0.5, 0.5), side="r", page="#3b3934", seed=0):
    """An authentic photograph mounted like an old print in a family album: dark album page, white border, paper
    photo corners, a pencil caption.  The photo itself is unaltered (only scaled and framed)."""
    def over(ctx, t, d):
        p = clamp(t / max(d, 0.1))
        zz = z[0] + (z[1] - z[0]) * ease(p)
        import ink
        ink.charcoal_fill(ctx, 0, 0, W, H, page, 1.0, 40 + seed, 140)
        g = cairo.RadialGradient(W / 2, H / 2, 200, W / 2, H / 2, W * 0.75)
        g.add_color_stop_rgba(0, 0, 0, 0, 0)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.5)
        ctx.set_source(g)
        ctx.paint()
        bw, bh = (1180, 820) if side in ("r", "l") else (1500, 780)
        pw, ph = _fit(path, bw, bh)
        cx = 760 if side == "r" else (1160 if side == "l" else W / 2)
        cy = 520 if side in ("r", "l") else 470
        ctx.save()
        ctx.translate(W / 2, H / 2)
        ctx.scale(zz, zz)
        ctx.translate(-W / 2, -H / 2)
        ctx.translate(cx, cy)
        ctx.rotate(tilt)
        bd = 22
        src(ctx, "#000000", 0.45)
        ctx.rectangle(-pw / 2 - bd + 10, -ph / 2 - bd + 14, pw + 2 * bd, ph + 2 * bd)
        ctx.fill()
        src(ctx, "#f1ead8")
        ctx.rectangle(-pw / 2 - bd, -ph / 2 - bd, pw + 2 * bd, ph + 2 * bd)
        ctx.fill()
        _draw_photo(ctx, path, -pw / 2, -ph / 2, pw, ph, 1.0, *focus)
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):    # photo corners
            ctx.save()
            ctx.translate(sx * (pw / 2 + bd - 2), sy * (ph / 2 + bd - 2))
            ctx.move_to(0, 0)
            ctx.line_to(-sx * 64, 0)
            ctx.line_to(0, -sy * 64)
            ctx.close_path()
            src(ctx, "#1e1d1a", 0.92)
            ctx.fill()
            ctx.restore()
        ctx.restore()
        a = clamp((t - 0.6) / 0.8)
        if side in ("r", "l"):
            x0 = 1440 if side == "r" else 90
            _caption(ctx, card, x0, 300, 400, a, dark_bg=True)
        else:
            _caption(ctx, card, 210, 900, 1500, a, dark_bg=True)
    return dict(layers=[], over=over, ink=None)


def memorial_frame(path, card, z=(1.0, 1.05), focus=(0.5, 0.5), seed=0, candle_on=True):
    """A framed photograph on a memorial table, a candle beside it.  The photo is unaltered."""
    def over(ctx, t, d):
        p = clamp(t / max(d, 0.1))
        zz = z[0] + (z[1] - z[0]) * ease(p)
        import ink
        ink.charcoal_fill(ctx, 0, 0, W, H, "#2c2a26", 1.0, 60 + seed, 120)
        src(ctx, "#4a3f33")
        ctx.rectangle(0, 900, W, 180)
        ctx.fill()
        pw, ph = _fit(path, 980, 680)
        ctx.save()
        ctx.translate(W / 2, H / 2)
        ctx.scale(zz, zz)
        ctx.translate(-W / 2, -H / 2)
        cx, cy = 820, 500
        fr = 34
        src(ctx, "#000000", 0.5)
        ctx.rectangle(cx - pw / 2 - fr - 30 + 12, cy - ph / 2 - fr - 30 + 16, pw + 2 * fr + 60, ph + 2 * fr + 60)
        ctx.fill()
        src(ctx, "#3a2c20")
        ctx.rectangle(cx - pw / 2 - fr - 30, cy - ph / 2 - fr - 30, pw + 2 * fr + 60, ph + 2 * fr + 60)
        ctx.fill()
        src(ctx, "#e9e2d0")
        ctx.rectangle(cx - pw / 2 - fr, cy - ph / 2 - fr, pw + 2 * fr, ph + 2 * fr)
        ctx.fill()
        _draw_photo(ctx, path, cx - pw / 2, cy - ph / 2, pw, ph, 1.0, *focus)
        ctx.restore()
        if candle_on:
            candle(ctx, 1460, 930, 1.6, t)
        _caption(ctx, card, 1380, 140, 470, clamp((t - 0.6) / 0.8), dark_bg=True)
    return dict(layers=[], over=over, ink=None)


# ------------------------------------------------------------------ cards
def _khnum(n):
    return "".join("០១២៣៤៥៦៧៨៩"[int(c)] for c in str(n))


def pencil_chapter(num, km, en, years, under=None):
    """Hand-written chapter title in pencil on a notebook page; the chapter's sketch shows through a soft window."""
    base = under() if under else dict(layers=[])

    def over(ctx, t, d):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        c = cairo.Context(surf)
        paper(c, PAPER, 300 + num, lines=True, margin=True)
        if under:   # cut a soft window on the right where the sketch shows
            m = cairo.RadialGradient(1440, 520, 120, 1440, 520, 560)
            m.add_color_stop_rgba(0, 0, 0, 0, 1)
            m.add_color_stop_rgba(0.75, 0, 0, 0, 0.6)
            m.add_color_stop_rgba(1, 0, 0, 0, 0)
            c.set_operator(cairo.OPERATOR_DEST_OUT)
            c.set_source(m)
            c.paint()
            c.set_operator(cairo.OPERATOR_OVER)
        ctx.set_source_surface(surf, 0, 0)
        ctx.paint()
        a = clamp(t / 0.6)
        s0 = text_surface("ជំពូកទី %s · CHAPTER %d" % (_khnum(num), num), 30, "#6a6458", KM_HAND, "")
        write_on(ctx, s0, 220, 210, clamp((t - 0.2) / 0.7), a)
        s1 = text_surface(km, 74, GRAPHITE, KM_HAND, "Bold", width=1050)
        write_on(ctx, s1, 220, 290, clamp((t - 0.6) / 1.4), 0.95)
        y2 = 300 + s1.get_height() + 10
        s2 = text_surface(en, 60, GRAPHITE, EN_HAND, "", width=1050)
        write_on(ctx, s2, 220, y2, clamp((t - 1.6) / 1.3), 0.92)
        y3 = y2 + s2.get_height() + 26
        pencil_underline(ctx, 220, y3, 520, clamp((t - 2.6) / 0.8), seed=num)
        s3 = text_surface(years, 40, "#4a463e", EN_HAND, "")
        write_on(ctx, s3, 225, y3 + 30, clamp((t - 3.0) / 0.6), 0.9)
    out = dict(base)
    out["over"] = over
    out["ink_stage"] = "before"
    return out


def title_card(km, en, sub_km, sub_en, under=None):
    base = under() if under else dict(layers=[])

    def over(ctx, t, d):
        a = clamp(t / 1.2) * clamp((d - t) / 1.0)
        g = cairo.LinearGradient(0, 0, 0, H)
        g.add_color_stop_rgba(0, 0, 0, 0, 0.0)
        g.add_color_stop_rgba(0.55, 0, 0, 0, 0.25 * a)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.6 * a)
        ctx.set_source(g)
        ctx.paint()
        s1 = text_surface(km, 86, "#f6efdc", "Moul", "")
        write_on(ctx, s1, (W - s1.get_width()) / 2, 600, clamp(t / 1.8), a)
        s2 = text_surface(en, 58, "#f6efdc", EN_PRINT, "SemiBold")
        ctx.set_source_surface(s2, (W - s2.get_width()) / 2, 600 + s1.get_height() + 6)
        ctx.paint_with_alpha(a * clamp((t - 1.0) / 1.0))
        s3 = text_surface(sub_km + "   ·   " + sub_en, 34, "#f2d9a8", KM_HAND, "")
        ctx.set_source_surface(s3, (W - s3.get_width()) / 2, 600 + s1.get_height() + s2.get_height() + 22)
        ctx.paint_with_alpha(a * clamp((t - 1.8) / 1.0))
    out = dict(base)
    out["over"] = over
    out["ink_stage"] = "before"
    return out


def text_page(lines, tone="#26241f", a_in=1.0):
    """Quiet text on dark paper (advisory, dedication, 'sources differ' notes).  lines: [(text, size, colour, font)]"""
    def over(ctx, t, d):
        import ink
        ink.charcoal_fill(ctx, 0, 0, W, H, tone, 1.0, 77, 160)
        g = cairo.RadialGradient(W / 2, H / 2, 200, W / 2, H / 2, W * 0.7)
        g.add_color_stop_rgba(0, 0, 0, 0, 0)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.55)
        ctx.set_source(g)
        ctx.paint()
        surfs = [text_surface(tx, sz, col, fn, "", width=1500, align="center") for (tx, sz, col, fn) in lines]
        tot = sum(s.get_height() + 22 for s in surfs)
        y = (H - tot) / 2
        for k, s in enumerate(surfs):
            a = clamp((t - 0.4 - k * 0.5) / 1.0) * clamp((d - t) / 0.8)
            ctx.set_source_surface(s, (W - s.get_width()) / 2, y)
            ctx.paint_with_alpha(a)
            y += s.get_height() + 22
    return dict(layers=[], over=over, ink=None)


def sources_differ(title_km, title_en, rows, foot=None):
    """A notebook page listing what different sources say (pencil table).  rows: [(label_km, label_en, value)]"""
    def over(ctx, t, d):
        paper(ctx, PAPER, 515, lines=True, margin=True)
        s = text_surface(title_km, 50, GRAPHITE, KM_HAND, "Bold", width=1500)
        write_on(ctx, s, 220, 120, clamp(t / 1.0))
        y = 130 + s.get_height()
        s = text_surface(title_en, 42, GRAPHITE, EN_HAND, "", width=1500)
        write_on(ctx, s, 220, y, clamp((t - 0.6) / 1.0))
        y += s.get_height() + 40
        for k, (lk, le, v) in enumerate(rows):
            a = clamp((t - 1.2 - k * 0.7) / 0.6)
            if a <= 0:
                continue
            s1 = text_surface(lk, 30, "#3a3630", KM_HAND, "", width=900)
            s2 = text_surface(le, 27, "#4a463e", EN_HAND, "", width=900)
            s3 = text_surface(v, 40, "#2a2620", EN_HAND, "Bold", width=560)
            ctx.set_source_surface(s1, 230, y)
            ctx.paint_with_alpha(a)
            ctx.set_source_surface(s2, 230, y + s1.get_height())
            ctx.paint_with_alpha(a)
            ctx.set_source_surface(s3, 1230, y + 10)
            ctx.paint_with_alpha(a)
            h = max(s1.get_height() + s2.get_height(), s3.get_height()) + 22
            pencil_underline(ctx, 230, y + h - 8, 1480, a, seed=k + 3, a=0.3)
            y += h + 10
        if foot:
            s = text_surface(foot, 26, "#5a554c", EN_HAND, "", width=1480)
            ctx.set_source_surface(s, 230, min(y + 20, H - 150))
            ctx.paint_with_alpha(clamp((t - 1.5 - len(rows) * 0.7) / 0.8))
    return dict(layers=[], over=over, ink=None)


# ------------------------------------------------------------------ transitions
_SM = {}


def smoke_mask(p):
    """Half-resolution alpha mask: incense smoke rising and drifting, revealing the next shot."""
    if "f" not in _SM:
        from core import value_noise
        hh, ww = H // 2, W // 2
        n = value_noise(ww, hh, 4, 1979, 5)
        n = (n - n.min()) / (n.max() - n.min())
        yy = np.mgrid[0:hh, 0:ww][0].astype(np.float32) / hh
        _SM["f"] = np.clip(0.55 * n + 0.45 * (1 - yy), 0, 1)
    f = _SM["f"] - p * 1.18 + 0.08
    m = np.clip(-f / 0.09, 0, 1)
    wisp = np.exp(-np.abs(f) / 0.035) * (1 - p) * 0.55
    z = np.zeros(m.shape + (3,), np.float32)
    return np_to_surface(np.dstack([z, m.astype(np.float32)])), np_to_surface(
        np.dstack([np.ones(m.shape + (3,), np.float32) * 0.93, wisp.astype(np.float32)]))
