"""Sets for 'The Khmer Republic: Cambodia 1970-1975'.  Drawn flat, then turned into charcoal-and-ink by ink.inkify.
Every scene is a reconstruction.  Paint warm accent props (lamps, incense, candles, the family's clothes) in
ink.GOLD_PAINT so they survive the ink pass as the film's single warm colour.

make_newsstand  Phnom Penh shophouse street with Dara's uncle's newspaper kiosk (war 0..1 adds sandbags, shelters)
make_pagoda     a Phnom Penh wat: vihara, incense, candles (refugees=True: families camped in the courtyard)
make_mekong     the river below Phnom Penh: barges and tugs of a supply convoy, distant smoke (no violence shown)
make_wallmap    the uncle's room: a hand-drawn map of Cambodia pinned on the wall, pencil front lines
make_empty      the same street, empty, a newspaper blowing along it (closing)
"""
import math

import paper as PP
from core import SH, SW, clamp, ease, ellipse, glow, mix, poly, rng, src, draw_text, KM_SANS
from paper import TOD, R60, sheet, path_poly
from sets import _key, _comb, people_dyn
from sets60 import rect, fill_rect, sky60, sugar_palm, kr_flag, independence_monument
from ink import GOLD_PAINT

C = R60
V = "70v1"


def _P(tod):
    return TOD[tod]


