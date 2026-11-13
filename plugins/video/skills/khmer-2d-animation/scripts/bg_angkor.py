"""Angkor / Khmer-heritage environments and helpers (registered into backgrounds.ENVIRONMENTS).

Environments:
  angkor_sunrise  Angkor Wat over the north reflecting pond (sunrise/sunset/day) with reflection, mist, birds
  angkor          Angkor Wat from the western causeway (day/evening) – replaces the simple version
  construction    12th-century building site: half-built towers, scaffolding, blocks, elephant hauling stone
  stone_diagram   animated explainer: cut sandstone -> log rollers + elephant -> earthen ramp -> stacked wall
  angkor_plan     aerial plan with timed highlights (bg params: {"highlights": [[item, km, en], ...]})
  meru            the five towers as Mount Meru (mountain appears behind the temple)
  apsara_relief   sandstone wall with carved apsaras (close-up)
  angkor_gallery  stone gallery interior with pillars, bas-relief band, incense altar
  plan_scroll     palm-leaf/parchment plan of Angkor Wat drawn progressively (insert shot)
  flag            the Cambodian national flag waving (Angkor Wat in white)
Use bg param {"birds": true} on any of them for flying birds.
"""
import math

import cairocffi as cairo

import backgrounds as B
from drawutil import (OUTLINE, blob, circle, clamp, curve, ease_io, ellipse, ellipse_path, fill_stroke, flower,
                      hexc, lerp, lin_grad, line, mix, poly, poly_path, rad_grad, rng, rrect, shade, smooth, src)

BOL = B.BOL
STONE = "#a89a7c"
FLAG_BLUE = "#032EA1"
FLAG_RED = "#E00025"


# --------------------------------------------------------------------------- helpers

def birds(ctx, t, n=7, seed=3, y0=120, y1=420, col="#2b2530", scale=1.0):
    r = rng(seed)
    span = B.X1 - B.X0 + 600
    for i in range(n):
        sp = r.uniform(70, 130)
        x = (r.uniform(0, span) + t * sp) % span + B.X0 - 300
        y = r.uniform(y0, y1) + math.sin(t * 0.7 + i) * 14
        s = r.uniform(0.6, 1.1) * scale
        flap = math.sin(t * r.uniform(7, 10) + i * 1.7)
        w, h = 22 * s, 12 * s * flap
        ctx.new_path()
        ctx.move_to(x - w, y - h)
        ctx.curve_to(x - w * 0.5, y - h * 0.4 - 4 * s, x - w * 0.2, y - 2 * s, x, y + 2 * s)
        ctx.curve_to(x + w * 0.2, y - 2 * s, x + w * 0.5, y - h * 0.4 - 4 * s, x + w, y - h)
        src(ctx, col)
        ctx.set_line_width(3.2 * s)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()


def mist(ctx, t, y, alpha=0.28, seed=5, col=(1, 1, 1)):
    r = rng(seed)
    for i in range(9):
        x = (r.uniform(B.X0, B.X1) + t * r.uniform(6, 14)) % (B.X1 - B.X0) + B.X0
        w = r.uniform(260, 520)
        hh = r.uniform(18, 34)
        ctx.new_path()
        ellipse_path(ctx, x, y + r.uniform(-20, 20), w, hh)
        ctx.set_source(rad_grad(x, y, 0, w, [(0, col + (alpha,)), (1, col + (0.0,))]))
        ctx.fill()


def prang(ctx, x, base, w, h, col, ol=BOL, detail=True):
    """Khmer lotus-bud tower (prang)."""
    top = base - h
    ctx.new_path()
    ctx.move_to(x - w, base)
    ctx.line_to(x - w * 0.98, base - h * 0.30)
    ctx.curve_to(x - w * 0.96, base - h * 0.62, x - w * 0.55, base - h * 0.92, x, top)
    ctx.curve_to(x + w * 0.55, base - h * 0.92, x + w * 0.96, base - h * 0.62, x + w * 0.98, base - h * 0.30)
    ctx.line_to(x + w, base)
    ctx.close_path()
    ctx.save()
    ctx.clip_preserve()
    src(ctx, col)
    ctx.fill_preserve()
    ctx.new_path()
    ctx.rectangle(x + w * 0.15, top - 10, w * 2, h + 20)
    ctx.set_source_rgba(0, 0, 0, 0.13)
    ctx.fill()
    if detail:
        for k in range(1, 9):
            yy = base - h * k / 9.5
            line(ctx, [(x - w * 1.1, yy), (x + w * 1.1, yy)], 1.5, shade(col, -0.32))
    ctx.restore()
    if ol:
        ctx.new_path()
        ctx.move_to(x - w, base)
        ctx.line_to(x - w * 0.98, base - h * 0.30)
        ctx.curve_to(x - w * 0.96, base - h * 0.62, x - w * 0.55, base - h * 0.92, x, top)
        ctx.curve_to(x + w * 0.55, base - h * 0.92, x + w * 0.96, base - h * 0.62, x + w * 0.98, base - h * 0.30)
        ctx.line_to(x + w, base)
        fill_stroke(ctx, None, ol)
    if detail:  # flame-like notches along the silhouette
        for k in range(2, 9):
            f = k / 9.5
            yy = base - h * f
            ww = w * (1.0 if f < 0.3 else (1 - ((f - 0.3) / 0.7) ** 1.6) * 0.98)
            for sd in (-1, 1):
                ex = x + sd * ww
                poly(ctx, [(ex, yy + 6), (ex + sd * 7, yy - 2), (ex, yy - 6)], col, ol * 0.5)
    line(ctx, [(x, top), (x, top - h * 0.08)], max(2, w * 0.08), shade(col, -0.2))


def gallery_band(ctx, x0, x1, base, h, col, ol=BOL, pillar_step=26):
    rrect(ctx, x0, base - h, x1 - x0, h, 2, col, ol)
    ctx.new_path()
    ctx.move_to(x0 - 6, base - h)
    ctx.line_to(x0 + 10, base - h - h * 0.45)
    ctx.line_to(x1 - 10, base - h - h * 0.45)
    ctx.line_to(x1 + 6, base - h)
    ctx.close_path()
    fill_stroke(ctx, shade(col, -0.12), ol)
    k = x0 + pillar_step
    while k < x1 - 4:
        rrect(ctx, k - 4, base - h * 0.86, 8, h * 0.86, 1, shade(col, -0.28), 0)
        k += pillar_step


