"""1960s mid-century sets for 'Sangkum Reastr Niyum, 1955-1970'.  Flat geometric shapes after New Khmer
Architecture (louvres, folded-plate roofs, pilotis, breeze-block screens).  Every scene is a reconstruction.
Palette: faded turquoise, mustard, coral, cream, charcoal (paper.R60).  All make_* return film scene dicts."""
import math

import cast
import paper as PP
from core import SH, SW, clamp, ease, ellipse, glow, lin, mix, poly, rad, rng, rrect, smooth, src, draw_text, KM_SANS, \
    EN_SANS, KM_DISPLAY
from paper import TOD, R60, sheet, path_poly, path_ellipse
from sets import _key, _comb, people_dyn, F, grp

C = R60
GROUND = 1120


def _P(tod):
    return TOD[tod]


def rect(ctx, x, y, w, h, col, sh=0.6, seed=0):
    sheet(ctx, path_poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)]), col, shadow=sh, seed=seed)


def fill_rect(ctx, x, y, w, h, col, a=1.0):
    src(ctx, col, a)
    ctx.rectangle(x, y, w, h)
    ctx.fill()


def sky60(ctx, P, hor=0.62, sun=(0.72, 0.36), r=80, seed=0, clouds=3):
    fill_rect(ctx, 0, 0, SW, SH, mix(P["sky1"], P["haze"], 0.3))
    PP.sky(ctx, P, hor, sun, r, 6, seed)
    if clouds:
        R = rng(seed + 5)
        for i in range(clouds):   # mid-century lozenge clouds
            cx, cy, w = R.random() * SW, SH * (0.08 + 0.25 * R.random()), 240 + R.random() * 260
            col = mix(P["sky1"], "#ffffff", 0.35)
            sheet(ctx, path_poly([(cx - w / 2, cy), (cx - w / 4, cy - 30), (cx + w / 3, cy - 30), (cx + w / 2, cy)]),
                  col, shadow=0.2, seed=seed + i)


# ---------------------------------------------------------------- architectural pieces
def louvres(ctx, P, x, y, w, h, n=None, col=None, fin=None, seed=0, diag=False):
    """Facade of vertical concrete fins (brise-soleil) with shadowed slots."""
    col = col or C["conc"]
    fill_rect(ctx, x, y, w, h, mix(P["shadow"], col, 0.45))
    n = n or max(4, int(w / 34))
    step = w / n
    for k in range(n):
        fx = x + k * step
        if diag:
            poly(ctx, [(fx, y), (fx + step * 0.55, y), (fx + step * 0.85, y + h), (fx + step * 0.3, y + h)])
        else:
            poly(ctx, [(fx, y), (fx + step * 0.5, y), (fx + step * 0.5, y + h), (fx, y + h)])
        src(ctx, fin or mix(col, P["light"], 0.15))
        ctx.fill()


def breeze(ctx, P, x, y, w, h, col=None, cell=30):
    """Breeze-block screen: grid of pierced squares / diamonds."""
    col = col or C["cream"]
    fill_rect(ctx, x, y, w, h, col)
    src(ctx, mix(P["shadow"], col, 0.4))
    yy = y + cell * 0.2
    while yy < y + h - cell * 0.3:
        xx = x + cell * 0.2
        while xx < x + w - cell * 0.3:
            c = (xx + cell * 0.3, yy + cell * 0.3)
            poly(ctx, [(c[0], c[1] - cell * 0.28), (c[0] + cell * 0.28, c[1]), (c[0], c[1] + cell * 0.28),
                       (c[0] - cell * 0.28, c[1])])
            ctx.fill()
            xx += cell
        yy += cell


def folded_roof(ctx, P, x, y, w, n=6, h=46, col=None, seed=0):
    """Folded-plate (zig-zag) concrete roof, a Vann Molyvann signature."""
    col = col or C["conc"]
    step = w / n
    for k in range(n):
        x0 = x + k * step
        sheet(ctx, path_poly([(x0, y), (x0 + step / 2, y - h), (x0 + step / 2, y + 10), (x0, y + 10)]),
              mix(col, P["light"], 0.2), shadow=0.3, seed=seed + k)
        sheet(ctx, path_poly([(x0 + step / 2, y - h), (x0 + step, y), (x0 + step, y + 10), (x0 + step / 2, y + 10)]),
              mix(col, P["shadow"], 0.25), shadow=0.0, seed=seed + k)


def pilotis(ctx, P, x, y, w, h, n=6, col=None):
    """Open ground floor on slim columns (shaded void behind)."""
    col = col or C["conc"]
    fill_rect(ctx, x, y, w, h, mix(P["shadow"], C["char"], 0.4), 0.85)
    for k in range(n + 1):
        cx = x + k * (w - 14) / n
        fill_rect(ctx, cx, y, 14, h, mix(col, P["light"], 0.1))


def nk_building(ctx, P, x, base, w, h, kind="louvre", col=None, seed=0, roof=True, pil=True):
    """A New Khmer style block: pilotis + facade (louvre / breeze / diag) + folded roof."""
    col = col or C["conc"]
    ph = 70 if pil else 0
    rect(ctx, x, base - h, w, h - ph, col, 0.9, seed)
    m = 18
    if kind == "louvre":
        louvres(ctx, P, x + m, base - h + m, w - 2 * m, h - ph - 2 * m, col=col, seed=seed)
    elif kind == "diag":
        louvres(ctx, P, x + m, base - h + m, w - 2 * m, h - ph - 2 * m, col=col, seed=seed, diag=True)
    elif kind == "breeze":
        breeze(ctx, P, x + m, base - h + m, w - 2 * m, h - ph - 2 * m, col=mix(col, "#ffffff", 0.2))
    elif kind == "bands":   # horizontal sun-shade bands with dark window strips
        rows = max(2, int((h - ph) / 70))
        for r_ in range(rows):
            yy = base - h + m + r_ * (h - ph - 2 * m) / rows
            fill_rect(ctx, x + m, yy + 18, w - 2 * m, (h - ph - 2 * m) / rows - 30, mix(P["shadow"], C["teal_d"], 0.5))
    if pil:
        pilotis(ctx, P, x + 10, base - ph, w - 20, ph, max(3, int(w / 90)), col)
    if roof:
        folded_roof(ctx, P, x - 20, base - h, w + 40, max(3, int(w / 110)), 40, col, seed + 30)


def sugar_palm(ctx, P, x, y, h, seed=0, col=None):
    PP.palm(ctx, P, x, y, h, "sugar", seed, col or mix(C["palm"], P["near"], 0.35))


def kh_flag(ctx, x, y, w, t=0.0, pole=True):
    """Kingdom of Cambodia flag (1948-1970): blue / red (double) / blue with white Angkor Wat."""
    h = w * 0.64
    if pole:
        fill_rect(ctx, x - 4, y - h * 1.2, 8, h * 2.6, "#e8e0cc")
    for a, b, c in ((0, 0.25, "#2f4f8a"), (0.25, 0.75, "#c8423a"), (0.75, 1.0, "#2f4f8a")):
        sw = math.sin(t * 2.4 + a * 5) * w * 0.02
        poly(ctx, [(x, y - h + h * a + sw), (x + w, y - h + h * a - sw), (x + w, y - h + h * b - sw), (x, y - h + h * b + sw)])
        src(ctx, c)
        ctx.fill()
    cx, cy = x + w * 0.5, y - h * 0.5
    src(ctx, "#f4efe4")
    for dx, th in ((-w * 0.13, h * 0.12), (-w * 0.065, h * 0.16), (0, h * 0.22), (w * 0.065, h * 0.16), (w * 0.13, h * 0.12)):
        poly(ctx, [(cx + dx - w * 0.025, cy + h * 0.12), (cx + dx, cy - th), (cx + dx + w * 0.025, cy + h * 0.12)])
        ctx.fill()
    ctx.rectangle(cx - w * 0.17, cy + h * 0.1, w * 0.34, h * 0.05)
    ctx.fill()