def shophouse(ctx, P, x, base, w, floors=3, seed=0, col=None, sign=None, shut=0.5):
    """1960s-70s Phnom Penh shophouse: ground-floor shop, upper floors with shutters and a balcony."""
    R = rng(seed)
    col = col or mix("#c8bfa4", P["haze"], 0.2)
    fh = 150
    h = fh * floors + 60
    rect(ctx, x, base - h, w, h, col, 0.6, seed)
    fill_rect(ctx, x - 6, base - h - 14, w + 12, 18, mix(col, "#000000", 0.25))
    for f in range(1, floors):
        y = base - f * fh - 30
        fill_rect(ctx, x + 10, y + 70, w - 20, 10, mix(col, "#000000", 0.3))   # balcony rail
        for k in range(int(w // 90)):
            wx = x + 22 + k * 90
            fill_rect(ctx, wx, y - 40, 56, 100, mix(col, "#000000", 0.45))
            if R.random() < shut:
                for j in range(6):
                    fill_rect(ctx, wx + 2, y - 36 + j * 16, 52, 8, mix(col, "#ffffff", 0.15))
    # ground floor: shop opening with folding grille
    fill_rect(ctx, x + 12, base - 140, w - 24, 140, mix(col, "#000000", 0.55))
    for k in range(int((w - 24) // 18)):
        fill_rect(ctx, x + 14 + k * 18, base - 140, 3, 140, mix(col, "#000000", 0.25))
    if sign:
        fill_rect(ctx, x + 18, base - 190, w - 36, 40, mix(col, "#000000", 0.6))
        for j in range(3):
            fill_rect(ctx, x + 40 + j * (w - 80) / 3, base - 176, (w - 80) / 3 - 20, 12, mix(col, "#ffffff", 0.3))


def kiosk(ctx, P, x, y, s=1.0, papers=True):
    """The uncle's newspaper kiosk: wooden stall, awning, stacks and pegged front pages."""
    w, h = 300 * s, 230 * s
    rect(ctx, x - w / 2, y - h, w, h, "#7a6446", 0.6, 7001)
    sheet(ctx, path_poly([(x - w / 2 - 40 * s, y - h - 10 * s), (x + w / 2 + 40 * s, y - h - 10 * s),
                          (x + w / 2 + 20 * s, y - h - 70 * s), (x - w / 2 - 20 * s, y - h - 70 * s)]), "#5a6248",
          shadow=0.5, seed=7002)
    for k in range(7):   # awning stripes
        fill_rect(ctx, x - w / 2 - 30 * s + k * (w + 60 * s) / 7, y - h - 66 * s, (w + 60 * s) / 14, 54 * s, "#8a8a6a")
    if papers:
        for k in range(4):   # pegged front pages on a string
            px = x - w / 2 + 30 * s + k * 68 * s
            fill_rect(ctx, px, y - h + 14 * s, 56 * s, 76 * s, "#e9e1c8")
            fill_rect(ctx, px + 4 * s, y - h + 20 * s, 48 * s, 12 * s, "#2a2824")
            for j in range(4):
                fill_rect(ctx, px + 4 * s, y - h + 40 * s + j * 10 * s, 48 * s, 3 * s, "#8a8478")
        for k in range(3):   # stacks on the counter
            sx = x - w / 2 + 40 * s + k * 90 * s
            for j in range(5):
                fill_rect(ctx, sx + (j % 2) * 3, y - 70 * s - j * 9 * s, 70 * s, 8 * s, "#e3dbc2" if j % 2 else "#d6ceb4")
    fill_rect(ctx, x - w / 2 - 6 * s, y - 60 * s, w + 12 * s, 14 * s, "#5a4630")


def sandbags(ctx, x, y, n=8, seed=0):
    R = rng(seed)
    for row in range(3):
        for k in range(n - row):
            bx = x + k * 64 + row * 32 + R.normal() * 2
            by = y - row * 30
            ctx.new_path()
            ellipse(ctx, bx, by, 36, 17)
            src(ctx, mix("#9a8e6c", "#5a523e", R.random() * 0.4))
            ctx.fill()


def lean_to(ctx, x, y, w, seed=0):
    """A refugee shelter: tarpaulin over poles, a mat, a bundle (no distress depicted)."""
    R = rng(seed)
    fill_rect(ctx, x, y - 150, 6, 150, "#4a3a2a")
    fill_rect(ctx, x + w, y - 110, 6, 110, "#4a3a2a")
    sheet(ctx, path_poly([(x - 20, y - 150), (x + w + 30, y - 110), (x + w + 20, y - 96), (x - 30, y - 136)]),
          mix("#6a7060", "#8a8a7a", R.random()), shadow=0.5, seed=seed)
    fill_rect(ctx, x + 10, y - 8, w - 10, 10, "#9a8a62")
    ctx.new_path()
    ellipse(ctx, x + w * 0.7, y - 22, 26, 20)
    src(ctx, "#7a6a4a")
    ctx.fill()


def _paper_fly(ctx, t, x0, y0, seed=0, speed=180, k=1.0):
    """A newspaper sheet blowing along the ground."""
    R = rng(seed)
    x = x0 + speed * t
    y = y0 - abs(math.sin(t * 1.8 + seed)) * 90 * k - 20 * math.sin(t * 0.7)
    ang = math.sin(t * 2.3 + seed) * 0.9 + t * 0.6
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    sq = 0.45 + 0.55 * abs(math.cos(t * 2.1 + seed))   # the sheet flaps (foreshortening)
    ctx.scale(1, sq)
    src(ctx, "#ece4cc")
    ctx.rectangle(-70, -50, 140, 100)
    ctx.fill()
    src(ctx, "#2a2824", 0.8)
    ctx.rectangle(-62, -42, 124, 18)
    ctx.fill()
    src(ctx, "#8a8478", 0.7)
    for j in range(5):
        ctx.rectangle(-62, -16 + j * 12, 124 - R.random() * 30, 4)
    ctx.fill()
    ctx.restore()


# ================================================================ NEWSSTAND STREET
def make_newsstand(tod="dawn", people=None, mouth_fn=None, war=0.0, papers=True, flags=False, traffic=0, crowd=False,
                   blow=False):
    P = _P(tod if tod in TOD else "day")

    def sky_(ctx):
        sky60(ctx, P, 0.6, (0.82, 0.42), 80, 7010, 2)

    def far(ctx):
        R = rng(7011)
        x = -40
        while x < SW:
            w = 160 + R.random() * 220
            h = 140 + R.random() * 200
            rect(ctx, x, 880 - h, w, h, mix(P["far"], P["haze"], 0.35 + 0.3 * R.random()), 0.2, 7012)
            x += w + 30
        independence_monument(ctx, P, 1900, 885, 170, 7013, mix(P["far"], "#6a5a4a", 0.3))

    def mid(ctx):
        sheet(ctx, path_poly([(-30, 960), (SW + 30, 960), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix("#8a8470", P["shadow"], 0.2), shadow=0.2, seed=7020)
        signs = ["ហាងបាយ", None, "ហាងមាស", None, "ឱសថស្ថាន", None]
        x = -20
        for k in range(6):
            w = 330 + (k % 3) * 40
            shophouse(ctx, P, x, 1010, w, 3 + (k % 2), 7021 + k,
                      mix(["#c8bfa4", "#b4ae94", "#cfc6aa"][k % 3], P["haze"], 0.15), signs[k], 0.4 + war * 0.4)
            x += w + 14
        for i, xx in enumerate((690, 1450, 2230)):
            sugar_palm(ctx, P, xx, 1015, 330, 7030 + i)
        if flags:
            for xx in (380, 1100, 1800):
                kr_flag(ctx, xx, 760, 110, 0.0)

    def street(ctx):
        sheet(ctx, path_poly([(-30, 1050), (SW + 30, 1050), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix("#5a5a52", P["shadow"], 0.25), shadow=0.2, seed=7040)
        fill_rect(ctx, -30, 1036, SW + 60, 22, mix("#b8b098", P["shadow"], 0.1))
        kiosk(ctx, P, 520, 1180, 1.05, papers)
        if war > 0.35:
            sandbags(ctx, 1500, 1170, 7, 7041)
        if war > 0.6:
            for i, xx in enumerate((1900, 2120)):
                lean_to(ctx, xx, 1180, 170, 7042 + i)
        # a lamp post with a warm lamp (the accent)
        fill_rect(ctx, 980, 760, 10, 420, "#3a3a34")
        fill_rect(ctx, 960, 744, 50, 22, "#3a3a34")
        ctx.new_path()
        ellipse(ctx, 985, 770, 16, 12)
        src(ctx, GOLD_PAINT if tod in ("dawn", "dusk", "night") else "#cfc6aa")
        ctx.fill()

    layers = [(_key("ns_sky", tod=tod, v=V), sky_, 0.0), (_key("ns_far", tod=tod, v=V), far, 0.25),
              (_key("ns_mid", tod=tod, w=round(war, 1), f=flags, v=V), mid, 0.55),
              (_key("ns_st", tod=tod, w=round(war, 1), p=papers, v=V), street, 0.85)]

    def fx(ctx, t, d, dp):
        if dp == 0.0 and tod in ("dawn", "dusk", "night"):
            glow(ctx, 985 * 0 + 1800, 600, 500, P["sun"], 0.10)
        if dp == 0.85:
            if tod in ("dawn", "dusk", "night"):
                glow(ctx, 985, 770, 120, "#ffb060", 0.25 + 0.04 * math.sin(t * 3))
            if blow:
                for j in range(2):
                    _paper_fly(ctx, t, -300 + j * 900, 1230 - j * 30, 31 + j, 210 - j * 40)
    from sets60 import traffic_dyn
    return dict(layers=layers, dyn=_comb(fx, traffic_dyn(P, traffic, seed=9) if traffic else None,
                                         people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.55, 0.85])


def make_empty(tod="grey", blow=True):
    return make_newsstand(tod, people=None, war=1.0, papers=False, blow=blow)


# ================================================================ PAGODA
def make_pagoda(tod="dusk", people=None, mouth_fn=None, refugees=False):
    P = _P(tod)

    def sky_(ctx):
        sky60(ctx, P, 0.62, (0.25, 0.38), 75, 7100, 2)

    def wat(ctx):
        sheet(ctx, path_poly([(-30, 1000), (SW + 30, 1000), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix("#9a9076", P["shadow"], 0.2), shadow=0.2, seed=7101)
        cx, base = 1250, 1000
        # platform and walls of the vihara
        rect(ctx, cx - 620, base - 90, 1240, 90, mix("#d8ceb2", P["haze"], 0.1), 0.6, 7102)
        rect(ctx, cx - 520, base - 380, 1040, 290, mix("#e2d8bc", P["haze"], 0.1), 0.7, 7103)
        for k in range(8):   # columns + windows
            fill_rect(ctx, cx - 480 + k * 132, base - 370, 30, 280, mix("#c8bea2", P["shadow"], 0.1))
            if k < 7:
                fill_rect(ctx, cx - 430 + k * 132, base - 300, 50, 110, mix("#4a4236", P["shadow"], 0.2))
        # tiered roof with naga finials
        for i, (w, h, y) in enumerate(((1240, 170, base - 380), (920, 150, base - 540), (600, 130, base - 680))):
            sheet(ctx, path_poly([(cx - w / 2, y), (cx + w / 2, y), (cx + w / 2 - 120, y - h), (cx - w / 2 + 120, y - h)]),
                  mix(["#7a5a3a", "#6a4e32", "#5e442c"][i], P["shadow"], 0.1), shadow=0.6, seed=7104 + i)
            for sx in (-1, 1):
                ex = cx + sx * w / 2
                poly(ctx, [(ex, y), (ex + sx * 40, y - 70), (ex + sx * 10, y - 30)])
                src(ctx, "#b89a5a")
                ctx.fill()
        poly(ctx, [(cx - 30, base - 810), (cx, base - 960), (cx + 30, base - 810)])
        src(ctx, "#b89a5a")
        ctx.fill()
        # incense pot and candles before the steps (warm accent)
        fill_rect(ctx, cx - 70, base + 40, 140, 60, "#5a4a36")
        for k in range(5):
            fill_rect(ctx, cx - 50 + k * 25, base - 20, 4, 60, GOLD_PAINT)
        for k in range(6):
            fill_rect(ctx, cx - 380 + k * 34 if k < 3 else cx + 280 + (k - 3) * 34, base + 60, 12, 36, "#efe6cf")
        for i, xx in enumerate((200, 2250)):
            sugar_palm(ctx, P, xx, 1010, 400, 7110 + i)
        if refugees:
            for i, xx in enumerate((160, 420, 1880, 2140)):
                lean_to(ctx, xx, 1240 + (i % 2) * 30, 190, 7120 + i)

    layers = [(_key("pg_sky", tod=tod, v=V), sky_, 0.0), (_key("pg_wat", tod=tod, r=refugees, v=V), wat, 0.55)]

    def fx(ctx, t, d, dp):
        if dp != 0.55:
            return
        cx, base = 1250, 1000
        for k in range(6):
            x = cx - 380 + k * 34 if k < 3 else cx + 280 + (k - 3) * 34
            fl = 1 + 0.15 * math.sin(t * 9 + k)
            ctx.new_path()
            ellipse(ctx, x + 6, base + 52, 6 * fl, 12 * fl)
            src(ctx, GOLD_PAINT)
            ctx.fill()
            glow(ctx, x + 6, base + 50, 60, "#ffb060", 0.18)
        for k in range(5):   # incense smoke curls
            for j in range(8):
                u = ((t * 0.25 + j / 8) % 1.0)
                src(ctx, "#d8d0bc", 0.22 * (1 - u))
                ctx.new_path()
                ellipse(ctx, cx - 48 + k * 25 + math.sin(u * 6 + k) * 18, base - 30 - u * 260, 5 + u * 14, 5 + u * 10)
                ctx.fill()
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.55])


# ================================================================ MEKONG CONVOY
def make_mekong(tod="dusk", people=None, mouth_fn=None, convoy=True, smoke=True):
    P = _P(tod)

    def sky_(ctx):
        sky60(ctx, P, 0.55, (0.7, 0.36), 80, 7200, 2)

    def banks(ctx):
        PP.ridge(ctx, P, 760, 40, mix(P["far"], P["haze"], 0.3), 7201)
        sheet(ctx, path_poly([(-30, 740), (SW + 30, 760), (SW + 30, 820), (-30, 800)]), mix("#5a6248", P["mid"], 0.3),
              shadow=0.2, seed=7202)
        for i in range(14):
            sugar_palm(ctx, P, 60 + i * 175, 790 + (i % 3) * 8, 150 + (i % 4) * 30, 7203 + i)
        PP.water(ctx, P, 800, SH + 40, 7220, mix("#5a6a6a", P["water"], 0.5), 6)
        sheet(ctx, path_poly([(-30, 1200), (900, 1180), (1400, 1230), (SW + 30, 1210), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix("#6a6450", P["shadow"], 0.2), shadow=0.3, seed=7230)

    layers = [(_key("mk70_sky", tod=tod, v=V), sky_, 0.0), (_key("mk70_banks", tod=tod, v=V), banks, 0.55)]

    def barge(ctx, x, y, L, kind):
        if kind == "tug":
            sheet(ctx, path_poly([(x - L / 2, y), (x + L / 2, y), (x + L / 2 + 30, y - 40), (x - L / 2, y - 40)]),
                  "#4a4a44", shadow=0.4, seed=7240)
            rect(ctx, x - L * 0.2, y - 110, L * 0.35, 70, "#6a6a60", 0.4, 7241)
            fill_rect(ctx, x - L * 0.1, y - 150, 16, 40, "#3a3a34")
        else:
            sheet(ctx, path_poly([(x - L / 2, y), (x + L / 2, y), (x + L / 2 + 20, y - 46), (x - L / 2 - 20, y - 46)]),
                  "#5a564c", shadow=0.4, seed=7242)
            for k in range(int(L // 70)):   # sacks of rice / drums under tarpaulins
                fill_rect(ctx, x - L / 2 + 10 + k * 70, y - 86, 58, 40, "#8a8268" if kind == "rice" else "#6a6e5a")

    def fx(ctx, t, d, dp):
        if dp == 0.0 and smoke:
            for k in range(12):   # distant smoke on the far bank (no violence shown)
                u = ((t * 0.06 + k / 12) % 1.0)
                for x0 in (420, 1900):
                    src(ctx, P["haze"], 0.32 * (1 - u))
                    ctx.new_path()
                    ellipse(ctx, x0 + math.sin(u * 4 + k) * 30 + u * 90, 720 - u * 460, 30 + u * 100, 24 + u * 70)
                    ctx.fill()
        if dp == 0.55 and convoy:
            x0 = 1450 + t * 45
            for k, (kind, L) in enumerate((("tug", 260), ("rice", 520), ("fuel", 480), ("tug", 240), ("rice", 500))):
                barge(ctx, x0 - k * 620, 960 + (k % 2) * 40, L, kind)
                src(ctx, "#e8e4d8", 0.25)   # wake
                ctx.rectangle(x0 - k * 620 - L / 2 - 200, 962 + (k % 2) * 40, 200, 4)
                ctx.fill()
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.55])


# ================================================================ THE UNCLE'S WALL MAP
CAMBODIA = [(102.4, 14.5), (103.7, 14.5), (105.5, 14.3), (106.0, 13.9), (107.5, 13.6), (107.6, 12.3), (106.0, 10.5),
            (104.6, 10.4), (103.4, 11.0), (102.6, 12.3), (102.3, 13.4)]


def make_wallmap(tod="night", people=None, mouth_fn=None, lines=0):
    """Hand-drawn map pinned on the wall; `lines` pencil front lines, each closer to Phnom Penh."""
    P = _P(tod)
    MX, MY, MW, MH = 700, 230, 1100, 760

    from maps import merc_y, _shapes
    Y0, Y1 = merc_y(14.9), merc_y(10.0)

    def xy(lon, lat):
        return MX + (lon - 102.1) / 5.8 * MW, MY + (Y0 - merc_y(lat)) / (Y0 - Y1) * MH

    def xym(lon, my):
        return MX + (lon - 102.1) / 5.8 * MW, MY + (Y0 - my) / (Y0 - Y1) * MH

    def wall(ctx):
        fill_rect(ctx, -30, -30, SW + 60, SH + 60, mix("#6a6a5a", P["shadow"], 0.3))
        for k in range(30):
            fill_rect(ctx, k * 90, 0, 3, SH, mix("#5a5a4c", P["shadow"], 0.3))
        fill_rect(ctx, MX - 30, MY - 30, MW + 60, MH + 60, "#e8dfc4")
        rings = [rg for rec, rgs in _shapes("ne_50m_admin_0_countries") if rec.get("ADMIN") == "Cambodia" for rg in rgs]
        for rg in rings:
            q = [xym(*p) for p in rg]
            poly(ctx, q)
            src(ctx, "#d6cbaa")
            ctx.fill_preserve()
            src(ctx, "#2a2824")
            ctx.set_line_width(4)
            ctx.stroke()
        # Mekong + Tonle Sap river and lake, in pencil
        ctx.save()
        ctx.rectangle(MX - 30, MY - 30, MW + 60, MH + 60)
        ctx.clip()
        src(ctx, "#4a4a46", 0.8)
        ctx.set_line_width(3)
        for rec, rgs in _shapes("ne_50m_rivers_lake_centerlines"):
            if str(rec.get("name", "")).startswith(("Mekong", "Tonl")):
                for rg in rgs:
                    q = [xym(*p) for p in rg]
                    ctx.move_to(*q[0])
                    for p in q[1:]:
                        ctx.line_to(*p)
                    ctx.stroke()
        for rec, rgs in _shapes("ne_50m_lakes"):
            if "Tonl" in str(rec.get("name", "")):
                for rg in rgs:
                    poly(ctx, [xym(*p) for p in rg])
                    src(ctx, "#6a6a62", 0.8)
                    ctx.fill()
        ctx.restore()
        x, y = xy(104.92, 11.57)
        ctx.new_path()
        ctx.arc(x, y, 12, 0, 6.283)
        src(ctx, "#8a2a1a")
        ctx.fill()
        for (px, py) in ((MX - 10, MY - 10), (MX + MW + 10, MY - 10)):
            ctx.new_path()
            ctx.arc(px, py, 12, 0, 6.283)
            src(ctx, "#8a3a2a")
            ctx.fill()

    layers = [(_key("wm_wall", tod=tod, v=V), wall, 0.55)]
    rings = [1.9, 1.35, 0.9, 0.5][:lines]

    def fx(ctx, t, d, dp):
        if dp != 0.55:
            return
        cx, cy = xy(104.92, 11.57)
        for i, r in enumerate(rings):   # pencil front lines, drawn on during the shot
            prog = clamp((t - 0.8 - i * 0.9) / 1.6)
            if prog <= 0:
                continue
            R = rng(70 + i)
            ctx.new_path()
            n = 40
            for k in range(int(n * prog) + 1):
                a = k / n * 2 * math.pi
                rr = r * (1 + 0.18 * math.sin(a * 3 + i) + 0.05 * R.normal())
                p = (cx + math.cos(a) * rr * MW / 6.0, cy + math.sin(a) * rr * MH / 5.0 * 0.8)
                (ctx.line_to if k else ctx.move_to)(*p)
            src(ctx, "#2a2824", 0.35 if i < len(rings) - 1 else 0.85)
            ctx.set_line_width(3)
            ctx.set_dash([10, 6])
            ctx.stroke()
            ctx.set_dash([])
        glow(ctx, 300, 300, 500, "#ffb060", 0.10)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.55])