def angkor_wat(ctx, cx, base, s=1.0, col=STONE, ol=BOL, built=1.0, t=0.0):
    """Angkor Wat west elevation: terrace, outer gallery with gopuras, stepped centre, five prangs.
    built < 1 draws the temple under construction (upper part missing + scaffolding)."""
    if built < 1.0:
        ctx.save()
        cut = base - 560 * s * built
        ctx.rectangle(B.X0, cut, B.X1 - B.X0, 2000)
        ctx.clip()
    rrect(ctx, cx - 760 * s, base - 30 * s, 1520 * s, 30 * s, 2, shade(col, -0.15), ol)
    # outer gallery with three gopuras
    gallery_band(ctx, cx - 720 * s, cx + 720 * s, base - 30 * s, 60 * s, shade(col, 0.04), ol, 22 * s)
    # stepped central pyramid (three levels) – drawn behind the outer gopuras
    lv = [(560, 150, 70), (430, 230, 70), (300, 300, 70)]
    for w, top_off, h in lv:
        gallery_band(ctx, cx - w * s, cx + w * s, base - top_off * s + h * s, h * s, shade(col, 0.02), ol, 24 * s)
    # five towers (corner pairs overlap in this view: draw back ones first)
    for dx, h, w in ((-185, 230, 48), (185, 230, 48), (-262, 205, 44), (262, 205, 44)):
        prang(ctx, cx + dx * s, base - 300 * s + 2, w * s, h * s, shade(col, -0.02 if abs(dx) < 200 else 0.04), ol)
    rrect(ctx, cx - 95 * s, base - 355 * s, 190 * s, 60 * s, 3, col, ol)
    prang(ctx, cx, base - 355 * s + 2, 62 * s, 300 * s, shade(col, 0.06), ol)
    for gx, gw, gh in ((0, 70, 150), (-470, 46, 108), (470, 46, 108)):
        prang(ctx, cx + gx * s, base - 85 * s, gw * s, gh * s, shade(col, 0.08), ol)
        rrect(ctx, cx + gx * s - gw * 0.9 * s, base - 90 * s, gw * 1.8 * s, 60 * s, 2, shade(col, 0.05), ol)
        rrect(ctx, cx + gx * s - gw * 0.35 * s, base - 78 * s, gw * 0.7 * s, 48 * s, 3, shade(col, -0.45), ol * 0.7)
    if built < 1.0:
        ctx.restore()
        # bamboo scaffolding over the unfinished upper part
        cut = base - 560 * s * built
        for k in range(-7, 8):
            x = cx + k * 48 * s
            line(ctx, [(x, cut + 30 * s), (x, cut - 120 * s)], 4, "#9b7a3c")
        for j in range(4):
            y = cut + 20 * s - j * 40 * s
            line(ctx, [(cx - 340 * s, y), (cx + 340 * s, y)], 3.5, "#9b7a3c")
        for k in range(-6, 7, 2):
            x = cx + k * 48 * s
            line(ctx, [(x, cut + 20 * s), (x + 48 * s, cut - 20 * s)], 2.5, "#8a6a30")


def elephant(ctx, x, y, s, t, walking=True, facing=1, col="#9c9aa6"):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * facing, s)
    ph = t * 3.0 if walking else 0.0
    for i, (lx, back) in enumerate(((-70, True), (60, True), (-50, False), (80, False))):
        sw = math.sin(ph + (0 if i in (0, 3) else math.pi)) * (18 if walking else 0)
        c = shade(col, -0.18) if back else col
        rrect(ctx, lx + sw - 20, -100, 40, 100, 14, c, BOL)
        ellipse(ctx, lx + sw, -4, 22, 7, shade(col, -0.3), 2)
    blob(ctx, [(-120, -110), (-95, -190), (10, -215), (110, -190), (130, -120), (90, -70), (-90, -70)], col)
    curve(ctx, (-125, -140), (-150, -120), (-145, -90), 5, OUTLINE)
    hy = -170 + math.sin(ph * 2) * 2
    ellipse(ctx, 145, hy, 62, 58, col, BOL)
    ctx.new_path()
    ctx.move_to(110, hy - 30)
    ctx.curve_to(70, hy - 60, 60, hy + 40, 110, hy + 50)
    ctx.curve_to(130, hy + 30, 135, hy - 10, 110, hy - 30)
    fill_stroke(ctx, shade(col, -0.08), BOL)
    sw = math.sin(ph * 1.3) * 12
    curve(ctx, (190, hy + 20), (215 + sw, hy + 80), (200 + sw, hy + 125), 26 + 2 * BOL, OUTLINE)
    curve(ctx, (190, hy + 20), (215 + sw, hy + 80), (200 + sw, hy + 125), 26, col)
    curve(ctx, (178, hy + 34), (200, hy + 50), (214, hy + 44), 7, "#f4efe2")
    circle(ctx, 165, hy - 12, 5, OUTLINE, 0)
    ctx.restore()


def sandstone_block(ctx, x, y, w, h, col="#b8a37f", holes=True):
    rrect(ctx, x - w / 2, y - h, w, h, 4, col, BOL)
    ctx.new_path()
    ctx.rectangle(x + w * 0.2, y - h, w * 0.3, h)
    ctx.set_source_rgba(0, 0, 0, 0.08)
    ctx.fill()
    if holes:  # the small holes seen on real Angkor blocks (for lifting pegs)
        for hx in (-0.25, 0.25):
            circle(ctx, x + hx * w, y - h * 0.55, 3.5, shade(col, -0.5), 0)


def label(ctx, km, en, x, y, size=34, bg=(0.10, 0.07, 0.05, 0.72), align="center", alpha=1.0,
          km_color="#ffffff", en_color="#ffe9a8"):
    """Khmer + English label card drawn inside an environment."""
    import textrender as TR
    if not B.TEXT_DIR:
        return
    sk = TR.render(km, size, B.TEXT_DIR, color=km_color) if km else None
    se = TR.render(en, int(size * 0.62), B.TEXT_DIR, color=en_color) if en else None
    w = max(s.get_width() for s in (sk, se) if s) + 24
    h = sum(s.get_height() for s in (sk, se) if s) + 10
    x0 = x - w / 2 if align == "center" else x
    ctx.save()
    ctx.new_path()
    from drawutil import rrect_path
    rrect_path(ctx, x0, y, w, h, 14)
    ctx.set_source_rgba(bg[0], bg[1], bg[2], bg[3] * alpha)
    ctx.fill()
    yy = y + 4
    for s_ in (sk, se):
        if s_:
            ctx.set_source_surface(s_, x0 + (w - s_.get_width()) / 2, yy)
            ctx.paint_with_alpha(alpha)
            yy += s_.get_height() - 2
    ctx.restore()


def flag_surface(w=1000, h=640):
    """Flat Cambodian flag (blue-red-blue, 1:2:1, Angkor Wat in white) as a cairo surface."""
    key = ("flag", w, h)
    if key in _CACHE:
        return _CACHE[key]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    g = cairo.Context(surf)
    src(g, FLAG_BLUE)
    g.paint()
    src(g, FLAG_RED)
    g.rectangle(0, h * 0.25, w, h * 0.5)
    g.fill()
    flag_temple(g, w / 2, h * 0.715, h * 0.5 * 0.82 / 368.0)  # emblem ~82% of the red band height
    _CACHE[key] = surf
    return surf


