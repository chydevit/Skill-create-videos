"""Sets for 'Democratic Kampuchea 1975-1979: We Remember'.  Drawn flat, then turned into pencil and charcoal by
memory.inkify (grey for memory, warm colour for the present day).  Every scene is a reconstruction or a symbol.
No violence is ever depicted: absence stands for loss (empty shoes, abandoned books, silent rooms, a candle).

make_memorial   present day: a memorial stupa at dawn, lotus pond, incense smoke (Yeay Sophal and Malis)
make_altar      present day: a small altar table: a drawn family portrait (fictional), lotus, incense, a candle
make_exodus     memory: the road out of the city, April 1975 (crowds walk; carts, bundles)
make_still      memory: still life close-ups (shoes, glasses, bowl, banknotes, books, gate)
make_classroom  memory/symbol: an empty classroom (books on the floor) or a barred, empty room (S-21, symbolic)
make_fields     memory: cooperative rice fields; dam=True: an earthen dam with lines of workers carrying baskets
make_hall       memory: a communal dining hall: long tables, tin bowls
"""
import math

import paper as PP
from core import SH, SW, clamp, ease, ellipse, glow, mix, poly, rng, src, spline
from paper import TOD, sheet, path_poly
from sets import _key, _comb, people_dyn
from sets60 import rect, fill_rect, sky60, sugar_palm
from memory import GOLD_PAINT, candle

V = "75v1"
TOD.setdefault("mist", dict(sky0="#9aa2a6", sky1="#e2dccd", sun="#f6eedc", water="#8a9898", far="#b4b8b2",
                            mid="#8a948a", near="#4a544c", light="#f4efe2", shadow="#2a2e30", haze="#d4d0c4"))
TOD.setdefault("morning", dict(sky0="#7fa6c4", sky1="#f6d9a8", sun="#fff0c8", water="#6f9a9a", far="#a8b8b0",
                               mid="#6f9a78", near="#3f6a50", light="#fff4dc", shadow="#2d3438", haze="#efd8b8"))


def _P(tod):
    return TOD[tod]


def _smoke(ctx, t, x, y, n=3, h=520, col="#f4f0e8", a=0.5, seed=0):
    """Incense smoke: thin ribbons rising and curling."""
    for k in range(n):
        ctx.new_path()
        ph = seed * 1.7 + k * 2.1
        pts = []
        for i in range(24):
            u = i / 23
            yy = y - u * h
            xx = x + k * 6 + math.sin(u * 5.0 + t * 0.9 + ph) * (6 + 60 * u * u) + u * 40 * math.sin(t * 0.3 + ph)
            pts.append((xx, yy))
        spline(ctx, pts)
        src(ctx, col, a * (0.7 - 0.15 * k))
        ctx.set_line_width(3.5 - k * 0.7)
        ctx.stroke()


def stupa(ctx, P, x, base, s=1.0, seed=0, col="#efe9dc"):
    """A Khmer memorial stupa: stepped base, glass-fronted shaft, tiered roofs and a tall spire."""
    shade = mix(col, P["shadow"], 0.25)
    rect(ctx, x - 300 * s, base - 60 * s, 600 * s, 60 * s, mix(col, "#b8ae98", 0.4), 0.4, seed)
    rect(ctx, x - 250 * s, base - 110 * s, 500 * s, 50 * s, mix(col, "#c8bea8", 0.3), 0.4, seed + 1)
    for k in range(5):   # steps
        fill_rect(ctx, x - 70 * s + k * 4 * s, base - 60 * s + k * 12 * s, 140 * s - k * 8 * s, 6 * s, shade, 0.6)
    rect(ctx, x - 150 * s, base - 520 * s, 300 * s, 410 * s, col, 0.5, seed + 2)
    fill_rect(ctx, x - 110 * s, base - 480 * s, 220 * s, 350 * s, mix("#8a96a0", P["sky1"], 0.3), 0.9)
    for k in range(5):
        fill_rect(ctx, x - 110 * s, base - 480 * s + k * 70 * s, 220 * s, 3 * s, mix(col, "#ffffff", 0.3), 0.8)
    fill_rect(ctx, x - 2 * s, base - 480 * s, 4 * s, 350 * s, mix(col, "#ffffff", 0.3), 0.8)
    y = base - 520 * s
    for k, (w, h) in enumerate(((380, 70), (300, 64), (230, 58), (170, 52))):   # tiered roofs
        w, h = w * s, h * s
        sheet(ctx, path_poly([(x - w / 2 - 30 * s, y), (x + w / 2 + 30 * s, y), (x + w / 2 - 10 * s, y - h),
                              (x - w / 2 + 10 * s, y - h)]), mix("#c8a24a", col, 0.35), shadow=0.3, seed=seed + 3 + k)
        for sx in (-1, 1):    # naga finials
            ctx.new_path()
            ctx.move_to(x + sx * (w / 2 + 30 * s), y)
            ctx.curve_to(x + sx * (w / 2 + 50 * s), y - 10 * s, x + sx * (w / 2 + 52 * s), y - 30 * s,
                         x + sx * (w / 2 + 40 * s), y - 42 * s)
            src(ctx, mix("#c8a24a", col, 0.3))
            ctx.set_line_width(7 * s)
            ctx.stroke()
        y -= h + 26 * s
        rect(ctx, x - w * 0.3, y, w * 0.6, 26 * s, col, 0.3, seed + 8 + k)
    sheet(ctx, path_poly([(x - 30 * s, y), (x + 30 * s, y), (x + 4 * s, y - 230 * s), (x - 4 * s, y - 230 * s)]),
          mix("#c8a24a", col, 0.25), shadow=0.3, seed=seed + 14)


