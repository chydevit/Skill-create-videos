"""Environment pack: bg_town (registered into backgrounds.ENVIRONMENTS) - places on the Kampong Cham -> Siem Reap trip.

Layer contract: fn(ctx, layer, t, tod) is called once per layer per frame in world coordinates:
SKY 0.05, BG 0.25, MG 0.6, GROUND 1.0 (characters are drawn right after it), OVER 1.0 (after the characters),
FG 1.3, SCREEN (screen space 1920x1080, after the tint).  OVER/SCREEN are only called for @extra environments.

Environments (bg params in brackets, sensible tod after the dash):
  bedroom_night   wooden Khmer home at 3 a.m.  [clock "3:00", dark 0..1]                       - interior
  restaurant      open-sided roadside restaurant, zinc roof  [backdrop rice_field|angkor|town, tables, table_w,
                  chairs, items, lights]       - rice_field: sunrise/morning, angkor: day, town: day/evening
  porridge_stall  bobor stall below Phnom Bakheng  [tables, table_w, chairs, items, tuktuk]      - morning
  hotel           "Lavender" boutique hotel; driveway x 1350-2100, y 700-935 kept clear for a van - day/evening/night
  hotel_lobby     reception; desk in GROUND x 1290-1810, top y 690  [night]                      - interior/day
  hotel_room      twin beds (top front edge y 820), lamp, steamy bathroom  [night]               - interior
  fern_cafe       plant-filled cafe  [tables, table_w, chairs, items]                            - day
  pub_street      Siem Reap Pub Street  [view street|dinner, tables, table_w, chairs, items]     - night
Seating: seated cast (legs "chair") stands at y 935 behind a table.  Tables are drawn in OVER: top surface
y 810-834, front edge 834-850 (laps ~850 are hidden), front legs to the floor at 948.
tables = list of centre x (default [700, 1220]); table_w default 520, so the two default tables meet at x 960 and
three people seated at 700 / 960 / 1220 are all behind a table.  chairs = list of x (default 3 per table).
"""
import math

import cairocffi as cairo

import backgrounds as B
from bg_angkor import angkor_wat, birds, mist, prang
from drawutil import (OUTLINE, blob, check_pattern, circle, clamp, curve, ease_io, ellipse, ellipse_path, fill_stroke,
                      flower, hexc, lerp, lin_grad, line, mix, poly, poly_path, rad_grad, rng, rrect, rrect_path, shade,
                      smooth, src, stripe_pattern)

BOL = B.BOL
X0, X1 = B.X0, B.X1
TAU = 2 * math.pi
TABLE_TOP = 828
STONE = "#b3a27f"
PURPLES = ("#9b3fb5", "#b04fc6", "#c56bd8", "#8a36a6", "#d48ce2")
LAV = ("#8f6cc8", "#a687da", "#7b5bb8")


def extra(fn):
    """Mark an environment as drawing the extra OVER (in front of characters) / SCREEN (screen-space) layers."""
    fn.extra_layers = True
    return fn


# =========================================================================== infrastructure

_REC = {}   # recorded (vector) drawings of static scenery, replayed every frame
_MAT = {}   # world->device matrices captured per layer (used by SCREEN glows)


def P(key, default=None):
    v = B.CUR.get(key)
    return default if v is None else v


def recording(key, draw):
    rec = _REC.get(key)
    if rec is None:
        rec = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, None)
        g = cairo.Context(rec)
        draw(g)
        del g
        _REC[key] = rec
    return rec


def cached(ctx, key, draw):
    """Replay a static drawing (recorded once as vectors, so it stays crisp under camera zoom)."""
    rec = recording(key, draw)
    ctx.save()
    ctx.set_source_surface(rec, 0, 0)
    ctx.paint()
    ctx.restore()