def flag_temple(g, cx, base, s):
    """White Angkor Wat emblem with thin black lines, as on the flag (drawn 560 wide x 368 high, times s)."""
    white = "#ffffff"
    g.save()
    g.translate(cx, base)
    g.scale(s, s)
    # stepped base
    for i, (w, h) in enumerate(((560, 26), (500, 26), (440, 26))):
        rrect(g, -w / 2, -h * (i + 1), w, h, 0, white, 2.2)
    yb = -78
    # outer towers, inner towers, central tower (three steps of height)
    for dx, tw, th in ((-200, 44, 150), (200, 44, 150), (-110, 52, 190), (110, 52, 190)):
        rrect(g, dx - tw * 0.8, yb - 34, tw * 1.6, 34, 0, white, 2.2)
        prang(g, dx, yb - 34, tw * 0.7, th, white, 2.2, detail=False)
        for k in range(1, 5):
            yy = yb - 34 - th * k / 5.5
            line(g, [(dx - tw * 0.45, yy), (dx + tw * 0.45, yy)], 1.6, OUTLINE)
    rrect(g, -75, yb - 60, 150, 60, 0, white, 2.2)
    prang(g, 0, yb - 60, 44, 230, white, 2.2, detail=False)
    for k in range(1, 6):
        yy = yb - 60 - 230 * k / 6.5
        line(g, [(-28, yy), (28, yy)], 1.6, OUTLINE)
    g.restore()


_CACHE = {}


def flag_wave(ctx, x, y, w, h, t, amp=0.045, strips=80):
    """Draw the flag waving from a pole at (x, y) (top-left corner)."""
    surf = flag_surface()
    fw, fh = surf.get_width(), surf.get_height()
    sx, sy = w / fw, h / fh
    sw = fw / strips
    for i in range(strips):
        u = i / strips
        k = u * 2 * math.pi * 1.4 - t * 5.2
        dy = math.sin(k) * amp * h * (0.15 + u)
        shade_k = 0.10 * math.cos(k) * (0.3 + u)
        ctx.save()
        ctx.translate(x, y + dy)
        ctx.scale(sx, sy * (1 - 0.04 * u * abs(math.sin(k))))
        ctx.rectangle(i * sw, 0, sw + 1.2, fh)
        ctx.clip()
        ctx.set_source_surface(surf, 0, 0)
        ctx.paint()
        if shade_k > 0:
            ctx.set_source_rgba(1, 1, 1, shade_k)
        else:
            ctx.set_source_rgba(0, 0, 0, -shade_k)
        ctx.paint()
        ctx.restore()


# --------------------------------------------------------------------------- plan geometry (top view)

def plan_rects(cx, cy, s):
    """Angkor Wat site plan, west at the left. Returns named geometry (scale s: 1 = fits 1080 high)."""
    R = {}
    R["moat_outer"] = (cx - 560 * s, cy - 480 * s, 1120 * s, 960 * s)
    R["moat_inner"] = (cx - 490 * s, cy - 410 * s, 980 * s, 820 * s)
    R["wall"] = (cx - 440 * s, cy - 360 * s, 880 * s, 720 * s)
    R["causeway"] = (cx - 560 * s, cy - 18 * s, 125 * s, 36 * s)
    R["gopura"] = (cx - 455 * s, cy - 60 * s, 34 * s, 120 * s)
    R["walkway"] = (cx - 420 * s, cy - 13 * s, 255 * s, 26 * s)
    R["libraries"] = [(cx - 330 * s, cy - 90 * s, 50 * s, 34 * s), (cx - 330 * s, cy + 56 * s, 50 * s, 34 * s)]
    R["ponds"] = [(cx - 260 * s, cy - 120 * s, 60 * s, 70 * s), (cx - 260 * s, cy + 50 * s, 60 * s, 70 * s)]
    R["g1"] = (cx - 170 * s, cy - 150 * s, 380 * s, 300 * s)
    R["cross"] = (cx - 150 * s, cy - 70 * s, 70 * s, 140 * s)
    R["g2"] = (cx - 70 * s, cy - 110 * s, 240 * s, 220 * s)
    R["g3"] = (cx - 25 * s, cy - 72 * s, 150 * s, 144 * s)
    tc = (cx + 50 * s, cy)
    R["towers"] = [(tc[0], tc[1], 30 * s)] + [(tc[0] + dx * 62 * s, tc[1] + dy * 58 * s, 20 * s)
                                                 for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1))]
    return R


def _rect(ctx, r, fill=None, ol=BOL, col=OUTLINE):
    ctx.new_path()
    ctx.rectangle(*r)
    if fill is not None:
        src(ctx, fill)
        ctx.fill_preserve()
    src(ctx, col)
    ctx.set_line_width(ol)
    ctx.stroke()