def frangipani(ctx, P, x, y, h, seed=0):
    R = rng(seed)
    col = mix("#6a5a48", P["shadow"], 0.2)
    def br(x0, y0, ang, L, w, d):
        x1, y1 = x0 + math.cos(ang) * L, y0 - math.sin(ang) * L
        ctx.new_path()
        ctx.move_to(x0, y0)
        ctx.line_to(x1, y1)
        src(ctx, col)
        ctx.set_line_width(w)
        ctx.set_line_cap(1)
        ctx.stroke()
        if d == 0:
            for k in range(6):
                a = R.random() * 6.28
                ctx.new_path()
                ellipse(ctx, x1 + math.cos(a) * 26, y1 + math.sin(a) * 18, 30, 12, a)
                src(ctx, mix("#4f7a52", P["mid"], 0.3))
                ctx.fill()
            for k in range(3):
                ctx.new_path()
                ellipse(ctx, x1 + R.normal() * 16, y1 + R.normal() * 10, 9, 9)
                src(ctx, "#f8f2e0")
                ctx.fill()
            return
        for k in range(2):
            br(x1, y1, ang + (k - 0.5) * (0.6 + R.random() * 0.4), L * 0.72, w * 0.66, d - 1)
    br(x, y, math.pi / 2 + R.normal() * 0.05, h * 0.32, 22 * h / 400, 3)


# ================================================================ PRESENT DAY: MEMORIAL AT DAWN
def make_memorial(tod="morning", people=None, mouth_fn=None, incense=True, visitors=False, close=False):
    P = _P(tod)

    def sky_(ctx):
        sky60(ctx, P, 0.6, (0.78, 0.44), 110, 7501, 2)
        PP.ridge(ctx, P, 860, 50, mix(P["far"], P["haze"], 0.45), 7502)

    def far(ctx):
        for i, x in enumerate((180, 420, 2050, 2280)):
            sugar_palm(ctx, P, x, 880, 300 + (i % 2) * 60, 7503 + i)
        stupa(ctx, P, 1250, 900, 0.95, 7510)

    def mid(ctx):
        sheet(ctx, path_poly([(-30, 880), (SW + 30, 880), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix("#9aa47a", P["mid"], 0.35), shadow=0.1, seed=7520)
        sheet(ctx, path_poly([(1080, 880), (1420, 880), (1700, SH + 30), (800, SH + 30)]),
              mix("#d8cdb4", P["light"], 0.3), shadow=0.1, seed=7521)      # path to the stupa
        for i, (x, y, h) in enumerate(((420, 1040, 520), (2000, 1050, 560), (2300, 1180, 600))):
            frangipani(ctx, P, x, y, h, 7530 + i)

    def near(ctx):
        # lotus pond along the bottom
        sheet(ctx, path_poly([(-30, 1250), (760, 1230), (900, SH + 30), (-30, SH + 30)]),
              mix("#6a8a8a", P["water"], 0.4), shadow=0.1, seed=7540)
        R = rng(7541)
        for k in range(9):
            x, y = 60 + R.random() * 680, 1270 + R.random() * 60
            ctx.new_path()
            ellipse(ctx, x, y, 46, 14)
            src(ctx, mix("#4f7a52", P["mid"], 0.2))
            ctx.fill()
        for k, (x, y) in enumerate(((180, 1240), (420, 1255), (620, 1236))):
            PP.lotus(ctx, P, x, y, 1.1, 1.0, 7542 + k, "#f2b6be")
        # incense pot on a low table near the path
        rect(ctx, 1500, 1150, 260, 22, "#7a5a3a", 0.4, 7550)
        fill_rect(ctx, 1520, 1172, 14, 70, "#5a4028")
        fill_rect(ctx, 1726, 1172, 14, 70, "#5a4028")
        ctx.new_path()
        ellipse(ctx, 1630, 1132, 70, 26)
        src(ctx, "#a88a5a")
        ctx.fill()
        fill_rect(ctx, 1562, 1100, 136, 34, "#a88a5a")
        for k in range(7):
            fill_rect(ctx, 1590 + k * 13, 1010 - (k % 3) * 8, 3, 92 + (k % 3) * 8, "#8a3a2a")

    layers = [(_key("mm_sky", tod=tod, v=V), sky_, 0.0), (_key("mm_far", tod=tod, v=V), far, 0.3),
              (_key("mm_mid", tod=tod, v=V), mid, 0.6), (_key("mm_near", tod=tod, v=V), near, 0.9)]

    def fx(ctx, t, d, dp):
        if dp == 0.0:
            glow(ctx, SW * 0.78, SH * 0.44 * 0.6 + 120, 420, P["sun"], 0.16)
        if dp == 0.9 and incense:
            for k in range(7):
                glow(ctx, 1592 + k * 13, 1008 - (k % 3) * 8, 9, GOLD_PAINT, 0.9)
            _smoke(ctx, t, 1630, 1000, 4, 620, "#f6f2ea", 0.42, 3)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.6, 0.9])