def kr_flag(ctx, x, y, w, t=0.0, pole=True):
    """Khmer Republic flag (from Oct 1970): blue with a red canton showing Angkor Wat, three white stars."""
    h = w * 0.64
    if pole:
        fill_rect(ctx, x - 4, y - h * 1.2, 8, h * 2.6, "#d8d4c8")
    sw = math.sin(t * 2.4) * w * 0.02
    poly(ctx, [(x, y - h + sw), (x + w, y - h - sw), (x + w, y - sw), (x, y + sw)])
    src(ctx, "#2f4f8a")
    ctx.fill()
    poly(ctx, [(x, y - h + sw), (x + w * 0.45, y - h), (x + w * 0.45, y - h * 0.5), (x, y - h * 0.5 + sw)])
    src(ctx, "#c8423a")
    ctx.fill()
    src(ctx, "#f4efe4")
    cx, cy = x + w * 0.225, y - h * 0.72
    for dx, th in ((-w * 0.06, h * 0.08), (0, h * 0.13), (w * 0.06, h * 0.08)):
        poly(ctx, [(cx + dx - w * 0.02, cy + h * 0.08), (cx + dx, cy - th), (cx + dx + w * 0.02, cy + h * 0.08)])
        ctx.fill()
    for k in range(3):
        sx, sy = x + w * (0.62 + 0.13 * k), y - h * (0.82 - 0.06 * (k % 2))
        _star(ctx, sx, sy, w * 0.035)


def _star(ctx, x, y, r):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    poly(ctx, pts)
    ctx.fill()


def independence_monument(ctx, P, x, y, s, seed=0, col=None):
    """Independence Monument (Vann Molyvann, built 1958-62): lotus-shaped tower of receding tiers of naga heads
    on a stepped base.  Simplified flat rendering."""
    red = col or mix("#b8604a", P["mid"], 0.1)
    for k in range(3):
        w = s * (1.0 - k * 0.2)
        yy = y - k * s * 0.12
        rect(ctx, x - w, yy - s * 0.12, 2 * w, s * 0.12, mix(red, P["light"], 0.05 * k), 0.7, seed + k)
    by = y - s * 0.36
    for k in range(7):
        w = s * (0.42 - k * 0.048)
        yy = by - k * s * 0.3
        sheet(ctx, path_poly([(x - w, yy), (x + w, yy), (x + w * 0.86, yy - s * 0.3), (x - w * 0.86, yy - s * 0.3)]),
              mix(red, P["light"], 0.03 * k), shadow=0.6, seed=seed + 5 + k)
        src(ctx, mix(red, P["shadow"], 0.35))
        for j in range(5):   # naga heads as a row of small fans
            hx = x - w * 0.8 + j * w * 0.4
            poly(ctx, [(hx - s * 0.03, yy - s * 0.02), (hx, yy - s * 0.1), (hx + s * 0.03, yy - s * 0.02)])
            ctx.fill()
        src(ctx, mix(red, "#000000", 0.25))
        for sg in (-1, 1):   # corner naga horns
            poly(ctx, [(x + sg * w, yy), (x + sg * w * 1.18, yy - s * 0.13), (x + sg * w * 0.94, yy - s * 0.07)])
            ctx.fill()
    top = by - 7 * s * 0.3
    sheet(ctx, path_poly([(x - s * 0.08, top), (x + s * 0.08, top), (x, top - s * 0.32)]),
          mix(red, P["light"], 0.2), shadow=0.3, seed=seed + 20)


# ---------------------------------------------------------------- vehicles (drawn per frame)
def cyclo(ctx, P, x, y, s, t, f=1, seed=0):
    """Phnom Penh cyclo: passenger seat in front, rider pedalling behind."""
    wc = "#1e1f24"
    for wx, r in ((x + 0.45 * s * f, 0.2 * s), (x + 0.05 * s * f, 0.2 * s), (x - 0.6 * s * f, 0.22 * s)):
        src(ctx, wc)
        ctx.new_path()
        ctx.arc(wx, y - r, r, 0, 6.283)
        ctx.set_line_width(s * 0.03)
        ctx.stroke()
        for k in range(4):
            a = t * 6 * f + k * math.pi / 4
            ctx.move_to(wx - math.cos(a) * r, y - r - math.sin(a) * r)
            ctx.line_to(wx + math.cos(a) * r, y - r + math.sin(a) * r)
        ctx.set_line_width(s * 0.008)
        ctx.stroke()
    src(ctx, wc)
    ctx.set_line_width(s * 0.035)
    ctx.move_to(x + 0.25 * s * f, y - 0.35 * s)
    ctx.line_to(x - 0.6 * s * f, y - 0.22 * s)
    ctx.line_to(x - 0.42 * s * f, y - 0.78 * s)
    ctx.stroke()
    # passenger seat + canopy
    sheet(ctx, path_poly([(x - 0.05 * s * f, y - 0.36 * s), (x + 0.6 * s * f, y - 0.36 * s), (x + 0.55 * s * f, y - 0.55 * s),
                          (x + 0.02 * s * f, y - 0.62 * s)]), C["coral"], shadow=0.3, seed=seed)
    sheet(ctx, path_poly([(x - 0.1 * s * f, y - 0.95 * s), (x + 0.5 * s * f, y - 0.95 * s), (x + 0.55 * s * f, y - 0.85 * s),
                          (x - 0.12 * s * f, y - 0.62 * s)]), C["teal"], shadow=0.2, seed=seed + 1)
    cast.draw(ctx, x - 0.5 * s * f, y - 0.15 * s, s * 1.25, "cyclo_man", "cyclo", t + seed, 90 * f, None, P, seed=seed,
              cutout=False)


def vespa(ctx, P, x, y, s, t, f=1, col=None, seed=0, rider="pp_man2"):
    col = col or C["teal"]
    cast.draw(ctx, x - 0.05 * s * f, y - 0.3 * s, s * 1.15, rider, "sit", t + seed, 90 * f, None, P, seed=seed,
              cutout=False)
    for wx in (x - 0.32 * s * f, x + 0.38 * s * f):
        src(ctx, "#1e1f24")
        ctx.new_path()
        ctx.arc(wx, y - 0.11 * s, 0.11 * s, 0, 6.283)
        ctx.fill()
    sheet(ctx, path_poly([(x - 0.48 * s * f, y - 0.14 * s), (x - 0.42 * s * f, y - 0.38 * s), (x - 0.05 * s * f, y - 0.42 * s),
                          (x + 0.05 * s * f, y - 0.2 * s), (x + 0.3 * s * f, y - 0.2 * s), (x + 0.42 * s * f, y - 0.72 * s),
                          (x + 0.5 * s * f, y - 0.7 * s), (x + 0.45 * s * f, y - 0.14 * s)], True), col, shadow=0.3, seed=seed)
    fill_rect(ctx, x + (0.36 if f > 0 else -0.56) * s, y - 0.78 * s, 0.2 * s, 0.03 * s, "#c9c9c4")


def car(ctx, P, x, y, s, t, f=1, col=None, seed=0):
    """Rounded 1960s saloon."""
    col = col or C["mustard"]
    body = [(x - 0.9 * s * f, y - 0.12 * s), (x - 0.92 * s * f, y - 0.34 * s), (x - 0.5 * s * f, y - 0.42 * s),
            (x - 0.3 * s * f, y - 0.66 * s), (x + 0.3 * s * f, y - 0.66 * s), (x + 0.52 * s * f, y - 0.42 * s),
            (x + 0.92 * s * f, y - 0.36 * s), (x + 0.92 * s * f, y - 0.12 * s)]
    sheet(ctx, path_poly(body, True), col, shadow=0.5, seed=seed)
    src(ctx, mix(P["sky0"], "#ffffff", 0.3), 0.9)
    poly(ctx, [(x - 0.42 * s * f, y - 0.43 * s), (x - 0.26 * s * f, y - 0.6 * s), (x + 0.26 * s * f, y - 0.6 * s),
               (x + 0.44 * s * f, y - 0.43 * s)])
    ctx.fill()
    fill_rect(ctx, x - 0.9 * s, y - 0.2 * s, 1.84 * s, 0.03 * s, "#e8e4da")
    for wx in (x - 0.55 * s, x + 0.55 * s):
        src(ctx, "#1e1f24")
        ctx.new_path()
        ctx.arc(wx, y - 0.12 * s, 0.15 * s, 0, 6.283)
        ctx.fill()
        src(ctx, "#c9c9c4")
        ctx.new_path()
        ctx.arc(wx, y - 0.12 * s, 0.06 * s, 0, 6.283)
        ctx.fill()