def draw_plan(ctx, cx, cy, s, t, ink=None, progress=1.0):
    """Coloured aerial plan, or (ink=colour) a line drawing revealed by progress 0..1."""
    R = plan_rects(cx, cy, s)
    if ink:
        items = [("moat_outer", None), ("moat_inner", None), ("wall", None), ("causeway", None), ("gopura", None),
                 ("walkway", None), ("g1", None), ("cross", None), ("g2", None), ("g3", None)]
        n = len(items) + 2
        for i, (k, _) in enumerate(items):
            p = clamp(progress * n - i, 0, 1)
            if p <= 0:
                continue
            ctx.save()
            ctx.set_dash([max(1, 4000 * p), 4000])
            _rect(ctx, R[k], None, 3.0, ink)
            ctx.restore()
        p = clamp(progress * n - len(items), 0, 1)
        if p > 0:
            for (x, y, r) in R["towers"]:
                ctx.new_path()
                ctx.arc(x, y, r * p, 0, 2 * math.pi)
                src(ctx, ink)
                ctx.set_line_width(2.6)
                ctx.stroke()
            for rr in R["libraries"]:
                _rect(ctx, rr, None, 2.0, ink)
        return R
    # ground + jungle
    ctx.new_path()
    ctx.rectangle(B.X0, -200, B.X1 - B.X0, 1500)
    src(ctx, "#4f8f3e")
    ctx.fill()
    r = rng(17)
    for _ in range(900):
        x, y = r.uniform(B.X0, B.X1), r.uniform(-150, 1250)
        circle(ctx, x, y, r.uniform(10, 24), shade("#4f8f3e", r.uniform(-0.25, 0.15)), 0)
    # moat (water ring)
    _rect(ctx, R["moat_outer"], "#3f9fcf", BOL)
    for _ in range(60):
        x = r.uniform(R["moat_outer"][0], R["moat_outer"][0] + R["moat_outer"][2])
        y = r.uniform(R["moat_outer"][1], R["moat_outer"][1] + R["moat_outer"][3])
        dx = math.sin(t * 1.4 + x * 0.05) * 6
        line(ctx, [(x + dx, y), (x + dx + 26, y)], 2, "#ffffff", 0.35)
    _rect(ctx, R["moat_inner"], "#8fbf6a", BOL)
    _rect(ctx, R["wall"], None, 6, "#9a6b45")
    for _ in range(140):
        x = r.uniform(R["moat_inner"][0] + 10, R["moat_inner"][0] + R["moat_inner"][2] - 10)
        y = r.uniform(R["moat_inner"][1] + 10, R["moat_inner"][1] + R["moat_inner"][3] - 10)
        if abs(y - cy) > 140 * s or x < cx - 380 * s:
            circle(ctx, x, y, r.uniform(8, 16) * s, "#5e9e46", 0)
    _rect(ctx, R["causeway"], "#cbbd9b", BOL)
    _rect(ctx, R["walkway"], "#d6c9a6", BOL)
    _rect(ctx, R["gopura"], "#b9aa88", BOL)
    for rr in R["ponds"]:
        _rect(ctx, rr, "#5fb0d6", 2.5)
    for rr in R["libraries"]:
        _rect(ctx, rr, "#b9aa88", 2.5)
    _rect(ctx, R["g1"], "#c9b994", BOL)
    _rect(ctx, (R["g1"][0] + 14 * s, R["g1"][1] + 14 * s, R["g1"][2] - 28 * s, R["g1"][3] - 28 * s), "#e2d6b4", 2.5)
    _rect(ctx, R["cross"], "#c1b18c", 2.5)
    _rect(ctx, R["g2"], "#bfae88", BOL)
    _rect(ctx, (R["g2"][0] + 12 * s, R["g2"][1] + 12 * s, R["g2"][2] - 24 * s, R["g2"][3] - 24 * s), "#dccfac", 2.5)
    _rect(ctx, R["g3"], "#b3a17a", BOL)
    for (x, y, rad) in R["towers"]:
        for k, c in enumerate(("#a8946c", "#bca782", "#d0bd96")):
            circle(ctx, x, y, rad * (1 - k * 0.3), c, 2.2)
    return R


def highlight_shapes(R, item):
    """Return a list of ('rect', r) / ('circle', (x, y, r)) / ('ring', (outer, inner)) for a plan item."""
    if item == "towers":
        return [("circle", c) for c in R["towers"]]
    if item == "moat":
        return [("ring", (R["moat_outer"], R["moat_inner"]))]
    if item == "walls":
        return [("rect", R["wall"]), ("rect", R["g2"]), ("rect", R["g3"])]
    if item == "galleries":
        return [("rect", R["g1"]), ("rect", R["g2"]), ("rect", R["g3"])]
    if item == "entrance":
        return [("rect", R["causeway"]), ("rect", R["gopura"]), ("rect", R["walkway"])]
    if item == "courtyards":
        return [("rect", R["cross"]), ("rect", (R["g1"][0] + 14, R["g1"][1] + 14, R["g1"][2] - 28, R["g1"][3] - 28))]
    if item == "reliefs":
        return [("rect", R["g1"])]
    return []


def draw_highlight(ctx, shapes, a, t):
    pulse = 0.65 + 0.35 * math.sin(t * 6)
    for kind, g in shapes:
        ctx.new_path()
        if kind == "rect":
            ctx.rectangle(*g)
        elif kind == "circle":
            ctx.arc(g[0], g[1], g[2] + 6, 0, 2 * math.pi)
        elif kind == "ring":
            ctx.rectangle(*g[0])
        ctx.set_source_rgba(1.0, 0.85, 0.2, 0.95 * a * pulse)
        ctx.set_line_width(9)
        ctx.stroke_preserve()
        ctx.set_source_rgba(1.0, 0.95, 0.5, 0.18 * a * pulse)
        ctx.fill()
        if kind == "ring":
            ctx.new_path()
            ctx.rectangle(*g[1])
            ctx.set_source_rgba(1.0, 0.85, 0.2, 0.95 * a * pulse)
            ctx.set_line_width(9)
            ctx.stroke()


# --------------------------------------------------------------------------- environments

def _maybe_birds(ctx, t, tod, **kw):
    if B.CUR.get("birds"):
        birds(ctx, t, col="#2b2530" if tod not in ("night",) else "#0b0b12", **kw)


def _angkor_sunrise(ctx, layer, t, tod):
    hz = 600
    p = B.TOD.get(tod, B.TOD["day"])
    if layer == "SKY":
        B.sky(ctx, t, tod, hz + 40)
        _maybe_birds(ctx, t, tod)
    elif layer == "BG":
        dark = tod in ("sunrise", "sunset")
        col = "#5d5262" if dark else STONE
        B.hills(ctx, hz + 6, "#3f5e4a" if dark else "#6f9a6a", 26, 201, step=110)
        for k, x in enumerate(range(-500, 2500, 120)):
            if abs(x - 960) > 760:
                B.sugar_palm(ctx, x + (k * 37) % 60, hz + 14, 150 + (k * 29) % 70, t, "#2f4f3a" if dark else "#4f9a52", 1.6)
        angkor_wat(ctx, 960, hz + 4, 0.78, col, BOL * 0.8)
        # pond with reflection
        y0, y1 = hz + 4, 790
        ctx.new_path()
        ctx.rectangle(B.X0, y0, B.X1 - B.X0, y1 - y0)
        ctx.set_source(lin_grad(0, y0, 0, y1, [(0, mix(p["sky"][1], "#3f6f8f", 0.25)), (1, mix(p["sky"][0], "#1f3f5f", 0.45))]))
        ctx.fill()
        ctx.save()
        ctx.rectangle(B.X0, y0, B.X1 - B.X0, y1 - y0)
        ctx.clip()
        ctx.push_group()
        ctx.translate(0, 2 * y0)
        ctx.scale(1, -1)
        angkor_wat(ctx, 960, hz + 4, 0.78, col, 0)
        for k, x in enumerate(range(-500, 2500, 120)):
            if abs(x - 960) > 760:
                B.sugar_palm(ctx, x + (k * 37) % 60, hz + 14, 150 + (k * 29) % 70, t, "#2f4f3a" if dark else "#4f9a52", 0)
        if p.get("sun"):
            circle(ctx, B.X0 + (B.X1 - B.X0) * p["sun"][0], (hz + 40) * p["sun"][1], 58, p["sun"][2], 0)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(0.42)
        r = rng(9)
        for _ in range(90):
            x, y = r.uniform(B.X0, B.X1), r.uniform(y0 + 4, y1)
            w = r.uniform(30, 120)
            dx = math.sin(t * 1.1 + y * 0.08) * 12
            line(ctx, [(x + dx, y), (x + dx + w, y)], 2.0, "#ffffff", 0.22)
        ctx.restore()
        line(ctx, [(B.X0, y0), (B.X1, y0)], 2.0, "#ffffff", 0.35)
    elif layer == "MG":
        mist(ctx, t, 640, 0.30 if tod == "sunrise" else 0.15)
        for x, y, s_ in ((120, 760, 1.0), (330, 735, 0.7), (1600, 750, 0.9), (1820, 770, 1.1)):
            B.lotus(ctx, x, y, s_, bloom=(int(x) % 3 == 0))
        dark = tod in ("sunrise", "sunset")
        B.sugar_palm(ctx, -120, 820, 560, t, "#24412f" if dark else "#3f8f3a")
        B.sugar_palm(ctx, 60, 840, 480, t, "#24412f" if dark else "#3f8f3a")
        B.sugar_palm(ctx, 1880, 830, 540, t, "#24412f" if dark else "#3f8f3a")
    elif layer == "GROUND":
        ctx.new_path()
        ctx.move_to(B.X0, 800)
        ctx.curve_to(400, 780, 1500, 800, B.X1, 785)
        ctx.line_to(B.X1, 1200)
        ctx.line_to(B.X0, 1200)
        ctx.close_path()
        ctx.set_source(lin_grad(0, 780, 0, 1080, [(0, "#8db35f"), (1, "#6b9a48")]))
        ctx.fill()
        ctx.new_path()
        ctx.move_to(B.X0, 1000)
        ctx.curve_to(500, 930, 1300, 900, B.X1, 920)
        ctx.line_to(B.X1, 1010)
        ctx.curve_to(1300, 990, 500, 1040, B.X0, 1120)
        ctx.close_path()
        src(ctx, "#c98c5a")  # laterite path
        ctx.fill()
        B.grass_tufts(ctx, 820, 1070, 60, 211, "#4c7f35")
    elif layer == "FG":
        for x in (-80, -20, 1950, 2010):
            for k in range(4):
                a = -1.9 + k * 0.25
                line(ctx, [(x + k * 14, 1110), (x + k * 14 + math.cos(a) * 60 + math.sin(t + k) * 6, 1110 + math.sin(a) * 260)],
                     7, "#3f6f2f")