# ================================================================ PRESENT DAY: ALTAR WITH A CANDLE
def make_altar(tod="morning", lit_at=None, portrait=True, people=None, mouth_fn=None):
    """A low altar table on the memorial terrace: a drawn portrait of Sophal's father (fictional), lotus, incense and
    a candle that Malis lights at time lit_at (None = already lit)."""
    P = _P(tod)

    def back(ctx):
        fill_rect(ctx, 0, 0, SW, SH, mix("#e8dcc4", P["haze"], 0.3))
        g = 0
        for k in range(9):
            fill_rect(ctx, 0, 120 + k * 110, SW, 4, mix("#c8b896", P["haze"], 0.3), 0.5)
        fill_rect(ctx, 0, 980, SW, 370, mix("#8a6a48", P["shadow"], 0.15))
        rect(ctx, 300, 820, 1800, 70, "#6a4a30", 0.5, 7601)          # table top
        fill_rect(ctx, 360, 890, 40, 300, "#4a3220")
        fill_rect(ctx, 2000, 890, 40, 300, "#4a3220")
        if portrait:   # framed pencil portrait of a man in a white shirt (fictional: Sophal's father)
            rect(ctx, 760, 420, 330, 410, "#3a2c20", 0.6, 7602)
            fill_rect(ctx, 790, 450, 270, 350, "#e9e2d0")
            import cast
            ctx.save()
            ctx.rectangle(790, 450, 270, 350)
            ctx.clip()
            cast.draw(ctx, 925, 1120, 640, "dad75", "idle", 0.0, 0, "calm", None)
            ctx.restore()
            src(ctx, "#3a2c20")
            ctx.set_line_width(30)
            ctx.rectangle(775, 435, 300, 380)
            ctx.stroke()
        # lotus bowl
        ctx.new_path()
        ellipse(ctx, 1380, 812, 120, 30)
        src(ctx, "#b8a07a")
        ctx.fill()
        for k, x in enumerate((1320, 1380, 1440)):
            PP.lotus(ctx, P, x, 790 - (k == 1) * 30, 1.5, 0.8 + 0.2 * (k == 1), 7610 + k, "#f2b6be")
        # incense pot
        ctx.new_path()
        ellipse(ctx, 1700, 812, 80, 22)
        src(ctx, "#a88a5a")
        ctx.fill()
        fill_rect(ctx, 1630, 760, 140, 52, "#a88a5a")
        for k in range(5):
            fill_rect(ctx, 1665 + k * 18, 640 - (k % 2) * 10, 3, 122, "#8a3a2a")

    layers = [(_key("al_back", tod=tod, p=portrait, v=V), back, 0.5)]

    def fx(ctx, t, d, dp):
        if dp != 0.5:
            return
        for k in range(5):
            glow(ctx, 1666 + k * 18, 640 - (k % 2) * 10, 8, GOLD_PAINT, 0.9)
        _smoke(ctx, t, 1700, 640, 3, 600, "#ffffff", 0.35, 5)
        lit = 1.0 if lit_at is None else clamp((t - lit_at) / 0.6)
        candle(ctx, 1160, 830, 2.4, t, 1.0, lit)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.5, 0.85])