def traffic_dyn(P, n=5, y=1215, depth=0.85, seed=0, cars=True, speed=1.0):
    R = rng(seed)
    items = []
    kinds = ["cyclo", "vespa", "car", "cyclo", "vespa", "car", "vespa"]
    for i in range(n):
        f = 1 if i % 2 == 0 else -1
        items.append(dict(k=kinds[i % len(kinds)] if cars else ["cyclo", "vespa"][i % 2], f=f,
                          x0=R.random() * SW * 1.4 - SW * 0.2, v=(70 + R.random() * 60) * speed * f,
                          y=y + (0 if f > 0 else 70), col=[C["teal"], C["coral"], C["mustard"], C["cream"]][i % 4]))

    def dyn(ctx, t, d, dp):
        if dp != depth:
            return
        for it in sorted(items, key=lambda q: q["y"]):
            x = (it["x0"] + it["v"] * t + SW * 0.3) % (SW * 1.6) - SW * 0.3
            if it["k"] == "cyclo":
                cyclo(ctx, P, x, it["y"], 230, t, it["f"], seed=int(it["x0"]) % 97)
            elif it["k"] == "vespa":
                vespa(ctx, P, x, it["y"], 200, t, it["f"], it["col"], seed=int(it["x0"]) % 89)
            else:
                car(ctx, P, x, it["y"], 230, t, it["f"], it["col"], seed=int(it["x0"]) % 83)
    return dyn