def _angkor_day(ctx, layer, t, tod):
    hz = 560
    if layer == "SKY":
        B.sky(ctx, t, tod, hz)
        _maybe_birds(ctx, t, tod)
    elif layer == "BG":
        B.hills(ctx, hz + 60, "#8db87d", 30, 221)
        for x in (-300, -60, 1980, 2220):
            B.sugar_palm(ctx, x, hz + 110, 260, t)
        dark = tod in ("sunset", "evening")
        angkor_wat(ctx, 960, hz + 118, 0.82, "#6a5a66" if dark else STONE)
    elif layer == "MG":
        B.water(ctx, hz + 118, 780, t, "#5aa8c8", tod)
        for x in (200, 1720):
            B.lotus(ctx, x, 745, 1.0)
        if tod in ("sunset", "evening"):
            mist(ctx, t, 700, 0.12, col=(1.0, 0.85, 0.7))
    elif layer == "GROUND":
        ctx.new_path()
        ctx.rectangle(B.X0, 780, B.X1 - B.X0, 400)
        src(ctx, "#cfc4a8")
        ctx.fill()
        for k in range(-6, 40):
            line(ctx, [(k * 80, 790), (k * 80 - 60, 1080)], 1.4, "#b4a888")
        rrect(ctx, B.X0, 770, B.X1 - B.X0, 24, 2, "#b4a888", BOL)
        # naga balustrade along the causeway
        rrect(ctx, B.X0, 752, B.X1 - B.X0, 16, 6, "#b9ad90", BOL * 0.8)
        for k in range(-6, 40):
            rrect(ctx, k * 120 - 6, 762, 12, 18, 2, "#a99d80", 1.5)
    elif layer == "FG":
        for x in (-60, 1980):
            for k in range(3):
                line(ctx, [(x + k * 30, 1100), (x + k * 30 + 20, 860)], 10, "#4f9a3a")


def _construction(ctx, layer, t, tod):
    hz = 600
    lt = B.CUR.get("lt", t)
    if layer == "SKY":
        B.sky(ctx, t, tod, hz)
        _maybe_birds(ctx, t, tod, n=4)
    elif layer == "BG":
        B.hills(ctx, hz + 10, "#7aa86a", 50, 301)
        for k, x in enumerate(range(-500, 2500, 140)):
            B.tree(ctx, x, hz + 40, 0.7 + (k % 3) * 0.1, "#4f8f45", "#5a4030", seed=k)
        angkor_wat(ctx, 1000, hz + 120, 0.72, STONE, BOL * 0.8, built=float(B.CUR.get("built", 0.55)))
    elif layer == "MG":
        # piles of cut sandstone
        for bx, by, n in ((140, 800, 3), (1700, 805, 4)):
            for j in range(n):
                for i in range(n - j):
                    sandstone_block(ctx, bx + i * 92 - (n - j) * 46 + 46 + j * 0, by - j * 52, 88, 52)
        # earthen ramp with a block on it
        poly(ctx, [(1250, 805), (1560, 805), (1560, 650), (1500, 650)], "#b38b5c", BOL)
        sandstone_block(ctx, 1450, 700, 90, 52)
        # elephant hauling a block on a sled (loops across)
        span = 2600
        ex = (lt * 70 + float(B.CUR.get("elephant_x", 0))) % span - 500
        sled_x = ex - 330
        line(ctx, [(sled_x + 50, 760), (ex - 60, 690)], 4, "#7a5a2a")
        for k in range(4):
            circle(ctx, sled_x - 50 + k * 34 + (-(lt * 70) % 34), 790, 10, "#8a6436", 2)
        rrect(ctx, sled_x - 70, 765, 150, 16, 3, "#7a5232", BOL * 0.8)
        sandstone_block(ctx, sled_x + 5, 765, 120, 70)
        elephant(ctx, ex, 800, 0.62, lt, True, 1)
    elif layer == "GROUND":
        B.ground(ctx, 790, "#d6b98a", "#c49e6c")
        r = rng(31)
        for _ in range(60):
            ellipse(ctx, r.uniform(B.X0, B.X1), r.uniform(820, 1070), r.uniform(4, 9), r.uniform(2, 5), "#b49a72", 0,
                    rot=r.uniform(0, 3))
        for x, y in ((300, 1050), (1500, 1040)):
            rrect(ctx, x - 140, y - 16, 280, 26, 12, "#8a6436", BOL)
    elif layer == "FG":
        sandstone_block(ctx, -40, 1110, 220, 120)
        sandstone_block(ctx, 1980, 1120, 240, 130)