# ================================================================ MEMORY: THE ROAD OUT OF THE CITY
def make_exodus(tod="grey", people=None, mouth_fn=None, city=True, carts=True, dust=True, home=False):
    """A national road leaving Phnom Penh: the city's edge behind, palms, abandoned cars and carts.  home=True: the
    same road in 1979, empty and overgrown, a few people walking back."""
    P = _P(tod)

    def sky_(ctx):
        sky60(ctx, P, 0.58, (0.25, 0.32), 80, 7701, 2)
        if city:
            R = rng(7702)
            x = 1300
            while x < SW + 40:
                w, h = 90 + R.random() * 120, 60 + R.random() * 160
                fill_rect(ctx, x, 800 - h, w, h + 20, mix(P["far"], P["haze"], 0.4 + 0.2 * R.random()))
                x += w + 10

    def land(ctx):
        sheet(ctx, path_poly([(-30, 800), (SW + 30, 800), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix("#9a9a7a", P["mid"], 0.4), shadow=0.1, seed=7710)
        for k in range(6):
            fill_rect(ctx, -30, 830 + k * (30 + k * 10), SW + 60, 5, mix("#7a7a60", P["mid"], 0.3), 0.6)
        for i, x in enumerate((140, 520, 980, 1900, 2260)):
            sugar_palm(ctx, P, x, 870 + (i % 2) * 20, 300 + (i % 3) * 40, 7711 + i)
        # the road: a wide band receding to the right
        sheet(ctx, path_poly([(-30, 1080), (SW + 30, 930), (SW + 30, 990), (-30, 1330)]),
              mix("#8a8678", P["shadow"], 0.15), shadow=0.1, seed=7720)
        if carts and not home:
            # an abandoned car on the verge and an overturned cart
            rect(ctx, 1700, 900, 220, 70, "#5a5a56", 0.4, 7721)
            rect(ctx, 1740, 860, 130, 44, "#6a6a66", 0.3, 7722)
            for x in (1735, 1880):
                ctx.new_path()
                ellipse(ctx, x, 972, 22, 22)
                src(ctx, "#2a2a28")
                ctx.fill()
            sheet(ctx, path_poly([(380, 1030), (560, 1010), (590, 1060), (410, 1080)]), "#6a5038", shadow=0.4,
                  seed=7723)
            ctx.new_path()
            ellipse(ctx, 600, 1050, 48, 48)
            src(ctx, "#4a3828")
            ctx.set_line_width(8)
            ctx.stroke()
        if home:   # weeds across the empty road
            R = rng(7730)
            for k in range(160):
                x = R.random() * SW
                y = 1330 - x * 0.16 + R.random() * 60 - 30
                ctx.new_path()
                ctx.move_to(x, y)
                ctx.line_to(x + R.normal() * 6, y - 18 - R.random() * 30)
                src(ctx, mix("#5a6a48", P["mid"], 0.3))
                ctx.set_line_width(3)
                ctx.stroke()

    layers = [(_key("ex_sky", tod=tod, c=city, v=V), sky_, 0.0),
              (_key("ex_land", tod=tod, c=carts, h=home, v=V), land, 0.6)]

    def fx(ctx, t, d, dp):
        if dp != 0.6 or not dust:
            return
        for k in range(10):   # dust haze drifting over the road
            u = (t * 0.03 + k / 10) % 1.0
            src(ctx, P["haze"], 0.18 * math.sin(u * math.pi))
            ctx.new_path()
            ellipse(ctx, -200 + u * (SW + 400), 1100 - u * 120, 260, 50)
            ctx.fill()
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.6])


def crowd(n=12, seed=0, vx=26, y0=1130, y1=1300, h0=260, h1=340, kinds=None, x0=-300, x1=SW + 200, pose="walk_slow"):
    """A slow column of people walking along the exodus road (sizes grow toward the camera)."""
    from sets import F
    R = rng(seed)
    kinds = kinds or ["mom75", "dad75", "pp_man", "pp_woman", "pp_woman2", "refugee_c", "kh_elder", "student_m",
                      "pp_man2", "refugee_w", "kh_monk", "student_f"]
    out = []
    for k in range(n):
        u = R.random()
        y = y0 + (y1 - y0) * u
        x = x0 + R.random() * (x1 - x0) - (y - y0) * 0.6
        h = h0 + (h1 - h0) * u
        kind = kinds[int(R.random() * len(kinds))]
        if kind in ("refugee_c", "vuthy", "child_k"):
            h *= 0.62
        ps = pose if kind != "kh_elder" else "walk_slow"
        if R.random() < 0.35 and kind not in ("refugee_c", "kh_monk"):
            ps = "carry_bundle"
        out.append(F(x, y, h, kind, ps, 90, 200 + seed + k, vx=vx * (0.8 + 0.4 * R.random()), vy=-vx * 0.12))
    return out