# ================================================================ 1. BOULEVARD (opening, ch.1, ch.5, closing)
def make_boulevard(tod="sunset", monument=True, traffic=6, people=None, mouth_fn=None, flags=False):
    P = _P(tod)

    def sky_(ctx):
        sky60(ctx, P, 0.62, (0.78, 0.44), 95, 600, 3)

    def far(ctx):
        # distant skyline: blocks + monument
        R = rng(601)
        x = -40
        while x < SW:
            w = 140 + R.random() * 200
            h = 160 + R.random() * 220
            rect(ctx, x, 900 - h, w, h, mix(P["far"], P["haze"], 0.3 + 0.3 * R.random()), 0.2, 602)
            x += w + 20
        if monument:
            independence_monument(ctx, P, 1700, 905, 190, 610, mix(P["far"], C["coral_d"], 0.35))

    def mid(ctx):
        sheet(ctx, path_poly([(-30, 940), (SW + 30, 940), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix(C["conc_d"], P["shadow"], 0.12), shadow=0.2, seed=620)
        nk_building(ctx, P, 60, 1000, 560, 420, "louvre", mix(C["cream"], P["haze"], 0.15), 621)
        nk_building(ctx, P, 700, 1000, 420, 300, "breeze", mix(C["teal_l"], P["haze"], 0.2), 622)
        nk_building(ctx, P, 1200, 1000, 380, 380, "diag", mix(C["mustard"], P["haze"], 0.25), 623)
        nk_building(ctx, P, 1700, 1000, 620, 260, "bands", mix(C["cream"], P["haze"], 0.1), 624)
        for i, x in enumerate((660, 1150, 1640, 2340)):
            sugar_palm(ctx, P, x, 1010, 360, 630 + i)
        if flags:
            for i, x in enumerate((300, 900, 1500, 2100)):
                kh_flag(ctx, x, 880, 90, 0.0)

    def street(ctx):
        sheet(ctx, path_poly([(-30, 1060), (SW + 30, 1060), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix(C["char_l"], P["shadow"], 0.2), shadow=0.2, seed=640)
        fill_rect(ctx, -30, 1040, SW + 60, 26, mix(C["cream_d"], P["shadow"], 0.1))
        for k in range(14):
            fill_rect(ctx, k * 190, 1250, 100, 10, mix(C["cream"], P["shadow"], 0.2))

    layers = [(_key("bv_sky", tod=tod), sky_, 0.0), (_key("bv_far", tod=tod, m=monument), far, 0.25),
              (_key("bv_mid", tod=tod, fl=flags), mid, 0.55), (_key("bv_st", tod=tod), street, 0.85)]
    return dict(layers=layers, dyn=_comb(traffic_dyn(P, traffic, seed=7) if traffic else None,
                                         people_dyn(people or [], P, mouth_fn)),
                dyn_depths=[0.55, 0.85])


# ================================================================ 2. SOPHEA'S ROOM (guide scenes, closing)
def make_room(tod="day", people=None, mouth_fn=None, variant="desk", sat=1.0):
    """A student's room, Phnom Penh: louvred window onto the city, desk with diary, camera and a transistor radio."""
    P = _P(tod)
    wall = mix(C["teal_l"], P["light"], 0.15) if tod in ("day", "golden") else mix(C["teal_d"], P["shadow"], 0.4)

    def room(ctx):
        fill_rect(ctx, 0, 0, SW, SH, wall)
        # window with view
        wx, wy, ww, wh = 1300, 200, 820, 600
        ctx.save()
        ctx.rectangle(wx, wy, ww, wh)
        ctx.clip()
        ctx.set_source(lin(0, wy, 0, wy + wh, [(0, P["sky0"]), (1, P["sky1"])]))
        ctx.paint()
        independence_monument(ctx, P, wx + ww * 0.62, wy + wh - 40, 110, 700, mix(P["far"], C["coral_d"], 0.3))
        R = rng(701)
        for k in range(7):
            bx = wx + k * 130 - 30
            bh = 120 + R.random() * 160
            fill_rect(ctx, bx, wy + wh - bh, 110, bh, mix(P["far"], P["haze"], 0.4 + 0.2 * R.random()))
        ctx.restore()
        for k in range(9):   # window louvres (half open)
            fill_rect(ctx, wx, wy + k * wh / 9, ww, 16, mix(C["cream"], P["shadow"], 0.15), 0.9)
        rect(ctx, wx - 24, wy - 24, ww + 48, 24, C["cream"], 0.4, 702)
        rect(ctx, wx - 24, wy + wh, ww + 48, 30, C["cream"], 0.6, 703)
        rect(ctx, wx - 24, wy, 24, wh, C["cream"], 0.3, 704)
        rect(ctx, wx + ww, wy, 24, wh, C["cream"], 0.3, 705)
        # poster (movie-poster style, abstract) and a calendar
        rect(ctx, 260, 180, 320, 450, C["mustard"], 0.7, 706)
        src(ctx, C["coral"])
        ctx.new_path()
        ctx.arc(420, 340, 110, 0, 6.283)
        ctx.fill()
        rect(ctx, 300, 500, 240, 26, C["char"], 0.0, 707)
        rect(ctx, 300, 545, 180, 16, C["char"], 0.0, 708)
        rect(ctx, 700, 260, 230, 300, C["cream"], 0.6, 709)
        rect(ctx, 700, 260, 230, 60, C["coral"], 0.0, 710)
        src(ctx, mix(C["char"], C["cream"], 0.4))
        for r_ in range(4):
            for c_ in range(5):
                ctx.rectangle(718 + c_ * 42, 340 + r_ * 52, 28, 28)
        ctx.fill()
        # floor
        fill_rect(ctx, 0, 1000, SW, SH - 1000, mix(C["mustard_d"], P["shadow"], 0.25))
        for k in range(12):
            fill_rect(ctx, 0, 1000 + k * 30, SW, 3, mix(C["mustard_d"], P["shadow"], 0.4), 0.5)

    def desk(ctx):
        # teak desk with tapered legs
        rect(ctx, 520, 860, 1100, 40, mix("#8a5a34", P["shadow"], 0.1), 0.8, 720)
        for lx, sg in ((560, -1), (1580, 1)):
            sheet(ctx, path_poly([(lx, 900), (lx + 26, 900), (lx + 26 + sg * 20, 1180), (lx + sg * 20, 1180)]),
                  mix("#6a4428", P["shadow"], 0.1), shadow=0.4, seed=721)
        # radio
        rrect(ctx, 1320, 730, 230, 130, 18)
        src(ctx, C["coral"])
        ctx.fill()
        breeze(ctx, P, 1340, 750, 120, 90, mix(C["cream"], C["coral"], 0.3), 18)
        src(ctx, C["cream"])
        ctx.new_path()
        ctx.arc(1505, 795, 26, 0, 6.283)
        ctx.fill()
        # lamp
        fill_rect(ctx, 640, 640, 8, 220, C["char"])
        sheet(ctx, path_poly([(590, 650), (700, 650), (670, 580), (620, 580)]), C["mustard"], shadow=0.4, seed=722)
        # diary + camera on desk
        sheet(ctx, path_poly([(860, 860), (1160, 860), (1140, 836), (880, 836)]), "#f6eedc", shadow=0.3, seed=723)
        sheet(ctx, path_poly([(860, 862), (1160, 862), (1160, 870), (860, 870)]), C["red"], shadow=0.0, seed=724)
        rrect(ctx, 1200, 800, 90, 58, 6)
        src(ctx, C["char"])
        ctx.fill()
        fill_rect(ctx, 1200, 800, 90, 14, "#c9c9c4")
        src(ctx, "#111111")
        ctx.new_path()
        ctx.arc(1245, 834, 18, 0, 6.283)
        ctx.fill()
        # chair back
        sheet(ctx, path_poly([(980, 1180), (1000, 900), (1030, 900), (1012, 1180)]), "#6a4428", shadow=0.4, seed=725)

    layers = [(_key("rm_room", tod=tod), room, 0.3), (_key("rm_desk", tod=tod), desk, 0.7)]

    def fx(ctx, t, d, dp):
        if dp == 0.7:
            glow(ctx, 645, 690, 300, "#ffe2a0", 0.25 if tod in ("night", "dusk", "lamp") else 0.08)
            # radio dial glow + sound waves
            for k in range(3):
                r = 30 + ((t * 40 + k * 30) % 90)
                src(ctx, C["cream"], 0.25 * (1 - r / 120))
                ctx.new_path()
                ctx.arc(1560, 760, r, -0.9, 0.2)
                ctx.set_line_width(3)
                ctx.stroke()
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.3, 0.7])


# ================================================================ 3. CAMPUS (Institute of Technology / university)
def make_campus(tod="day", people=None, mouth_fn=None):
    P = _P(tod)

    def sky_(ctx):
        sky60(ctx, P, 0.6, (0.2, 0.3), 80, 740, 3)

    def bld(ctx):
        sheet(ctx, path_poly([(-30, 980), (SW + 30, 980), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix(C["palm"], P["mid"], 0.4), shadow=0.2, seed=741)
        # long raised teaching block with diagonal louvres and stair tower
        nk_building(ctx, P, 160, 1000, 1500, 430, "diag", C["cream"], 742)
        rect(ctx, 1680, 480, 260, 520, C["coral"], 0.9, 743)
        breeze(ctx, P, 1705, 520, 210, 420, mix(C["coral"], "#ffffff", 0.35), 34)
        # hyperbolic lecture hall roof (as at the Institute of Foreign Languages) - simplified saddle
        sheet(ctx, path_poly([(1960, 1000), (1960, 640), (2140, 720), (2330, 600), (2330, 1000)]), C["teal"],
              shadow=0.9, seed=744)
        for i, x in enumerate((90, 1630, 2380)):
            sugar_palm(ctx, P, x, 1010, 420, 745 + i)
        # path
        sheet(ctx, path_poly([(900, SH + 30), (1500, SH + 30), (1300, 1000), (1100, 1000)]), C["cream_d"], shadow=0.1,
              seed=749)

    layers = [(_key("cp_sky", tod=tod), sky_, 0.0), (_key("cp_bld", tod=tod), bld, 0.55)]
    return dict(layers=layers, dyn=people_dyn(people or [], P, mouth_fn), dyn_depths=[0.55])


# ================================================================ 4. CHAKTOMUK CONFERENCE HALL (1961)
def make_chaktomuk(tod="golden", people=None, mouth_fn=None):
    P = _P(tod)

    def sky_(ctx):
        sky60(ctx, P, 0.56, (0.3, 0.32), 85, 760, 2)
        PP.water(ctx, P, 940, SH + 40, 761, mix(C["teal"], P["water"], 0.4), 4)

    def hall(ctx):
        # riverside terrace
        rect(ctx, 400, 960, 1600, 50, C["conc_d"], 0.6, 762)
        # fan-shaped hall: radiating folded-plate roof blades rising to the river
        cx, cy = 1200, 990
        for k in range(13):
            a0 = math.pi + k * math.pi / 13
            a1 = a0 + math.pi / 13
            r0, r1 = 520, 520
            col = mix(C["cream"], P["shadow"], 0.18 if k % 2 else 0.0)
            sheet(ctx, path_poly([(cx, cy - 60), (cx + math.cos(a0) * r0, cy + math.sin(a0) * r0 * 0.52),
                                  (cx + math.cos(a1) * r1, cy + math.sin(a1) * r1 * 0.52)]), col, shadow=0.5, seed=763 + k)
        # glazed fan wall + pilotis
        sheet(ctx, path_poly([(700, 990), (1700, 990), (1640, 900), (760, 900)]),
              mix(C["teal_d"], P["shadow"], 0.3), shadow=0.5, seed=780)
        for k in range(12):
            fill_rect(ctx, 760 + k * 78, 900, 10, 90, C["cream"])
        sugar_palm(ctx, P, 380, 980, 380, 781)
        sugar_palm(ctx, P, 2050, 980, 340, 782)

    layers = [(_key("ck_sky", tod=tod), sky_, 0.0), (_key("ck_hall", tod=tod), hall, 0.5)]

    def fx(ctx, t, d, dp):
        if dp == 0.0:
            PP.water_fx(ctx, t, P, 1010, SH, 762, 18, 40)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.5])


# ================================================================ 5. NATIONAL SPORTS COMPLEX (1964)
def make_stadium(tod="day", people=None, mouth_fn=None, crowd=True, podium=False, flags=True):
    P = _P(tod)

    def sky_(ctx):
        sky60(ctx, P, 0.5, (0.7, 0.24), 70, 800, 3)

    def bowl(ctx):
        # sweeping earthwork bowl seen from inside: tiers of seating
        for k in range(9):
            y0 = 520 + k * 52
            col = mix(C["conc"], P["shadow"], 0.05 + 0.03 * (k % 2))
            sheet(ctx, path_poly([(-30, y0), (SW * 0.5, y0 - 40 + k * 4), (SW + 30, y0), (SW + 30, y0 + 52), (-30, y0 + 52)]),
                  col, shadow=0.15, seed=801 + k, edge=False)
        # cantilevered roof blade
        sheet(ctx, path_poly([(1500, 470), (2430, 380), (2430, 420), (1500, 500)]), C["cream"], shadow=0.8, seed=812)
        for k in range(6):
            fill_rect(ctx, 1560 + k * 150, 490 - k * 14, 10, 80, C["conc_d"])
        # field + track
        sheet(ctx, path_poly([(-30, 990), (SW + 30, 990), (SW + 30, SH + 30), (-30, SH + 30)]), C["coral_d"], shadow=0.2,
              seed=813)
        sheet(ctx, path_poly([(-30, 1060), (SW + 30, 1060), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix(C["palm"], P["mid"], 0.3), shadow=0.2, seed=814)
        for k in range(5):
            fill_rect(ctx, -30, 1000 + k * 12, SW + 60, 2, C["cream"], 0.7)
        if podium:
            rect(ctx, 1080, 900, 240, 90, C["cream"], 0.7, 815)
            fill_rect(ctx, 1080, 900, 240, 18, C["coral"])
            fill_rect(ctx, 1196, 840, 6, 60, C["char"])
        if flags:
            for i in range(9):
                kh_flag(ctx, 200 + i * 250, 470, 60, i * 0.7)

    layers = [(_key("st_sky", tod=tod), sky_, 0.0), (_key("st_bowl", tod=tod, p=podium, f=flags), bowl, 0.5)]
    R = rng(820)
    dots = [(R.random() * SW, 540 + R.random() * 430, R.integers(0, 4)) for _ in range(1400)] if crowd else []

    def fx(ctx, t, d, dp):
        if dp != 0.5:
            return
        cols = [C["cream"], C["coral"], C["teal"], C["mustard"]]
        for i, (x, y, c) in enumerate(dots):   # crowd, with occasional waves
            bob = 3 * math.sin(t * 3 + x * 0.01) if (i % 3 == 0) else 0
            src(ctx, cols[c], 0.9)
            ctx.rectangle(x, y + bob, 7, 9)
            ctx.fill()
            src(ctx, "#2a2018", 0.9)
            ctx.rectangle(x + 1, y - 5 + bob, 5, 5)
            ctx.fill()
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.5])


# ================================================================ 6. PORT (Sihanoukville, opened 1960) + ROAD/RAIL
def _freighter(ctx, P, x, y, L, seed=0, col=None):
    col = col or C["char_l"]
    sheet(ctx, path_poly([(x - L / 2, y - L * 0.1), (x + L / 2 + L * 0.04, y - L * 0.12), (x + L * 0.45, y),
                          (x - L * 0.46, y)]), col, shadow=0.6, seed=seed)
    fill_rect(ctx, x - L / 2, y - L * 0.04, L, L * 0.012, C["coral"])
    rect(ctx, x + L * 0.18, y - L * 0.24, L * 0.2, L * 0.13, C["cream"], 0.5, seed + 1)
    fill_rect(ctx, x + L * 0.2, y - L * 0.2, L * 0.16, L * 0.025, C["teal_d"])
    rect(ctx, x + L * 0.25, y - L * 0.34, L * 0.05, L * 0.1, C["mustard"], 0.3, seed + 2)
    for k in range(3):
        fill_rect(ctx, x - L * 0.38 + k * L * 0.16, y - L * 0.26, L * 0.008, L * 0.15, C["char"])


def _crane(ctx, P, x, y, h, col):
    src(ctx, col)
    ctx.set_line_width(10)
    ctx.move_to(x - 40, y)
    ctx.line_to(x, y - h)
    ctx.line_to(x + 40, y)
    ctx.move_to(x, y - h)
    ctx.line_to(x + h * 0.7, y - h * 0.9)
    ctx.stroke()
    ctx.set_line_width(3)
    for k in range(6):
        ctx.move_to(x - 40 + k * 7, y - k * h / 6)
        ctx.line_to(x + 40 - (k + 1) * 7, y - (k + 1) * h / 6)
    ctx.stroke()


def make_port60(tod="day", people=None, mouth_fn=None):
    P = _P(tod)

    def sky_(ctx):
        sky60(ctx, P, 0.55, (0.2, 0.28), 80, 840, 3)
        PP.ridge(ctx, P, 760, 120, mix(P["far"], P["haze"], 0.3), 841, peaks=[(300, 80, 250)])
        PP.water(ctx, P, 800, SH + 40, 842, mix(C["teal"], P["water"], 0.5), 4)

    def quay(ctx):
        _freighter(ctx, P, 1500, 900, 900, 843)
        for i, x in enumerate((420, 760, 2160)):
            _crane(ctx, P, x, 980, 420, [C["coral"], C["mustard"], C["coral"]][i])
        rect(ctx, -30, 980, SW + 60, 60, C["conc"], 0.6, 845)
        for k in range(4):   # warehouses
            nk_building(ctx, P, 60 + k * 300, 1240, 260, 200, "bands", [C["cream"], C["teal_l"]][k % 2], 846 + k,
                        roof=True, pil=False)
        sheet(ctx, path_poly([(-30, 1040), (SW + 30, 1040), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix(C["conc_d"], P["shadow"], 0.1), shadow=0.2, seed=850)
        R = rng(851)
        for k in range(40):   # sacks / crates on the quay
            x = 1300 + R.random() * 1000
            y = 1080 + R.random() * 140
            sheet(ctx, path_ellipse(x, y, 30, 18), mix(C["cream_d"], C["mustard"], R.random() * 0.5), shadow=0.3,
                  seed=852 + k)

    layers = [(_key("pt_sky", tod=tod), sky_, 0.0), (_key("pt_quay", tod=tod), quay, 0.55)]

    def fx(ctx, t, d, dp):
        if dp == 0.0:
            PP.water_fx(ctx, t, P, 820, 980, 853, 14, 30)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.55])


def make_road(tod="day", people=None, mouth_fn=None, train=True, trucks=True):
    """Highway and railway across the plain (Friendship Highway 1959; railway to the coast completed 1969)."""
    P = _P(tod)

    def sky_(ctx):
        sky60(ctx, P, 0.58, (0.25, 0.3), 80, 860, 3)
        PP.ridge(ctx, P, 820, 140, mix(P["far"], P["haze"], 0.35), 861, peaks=[(1700, 120, 300)])

    def land(ctx):
        sheet(ctx, path_poly([(-30, 860), (SW + 30, 860), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix(C["mustard"], P["mid"], 0.35), shadow=0.1, seed=862)
        for k in range(8):
            fill_rect(ctx, -30, 880 + k * 18, SW + 60, 6, mix(C["palm"], P["mid"], 0.3), 0.6)
        for i, x in enumerate((200, 600, 1300, 2000, 2250)):
            sugar_palm(ctx, P, x, 900, 260, 863 + i)
        # rail embankment and track
        rect(ctx, -30, 990, SW + 60, 30, C["conc_d"], 0.3, 870)
        for k in range(60):
            fill_rect(ctx, k * 42, 992, 12, 26, "#5a4a3a")
        fill_rect(ctx, -30, 996, SW + 60, 4, "#9a9a9a")
        fill_rect(ctx, -30, 1010, SW + 60, 4, "#9a9a9a")
        # road
        sheet(ctx, path_poly([(-30, 1120), (SW + 30, 1120), (SW + 30, 1290), (-30, 1290)]), C["char_l"], shadow=0.2,
              seed=871)
        for k in range(14):
            fill_rect(ctx, k * 190, 1200, 100, 8, C["cream"])

    layers = [(_key("rd_sky", tod=tod), sky_, 0.0), (_key("rd_land", tod=tod), land, 0.6)]

    def fx(ctx, t, d, dp):
        if dp != 0.6:
            return
        if train:
            x0 = -900 + t * 120
            for k in range(6):
                x = x0 + k * 190
                rect(ctx, x, 920, 180, 74, [C["teal_d"], C["mustard"], C["mustard"], C["coral_d"], C["mustard"], C["mustard"]][k],
                     0.3, 875)
                fill_rect(ctx, x + 10, 935, 160, 18, C["cream"] if k else C["char"], 0.8)
            glow(ctx, x0 + 1150, 940, 30, "#fff0c0", 0.5)
        if trucks:
            for k, (x0, v) in enumerate(((200, 90), (1500, -70))):
                x = (x0 + v * t) % (SW + 600) - 300
                car(ctx, P, x, 1170 + k * 70, 240, t, 1 if v > 0 else -1, [C["coral"], C["teal"]][k], seed=877 + k)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.6])


# ================================================================ 7. CINEMA (archive projection + Khmer film boom)
def make_cinema(image=None, people=None, mouth_fn=None, title=None, still="film"):
    """Old picture palace: a screen inside a proscenium; seated audience heads in silhouette.
    image: archive file shown on the screen (authentic, unaltered); else a drawn 'film still'."""
    P = _P("night")

    def hall(ctx):
        fill_rect(ctx, 0, 0, SW, SH, "#1a1416")
        # curtains
        for sg, x0 in ((-1, 0), (1, SW)):
            for k in range(8):
                xx = x0 - sg * (k * 40)
                fill_rect(ctx, min(xx, xx - sg * 40), 0, 40, SH, mix(C["red"], "#000000", 0.25 + 0.15 * (k % 2)))
        # proscenium in Art-Deco/modern steps
        for k in range(3):
            rrect(ctx, 300 - k * 30, 120 - k * 26, 1800 + k * 60, 900 + k * 52, 12)
            src(ctx, mix(C["mustard_d"], "#000000", 0.2 + 0.2 * k))
            ctx.set_line_width(14)
            ctx.stroke()
        fill_rect(ctx, 330, 150, 1740, 840, "#0e0c0c")

    def seats(ctx):
        R = rng(900)
        for row in range(4):
            for k in range(26):
                x = -20 + k * 98 + (row % 2) * 49 + R.random() * 10
                y = 1150 + row * 70
                src(ctx, "#060505")
                ctx.new_path()
                ellipse(ctx, x, y, 34, 42)
                ctx.fill()
                ctx.rectangle(x - 48, y + 30, 96, 120)
                ctx.fill()

    layers = [(_key("cn_hall"), hall, 0.3), (_key("cn_seats"), seats, 0.9)]

    def fx(ctx, t, d, dp):
        if dp != 0.3:
            return
        fl = 0.92 + 0.08 * math.sin(t * 37) * math.sin(t * 13)
        ctx.save()
        ctx.rectangle(330, 150, 1740, 840)
        ctx.clip()
        if image:
            import photos
            from core import load_image, paint_cover
            s = load_image(photos._path(image))
            paint_cover(ctx, s, 330, 150, 1740, 840, 1.0 + 0.05 * t / max(d, 1), contain=True)
            src(ctx, "#000000", 0.25)   # monochrome projection feel
            ctx.paint()
        else:   # drawn film still: a couple on a terrace at sunset (generic, not a real film)
            Pg = _P("sunset")
            ctx.set_source(lin(0, 150, 0, 990, [(0, Pg["sky0"]), (1, Pg["sky1"])]))
            ctx.paint()
            src(ctx, Pg["sun"])
            ctx.new_path()
            ctx.arc(1500, 600, 110, 0, 6.283)
            ctx.fill()
            fill_rect(ctx, 330, 800, 1740, 200, mix(Pg["near"], C["teal_d"], 0.3))
            cast.draw(ctx, 1050, 960, 520, "singer", "idle", t, 40, "smile", Pg, cutout=False)
            cast.draw(ctx, 1300, 960, 560, "musician", "talk", t, -40, "smile", Pg, cutout=False)
        ctx.restore()
        # projector beam
        ctx.set_source(lin(1200, SH, 1200, 400, [(0, "#fff8e0", 0.18 * fl), (1, "#fff8e0", 0.0)]))
        poly(ctx, [(1180, SH), (1220, SH), (2000, 160), (400, 160)])
        ctx.fill()
        src(ctx, "#000000", 1 - fl)
        ctx.rectangle(330, 150, 1740, 840)
        ctx.fill()
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.3, 0.9])