def _stone_diagram(ctx, layer, t, tod):
    lt = B.CUR.get("lt", t)
    cyc = float(B.CUR.get("cycle", 12.0))
    k = (lt % cyc) / cyc
    if layer == "SKY":
        ctx.new_path()
        ctx.rectangle(B.X0, -200, B.X1 - B.X0, 1500)
        src(ctx, "#efe2c0")
        ctx.fill()
        for x in range(-520, 2460, 60):
            line(ctx, [(x, -200), (x, 1300)], 1, "#d9c79f")
        for y in range(-200, 1300, 60):
            line(ctx, [(B.X0, y), (B.X1, y)], 1, "#d9c79f")
        rrect(ctx, 60, 50, 1800, 980, 18, None, 4)
    elif layer == "MG":
        gy = 820
        line(ctx, [(80, gy), (1840, gy)], 4, "#6b4a2a")
        # 1. quarry
        poly(ctx, [(90, gy), (90, 520), (300, 520), (330, 600), (330, gy)], "#b9a27a", BOL)
        for y in (580, 650, 720):
            line(ctx, [(95, y), (325, y)], 2, "#8b7553")
        cut_k = clamp(k / 0.2, 0, 1)
        sandstone_block(ctx, 230, 600 + 0 * cut_k, 120, 80)
        if cut_k < 1:
            line(ctx, [(170, 520), (170, 520 + 80 * cut_k)], 3, "#d8242c")
        # 2. rollers + elephant
        mk = clamp((k - 0.2) / 0.45, 0, 1)
        bx = lerp(420, 1180, ease_io(mk))
        for i in range(6):
            rx = 380 + i * 140
            circle(ctx, rx, gy - 12, 12, "#8a6436", 2)
        if 0.2 <= k < 0.7:
            sandstone_block(ctx, bx, gy - 24, 130, 80)
            line(ctx, [(bx + 65, gy - 60), (bx + 220, gy - 120)], 4, "#7a5a2a")
            elephant(ctx, bx + 330, gy, 0.55, lt, True, 1)
        # 3. ramp + wall
        poly(ctx, [(1180, gy), (1640, gy), (1640, 560), (1560, 560)], "#c9a36c", BOL)
        layers_done = 3
        for j in range(layers_done):
            for i in range(3):
                sandstone_block(ctx, 1640 + 60 + i * 64, gy - j * 50, 62, 50, holes=False)
        rk = clamp((k - 0.7) / 0.25, 0, 1)
        if k >= 0.7:
            px = lerp(1200, 1600, ease_io(min(1, rk * 1.3)))
            py = lerp(gy - 24, 560, ease_io(min(1, rk * 1.3)))
            if rk > 0.77:
                px, py = lerp(1600, 1828, (rk - 0.77) / 0.23), lerp(560, gy - 150, (rk - 0.77) / 0.23)
            sandstone_block(ctx, px, py, 62, 50)
        # arrows
        for x0, x1 in ((340, 420), (1120, 1190)):
            line(ctx, [(x0, 440), (x1, 440)], 4, "#6b4a2a")
            poly(ctx, [(x1, 430), (x1 + 16, 440), (x1, 450)], "#6b4a2a", 0)
        for i, (x, km, en) in enumerate(((210, "កាត់ថ្មភក់", "Cutting sandstone"),
                                         (780, "ដឹកជញ្ជូនលើដុំឈើមូល", "Hauling on log rollers"),
                                         (1560, "ផ្គុំថ្មជាជាន់ៗ", "Stacking in layers"))):
            active = (i == 0 and k < 0.2) or (i == 1 and 0.2 <= k < 0.7) or (i == 2 and k >= 0.7)
            circle(ctx, x - 150, 150, 30, "#d8333a" if active else "#b5a07a", 3)
            label(ctx, km, en, x + 20, 100, 36, alpha=1.0 if active else 0.55)
    elif layer == "GROUND":
        pass