# ================================================================ MEMORY: STILL LIFE
def make_still(kind="shoes", tod="grey"):
    """Close-up symbols: 'shoes' (a pair of sandals left on the road), 'glasses' (broken spectacles on a book),
    'bowl' (a tin bowl and spoon), 'notes' (banknotes in the wind), 'books' (books on a classroom floor),
    'gate' (a chained pagoda gate), 'krama' (a scarf left on a bamboo fence)."""
    P = _P(tod)

    def ground(ctx):
        if kind in ("books", "glasses"):
            fill_rect(ctx, 0, 0, SW, SH, "#9a8a70")
            for k in range(14):                       # floor boards
                fill_rect(ctx, 0, k * 100, SW, 4, "#6a5a48", 0.7)
        elif kind == "gate":
            sky60(ctx, P, 0.7, (0.7, 0.3), 60, 7801, 1)
        else:
            fill_rect(ctx, 0, 0, SW, SH, "#a49c88")
            R = rng(7802)
            for k in range(900):                      # dust and grit
                src(ctx, "#6a6458", 0.25 + 0.3 * R.random())
                ctx.new_path()
                ellipse(ctx, R.random() * SW, R.random() * SH, 1 + R.random() * 4, 1 + R.random() * 3)
                ctx.fill()

    def objects(ctx):
        if kind == "shoes":
            for k, (x, y, a) in enumerate(((1060, 760, -0.25), (1300, 800, 0.15))):
                ctx.save()
                ctx.translate(x, y)
                ctx.rotate(a)
                ctx.new_path()
                ellipse(ctx, 0, 0, 160, 62)
                src(ctx, "#3a3632")
                ctx.fill()
                ctx.new_path()
                ellipse(ctx, 0, 0, 140, 48)
                src(ctx, "#5a544c")
                ctx.fill()
                src(ctx, "#2a2622")
                ctx.set_line_width(14)
                ctx.move_to(-20, -40)
                ctx.curve_to(10, -70, 60, -50, 50, 30)
                ctx.stroke()
                ctx.restore()
        elif kind == "glasses":
            rect(ctx, 820, 560, 760, 480, "#6a5a4a", 0.6, 7810)          # closed book
            fill_rect(ctx, 840, 580, 720, 440, "#8a7a62")
            fill_rect(ctx, 1150, 560, 14, 480, "#4a3e32")
            for k, cx in enumerate((1080, 1330)):
                src(ctx, "#1e1c1a")
                ctx.set_line_width(12)
                ctx.new_path()
                ellipse(ctx, cx, 720, 110, 82)
                ctx.stroke()
                src(ctx, "#d8d4c8", 0.35)
                ctx.new_path()
                ellipse(ctx, cx, 720, 100, 72)
                ctx.fill()
            src(ctx, "#1e1c1a")
            ctx.set_line_width(10)
            ctx.move_to(1190, 712)
            ctx.curve_to(1200, 690, 1215, 690, 1222, 712)
            ctx.stroke()
            ctx.move_to(970, 700)
            ctx.line_to(760, 640)
            ctx.stroke()
            src(ctx, "#2a2826")                       # the crack across one lens
            ctx.set_line_width(4)
            ctx.move_to(1270, 650)
            ctx.line_to(1320, 715)
            ctx.line_to(1300, 760)
            ctx.line_to(1360, 790)
            ctx.stroke()
        elif kind == "bowl":
            ctx.new_path()
            ellipse(ctx, 1200, 700, 330, 120)
            src(ctx, "#6a6a66")
            ctx.fill()
            ctx.new_path()
            ellipse(ctx, 1200, 680, 300, 96)
            src(ctx, "#8a8a84")
            ctx.fill()
            ctx.new_path()
            ellipse(ctx, 1200, 700, 250, 70)
            src(ctx, "#c8c2b0")
            ctx.fill()                                # thin porridge
            src(ctx, "#4a4a46")
            ctx.set_line_width(18)
            ctx.move_to(1500, 820)
            ctx.line_to(1820, 1000)
            ctx.stroke()
        elif kind == "books":
            R = rng(7820)
            for k in range(9):
                x, y, a = 400 + R.random() * 1600, 380 + R.random() * 620, R.normal() * 0.6
                ctx.save()
                ctx.translate(x, y)
                ctx.rotate(a)
                rect(ctx, -150, -100, 300, 200, ["#7a6a58", "#6a6a6a", "#8a7a62", "#5a5048"][k % 4], 0.5, 7821 + k)
                fill_rect(ctx, -140, -92, 280, 184, "#e2dac6")
                for j in range(7):
                    fill_rect(ctx, -120, -70 + j * 22, 110 if j % 3 else 80, 4, "#8a8274", 0.8)
                    fill_rect(ctx, 12, -70 + j * 22, 110 if j % 2 else 90, 4, "#8a8274", 0.8)
                fill_rect(ctx, -3, -96, 6, 192, "#a89e8a")
                ctx.restore()
        elif kind == "gate":
            sheet(ctx, path_poly([(-30, 1000), (SW + 30, 1000), (SW + 30, SH + 30), (-30, SH + 30)]),
                  mix("#8a8a78", P["mid"], 0.3), shadow=0.1, seed=7830)
            # pagoda roof behind the wall
            sheet(ctx, path_poly([(900, 520), (1500, 520), (1700, 700), (700, 700)]), mix("#7a5a40", P["far"], 0.3),
                  shadow=0.3, seed=7831)
            sheet(ctx, path_poly([(1050, 360), (1350, 360), (1500, 520), (900, 520)]), mix("#8a6a48", P["far"], 0.3),
                  shadow=0.3, seed=7832)
            rect(ctx, -30, 640, SW + 60, 380, "#b8b0a0", 0.5, 7833)    # wall
            rect(ctx, 820, 470, 760, 560, "#c8c0ae", 0.6, 7834)         # gate arch
            sheet(ctx, path_poly([(780, 480), (1620, 480), (1460, 320), (940, 320)]), "#a89878", shadow=0.4, seed=7835)
            for k in range(2):                                          # closed doors
                rect(ctx, 900 + k * 300, 600, 300, 430, "#5a4a3a", 0.3, 7836 + k)
                for j in range(5):
                    fill_rect(ctx, 920 + k * 300, 630 + j * 80, 260, 6, "#3a3028", 0.8)
            src(ctx, "#2a2a28")                                         # chain and padlock
            ctx.set_line_width(10)
            for j in range(9):
                ctx.new_path()
                ellipse(ctx, 1110 + j * 20, 800 + math.sin(j * 0.7) * 10, 14, 9, 0.3 * (j % 2))
                ctx.stroke()
            rect(ctx, 1170, 820, 60, 70, "#3a3a38", 0.3, 7840)
            R = rng(7841)
            for k in range(220):                                        # weeds at the foot of the wall
                x = R.random() * SW
                ctx.new_path()
                ctx.move_to(x, 1030)
                ctx.line_to(x + R.normal() * 10, 1030 - 20 - R.random() * 70)
                src(ctx, mix("#4a5a3a", P["mid"], 0.3))
                ctx.set_line_width(3)
                ctx.stroke()
        elif kind == "krama":
            sky60(ctx, P, 0.7, (0.7, 0.3), 60, 7850, 1)
            for k in range(14):
                fill_rect(ctx, 200 + k * 150, 500, 18, 700, "#7a6a50")
            fill_rect(ctx, 0, 620, SW, 16, "#6a5a40")
            fill_rect(ctx, 0, 860, SW, 16, "#6a5a40")
            sheet(ctx, path_poly([(980, 610), (1300, 610), (1330, 1000), (1260, 1010), (1200, 700), (1060, 700),
                                  (1010, 1020), (950, 1000)]), "#1f5cff", shadow=0.5, seed=7851)
            for j in range(6):
                fill_rect(ctx, 990, 640 + j * 50, 300, 8, "#e8e4da", 0.8)

    layers = [(_key("st_g", k=kind, tod=tod, v=V), ground, 0.3), (_key("st_o", k=kind, tod=tod, v=V), objects, 0.7)]

    def fx(ctx, t, d, dp):
        if dp != 0.7 or kind != "notes":
            return
        R = rng(7860)
        for k in range(16):                                             # riel notes blowing across the street
            sp = 120 + R.random() * 140
            x = (R.random() * SW + t * sp) % (SW + 400) - 200
            y = 300 + R.random() * 900 + math.sin(t * 1.5 + k) * 40
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(math.sin(t * 2 + k) * 0.8)
            ctx.scale(1, 0.6 + 0.4 * math.cos(t * 2.5 + k))
            src(ctx, "#b8b4a4")
            ctx.rectangle(-90, -42, 180, 84)
            ctx.fill()
            src(ctx, "#6a665c")
            ctx.set_line_width(3)
            ctx.rectangle(-80, -34, 160, 68)
            ctx.stroke()
            ctx.new_path()
            ellipse(ctx, 40, 0, 22, 22)
            ctx.stroke()
            ctx.restore()
    return dict(layers=layers, dyn=fx, dyn_depths=[0.7])