# ================================================================ 8. STAGE (1960s band night) and ROYAL BALLET
def make_stage(tod="night", people=None, mouth_fn=None, variant="band"):
    P = _P("night")

    def hall(ctx):
        fill_rect(ctx, 0, 0, SW, SH, "#1c1820" if variant == "band" else "#241a14")
        if variant == "band":
            # geometric backdrop: starburst + circles
            cx, cy = 1200, 520
            for k in range(24):
                a0 = k * math.pi / 12
                src(ctx, [C["teal_d"], C["coral_d"]][k % 2], 0.8)
                poly(ctx, [(cx, cy), (cx + math.cos(a0) * 1800, cy + math.sin(a0) * 1800),
                           (cx + math.cos(a0 + 0.13) * 1800, cy + math.sin(a0 + 0.13) * 1800)])
                ctx.fill()
            for r_, c_ in ((340, C["mustard"]), (260, C["coral"]), (180, C["cream"])):
                src(ctx, c_, 0.9)
                ctx.new_path()
                ctx.arc(cx, cy, r_, 0, 6.283)
                ctx.fill()
        else:
            # gold-and-red palace-dance backdrop with a stylised tiered roof
            fill_rect(ctx, 0, 0, SW, SH, mix(C["red"], "#000000", 0.45))
            for k in range(4):
                w = 900 - k * 180
                sheet(ctx, path_poly([(1200 - w, 620 - k * 110), (1200 - w * 0.6, 520 - k * 110),
                                      (1200 + w * 0.6, 520 - k * 110), (1200 + w, 620 - k * 110)]),
                      mix(C["mustard"], "#000000", 0.15 * k), shadow=0.5, seed=920 + k)
        # stage floor
        sheet(ctx, path_poly([(-30, 1000), (SW + 30, 1000), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix("#6a4428", "#000000", 0.35), shadow=0.3, seed=930)
        fill_rect(ctx, -30, 1000, SW + 60, 14, C["mustard"])

    def gear(ctx):
        if variant != "band":
            return
        # drum kit + amp + mic stand
        rect(ctx, 1700, 860, 220, 150, C["char"], 0.6, 940)
        breeze(ctx, P, 1715, 875, 190, 120, C["char_l"], 22)
        for x, r_ in ((520, 90), (650, 55), (420, 55)):
            sheet(ctx, path_ellipse(x, 1000 - r_, r_, r_), C["cream"], shadow=0.5, seed=941)
            src(ctx, C["coral"])
            ctx.new_path()
            ctx.arc(x, 1000 - r_, r_ * 0.75, 0, 6.283)
            ctx.fill()

    layers = [(_key("sg_hall", v=variant), hall, 0.3), (_key("sg_gear", v=variant), gear, 0.6)]

    def fx(ctx, t, d, dp):
        if dp != 0.6:
            return
        for k, (x, c_) in enumerate(((600, C["coral"]), (1200, C["mustard"]), (1800, C["teal_l"]))):
            sw = math.sin(t * 0.7 + k * 2) * 200
            ctx.set_source(lin(x, 0, x + sw, 1000, [(0, c_, 0.28), (1, c_, 0.0)]))
            poly(ctx, [(x - 30, 0), (x + 30, 0), (x + sw + 220, 1050), (x + sw - 220, 1050)])
            ctx.fill()
        if variant == "band":
            fill_rect(ctx, 1196, 760, 6, 240, "#c9c9c4")
            src(ctx, "#c9c9c4")
            ctx.new_path()
            ellipse(ctx, 1199, 750, 14, 20)
            ctx.fill()
    return dict(layers=layers, dyn=_comb(people_dyn(people or [], P, mouth_fn), fx), dyn_depths=[0.3, 0.6])


# ================================================================ 9. POLLING STATION (1955 election, reconstruction)
def make_polling(tod="day", people=None, mouth_fn=None):
    P = _P(tod)

    def room(ctx):
        sky60(ctx, P, 0.55, (0.8, 0.3), 70, 960, 2)
        # village school used as polling station: wooden walls, tiled roof
        rect(ctx, 200, 560, 2000, 460, mix("#c89a5a", P["light"], 0.1), 0.8, 961)
        for k in range(20):
            fill_rect(ctx, 200 + k * 100, 560, 4, 460, mix("#8a6a3c", P["shadow"], 0.1), 0.6)
        sheet(ctx, path_poly([(120, 580), (1200, 330), (2280, 580)]), C["coral_d"], shadow=0.8, seed=962)
        for i, x in enumerate((500, 1700)):
            rect(ctx, x, 700, 200, 180, mix(P["shadow"], C["teal_d"], 0.5), 0.2, 963 + i)
        kh_flag(ctx, 1150, 520, 120, 0.0)
        # ground
        sheet(ctx, path_poly([(-30, 1020), (SW + 30, 1020), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix("#c08a5a", P["mid"], 0.2), shadow=0.2, seed=965)
        # table + ballot box
        rect(ctx, 1000, 930, 420, 30, "#6a4428", 0.6, 966)
        fill_rect(ctx, 1020, 960, 14, 120, "#5a3a20")
        fill_rect(ctx, 1386, 960, 14, 120, "#5a3a20")
        rect(ctx, 1130, 820, 160, 110, C["cream"], 0.6, 967)
        fill_rect(ctx, 1175, 820, 70, 8, C["char"])

    layers = [(_key("pl_room", tod=tod), room, 0.5)]
    return dict(layers=layers, dyn=people_dyn(people or [], P, mouth_fn), dyn_depths=[0.5])


# ================================================================ 10. CONFERENCE TABLE (Geneva / Bandung, schematic)
def make_conference(tod="day", people=None, mouth_fn=None, flags=8, banner=None):
    P = _P(tod)

    def room(ctx):
        fill_rect(ctx, 0, 0, SW, SH, mix(C["cream"], P["shadow"], 0.1))
        louvres(ctx, P, 0, 0, SW, 700, 30, C["cream"], mix(C["cream"], "#ffffff", 0.4))
        if banner:
            rect(ctx, 500, 120, 1400, 120, C["teal_d"], 0.6, 980)
            draw_text(ctx, banner, 1200, 180, 60, C["cream"], "mc", font="Futura", weight="Bold")
        R = rng(981)
        for k in range(flags):
            x = 300 + k * (1800 / max(1, flags - 1))
            fill_rect(ctx, x - 3, 380, 6, 360, "#c9c9c4")
            cols = [(C["coral"], C["cream"]), (C["teal"], C["mustard"]), (C["blue"], C["cream"]), (C["mustard"], C["red"])]
            a, b = cols[R.integers(0, 4)]
            fill_rect(ctx, x + 3, 390, 110, 70, a)
            fill_rect(ctx, x + 3, 412, 110, 26, b)
        sheet(ctx, path_poly([(-30, 860), (SW + 30, 860), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix(C["teal_d"], P["shadow"], 0.4), shadow=0.2, seed=982)
        # long table with microphones and name plates
        sheet(ctx, path_poly([(150, 960), (2250, 960), (2350, 1080), (50, 1080)]), C["cream"], shadow=0.8, seed=983)
        fill_rect(ctx, 50, 1080, 2300, 40, mix(C["cream_d"], P["shadow"], 0.2))
        for k in range(10):
            x = 260 + k * 210
            fill_rect(ctx, x, 900, 4, 60, C["char"])
            src(ctx, C["char"])
            ctx.new_path()
            ellipse(ctx, x + 2, 896, 9, 12)
            ctx.fill()
            fill_rect(ctx, x + 30, 936, 90, 24, C["mustard"])

    layers = [(_key("cf_room", tod=tod, f=flags, b=banner), room, 0.5)]
    return dict(layers=layers, dyn=people_dyn(people or [], P, mouth_fn), dyn_depths=[0.5])


# ================================================================ 11. NATIONAL ASSEMBLY (18 March 1970, reconstruction)
def make_assembly(tod="grey", people=None, mouth_fn=None, hands=True):
    P = _P(tod)

    def hall(ctx):
        fill_rect(ctx, 0, 0, SW, SH, mix(C["char"], P["haze"], 0.25))
        louvres(ctx, P, 0, 0, SW, 600, 40, mix(C["char_l"], P["haze"], 0.3), mix(C["conc_d"], P["haze"], 0.3))
        # rostrum
        rect(ctx, 900, 440, 600, 220, mix(C["conc_d"], P["shadow"], 0.2), 0.8, 990)
        fill_rect(ctx, 1150, 380, 100, 60, mix(C["conc"], P["shadow"], 0.3))
        # curved benches
        for row in range(5):
            y = 760 + row * 110
            sheet(ctx, path_poly([(-30, y), (SW / 2, y - 60), (SW + 30, y), (SW + 30, y + 40), (SW / 2, y - 20), (-30, y + 40)]),
                  mix("#6a4428", P["shadow"], 0.3), shadow=0.4, seed=991 + row)

    layers = [(_key("as_hall", tod=tod), hall, 0.4)]
    R = rng(995)
    seats = [(80 + k * 92 + (row % 2) * 46, 735 + row * 110 - 60 * (1 - abs((80 + k * 92) / SW * 2 - 1)), row)
             for row in range(5) for k in range(25)]

    def fx(ctx, t, d, dp):
        if dp != 0.4:
            return
        for i, (x, y, row) in enumerate(seats):
            src(ctx, mix("#141418", P["haze"], 0.1 * row))
            ctx.new_path()
            ellipse(ctx, x, y - 30, 20, 25)
            ctx.fill()
            ctx.rectangle(x - 30, y - 8, 60, 40)
            ctx.fill()
            if hands and (i * 7919) % 31 != 0:   # nearly all hands raised (the record gives 86-3 / 89-0 variants)
                up = smooth((t - 1.0 - (i % 17) * 0.08) / 0.6)
                if up > 0:
                    ctx.set_line_width(9)
                    ctx.move_to(x + 18, y - 10)
                    ctx.line_to(x + 22, y - 10 - 60 * up)
                    ctx.stroke()
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.4])


# ================================================================ 12. VILLAGE (rural Cambodia; Samlaut hills in grey)
def make_village(tod="day", people=None, mouth_fn=None, hills=False, smoke=False):
    P = _P(tod)

    def sky_(ctx):
        sky60(ctx, P, 0.6, (0.3, 0.32), 70, 1000, 2)
        PP.ridge(ctx, P, 780, 200 if hills else 60, mix(P["far"], P["haze"], 0.25), 1001,
                 peaks=[(1700, 180, 260), (600, 120, 300)] if hills else None)

    def fields(ctx):
        sheet(ctx, path_poly([(-30, 800), (SW + 30, 800), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix(C["palm"], P["mid"], 0.4), shadow=0.1, seed=1002)
        for r_ in range(6):   # paddy dykes
            y = 820 + r_ * (60 + r_ * 18)
            fill_rect(ctx, -30, y, SW + 60, 8, mix(C["mustard"], P["mid"], 0.4), 0.8)
        for i, x in enumerate((300, 1500, 1980)):
            PP.stilt_house(ctx, P, x, 980 + i * 20, 130 + i * 10, 1003 + i, mix("#8a6a3c", P["mid"], 0.2),
                           mix("#b08a4a", P["mid"], 0.2))
        for i, x in enumerate((120, 700, 1150, 2300)):
            sugar_palm(ctx, P, x, 990, 380, 1010 + i)

    layers = [(_key("vl_sky", tod=tod, h=hills), sky_, 0.0), (_key("vl_fields", tod=tod), fields, 0.55)]

    def fx(ctx, t, d, dp):
        if dp != 0.0 or not smoke:
            return
        for k in range(14):   # distant smoke columns (no violence shown)
            u = ((t * 0.08 + k / 14) % 1.0)
            for x0 in (1650, 1850):
                src(ctx, P["haze"], 0.35 * (1 - u))
                ctx.new_path()
                ellipse(ctx, x0 + math.sin(u * 4 + k) * 40 + u * 120, 700 - u * 520, 40 + u * 120, 30 + u * 80)
                ctx.fill()
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.55])


# ================================================================ 13. BORDER AT NIGHT (Vietnam War, schematic)
def make_border(tod="night", people=None, mouth_fn=None, flashes=True, heli=True):
    P = _P(tod)

    def sky_(ctx):
        sky60(ctx, P, 0.62, (0.82, 0.2), 40, 1020, 0)
        PP.ridge(ctx, P, 840, 90, mix(P["far"], P["haze"], 0.2), 1021)

    def jungle(ctx):
        R = rng(1022)
        for k in range(46):   # flat tree-line of rounded crowns
            x = R.random() * SW
            y = 900 + R.random() * 60
            r_ = 60 + R.random() * 90
            sheet(ctx, path_ellipse(x, y, r_, r_ * 0.8), mix(P["near"], C["palm_d"], 0.3 + 0.3 * R.random()), shadow=0.3,
                  seed=1023 + k)
        sheet(ctx, path_poly([(-30, 980), (SW + 30, 980), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix(P["near"], "#000000", 0.2), shadow=0.2, seed=1070)

    layers = [(_key("bd_sky", tod=tod), sky_, 0.0), (_key("bd_jungle", tod=tod), jungle, 0.5)]

    def fx(ctx, t, d, dp):
        if dp == 0.0 and flashes:
            for k, (x, per) in enumerate(((600, 3.1), (1300, 4.3), (1900, 2.7))):
                ph = (t + k * 1.3) % per
                if ph < 0.35:
                    glow(ctx, x, 830, 260, "#ffcf8a", 0.5 * (1 - ph / 0.35))
            fy = 300 + (t * 20) % 300   # slow-falling flare
            glow(ctx, 900, fy, 160, "#fff0c8", 0.35)
        if dp == 0.0 and heli:
            for k in range(2):
                x = (-300 + t * 90 + k * 500) % (SW + 600) - 300
                y = 420 + k * 70
                src(ctx, "#0a0c10")
                ctx.new_path()
                ellipse(ctx, x, y, 70, 26)
                ctx.fill()
                ctx.rectangle(x - 150, y - 6, 90, 10)
                ctx.fill()
                ctx.rectangle(x - 120 + 60 * math.sin(t * 40), y - 34, 240 - 120 * abs(math.sin(t * 40)), 4)
                ctx.fill()
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.5])


# ================================================================ 14. AIRPORT (Pochentong; visitors arrive / a departure)
def make_airport(tod="day", people=None, mouth_fn=None, plane=True, depart=False):
    P = _P(tod)

    def sky_(ctx):
        sky60(ctx, P, 0.6, (0.75, 0.3), 80, 1100, 3)

    def apron(ctx):
        nk_building(ctx, P, 120, 900, 900, 240, "louvre", C["cream"], 1101, pil=True)
        fill_rect(ctx, 920, 560, 70, 100, C["teal_d"])   # control-tower cab
        rect(ctx, 930, 660, 50, 240, C["cream"], 0.6, 1102)
        sheet(ctx, path_poly([(-30, 900), (SW + 30, 900), (SW + 30, SH + 30), (-30, SH + 30)]), C["conc_d"], shadow=0.1,
              seed=1103)
        for k in range(12):
            fill_rect(ctx, k * 220, 1150, 120, 10, C["mustard"])

    layers = [(_key("ap_sky", tod=tod), sky_, 0.0), (_key("ap_apron", tod=tod), apron, 0.55)]

    def fx(ctx, t, d, dp):
        if dp != 0.55 or not plane:
            return
        q = ease(clamp((t - 1.0) / max(1.0, d - 2))) if depart else 0.0
        x, y = 1500 + q * 1400, 1060 - q * q * 600
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(-0.12 * q)
        # rear-engined jet airliner silhouette, cream + teal cheat line
        sheet(ctx, path_poly([(-520, -40), (380, -60), (470, -30), (380, 10), (-520, 10), (-560, -20)], True), C["cream"],
              shadow=0.6, seed=1110)
        fill_rect(ctx, -520, -26, 960, 12, C["teal"])
        sheet(ctx, path_poly([(-470, -50), (-560, -220), (-500, -220), (-380, -50)]), C["teal"], shadow=0.3, seed=1111)
        sheet(ctx, path_poly([(-100, 0), (-260, 90), (-180, 90), (40, 0)]), mix(C["cream"], P["shadow"], 0.2), shadow=0.3,
              seed=1112)
        rrect(ctx, -420, -66, 120, 36, 16)
        src(ctx, C["conc_d"])
        ctx.fill()
        src(ctx, C["char"])
        for k in range(14):
            ctx.rectangle(-300 + k * 46, -46, 18, 14)
        ctx.fill()
        ctx.restore()
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.55])


# ================================================================ 15. MARKET / BANK (economy chapter)
def make_market(tod="day", people=None, mouth_fn=None, banner_km=None, banner_en=None):
    P = _P(tod)

    def sky_(ctx):
        sky60(ctx, P, 0.6, (0.2, 0.3), 70, 1120, 2)

    def town(ctx):
        # Art-Deco central market dome (Phsar Thmei, 1937) in the distance
        cx, cy = 1600, 860
        sheet(ctx, path_ellipse(cx, cy, 300, 280), mix(C["mustard"], P["haze"], 0.35), shadow=0.5, seed=1121)
        for k in range(9):
            a = math.pi + k * math.pi / 8
            src(ctx, mix(C["mustard_d"], P["haze"], 0.35))
            ctx.set_line_width(6)
            ctx.move_to(cx, cy - 280)
            ctx.curve_to(cx + math.cos(a) * 200, cy - 200, cx + math.cos(a) * 300, cy - 60, cx + math.cos(a) * 300, cy)
            ctx.stroke()
        rect(ctx, cx - 340, cy, 680, 120, mix(C["cream"], P["haze"], 0.3), 0.5, 1122)
        # bank facade at left
        rect(ctx, 100, 520, 820, 500, C["cream"], 0.9, 1123)
        for k in range(6):
            fill_rect(ctx, 160 + k * 130, 620, 40, 400, mix(C["conc"], P["light"], 0.2))
        rect(ctx, 100, 500, 820, 60, C["teal_d"], 0.6, 1124)
        if banner_km:
            rect(ctx, 160, 560, 700, 70, C["coral"], 0.3, 1125)
            draw_text(ctx, banner_km, 510, 595, 34, C["cream"], "mc", font=KM_SANS, weight="Bold")
        sheet(ctx, path_poly([(-30, 1020), (SW + 30, 1020), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix(C["conc_d"], P["shadow"], 0.1), shadow=0.2, seed=1126)
        R = rng(1127)
        for k in range(6):   # market umbrellas + stalls
            x = 1050 + k * 220
            sheet(ctx, path_poly([(x - 110, 1000), (x, 940), (x + 110, 1000)]), [C["coral"], C["teal"], C["mustard"]][k % 3],
                  shadow=0.4, seed=1128 + k)
            fill_rect(ctx, x - 3, 1000, 6, 90, C["char"])
            rect(ctx, x - 90, 1090, 180, 40, mix(C["cream_d"], P["shadow"], 0.1), 0.3, 1135 + k)

    layers = [(_key("mk_sky", tod=tod), sky_, 0.0), (_key("mk_town", tod=tod, b=banner_km), town, 0.55)]
    return dict(layers=layers, dyn=people_dyn(people or [], P, mouth_fn), dyn_depths=[0.55])


# ================================================================ 16. RIVERFRONT & ROYAL PALACE (1955 abdication)
def make_palace60(tod="golden", people=None, mouth_fn=None, flag=True):
    P = _P(tod)

    def sky_(ctx):
        sky60(ctx, P, 0.55, (0.22, 0.3), 90, 1140, 3)

    def palace(ctx):
        base = mix(C["cream"], P["light"], 0.1)
        rect(ctx, -30, 860, SW + 60, 70, mix(C["mustard"], P["mid"], 0.15), 0.5, 1141)   # crenellated wall
        for k in range(40):
            fill_rect(ctx, k * 62, 840, 30, 22, mix(C["mustard"], P["mid"], 0.15))
        rect(ctx, 700, 640, 1000, 290, base, 0.9, 1142)
        for k in range(9):
            fill_rect(ctx, 740 + k * 115, 660, 24, 270, mix(base, P["shadow"], 0.2))
        for k in range(3):   # tiered roofs, mustard and teal tiles
            w = 600 - k * 140
            yy = 640 - k * 85
            sheet(ctx, path_poly([(1200 - w, yy), (1200 - w * 0.6, yy - 100), (1200 + w * 0.6, yy - 100), (1200 + w, yy)]),
                  [C["mustard"], C["teal"], C["mustard_d"]][k], shadow=0.8, seed=1143 + k)
        for k in range(5):
            w = 100 - k * 15
            yy = 385 - k * 50
            sheet(ctx, path_poly([(1200 - w, yy), (1200 + w, yy), (1200 + w * 0.78, yy - 50), (1200 - w * 0.78, yy - 50)]),
                  mix(C["mustard"], P["light"], 0.06 * k), shadow=0.4, seed=1150 + k)
        sheet(ctx, path_poly([(1190, 140), (1210, 140), (1200, 60)]), C["mustard"], shadow=0.2, seed=1156)
        sheet(ctx, path_poly([(-30, 930), (SW + 30, 930), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix(C["palm"], P["mid"], 0.3), shadow=0.2, seed=1157)
        for i, x in enumerate((240, 2160)):
            sugar_palm(ctx, P, x, 960, 420, 1158 + i)
        if flag:
            kh_flag(ctx, 1950, 860, 110, 0.0)

    layers = [(_key("pa_sky", tod=tod), sky_, 0.0), (_key("pa_pal", tod=tod, f=flag), palace, 0.55)]
    return dict(layers=layers, dyn=people_dyn(people or [], P, mouth_fn), dyn_depths=[0.55])


# ================================================================ 17. MONUMENT PLAZA (ch.5 and closing)
def make_monument60(tod="golden", people=None, mouth_fn=None, building=False):
    P = _P(tod)

    def sky_(ctx):
        sky60(ctx, P, 0.62, (0.8, 0.42), 90, 1160, 3)

    def plaza(ctx):
        sheet(ctx, path_poly([(-30, 1000), (SW + 30, 1000), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix(C["conc_d"], P["shadow"], 0.1), shadow=0.2, seed=1161)
        sheet(ctx, path_poly([(-30, 1060), (SW + 30, 1060), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix(C["palm"], P["mid"], 0.3), shadow=0.2, seed=1162)
        if building:   # scaffold during construction (1958-62)
            src(ctx, mix("#8a6a3c", P["shadow"], 0.1))
            ctx.set_line_width(6)
            for k in range(9):
                x = 960 + k * 60
                ctx.move_to(x, 1005)
                ctx.line_to(x, 380)
            for k in range(12):
                y = 1000 - k * 52
                ctx.move_to(950, y)
                ctx.line_to(1450, y)
            ctx.stroke()
        independence_monument(ctx, P, 1200, 1005, 300 if not building else 300, 1170)
        if building:
            fill_rect(ctx, 960, 200, 500, 400, mix(P["sky0"], P["sky1"], 0.5))   # unfinished top hidden by sky band
        for i, x in enumerate((220, 520, 1880, 2180)):
            sugar_palm(ctx, P, x, 1010, 360, 1180 + i)

    layers = [(_key("mo_sky", tod=tod), sky_, 0.0), (_key("mo_plaza", tod=tod, b=building), plaza, 0.55)]

    def fx(ctx, t, d, dp):
        if dp == 0.55:
            glow(ctx, 1200, 600, 600, P["sun"], 0.12 + 0.03 * math.sin(t * 1.5))
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.55])


def sophea(x, y, h, pose="ask", yaw=30, **kw):
    """The fictional guide, talking (mouth from her voice)."""
    return F(x, y, h, "sophea", pose, yaw, 11, talk=True, expr=kw.pop("expr", "smile"), **kw)