def _angkor_plan(ctx, layer, t, tod):
    lt = B.CUR.get("lt", t)
    dur = float(B.CUR.get("dur", 20.0))
    if layer == "SKY":
        R = draw_plan(ctx, 960, 540, 1.0, t)
        hl = B.CUR.get("highlights") or []
        if not hl:
            return
        t0 = float(B.CUR.get("hl_start", 1.0))
        t1 = float(B.CUR.get("hl_end", dur - 1.0))
        seg = (t1 - t0) / len(hl)
        i = int((lt - t0) // seg) if lt >= t0 else -1
        if 0 <= i < len(hl):
            item, km, en = hl[i][0], hl[i][1], hl[i][2]
            a = clamp(min((lt - t0 - i * seg) / 0.4, (t0 + (i + 1) * seg - lt) / 0.3), 0, 1)
            draw_highlight(ctx, highlight_shapes(R, item), a, t)
            label(ctx, km, en, 960, 900, 44, alpha=a)
        # compass
        circle(ctx, 1760, 150, 46, "#f4efe2", 3)
        poly(ctx, [(1760, 110), (1772, 150), (1748, 150)], "#d8333a", 0)
        line(ctx, [(1712, 150), (1808, 150)], 2)
        import textrender as TR
        if B.TEXT_DIR:
            s_ = TR.render("ជើង N", 22, B.TEXT_DIR, color="#ffffff")
            ctx.set_source_surface(s_, 1760 - s_.get_width() / 2, 60)
            ctx.paint()


def _meru(ctx, layer, t, tod):
    lt = B.CUR.get("lt", t)
    hz = 760
    a = smooth((lt - float(B.CUR.get("mountain_at", 2.0))) / 2.5)
    if layer == "SKY":
        B.sky(ctx, t, tod, hz)
        _maybe_birds(ctx, t, tod, n=4)
    elif layer == "BG":
        if a > 0:
            ctx.save()
            ctx.push_group()
            pts = [(-200, hz + 20), (380, 420), (520, 300), (660, 330), (800, 170), (960, 40), (1120, 170), (1260, 330),
                   (1400, 300), (1540, 420), (2120, hz + 20)]
            ctx.new_path()
            ctx.move_to(*pts[0])
            for p_ in pts[1:]:
                ctx.line_to(*p_)
            ctx.close_path()
            ctx.set_source(lin_grad(0, 40, 0, hz, [(0, "#f6f0ff"), (0.25, "#9db3dd"), (1, "#5f7fae")]))
            ctx.fill_preserve()
            src(ctx, OUTLINE)
            ctx.set_line_width(BOL)
            ctx.stroke()
            for x in (800, 960, 1120):
                for k_ in range(3):
                    B.cloud(ctx, x - 200 + k_ * 120, 200 + k_ * 40 + (x - 960) * 0.3, 0.5)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(a * 0.85)
            ctx.restore()
        B.hills(ctx, hz, "#7aa86a", 30, 401)
    elif layer == "MG":
        angkor_wat(ctx, 960, hz + 20, 1.05, STONE)
        if a > 0.3:
            # glowing guide lines from the five tower tips to the five peaks
            s = 1.05
            tips = [(960, hz + 20 - (355 + 300) * s), (960 - 185 * s, hz + 20 - (300 + 230) * s),
                    (960 + 185 * s, hz + 20 - (300 + 230) * s), (960 - 262 * s, hz + 20 - (300 + 205) * s),
                    (960 + 262 * s, hz + 20 - (300 + 205) * s)]
            peaks = [(960, 40), (800, 170), (1120, 170), (660, 330), (1260, 330)]
            for (x0, y0), (x1, y1) in zip(tips, peaks):
                ctx.save()
                ctx.set_dash([12, 10])
                line(ctx, [(x0, y0), (x1, y1)], 3, "#ffd84a", (a - 0.3) / 0.7)
                ctx.restore()
        if a > 0.6:
            label(ctx, "ភ្នំព្រះសុមេរុ", "Mount Meru — the sacred mountain", 960, 880, 46, alpha=(a - 0.6) / 0.4)
    elif layer == "GROUND":
        B.ground(ctx, hz + 20, "#8fbf62", "#6aa449")


_APSARA = None


def _apsara_char(seed):
    global _APSARA
    import rig
    if _APSARA is None:
        _APSARA = {"character_id": "apsara_relief", "_rig": rig.merge_rig({
            "build": "adult_f", "hair": {"style": "long", "color": "#151515", "flower": "#FFFFFF"},
            "top": {"style": "royal", "color": "#FFF6E6", "accent": "#EDB33A"},
            "bottom": {"style": "sampot", "color": "#D93A2B", "hem": "#EDB33A"}, "sash": "#EDB33A",
            "headwear": "mokot", "jewelry": ["earrings", "necklace", "bracelets", "anklets"]})}
    return _APSARA


def stone_figure(ctx, x, y, s, theta, pose_t, stone="#b8a27c"):
    """Draw an apsara as a carved relief (stone-tinted, with a cut shadow)."""
    import rig
    ch = _apsara_char(0)
    st = dict(theta=theta, pose="dance", expr="smile", t=pose_t, legs="stand")
    ctx.push_group()
    rig.draw_character(ctx, ch, st, x, y, s)
    ctx.set_operator(cairo.OPERATOR_ATOP)
    ctx.set_source_rgba(*hexc(stone), 0.80)
    ctx.paint()
    ctx.set_operator(cairo.OPERATOR_OVER)
    pat = ctx.pop_group()
    ctx.save()
    ctx.translate(7, 9)
    ctx.set_source_rgba(0.18, 0.12, 0.06, 0.45)
    ctx.mask(pat)
    ctx.restore()
    ctx.set_source(pat)
    ctx.paint()


def _apsara_relief(ctx, layer, t, tod):
    if layer == "SKY":
        ctx.new_path()
        ctx.rectangle(B.X0, -200, B.X1 - B.X0, 1500)
        ctx.set_source(lin_grad(0, -200, 400, 1300, [(0, "#d3bd95"), (1, "#9c8463")]))
        ctx.fill()
        r = rng(41)
        y = -200
        row = 0
        while y < 1300:
            h = r.uniform(110, 160)
            line(ctx, [(B.X0, y), (B.X1, y)], 2.5, "#7d6a4f")
            x = B.X0 + (row % 2) * 120
            while x < B.X1:
                line(ctx, [(x, y), (x, y + h)], 2.2, "#7d6a4f")
                x += r.uniform(180, 320)
            y += h
            row += 1
        for _ in range(140):
            circle(ctx, r.uniform(B.X0, B.X1), r.uniform(-200, 1300), r.uniform(6, 30),
                   (0.35, 0.40, 0.30) if r.random() < 0.5 else (0.25, 0.22, 0.2), 0)
        ctx.new_path()
        ctx.rectangle(B.X0, -200, B.X1 - B.X0, 1500)
        ctx.set_source_rgba(0.85, 0.75, 0.6, 0.55)
        ctx.fill()
    elif layer == "BG":
        for nx, w in ((480, 330), (960, 400), (1440, 330)):
            ctx.new_path()
            ctx.move_to(nx - w / 2, 1000)
            ctx.line_to(nx - w / 2, 330)
            ctx.curve_to(nx - w / 2, 200, nx - 40, 150, nx, 110)
            ctx.curve_to(nx + 40, 150, nx + w / 2, 200, nx + w / 2, 330)
            ctx.line_to(nx + w / 2, 1000)
            ctx.close_path()
            ctx.set_source(lin_grad(nx - w / 2, 0, nx + w / 2, 0, [(0, "#8c7556"), (0.15, "#b59e78"), (1, "#a58d68")]))
            ctx.fill_preserve()
            src(ctx, "#5f4d36")
            ctx.set_line_width(5)
            ctx.stroke()
        for x in (720, 1200):
            for y in (300, 560, 820):
                for k in range(8):
                    a = k * math.pi / 4
                    ellipse(ctx, x + math.cos(a) * 22, y + math.sin(a) * 22, 14, 7, "#b8a27c", 2.0, rot=a)
                circle(ctx, x, y, 12, "#a48d68", 2.0)
    elif layer == "MG":
        stone_figure(ctx, 480, 990, 1.25, 30, 0.6)
        stone_figure(ctx, 960, 1010, 1.5, -20, 2.4)
        stone_figure(ctx, 1440, 990, 1.25, -30, 1.4)
    elif layer == "FG":
        rrect(ctx, B.X0, 1000, B.X1 - B.X0, 120, 0, "#a48d68", 3)
        for k in range(-8, 50):
            x = k * 60
            blob(ctx, [(x - 26, 1060), (x, 1010), (x + 26, 1060), (x, 1080)], "#b8a27c", 2.0)


def _angkor_gallery(ctx, layer, t, tod):
    vx, vy = 960, 560
    if layer == "SKY":
        ctx.new_path()
        ctx.rectangle(B.X0, -200, B.X1 - B.X0, 1500)
        src(ctx, "#6d5f4c")
        ctx.fill()
        # bright opening at the far end
        ctx.new_path()
        ctx.rectangle(vx - 110, vy - 170, 220, 300)
        ctx.set_source(lin_grad(0, vy - 170, 0, vy + 130, [(0, "#fff4d6"), (1, "#e9d2a0")]))
        ctx.fill()
    elif layer == "BG":
        # ceiling and floor planes
        poly(ctx, [(B.X0, -200), (B.X1, -200), (vx + 110, vy - 170), (vx - 110, vy - 170)], "#5a4d3d", 0)
        poly(ctx, [(B.X0, 1300), (B.X1, 1300), (vx + 110, vy + 130), (vx - 110, vy + 130)], "#b9a885", 0)
        for k in range(1, 14):
            f = (k / 14) ** 2
            y = lerp(vy + 130, 1300, f)
            hw = lerp(110, 2000, f)
            line(ctx, [(vx - hw, y), (vx + hw, y)], 1.6, "#9a8a69")
            yc = lerp(vy - 170, -200, f)
            line(ctx, [(vx - hw, yc), (vx + hw, yc)], 3, "#4a3f31")
        # bas-relief band along the left wall
        ctx.save()
        ctx.new_path()
        poly_path(ctx, [(B.X0, 300), (vx - 110, vy - 60), (vx - 110, vy + 60), (B.X0, 900)])
        src(ctx, "#a48f6c")
        ctx.fill_preserve()
        ctx.clip()
        for k in range(40):
            f = (k / 40)
            x = lerp(vx - 110, B.X0, f ** 1.6)
            sc_ = lerp(0.1, 1.4, f ** 1.6)
            y = lerp(vy, 600, f ** 1.6)
            ctx.save()
            ctx.translate(x, y)
            ctx.scale(sc_, sc_)
            circle(ctx, 0, -60, 14, "#8a7556", 1.5)
            rrect(ctx, -12, -46, 24, 50, 6, "#8a7556", 1.5)
            line(ctx, [(10, -40), (34, -90)], 3, "#5f4d36")
            ctx.restore()
        ctx.restore()
    elif layer == "MG":
        # pillars receding on both sides
        for side in (-1, 1):
            for k in range(9, -1, -1):
                f = ((k + 1) / 10) ** 1.7
                x = vx + side * lerp(120, 1250, f)
                hw = lerp(10, 95, f)
                top = lerp(vy - 160, -120, f)
                bot = lerp(vy + 125, 1200, f)
                col = shade("#a8946f", -0.1 + 0.15 * f)
                rrect(ctx, x - hw, top, hw * 2, bot - top, 2, col, BOL * f + 0.5)
                for band in (0.12, 0.88):
                    yb = lerp(top, bot, band)
                    rrect(ctx, x - hw * 1.15, yb - hw * 0.25, hw * 2.3, hw * 0.5, 2, shade(col, 0.1), BOL * f * 0.7 + 0.4)
                if f > 0.3:  # small carved devata on the pillar face
                    ellipse(ctx, x, lerp(top, bot, 0.45), hw * 0.35, hw * 0.9, shade(col, -0.12), 1.2)
        # light shafts
        for x0 in (520, 1340):
            poly(ctx, [(x0, -200), (x0 + 180, -200), (x0 + 420, 1200), (x0 + 220, 1200)], None, 0)
            ctx.set_source_rgba(1, 0.95, 0.8, 0.10)
            ctx.fill()
        if B.CUR.get("altar", True):
            ax = float(B.CUR.get("altar_x", 1300))
            rrect(ctx, ax - 120, 780, 240, 110, 6, "#8a4a2a", BOL)
            rrect(ctx, ax - 140, 770, 280, 22, 4, "#b5642f", BOL)
            blob(ctx, [(ax - 46, 770), (ax + 46, 770), (ax + 36, 720), (ax - 36, 720)], "#c9a14a")
            ellipse(ctx, ax, 720, 38, 8, "#8a6a2a", 2)
            for k in range(3):
                x = ax - 12 + k * 12
                line(ctx, [(x, 720), (x + (k - 1) * 4, 650)], 3, "#b5422a")
                circle(ctx, x + (k - 1) * 4, 650, 3, "#ff7a2a", 0)
                smoke(ctx, x + (k - 1) * 4, 646, t + k, 0.7)
            for fx in (ax - 100, ax + 100):
                rrect(ctx, fx - 8, 720, 16, 50, 3, "#f6eed8", 2)
                ellipse(ctx, fx, 712, 5, 9, "#ffb02a", 0)
                flower(ctx, fx + (20 if fx > ax else -20), 752, 10, "#f07fb6")
    elif layer == "GROUND":
        pass


def smoke(ctx, x, y, t, s=1.0):
    for k in range(6):
        ph = (t * 0.6 + k / 6) % 1.0
        yy = y - ph * 160 * s
        xx = x + math.sin(ph * 6 + t + k) * 14 * s * ph
        ctx.new_path()
        ctx.arc(xx, yy, (4 + ph * 16) * s, 0, 2 * math.pi)
        ctx.set_source_rgba(0.92, 0.92, 0.95, 0.35 * (1 - ph))
        ctx.fill()


def _plan_scroll(ctx, layer, t, tod):
    lt = B.CUR.get("lt", t)
    dur = float(B.CUR.get("dur", 6.0))
    if layer == "SKY":
        ctx.new_path()
        ctx.rectangle(B.X0, -200, B.X1 - B.X0, 1500)
        ctx.set_source(lin_grad(0, 0, 0, 1080, [(0, "#6b3f22"), (1, "#4a2a16")]))
        ctx.fill()
        for y in range(-200, 1300, 46):
            line(ctx, [(B.X0, y), (B.X1, y + 10)], 2, "#5a341b")
    elif layer == "MG":
        rrect(ctx, 260, 120, 1400, 860, 10, "#f0dfb4", BOL)
        for x in (250, 1670):
            rrect(ctx, x - 28, 100, 56, 900, 26, "#d9c08a", BOL)
        draw_plan(ctx, 960, 560, 0.78, t, ink="#4a2f1a", progress=clamp(lt / max(1.0, dur * 0.8), 0, 1))
        label(ctx, "ប្លង់ប្រាសាទអង្គរវត្ត", "Plan of Angkor Wat", 960, 140, 38, bg=(0.35, 0.22, 0.1, 0.0),
              km_color="#4a2f1a", en_color="#6b4a2a")


def _flag(ctx, layer, t, tod):
    if layer == "SKY":
        B.sky(ctx, t, tod, 900)
        _maybe_birds(ctx, t, tod, n=4)
    elif layer == "BG":
        B.hills(ctx, 980, "#7aa86a", 40, 501)
        angkor_wat(ctx, 1500, 990, 0.32, STONE, 2)
    elif layer == "MG":
        px = 330
        rrect(ctx, px - 12, 60, 24, 1100, 8, "#d9d9de", BOL)
        circle(ctx, px, 52, 22, "#e9c24a", BOL)
        flag_wave(ctx, px + 10, 110, 1150, 736, t)
    elif layer == "GROUND":
        pass


def register(envs):
    envs.update({
        "angkor_sunrise": _angkor_sunrise,
        "angkor": _angkor_day,
        "construction": _construction,
        "stone_diagram": _stone_diagram,
        "angkor_plan": _angkor_plan,
        "meru": _meru,
        "apsara_relief": _apsara_relief,
        "angkor_gallery": _angkor_gallery,
        "plan_scroll": _plan_scroll,
        "flag": _flag,
    })