# ================================================================ MEMORY / SYMBOL: CLASSROOM
def make_classroom(variant="books", tod="grey", people=None, mouth_fn=None):
    """'books': an abandoned classroom, books on the floor, chalk letters on the board.
    'bars': the same kind of room with barred windows, empty, a single chair (S-21, symbolic; nothing else shown)."""
    P = _P(tod)

    def room(ctx):
        fill_rect(ctx, 0, 0, SW, SH, "#c8c0ae")
        fill_rect(ctx, 0, 1000, SW, 350, "#8a7e6a")                     # floor
        for k in range(8):
            fill_rect(ctx, 0, 1000 + k * 46, SW, 3, "#6a604e", 0.6)
        for k, x in enumerate((180, 1680)):                             # windows
            fill_rect(ctx, x, 260, 520, 520, "#efece2")
            fill_rect(ctx, x, 260, 520, 14, "#7a7266")
            fill_rect(ctx, x, 766, 520, 14, "#7a7266")
            n = 9 if variant == "bars" else 3
            for j in range(n + 1):
                fill_rect(ctx, x + j * 520 / n - 4, 260, 8 if variant == "bars" else 12, 520, "#5a544a")
            if variant != "bars":
                fill_rect(ctx, x, 510, 520, 10, "#5a544a")
        if variant == "books":
            rect(ctx, 820, 300, 760, 400, "#3a3e38", 0.5, 7901)          # blackboard
            for j, w in enumerate((420, 300, 520)):                       # faint chalk lines (Khmer letters)
                fill_rect(ctx, 880, 380 + j * 90, w, 6, "#a8aaa0", 0.6)
            for r_ in range(2):
                for c in range(4):
                    x, y = 360 + c * 470, 920 + r_ * 160
                    rect(ctx, x, y, 300, 40, "#7a6248", 0.4, 7910 + r_ * 4 + c)
                    fill_rect(ctx, x + 20, y + 40, 16, 150, "#5a4836")
                    fill_rect(ctx, x + 264, y + 40, 16, 150, "#5a4836")
            for k, (x, y, a) in enumerate(((700, 1220, 0.4), (1300, 1260, -0.3), (1750, 1200, 0.9))):
                ctx.save()
                ctx.translate(x, y)
                ctx.rotate(a)
                rect(ctx, -70, -46, 140, 92, "#6a6458", 0.4, 7930 + k)
                fill_rect(ctx, -64, -40, 128, 80, "#ddd6c4")
                ctx.restore()
        else:
            rect(ctx, 1090, 980, 220, 30, "#6a5a48", 0.4, 7940)          # a single chair
            fill_rect(ctx, 1100, 1010, 14, 140, "#4a3e30")
            fill_rect(ctx, 1286, 1010, 14, 140, "#4a3e30")
            fill_rect(ctx, 1100, 780, 14, 210, "#4a3e30")
            fill_rect(ctx, 1100, 800, 200, 14, "#4a3e30")

    layers = [(_key("cr_room", v_=variant, tod=tod, v=V), room, 0.5)]

    def fx(ctx, t, d, dp):
        if dp != 0.5:
            return
        for x in (180, 1680):                                           # shafts of light and dust
            g = 0.10 if variant == "books" else 0.13
            ctx.new_path()
            poly(ctx, [(x, 260), (x + 520, 260), (x + 820, 1250), (x + 260, 1250)])
            src(ctx, "#fffaea", g)
            ctx.fill()
        R = rng(7950)
        for k in range(40):
            x = 300 + R.random() * 1900
            y = (R.random() * 900 + t * (8 + R.random() * 10)) % 900 + 300
            src(ctx, "#fffaea", 0.35)
            ctx.new_path()
            ellipse(ctx, x + math.sin(t + k) * 20, y, 3, 3)
            ctx.fill()
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.5, 0.8])