def paint_rec(ctx, rec, x, y, rot=0.0, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    if rot:
        ctx.rotate(rot)
    if s != 1.0:
        ctx.scale(s, s)
    ctx.set_source_surface(rec, 0, 0)
    ctx.paint()
    ctx.restore()


def fill_world(ctx, col, y0=-700, y1=1700):
    ctx.new_path()
    ctx.rectangle(X0 - 500, y0, X1 - X0 + 1000, y1 - y0)
    if isinstance(col, cairo.Pattern):
        ctx.set_source(col)
    else:
        src(ctx, col)
    ctx.fill()


def glow(ctx, x, y, r, col, a=0.5, add=False):
    c = hexc(col)
    ctx.save()
    if add:
        ctx.set_operator(cairo.OPERATOR_ADD)
    ctx.new_path()
    ctx.arc(x, y, r, 0, TAU)
    ctx.set_source(rad_grad(x, y, 0, r, [(0, c + (a,)), (0.3, c + (a * 0.55,)), (1, c + (0.0,))]))
    ctx.fill()
    ctx.restore()


def steam(ctx, x, y, t, s=1.0, n=5, a=0.45, rise=120, seed=0):
    """Soft rising puffs; each fades in and out so nothing pops."""
    for k in range(n):
        ph = (t * 0.3 + k / n + seed * 0.37) % 1.0
        yy = y - ph * rise * s
        xx = x + math.sin(ph * 4.5 + t * 0.7 + k * 1.9 + seed) * 9 * s * (0.3 + ph)
        al = a * math.sin(ph * math.pi) ** 1.3
        ctx.new_path()
        ctx.arc(xx, yy, (5 + ph * 15) * s, 0, TAU)
        ctx.set_source_rgba(1, 1, 1, al)
        ctx.fill()


def darkness(ctx, lights, dark=0.5, col=(0.03, 0.04, 0.13)):
    """Night darkness over everything (use in OVER) with soft holes (x, y, r, strength 0..1) around lights."""
    ctx.save()
    ctx.push_group()
    ctx.set_source_rgba(col[0], col[1], col[2], dark)
    ctx.paint()
    ctx.set_operator(cairo.OPERATOR_DEST_OUT)
    for x, y, r, k in lights:
        ctx.new_path()
        ctx.arc(x, y, r, 0, TAU)
        ctx.set_source(rad_grad(x, y, 0, r, [(0, (0, 0, 0, k)), (0.45, (0, 0, 0, k * 0.75)), (1, (0, 0, 0, 0))]))
        ctx.fill()
    ctx.pop_group_to_source()
    ctx.paint()
    ctx.restore()


def keep_matrix(ctx, name):
    _MAT[name] = ctx.get_matrix()


def with_matrix(ctx, name):
    m = _MAT.get(name)
    if m is None:
        return False
    ctx.set_matrix(m)
    return True


def persp_floor(g, y0, y1, c0, c1, line_col, vx=960, vy=520, step=150, rows=9, lw=2.0, power=1.75):
    g.new_path()
    g.rectangle(X0 - 500, y0, X1 - X0 + 1000, y1 - y0 + 600)
    g.set_source(lin_grad(0, y0, 0, y1, [(0, c0), (1, c1)]))
    g.fill()
    for k in range(1, rows + 1):
        yy = y0 + (y1 - y0) * (k / rows) ** power
        line(g, [(X0 - 500, yy), (X1 + 500, yy)], lw * (0.7 + 0.6 * k / rows), line_col)
    kk = (1500 - vy) / (y0 - vy)
    x = 960 - step * 26
    while x < 960 + step * 26:
        line(g, [(x, y0), (vx + (x - vx) * kk, 1500)], lw, line_col)
        x += step


def plank_floor(g, y0, col, line_col, seed=1, rows=10):
    g.new_path()
    g.rectangle(X0 - 500, y0, X1 - X0 + 1000, 1300)
    g.set_source(lin_grad(0, y0, 0, 1080, [(0, shade(col, -0.06)), (1, shade(col, 0.06))]))
    g.fill()
    r = rng(seed)
    prev = y0
    for k in range(1, rows + 1):
        yy = y0 + (1150 - y0) * (k / rows) ** 1.6
        line(g, [(X0 - 500, yy), (X1 + 500, yy)], 1.6 + k * 0.25, line_col)
        x = X0 - 500 + r.uniform(0, 300)
        while x < X1 + 500:
            line(g, [(x, prev), (x, yy)], 1.4 + k * 0.15, line_col)
            x += r.uniform(260, 520) * (0.6 + k * 0.08)
        prev = yy


# =========================================================================== small props

def parse_clock(v):
    try:
        if isinstance(v, (int, float)):
            return int(v), int(round((v - int(v)) * 60))
        hh, mm = str(v).strip().split(":")[:2]
        return int(hh), int(mm)
    except Exception:
        return 3, 0


def wall_clock(ctx, x, y, r, hh, mm, sec=None):
    ctx.new_path()
    ctx.arc(x + 6, y + 9, r + 12, 0, TAU)
    ctx.set_source_rgba(0, 0, 0, 0.25)
    ctx.fill()
    circle(ctx, x, y, r + 12, "#a8693a", BOL)
    circle(ctx, x, y, r + 3, "#7a4a28", 0)
    circle(ctx, x, y, r, "#fff8e4", BOL * 0.8)
    for k in range(12):
        a = k * math.pi / 6
        big = k % 3 == 0
        r0 = r * (0.68 if big else 0.79)
        line(ctx, [(x + math.sin(a) * r0, y - math.cos(a) * r0), (x + math.sin(a) * r * 0.9, y - math.cos(a) * r * 0.9)],
             6.5 if big else 3, OUTLINE)
    ha = ((hh % 12) + mm / 60.0) * math.pi / 6
    ma = mm * math.pi / 30
    line(ctx, [(x - math.sin(ha) * r * 0.1, y + math.cos(ha) * r * 0.1),
               (x + math.sin(ha) * r * 0.5, y - math.cos(ha) * r * 0.5)], 11, "#2a1d14")
    line(ctx, [(x - math.sin(ma) * r * 0.12, y + math.cos(ma) * r * 0.12),
               (x + math.sin(ma) * r * 0.8, y - math.cos(ma) * r * 0.8)], 7, "#2a1d14")
    if sec is not None:
        sa = sec * math.pi / 30
        line(ctx, [(x - math.sin(sa) * r * 0.2, y + math.cos(sa) * r * 0.2),
                   (x + math.sin(sa) * r * 0.84, y - math.cos(sa) * r * 0.84)], 2.5, "#d8333a")
    circle(ctx, x, y, 6, "#d8333a", 1.5)


def backpack(ctx, x, y, s=1.0, col="#d8433a", acc=None):
    acc = acc or shade(col, -0.25)
    W, H = 96 * s, 124 * s
    for w_, c_ in ((7 * s + 2 * BOL, OUTLINE), (7 * s, acc)):
        curve(ctx, (x - 20 * s, y - H + 8 * s), (x, y - H - 34 * s), (x + 20 * s, y - H + 8 * s), w_, c_)
    rrect(ctx, x - W / 2, y - H, W, H, 30 * s, col, BOL)
    rrect(ctx, x + W * 0.1, y - H + 16 * s, W * 0.3, H - 30 * s, 12 * s, shade(col, -0.08), 0)
    rrect(ctx, x - W * 0.5 + 4 * s, y - H, W - 8 * s, H * 0.34, 26 * s, acc, BOL * 0.8)
    rrect(ctx, x - W * 0.34, y - H * 0.5, W * 0.68, H * 0.42, 14 * s, shade(col, 0.12), BOL * 0.8)
    line(ctx, [(x - W * 0.26, y - H * 0.38), (x + W * 0.26, y - H * 0.38)], 2 * s, shade(col, -0.35))
    rrect(ctx, x - 6 * s, y - H * 0.72, 12 * s, 16 * s, 3 * s, "#f0c24a", 1.4)


def duffel(ctx, x, y, s=1.0, col="#2f6fb2", acc="#f2c14e"):
    W, H = 170 * s, 72 * s
    for w_, c_ in ((7 * s + 2 * BOL, OUTLINE), (7 * s, shade(col, -0.3))):
        curve(ctx, (x - 40 * s, y - H + 8 * s), (x, y - H - 40 * s), (x + 40 * s, y - H + 8 * s), w_, c_)
    rrect(ctx, x - W / 2, y - H, W, H, 32 * s, col, BOL)
    rrect(ctx, x - W / 2 + 30 * s, y - H * 0.62, W - 60 * s, 13 * s, 4, acc, 0)
    for sd in (-1, 1):
        ellipse(ctx, x + sd * (W / 2 - 18 * s), y - H / 2, 13 * s, H / 2 - 6 * s, shade(col, -0.15), BOL * 0.8)
    line(ctx, [(x - W * 0.3, y - H + 6 * s), (x + W * 0.3, y - H + 6 * s)], 2.2 * s, shade(col, -0.4))


def suitcase(ctx, x, y, s=1.0, col="#f2b23a", handle=True):
    W, H = 100 * s, 150 * s
    if handle:
        for sd in (-1, 1):
            line(ctx, [(x + sd * 22 * s, y - H), (x + sd * 22 * s, y - H - 64 * s)], 6 * s + 2 * BOL * 0.8, OUTLINE)
            line(ctx, [(x + sd * 22 * s, y - H), (x + sd * 22 * s, y - H - 64 * s)], 6 * s, "#b9c0c8")
        rrect(ctx, x - 30 * s, y - H - 74 * s, 60 * s, 14 * s, 6 * s, "#5a5f66", BOL * 0.8)
    for sd in (-1, 1):
        circle(ctx, x + sd * W * 0.32, y - 7 * s, 8 * s, "#3a3a40", BOL * 0.6)
    rrect(ctx, x - W / 2, y - H, W, H - 8 * s, 14 * s, col, BOL)
    for k in (-1, 0, 1):
        line(ctx, [(x + k * W * 0.25, y - H + 14 * s), (x + k * W * 0.25, y - 22 * s)], 3 * s, shade(col, -0.2))
    rrect(ctx, x - W / 2 + 6 * s, y - H + 6 * s, 10 * s, H - 26 * s, 4 * s, shade(col, 0.25), 0)


def pillow(ctx, x, y, w, h, col="#ffffff", ol=BOL):
    blob(ctx, [(x - w / 2, y - h * 0.1), (x - w * 0.42, y - h / 2), (x, y - h * 0.44), (x + w * 0.42, y - h / 2),
               (x + w / 2, y - h * 0.1), (x + w * 0.42, y + h / 2), (x, y + h * 0.44), (x - w * 0.42, y + h / 2)], col, ol)


def plastic_chair(ctx, x, y, s=1.0, col="#d8433a"):
    d = shade(col, -0.24)
    for sd in (-1, 1):
        line(ctx, [(x + sd * 34 * s, y - 92 * s), (x + sd * 40 * s, y - 6 * s)], 10 * s + 2 * BOL, OUTLINE)
        line(ctx, [(x + sd * 34 * s, y - 92 * s), (x + sd * 40 * s, y - 6 * s)], 10 * s, d)
    rrect(ctx, x - 48 * s, y - 224 * s, 96 * s, 114 * s, 24 * s, col, BOL)
    for k in (-1, 0, 1):
        rrect(ctx, x + k * 22 * s - 5 * s, y - 202 * s, 10 * s, 58 * s, 5 * s, d, 0)
    rrect(ctx, x - 56 * s, y - 110 * s, 112 * s, 20 * s, 8 * s, shade(col, 0.12), BOL)
    for sd in (-1, 1):
        poly(ctx, [(x + sd * 40 * s, y - 92 * s), (x + sd * 52 * s, y - 92 * s), (x + sd * 60 * s, y),
                   (x + sd * 46 * s, y)], col, BOL)


def plastic_stool(ctx, x, y, s=1.0, col="#2f7fc0"):
    d = shade(col, -0.3)
    poly(ctx, [(x - 32 * s, y - 92 * s), (x + 32 * s, y - 92 * s), (x + 44 * s, y), (x - 44 * s, y)], col, BOL)
    poly(ctx, [(x - 15 * s, y - 52 * s), (x + 15 * s, y - 52 * s), (x + 20 * s, y), (x - 20 * s, y)], d, BOL * 0.6)
    ellipse(ctx, x, y - 92 * s, 36 * s, 9 * s, shade(col, 0.18), BOL)


def wood_chair(ctx, x, y, s=1.0, col="#b07a45"):
    d = shade(col, -0.22)
    for sd in (-1, 1):
        rrect(ctx, x + sd * 44 * s - 6 * s, y - 232 * s, 12 * s, 232 * s, 4 * s, d, BOL)
    rrect(ctx, x - 52 * s, y - 236 * s, 104 * s, 24 * s, 9 * s, col, BOL)
    for k in (-1, 0, 1):
        rrect(ctx, x + k * 20 * s - 4 * s, y - 212 * s, 8 * s, 96 * s, 3 * s, col, BOL * 0.6)
    rrect(ctx, x - 56 * s, y - 114 * s, 112 * s, 18 * s, 5 * s, shade(col, 0.12), BOL)
    for sd in (-1, 1):
        rrect(ctx, x + sd * 48 * s - 6 * s, y - 98 * s, 12 * s, 98 * s, 3 * s, col, BOL)


def rattan_chair(ctx, x, y, s=1.0, col="#d1a564"):
    d = shade(col, -0.25)
    ctx.new_path()
    ctx.move_to(x - 58 * s, y - 110 * s)
    ctx.curve_to(x - 66 * s, y - 250 * s, x + 66 * s, y - 250 * s, x + 58 * s, y - 110 * s)
    ctx.close_path()
    fill_stroke(ctx, col, BOL)
    for k in range(1, 6):
        yy = y - 110 * s - k * 22 * s
        ww = 58 * s * (1 - (k / 6.2) ** 2.4)
        line(ctx, [(x - ww, yy), (x + ww, yy)], 2.2 * s, d)
    for k in (-2, -1, 0, 1, 2):
        line(ctx, [(x + k * 18 * s, y - 112 * s), (x + k * 13 * s, y - 228 * s)], 1.8 * s, d)
    rrect(ctx, x - 60 * s, y - 118 * s, 120 * s, 18 * s, 7 * s, shade(col, 0.1), BOL)
    for sd in (-1, 1):
        rrect(ctx, x + sd * 50 * s - 6 * s, y - 100 * s, 12 * s, 100 * s, 4 * s, d, BOL)


CHAIR_FN = {"plastic": plastic_chair, "stool": plastic_stool, "wood": wood_chair, "rattan": rattan_chair}


# --------------------------------------------------------------------------- tableware

def bowl(ctx, x, y, s=1.0, kind="noodle", col="#ffffff", band="#3a7fc0"):
    rw, ry = 31 * s, y - 25 * s
    ctx.new_path()
    ctx.move_to(x - rw, ry)
    ctx.curve_to(x - rw * 0.95, ry + 27 * s, x + rw * 0.95, ry + 27 * s, x + rw, ry)
    ctx.close_path()
    fill_stroke(ctx, col, BOL * 0.8)
    rrect(ctx, x - 12 * s, y - 6 * s, 24 * s, 6 * s, 2, shade(col, -0.1), BOL * 0.6)
    curve(ctx, (x - rw * 0.88, ry + 7 * s), (x, ry + 15 * s), (x + rw * 0.88, ry + 7 * s), 2.6 * s, band)
    if kind == "noodle":
        ellipse(ctx, x, ry, rw, 8 * s, "#e9b866", BOL * 0.8)
        for k in (-1, 0, 1):
            curve(ctx, (x + k * 12 * s - 8 * s, ry - 1 * s), (x + k * 12 * s, ry - 6 * s), (x + k * 12 * s + 8 * s, ry + 1 * s),
                  2.4 * s, "#f8de86")
        for dx in (-14, 10):
            ellipse(ctx, x + dx * s, ry + 1 * s, 7 * s, 3 * s, "#d98a6a", 0.8)
        for dx in (-4, 18, -20):
            circle(ctx, x + dx * s, ry - 1 * s, 2.4 * s, "#3f9a3a", 0)
        line(ctx, [(x + 6 * s, ry), (x + 34 * s, ry - 44 * s)], 3 * s, "#c08a4a")
        line(ctx, [(x + 12 * s, ry + 1 * s), (x + 42 * s, ry - 40 * s)], 3 * s, "#c08a4a")
    elif kind == "porridge":
        ellipse(ctx, x, ry, rw, 8 * s, "#f7f1e1", BOL * 0.8)
        for dx, dy, c in ((-12, -1, "#3f9a3a"), (6, 1, "#3f9a3a"), (16, -2, "#a8692a"), (-4, -2, "#a8692a"),
                          (-20, 1, "#3f9a3a"), (2, -3, "#d9a23a")):
            circle(ctx, x + dx * s, ry + dy * s, 2.6 * s, c, 0)
        ellipse(ctx, x + 10 * s, ry - 1 * s, 7 * s, 4 * s, "#f6c64a", 0.8)
        line(ctx, [(x - 6 * s, ry), (x - 26 * s, ry - 34 * s)], 4 * s, "#e4e8ec")
        ellipse(ctx, x - 27 * s, ry - 37 * s, 5 * s, 7 * s, "#e4e8ec", 0.8, rot=0.5)
    else:
        ellipse(ctx, x, ry, rw, 8 * s, "#d9a441", BOL * 0.8)
        for dx in (-12, 4, 14):
            circle(ctx, x + dx * s, ry, 3 * s, "#5aa83a", 0)


def plate(ctx, x, y, s=1.0, kind="rice"):
    ellipse(ctx, x, y - 5 * s, 42 * s, 10 * s, "#ffffff", BOL * 0.8)
    ellipse(ctx, x, y - 6 * s, 31 * s, 6.5 * s, "#eef2f5", 0)
    b = y - 8 * s
    if kind == "rice":
        blob(ctx, [(x - 24 * s, b), (x - 18 * s, b - 14 * s), (x - 4 * s, b - 20 * s), (x + 4 * s, b - 8 * s)], "#fbfaf4", 0.9)
        for k in range(3):
            ellipse(ctx, x + (8 + k * 7) * s, b - (6 + k * 3) * s, 9 * s, 4 * s, "#b5602e", 0.9, rot=-0.3)
        circle(ctx, x + 22 * s, b - 2 * s, 5 * s, "#e8483a", 0.8)
        ellipse(ctx, x - 26 * s, b - 1 * s, 7 * s, 3 * s, "#7cc04a", 0.8)
    elif kind == "friedrice":
        blob(ctx, [(x - 26 * s, b), (x - 14 * s, b - 16 * s), (x + 8 * s, b - 19 * s), (x + 24 * s, b)], "#eeb84e", 0.9)
        for dx, dy, c in ((-10, -8, "#e8603a"), (2, -12, "#5aa83a"), (12, -6, "#e8603a"), (-2, -4, "#5aa83a")):
            circle(ctx, x + dx * s, b + dy * s, 2.6 * s, c, 0)
        ellipse(ctx, x + 20 * s, b - 4 * s, 8 * s, 4 * s, "#7cc04a", 0.8)
    elif kind == "loklak":
        ellipse(ctx, x - 10 * s, b - 3 * s, 20 * s, 6 * s, "#6fb84a", 0.9)
        for k in range(5):
            rrect(ctx, x - 20 * s + k * 8 * s, b - 14 * s - (k % 2) * 5 * s, 10 * s, 9 * s, 2, "#7a3a20", 0.9)
        circle(ctx, x + 22 * s, b - 4 * s, 6 * s, "#e8483a", 0.8)
        ellipse(ctx, x + 10 * s, b - 2 * s, 6 * s, 3 * s, "#f6f2e6", 0.8)
    elif kind == "chakway":
        for k, rot in ((0, -0.15), (1, 0.12)):
            ellipse(ctx, x + (k * 6 - 3) * s, b - (6 + k * 6) * s, 30 * s, 6 * s, "#e0a344", 1.2, rot=rot)
            line(ctx, [(x - 20 * s, b - (6 + k * 6) * s), (x + 18 * s, b - (8 + k * 6) * s)], 1.4 * s, "#b77a28")
    elif kind == "spring":
        for k in range(3):
            ellipse(ctx, x - 16 * s + k * 16 * s, b - 7 * s, 8 * s, 16 * s, "#f3efe2", 1.0, rot=0.35)
            line(ctx, [(x - 18 * s + k * 16 * s, b - 14 * s), (x - 14 * s + k * 16 * s, b - 2 * s)], 2.2 * s, "#6fb84a")
            circle(ctx, x - 13 * s + k * 16 * s, b - 10 * s, 2.2 * s, "#f08a8a", 0)
        ellipse(ctx, x + 30 * s, b - 2 * s, 6 * s, 3 * s, "#c0392b", 0.8)
    elif kind == "amok":
        poly(ctx, [(x - 22 * s, b - 22 * s), (x + 22 * s, b - 22 * s), (x + 16 * s, b), (x - 16 * s, b)], "#4f9a3a", 1.2)
        for k in (-1, 0, 1):
            line(ctx, [(x + k * 13 * s, b - 22 * s), (x + k * 10 * s, b)], 1.2 * s, "#2f6a2a")
        ellipse(ctx, x, b - 22 * s, 22 * s, 6 * s, "#f2c14e", 1.0)
        line(ctx, [(x - 8 * s, b - 23 * s), (x + 8 * s, b - 22 * s)], 2.2 * s, "#e0402a")
        circle(ctx, x + 4 * s, b - 25 * s, 2.4 * s, "#3f9a3a", 0)
    elif kind == "noodles":
        blob(ctx, [(x - 26 * s, b), (x - 12 * s, b - 15 * s), (x + 10 * s, b - 17 * s), (x + 26 * s, b)], "#c98a3e", 0.9)
        for k in range(4):
            curve(ctx, (x - 18 * s + k * 9 * s, b - 4 * s), (x - 14 * s + k * 9 * s, b - 16 * s),
                  (x - 8 * s + k * 9 * s, b - 6 * s), 1.6 * s, "#9a5a22")
        circle(ctx, x + 8 * s, b - 12 * s, 3 * s, "#5aa83a", 0)
        circle(ctx, x - 6 * s, b - 10 * s, 3 * s, "#e8603a", 0)
    elif kind == "cake":
        poly(ctx, [(x - 20 * s, b), (x + 14 * s, b - 4 * s), (x + 14 * s, b - 26 * s), (x - 20 * s, b - 22 * s)], "#f6dfb0", 1.2)
        poly(ctx, [(x - 20 * s, b - 22 * s), (x + 14 * s, b - 26 * s), (x + 22 * s, b - 32 * s), (x - 10 * s, b - 28 * s)],
             "#f3a6b8", 1.2)
        line(ctx, [(x - 20 * s, b - 12 * s), (x + 14 * s, b - 15 * s)], 2.4 * s, "#f3a6b8")
        circle(ctx, x + 4 * s, b - 34 * s, 5 * s, "#d8333a", 1.0)
    elif kind == "cookies":
        for k, (dx, dy) in enumerate(((-14, -4), (10, -4), (-2, -12))):
            ellipse(ctx, x + dx * s, b + dy * s, 14 * s, 6 * s, "#d9a35a", 1.0)
            for m in range(3):
                circle(ctx, x + (dx - 5 + m * 5) * s, b + (dy - 1 + (m % 2) * 2) * s, 1.6 * s, "#5a3420", 0)


def _ice(ctx, x, y, s):
    ctx.new_path()
    rrect_path(ctx, x - 6 * s, y - 5 * s, 12 * s, 10 * s, 3 * s)
    ctx.set_source_rgba(1, 1, 1, 0.65)
    ctx.fill()


def glass(ctx, x, y, s=1.0, liquid="#c8742a", top=None, h=62, ice=True, straw="#e84a5f", lemon=False, wide=20):
    H, wt, wb = h * s, wide * s, wide * 0.78 * s
    yt = y - H

    def wx(yy):
        return wt + (wb - wt) * (yy - yt) / H

    body = [(x - wt, yt), (x + wt, yt), (x + wb, y), (x - wb, y)]
    poly(ctx, body, (0.86, 0.93, 0.97), 0)
    lv = yt + 0.15 * H
    poly(ctx, [(x - wx(lv), lv), (x + wx(lv), lv), (x + wb, y), (x - wb, y)], liquid, 0)
    if top:
        mid = lv + 0.38 * H
        poly(ctx, [(x - wx(lv), lv), (x + wx(lv), lv), (x + wx(mid), mid), (x - wx(mid), mid)], top, 0)
    if ice:
        for dx, dy in ((-7, 5), (6, 3), (-1, 15)):
            _ice(ctx, x + dx * s, lv + dy * s, s)
    if straw:
        line(ctx, [(x + 3 * s, y - 10 * s), (x + 11 * s, yt - 24 * s)], 5 * s + 2.2, OUTLINE)
        line(ctx, [(x + 3 * s, y - 10 * s), (x + 11 * s, yt - 24 * s)], 5 * s, straw)
    line(ctx, [(x - wt * 0.62, yt + 6 * s), (x - wb * 0.62, y - 6 * s)], 2.5 * s, "#ffffff", 0.75)
    poly(ctx, body, None, BOL * 0.8)
    if lemon:
        circle(ctx, x - wt + 2 * s, yt + 3 * s, 9 * s, "#f6e04a", 1.4)
        for k in range(3):
            a = k * math.pi / 3
            line(ctx, [(x - wt + 2 * s - math.cos(a) * 7 * s, yt + 3 * s - math.sin(a) * 7 * s),
                       (x - wt + 2 * s + math.cos(a) * 7 * s, yt + 3 * s + math.sin(a) * 7 * s)], 1.2, "#e3b82a")


def pitcher(ctx, x, y, s=1.0, liquid="#d58a3a"):
    curve(ctx, (x + 20 * s, y - 70 * s), (x + 48 * s, y - 52 * s), (x + 20 * s, y - 22 * s), 8 * s + 2 * BOL * 0.8, OUTLINE)
    curve(ctx, (x + 20 * s, y - 70 * s), (x + 48 * s, y - 52 * s), (x + 20 * s, y - 22 * s), 8 * s, "#dfe9ef")
    body = [(x - 24 * s, y), (x - 26 * s, y - 70 * s), (x - 34 * s, y - 86 * s), (x + 24 * s, y - 86 * s),
            (x + 26 * s, y - 70 * s), (x + 24 * s, y)]
    poly(ctx, body, (0.86, 0.93, 0.97), 0)
    poly(ctx, [(x - 25 * s, y - 60 * s), (x + 25 * s, y - 60 * s), (x + 24 * s, y), (x - 24 * s, y)], liquid, 0)
    for dx, dy in ((-10, -54), (6, -50), (-2, -40)):
        _ice(ctx, x + dx * s, y + dy * s, s)
    line(ctx, [(x - 16 * s, y - 76 * s), (x - 16 * s, y - 8 * s)], 3 * s, "#ffffff", 0.7)
    poly(ctx, body, None, BOL * 0.8)


def teapot(ctx, x, y, s=1.0, col="#f2ead8", band="#3a7fc0"):
    curve(ctx, (x + 26 * s, y - 36 * s), (x + 52 * s, y - 28 * s), (x + 28 * s, y - 10 * s), 6 * s + 2 * BOL * 0.8, OUTLINE)
    curve(ctx, (x + 26 * s, y - 36 * s), (x + 52 * s, y - 28 * s), (x + 28 * s, y - 10 * s), 6 * s, col)
    poly(ctx, [(x - 24 * s, y - 24 * s), (x - 50 * s, y - 46 * s), (x - 44 * s, y - 50 * s), (x - 18 * s, y - 34 * s)],
         col, BOL * 0.8)
    ellipse(ctx, x, y - 24 * s, 32 * s, 24 * s, col, BOL * 0.8)
    curve(ctx, (x - 28 * s, y - 26 * s), (x, y - 16 * s), (x + 28 * s, y - 26 * s), 3 * s, band)
    ellipse(ctx, x, y - 46 * s, 16 * s, 5 * s, shade(col, -0.08), BOL * 0.7)
    circle(ctx, x, y - 54 * s, 5 * s, band, BOL * 0.6)


def cup(ctx, x, y, s=1.0, col="#f2ead8", liquid="#b8792a"):
    poly(ctx, [(x - 12 * s, y - 22 * s), (x + 12 * s, y - 22 * s), (x + 9 * s, y), (x - 9 * s, y)], col, BOL * 0.7)
    ellipse(ctx, x, y - 22 * s, 12 * s, 3.5 * s, liquid, BOL * 0.6)


def tissue_box(ctx, x, y, s=1.0, col="#f08ab0"):
    rrect(ctx, x - 26 * s, y - 30 * s, 52 * s, 30 * s, 4 * s, col, BOL * 0.8)
    blob(ctx, [(x - 10 * s, y - 30 * s), (x - 4 * s, y - 50 * s), (x + 8 * s, y - 44 * s), (x + 12 * s, y - 30 * s)],
         "#ffffff", 1.2)
    flower(ctx, x - 10 * s, y - 15 * s, 8 * s, "#ffffff", "#f6d23a", 0)


def chopstick_cup(ctx, x, y, s=1.0):
    for k in range(5):
        line(ctx, [(x - 6 * s + k * 3 * s, y - 20 * s), (x - 12 * s + k * 6 * s, y - 62 * s)], 2.4 * s, "#c08a4a")
    rrect(ctx, x - 13 * s, y - 34 * s, 26 * s, 34 * s, 5 * s, "#7a8a96", BOL * 0.8)


def sauce_bottle(ctx, x, y, s=1.0, col="#d8333a", cap="#f2f2f2"):
    rrect(ctx, x - 4 * s, y - 62 * s, 8 * s, 14 * s, 2, cap, BOL * 0.6)
    rrect(ctx, x - 10 * s, y - 50 * s, 20 * s, 50 * s, 7 * s, col, BOL * 0.8)
    line(ctx, [(x - 5 * s, y - 42 * s), (x - 5 * s, y - 8 * s)], 2.4 * s, "#ffffff", 0.55)


def bottle(ctx, x, y, s=1.0, col="#a8642a"):
    ctx.new_path()
    ctx.move_to(x - 11 * s, y)
    ctx.line_to(x - 11 * s, y - 46 * s)
    ctx.curve_to(x - 11 * s, y - 58 * s, x - 5 * s, y - 62 * s, x - 5 * s, y - 74 * s)
    ctx.line_to(x + 5 * s, y - 74 * s)
    ctx.curve_to(x + 5 * s, y - 62 * s, x + 11 * s, y - 58 * s, x + 11 * s, y - 46 * s)
    ctx.line_to(x + 11 * s, y)
    ctx.close_path()
    fill_stroke(ctx, col, BOL * 0.8)
    rrect(ctx, x - 6 * s, y - 80 * s, 12 * s, 7 * s, 2, "#d9b53a", BOL * 0.5)
    line(ctx, [(x - 6 * s, y - 40 * s), (x - 6 * s, y - 8 * s)], 2.4 * s, "#ffffff", 0.45)


def candle_jar(ctx, x, y, s=1.0, t=0.0):
    rrect(ctx, x - 14 * s, y - 30 * s, 28 * s, 30 * s, 6 * s, (0.95, 0.85, 0.55), BOL * 0.7)
    rrect(ctx, x - 9 * s, y - 20 * s, 18 * s, 18 * s, 3 * s, "#fff4d6", 0)
    fl = 1.0 + 0.06 * math.sin(t * 3.1) + 0.04 * math.sin(t * 5.3)
    ellipse(ctx, x, y - 26 * s, 4 * s, 8 * s * fl, "#ffcc33", 0)
    ellipse(ctx, x, y - 24 * s, 2 * s, 4 * s * fl, "#fff6c8", 0)


def small_pot_plant(ctx, x, y, s=1.0, pot="#d9774a", leaf="#4f9e46"):
    for k in range(5):
        a = -math.pi / 2 + (k - 2) * 0.45
        ellipse(ctx, x + math.cos(a) * 12 * s, y - 24 * s + math.sin(a) * 12 * s, 6 * s, 11 * s,
                shade(leaf, -0.08 * (k % 2)), 1.0, rot=a + math.pi / 2)
    poly(ctx, [(x - 13 * s, y - 22 * s), (x + 13 * s, y - 22 * s), (x + 10 * s, y), (x - 10 * s, y)], pot, BOL * 0.7)


# --------------------------------------------------------------------------- tables

TSTYLE = {
    "cloth": dict(leg="#c9ced6", legw=12, inset=30, cloth=("#d8433a", "#fff6ea"), drop=56),
    "steel": dict(leg="#9aa4ad", legw=10, inset=22, sheet="#f39cbc", drop=30),
    "wood": dict(top="#c98d55", edge="#9c6236", leg="#8a5430", legw=18, inset=26, apron=26),
    "pub": dict(leg="#5e3a22", legw=16, inset=28, cloth=("#2f7a52", "#f4efe2"), drop=44),
}


def table(ctx, cx, w, style="wood", top=TABLE_TOP):
    S = TSTYLE[style]
    x0, x1 = cx - w / 2, cx + w / 2
    floor = 948
    for lx in (x0 + S["inset"], x1 - S["inset"]):
        rrect(ctx, lx - S["legw"] / 2, top + 10, S["legw"], floor - top - 10, min(4, S["legw"] / 2), S["leg"], BOL)
        ellipse(ctx, lx, floor, S["legw"] * 0.8, 4, shade(S["leg"], -0.35), 0)
    surf = [(x0 + 16, top - 18), (x1 - 16, top - 18), (x1 + 6, top + 6), (x0 - 6, top + 6)]
    if S.get("cloth"):
        pat = check_pattern(S["cloth"][0], S["cloth"][1], 13)
        d = S["drop"]
        n = max(4, int(w / 70))
        ctx.new_path()
        ctx.move_to(x0 - 8, top + 2)
        ctx.line_to(x1 + 8, top + 2)
        ctx.line_to(x1 + 12, top + d)
        for i in range(n):
            xa = x1 + 12 - (w + 24) * i / n
            xb = x1 + 12 - (w + 24) * (i + 1) / n
            ctx.curve_to(xa - 8, top + d + 13, xb + 8, top + d + 13, xb, top + d)
        ctx.close_path()
        fill_stroke(ctx, pat, BOL)
        for i in range(1, n):
            xx = x0 - 8 + (w + 16) * i / n
            line(ctx, [(xx, top + 12), (xx, top + d + 6)], 3, (0, 0, 0), 0.10)
        poly(ctx, surf, pat, BOL)
        line(ctx, [(x0 + 30, top - 10), (x0 + w * 0.42, top - 10)], 4, "#ffffff", 0.35)
        return
    if S.get("sheet"):
        d = S["drop"]
        ctx.new_path()
        ctx.move_to(x0 - 8, top + 2)
        ctx.line_to(x1 + 8, top + 2)
        ctx.line_to(x1 + 10, top + d)
        ctx.line_to(x0 - 10, top + d)
        ctx.close_path()
        fill_stroke(ctx, S["sheet"], BOL)
        r = rng(int(cx))
        k = x0 + 18
        while k < x1 - 10:
            flower(ctx, k, top + d * 0.55 + r.uniform(-4, 4), 7, "#ffffff", "#f6d23a", 0)
            k += 46
        poly(ctx, surf, S["sheet"], BOL)
        k = x0 + 40
        while k < x1 - 30:
            flower(ctx, k, top - 6, 6, "#ffffff", "#f6d23a", 0)
            k += 70
        return
    if S.get("apron"):
        rrect(ctx, x0 + 10, top + 12, w - 20, S["apron"], 3, shade(S["edge"], -0.08), BOL)
    poly(ctx, surf, S["top"], BOL)
    line(ctx, [(x0 + 30, top - 11), (x0 + w * 0.42, top - 11)], 3, shade(S["top"], 0.4))
    rrect(ctx, x0 - 8, top + 3, w + 16, 15, 4, S["edge"], BOL)


def table_conf(default_tables=(700, 1220), default_w=520):
    tabs = B.CUR.get("tables", list(default_tables))
    if not tabs:
        tabs = []
    w = float(P("table_w", default_w))
    chairs = B.CUR.get("chairs")
    if chairs is None:
        chairs = [cx + k * w * 0.3 for cx in tabs for k in (-1, 0, 1)]
    return [float(x) for x in tabs], w, [float(x) for x in (chairs or [])]


def _places(cx, w):
    n = 3 if w >= 380 else 2
    return [cx + (i - (n - 1) / 2.0) * w * 0.29 for i in range(n)]


def table_items(ctx, cx, w, menu, top=TABLE_TOP, ends=(True, True)):
    """Static tableware for one table (steam is drawn separately by table_steam)."""
    y = top - 3
    x0, x1 = cx - w / 2, cx + w / 2
    # shared things first (further back)
    if menu == "restaurant":
        if ends[0]:
            pitcher(ctx, x0 + 36, y - 2, 0.95)
        if ends[1]:
            sauce_bottle(ctx, x1 - 28, y - 2, 0.9, "#d8333a")
            tissue_box(ctx, x1 - 66, y, 0.85)
    elif menu == "bobor":
        if ends[0]:
            teapot(ctx, x0 + 48, y - 2, 0.9)
        if ends[1]:
            sauce_bottle(ctx, x1 - 26, y - 2, 0.85, "#d8333a")
            chopstick_cup(ctx, x1 - 54, y - 2, 0.85)
    elif menu == "cafe":
        if ends[1]:
            small_pot_plant(ctx, x1 - 36, y - 2, 1.15, "#f2efe6", "#5aa84a")
    elif menu == "dinner":
        if ends[0]:
            bottle(ctx, x0 + 32, y - 2, 0.9, "#8a5a2a")
        if ends[1]:
            sauce_bottle(ctx, x1 - 30, y - 2, 0.85, "#d8333a")
    places = _places(cx, w)
    k0 = int(abs(cx) // 37)
    for i, px in enumerate(places):
        sd = 1 if (i + k0) % 2 == 0 else -1
        gx = px + sd * w * 0.115
        j = (i + k0) % 3
        if menu == "restaurant":
            liq, tp = [("#d2843a", None), ("#6b3f22", "#ead7b8"), ("#c6e07a", None)][(i + k0 + 1) % 3]
            glass(ctx, gx, y, 0.95, liq, tp, lemon=(liq == "#c6e07a"))
            if j == 0:
                bowl(ctx, px, y, 1.0, "noodle")
            else:
                plate(ctx, px, y, 1.0, "rice" if j == 1 else "friedrice")
        elif menu == "bobor":
            if j == 1:
                plate(ctx, gx, y, 0.9, "chakway")
            else:
                cup(ctx, gx, y, 1.0)
            bowl(ctx, px, y, 1.0, "porridge", "#ffffff", "#2f8a6a")
        elif menu == "cafe":
            liq, tp, st = [("#7a4a2a", "#f1e3c8", "#2f8a5a"), ("#8fc25a", "#eef3dc", "#2f8a5a"),
                           ("#e09a3a", None, "#e84a5f"), ("#f07a9a", None, "#f2c14e")][(i + k0) % 4]
            if j == 0:
                plate(ctx, px, y, 0.9, "cake")
            elif j == 1:
                ellipse(ctx, px, y - 3, 30, 7, "#ffffff", BOL * 0.7)
                cup(ctx, px, y - 4, 1.2, "#ffffff", "#7a4a2a")
            else:
                plate(ctx, px, y, 0.9, "cookies")
            glass(ctx, gx, y, 1.05, liq, tp, h=70, straw=st, lemon=(liq == "#e09a3a"))
            if j == 2:
                small_pot_plant(ctx, px - sd * w * 0.12, y, 1.0)
        elif menu == "dinner":
            liq = ["#f2a531", "#f05a7a", "#e8e070", "#d06ad0"][(i + k0) % 4]
            glass(ctx, gx, y, 1.0, liq, None, h=66, straw="#ffffff", ice=False)
            plate(ctx, px, y, 1.0, ["amok", "noodles", "loklak", "spring"][(i + k0) % 4])


def table_steam(ctx, cx, w, menu, t, top=TABLE_TOP):
    y = top - 3
    places = _places(cx, w)
    k0 = int(abs(cx) // 37)
    for i, px in enumerate(places):
        j = (i + k0) % 3
        if menu == "bobor" or (menu == "restaurant" and j == 0):
            steam(ctx, px, y - 30, t, 1.0, 4, 0.42, 90, seed=i + k0)
        elif menu == "dinner" and (i + k0) % 4 in (0, 2):
            steam(ctx, px, y - 26, t, 0.8, 4, 0.30, 80, seed=i + k0)


def draw_tables(ctx, tabs, w, style, menu, t, items=True):
    if not tabs:
        return
    key = ("tables", tuple(tabs), w, style, menu, bool(items))

    def draw(g):
        st = sorted(tabs)
        for i, cx in enumerate(st):
            left_join = i > 0 and (cx - w / 2) - (st[i - 1] + w / 2) < 60
            right_join = i + 1 < len(st) and (st[i + 1] - w / 2) - (cx + w / 2) < 60
            table(g, cx, w, style)
            if items:
                table_items(g, cx, w, menu, ends=(not left_join, not right_join))

    cached(ctx, key, draw)
    if items:
        for cx in tabs:
            table_steam(ctx, cx, w, menu, t)


def draw_chairs(ctx, chairs, kind, cols, y=925, s=1.0):
    if not chairs:
        return
    key = ("chairs", tuple(chairs), kind, tuple(cols), y, s)

    def draw(g):
        for i, x in enumerate(chairs):
            CHAIR_FN[kind](g, x, y, s, cols[i % len(cols)])

    cached(ctx, key, draw)


# --------------------------------------------------------------------------- outdoor props

def tuktuk(ctx, x, y, s=1.0, col="#2f6fb2", roof="#20456e", facing=1, lit=False):
    """Cambodian remork: motorbike pulling a roofed carriage (side view). (x, y) = ground under the carriage."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * facing, s)

    def wheel(wx, r):
        circle(ctx, wx, -r, r, "#2a2a30", BOL)
        circle(ctx, wx, -r, r * 0.55, "#b9c0c8", BOL * 0.6)
        circle(ctx, wx, -r, r * 0.18, "#5a5f66", 0)

    for px in (-205, 52):
        rrect(ctx, px - 5, -250, 10, 190, 3, "#c9ced6", BOL * 0.8)
    rrect(ctx, -200, -186, 250, 106, 4, "#3a2a24", 0)
    rrect(ctx, -196, -122, 46, 50, 8, "#c0392b", BOL * 0.7)
    rrect(ctx, 0, -122, 46, 50, 8, "#c0392b", BOL * 0.7)
    rrect(ctx, -200, -88, 250, 22, 6, "#7a2a22", BOL * 0.7)
    rrect(ctx, -212, -78, 274, 44, 6, col, BOL)
    line(ctx, [(-206, -60), (56, -60)], 3, shade(col, 0.4))
    rrect(ctx, -232, -268, 314, 26, 8, roof, BOL)
    for k in range(10):
        cx_ = -226 + k * 30.2
        ellipse(ctx, cx_ + 15, -242, 15, 9, "#f2c14e" if k % 2 else "#e84a5f", BOL * 0.5)
    for sd in (-218, 66):
        rrect(ctx, sd - 8, -240, 16, 70, 6, "#f4efe2", BOL * 0.6)
    wheel(-80, 34)
    line(ctx, [(52, -58), (150, -80)], 7 + 2 * BOL * 0.6, OUTLINE)
    line(ctx, [(52, -58), (150, -80)], 7, "#8a8f96")
    # motorbike (underbone style) pulling the carriage
    wheel(160, 30)
    wheel(304, 30)
    ctx.new_path()
    ctx.arc(304, -30, 38, math.pi * 1.05, math.pi * 1.6)
    src(ctx, OUTLINE)
    ctx.set_line_width(9)
    ctx.stroke()
    line(ctx, [(122, -40), (190, -40)], 7 + 2 * BOL * 0.6, OUTLINE)
    line(ctx, [(122, -40), (190, -40)], 7, "#b9c0c8")
    blob(ctx, [(118, -66), (150, -86), (214, -84), (236, -66), (262, -70), (282, -108), (296, -112), (290, -74),
               (262, -42), (214, -44), (160, -46), (122, -50)], "#e84a5f", BOL)
    curve(ctx, (226, -62), (250, -60), (276, -100), 3, shade("#e84a5f", -0.3))
    rrect(ctx, 122, -100, 98, 22, 10, "#2a2a30", BOL * 0.8)
    line(ctx, [(304, -30), (282, -150)], 7 + 2 * BOL * 0.7, OUTLINE)
    line(ctx, [(304, -30), (282, -150)], 7, "#b9c0c8")
    rrect(ctx, 272, -140, 34, 26, 10, "#e84a5f", BOL * 0.8)
    ellipse(ctx, 304, -128, 8, 10, "#fff3b0" if lit else "#e8eef2", BOL * 0.7)
    line(ctx, [(262, -156), (296, -150)], 6 + 2 * BOL * 0.6, OUTLINE)
    line(ctx, [(262, -156), (296, -150)], 6, "#2a2a30")
    line(ctx, [(280, -152), (276, -174)], 2.4, OUTLINE)
    ellipse(ctx, 276, -178, 7, 5, "#c9ced6", 1.2)
    ctx.restore()


def scooter(ctx, x, y, s=1.0, col="#e84a5f", facing=1):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * facing, s)
    for wx in (-62, 70):
        circle(ctx, wx, -26, 26, "#2a2a30", BOL)
        circle(ctx, wx, -26, 12, "#b9c0c8", BOL * 0.6)
    line(ctx, [(70, -26), (54, -128)], 6 + BOL * 1.4, OUTLINE)
    line(ctx, [(70, -26), (54, -128)], 6, "#b9c0c8")
    blob(ctx, [(-100, -46), (-94, -78), (-20, -84), (0, -56), (34, -54), (44, -116), (66, -120), (70, -88), (56, -40),
               (20, -24), (-40, -24), (-90, -30)], col, BOL)
    curve(ctx, (-2, -54), (20, -44), (36, -60), 2.6, shade(col, -0.3))
    rrect(ctx, -96, -98, 84, 20, 9, "#2a2a30", BOL * 0.8)
    line(ctx, [(36, -132), (72, -128)], 6 + BOL * 1.2, OUTLINE)
    line(ctx, [(36, -132), (72, -128)], 6, "#2a2a30")
    ellipse(ctx, 68, -110, 7, 9, "#f2f2e8", BOL * 0.6)
    ctx.restore()


def crown_mass(ctx, pts, col, ol=BOL, polys=()):
    """Union of circles (x, y, r) (+ optional polygons) with a single outer outline (canopies, bushes, hills)."""
    ctx.new_path()
    for pp in polys:
        poly_path(ctx, pp)
    for x, y, r in pts:
        ctx.new_sub_path()
        ctx.arc(x, y, r, 0, TAU)
    if ol:
        src(ctx, OUTLINE)
        ctx.set_line_width(ol * 2)
        ctx.stroke_preserve()
    src(ctx, col)
    ctx.fill()


def tall_tree(ctx, x, base, h, s=1.0, col="#4f8f45", trunk="#bfb29c", seed=0):
    """Angkor-forest tree: tall straight pale trunk with a high crown."""
    r = rng(seed + int(x))
    top = base - h
    poly(ctx, [(x - 20 * s, base), (x - 11 * s, top + 40 * s), (x + 11 * s, top + 40 * s), (x + 20 * s, base)], trunk, BOL)
    for k in range(4):
        yy = base - h * r.uniform(0.15, 0.8)
        line(ctx, [(x - 10 * s, yy), (x + 8 * s, yy - 4)], 2, shade(trunk, -0.3))
    line(ctx, [(x + 8 * s, base - 4), (x + 5 * s, top + 60 * s)], 4 * s, shade(trunk, 0.25))
    for a in (-0.7, 0.6):
        line(ctx, [(x, top + 70 * s), (x + math.sin(a) * 90 * s, top + 10 * s)], 9 * s, trunk)
    blobs = [(0, 0, 90), (-90, 26, 70), (90, 22, 74), (-150, 60, 52), (150, 58, 56), (-40, -40, 66), (50, -36, 64),
             (0, 50, 60)]
    crown_mass(ctx, [(x + bx * s, top + by * s, br * s * r.uniform(0.9, 1.1)) for bx, by, br in blobs], col)
    for bx, by, br in blobs[:5]:
        ellipse(ctx, x + (bx - br * 0.2) * s, top + (by - br * 0.3) * s, br * 0.5 * s, br * 0.32 * s, shade(col, 0.16), 0)


def bougain(ctx, x, y, s=1.0, seed=0, n=16, sx=60, sy=40, cols=PURPLES, leaf="#3f8f3a"):
    """Bougainvillea clump: leaves and purple/magenta bract clusters."""
    r = rng(seed)
    for _ in range(int(n * 0.7)):
        ex, ey = x + r.uniform(-sx, sx) * s, y + r.uniform(-sy, sy) * s
        ellipse(ctx, ex, ey, 9 * s, 5 * s, shade(leaf, r.uniform(-0.15, 0.1)), 1.0, rot=r.uniform(0, 3))
    for _ in range(n):
        fx, fy = x + r.uniform(-sx, sx) * s, y + r.uniform(-sy, sy) * s
        c = r.choice(cols)
        rr = r.uniform(5, 7.5) * s
        for k in range(3):
            a = k * TAU / 3 + r.uniform(0, 1)
            circle(ctx, fx + math.cos(a) * rr * 0.75, fy + math.sin(a) * rr * 0.75, rr, c, 0.9)
        circle(ctx, fx, fy, 1.6 * s, "#fff3b0", 0)


def bougain_cascade(ctx, x, y, length, s=1.0, seed=0, drift=0.0):
    r = rng(seed)
    n = max(2, int(length / 26))
    for i in range(n):
        u = i / max(1, n - 1)
        bougain(ctx, x + drift * u * u + r.uniform(-8, 8), y + u * length, s * (1.0 - 0.35 * u), seed + i * 7,
                n=9, sx=34 * (1 - 0.3 * u), sy=18)


def lavender(ctx, x, y, s=1.0, seed=0, w=70):
    r = rng(seed)
    ellipse(ctx, x, y - 14 * s, w * s, 22 * s, "#6f9a5a", BOL * 0.8)
    for k in range(14):
        sx = x + (k / 13.0 - 0.5) * w * 1.7 * s + r.uniform(-4, 4)
        hh = r.uniform(46, 70) * s * (1 - abs(k / 13.0 - 0.5) * 0.7)
        lean = (sx - x) * 0.25
        line(ctx, [(sx, y - 20 * s), (sx + lean, y - 20 * s - hh)], 2.2 * s, "#5d8a4a")
        for j in range(5):
            yy = y - 20 * s - hh + j * 6 * s
            ellipse(ctx, sx + lean * (1 - j * 0.06), yy, 3.6 * s, 4.6 * s, LAV[(k + j) % 3], 0.6)


def potted_palm(ctx, x, y, s=1.0, pot="#c7744a", leaf="#3f9a40"):
    for k in range(9):
        a = -math.pi / 2 + (k - 4) * 0.36
        L = (150 - abs(k - 4) * 12) * s
        ex, ey = x + math.cos(a) * L, y - 80 * s + math.sin(a) * L * 0.9 + abs(k - 4) * 14 * s
        mx, my = x + math.cos(a) * L * 0.5, y - 80 * s + math.sin(a) * L * 0.6
        curve(ctx, (x, y - 70 * s), (mx, my - 20 * s), (ex, ey), 3 * s, "#2f6a2a")
        for j in range(1, 8):
            u = j / 8.0
            px = (1 - u) ** 2 * x + 2 * (1 - u) * u * mx + u * u * ex
            py = (1 - u) ** 2 * (y - 70 * s) + 2 * (1 - u) * u * (my - 20 * s) + u * u * ey
            ll = 22 * s * math.sin(math.pi * u) + 6 * s
            for sd in (-1, 1):
                ellipse(ctx, px + sd * ll * 0.4, py + ll * 0.3, ll * 0.5, 3.4 * s, shade(leaf, -0.06 * (j % 2)), 0.8,
                        rot=a + sd * 1.2)
    poly(ctx, [(x - 40 * s, y - 70 * s), (x + 40 * s, y - 70 * s), (x + 30 * s, y), (x - 30 * s, y)], pot, BOL)
    rrect(ctx, x - 46 * s, y - 80 * s, 92 * s, 16 * s, 4 * s, shade(pot, 0.1), BOL)


def frond(ctx, x, y, ang, L, droop, col, s=1.0, leaflet=15):
    pts = [(x, y)]
    px, py = x, y
    for i in range(1, 13):
        u = i / 12.0
        a = ang + droop * u * u
        px += math.cos(a) * L / 12
        py += math.sin(a) * L / 12
        pts.append((px, py))
    line(ctx, pts, 2.2 * s, shade(col, -0.35))
    for i in range(1, 13):
        u = i / 12.0
        a = ang + droop * u * u
        ll = (leaflet * math.sin(math.pi * min(1, u * 1.1)) + 3) * s
        for sd in (-1, 1):
            aa = a + sd * 1.15
            ellipse(ctx, pts[i][0] + math.cos(aa) * ll * 0.5, pts[i][1] + math.sin(aa) * ll * 0.5, ll * 0.55, 3.2 * s,
                    shade(col, 0.08 * ((i + sd) % 2)), 0.7, rot=aa)


def fern_pot(ctx, x, y, s=1.0, seed=0, pot="#f2efe6", col="#5fae4a"):
    """Hanging Boston fern: pot rim centred at (x, y), fronds spilling over it."""
    r = rng(seed)
    for k in range(12):
        side = -1 if k % 2 else 1
        ang = -math.pi / 2 + side * r.uniform(0.5, 1.5)
        droop = side * r.uniform(1.4, 2.2)
        frond(ctx, x + side * r.uniform(2, 14) * s, y + 2 * s, ang, r.uniform(110, 170) * s, droop,
              shade(col, r.uniform(-0.12, 0.08)), s)
    ctx.new_path()
    ctx.move_to(x - 40 * s, y)
    ctx.curve_to(x - 40 * s, y + 46 * s, x + 40 * s, y + 46 * s, x + 40 * s, y)
    ctx.close_path()
    fill_stroke(ctx, pot, BOL)
    curve(ctx, (x - 36 * s, y + 12 * s), (x, y + 20 * s), (x + 36 * s, y + 12 * s), 2.5 * s, shade(pot, -0.25))
    for k in range(5):
        side = -1 if k % 2 else 1
        frond(ctx, x + side * r.uniform(0, 10) * s, y, -math.pi / 2 + side * r.uniform(0.2, 0.9), r.uniform(70, 110) * s,
              side * r.uniform(1.6, 2.4), shade(col, 0.06), s, 12)


def pothos(ctx, x, y, length, s=1.0, seed=0, sway=0.0):
    r = rng(seed)
    pts = []
    n = max(3, int(length / 22))
    for i in range(n + 1):
        u = i / n
        pts.append((x + math.sin(u * 3 + seed) * 14 * s + sway * u * u, y + u * length))
    line(ctx, pts, 2.2 * s, "#3f7a32")
    for i, (px, py) in enumerate(pts[1:]):
        sd = 1 if i % 2 else -1
        c = r.choice(("#4caf50", "#6cc04a", "#3f9a3a"))
        ellipse(ctx, px + sd * 9 * s, py, 10 * s, 7 * s, c, 0.9, rot=sd * 0.6)
        line(ctx, [(px + sd * 4 * s, py), (px + sd * 14 * s, py - 1 * s)], 1.2, "#e8f0a0", 0.7)


def monstera(ctx, x, y, s=1.0, ang=-1.57, col="#3f8f3a"):
    """Monstera leaf (heart shape with holes) on a stem from (x, y) pointing at angle ang."""
    L = 150 * s
    bx, by = x + math.cos(ang) * L * 0.35, y + math.sin(ang) * L * 0.35
    for w_, c_ in ((5 * s + 2.4, OUTLINE), (5 * s, "#3f7a32")):
        curve(ctx, (x, y), ((x + bx) / 2 + 6 * s, (y + by) / 2), (bx, by), w_, c_)
    Lh, W = L * 0.85, L * 0.42
    ctx.save()
    ctx.translate(bx, by)
    ctx.rotate(ang + math.pi / 2)

    def leaf_path():
        ctx.new_path()
        ctx.move_to(0, 4 * s)
        ctx.curve_to(-W * 1.25, 0, -W * 0.9, -Lh * 0.95, 0, -Lh)
        ctx.curve_to(W * 0.9, -Lh * 0.95, W * 1.25, 0, 0, 4 * s)
        ctx.close_path()

    holes = []
    for sd in (-1, 1):
        for f, hx in ((0.25, 0.42), (0.47, 0.44), (0.69, 0.36)):
            holes.append((sd * W * hx, -Lh * f, W * 0.17, 4.2 * s, sd * 0.45))
    ctx.push_group()
    leaf_path()
    src(ctx, col)
    ctx.fill()
    ctx.set_operator(cairo.OPERATOR_CLEAR)
    for hx, hy, rx, ry, rot in holes:
        ctx.new_path()
        ellipse_path(ctx, hx, hy, rx, ry, rot)
        ctx.fill()
    ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.pop_group_to_source()
    ctx.paint()
    leaf_path()
    fill_stroke(ctx, None, BOL * 0.8)
    for hx, hy, rx, ry, rot in holes:
        ctx.new_path()
        ellipse_path(ctx, hx, hy, rx, ry, rot)
        fill_stroke(ctx, None, 1.4)
    line(ctx, [(0, 0), (0, -Lh * 0.9)], 2.4 * s, shade(col, -0.3))
    for sd in (-1, 1):
        for f in (0.36, 0.58, 0.8):
            line(ctx, [(0, -Lh * f + 10 * s), (sd * W * 0.72, -Lh * f - 6 * s)], 1.4 * s, shade(col, 0.25))
    ctx.restore()


def emblem(g, x, y, r):
    """Hotel emblem: purple five-petal flower with lavender sprigs (no words)."""
    for k in range(5):
        a = k * TAU / 5 - math.pi / 2
        ellipse(g, x + math.cos(a) * r * 0.5, y + math.sin(a) * r * 0.5, r * 0.42, r * 0.3, "#9b3fb5", 1.6, rot=a)
    circle(g, x, y, r * 0.22, "#f2c14e", 1.4)
    for sd in (-1, 1):
        line(g, [(x + sd * r * 1.1, y + r * 0.7), (x + sd * r * 1.25, y - r * 0.6)], 2, "#5d8a4a")
        for j in range(5):
            ellipse(g, x + sd * (r * 1.12 + j * r * 0.025), y + r * 0.45 - j * r * 0.24, r * 0.09, r * 0.12,
                    LAV[j % 3], 0.6)


# =========================================================================== 1. bedroom_night

def _night_window(g, x, y, w, h):
    for sx in (x - w * 0.34 - 12, x + w + 12):
        rrect(g, sx, y - 6, w * 0.34, h + 12, 4, "#6e4a2e", BOL)
        for k in range(1, 7):
            line(g, [(sx + 6, y + k * h / 7), (sx + w * 0.34 - 6, y + k * h / 7)], 2.5, "#4e3320")
    rrect(g, x - 12, y - 12, w + 24, h + 24, 4, "#5a3a24", BOL)
    g.save()
    g.new_path()
    g.rectangle(x, y, w, h)
    g.clip()
    g.set_source(lin_grad(0, y, 0, y + h, [(0, "#0a1230"), (1, "#24426f")]))
    g.paint()
    r = rng(77)
    for _ in range(40):
        circle(g, r.uniform(x, x + w), r.uniform(y, y + h * 0.7), r.uniform(1.0, 2.2), "#fff8d8", 0)
    mx, my = x + w * 0.74, y + h * 0.24
    glow(g, mx, my, 90, "#c8d8ff", 0.25)
    circle(g, mx, my, 28, "#fdf3c8", 0)
    circle(g, mx + 12, my - 8, 25, "#13204a", 0)
    B.hills(g, y + h - 20, "#0b1428", 30, 5, step=90)
    for px, ph in ((x + w * 0.28, h * 0.78), (x + w * 0.6, h * 0.6)):
        line(g, [(px, y + h), (px, y + h - ph)], 6, "#070d1e")
        for k in range(13):
            a = -math.pi + k * math.pi / 12
            poly(g, [(px - 3, y + h - ph), (px + math.cos(a) * ph * 0.24, y + h - ph + math.sin(a) * ph * 0.2 + 6),
                     (px + 3, y + h - ph + 3)], "#070d1e", 0)
    g.restore()
    for k in range(1, 6):
        line(g, [(x + k * w / 6, y), (x + k * w / 6, y + h)], 7, "#4e3320")
    line(g, [(x, y + h * 0.5), (x + w, y + h * 0.5)], 6, "#4e3320")
    rrect(g, x - 22, y + h + 10, w + 44, 18, 3, "#6e4a2e", BOL)


def _bedroom_wall(g):
    base = "#7d583a"
    fill_world(g, base)
    r = rng(301)
    x = X0 - 200
    while x < X1 + 200:
        g.new_path()
        g.rectangle(x, -700, 84, 1470)
        src(g, shade(base, r.uniform(-0.08, 0.05)))
        g.fill()
        line(g, [(x, -700), (x, 770)], 3, "#4b3322")
        for _ in range(r.randint(0, 2)):
            ellipse(g, x + r.uniform(20, 64), r.uniform(120, 720), 5, 10, shade(base, -0.28), 0)
        x += 84
    g.new_path()
    g.rectangle(X0 - 500, -700, X1 - X0 + 1000, 760)
    src(g, "#4a3020")
    g.fill()
    for k in range(-10, 40):
        line(g, [(k * 120, -700), (k * 120, 62)], 12, "#38241a")
    rrect(g, X0 - 300, 52, X1 - X0 + 600, 34, 2, "#6a4528", BOL)
    g.new_path()
    g.rectangle(X0 - 500, 768, X1 - X0 + 1000, 900)
    src(g, "#7b5434")
    g.fill()
    rrect(g, X0 - 300, 750, X1 - X0 + 600, 24, 0, "#5a3a24", BOL * 0.7)
    _night_window(g, 150, 210, 330, 300)
    # krama hanging on a nail next to the window
    circle(g, 660, 300, 5, "#2a1d14", 0)
    poly(g, [(620, 304), (700, 304), (712, 470), (690, 486), (672, 470), (650, 486), (630, 470)],
         check_pattern("#2f6fb2", "#f4efe6", 9), BOL)
    # framed photo (a pastel temple landscape - no people)
    rrect(g, 780, 240, 210, 156, 4, "#c9a46a", BOL)
    g.save()
    g.new_path()
    g.rectangle(796, 256, 178, 124)
    g.clip()
    g.set_source(lin_grad(0, 256, 0, 380, [(0, "#9fd0ea"), (1, "#f6d9a8")]))
    g.paint()
    angkor_wat(g, 885, 362, 0.11, "#a08f73", 1.0)
    g.new_path()
    g.rectangle(796, 360, 178, 30)
    src(g, "#7cb05a")
    g.fill()
    g.restore()
    rrect(g, 796, 256, 178, 124, 2, None, BOL * 0.8)
    # little altar shelf with a red night light (Khmer homes)
    rrect(g, 1600, 236, 210, 16, 3, "#6a4528", BOL)
    for bx in (1620, 1790):
        poly(g, [(bx - 6, 252), (bx + 6, 252), (bx, 282)], "#6a4528", BOL * 0.6)
    rrect(g, 1680, 196, 50, 40, 6, "#c9a14a", BOL * 0.8)
    for k in range(3):
        line(g, [(1694 + k * 11, 196), (1694 + k * 11, 160)], 2.4, "#b5422a")
    flower(g, 1640, 222, 12, "#f6d23a", "#f08a2a")
    flower(g, 1772, 222, 12, "#ffffff", "#f6d23a")
    line(g, [(1705, 52), (1705, 110)], 2, OUTLINE)
    glow(g, 1705, 120, 70, "#ff4a3a", 0.35)
    circle(g, 1705, 120, 10, "#ff4a3a", 1.5)


def _bedroom_floor(g):
    plank_floor(g, 772, "#8f6440", "#6a4628", seed=5, rows=9)
    # mats with pillows and blankets (back, between the cast's feet)
    poly(g, [(520, 792), (1440, 792), (1500, 866), (460, 866)], check_pattern("#c0392b", "#e9c46a", 13), BOL)
    for px, c in ((640, "#ffffff"), (900, "#f6d6e6"), (1160, "#d6ecf6")):
        pillow(g, px, 800, 120, 38, c)
    blob(g, [(980, 812), (1140, 806), (1300, 818), (1420, 846), (1260, 860), (1060, 852)], "#7a9fd8", BOL)
    blob(g, [(520, 820), (680, 812), (820, 830), (760, 858), (560, 858)], "#f2a6b8", BOL)
    # wooden sleeping platform (kre) under a mosquito net, left
    bx0, bx1 = -560, 120
    for lx in (bx0 + 30, (bx0 + bx1) / 2, bx1 - 30):
        rrect(g, lx - 12, 700, 24, 100, 3, "#5e3a22", BOL)
    rrect(g, bx0, 690, bx1 - bx0, 72, 4, "#8a5a34", BOL)
    for k in range(1, 7):
        line(g, [(bx0 + k * 100, 694), (bx0 + k * 100, 758)], 2, "#6a4628")
    rrect(g, bx0 + 10, 668, bx1 - bx0 - 20, 26, 6, check_pattern("#c58a3a", "#e9cf8a", 10), BOL)
    pillow(g, -420, 650, 150, 50, "#ffffff")
    pillow(g, -250, 652, 150, 50, "#f6e6c8")
    blob(g, [(-160, 660), (-40, 640), (60, 648), (110, 672), (20, 690), (-140, 690)],
         check_pattern("#5a7fc0", "#eef2fa", 11), BOL)
    g.save()
    g.new_path()
    g.move_to(bx0 + 20, 380)
    g.line_to(bx1 - 20, 380)
    g.curve_to(bx1 - 10, 520, bx1 + 6, 600, bx1 + 4, 690)
    g.line_to(bx0, 690)
    g.close_path()
    g.set_source_rgba(0.92, 0.94, 1.0, 0.22)
    g.fill_preserve()
    g.set_source_rgba(0.95, 0.97, 1.0, 0.6)
    g.set_line_width(2.5)
    g.stroke()
    for k in range(1, 11):
        xx = bx0 + 20 + k * (bx1 - bx0 - 40) / 11
        line(g, [(xx, 382), (xx + 4 + k * 0.6, 688)], 1.6, (0.95, 0.97, 1.0), 0.3)
    for xx in (bx0 + 20, bx1 - 20):
        line(g, [(xx, 380), (xx, 60)], 1.8, (0.9, 0.9, 0.85), 0.6)
    g.restore()
    # wardrobe, right
    rrect(g, 1560, 360, 360, 440, 6, "#6a4126", BOL)
    rrect(g, 1550, 344, 380, 26, 4, "#5a3620", BOL)
    rrect(g, 1578, 384, 152, 396, 4, "#7a4c2e", BOL * 0.8)
    rrect(g, 1750, 384, 152, 396, 4, "#7a4c2e", BOL * 0.8)
    circle(g, 1716, 590, 6, "#e0b04a", 1.2)
    circle(g, 1764, 590, 6, "#e0b04a", 1.2)
    rrect(g, 1592, 404, 124, 210, 6, "#9cc3d8", BOL * 0.8)
    line(g, [(1610, 430), (1660, 520)], 6, "#ffffff", 0.35)
    # packed bags ready for the trip
    backpack(g, 1500, 912, 1.05, "#d8433a")
    duffel(g, 1690, 936, 1.0, "#2f6fb2")
    backpack(g, 1660, 868, 0.7, "#f2b23a", "#c47a2a")
    suitcase(g, 1870, 906, 1.0, "#3fa58a")
    # woven basket of fruit for the road
    curve(g, (1384, 880), (1416, 820), (1448, 880), 5 + 2 * BOL * 0.7, OUTLINE)
    curve(g, (1384, 880), (1416, 820), (1448, 880), 5, "#b98a4a")
    for k, (fx, fy, c) in enumerate(((1396, 878, "#f2a531"), (1416, 872, "#7cc04a"), (1436, 878, "#f2a531"),
                                     (1406, 868, "#f2a531"))):
        circle(g, fx, fy, 11, c, 1.4)
    curve(g, (1420, 866), (1440, 852), (1452, 870), 7, "#f2d23a")
    poly(g, [(1376, 880), (1456, 880), (1446, 934), (1386, 934)], "#c9a46a", BOL)
    for k in range(1, 4):
        line(g, [(1378 + k * 1.5, 880 + k * 13), (1454 - k * 1.5, 880 + k * 13)], 1.6, "#9a7a40")
    for k in range(1, 6):
        line(g, [(1376 + k * 13.3, 882), (1386 + k * 10, 932)], 1.4, "#9a7a40")
    for k in range(2):
        ellipse(g, 420 + k * 34, 930, 14, 30, "#2f8a5a", BOL * 0.7)
        curve(g, (410 + k * 34, 930), (420 + k * 34, 912), (430 + k * 34, 930), 3, "#f2f2f2")


@extra
def _bedroom_night(ctx, layer, t, tod):
    dark = float(P("dark", 1.0))
    if layer == "SKY":
        fill_world(ctx, "#3a2a20")
    elif layer == "MG":
        cached(ctx, ("bedroom", "wall"), _bedroom_wall)
        h, m = parse_clock(P("clock", "3:00"))
        wall_clock(ctx, 1290, 300, 68, h, m, sec=int(t) % 60)
        for k, (sx, sy) in enumerate(((205, 250), (315, 330), (370, 236), (260, 380))):
            a = 0.35 + 0.35 * math.sin(t * 0.9 + k * 2.1)
            line(ctx, [(sx - 6, sy), (sx + 6, sy)], 1.6, "#ffffff", a)
            line(ctx, [(sx, sy - 6), (sx, sy + 6)], 1.6, "#ffffff", a)
    elif layer == "GROUND":
        cached(ctx, ("bedroom", "floor"), _bedroom_floor)
        line(ctx, [(960, -600), (960, 136)], 3, OUTLINE)
        poly(ctx, [(930, 136), (990, 136), (1012, 162), (908, 162)], "#3f7a5a", BOL)
        circle(ctx, 960, 172, 16, "#fff6c8", BOL * 0.7)
    elif layer == "OVER":
        darkness(ctx, [(960, 360, 1150, 1.0), (315, 360, 300, 0.45), (1705, 140, 160, 0.4)], 0.62 * dark)
        glow(ctx, 960, 175, 300, "#ffcf7a", 0.28 * dark, add=True)
        glow(ctx, 960, 420, 900, "#ff9a40", 0.07 * dark, add=True)
        glow(ctx, 960, 172, 46, "#fff3b0", 0.8)
        circle(ctx, 960, 172, 15, "#fffbe6", 0)


# =========================================================================== 2. restaurant

def _rest_bg(g, bd, hz, warm):
    if bd == "rice_field":
        B.mountains(g, hz + 16, "#9b9cc8" if warm else "#a4bccb", 12, 150)
        B.hills(g, hz + 26, "#7f9e78" if warm else "#88b97a", 30, 13)
        for k, x in enumerate(range(-520, 2500, 120)):
            B.sugar_palm(g, x + (k * 41) % 70, hz + 40, 110 + (k * 29) % 70, 0.0, "#3f6a4a" if warm else "#4f9a52", 1.6)
    elif bd == "angkor":
        B.hills(g, hz + 30, "#8fb88a", 40, 221)
        angkor_wat(g, 960, hz + 40, 0.5, "#a89a7c", BOL * 0.7)
        r = rng(41)
        pts = []
        x = X0 - 60
        while x < X1 + 60:
            near = abs(x - 960) < 380
            pts.append((x, (hz - 2 if near else hz - 30) + r.uniform(-10, 10), r.uniform(42, 66)))
            x += r.uniform(40, 64)
        band = [(X0 - 100, hz + 10), (X1 + 100, hz + 10), (X1 + 100, 900), (X0 - 100, 900)]
        crown_mass(g, pts, "#4f8f45", BOL * 0.8, polys=[band])
        for x_, y_, r_ in pts[::2]:
            ellipse(g, x_ - r_ * 0.2, y_ - r_ * 0.3, r_ * 0.45, r_ * 0.25, "#64a457", 0)
        for x_, y_, r_ in pts[1::3]:
            ellipse(g, x_ + r_ * 0.2, y_ + r_ * 0.5, r_ * 0.5, r_ * 0.22, "#447f3c", 0)
    else:
        for k, x in enumerate(range(-520, 2500, 170)):
            h = 240 + (k * 67) % 180
            rrect(g, x, hz + 40 - h, 160, h + 60, 2, ["#c9d6e3", "#e3d0b5", "#d4c3d9", "#cfe0c4"][k % 4], BOL * 0.8)
            for j in range(2):
                for i in range(int(h / 70)):
                    rrect(g, x + 24 + j * 70, hz + 40 - h + 24 + i * 70, 42, 40, 2, "#8fb3cc", 1.6)


def _rest_mg_static(g, bd, hz):
    if bd == "angkor":
        B.ground(g, hz + 60, "#a9c47a", "#c9a46e")
        g.new_path()
        g.rectangle(X0 - 500, 730, X1 - X0 + 1000, 80)
        src(g, "#c98f5a")
        g.fill()
        B.market_stall(g, 440, 762, 0.55, "#2f7fc0", seed=440)
        B.market_stall(g, 1380, 762, 0.55, "#d8333a", seed=1380)
        tuktuk(g, 1560, 776, 0.45, "#3a9a5a", "#235a3a", facing=-1)
        tall_tree(g, 40, 790, 560, 1.15, "#4a8c42", seed=3)
        tall_tree(g, 1880, 790, 600, 1.2, "#4f9447", seed=4)
        tall_tree(g, -420, 790, 520, 1.0, seed=5)
        tall_tree(g, 2330, 790, 520, 1.0, seed=6)
    else:  # town
        B.ground(g, hz + 60, "#b9b4aa", "#9f9a90")
        g.new_path()
        g.rectangle(X0 - 500, 690, X1 - X0 + 1000, 120)
        src(g, "#77737a")
        g.fill()
        for k in range(-6, 30):
            line(g, [(k * 180, 750), (k * 180 + 90, 750)], 5, "#f2f2f2")
        cols = ["#f0c58a", "#e8a798", "#b7d3a8", "#f3e08e", "#a8c8e8"]
        for k, x in enumerate(range(-520, 2500, 300)):
            rrect(g, x, 380, 290, 300, 3, cols[k % 5], BOL)
            rrect(g, x + 20, 560, 250, 120, 3, "#5a4a3a", BOL)
            for j in range(2):
                rrect(g, x + 36 + j * 124, 412, 92, 100, 3, "#8fb8d8", BOL * 0.8)
            poly(g, [(x - 8, 560), (x + 298, 560), (x + 314, 528), (x - 24, 528)], ["#d8333a", "#2f7fc0", "#3a9a5a"][k % 3],
                 BOL)
        scooter(g, 520, 700, 0.55, "#e84a5f", 1)
        scooter(g, 610, 702, 0.55, "#2f6fb2", 1)
        scooter(g, 1450, 700, 0.55, "#f2b23a", -1)


def _rest_ground(g, warm, lit):
    persp_floor(g, 790, 1080, "#ddd2bd", "#c7b89c", "#b3a386", vy=560, step=170)
    rrect(g, X0 - 300, 782, X1 - X0 + 600, 14, 0, "#a99a80", BOL * 0.8)
    # zinc roof underside
    eave, top, vx, vy = 168, -650, 960, 620
    g.new_path()
    g.rectangle(X0 - 500, top, X1 - X0 + 1000, eave - top)
    under = ("#8d8f9a", "#b9bcc4") if warm else ("#9aa6ae", "#c9d2d8")
    g.set_source(lin_grad(0, -100, 0, eave, [(0, under[0]), (1, under[1])]))
    g.fill()
    kk = (vy - top) / (vy - eave)
    for xb in range(X0 - 300, X1 + 300, 28):
        line(g, [(xb, eave), (vx + (xb - vx) * kk, top)], 2.4, shade(under[0], -0.18))
        line(g, [(xb + 9, eave), (vx + (xb + 9 - vx) * kk, top)], 3, "#ffffff", 0.35)
    for j in (1, 2, 3, 4):
        yy = eave - (eave - top) * (j / 5.0) ** 1.5
        rrect(g, X0 - 300, yy - 6 - j * 3, X1 - X0 + 600, 12 + j * 6, 0, "#7d6a58", BOL * 0.7)
    rrect(g, X0 - 300, eave - 14, X1 - X0 + 600, 28, 2, "#6d8aa0", BOL)
    line(g, [(X0 - 300, eave + 10), (X1 + 300, eave + 10)], 4, "#4f6a80")
    # posts
    for px in (-430, 150, 1770, 2350):
        rrect(g, px - 13, eave, 26, 790 - eave, 3, "#8fb0c4", BOL)
        line(g, [(px - 4, eave + 10), (px - 4, 780)], 4, "#c9dce8")
        rrect(g, px - 20, 776, 40, 14, 2, "#6d8aa0", BOL * 0.7)
    # potted bougainvillea along the edge
    for px, sd in ((320, 11), (1600, 12)):
        bougain(g, px, 690, 1.1, sd, n=22, sx=70, sy=50)
        poly(g, [(px - 40, 730), (px + 40, 730), (px + 30, 796), (px - 30, 796)], "#c7744a", BOL)
        rrect(g, px - 46, 722, 92, 16, 4, "#d6865a", BOL)
    # stacked plastic chairs, left
    for k in range(4):
        plastic_chair(g, 40 + k * 4, 860 - k * 16, 0.9, "#2f7fc0")
    # drinks cooler + water dispenser, right
    rrect(g, 1610, 770, 150, 100, 10, "#2f7fc0", BOL)
    rrect(g, 1600, 752, 170, 30, 8, "#ffffff", BOL)
    rrect(g, 1660, 800, 50, 12, 4, "#1f5f9a", BOL * 0.6)
    rrect(g, 1810, 690, 70, 170, 6, "#f4f4f0", BOL)
    rrect(g, 1818, 600, 54, 96, 18, "#8fd0f2", BOL)
    rrect(g, 1828, 740, 16, 12, 2, "#d8333a", 1.2)
    rrect(g, 1848, 740, 16, 12, 2, "#2f7fc0", 1.2)
    # hanging bulbs
    for bx in (560, 960, 1360):
        line(g, [(bx, top), (bx, 238)], 2.5, OUTLINE)
        rrect(g, bx - 7, 230, 14, 14, 2, "#3a3a40", 0)
        if lit:
            glow(g, bx, 256, 110, "#ffd27a", 0.45)
        circle(g, bx, 256, 14, "#fff3b0" if lit else "#f4f1e6", BOL * 0.7)


def _rest_fg(g):
    for x, sd in ((40, 1), (1880, -1)):
        line(g, [(x, -400), (x, 40)], 2.5, OUTLINE)
        for k in range(6):
            pothos(g, x + sd * (k * 14 - 30), 70, 120 + (k * 47) % 110, 1.2, seed=k + (0 if sd > 0 else 9))
        poly(g, [(x - 54, 40), (x + 54, 40), (x + 40, 92), (x - 40, 92)], "#d6865a", BOL)
        for k in range(7):
            a = -math.pi / 2 + (k - 3) * 0.4
            ellipse(g, x + math.cos(a) * 40, 30 + math.sin(a) * 26, 22, 12, "#4caf50" if k % 2 else "#3f9a3a", 1.2, rot=a)


@extra
def _restaurant(ctx, layer, t, tod):
    bd = P("backdrop", "rice_field")
    if bd not in ("rice_field", "angkor", "town"):
        bd = "rice_field"
    hz = {"rice_field": 600, "angkor": 600, "town": 620}[bd]
    warm = tod in ("sunrise", "sunset", "evening", "night")
    lit = bool(P("lights", tod in ("sunrise", "sunset", "evening", "night")))
    if layer == "SKY":
        B.sky(ctx, t, tod, hz)
        if tod in ("sunrise", "morning", "sunset"):
            birds(ctx, t, n=5, seed=8, y0=200, y1=380, col="#3a2a3a")
    elif layer == "BG":
        cached(ctx, ("rest", "BG", bd, warm), lambda g: _rest_bg(g, bd, hz, warm))
        if bd == "rice_field" and tod in ("sunrise", "morning"):
            mist(ctx, t, hz + 30, 0.22)
    elif layer == "MG":
        if bd == "rice_field":
            B.paddies(ctx, hz + 32, 800, t, "#9cc65e" if warm else "#86c45a")
            for x, h in ((1330, 470), (1480, 400), (-260, 450), (300, 360), (2260, 440)):
                B.sugar_palm(ctx, x, 800, h, t, "#3d7a45" if warm else "#3f8f3a")
        else:
            cached(ctx, ("rest", "MG", bd), lambda g: _rest_mg_static(g, bd, hz))
    elif layer == "GROUND":
        keep_matrix(ctx, "rest")
        cached(ctx, ("rest", "GROUND", warm, lit), lambda g: _rest_ground(g, warm, lit))
        tabs, w, chairs = table_conf()
        draw_chairs(ctx, chairs, "plastic", ("#d8433a", "#2f7fc0"))
    elif layer == "OVER":
        tabs, w, chairs = table_conf()
        draw_tables(ctx, tabs, w, "cloth", P("menu", "restaurant"), t, bool(P("items", True)))
    elif layer == "FG":
        cached(ctx, ("rest", "FG"), _rest_fg)
    elif layer == "SCREEN":
        if lit and tod in ("sunset", "evening", "night"):
            ctx.save()
            if with_matrix(ctx, "rest"):
                for bx in (560, 960, 1360):
                    glow(ctx, bx, 256, 90, "#ffb347", 0.35, add=True)
            ctx.restore()


# =========================================================================== 3. porridge_stall (Phnom Bakheng)

def bakheng(g, cx, base, s=1.0, col=STONE):
    """Phnom Bakheng: stepped sandstone pyramid with small shrines on the terraces and five towers on top."""
    tiers = [(420, 30), (350, 28), (285, 27), (225, 26), (170, 25)]
    y = base
    for i, (w, h) in enumerate(tiers):
        rrect(g, cx - w / 2 * s, y - h * s, w * s, h * s, 2, shade(col, -0.06 + i * 0.03), BOL * 0.8)
        line(g, [(cx - w / 2 * s + 4, y - h * s + 5), (cx + w / 2 * s - 4, y - h * s + 5)], 2, shade(col, 0.25))
        nn = 3 if i < 3 else 2
        for k in range(-nn, nn + 1):
            if k == 0:
                continue
            tx = cx + k * (w / 2 - 14) / nn * s
            prang(g, tx, y - h * s + 1, 7 * s, 20 * s, shade(col, 0.04), BOL * 0.45, detail=False)
        y -= h * s
    rrect(g, cx - 16 * s, y, 32 * s, base - y, 2, shade(col, -0.18), BOL * 0.6)
    for k in range(1, 12):
        yy = y + (base - y) * k / 12
        line(g, [(cx - 14 * s, yy), (cx + 14 * s, yy)], 1.4, shade(col, -0.35))
    for dx, h_, w_ in ((-58, 60, 17), (58, 60, 17)):
        prang(g, cx + dx * s, y + 1, w_ * s, h_ * s, shade(col, -0.02), BOL * 0.6)
    rrect(g, cx - 28 * s, y - 16 * s, 56 * s, 17 * s, 2, col, BOL * 0.6)
    prang(g, cx, y - 15 * s, 25 * s, 82 * s, shade(col, 0.07), BOL * 0.7)
    for dx in (-86, 86):
        prang(g, cx + dx * s, y + 1, 13 * s, 40 * s, shade(col, 0.04), BOL * 0.5)


def _porridge_bg(g):
    B.mountains(g, 660, "#a9bfd0", 31, 120)
    B.hills(g, 670, "#9cc08f", 26, 32)
    peak_x, peak_y, base = 1060, 365, 700

    def hy(x):  # forested hill with a broad summit plateau for the temple
        d = abs(x - peak_x)
        if d < 240:
            return peak_y
        u = min(1.0, (d - 240) / 760.0)
        return peak_y + (base - peak_y) * (0.5 - 0.5 * math.cos(math.pi * u))

    bakheng(g, peak_x, peak_y + 38, 0.95)
    green = "#3f7d45"
    r = rng(51)
    pts = []
    x = 140
    while x < 1990:
        pts.append((x, hy(x) + 24 + r.uniform(-4, 4), r.uniform(26, 38)))
        x += r.uniform(24, 36)
    body = [(140, 800)] + [(x_, hy(x_) + 36) for x_ in range(140, 2000, 20)] + [(1990, 800)]
    crown_mass(g, pts, green, BOL * 0.8, polys=[body])
    # canopy texture: soft lighter crown tops scattered over the slope
    for j in range(6):
        x = 170 + (j % 2) * 40
        while x < 1960:
            y = hy(x) + 60 + j * 46 + r.uniform(-10, 10)
            if y < 690 and r.random() < 0.7:
                rr = r.uniform(18, 34)
                ellipse(g, x, y, rr, rr * 0.5, shade(green, 0.07 + 0.04 * (j % 2)), 0)
                ellipse(g, x - rr * 0.3, y - rr * 0.15, rr * 0.4, rr * 0.16, shade(green, 0.2), 0)
            x += r.uniform(60, 100)
    for k, x in enumerate((-420, -300, -150, 2120, 2260, 2390)):
        B.sugar_palm(g, x, 700, 200 + (k * 37) % 70, 0.0, "#4f9a52", 1.6)


def _porridge_mg(g):
    B.ground(g, 690, "#a9c47a", "#98b86a")
    g.new_path()
    g.rectangle(X0 - 500, 712, X1 - X0 + 1000, 56)
    src(g, "#7d7a7c")
    g.fill()
    line(g, [(X0 - 500, 714), (X1 + 500, 714)], 3, "#e9e4d8")
    for k in range(-8, 40):
        line(g, [(k * 140, 742), (k * 140 + 70, 742)], 4, "#f2e6a0")
    r = rng(52)
    bush_pts = [(x + r.uniform(-10, 10), 712 + r.uniform(-6, 4), r.uniform(22, 36))
                for x in list(range(300, 900, 48)) + list(range(1280, 1780, 48))]
    crown_mass(g, bush_pts, "#5a9a4a", BOL * 0.7)
    for x, y, rr in bush_pts[::2]:
        ellipse(g, x - rr * 0.25, y - rr * 0.3, rr * 0.45, rr * 0.25, "#79b862", 0)
    tall_tree(g, -60, 740, 640, 1.15, "#447f3e", seed=21)
    tall_tree(g, 160, 730, 560, 1.0, "#4f8f45", seed=22)
    tall_tree(g, 1840, 735, 620, 1.15, "#4a8a42", seed=23)
    tall_tree(g, 2120, 740, 600, 1.1, "#447f3e", seed=24)
    tall_tree(g, -360, 740, 600, 1.1, seed=25)


def _porridge_ground(g, tuk):
    B.ground(g, 768, "#d39a62", "#bd8250")
    g.new_path()
    g.rectangle(X0 - 500, 768, X1 - X0 + 1000, 10)
    src(g, "#a8703f")
    g.fill()
    r = rng(61)
    for _ in range(90):
        ellipse(g, r.uniform(X0, X1), r.uniform(790, 1070), r.uniform(4, 9), r.uniform(2, 4), "#a8703f", 0,
                rot=r.uniform(0, 3))
    for _ in range(26):
        ellipse(g, r.uniform(X0, X1), r.uniform(800, 1070), 9, 4, ["#c98a2e", "#8a6a2a", "#d8b03a"][r.randrange(3)], 0,
                rot=r.uniform(0, 3))
    B.grass_tufts(g, 780, 1070, 30, 63, "#6a8f3a")
    # stacked stools + water barrel at the back left
    for k in range(4):
        plastic_stool(g, -120, 840 - k * 22, 0.9, ["#d8433a", "#2f7fc0", "#3a9a5a", "#f2b23a"][k])
    rrect(g, -260, 740, 90, 110, 12, "#2f7fc0", BOL)
    # big patio umbrella over the cart
    line(g, [(250, 900), (250, 250)], 10 + 2 * BOL, OUTLINE)
    line(g, [(250, 900), (250, 250)], 10, "#d8d8de")
    g.new_path()
    g.move_to(-70, 300)
    g.curve_to(-10, 190, 510, 190, 570, 300)
    g.close_path()
    fill_stroke(g, stripe_pattern("#2f7fc0", "#f4f4f0", 40, vertical=True), BOL)
    for k in range(10):
        cx_ = -70 + k * 64 + 32
        ellipse(g, cx_, 302, 32, 12, "#2f7fc0" if k % 2 else "#f4f4f0", BOL * 0.6)
    circle(g, 250, 210, 9, "#d8d8de", BOL * 0.7)
    # the cart
    for wx in (110, 400):
        circle(g, wx, 858, 42, "#2a2a30", BOL)
        circle(g, wx, 858, 30, "#c9ced6", BOL * 0.6)
        for k in range(8):
            a = k * math.pi / 4
            line(g, [(wx, 858), (wx + math.cos(a) * 28, 858 + math.sin(a) * 28)], 1.6, "#7a8088")
    rrect(g, 30, 700, 450, 150, 6, "#3c7fc2", BOL)
    rrect(g, 30, 700, 450, 20, 4, "#f4f4f0", BOL * 0.8)
    for k in range(3):
        rrect(g, 52 + k * 145, 736, 128, 96, 6, "#356fb0", BOL * 0.7)
        circle(g, 160 + k * 145, 784, 5, "#d9d9de", 1.2)
    # glass display case with fried dough sticks and eggs
    rrect(g, 50, 590, 250, 112, 6, (0.80, 0.90, 0.96), BOL)
    for k in range(5):
        ellipse(g, 100 + k * 14, 668 - (k % 2) * 6, 34, 6, "#e0a344", 1.0, rot=-0.15 + 0.08 * k)
    for k in range(4):
        circle(g, 200 + k * 20, 680, 10, "#f6f1e6", 1.2)
    rrect(g, 250, 640, 36, 52, 8, "#b8d87a", 1.4)
    line(g, [(64, 600), (64, 690)], 4, "#ffffff", 0.6)
    rrect(g, 46, 582, 258, 14, 4, "#d9d9de", BOL * 0.8)
    # charcoal stove + big pot of bobor
    poly(g, [(318, 700), (452, 700), (440, 640), (330, 640)], "#a35a35", BOL)
    rrect(g, 352, 668, 66, 18, 4, "#2a1d14", 0)
    glow(g, 385, 676, 34, "#ff7a2a", 0.7)
    rrect(g, 316, 560, 138, 84, 12, "#c9ced6", BOL)
    line(g, [(330, 572), (330, 632)], 5, "#ffffff", 0.6)
    ellipse(g, 385, 560, 72, 14, "#aab4bd", BOL)
    ellipse(g, 385, 560, 58, 9, "#f7f1e1", 0)
    for sd in (-1, 1):
        rrect(g, 385 + sd * 76 - 8, 576, 16, 10, 3, "#7a8088", BOL * 0.6)
    line(g, [(400, 562), (470, 500)], 6, "#8a8f96")
    ellipse(g, 474, 496, 10, 6, "#8a8f96", 1.2)
    for k in range(4):
        ellipse(g, 440, 690 - k * 9, 26, 8, "#ffffff", BOL * 0.6)
    if tuk:
        tuktuk(g, 1700, 886, 0.82, "#2f6fb2", facing=-1)
    bougain(g, 1960, 760, 1.2, 66, n=20, sx=60, sy=50)


def _porridge_fg(g):
    for x, sd in ((-40, 1), (1960, -1)):
        for k in range(9):
            a = -math.pi / 2 + (k - 4) * 0.22 * sd
            line(g, [(x + k * 10 * sd, 1110), (x + k * 10 * sd + math.cos(a) * 60, 1110 + math.sin(a) * 220)], 8,
                 "#4f8a3a" if k % 2 else "#3f7a32")


@extra
def _porridge_stall(ctx, layer, t, tod):
    if layer == "SKY":
        B.sky(ctx, t, tod, 660)
        birds(ctx, t, n=6, seed=12, y0=140, y1=320, col="#3a3040")
    elif layer == "BG":
        cached(ctx, ("bobor", "BG"), _porridge_bg)
        mist(ctx, t, 650, 0.26 if tod in ("morning", "sunrise") else 0.12, seed=7)
    elif layer == "MG":
        cached(ctx, ("bobor", "MG"), _porridge_mg)
    elif layer == "GROUND":
        tuk = bool(P("tuktuk", True))
        cached(ctx, ("bobor", "GROUND", tuk), lambda g: _porridge_ground(g, tuk))
        steam(ctx, 385, 552, t, 2.1, 7, 0.55, 95, seed=1)
        steam(ctx, 360, 552, t + 1.3, 1.7, 5, 0.4, 90, seed=4)
        tabs, w, chairs = table_conf()
        draw_chairs(ctx, chairs, "stool", ("#d8433a", "#2f7fc0", "#3a9a5a"), y=930)
    elif layer == "OVER":
        tabs, w, chairs = table_conf()
        draw_tables(ctx, tabs, w, "steel", P("menu", "bobor"), t, bool(P("items", True)))
    elif layer == "FG":
        cached(ctx, ("bobor", "FG"), _porridge_fg)


# =========================================================================== 4. hotel (Lavender)

H_X0, H_X1 = -260, 1320
H_BAYS_L = (-150, 60, 270)
H_BAYS_R = (850, 1050, 1230)
H_DOOR = 560
CAN_TOP, CAN_BOT = 432, 478


def _window(g, x, y, w, h, glass_col, shutter="#8a5530", lit=False):
    for sd in (-1, 1):
        sx = x - w / 2 - w * 0.42 if sd < 0 else x + w / 2
        rrect(g, sx, y, w * 0.42, h, 3, shutter, BOL * 0.8)
        for k in range(1, 7):
            line(g, [(sx + 4, y + k * h / 7), (sx + w * 0.42 - 4, y + k * h / 7)], 1.8, shade(shutter, -0.3))
    g.new_path()
    g.move_to(x - w / 2, y + h)
    g.line_to(x - w / 2, y + w / 2)
    g.arc(x, y + w / 2, w / 2, math.pi, 2 * math.pi)
    g.line_to(x + w / 2, y + h)
    g.close_path()
    fill_stroke(g, glass_col, BOL)
    if not lit:
        line(g, [(x - w * 0.3, y + h * 0.75), (x + w * 0.1, y + h * 0.3)], 5, "#ffffff", 0.45)
    line(g, [(x, y + w / 2), (x, y + h)], 3, "#f4efe2")
    line(g, [(x - w / 2, y + h * 0.55), (x + w / 2, y + h * 0.55)], 3, "#f4efe2")
    g.new_path()
    g.arc(x, y + w / 2, w / 2 + 6, math.pi, 2 * math.pi)
    src(g, "#e9d9b8")
    g.set_line_width(9)
    g.stroke()


def _hotel_building(g, mode):
    lit = mode in ("night", "evening")
    night = mode == "night"
    wall = "#f6ead2" if not night else "#efe0c4"
    r = rng(91)

    def gcol():
        if night:
            return "#ffd36b"
        if lit:
            return "#ffd36b" if r.random() < 0.55 else "#8fa8c8"
        return "#9fd0ea"

    x0, x1 = H_X0, H_X1
    # roof + pediment
    poly(g, [(x0 - 50, 92), (x0 + 110, -60), (x1 - 110, -60), (x1 + 50, 92)], "#c4643c", BOL)
    for k in range(1, 6):
        yy = 92 - k * 26
        f = k / 6.0
        line(g, [(x0 - 50 + 160 * f, yy), (x1 + 50 - 160 * f, yy)], 2, "#9a4628")
    xx = x0 - 30
    while xx < x1 + 40:
        line(g, [(xx, 90), (xx + 6, 66)], 1.6, "#9a4628")
        xx += 22
    poly(g, [(H_DOOR - 170, 96), (H_DOOR, -10), (H_DOOR + 170, 96)], "#f2e2c4", BOL)
    circle(g, H_DOOR, 52, 26, "#e9d9b8", BOL * 0.8)
    emblem(g, H_DOOR, 52, 18)
    # walls and bands
    rrect(g, x0, 92, x1 - x0, 596, 2, wall, BOL)
    rrect(g, H_DOOR - 150, 92, 300, 596, 2, shade(wall, 0.25), BOL)
    g.new_path()
    g.rectangle(x1 - 60, 96, 56, 590)
    g.set_source_rgba(0, 0, 0, 0.05)
    g.fill()
    for yy, hh in ((80, 18), (264, 12), (440, 14)):
        rrect(g, x0 - 12, yy, x1 - x0 + 24, hh, 2, "#e6d3ae", BOL * 0.8)
    rrect(g, x0 - 10, 682, x1 - x0 + 20, 22, 2, "#cdbb98", BOL)
    # windows: 3rd floor (116-234), 2nd floor (290-422), ground floor (500-666)
    for bx in H_BAYS_L + H_BAYS_R + (H_DOOR,):
        _window(g, bx, 116, 80, 118, gcol(), lit=lit)
    for bx in H_BAYS_L + H_BAYS_R:
        _window(g, bx, 290, 84, 132, gcol(), lit=lit)
    for bx in H_BAYS_L + H_BAYS_R:
        _window(g, bx, 500, 92, 166, gcol(), lit=lit)
        rrect(g, bx - 62, 650, 124, 26, 4, "#d9cbb0", BOL * 0.8)
        lavender(g, bx - 30, 654, 0.55, seed=bx + 1, w=50)
        lavender(g, bx + 30, 654, 0.55, seed=bx + 2, w=50)
    # balconies (2nd and 3rd floor): iron railings with cascading bougainvillea
    for by, bays in ((440, H_BAYS_L + H_BAYS_R), (264, H_BAYS_L + H_BAYS_R + (H_DOOR,))):
        for bx in bays:
            rrect(g, bx - 82, by - 4, 164, 14, 2, "#e6d3ae", BOL * 0.8)
            rrect(g, bx - 78, by - 44, 156, 6, 2, "#3a3440", 0)
            for k in range(14):
                line(g, [(bx - 74 + k * 11.4, by - 40), (bx - 74 + k * 11.4, by - 4)], 2.4, "#3a3440")
            bougain(g, bx - 46, by - 40, 0.8, seed=bx + by, n=10, sx=36, sy=14)
            bougain_cascade(g, bx + 50, by + 8, 70 if by == 440 else 90, 0.8, seed=bx * 3 + by, drift=8)
    # sign panel (no words) with the flower emblem
    rrect(g, H_DOOR - 92, 300, 184, 92, 10, "#7b4fa8", BOL)
    rrect(g, H_DOOR - 82, 310, 164, 72, 7, "#f6eefa", BOL * 0.7)
    emblem(g, H_DOOR, 346, 22)
    for k in range(5):
        circle(g, H_DOOR - 70 + k * 35, 326 + (k % 2) * 40, 3, "#c9a4e0", 0)
    # entrance door (arched, wooden, glazed)
    g.new_path()
    g.move_to(H_DOOR - 62, 684)
    g.line_to(H_DOOR - 62, 552)
    g.arc(H_DOOR, 552, 62, math.pi, 2 * math.pi)
    g.line_to(H_DOOR + 62, 684)
    g.close_path()
    fill_stroke(g, "#e6d3ae", BOL)
    g.new_path()
    g.move_to(H_DOOR - 52, 684)
    g.line_to(H_DOOR - 52, 556)
    g.arc(H_DOOR, 556, 52, math.pi, 2 * math.pi)
    g.line_to(H_DOOR + 52, 684)
    g.close_path()
    fill_stroke(g, "#8a5530", BOL)
    g.new_path()
    g.arc(H_DOOR, 556, 44, math.pi, 2 * math.pi)
    g.close_path()
    fill_stroke(g, "#ffd36b" if lit else "#9fd0ea", BOL * 0.7)
    for sd in (-1, 1):
        rrect(g, H_DOOR + sd * 26 - 18, 566, 36, 54, 3, "#ffd36b" if lit else "#b8dcef", BOL * 0.6)
        rrect(g, H_DOOR + sd * 26 - 18, 630, 36, 46, 3, "#7a4826", BOL * 0.6)
    line(g, [(H_DOOR, 556), (H_DOOR, 684)], 3, OUTLINE)
    for sd in (-1, 1):
        circle(g, H_DOOR + sd * 10, 626, 4, "#e9c24a", 1)
    # wall lanterns
    for sd in (-1, 1):
        lx = H_DOOR + sd * 92
        line(g, [(lx, 520), (lx, 540)], 3, OUTLINE)
        rrect(g, lx - 12, 540, 24, 34, 4, "#ffe9a0" if lit else "#f4efe2", BOL * 0.8)
        poly(g, [(lx - 16, 540), (lx + 16, 540), (lx, 526)], "#3a3440", BOL * 0.6)
        if lit:
            glow(g, lx, 556, 70, "#ffd36b", 0.5)
    # climbing bougainvillea at the building corners
    for cx_ in (x0 + 20, x1 - 20):
        for k in range(12):
            bougain(g, cx_ + math.sin(k * 0.9) * 22, 660 - k * 48, 1.0, seed=k * 13 + int(cx_), n=14, sx=46, sy=30)
    # flowering mass between the sign and the canopy
    for k in range(7):
        bougain(g, H_DOOR - 150 + k * 50, 404 + (k % 2) * 10, 0.95, seed=400 + k, n=12, sx=32, sy=18)
    if lit:
        for bx in H_BAYS_L + H_BAYS_R:
            glow(g, bx, 580, 120, "#ffcf6a", 0.25)


def _hotel_front(g):
    # forecourt (stone pavers) + driveway on the right
    persp_floor(g, 702, 1080, "#e6d8bf", "#d4c2a2", "#c2ae8c", vy=420, step=130, rows=8)
    g.new_path()
    g.move_to(1330, 702)
    g.line_to(X1 + 500, 702)
    g.line_to(X1 + 500, 1300)
    g.line_to(1180, 1300)
    g.close_path()
    src(g, "#cdc8c0")
    g.fill()
    for k in range(1, 8):
        yy = 702 + (1080 - 702) * (k / 8.0) ** 1.7
        line(g, [(1330 - (yy - 702) * 0.25, yy), (X1 + 500, yy)], 2, "#b2ada4")
    line(g, [(1330, 702), (1180, 1300)], 6, "#a8a296")


def _hotel_front_over(g, mode):
    """Steps, canopy, palms and planters: in front of the facade (still GROUND, behind the cast)."""
    lit = mode in ("night", "evening")
    for k, (w, y) in enumerate(((190, 700), (226, 714), (262, 728))):
        rrect(g, H_DOOR - w / 2, y, w, 16, 2, shade("#e0d4bc", -0.04 * k), BOL)
    for sd in (-1, 1):
        rrect(g, H_DOOR + sd * 118 - 5, CAN_BOT, 10, 736 - CAN_BOT, 3, "#5a3a5a", BOL * 0.8)
    g.new_path()
    g.move_to(H_DOOR - 136, CAN_BOT)
    g.curve_to(H_DOOR - 120, CAN_TOP - 30, H_DOOR + 120, CAN_TOP - 30, H_DOOR + 136, CAN_BOT)
    g.close_path()
    fill_stroke(g, stripe_pattern("#9b6ac8", "#c9a8e8", 22, vertical=True), BOL)
    for k in range(8):
        cx_ = H_DOOR - 136 + k * 34 + 17
        ellipse(g, cx_, CAN_BOT + 2, 17, 9, "#7b4fa8", BOL * 0.6)
    if lit:
        glow(g, H_DOOR, CAN_BOT + 20, 150, "#ffd36b", 0.35)
    potted_palm(g, H_DOOR - 196, 750, 0.9)
    potted_palm(g, H_DOOR + 196, 750, 0.9)
    for px in (-200, 30, 250, 860, 1080, 1270):
        rrect(g, px - 70, 700, 140, 36, 4, "#f2efe6", BOL)
        lavender(g, px - 32, 706, 0.75, seed=px, w=46)
        lavender(g, px + 32, 706, 0.75, seed=px + 5, w=46)
    lx = 2180  # lamp post at the driveway mouth (outside the van's clear zone)
    rrect(g, lx - 7, 520, 14, 230, 4, "#3a3440", BOL)
    rrect(g, lx - 18, 490, 36, 40, 6, "#ffe9a0" if lit else "#f4efe2", BOL)
    poly(g, [(lx - 24, 490), (lx + 24, 490), (lx, 470)], "#3a3440", BOL * 0.7)
    if lit:
        glow(g, lx, 510, 110, "#ffd36b", 0.45)


def _hotel_mg(g):
    g.new_path()
    g.rectangle(X0 - 500, 650, X1 - X0 + 1000, 200)
    src(g, "#8fbf6a")
    g.fill()
    crown_mass(g, [(x, 660, 40) for x in range(X0 - 60, X1 + 80, 70)], "#5a9a4a", BOL * 0.7)
    # garden wall on the driveway side with bougainvillea pouring over it
    rrect(g, 1340, 560, 1300, 144, 2, "#f2e6cc", BOL)
    rrect(g, 1330, 548, 1320, 18, 2, "#c4643c", BOL)
    for k in range(18):
        bougain(g, 1380 + k * 66, 552 + (k % 3) * 6, 1.1, seed=700 + k, n=14, sx=44, sy=24)
    for k in range(0, 18, 2):
        bougain_cascade(g, 1400 + k * 66, 572, 60 + (k * 13) % 50, 0.9, seed=900 + k)
    rrect(g, 2060, 470, 60, 234, 3, "#efe0c4", BOL)
    rrect(g, 2052, 460, 76, 18, 3, "#c4643c", BOL)


def _hotel_bg(g):
    for k, x in enumerate(range(-520, 2500, 150)):
        B.tree(g, x, 690, 0.9 + (k % 3) * 0.12, "#5a9a4c" if k % 2 else "#4f8f45", "#6a4a30", seed=k)
    for x, s_ in ((1560, 1.0), (1960, 0.95), (-380, 1.1)):
        B.tree(g, x, 700, s_, "#8a6cc4", "#6a4a30", seed=int(x))
        r = rng(int(x))
        for _ in range(40):
            circle(g, x + r.uniform(-115, 115) * s_, 700 - r.uniform(110, 290) * s_, r.uniform(5, 9),
                   r.choice(("#b89ae6", "#6f50a8", "#c9b0f0")), 0)
    for x in (1440, 1720, 2300):
        B.coconut(g, x, 700, 470, 0.0, lean=0.06)


def _hotel_fg(g):
    for k, x in enumerate((-60, 40, 140)):
        lavender(g, x, 1100, 1.8, seed=k + 31, w=60)


@extra
def _hotel(ctx, layer, t, tod):
    mode = "night" if (tod == "night" or P("night", False)) else ("evening" if tod in ("evening", "sunset") else "day")
    if layer == "SKY":
        B.sky(ctx, t, tod, 660)
    elif layer == "BG":
        cached(ctx, ("hotel", "BG"), _hotel_bg)
    elif layer == "MG":
        cached(ctx, ("hotel", "MG"), _hotel_mg)
    elif layer == "GROUND":
        keep_matrix(ctx, "hotel")

        def draw(g):
            _hotel_front(g)
            _hotel_building(g, mode)
            _hotel_front_over(g, mode)

        cached(ctx, ("hotel", "GROUND", mode), draw)
    elif layer == "FG":
        cached(ctx, ("hotel", "FG"), _hotel_fg)
    elif layer == "SCREEN":
        if mode == "day" or tod not in ("night", "evening", "sunset"):
            return
        ctx.save()
        if with_matrix(ctx, "hotel"):
            if mode == "night":
                # warm porch light pooling around the entrance (lifts the blue night tint locally)
                ctx.set_operator(cairo.OPERATOR_COLOR_DODGE)
                c = (0.45, 0.36, 0.0)
                ctx.new_path()
                ctx.arc(H_DOOR, 640, 520, 0, TAU)
                ctx.set_source(rad_grad(H_DOOR, 640, 0, 520, [(0, c + (0.55,)), (0.5, c + (0.3,)), (1, c + (0.0,))]))
                ctx.fill()
                ctx.set_operator(cairo.OPERATOR_ADD)
                for bx in H_BAYS_L + H_BAYS_R + (H_DOOR,):
                    for y0, h in ((126, 104), (300, 118)):
                        if bx == H_DOOR and y0 == 300:
                            continue
                        ctx.new_path()
                        ctx.rectangle(bx - 34, y0 + 12, 68, h - 16)
                        ctx.set_source_rgba(0.34, 0.22, 0.04, 1)
                        ctx.fill()
                        glow(ctx, bx, y0 + h / 2, 90, "#ff9a30", 0.16, add=True)
            for sd in (-1, 1):
                glow(ctx, H_DOOR + sd * 92, 556, 60, "#ffb347", 0.45, add=True)
            glow(ctx, 2180, 510, 80, "#ffb347", 0.5, add=True)
            glow(ctx, H_DOOR, CAN_BOT + 10, 120, "#ffb347", 0.18, add=True)
        ctx.restore()


# =========================================================================== 5. hotel_lobby

def _lobby_wall(g, night):
    wall = "#f3e4c8" if not night else "#c9b494"
    fill_world(g, wall)
    g.new_path()
    g.rectangle(X0 - 500, 60, X1 - X0 + 1000, 710)
    g.set_source(lin_grad(0, 60, 0, 600, [(0, shade(wall, -0.06)), (1, wall)]))
    g.fill()
    g.new_path()
    g.rectangle(X0 - 500, -700, X1 - X0 + 1000, 750)
    src(g, "#ede0c6" if not night else "#a8957a")
    g.fill()
    for k in range(-6, 30):
        rrect(g, k * 200 - 14, -700, 28, 744, 0, "#8a5a34", BOL * 0.7)
    rrect(g, X0 - 300, 40, X1 - X0 + 600, 26, 2, "#e0cfaa", BOL)
    rrect(g, X0 - 300, 62, X1 - X0 + 600, 10, 0, "#c9b48c", BOL * 0.6)
    # wood wainscot
    rrect(g, X0 - 300, 590, X1 - X0 + 600, 180, 0, "#7a4a2c", BOL)
    rrect(g, X0 - 300, 580, X1 - X0 + 600, 16, 2, "#9a6236", BOL)
    for k in range(-4, 24):
        rrect(g, k * 120 + 14, 612, 92, 136, 4, "#86532f", BOL * 0.6)
    g.new_path()
    g.rectangle(X0 - 500, 770, X1 - X0 + 1000, 900)
    src(g, "#d9c49c")
    g.fill()
    # big arched garden window/door, left
    wx, ww, wy = 90, 380, 150
    g.new_path()
    g.move_to(wx, 770)
    g.line_to(wx, wy + ww / 2)
    g.arc(wx + ww / 2, wy + ww / 2, ww / 2, math.pi, 2 * math.pi)
    g.line_to(wx + ww, 770)
    g.close_path()
    fill_stroke(g, "#8a5a34", BOL)
    g.save()
    g.new_path()
    g.move_to(wx + 16, 770)
    g.line_to(wx + 16, wy + ww / 2)
    g.arc(wx + ww / 2, wy + ww / 2, ww / 2 - 16, math.pi, 2 * math.pi)
    g.line_to(wx + ww - 16, 770)
    g.close_path()
    g.clip()
    if night:
        g.set_source(lin_grad(0, wy, 0, 770, [(0, "#0e1838"), (1, "#2a3f6a")]))
        g.paint()
        r = rng(5)
        for _ in range(16):
            circle(g, r.uniform(wx, wx + ww), r.uniform(wy, 500), 1.6, "#fff8d8", 0)
        crown_mass(g, [(wx + 60 + k * 70, 640 + (k % 2) * 20, 70) for k in range(5)], "#1c2e3a", 0)
        for k in range(5):
            circle(g, wx + 60 + k * 70, 620, 4, "#ffd36b", 0)
    else:
        g.set_source(lin_grad(0, wy, 0, 770, [(0, "#8fd0f2"), (1, "#e2f4fb")]))
        g.paint()
        B.coconut(g, wx + 270, 720, 420, 0.0, lean=-0.1)
        crown_mass(g, [(wx + 30 + k * 60, 660 + (k % 2) * 18, 60) for k in range(7)], "#5aa84a", BOL * 0.7)
        for k in range(8):
            bougain(g, wx + 40 + k * 44, 620 + (k % 3) * 12, 1.0, seed=k + 50, n=10, sx=30, sy=20)
    g.restore()
    for k in range(1, 4):
        line(g, [(wx + k * ww / 4, wy + 20), (wx + k * ww / 4, 770)], 6, "#8a5a34")
    line(g, [(wx, 470), (wx + ww, 470)], 6, "#8a5a34")
    # lavender drapes
    for sd, dx in ((-1, wx - 50), (1, wx + ww - 10)):
        g.new_path()
        g.move_to(dx, 100)
        g.line_to(dx + 60, 100)
        g.curve_to(dx + 70 + sd * 10, 400, dx + 50, 600, dx + 60, 770)
        g.line_to(dx, 770)
        g.close_path()
        fill_stroke(g, "#a98bd0", BOL)
        for k in range(1, 4):
            line(g, [(dx + k * 15, 110), (dx + k * 15 + 4, 760)], 2.4, "#8a6cb8")
    rrect(g, wx - 70, 90, ww + 140, 14, 6, "#8a5a34", BOL)
    # framed painting of Angkor Wat at sunset
    rrect(g, 690, 200, 380, 250, 4, "#c9a14a", BOL)
    g.save()
    g.new_path()
    g.rectangle(712, 222, 336, 206)
    g.clip()
    g.set_source(lin_grad(0, 222, 0, 428, [(0, "#6a5aa8"), (0.6, "#f6a35f"), (1, "#f7d08a")]))
    g.paint()
    circle(g, 880, 360, 30, "#ffd27a", 0)
    angkor_wat(g, 880, 412, 0.24, "#5d4c62", 1.4)
    g.new_path()
    g.rectangle(712, 410, 336, 30)
    src(g, "#4f6a8a")
    g.fill()
    g.restore()
    rrect(g, 712, 222, 336, 206, 2, None, BOL * 0.8)
    # sconces
    for sx in (620, 1140):
        glow(g, sx, 320, 120, "#ffd27a", 0.55 if night else 0.35)
        rrect(g, sx - 8, 330, 16, 40, 3, "#c9a14a", BOL * 0.7)
        poly(g, [(sx - 26, 300), (sx + 26, 300), (sx + 18, 340), (sx - 18, 340)], "#fff0c8", BOL * 0.8)
    # key board behind the desk
    rrect(g, 1380, 270, 340, 260, 8, "#8a5530", BOL)
    rrect(g, 1396, 286, 308, 228, 4, "#a8703f", BOL * 0.7)
    tags = ["#9b3fb5", "#c56bd8", "#7b5bb8", "#9b3fb5", "#d48ce2"]
    r = rng(17)
    for row in range(3):
        for col in range(6):
            hx, hy = 1424 + col * 50, 312 + row * 72
            circle(g, hx, hy, 4, "#d9b53a", 1)
            if r.random() < 0.8:
                line(g, [(hx, hy), (hx, hy + 22)], 2.4, "#c9a14a")
                circle(g, hx, hy + 12, 5, "#c9a14a", 1)
                rrect(g, hx - 7, hy + 22, 14, 26, 5, tags[(row + col) % 5], BOL * 0.5)
    circle(g, 1550, 222, 34, "#f6eefa", BOL)
    emblem(g, 1550, 222, 20)
    # pendant lamps
    for px in (960, 1550):
        line(g, [(px, -700), (px, 120)], 2.5, OUTLINE)
        glow(g, px, 160, 150, "#ffd27a", 0.45 if night else 0.3)
        ellipse(g, px, 140, 46, 30, "#d6a861", BOL)
        for k in range(1, 4):
            curve(g, (px - 44 + k * 22, 116), (px - 44 + k * 22, 140), (px - 44 + k * 22, 166), 1.6, "#a8783a")


def _lobby_floor(g, night):
    persp_floor(g, 770, 1080, "#efe4cf" if not night else "#cdbd9e", "#e2d2b4" if not night else "#b9a684",
                "#cbb895" if not night else "#9e8c6c", vy=480, step=150, rows=7, lw=2.5)
    # rug
    g.new_path()
    g.move_to(380, 850)
    g.line_to(1260, 850)
    g.line_to(1360, 1010)
    g.line_to(280, 1010)
    g.close_path()
    fill_stroke(g, "#7b3f6a", BOL)
    g.new_path()
    g.move_to(410, 866)
    g.line_to(1230, 866)
    g.line_to(1318, 994)
    g.line_to(322, 994)
    g.close_path()
    fill_stroke(g, "#a65a8a", BOL * 0.6)
    for k in range(9):
        flower(g, 460 + k * 92, 930, 12, "#f2c14e", "#7b3f6a", 0)
    # console table with a big vase of purple flowers under the painting
    rrect(g, 740, 690, 280, 18, 3, "#7a4a2c", BOL)
    for lx in (756, 1004):
        rrect(g, lx - 7, 706, 14, 84, 2, "#6a3f24", BOL * 0.8)
    for k in range(9):
        a = -math.pi / 2 + (k - 4) * 0.28
        line(g, [(880, 630), (880 + math.cos(a) * 90, 630 + math.sin(a) * 110)], 2.4, "#4f8a3a")
        for j in range(4):
            ellipse(g, 880 + math.cos(a) * (60 + j * 9), 630 + math.sin(a) * (74 + j * 11), 5, 7, LAV[(k + j) % 3], 0.6)
    blob(g, [(856, 690), (904, 690), (912, 650), (880, 616), (848, 650)], "#e9e2f2", BOL)
    for k in range(3):
        rrect(g, 950 + k * 22, 664 - k * 6, 18, 26 + k * 6, 2, ["#9fd0ea", "#f2c14e", "#e86ab0"][k], 1.2)
    # potted palm in the corner
    potted_palm(g, 1930, 800, 1.3)
    # luggage near the door
    suitcase(g, 250, 960, 1.15, "#2fa59a")
    suitcase(g, 380, 950, 0.95, "#f2913a", handle=False)
    duffel(g, 120, 970, 0.9, "#8a5aa8", "#f2c14e")
    # front desk
    rrect(g, 1290, 700, 520, 170, 4, "#7a4626", BOL)
    for k in range(3):
        rrect(g, 1312 + k * 166, 734, 144, 112, 4, "#8a5530", BOL * 0.8)
        emblem(g, 1384 + k * 166, 790, 13)
    rrect(g, 1290, 712, 520, 12, 0, "#a68bd0", BOL * 0.6)
    rrect(g, 1280, 860, 540, 16, 3, "#5a3420", BOL)
    rrect(g, 1270, 684, 560, 28, 6, "#f0e8dc", BOL)
    line(g, [(1290, 690), (1500, 690)], 3, "#ffffff", 0.8)
    # on the desk: bell, guest book, monitor (back), lamp, flowers
    ellipse(g, 1330, 682, 22, 6, "#c9ced6", BOL * 0.7)
    g.new_path()
    g.arc(1330, 680, 16, math.pi, 2 * math.pi)
    g.close_path()
    fill_stroke(g, "#dfe5ea", BOL * 0.7)
    circle(g, 1330, 660, 4, "#c9ced6", 1)
    poly(g, [(1380, 686), (1440, 678), (1500, 686), (1440, 694)], "#f6f1e6", BOL * 0.7)
    line(g, [(1440, 678), (1440, 694)], 1.6, OUTLINE)
    rrect(g, 1540, 600, 110, 76, 6, "#4a4f58", BOL)
    rrect(g, 1584, 674, 22, 12, 2, "#4a4f58", BOL * 0.7)
    glow(g, 1700, 590, 110, "#ffd27a", 0.4)
    line(g, [(1700, 684), (1700, 600)], 4, "#c9a14a")
    poly(g, [(1676, 560), (1724, 560), (1736, 604), (1664, 604)], "#fff0c8", BOL * 0.8)
    for k in range(7):
        a = -math.pi / 2 + (k - 3) * 0.3
        line(g, [(1775, 640), (1775 + math.cos(a) * 60, 640 + math.sin(a) * 70)], 2, "#4f8a3a")
        for j in range(3):
            ellipse(g, 1775 + math.cos(a) * (40 + j * 8), 640 + math.sin(a) * (48 + j * 9), 4, 6, LAV[(k + j) % 3], 0.5)
    blob(g, [(1760, 686), (1790, 686), (1796, 650), (1775, 626), (1754, 650)], "#e9e2f2", BOL * 0.8)


def _lobby_fg(g):
    for k in range(5):
        monstera(g, -60 + k * 14, 1120, 1.4, -1.2 + k * 0.25, "#3f8f3a" if k % 2 else "#4a9a40")


@extra
def _hotel_lobby(ctx, layer, t, tod):
    night = bool(P("night", tod == "night"))
    if layer == "SKY":
        fill_world(ctx, "#e9d9b8")
    elif layer == "MG":
        cached(ctx, ("lobby", "wall", night), lambda g: _lobby_wall(g, night))
    elif layer == "GROUND":
        cached(ctx, ("lobby", "floor", night), lambda g: _lobby_floor(g, night))
    elif layer == "OVER":
        if night:
            darkness(ctx, [(960, 300, 900, 0.9), (1600, 400, 600, 0.9), (620, 320, 400, 0.8)], 0.35)
    elif layer == "FG":
        cached(ctx, ("lobby", "FG"), _lobby_fg)


# =========================================================================== 6. hotel_room

def _room_wall(g, night):
    wall = "#f1e6d8" if not night else "#b9a68c"
    acc = "#c9b6dc" if not night else "#8f7ca8"
    fill_world(g, wall)
    rrect(g, 330, 160, 1290, 610, 0, acc, BOL * 0.8)
    for k in range(1, 12):
        line(g, [(330 + k * 107.5, 166), (330 + k * 107.5, 764)], 2, shade(acc, -0.08))
    g.new_path()
    g.rectangle(X0 - 500, -700, X1 - X0 + 1000, 760)
    src(g, shade(wall, 0.15))
    g.fill()
    rrect(g, X0 - 300, 52, X1 - X0 + 600, 18, 0, shade(wall, -0.08), BOL * 0.7)
    rrect(g, X0 - 300, 750, X1 - X0 + 600, 18, 0, shade(wall, -0.18), BOL * 0.7)
    g.new_path()
    g.rectangle(X0 - 500, 768, X1 - X0 + 1000, 900)
    src(g, "#b98a5a" if not night else "#7a5a3c")
    g.fill()
    # window with lavender curtains
    wx, wy, ww, wh = 20, 190, 250, 400
    rrect(g, wx - 14, wy - 14, ww + 28, wh + 28, 4, "#f4f0ea", BOL)
    g.save()
    g.new_path()
    g.rectangle(wx, wy, ww, wh)
    g.clip()
    if night:
        g.set_source(lin_grad(0, wy, 0, wy + wh, [(0, "#0c1636"), (1, "#2b4677")]))
        g.paint()
        r = rng(15)
        for _ in range(20):
            circle(g, r.uniform(wx, wx + ww), r.uniform(wy, wy + 200), 1.5, "#fff8d8", 0)
        for k in range(5):
            x_ = wx + k * 56
            h_ = 90 + (k * 37) % 80
            rrect(g, x_, wy + wh - h_, 50, h_ + 10, 0, "#1a2440", 0)
            for j in range(4):
                circle(g, x_ + 12 + (j % 2) * 24, wy + wh - h_ + 18 + j * 18, 3, "#ffd36b", 0)
    else:
        g.set_source(lin_grad(0, wy, 0, wy + wh, [(0, "#7fc4ee"), (1, "#d8f0fb")]))
        g.paint()
        B.cloud(g, wx + 40, wy + 70, 0.5)
        B.coconut(g, wx + 180, wy + wh + 30, 330, 0.0, lean=-0.08)
        crown_mass(g, [(wx + k * 50, wy + wh - 20 + (k % 2) * 14, 46) for k in range(7)], "#5aa84a", BOL * 0.6)
    g.restore()
    line(g, [(wx + ww / 2, wy), (wx + ww / 2, wy + wh)], 6, "#f4f0ea")
    line(g, [(wx, wy + wh * 0.45), (wx + ww, wy + wh * 0.45)], 6, "#f4f0ea")
    rrect(g, wx - 40, 156, ww + 80, 12, 5, "#8a5a34", BOL * 0.8)
    for dx in (wx - 52, wx + ww - 24):
        g.new_path()
        g.move_to(dx, 160)
        g.line_to(dx + 76, 160)
        g.curve_to(dx + 60, 360, dx + 84, 560, dx + 70, 720)
        g.line_to(dx + 6, 720)
        g.curve_to(dx - 6, 520, dx + 10, 300, dx, 160)
        g.close_path()
        fill_stroke(g, "#a98bd0" if not night else "#7a62a0", BOL)
        for k in range(1, 4):
            line(g, [(dx + k * 18, 170), (dx + k * 18 + 2, 710)], 2.2, "#8a6cb8" if not night else "#5f4a84")
    # lotus painting above the bedside table
    rrect(g, 860, 260, 200, 150, 4, "#c9a14a", BOL)
    g.save()
    g.new_path()
    g.rectangle(874, 274, 172, 122)
    g.clip()
    src(g, "#5fb0b8")
    g.paint()
    B.lotus(g, 960, 372, 1.3)
    B.lotus(g, 910, 386, 0.7, bloom=False)
    g.restore()
    rrect(g, 874, 274, 172, 122, 2, None, BOL * 0.7)
    # wall AC unit
    rrect(g, 1240, 180, 230, 66, 12, "#f8f8f6", BOL)
    for k in range(4):
        line(g, [(1256, 222 + k * 5), (1454, 222 + k * 5)], 1.6, "#c9ced6")
    circle(g, 1446, 196, 3, "#4ad06a", 0)
    # bathroom door ajar
    dx0, dx1, dy0 = 1690, 1890, 300
    rrect(g, dx0 - 14, dy0 - 14, dx1 - dx0 + 28, 770 - dy0 + 14, 3, "#f4f0ea", BOL)
    g.new_path()
    g.rectangle(dx0, dy0, dx1 - dx0, 770 - dy0)
    g.set_source(lin_grad(dx0, 0, dx1, 0, [(0, "#fffaf0" if night else "#f2f7fa"),
                                          (1, "#ffe9b8" if night else "#d8e8ee")]))
    g.fill()
    for k in range(1, 6):
        line(g, [(dx0, dy0 + k * 78), (dx0 + 90, dy0 + k * 78)], 1.6, "#b8ccd6")
    for k in range(1, 3):
        line(g, [(dx0 + k * 45, dy0), (dx0 + k * 45, 768)], 1.6, "#b8ccd6")
    rrect(g, dx0 + 14, 470, 60, 50, 6, "#e8f4f8", BOL * 0.6)
    rrect(g, dx0 + 20, 528, 50, 8, 2, "#c9ced6", 1.2)
    poly(g, [(dx0 + 92, dy0 + 6), (dx1 + 6, dy0 - 10), (dx1 + 6, 786), (dx0 + 92, 766)], "#efe6da", BOL)
    rrect(g, dx0 + 110, 520, 12, 40, 4, "#c9a14a", BOL * 0.6)
    for yy in (dy0 + 40, dy0 + 250):
        poly(g, [(dx0 + 116, yy), (dx1 - 10, yy - 8), (dx1 - 10, yy + 160), (dx0 + 116, yy + 150)], None, 1.6)
    # towel on a hook
    circle(g, 1630, 470, 6, "#c9a14a", 1.2)
    g.new_path()
    g.move_to(1600, 470)
    g.line_to(1660, 470)
    g.curve_to(1670, 540, 1660, 600, 1668, 640)
    g.line_to(1594, 640)
    g.curve_to(1600, 600, 1590, 540, 1600, 470)
    g.close_path()
    fill_stroke(g, "#ffffff" if not night else "#ddd6e6", BOL)
    rrect(g, 1594, 610, 74, 12, 2, "#a98bd0", 0)


def _bed(g, cx, night):
    sheet = "#ffffff" if not night else "#e6e0ee"
    rrect(g, cx - 240, 500, 480, 220, 40, "#8d78a8" if not night else "#6a5a82", BOL)
    for k in range(1, 4):
        line(g, [(cx - 240 + k * 120, 520), (cx - 240 + k * 120, 700)], 2, "#7a6696")
    rrect(g, cx - 246, 868, 492, 30, 4, "#8a5a34", BOL)
    for sd in (-1, 1):
        rrect(g, cx + sd * 220 - 9, 892, 18, 18, 2, "#6a4226", BOL * 0.7)
    poly(g, [(cx - 214, 690), (cx + 214, 690), (cx + 236, 820), (cx - 236, 820)], sheet, BOL)
    rrect(g, cx - 236, 818, 472, 56, 6, sheet, BOL)
    for sd in (-1, 1):
        pillow(g, cx + sd * 100, 704, 170, 54, "#fbfaf6")
    poly(g, [(cx - 226, 760), (cx + 226, 760), (cx + 232, 792), (cx - 232, 792)], "#9b6ac8", BOL * 0.8)
    rrect(g, cx - 236, 818, 472, 18, 4, "#9b6ac8", BOL * 0.6)
    line(g, [(cx - 200, 724), (cx + 190, 728)], 2, "#d6d0dc")
    ellipse(g, cx, 742, 44, 14, "#ffffff", BOL * 0.7)
    flower(g, cx, 736, 11, "#c56bd8", "#f2c14e", 1.0)


def _room_floor(g, night):
    plank_floor(g, 768, "#c08f5e" if not night else "#8a6644", "#a0723f" if not night else "#6a4a2e", seed=9, rows=9)
    g.new_path()
    ellipse_path(g, 960, 960, 640, 70)
    src(g, "#e9dff0" if not night else "#a89cb8")
    g.fill()
    _bed(g, 560, night)
    _bed(g, 1340, night)
    rrect(g, 870, 664, 180, 106, 6, "#8a5a34", BOL)
    rrect(g, 862, 654, 196, 18, 4, "#a8703f", BOL)
    rrect(g, 890, 700, 140, 26, 4, "#7a4a2a", BOL * 0.7)
    circle(g, 960, 713, 4, "#e9c24a", 1)
    blob(g, [(938, 654), (982, 654), (976, 620), (944, 620)], "#f2efe6", BOL * 0.8)
    line(g, [(960, 620), (960, 600)], 4, "#c9a14a")
    poly(g, [(924, 548), (996, 548), (1012, 604), (908, 604)], "#fff0c8" if night else "#f6ead2", BOL)
    rrect(g, 1010, 640, 26, 16, 3, "#2a2a30", BOL * 0.6)
    backpack(g, 300, 910, 1.0, "#d8433a")
    backpack(g, 1500, 812, 0.85, "#2f6fb2", "#1f4f8a")
    duffel(g, 1660, 930, 0.85, "#3a9a5a", "#f2c14e")


@extra
def _hotel_room(ctx, layer, t, tod):
    night = bool(P("night", tod == "night"))
    if layer == "SKY":
        fill_world(ctx, "#e9dccb")
    elif layer == "MG":
        cached(ctx, ("room", "wall", night), lambda g: _room_wall(g, night))
        # shower steam drifting out of the half-open bathroom door
        for k in range(8):
            ph = (t * 0.11 + k / 8.0) % 1.0
            x = 1740 - ph * 300 + math.sin(t * 0.6 + k * 1.7) * 16
            y = 640 - ph * 360 - math.sin(ph * math.pi) * 30
            rr = 22 + ph * 52
            a = 0.75 * math.sin(ph * math.pi) ** 1.1
            for dx, dy, f in ((0, 0, 1.0), (-0.7, 0.25, 0.7), (0.65, 0.3, 0.65)):
                ctx.new_path()
                ctx.arc(x + dx * rr, y + dy * rr, rr * f, 0, TAU)
                ctx.set_source_rgba(0.70, 0.74, 0.86, a * 0.55)
                ctx.set_line_width(3)
                ctx.stroke_preserve()
                ctx.set_source_rgba(1, 1, 1, a * 0.8)
                ctx.fill()
    elif layer == "GROUND":
        cached(ctx, ("room", "floor", night), lambda g: _room_floor(g, night))
        if night:
            glow(ctx, 960, 580, 260, "#ffcf7a", 0.45)
    elif layer == "OVER":
        if night:
            darkness(ctx, [(960, 560, 1000, 1.0), (1790, 520, 420, 0.8), (140, 400, 300, 0.4)], 0.45)
            glow(ctx, 960, 576, 520, "#ffb35a", 0.10, add=True)


# =========================================================================== 7. fern_cafe

def _cafe_wall(g):
    wall = "#f3efe4"
    fill_world(g, wall)
    r = rng(71)
    for row in range(0, 30):
        yy = -40 + row * 28
        off = 0 if row % 2 else 42
        for k in range(-8, 40):
            if r.random() < 0.5:
                rrect(g, k * 84 + off, yy, 80, 24, 3, shade(wall, r.uniform(-0.05, 0.0)), 0)
    # ceiling with beams
    g.new_path()
    g.rectangle(X0 - 500, -700, X1 - X0 + 1000, 740)
    src(g, "#8a6a4a")
    g.fill()
    for k in range(-8, 40):
        line(g, [(k * 90, -700), (k * 90, 30)], 3, "#6a4e34")
    rrect(g, X0 - 300, 26, X1 - X0 + 600, 34, 2, "#5e4430", BOL)
    # big steel-framed windows onto a sunny garden
    for wx0, wx1 in ((110, 620), (700, 1220), (1300, 1810)):
        rrect(g, wx0 - 10, 130, wx1 - wx0 + 20, 572, 2, "#2f3a34", BOL)
        g.save()
        g.new_path()
        g.rectangle(wx0, 140, wx1 - wx0, 552)
        g.clip()
        g.set_source(lin_grad(0, 140, 0, 692, [(0, "#d6f0f6"), (0.5, "#eef8e6"), (1, "#cfe9b8")]))
        g.paint()
        rr = rng(wx0)
        pts = [(x_, 330 + rr.uniform(-40, 60), rr.uniform(60, 110)) for x_ in range(wx0 - 60, wx1 + 80, 70)]
        crown_mass(g, pts + [(x_, 600, 140) for x_ in range(wx0, wx1 + 60, 120)], "#7fc06a", BOL * 0.6)
        for x_, y_, r_ in pts:
            ellipse(g, x_ - r_ * 0.3, y_ - r_ * 0.3, r_ * 0.4, r_ * 0.25, "#a6d88a", 0)
        crown_mass(g, [(x_, 640 + rr.uniform(-20, 20), 70) for x_ in range(wx0 - 40, wx1 + 60, 60)], "#4f9a40",
                   BOL * 0.6)
        for _ in range(4):
            B.banana(g, rr.uniform(wx0, wx1), 700, 1.2, 0.0)
        g.restore()
        for k in range(1, 4):
            xx = wx0 + k * (wx1 - wx0) / 4
            line(g, [(xx, 140), (xx, 692)], 7, "#2f3a34")
        for k in range(1, 4):
            yy = 140 + k * 138
            line(g, [(wx0, yy), (wx1, yy)], 7, "#2f3a34")
        rrect(g, wx0 - 24, 690, wx1 - wx0 + 48, 18, 3, "#b07a45", BOL)
        for k in range(4):
            px = wx0 + 50 + k * (wx1 - wx0 - 100) / 3
            small_pot_plant(g, px, 692, 1.3, ["#f2efe6", "#d9774a", "#9fc6b0", "#f2efe6"][k],
                            ["#5aa84a", "#3f8f3a", "#7cc04a", "#4caf50"][k])
    # shelves at both ends with plants, (wordless) books and trailing pothos
    for sx0 in (-420, 1850):
        for k in range(3):
            yy = 260 + k * 160
            rrect(g, sx0, yy, 500, 14, 2, "#9a6a3e", BOL)
            for j in range(5):
                px = sx0 + 40 + j * 96
                if (j + k) % 3 == 0:
                    for b in range(4):
                        rrect(g, px - 30 + b * 15, yy - 54 + (b % 2) * 6, 13, 54 - (b % 2) * 6, 2,
                              ["#d8433a", "#2f7fc0", "#f2c14e", "#3a9a5a"][b], 1.4)
                else:
                    small_pot_plant(g, px, yy, 1.5, ["#f2efe6", "#d9774a"][j % 2])
                    if (j + k) % 2:
                        pothos(g, px + 10, yy + 10, 90 + (j * 23) % 70, 1.0, seed=j * 7 + k)
    # soft afternoon light shafts
    for x0_ in (160, 750, 1350):
        g.new_path()
        poly_path(g, [(x0_, 140), (x0_ + 260, 140), (x0_ + 560, 770), (x0_ + 300, 770)])
        g.set_source_rgba(1, 0.98, 0.85, 0.10)
        g.fill()
    g.new_path()
    g.rectangle(X0 - 500, 768, X1 - X0 + 1000, 900)
    src(g, "#c99a66")
    g.fill()


def _cafe_floor(g):
    plank_floor(g, 768, "#d2a56e", "#b0824e", seed=21, rows=9)
    for x0_ in (220, 820, 1420):
        g.new_path()
        poly_path(g, [(x0_ + 120, 770), (x0_ + 380, 770), (x0_ + 520, 1080), (x0_ + 200, 1080)])
        g.set_source_rgba(1, 0.97, 0.8, 0.12)
        g.fill()
    # cushioned bench along the window wall
    rrect(g, X0 - 300, 700, X1 - X0 + 600, 84, 4, "#9a6a3e", BOL)
    for k in range(-6, 30):
        rrect(g, k * 120 + 6, 690, 108, 26, 10, "#7fae7a", BOL * 0.8)
    for k in range(-6, 30):
        line(g, [(k * 120, 722), (k * 120, 782)], 2, "#7a5230")
    # big floor plants
    for k in range(6):
        monstera(g, 40 + k * 8, 800, 1.1, -2.4 + k * 0.32, "#3f8f3a" if k % 2 else "#4a9a40")
    poly(g, [(10, 800), (90, 800), (78, 880), (22, 880)], "#f2efe6", BOL)
    line(g, [(1880, 880), (1880, 520)], 6, "#6a4a30")
    r = rng(5)
    for k in range(16):
        ly = 540 + k * 20
        sd = 1 if k % 2 else -1
        ellipse(g, 1880 + sd * 30, ly, 30, 20, shade("#3f8f3a", r.uniform(-0.1, 0.12)), BOL * 0.6, rot=sd * 0.5)
    poly(g, [(1840, 860), (1920, 860), (1908, 930), (1852, 930)], "#d9774a", BOL)


def _fern_rec(seed, pot, L):
    def draw(g):
        line(g, [(0, -400), (0, L)], 2.5, "#7a5a3a")
        for sd in (-1, 0, 1):
            line(g, [(0, L), (sd * 38, L + 40)], 2, "#7a5a3a")
        fern_pot(g, 0, L + 40, 1.0, seed, pot)
    return recording(("fern", seed, pot, L), draw)


def _lamp_rec(L):
    def draw(g):
        line(g, [(0, -400), (0, L)], 2.5, OUTLINE)
        g.new_path()
        g.move_to(-50, L + 70)
        g.curve_to(-54, L, 54, L, 50, L + 70)
        g.close_path()
        fill_stroke(g, "#d6a861", BOL)
        for k in range(1, 5):
            curve(g, (-48 + k * 19, L + 14), (-50 + k * 20, L + 40), (-48 + k * 19, L + 70), 1.6, "#a8783a")
        for k in range(1, 3):
            line(g, [(-46, L + 20 + k * 18), (46, L + 20 + k * 18)], 1.4, "#a8783a")
        ellipse(g, 0, L + 70, 50, 8, "#fff0c8", BOL * 0.7)
    return recording(("ratlamp", L), draw)


FERNS = ((150, 60, 1, "#f2efe6"), (660, 40, 2, "#d9774a"), (1260, 60, 3, "#f2efe6"), (1830, 44, 4, "#9fc6b0"),
         (-300, 50, 5, "#d9774a"), (2280, 50, 6, "#f2efe6"))
LAMPS = ((420, 170), (980, 200), (1540, 170))


@extra
def _fern_cafe(ctx, layer, t, tod):
    if layer == "SKY":
        fill_world(ctx, "#efe9dc")
    elif layer == "MG":
        cached(ctx, ("cafe", "wall"), _cafe_wall)
        for x, L, seed, pot in FERNS:
            paint_rec(ctx, _fern_rec(seed, pot, L), x, 60, math.sin(t * 0.5 + seed) * 0.018)
        for k, (x, L) in enumerate(LAMPS):
            glow(ctx, x, 60 + L + 80, 160, "#ffd27a", 0.32)
            paint_rec(ctx, _lamp_rec(L), x, 60, math.sin(t * 0.4 + k) * 0.008)
    elif layer == "GROUND":
        cached(ctx, ("cafe", "floor"), _cafe_floor)
        tabs, w, chairs = table_conf()
        draw_chairs(ctx, chairs, "rattan", ("#d1a564", "#c4955a"))
    elif layer == "OVER":
        tabs, w, chairs = table_conf()
        draw_tables(ctx, tabs, w, "wood", P("menu", "cafe"), t, bool(P("items", True)))
    elif layer == "FG":
        cached(ctx, ("cafe", "FG"), _cafe_fg)
        for k, x in enumerate((-90, 2010)):
            for j in range(3):
                pothos(ctx, x + j * 30 * (1 if k == 0 else -1), -60, 220 + j * 60, 1.4, seed=40 + j + k * 5,
                       sway=math.sin(t * 0.6 + j + k) * 10)


def _cafe_fg(g):
    for k in range(6):
        monstera(g, -80 + k * 10, 1130, 1.5, -1.3 + k * 0.22, "#3a8a35" if k % 2 else "#469a3f")
    for k in range(5):
        monstera(g, 2010 - k * 10, 1130, 1.4, -1.9 - k * 0.22, "#3a8a35" if k % 2 else "#469a3f")


# =========================================================================== 8. pub_street

SHOP_COLS = ("#f2b84a", "#f08a6a", "#8fd6b4", "#f4dca8", "#9cc8ec", "#f2a6c8", "#c8e07a", "#e8c070")
SIGN_COLS = ("#ff3fa0", "#2fe0ff", "#7cff4a", "#ffe23a", "#ff8a2a", "#c06aff")
ICONS = ("cocktail", "beer", "star", "heart", "note", "palm", "bowl")
SHOP_W = 380


def neon_icon(ctx, kind, x, y, s, col, width=4.0):
    ctx.save()
    src(ctx, col)
    ctx.set_line_width(width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.new_path()
    if kind == "cocktail":
        ctx.move_to(x - 18 * s, y - 16 * s)
        ctx.line_to(x + 18 * s, y - 16 * s)
        ctx.line_to(x, y + 4 * s)
        ctx.close_path()
        ctx.move_to(x, y + 4 * s)
        ctx.line_to(x, y + 20 * s)
        ctx.move_to(x - 10 * s, y + 20 * s)
        ctx.line_to(x + 10 * s, y + 20 * s)
        ctx.new_sub_path()
        ctx.arc(x + 12 * s, y - 20 * s, 5 * s, 0, TAU)
    elif kind == "beer":
        ctx.rectangle(x - 13 * s, y - 14 * s, 22 * s, 32 * s)
        ctx.new_sub_path()
        ctx.arc(x + 12 * s, y + 2 * s, 8 * s, -math.pi / 2, math.pi / 2)
        ctx.move_to(x - 13 * s, y - 14 * s)
        ctx.curve_to(x - 14 * s, y - 24 * s, x + 10 * s, y - 24 * s, x + 9 * s, y - 14 * s)
    elif kind == "star":
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            rr = (20 if k % 2 == 0 else 8.5) * s
            (ctx.move_to if k == 0 else ctx.line_to)(x + math.cos(a) * rr, y + math.sin(a) * rr)
        ctx.close_path()
    elif kind == "heart":
        ctx.move_to(x, y + 18 * s)
        ctx.curve_to(x - 26 * s, y, x - 16 * s, y - 22 * s, x, y - 8 * s)
        ctx.curve_to(x + 16 * s, y - 22 * s, x + 26 * s, y, x, y + 18 * s)
    elif kind == "note":
        ctx.new_sub_path()
        ctx.arc(x - 6 * s, y + 12 * s, 7 * s, 0, TAU)
        ctx.move_to(x + 1 * s, y + 12 * s)
        ctx.line_to(x + 1 * s, y - 20 * s)
        ctx.line_to(x + 14 * s, y - 12 * s)
    elif kind == "palm":
        tx, ty = x + 3 * s, y - 12 * s
        ctx.move_to(x - 4 * s, y + 22 * s)
        ctx.curve_to(x - 3 * s, y + 6 * s, x + 4 * s, y - 2 * s, tx, ty)
        for a, L in ((-3.0, 24), (-2.3, 20), (-0.85, 20), (-0.15, 24)):
            ex, ey = tx + math.cos(a) * L * s, ty + math.sin(a) * L * s * 0.5
            ctx.move_to(tx, ty)
            ctx.curve_to(tx + math.cos(a) * L * s * 0.5, ty - 12 * s, ex, ey - 6 * s, ex, ey + 9 * s)
    else:  # bowl with chopsticks
        ctx.move_to(x - 20 * s, y - 2 * s)
        ctx.curve_to(x - 18 * s, y + 18 * s, x + 18 * s, y + 18 * s, x + 20 * s, y - 2 * s)
        ctx.close_path()
        ctx.move_to(x + 2 * s, y - 6 * s)
        ctx.line_to(x + 18 * s, y - 24 * s)
        ctx.move_to(x + 8 * s, y - 4 * s)
        ctx.line_to(x + 24 * s, y - 20 * s)
    ctx.stroke()
    ctx.restore()


_SHOPS = []


def _shops():
    if not _SHOPS:
        for k, x in enumerate(range(X0 - 40, X1 + 40, SHOP_W)):
            _SHOPS.append(dict(k=k, x=x, col=SHOP_COLS[k % len(SHOP_COLS)], sign=SIGN_COLS[(k * 2) % len(SIGN_COLS)],
                               icon=ICONS[k % len(ICONS)], awning=k % 3 != 1, blade=k % 2 == 0,
                               blade_col=SIGN_COLS[(k * 2 + 3) % len(SIGN_COLS)], blade_icon=ICONS[(k + 3) % len(ICONS)]))
    return _SHOPS


def _pub_facades(g):
    g.new_path()
    g.rectangle(X0 - 500, 0, X1 - X0 + 1000, 220)
    g.set_source(lin_grad(0, 0, 0, 220, [(0, (1, 0.6, 0.3, 0.0)), (1, (1, 0.6, 0.3, 0.35))]))
    g.fill()
    for sh in _shops():
        x, w, col = sh["x"], SHOP_W, sh["col"]
        k = sh["k"]
        roof_y = 150 + (k % 3) * 18
        if k % 2:
            poly(g, [(x - 6, roof_y + 10), (x + w / 2, roof_y - 50), (x + w + 6, roof_y + 10)], "#c4643c", BOL)
        rrect(g, x, roof_y, w, 770 - roof_y, 0, col, BOL)
        rrect(g, x - 8, roof_y - 4, w + 16, 22, 2, shade(col, -0.12), BOL)
        for px in (x + 12, x + w - 28):
            rrect(g, px, roof_y + 18, 16, 760 - roof_y - 18, 0, shade(col, 0.2), BOL * 0.6)
        # upper floor: French windows with shutters + balcony
        for j in range(2):
            wx = x + 92 + j * 196
            for sd in (-1, 1):
                sx = wx - 34 - 28 if sd < 0 else wx + 34
                rrect(g, sx, 230, 28, 150, 2, ["#2f8a6a", "#2f6fb2", "#a8432a"][k % 3], BOL * 0.7)
                for m in range(1, 7):
                    line(g, [(sx + 3, 230 + m * 21), (sx + 25, 230 + m * 21)], 1.4, (0, 0, 0), 0.3)
            g.new_path()
            g.move_to(wx - 34, 380)
            g.line_to(wx - 34, 262)
            g.arc(wx, 262, 34, math.pi, 2 * math.pi)
            g.line_to(wx + 34, 380)
            g.close_path()
            fill_stroke(g, "#ffd36b" if (k + j) % 3 else "#ffb0d0", BOL)
            line(g, [(wx, 236), (wx, 380)], 3, shade(col, -0.3))
        rrect(g, x + 6, 380, w - 12, 12, 2, shade(col, -0.18), BOL * 0.8)
        for m in range(int((w - 24) / 12)):
            line(g, [(x + 16 + m * 12, 344), (x + 16 + m * 12, 380)], 2, "#2a2230")
        line(g, [(x + 10, 344), (x + w - 10, 344)], 4, "#2a2230")
        # signboard: blank colour panel with a neon icon (no words)
        rrect(g, x + 40, 400, w - 80, 66, 8, "#2a2230", BOL)
        rrect(g, x + 48, 408, w - 96, 50, 5, shade(sh["sign"], -0.55), 0)
        neon_icon(g, sh["icon"], x + w / 2, 433, 0.9, sh["sign"], 4)
        for sd in (-1, 1):
            for m in range(3):
                circle(g, x + w / 2 + sd * (60 + m * 34), 433, 5, sh["sign"], 0)
        # glowing shop front
        sx0, sx1 = x + 30, x + w - 30
        g.new_path()
        g.rectangle(sx0, 480, sx1 - sx0, 290)
        g.set_source(lin_grad(0, 480, 0, 770, [(0, "#fff4c0"), (1, "#ffb84a")]))
        g.fill()
        r = rng(k)
        kind = k % 3
        if kind == 0:  # bar: bottle shelves + counter
            for m in range(3):
                line(g, [(sx0 + 10, 530 + m * 40), (sx1 - 10, 530 + m * 40)], 4, "#8a5a34")
                for b in range(10):
                    bx = sx0 + 22 + b * (sx1 - sx0 - 44) / 9
                    rrect(g, bx - 5, 530 + m * 40 - 24, 10, 24, 3,
                          r.choice(("#e84a5f", "#2fa59a", "#f2c14e", "#7a4ab8", "#3a9a5a")), 1)
            rrect(g, sx0 + 10, 680, sx1 - sx0 - 20, 90, 4, "#7a3a24", BOL)
        elif kind == 1:  # restaurant: lamps + tables
            for m in range(3):
                lx = sx0 + 50 + m * (sx1 - sx0 - 100) / 2
                line(g, [(lx, 480), (lx, 520)], 2, "#5a3a24")
                ellipse(g, lx, 528, 18, 10, "#ff7a3a", 1.2)
                rrect(g, lx - 40, 690, 80, 12, 2, "#8a4a2a", 1.4)
                line(g, [(lx - 30, 700), (lx - 30, 770)], 5, "#8a4a2a")
                line(g, [(lx + 30, 700), (lx + 30, 770)], 5, "#8a4a2a")
        else:  # shop: pink light, lanterns and goods
            g.new_path()
            g.rectangle(sx0, 480, sx1 - sx0, 290)
            g.set_source_rgba(1, 0.4, 0.7, 0.25)
            g.fill()
            for m in range(4):
                lx = sx0 + 30 + m * (sx1 - sx0 - 60) / 3
                ellipse(g, lx, 540, 14, 18, "#e8333a", 1.2)
            for m in range(5):
                rrect(g, sx0 + 20 + m * 60, 640, 44, 130, 4, r.choice(("#f2c14e", "#9b3fb5", "#2fa59a")), 1.2)
        rrect(g, sx0, 480, sx1 - sx0, 290, 0, None, BOL)
        if sh["awning"]:
            poly(g, [(sx0 - 14, 470), (sx1 + 14, 470), (sx1 + 30, 530), (sx0 - 30, 530)],
                 stripe_pattern("#e8333a", "#fff6ea", 22, vertical=True), BOL)
            n = 9
            for m in range(n):
                cx_ = sx0 - 30 + (sx1 - sx0 + 60) * (m + 0.5) / n
                ellipse(g, cx_, 532, (sx1 - sx0 + 60) / n / 2, 9, "#e8333a" if m % 2 else "#fff6ea", BOL * 0.6)
        if sh["blade"]:
            bx = x + w - 20
            rrect(g, bx - 30, 220, 60, 120, 8, "#2a2230", BOL)
            rrect(g, bx - 24, 226, 48, 108, 5, shade(sh["blade_col"], -0.55), 0)
            neon_icon(g, sh["blade_icon"], bx, 280, 0.8, sh["blade_col"], 3.5)
    # sidewalk the crowd stands on
    g.new_path()
    g.rectangle(X0 - 500, 768, X1 - X0 + 1000, 900)
    src(g, "#b8a890")
    g.fill()
    line(g, [(X0 - 500, 770), (X1 + 500, 770)], 3, "#8a7a64")
    for k in range(-10, 40):
        line(g, [(k * 110, 770), (k * 110 - 30, 820)], 2, "#9a8a72")


def _pub_bg(g):
    r = rng(81)
    x = X0 - 100
    while x < X1 + 100:
        w = r.uniform(120, 260)
        h = r.uniform(80, 220)
        rrect(g, x, 260 - h, w, h + 400, 2, "#3a3050", 0)
        for _ in range(int(w * h / 3000)):
            circle(g, x + r.uniform(10, w - 10), 260 - h + r.uniform(10, h), 3, "#ffcf6a", 0)
        x += w + r.uniform(0, 40)
    for x in (-200, 380, 1280, 2000):
        line(g, [(x, 300), (x + 10, 80)], 8, "#2a2440")
        for k in range(9):
            a = -math.pi + k * math.pi / 8
            line(g, [(x + 10, 80), (x + 10 + math.cos(a) * 60, 80 + math.sin(a) * 36 + 20)], 6, "#2a2440")


def _zig_bulbs(x0, x1, y_low, y_high, seg, sag, spacing, seed):
    """Zig-zag light strings between facade points (y_low) and points high above the street (y_high)."""
    wires = []
    k = 0
    x = x0
    r = rng(seed)
    while x < x1:
        a = (x, y_low) if k % 2 == 0 else (x, y_high)
        b = (x + seg, y_high) if k % 2 == 0 else (x + seg, y_low)
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(2, int(L / spacing))
        wires.append([(lerp(a[0], b[0], i / n), lerp(a[1], b[1], i / n) + sag * math.sin(math.pi * i / n))
                      for i in range(n + 1)])
        x += seg
        k += 1
    bulbs = []
    cols = ("#fff0a0", "#ff5a5a", "#ffd23a", "#5aff8a", "#5ab8ff", "#ff7ad8")
    for wire in wires:
        for i in range(1, len(wire) - 1):
            bulbs.append((wire[i][0], wire[i][1] + 6, cols[r.randrange(len(cols))], r.uniform(0, 6)))
    return wires, bulbs


_ZIG = {}
ZIG_ARGS = {"mid": (X0 - 200, X1 + 200, 214, -120, 230, 26, 34, 11),
            "near": (X0 - 600, X1 + 600, 60, -260, 300, 60, 46, 12)}


def zig(name):
    if name not in _ZIG:
        _ZIG[name] = _zig_bulbs(*ZIG_ARGS[name])
    return _ZIG[name]


def draw_bulbs(ctx, wires, bulbs, t, r=6.0, wire="#2a2230"):
    for w_ in wires:
        line(ctx, w_, 2.2, wire)
    for x, y, c, ph in bulbs:
        k = 0.75 + 0.25 * math.sin(t * 1.1 + ph)
        circle(ctx, x, y, r, mix("#6a4a2a", c, k), 1.2)


def bulb_glows(ctx, bulbs, t, r=26, a=0.55):
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_ADD)
    for x, y, c, ph in bulbs:
        k = 0.7 + 0.3 * math.sin(t * 1.1 + ph)
        cc = hexc(c)
        ctx.new_path()
        ctx.arc(x, y, r, 0, TAU)
        ctx.set_source(rad_grad(x, y, 0, r, [(0, cc + (a * k,)), (0.25, cc + (a * k * 0.5,)), (1, cc + (0.0,))]))
        ctx.fill()
    ctx.restore()


def lantern(ctx, x, y, s, col, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    line(ctx, [(0, 0), (0, 14 * s)], 2, "#2a2230")
    rrect(ctx, -12 * s, 12 * s, 24 * s, 8 * s, 2, "#e9b53b", BOL * 0.6)
    ellipse(ctx, 0, 44 * s, 30 * s, 26 * s, col, BOL * 0.8)
    for k in (-1, 1):
        ctx.new_path()
        ellipse_path(ctx, 0, 44 * s, 30 * s * 0.55, 26 * s)
        src(ctx, shade(col, -0.25))
        ctx.set_line_width(1.6)
        ctx.stroke()
    line(ctx, [(0, 18 * s), (0, 70 * s)], 1.6, shade(col, -0.25))
    rrect(ctx, -12 * s, 68 * s, 24 * s, 8 * s, 2, "#e9b53b", BOL * 0.6)
    line(ctx, [(0, 76 * s), (0, 100 * s)], 3 * s, "#e9b53b")
    ctx.restore()


LANTERNS = [(x, ["#e8333a", "#ff8a2a", "#e8333a", "#ffd23a"][i % 4]) for i, x in enumerate(range(-560, 2700, 260))]


def _fg_string_y(x):
    u = ((x + 600) % 520) / 520.0
    return 40 + 70 * math.sin(math.pi * u)


def crowd(ctx, t, y, n=34, seed=5, scale=1.0):
    """Simple silhouettes milling in front of the shops; a few stroll slowly."""
    r = rng(seed)
    cols = ("#3b3352", "#4a3a5a", "#2f3f5a", "#55405a", "#3a4a4a", "#5a4a3a")
    for i in range(n):
        x0 = r.uniform(X0 - 100, X1 + 100)
        sp = r.choice((0, 0, 0, r.uniform(14, 30), -r.uniform(14, 30)))
        x = (x0 - X0 + 200 + t * sp) % (X1 - X0 + 400) + X0 - 200
        h = r.uniform(170, 215) * scale
        yy = y + r.uniform(-8, 6)
        col = r.choice(cols)
        bob = math.sin(t * r.uniform(1.0, 1.6) + i) * 2.0 + (abs(math.sin(t * 4 + i)) * 3 if sp else 0)
        bw = h * r.uniform(0.17, 0.22)
        sw = math.sin(t * 4 + i) * (6 if sp else 0)
        for sd in (-1, 1):
            line(ctx, [(x + sd * bw * 0.22, yy - h * 0.45), (x + sd * bw * 0.22 + sd * sw * 0.5, yy)], bw * 0.34,
                 shade(col, -0.2))
        rrect(ctx, x - bw / 2, yy - h * 0.80 - bob, bw, h * 0.42, bw * 0.38, col, 0)
        circle(ctx, x, yy - h * 0.88 - bob, h * 0.1, shade(col, 0.08), 0)
        if i % 5 == 0:
            ellipse(ctx, x, yy - h * 0.95 - bob, h * 0.15, h * 0.035, shade(col, -0.1), 0)
        elif i % 7 == 0:
            rrect(ctx, x - bw * 0.62, yy - h * 0.78 - bob, bw * 0.3, h * 0.28, 5, "#7a4a3a", 0)
        line(ctx, [(x + bw * 0.42, yy - h * 0.78 - bob), (x + bw * 0.46, yy - h * 0.52 - bob)], 2.4, "#ffb860", 0.55)
        if i % 9 == 4:
            rrect(ctx, x + bw * 0.4, yy - h * 0.72 - bob, 8, 12, 2, "#bfe6ff", 0)


def _pub_ground(g, view):
    g.new_path()
    g.rectangle(X0 - 500, 800, X1 - X0 + 1000, 900)
    g.set_source(lin_grad(0, 800, 0, 1080, [(0, "#8a7a8a"), (1, "#6a5a6a")]))
    g.fill()
    rrect(g, X0 - 300, 796, X1 - X0 + 600, 14, 0, "#d6c8b0", BOL * 0.8)
    for k in range(-10, 40):
        line(g, [(k * 90, 812), (k * 90 - 120, 1080)], 1.6, "#7a6a7a")
    for yy in (850, 920, 1010):
        line(g, [(X0 - 500, yy), (X1 + 500, yy)], 1.6, "#7a6a7a")
    for sh in _shops():
        cx_ = sh["x"] + SHOP_W / 2
        g.new_path()
        ellipse_path(g, cx_, 850, 200, 40)
        g.set_source(rad_grad(cx_, 850, 0, 200, [(0, (1, 0.8, 0.4, 0.45)), (1, (1, 0.8, 0.4, 0.0))]))
        g.fill()
    if view == "street":
        tuktuk(g, 1760, 905, 0.9, "#2f6fb2", "#20456e", facing=-1, lit=True)
        scooter(g, 120, 880, 0.75, "#e84a5f", 1)
    else:
        tuktuk(g, 1900, 880, 0.75, "#2f6fb2", "#20456e", facing=-1, lit=True)
        for x in (1600, 300):
            plastic_chair(g, x, 870, 0.85, "#e8333a")


def _pub_screen(ctx, t, view, tod):
    if tod == "night":
        # warm street light: colour-dodge lifts red/green that the blue night multiply removed, then a warm multiply
        ctx.save()
        if with_matrix(ctx, "pubMG"):
            ctx.set_operator(cairo.OPERATOR_COLOR_DODGE)
            c = (0.48, 0.40, 0.0)
            ctx.set_source(lin_grad(0, 140, 0, 620, [(0, c + (0.10,)), (1, c + (0.78,))]))
            ctx.rectangle(X0 - 500, -700, X1 - X0 + 1000, 2400)
            ctx.fill()
            ctx.set_operator(cairo.OPERATOR_MULTIPLY)
            m = (1.0, 0.88, 0.64)
            ctx.set_source(lin_grad(0, 140, 0, 620, [(0, m + (0.0,)), (1, m + (0.55,))]))
            ctx.rectangle(X0 - 500, -700, X1 - X0 + 1000, 2400)
            ctx.fill()
        ctx.restore()
    ctx.save()
    if with_matrix(ctx, "pubMG"):
        ctx.set_operator(cairo.OPERATOR_ADD)
        for sh in _shops():
            x = sh["x"]
            cc = hexc(sh["sign"])
            pulse = 0.85 + 0.15 * math.sin(t * 0.8 + sh["k"] * 1.9)
            ctx.new_path()
            ctx.rectangle(x + 30, 392, SHOP_W - 60, 82)
            ctx.set_source(rad_grad(x + SHOP_W / 2, 433, 10, SHOP_W * 0.5, [(0, cc + (0.30 * pulse,)), (1, cc + (0.0,))]))
            ctx.fill()
            neon_icon(ctx, sh["icon"], x + SHOP_W / 2, 433, 0.9, tuple(v * 0.7 * pulse for v in cc), 10)
            neon_icon(ctx, sh["icon"], x + SHOP_W / 2, 433, 0.9, (0.85, 0.85, 0.85), 3)
            if sh["blade"]:
                bc = hexc(sh["blade_col"])
                glow(ctx, x + SHOP_W - 20, 280, 90, sh["blade_col"], 0.32 * pulse, add=True)
                neon_icon(ctx, sh["blade_icon"], x + SHOP_W - 20, 280, 0.8, tuple(v * 0.7 for v in bc), 8)
                neon_icon(ctx, sh["blade_icon"], x + SHOP_W - 20, 280, 0.8, (0.85, 0.85, 0.85), 2.5)
            for j in range(2):
                glow(ctx, x + 92 + j * 196, 300, 70, "#ffb347", 0.22, add=True)
        wires, bulbs = zig("mid")
        bulb_glows(ctx, bulbs, t, 22, 0.55)
    ctx.restore()
    ctx.save()
    if with_matrix(ctx, "pubFG"):
        wires, bulbs = zig("near")
        bulb_glows(ctx, bulbs, t, 34, 0.6)
        for i, (x, c) in enumerate(LANTERNS):
            glow(ctx, x, _fg_string_y(x) + 74, 70, c, 0.45, add=True)
    ctx.restore()
    if view == "dinner" and P("items", True):
        ctx.save()
        if with_matrix(ctx, "pubGR"):
            tabs, w, chairs = table_conf()
            for cx in tabs:
                glow(ctx, cx + w * 0.15, TABLE_TOP - 32, 70, "#ffb347", 0.6, add=True)
        ctx.restore()


@extra
def _pub_street(ctx, layer, t, tod):
    view = P("view", "street")
    if layer == "SKY":
        sk = B.TOD.get(tod if tod in ("evening", "sunset") else "night")["sky"]
        ctx.new_path()
        ctx.rectangle(X0 - 500, -700, X1 - X0 + 1000, 1500)
        ctx.set_source(lin_grad(0, -100, 0, 500, [(0, sk[0]), (1, "#5a3a6a")]))
        ctx.fill()
        r = rng(3)
        for _ in range(40):
            circle(ctx, r.uniform(X0, X1), r.uniform(-150, 200), r.uniform(1, 2), (1, 1, 0.9), 0)
    elif layer == "BG":
        cached(ctx, ("pub", "BG"), _pub_bg)
    elif layer == "MG":
        keep_matrix(ctx, "pubMG")
        cached(ctx, ("pub", "facades"), _pub_facades)
        wires, bulbs = zig("mid")
        draw_bulbs(ctx, wires, bulbs, t, 5.5)
        for sh in _shops():
            for m in range(9):
                bx = sh["x"] + 30 + m * (SHOP_W - 60) / 8
                k = 0.7 + 0.3 * math.sin(t * 1.3 + m * 1.7 + sh["k"])
                circle(ctx, bx, 348 + 6 * math.sin(math.pi * m / 8), 4, mix("#7a5a2a", "#fff2a0", k), 0)
        crowd(ctx, t, 784, n=40, seed=5, scale=1.0)
    elif layer == "GROUND":
        keep_matrix(ctx, "pubGR")
        cached(ctx, ("pub", "street", view), lambda g: _pub_ground(g, view))
        if view == "dinner":
            tabs, w, chairs = table_conf()
            draw_chairs(ctx, chairs, "plastic", ("#e8333a", "#2f7fc0", "#3a9a5a"))
    elif layer == "OVER":
        if view == "dinner":
            tabs, w, chairs = table_conf()
            draw_tables(ctx, tabs, w, "pub", P("menu", "dinner"), t, bool(P("items", True)))
            if P("items", True):
                for cx in tabs:
                    candle_jar(ctx, cx + w * 0.15, TABLE_TOP - 3, 1.0, t)
    elif layer == "FG":
        keep_matrix(ctx, "pubFG")
        wires, bulbs = zig("near")
        draw_bulbs(ctx, wires, bulbs, t, 8)
        line(ctx, [(x_, _fg_string_y(x_) + 30) for x_ in range(X0 - 600, X1 + 620, 20)], 2.2, "#2a2230")
        for i, (x, c) in enumerate(LANTERNS):
            lantern(ctx, x, _fg_string_y(x) + 30, 1.0, c, math.sin(t * 0.8 + i * 1.3) * 0.06)
    elif layer == "SCREEN":
        _pub_screen(ctx, t, view, tod)


# =========================================================================== registry

def register(envs):
    envs.update({
        "bedroom_night": _bedroom_night,
        "restaurant": _restaurant,
        "porridge_stall": _porridge_stall,
        "hotel": _hotel,
        "hotel_lobby": _hotel_lobby,
        "hotel_room": _hotel_room,
        "fern_cafe": _fern_cafe,
        "pub_street": _pub_street,
    })