# ================================================================ MEMORY: COOPERATIVE FIELDS AND DAM
def make_fields(tod="grey", people=None, mouth_fn=None, dam=False, night=False):
    P = _P("night" if night else tod)

    def sky_(ctx):
        sky60(ctx, P, 0.55, (0.3, 0.3), 70, 8001, 1)
        PP.ridge(ctx, P, 760, 40, mix(P["far"], P["haze"], 0.35), 8002)

    def land(ctx):
        sheet(ctx, path_poly([(-30, 740), (SW + 30, 740), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix("#8a9a7a", P["mid"], 0.4), shadow=0.1, seed=8003)
        for r_ in range(7):   # straight paddy dykes in a grid (DK re-dug fields into squares)
            y = 760 + r_ * (40 + r_ * 16)
            fill_rect(ctx, -30, y, SW + 60, 7, mix("#c0b48c", P["mid"], 0.4), 0.85)
        for c in range(-8, 16):
            x0 = 1200 + c * 180
            ctx.new_path()
            ctx.move_to(x0 + (x0 - 1200) * 0.05, 760)
            ctx.line_to(x0 + (x0 - 1200) * 1.9, SH + 30)
            src(ctx, mix("#c0b48c", P["mid"], 0.4), 0.7)
            ctx.set_line_width(6)
            ctx.stroke()
        for i, x in enumerate((240, 1960)):
            sugar_palm(ctx, P, x, 780, 260, 8010 + i)
        if dam:   # a long earthen embankment crossing the scene
            sheet(ctx, path_poly([(-30, 900), (SW + 30, 760), (SW + 30, 880), (-30, 1080)]),
                  mix("#a08a68", P["mid"], 0.2), shadow=0.6, seed=8020)
            sheet(ctx, path_poly([(-30, 880), (SW + 30, 742), (SW + 30, 770), (-30, 912)]),
                  mix("#b8a07a", P["light"], 0.2), shadow=0.0, seed=8021)
            fill_rect(ctx, 1500, 560, 8, 260, "#3a3632")               # a flag on a pole (grey in memory)
            sheet(ctx, path_poly([(1508, 560), (1650, 575), (1508, 630)]), "#7a4a40", shadow=0.2, seed=8022)

    layers = [(_key("fd_sky", tod=tod, n=night, v=V), sky_, 0.0), (_key("fd_land", tod=tod, d=dam, n=night, v=V),
                                                                    land, 0.6)]

    def fx(ctx, t, d, dp):
        if dp == 0.0 and night:
            ctx.new_path()
            ellipse(ctx, 1900, 200, 40, 40)
            src(ctx, "#e8e4d4", 0.8)
            ctx.fill()
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.6])


def workers(n=10, seed=0, y0=1000, y1=1280, h0=240, h1=330, pose="harvest", kinds=("worker_m", "worker_w"), vx=0,
            x0=100, x1=SW - 100, yaw=90):
    from sets import F
    R = rng(seed)
    out = []
    for k in range(n):
        u = R.random()
        y = y0 + (y1 - y0) * u
        out.append(F(x0 + R.random() * (x1 - x0), y, h0 + (h1 - h0) * u, kinds[k % len(kinds)], pose,
                     yaw * (1 if R.random() < 0.7 else -1), 300 + seed + k, vx=vx))
    return out


# ================================================================ MEMORY: COMMUNAL DINING HALL
def make_hall(tod="grey", people=None, mouth_fn=None):
    P = _P(tod)

    def back(ctx):
        sky60(ctx, P, 0.6, (0.5, 0.3), 60, 8101, 1)
        sheet(ctx, path_poly([(-30, 860), (SW + 30, 860), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix("#8a8470", P["mid"], 0.3), shadow=0.1, seed=8102)
        sheet(ctx, path_poly([(-60, 300), (SW + 60, 300), (SW - 100, 120), (100, 120)]), "#8a7a5a", shadow=0.6,
              seed=8103)   # thatched roof
        R = rng(8104)
        for k in range(160):
            x = 100 + R.random() * (SW - 200)
            ctx.new_path()
            ctx.move_to(x, 130 + R.random() * 20)
            ctx.line_to(x + R.normal() * 8, 300)
            src(ctx, "#6a5a40", 0.5)
            ctx.set_line_width(3)
            ctx.stroke()
        for k in range(7):
            fill_rect(ctx, 120 + k * 360, 300, 22, 700, "#5a4a36")

    def tables(ctx):
        for r_ in range(2):
            y = 980 + r_ * 200
            rect(ctx, 80, y, SW - 160, 40, "#7a6a50", 0.5, 8110 + r_)
            for k in range(14):
                x = 160 + k * 160
                ctx.new_path()
                ellipse(ctx, x, y + 6, 46, 14)
                src(ctx, "#8a8a84")
                ctx.fill()
                ctx.new_path()
                ellipse(ctx, x, y + 2, 36, 9)
                src(ctx, "#bcb6a4")
                ctx.fill()

    layers = [(_key("hl_back", tod=tod, v=V), back, 0.3), (_key("hl_tab", tod=tod, v=V), tables, 0.85)]
    return dict(layers=layers, dyn=people_dyn(people or [], P, mouth_fn), dyn_depths=[0.6, 0.85])
