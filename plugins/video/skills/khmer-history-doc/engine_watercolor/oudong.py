"""Oudong film sets (watercolor + ink + gold leaf), built on chaktomuk.py and longvek.py.
All scenes are artistic reconstructions.

  stupa(ctx, P, x, y, h, seed, style, door)          whitewashed royal stupa (chedei) with gold finial
  make_royal_hill(tod, view, ...)                     Phnom Preah Reach Troap
      view: far (rice fields and river, the ridge crowned by stupas) | crest (close row of stupas, a doorway)
            | stairs (naga stairway with pilgrims) | city (wooden royal city below the ridge)
  make_atharas(tod, ruined, people, mouth_fn)         Vihear Preah Atharas with its great standing Buddha
  make_loom(tod, people, mouth_fn)                    weaving hol under a stilt house
  make_crafts(tod, people, mouth_fn)                  silversmith's mat: animal-shaped betel boxes, hol cloth
  make_faiths(tod, people, mouth_fn)                  riverbank: a wooden mosque and a monastery side by side
  make_steamer(tod, mode, people, mouth_fn)           river below the hill; a steam gunboat arrives or leaves
  make_burning(tod, people, mouth_fn)                 war years: storm, burning stilt village, people fleeing
  extra living-panel kinds (patched into chaktomuk._content):
      wedding, voc_clash, chbab, two_courts, kakey, rebuild, coronation, hide_leaves
"""
import math

import cast
import chaktomuk as K
import longvek as LV
import paper as PP
import wc
from core import SH, SW, clamp, ellipse, glow, lin, mix, rng, shade, smooth, src
from paper import TOD, jag, path_ellipse, path_poly, sheet
from sets import F, _birds, _comb, _key, _mist, grp, people_dyn

V = "o2"
STUPA, STUPA_D, LICHEN, LACQUER, SAFFRON = "#ece4d4", "#c8bca8", "#6f7a62", "#8a2a1e", "#e08a2e"
HILL_G, MONSOON = "#5f7f4a", "#5e7286"

cast.CAST.update({
    "fr_officer": dict(cast.CAST["iberian"], km="មន្ត្រីបារាំង (គំនូរ)", en="French officer (stylised)",
                       hair="short", hair_c="#5a3a22", wrap=("robe", "#f0ece4"), top=("robe_top", "#f6f2ea")),
    "dutch": dict(cast.CAST["iberian"], km="ឈ្មួញហូឡង់ (គំនូរ)", en="Dutch merchant (stylised)", hair="short",
                  hair_c="#8a6a3a", wrap=("robe", "#2a2a30"), top=("robe_top", "#3a3a44")),
    "princess": dict(cast.CAST["c_dancer"], km="ព្រះនាង (គំនូរ)", en="Princess (stylised, seen from afar)",
                     wrap=("skirt_long", "#efe6d2", "stripes"), top=("sash", "#c9a34a")),
    "sister": dict(cast.CAST["c_woman"], km="ប្អូនស្រីកូនឥដ្ឋ", en="Kon Eth's sister (fictional)",
                   wrap=("skirt_long", "#8a2a1e", "stripes"), top=("sash", "#e08a2e")),
    "cham": dict(cast.CAST["c_man"], km="អ្នកភូមិចាម", en="Cham villager", hair="cloth_head", hair_c="#efe6d2",
                 wrap=("skirt_long", "#3f6a5a", "stripes")),
})


def _k(name, **kw):
    return _key(name, v=V, **kw)


# ---------------------------------------------------------------- stupas and the ridge
def stupa(ctx, P, x, y, h, seed=0, style=0, door=False, col=None, lichen=0.35):
    """A whitewashed royal stupa: stepped square base, bell (or tiered tower), ring spire and gold finial."""
    R = rng(seed)
    c = col or mix(STUPA, P["light"], 0.15)
    w = h * 0.42
    yb = y
    for i in range(3):   # stepped base
        bw, bh = w * (1 - 0.13 * i), h * 0.055
        sheet(ctx, path_poly([(x - bw / 2, yb), (x + bw / 2, yb), (x + bw / 2, yb - bh), (x - bw / 2, yb - bh)]),
              shade(c, -0.06 * (2 - i)), seed=seed + i, edge=(i == 0))
        wc.gold_line(ctx, path_poly([(x - bw / 2, yb - bh), (x + bw / 2, yb - bh)]), max(1.2, h * 0.004), 0.55)
        yb -= bh
    hb = h * (0.26 if style != 1 else 0.3)
    if style == 1:       # tiered square tower (prang-like)
        pts = []
        for i in range(5):
            ww = w * (0.34 - i * 0.045)
            pts += [(x - ww, yb - hb * i / 5), (x - ww, yb - hb * (i + 0.8) / 5), (x - ww * 0.88, yb - hb * (i + 1) / 5)]
        body = pts + [(2 * x - px_, py_) for px_, py_ in reversed(pts)]
    else:                # bell
        left = [(x - w * 0.36 * (1 - (u / 10) ** 1.7 * 0.62), yb - hb * u / 10) for u in range(11)]
        body = left + [(2 * x - px_, py_) for px_, py_ in reversed(left)]
    sheet(ctx, path_poly(body), c, seed=seed + 5)
    # soft shadow on the right half
    src(ctx, P["shadow"], 0.16)
    half = [(x, yb)] + [(px_, py_) for px_, py_ in body if px_ > x] + [(x, yb - hb)]
    ctx.new_path()
    ctx.move_to(*half[0])
    for p in half[1:]:
        ctx.line_to(*p)
    ctx.close_path()
    ctx.fill()
    if door:             # carved doorway niche at the foot of the bell
        dw, dh = w * 0.16, hb * 0.5
        ctx.new_path()
        ctx.move_to(x - dw, yb)
        ctx.line_to(x - dw, yb - dh * 0.65)
        ctx.curve_to(x - dw, yb - dh * 1.05, x + dw, yb - dh * 1.05, x + dw, yb - dh * 0.65)
        ctx.line_to(x + dw, yb)
        ctx.close_path()
        src(ctx, "#2a2018", 0.85)
        ctx.fill_preserve()
        src(ctx, wc.GOLD, 0.8)
        ctx.set_line_width(max(1.5, h * 0.006))
        ctx.stroke()
    yt = yb - hb
    hw = w * 0.15
    sheet(ctx, path_poly([(x - hw, yt), (x + hw, yt), (x + hw, yt - h * 0.05), (x - hw, yt - h * 0.05)]),
          shade(c, -0.05), seed=seed + 6)
    yt -= h * 0.05
    n = 7
    sp = h * (0.36 if style != 2 else 0.46)
    for i in range(n):   # ring spire
        rw = w * (0.13 - i * 0.014)
        sheet(ctx, path_ellipse(x, yt - sp * i / n - sp * 0.04, max(3, rw), sp / n * 0.55), shade(c, -0.03 * (i % 2)),
              seed=seed + 10 + i, edge=False, texture=False)
    tip = yt - sp
    wc.gold_leaf(ctx, path_poly([(x - w * 0.03, tip + h * 0.05), (x, tip - h * 0.07), (x + w * 0.03, tip + h * 0.05)]),
                 0.95, seed)
    if lichen:           # weathering: grey-green stains under the ledges
        for k in range(6):
            lx = x + (R.random() - 0.5) * w * 0.6
            ly = y - R.random() * h * 0.45
            src(ctx, LICHEN, lichen * 0.18)
            ellipse(ctx, lx, ly, w * (0.05 + 0.06 * R.random()), h * (0.02 + 0.05 * R.random()))
            ctx.fill()
    return tip - h * 0.07


def ridge_y(x, base=900, height=260):
    """Crest line of the royal ridge: a long low hill with two humps."""
    u = x / SW
    return base - height * (0.55 * math.exp(-((u - 0.38) / 0.2) ** 2) + 0.45 * math.exp(-((u - 0.68) / 0.16) ** 2)
                            + 0.12)


RIDGE_STUPAS = [(560, 0.75, 0), (760, 0.9, 1), (900, 1.15, 0), (1040, 0.8, 2), (1500, 0.9, 0), (1650, 1.2, 1),
                (1780, 0.8, 0)]


def ridge(ctx, P, base=900, height=260, s=1.0, seed=0, col=None, stupas=True, atharas=True):
    pts = [(-40, base + 60)] + [(x, ridge_y(x, base, height)) for x in range(-40, SW + 81, 40)] + [(SW + 40, base + 60)]
    sheet(ctx, path_poly(pts), col or mix(HILL_G, P["far"], 0.45), seed=seed)
    tips = []
    if atharas:          # Vihear Preah Atharas: a long hall on the first hump
        ax = 1240
        ay = ridge_y(ax, base, height) + 6
        sheet(ctx, path_poly([(ax - 90 * s, ay), (ax + 90 * s, ay), (ax + 80 * s, ay - 46 * s), (ax - 80 * s, ay - 46 * s)]),
              mix("#b89a7a", P["far"], 0.3), seed=seed + 1)
        sheet(ctx, path_poly([(ax - 100 * s, ay - 44 * s), (ax, ay - 92 * s), (ax + 100 * s, ay - 44 * s)]),
              mix("#7a3a22", P["far"], 0.35), seed=seed + 2)
    if stupas:
        for k, (x, sc, st) in enumerate(RIDGE_STUPAS):
            y = ridge_y(x, base, height) + 8
            tips.append((x, stupa(ctx, P, x, y, 120 * sc * s, seed + 20 + k, st, lichen=0.2)))
    return tips


def _glints(ctx, tips, t, d, a=1.0, sweep=True):
    """First light runs along the stupa finials from left to right."""
    for k, (x, y) in enumerate(tips):
        q = smooth((t / max(d, 1) * 1.6 - k * 0.12)) if sweep else 1.0
        if q > 0:
            glow(ctx, x, y, 40 + 30 * q, "#ffe6a0", 0.55 * q * a)


def _rice(ctx, P, y0, y1, seed=0):
    R = rng(seed)
    y = y0
    k = 0
    while y < y1:
        hh = 30 + k * 14
        col = mix(P["mid"], "#9ab85a", 0.3 + 0.3 * R.random())
        sheet(ctx, path_poly(jag([(-40, y), (SW + 40, y + 6)], 3, seed + k, 40) + [(SW + 40, y + hh), (-40, y + hh)]),
              col, seed=seed + k, edge=False)
        src(ctx, mix(P["water"], P["sky1"], 0.4), 0.35)
        ctx.rectangle(-40, y + hh - 5, SW + 80, 4)
        ctx.fill()
        y += hh
        k += 1


def _monks(t, x0=200, y=1180, h=300, n=4, vx=38, depth=0.6):
    return grp(depth, *[F(x0 - k * 150, y, h, "monk", "pot", 90, 3100 + k, vx=vx) for k in range(n)])


# ---------------------------------------------------------------- 1. THE ROYAL HILL
def make_royal_hill(tod="dawn", view="far", rain=0.0, smoke=0.0, mist=0.0, pilgrims=False, monks=False,
                    flags=False, survey=False, today=False, glint=True, build=False, people=None, mouth_fn=None):
    P = TOD[tod]
    store = {}

    def sky_(ctx):
        PP.sky(ctx, P, 0.55, (0.25, 0.42) if tod in ("dawn", "mist") else (0.72, 0.35), 60, 7, 3001)
        PP.clouds(ctx, P, 6 if tod in ("storm", "monsoon") else 4, (0.04, 0.28), 3002,
                  mix(P["sky0"], P["shadow"], 0.3) if tod in ("storm", "monsoon") or smoke else None)

    layers = [(_k("rh_sky", tod=tod, sm=smoke > 0), sky_, 0.0)]
    deps = [0.0]

    if view == "far":
        def far(ctx):
            store["tips"] = ridge(ctx, P, 780, 300, 1.6, 3010)
            K.forest_band(ctx, P, 820, 22, 110, 3011, mix(P["far"], P["mid"], 0.5))

        def mid(ctx):
            K._water_band(ctx, P, 860, 930, seed=31)
            _rice(ctx, P, 930, SH + 40, 3020)
            for k, x in enumerate((180, 620, 1880, 2260)):
                PP.palm(ctx, P, x, 990 + (k % 2) * 30, 260, "sugar", 3030 + k, mix(P["mid"], P["near"], 0.4))
        layers += [(_k("rh_far", tod=tod), far, 0.3), (_k("rh_mid", tod=tod), mid, 0.6)]
        deps += [0.3, 0.6]
        if not store:
            pass
    elif view == "crest":
        def far(ctx):
            K.forest_band(ctx, P, 900, 20, 200, 3040, mix(P["far"], P["haze"], 0.3))
            _water_band_far(ctx, P)

        def near(ctx):
            sheet(ctx, path_poly(jag([(-40, 1000), (SW + 40, 990)], 3, 3050, 40) + [(SW + 40, SH + 40), (-40, SH + 40)]),
                  mix("#b8a07a", P["mid"], 0.35), seed=3051)
            tips = []
            tips.append((450, stupa(ctx, P, 450, 1010, 620, 3060, 1)))
            tips.append((1950, stupa(ctx, P, 1950, 1010, 560, 3061, 2)))
            tips.append((1200, stupa(ctx, P, 1200, 1030, 900, 3062, 0, door=True)))
            store["tips"] = tips
            if survey:   # surveyor's tripod and staff
                src(ctx, "#3a2a1a")
                ctx.set_line_width(5)
                for dx in (-30, 0, 30):
                    ctx.move_to(1620, 1060)
                    ctx.line_to(1620 + dx, 1160)
                ctx.stroke()
                src(ctx, "#8a8a7a")
                ctx.rectangle(1600, 1046, 40, 18)
                ctx.fill()
        layers += [(_k("rh_cf", tod=tod), far, 0.3), (_k("rh_cn", tod=tod, sv=survey), near, 0.6)]
        deps += [0.3, 0.6]
    elif view == "stairs":
        def far(ctx):
            K.forest_band(ctx, P, 700, 20, 220, 3070, mix(P["far"], P["mid"], 0.4))
            tips = []
            for k, (x, s_) in enumerate(((1500, 0.9), (1800, 1.2), (2100, 0.8))):
                tips.append((x, stupa(ctx, P, x, 560 + k * 10, 360 * s_, 3071 + k, k % 3)))
            store["tips"] = tips

        def near(ctx):
            sheet(ctx, path_poly([(-40, SH + 40), (-40, 1000), (1300, 560), (SW + 40, 520), (SW + 40, SH + 40)]),
                  mix(HILL_G, P["mid"], 0.4), seed=3080)
            # stairway rising to the right with naga balustrades
            for i in range(26):
                u = i / 26
                x0, y0 = 300 + u * 1050, 1320 - u * 760
                sheet(ctx, path_poly([(x0 - 120, y0), (x0 + 120, y0 - 40), (x0 + 120, y0 - 70), (x0 - 120, y0 - 30)]),
                      shade("#c8b89a", -0.08 * (i % 2)), seed=3090 + i, edge=False, texture=False)
            for side in (-1, 1):
                ctx.new_path()
                ctx.move_to(300 + side * 140, 1320 - side * 20)
                ctx.line_to(1350 + side * 140, 560 - side * 20)
                src(ctx, "#4f7a5a")
                ctx.set_line_width(26)
                ctx.stroke()
                hx, hy = 300 + side * 140, 1320 - side * 20
                sheet(ctx, path_ellipse(hx, hy - 60, 46, 70), "#4f7a5a", seed=3120 + side)   # naga hood
            for k in range(6):
                K.tree(ctx, P, 1500 + k * 160, 980 + (k % 2) * 40, 300, 3130 + k, P["near"])
        layers += [(_k("rh_sf", tod=tod), far, 0.3), (_k("rh_sn", tod=tod), near, 0.6)]
        deps += [0.3, 0.6]
    else:   # city
        def far(ctx):
            store["tips"] = ridge(ctx, P, 640, 260, 0.85, 3140)
            K.forest_band(ctx, P, 700, 20, 140, 3141, mix(P["far"], P["mid"], 0.5))

        def mid(ctx):
            sheet(ctx, path_poly([(-40, 760), (SW + 40, 760), (SW + 40, SH + 40), (-40, SH + 40)]),
                  mix("#b8945a", P["mid"], 0.35), seed=3150)
            halls = ((1200, 900, 600, 3), (620, 900, 360, 2), (1780, 900, 360, 2), (260, 880, 220, 1),
                     (2150, 880, 240, 1))
            for k, (x, y, s_, tiers) in enumerate(halls):
                if build and k > 0:   # pillars only, being raised
                    for j in range(6):
                        px = x - s_ * 0.45 + j * s_ * 0.18
                        sheet(ctx, path_poly([(px - 8, y), (px + 8, y), (px + 8, y - s_ * 0.5), (px - 8, y - s_ * 0.5)]),
                              K.TEAK, seed=3160 + k * 10 + j)
                else:
                    K.wood_hall(ctx, P, x, y, s_, 3170 + k, tiers=tiers)
            if flags:
                for k in range(5):
                    fx_ = 300 + k * 450
                    src(ctx, "#3a2a1a")
                    ctx.set_line_width(5)
                    ctx.move_to(fx_, 960)
                    ctx.line_to(fx_, 700)
                    ctx.stroke()
        layers += [(_k("rh_cyf", tod=tod), far, 0.3), (_k("rh_cym", tod=tod, b=build, f=flags), mid, 0.6)]
        deps += [0.3, 0.6]

    def fx(ctx, t, d, depth):
        if depth == 0.3:
            if mist:
                _mist(ctx, t, 830 if view == "far" else 900, 180, P["haze"], mist * (1 - 0.5 * smooth(t / max(d, 1))), 3, 9)
            if view == "far" and tod in ("dawn", "mist", "day"):
                _birds(ctx, t, 300, 520, 6, "#f4f0e8", 26)
            if glint and tod in ("dawn", "golden", "dusk") and view in ("far", "city", "stairs"):
                _glints(ctx, _tips_for(view), t, d, 1.0, view == "far")
        if depth == 0.6:
            if view == "crest" and glint and tod in ("dawn", "golden", "dusk"):
                glow(ctx, 1200, stupa_top(1030, 900, 0), 70, "#ffe6a0", 0.5)
            if flags:
                for k in range(5):
                    fx_ = 300 + k * 450
                    wv = math.sin(t * 3 + k) * 8
                    sheet(ctx, path_poly([(fx_, 700), (fx_ + 90, 712 + wv), (fx_ + 80, 740 + wv), (fx_, 750)]),
                          ["#c9a34a", "#a4442e"][k % 2], seed=3190 + k, edge=False, texture=False)
            if smoke:
                for j in range(12):
                    ph = (t * 0.05 + j / 12) % 1
                    x = (j * 210 + t * 10) % SW
                    src(ctx, "#3a3438", 0.45 * smoke * (1 - ph))
                    ellipse(ctx, x, 880 - ph * 560, 80 + ph * 240, 50 + ph * 150)
                    ctx.fill()
            if rain:
                wc.rain(ctx, t, rain, 11)
    groups = list(people or [])
    if monks:
        groups.append(_monks(0, 100 if view != "crest" else 700, 1200 if view == "crest" else 1180,
                             280 if view == "crest" else 200, 4, 42))
    if pilgrims and view == "stairs":
        groups.append(grp(0.6, *[F(420 + k * 150, 1240 - k * 105, 170 - k * 6, ["c_woman", "c_man", "c_child"][k % 3],
                                   "walk_slow", 60, 3200 + k, vx=14, vy=-10) for k in range(5)]))
    return dict(layers=layers, dyn=_comb(fx, people_dyn(groups, P, mouth_fn)), dyn_depths=deps)


def _water_band_far(ctx, P):
    src(ctx, mix(P["water"], P["sky1"], 0.4), 0.6)
    ctx.rectangle(-40, 905, SW + 80, 30)
    ctx.fill()


def stupa_top(y, h, style=0):
    return y - h * (0.165 + (0.3 if style == 1 else 0.26) + 0.05 + (0.46 if style == 2 else 0.36) + 0.07)


def _tips_for(view):
    if view == "far":
        return [(x, stupa_top(ridge_y(x, 780, 300) + 8, 120 * sc * 1.6, st)) for x, sc, st in RIDGE_STUPAS]
    if view == "city":
        return [(x, stupa_top(ridge_y(x, 640, 260) + 8, 120 * sc * 0.85, st)) for x, sc, st in RIDGE_STUPAS]
    return [(x, stupa_top(560 + k * 10, 360 * s_, k % 3)) for k, (x, s_) in enumerate(((1500, 0.9), (1800, 1.2), (2100, 0.8)))]


# ---------------------------------------------------------------- 2. VIHEAR PREAH ATHARAS
def make_atharas(tod="golden", ruined=False, people=None, mouth_fn=None):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.6, (0.7, 0.3), 60, 7, 3301)
        K.forest_band(ctx, P, 1000, 16, 260, 3302, mix(P["far"], P["mid"], 0.4))

    def hall(ctx):
        wallc = mix("#c8a88a", P["light"], 0.1)
        sheet(ctx, path_poly([(-40, 1120), (SW + 40, 1120), (SW + 40, SH + 40), (-40, SH + 40)]), shade(wallc, -0.2),
              seed=3310)
        for k, x in enumerate((240, 560, 1840, 2160)):   # columns
            top = 260 if not ruined else 260 + (k * 173) % 360
            sheet(ctx, path_poly([(x - 55, 1120), (x + 55, 1120), (x + 50, top), (x - 50, top)]),
                  shade(wallc, -0.05 * (k % 2)), seed=3320 + k)
            if ruined:
                sheet(ctx, path_poly([(x - 60, top), (x + 60, top), (x + 40, top - 30), (x - 30, top - 20)]),
                      shade(wallc, -0.25), seed=3330 + k)
        if not ruined:
            sheet(ctx, path_poly([(-40, 260), (SW + 40, 260), (SW + 40, -40), (-40, -40)]), "#4a2a1a", seed=3340)
            sheet(ctx, path_poly([(-40, 300), (SW + 40, 300), (SW + 40, 240), (-40, 240)]), LACQUER, seed=3341)
        # the standing Buddha: plastered brick, robe folds, raised right hand, ushnisha
        cx, base = 1200, 1120
        sk = mix("#e4d6bc", P["light"], 0.15)
        sheet(ctx, path_poly([(cx - 260, base), (cx + 260, base), (cx + 230, base - 90), (cx - 230, base - 90)]),
              shade(sk, -0.15), seed=3350)   # pedestal
        sheet(ctx, path_poly([(cx - 150, base - 90), (cx + 150, base - 90), (cx + 125, base - 640), (cx + 95, base - 760),
                              (cx - 95, base - 760), (cx - 125, base - 640)]), sk, seed=3351)   # robe
        src(ctx, shade(sk, -0.3), 0.5)
        ctx.set_line_width(4)
        for k in range(7):
            ctx.move_to(cx - 110 + k * 36, base - 100)
            ctx.curve_to(cx - 100 + k * 34, base - 300, cx - 90 + k * 30, base - 500, cx - 70 + k * 23, base - 700)
        ctx.stroke()
        sheet(ctx, path_ellipse(cx, base - 830, 78, 92), sk, seed=3352)   # head
        sheet(ctx, path_ellipse(cx, base - 920, 40, 40), shade(sk, -0.1), seed=3353)   # ushnisha
        wc.gold_leaf(ctx, path_poly([(cx - 10, base - 950), (cx, base - 1010), (cx + 10, base - 950)]), 0.9, 1)
        for side in (-1, 1):   # ears and shoulders
            sheet(ctx, path_ellipse(cx + side * 82, base - 820, 16, 48), shade(sk, -0.08), seed=3354 + side)
        sheet(ctx, path_poly([(cx + 120, base - 640), (cx + 180, base - 520), (cx + 200, base - 600),
                              (cx + 160, base - 680)]), sk, seed=3356)   # raised hand (abhaya)
        src(ctx, "#2a1a10", 0.6)
        ctx.set_line_width(3)
        for side in (-1, 1):
            ctx.move_to(cx + side * 36, base - 840)
            ctx.line_to(cx + side * 14, base - 836)
        ctx.move_to(cx - 14, base - 790)
        ctx.curve_to(cx - 5, base - 784, cx + 5, base - 784, cx + 14, base - 790)
        ctx.stroke()
        if ruined:   # scars of 1977 repaired: lighter patches
            for k in range(5):
                src(ctx, "#fff8ec", 0.18)
                ellipse(ctx, cx - 80 + k * 40, base - 300 - k * 90, 40, 26)
                ctx.fill()

    layers = [(_k("ath_bg", tod=tod), bg, 0.2), (_k("ath_h", tod=tod, r=ruined), hall, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.6:
            for k in range(6):   # incense threads and candle glows at the pedestal
                x = 1000 + k * 80
                glow(ctx, x, 1060, 30, "#ffd890", 0.35 + 0.1 * math.sin(t * 3 + k))
                for j in range(4):
                    ph = (t * 0.12 + j / 4 + k * 0.13) % 1
                    src(ctx, "#efe8e0", 0.18 * (1 - ph))
                    ellipse(ctx, x + math.sin(t + j + ph * 6) * 20, 1050 - ph * 400, 10 + ph * 30, 16 + ph * 40)
                    ctx.fill()
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.2, 0.6])


# ---------------------------------------------------------------- 3. WEAVING HOL
def _hol_band(ctx, x0, y0, w, h, rows, t=0.0):
    cols = ("#8a2a1e", "#e08a2e", "#2f4a5a", "#c9a34a", "#5f7f4a")
    rh = h / max(rows, 1)
    for r in range(rows):
        for c in range(int(w / 40)):
            k = (r + c * 3 + (r // 3) * 2) % 5
            src(ctx, cols[k], 0.9)
            x = x0 + c * 40 + (6 if (r // 2) % 2 else 0)
            ctx.move_to(x, y0 - r * rh)
            ctx.line_to(x + 20, y0 - r * rh - rh * 0.5)
            ctx.line_to(x + 40, y0 - r * rh)
            ctx.line_to(x + 20, y0 - r * rh + rh * 0.5)
            ctx.close_path()
            ctx.fill()


def make_loom(tod="golden", people=None, mouth_fn=None):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.6, (0.75, 0.3), 60, 7, 3401)
        K.forest_band(ctx, P, 820, 16, 200, 3402, mix(P["far"], P["mid"], 0.4))
        K.stilt_house(ctx, P, 1900, 900, 320, 3403)

    def shed(ctx):
        sheet(ctx, path_poly([(-40, 1000), (SW + 40, 1000), (SW + 40, SH + 40), (-40, SH + 40)]),
              mix("#b8945a", P["mid"], 0.3), seed=3410)
        for x in (300, 1500):   # house posts and floor beams overhead
            sheet(ctx, path_poly([(x - 18, 1020), (x + 18, 1020), (x + 18, 200), (x - 18, 200)]), K.TEAK, seed=3411 + x)
        sheet(ctx, path_poly([(-40, 240), (SW + 40, 240), (SW + 40, 160), (-40, 160)]), shade(K.TEAK, -0.2), seed=3420)
        # loom frame
        src(ctx, "#5a3a22")
        ctx.set_line_width(14)
        for x in (620, 1260):
            ctx.move_to(x, 1060)
            ctx.line_to(x, 620)
        ctx.move_to(600, 640)
        ctx.line_to(1280, 640)
        ctx.move_to(600, 980)
        ctx.line_to(1280, 980)
        ctx.stroke()
        src(ctx, "#efe6d2", 0.7)   # warp threads
        ctx.set_line_width(1.2)
        for k in range(70):
            ctx.move_to(640 + k * 8.6, 650)
            ctx.line_to(640 + k * 8.6, 970)
        ctx.stroke()

    layers = [(_k("lm_bg", tod=tod), bg, 0.2), (_k("lm_s", tod=tod), shed, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.6:
            rows = int(6 + 10 * smooth(t / max(d, 1)))
            _hol_band(ctx, 640, 960, 600, 300, rows, t)
            bx = 640 + (math.sin(t * 2.2) * 0.5 + 0.5) * 560   # shuttle
            sheet(ctx, path_ellipse(bx, 960 - rows * 18.75, 30, 8), "#c9a34a", seed=3430, edge=False, texture=False)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.2, 0.6])


# ---------------------------------------------------------------- 4. SILVER AND SILK (craft mat)
def silver_animal(ctx, x, y, s, kind=0, seed=0):
    """An animal-shaped silver betel box (turtle, bird, rabbit, fish) with repousse dots."""
    def metal(path_fn):
        path_fn(ctx)
        ctx.set_source(lin(x, y - s, x, y, [(0, "#f4f6f8"), (0.5, "#b8bcc4"), (1, "#7a7e88")]))
        ctx.fill_preserve()
        src(ctx, "#4a4e58", 0.7)
        ctx.set_line_width(2)
        ctx.stroke()
    parts = {0: [(0, -0.35, 0.9, 0.38), (1.0, -0.3, 0.22, 0.16)],                       # turtle: shell, head
             1: [(0, -0.4, 0.75, 0.42), (0.75, -0.8, 0.22, 0.22), (-0.85, -0.55, 0.3, 0.12)],   # bird
             2: [(0, -0.4, 0.7, 0.42), (0.7, -0.75, 0.26, 0.24), (0.62, -1.15, 0.08, 0.25), (0.8, -1.15, 0.08, 0.25)],
             3: [(0, -0.35, 0.95, 0.3), (-1.05, -0.35, 0.22, 0.25)]}[kind % 4]          # fish, tail
    for (cx, cy, rx, ry) in parts:
        metal(path_ellipse(x + cx * s, y + cy * s, rx * s, ry * s))
    R = rng(seed)
    for k in range(18):
        src(ctx, "#ffffff", 0.5)
        ctx.arc(x + (R.random() - 0.5) * s * 1.2, y - s * (0.2 + R.random() * 0.4), 2.5, 0, 6.283)
        ctx.fill()


def make_crafts(tod="golden", people=None, mouth_fn=None):
    P = TOD[tod]

    def mat(ctx):
        ctx.set_source(lin(0, 0, 0, SH, [(0, "#6a4a2a"), (1, "#3a2414")]))
        ctx.paint()
        sheet(ctx, path_poly([(200, 420), (2200, 420), (2320, 1250), (80, 1250)]), "#c8a86a", seed=3501)   # woven mat
        src(ctx, "#8a6a3a", 0.35)
        ctx.set_line_width(3)
        for k in range(40):
            ctx.move_to(200 + k * 52, 420)
            ctx.line_to(80 + k * 58, 1250)
        ctx.stroke()
        for k in range(3):   # folded hol cloths
            x0, y0 = 1350 + k * 40, 1150 - k * 70
            sheet(ctx, path_poly([(x0, y0), (x0 + 760, y0), (x0 + 760, y0 - 120), (x0, y0 - 120)]), "#8a2a1e",
                  seed=3510 + k, edge=False, texture=False)
            ctx.save()
            ctx.rectangle(x0, y0 - 120, 760, 120)
            ctx.clip()
            _hol_band(ctx, x0, y0 - 6, 760, 120, 6)
            ctx.restore()

    layers = [(_k("cr_mat", tod=tod), mat, 0.5)]

    def fx(ctx, t, d, depth):
        for k, (x, y, s_, kind) in enumerate(((420, 900, 120, 0), (720, 800, 110, 1), (1000, 950, 100, 2),
                                              (560, 1120, 110, 3))):
            silver_animal(ctx, x, y, s_, kind, 3520 + k)
            glow(ctx, x + 30 * math.sin(t + k), y - s_ * 0.6, 26, "#ffffff", 0.25 + 0.2 * math.sin(t * 2 + k))
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.5])


# ---------------------------------------------------------------- 5. MANY FAITHS ON ONE RIVERBANK
def make_faiths(tod="golden", people=None, mouth_fn=None):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.55, (0.6, 0.3), 60, 7, 3601)
        PP.clouds(ctx, P, 4, (0.04, 0.25), 3602)

    def bank(ctx):
        K.forest_band(ctx, P, 760, 20, 170, 3610, mix(P["far"], P["mid"], 0.5))
        sheet(ctx, path_poly(jag([(-40, 800), (SW + 40, 805)], 3, 3611, 40) + [(SW + 40, 860), (-40, 860)]),
              mix("#b8945a", P["mid"], 0.4), seed=3612)
        # wooden mosque (left): hall with tiered roof and a square wooden minaret
        K.wood_hall(ctx, P, 620, 840, 420, 3620, tiers=2, gable=False, col="#9a6a40")
        mx = 360
        sheet(ctx, path_poly([(mx - 40, 840), (mx + 40, 840), (mx + 34, 420), (mx - 34, 420)]), "#9a6a40", seed=3621)
        sheet(ctx, path_poly([(mx - 60, 420), (mx + 60, 420), (mx, 340)]), "#7a3a22", seed=3622)
        sheet(ctx, path_ellipse(mx, 330, 14, 14), "#c9a34a", seed=3623)
        # monastery (right): hall and a stupa
        K.wood_hall(ctx, P, 1760, 840, 460, 3630, tiers=2)
        stupa(ctx, P, 2180, 850, 360, 3631, 0)

    def water(ctx):
        K._water_band(ctx, P, 860, seed=36)

    layers = [(_k("fa_sky", tod=tod), sky_, 0.0), (_k("fa_b", tod=tod), bank, 0.3), (_k("fa_w", tod=tod), water, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.6:
            PP.water_fx(ctx, t, P, 880, SH, 4, 14, 50)
            for k in range(3):
                K.boat(ctx, P, (k * 760 + t * 26) % (SW + 400) - 200, 1050 + k * 70, 300, 3640 + k, "canoe",
                       1 if k % 2 else -1, t, crew=2)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.3, 0.6])


# ---------------------------------------------------------------- 6. STEAMBOAT BELOW THE HILL
def steamer(ctx, P, x, y, L, t=0.0, f=1, seed=0, flag=True):
    """A small 1860s river steam gunboat: dark hull, white deckhouse, funnel, mast, smoke."""
    hull = [(x - L / 2, y - L * 0.06), (x + L / 2, y - L * 0.06), (x + L * 0.42 * f if f > 0 else x + L * 0.42, y + L * 0.02),
            (x - L * 0.42, y + L * 0.02)]
    hull = [(x - L * 0.5 * f, y - L * 0.07), (x + L * 0.55 * f, y - L * 0.07), (x + L * 0.44 * f, y + L * 0.03),
            (x - L * 0.46 * f, y + L * 0.03)]
    sheet(ctx, path_poly(hull), "#2a2a30", seed=seed)
    sheet(ctx, path_poly([(x - L * 0.3 * f, y - L * 0.07), (x + L * 0.2 * f, y - L * 0.07), (x + L * 0.2 * f, y - L * 0.16),
                          (x - L * 0.3 * f, y - L * 0.16)]), "#efe8dc", seed=seed + 1)
    fx_ = x - L * 0.02 * f
    sheet(ctx, path_poly([(fx_ - L * 0.025, y - L * 0.16), (fx_ + L * 0.025, y - L * 0.16), (fx_ + L * 0.025, y - L * 0.32),
                          (fx_ - L * 0.025, y - L * 0.32)]), "#1e1a17", seed=seed + 2)
    src(ctx, "#3a2a1a")
    ctx.set_line_width(max(2, L * 0.006))
    mx = x + L * 0.32 * f
    ctx.move_to(mx, y - L * 0.07)
    ctx.line_to(mx, y - L * 0.42)
    ctx.stroke()
    if flag:
        wv = math.sin(t * 3) * L * 0.01
        for k, c in enumerate(("#2f4a8a", "#f4f0e8", "#a4442e")):
            src(ctx, c)
            ctx.rectangle(mx - (k + 1) * L * 0.025 * f if f > 0 else mx + k * L * 0.025, y - L * 0.42 + wv, L * 0.025,
                          L * 0.045)
            ctx.fill()
    for j in range(8):   # smoke
        ph = (t * 0.25 + j / 8) % 1
        src(ctx, "#4a4448", 0.4 * (1 - ph))
        ellipse(ctx, fx_ - ph * L * 0.5 * f, y - L * 0.34 - ph * L * 0.25, L * (0.03 + ph * 0.08), L * (0.02 + ph * 0.05))
        ctx.fill()


def make_steamer(tod="golden", mode="arrive", people=None, mouth_fn=None):
    P = TOD[tod]
    store = {}

    def sky_(ctx):
        PP.sky(ctx, P, 0.55, (0.72, 0.35), 60, 7, 3701)
        PP.clouds(ctx, P, 4, (0.04, 0.28), 3702)

    def far(ctx):
        store["tips"] = ridge(ctx, P, 700, 240, 0.8, 3710)
        K.forest_band(ctx, P, 760, 22, 120, 3711, mix(P["far"], P["mid"], 0.5))
        sheet(ctx, path_poly(jag([(-40, 790), (SW + 40, 795)], 3, 3712, 40) + [(SW + 40, 810), (-40, 810)]),
              mix(K.RIVER, P["mid"], 0.5), seed=3713)

    def water(ctx):
        K._water_band(ctx, P, 810, seed=37)

    layers = [(_k("st_sky", tod=tod), sky_, 0.0), (_k("st_far", tod=tod), far, 0.3), (_k("st_w", tod=tod), water, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.3 and tod in ("golden", "dusk"):
            _glints(ctx, _tips_city(), t, d, 0.6, False)
        if depth == 0.6:
            PP.water_fx(ctx, t, P, 830, SH, 4, 14, 50)
            if mode == "arrive":
                steamer(ctx, P, -300 + t * 120, 1000, 760, t, 1, 3720)
            else:
                steamer(ctx, P, 1300 + t * 110, 980, 640, t, 1, 3721)
                for k in range(3):
                    K.boat(ctx, P, 300 + k * 260 + t * 20, 1120 + k * 40, 260, 3730 + k, "canoe", 1, t, crew=2)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.3, 0.6])


def _tips_city():
    return [(x, stupa_top(ridge_y(x, 700, 240) + 8, 120 * sc * 0.8, st)) for x, sc, st in RIDGE_STUPAS]


# ---------------------------------------------------------------- 7. YEARS OF CRISIS
def make_burning(tod="storm", people=None, mouth_fn=None, fire=1.0, rain=0.7):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.55, (0.5, 0.3), 60, 7, 3801)
        PP.clouds(ctx, P, 7, (0.02, 0.32), 3802, mix(P["sky0"], P["shadow"], 0.35))

    def village(ctx):
        K.forest_band(ctx, P, 780, 20, 170, 3810, mix(P["far"], P["mid"], 0.5))
        sheet(ctx, path_poly(jag([(-40, 800), (SW + 40, 805)], 3, 3811, 40) + [(SW + 40, SH + 40), (-40, SH + 40)]),
              mix("#8a7a5a", P["mid"], 0.4), seed=3812)
        for k, x in enumerate((300, 700, 1150, 1600, 2050)):
            K.stilt_house(ctx, P, x, 900 + (k % 2) * 30, 260, 3820 + k)

    layers = [(_k("bn_sky", tod=tod), sky_, 0.0), (_k("bn_v", tod=tod), village, 0.5)]

    def fx(ctx, t, d, depth):
        if depth == 0.5:
            for k, x in enumerate((700, 1600)):
                glow(ctx, x, 820, 260, "#ff8a30", 0.35 * fire * (0.8 + 0.2 * math.sin(t * 5 + k)))
                for j in range(10):
                    ph = (t * 0.08 + j / 10) % 1
                    src(ctx, "#2e2a2e", 0.5 * (1 - ph) * fire)
                    ellipse(ctx, x + math.sin(j + t * 0.3) * 60 + ph * 200, 780 - ph * 600, 60 + ph * 200, 40 + ph * 130)
                    ctx.fill()
                for j in range(16):
                    ph = (t * 0.35 + j / 16) % 1
                    src(ctx, "#ffb050", 0.8 * (1 - ph) * fire)
                    ctx.arc(x - 120 + (j * 37) % 240, 850 - ph * 420, 3, 0, 6.283)
                    ctx.fill()
            if rain:
                wc.rain(ctx, t, rain, 13)
    groups = list(people or [])
    groups.append(grp(0.5, *[F(2300 - k * 170, 1180 + (k % 2) * 40, 230, ["c_woman", "c_man", "c_child"][k % 3],
                               "carry_shoulder" if k % 3 == 1 else "walk", -90, 3830 + k, vx=-60, sil=P["shadow"])
                             for k in range(5)]))
    return dict(layers=layers, dyn=_comb(fx, people_dyn(groups, P, mouth_fn)), dyn_depths=[0.0, 0.5])


# ---------------------------------------------------------------- 8. EXTRA LIVING-PANEL KINDS
def ship(ctx, P, x, y, L, t=0.0, f=1, seed=0, sails=True):
    """A 17th-century European ship (VOC style), simplified."""
    sheet(ctx, path_poly([(x - L * 0.5 * f, y - L * 0.16), (x + L * 0.45 * f, y - L * 0.1), (x + L * 0.38 * f, y + L * 0.04),
                          (x - L * 0.36 * f, y + L * 0.04), (x - L * 0.5 * f, y - L * 0.22)]), "#5a3a22", seed=seed)
    src(ctx, "#3a2a1a")
    ctx.set_line_width(max(2, L * 0.008))
    for k, mx in enumerate((-0.22, 0.02, 0.24)):
        x0 = x + mx * L * f
        ctx.move_to(x0, y - L * 0.12)
        ctx.line_to(x0, y - L * (0.75 - 0.1 * (k == 2)))
        ctx.stroke()
        if sails:
            for j in range(2):
                yy = y - L * (0.28 + j * 0.24)
                bl = math.sin(t * 1.5 + k + j) * L * 0.01
                sheet(ctx, path_poly([(x0 - L * 0.09, yy), (x0 + L * 0.09, yy), (x0 + L * 0.1 + bl, yy + L * 0.18),
                                      (x0 - L * 0.1 + bl, yy + L * 0.18)]), "#efe6d2", seed=seed + k * 3 + j, edge=False)


_prev_content = K._content


def _content(kind, P):
    gy = 1040
    if kind == "wedding":     # Vietnamese tradition: a princess arrives by boat; figures distant and stylised
        figs = [F(1800 + k * 120, gy, 280, "c_noble", "bow", -60, 4000 + k) for k in range(2)]

        def props(ctx, P, t):
            K._water_band(ctx, P, 940, 1060, seed=40)
            bx = 600 + t * 40
            K.boat(ctx, P, bx, 990, 820, 4010, "barge", 1, t, crew=6)
            cast.draw(ctx, bx - 40, 950, 130, "princess", "sit", t, 180, None, P, cutout=False)
            for k in range(3):   # parasols and banners
                src(ctx, "#3a2a1a")
                ctx.set_line_width(4)
                ctx.move_to(bx - 200 + k * 160, 960)
                ctx.line_to(bx - 200 + k * 160, 760)
                ctx.stroke()
                sheet(ctx, path_ellipse(bx - 200 + k * 160, 760, 60, 20), ["#c9a34a", "#a4442e"][k % 2],
                      seed=4020 + k, edge=False)
        return figs, props
    if kind == "voc_clash":   # VOC records: the Dutch fleet defeated on the river, 1644 (stylised)
        def props(ctx, P, t):
            K._water_band(ctx, P, 900, 1060, seed=41)
            ship(ctx, P, 1550 - t * 10, 1000, 560, t, -1, 4030)
            for k in range(4):
                K.boat(ctx, P, 300 + k * 230 + t * (30 + k * 4), 980 + (k % 2) * 50, 360, 4040 + k, "war", 1, t, crew=7)
            for j in range(10):
                ph = (t * 0.2 + j / 10) % 1
                src(ctx, "#4a4448", 0.4 * (1 - ph))
                ellipse(ctx, 1450 + j * 20, 800 - ph * 300, 40 + ph * 120, 30 + ph * 80)
                ctx.fill()
        return [], props
    if kind == "chbab":       # Chbab: a child bows to the parents; a teacher reads the verse
        figs = [F(700, gy, 300, "c_man", "sit", 60, 4050), F(900, gy, 290, "c_woman", "sit", 60, 4051),
                F(1250, gy, 200, "c_child", "kneel_pray", -60, 4052), F(1750, gy, 340, "monk", "read", -40, 4053)]
        return figs, None
    if kind == "two_courts":  # rival princes turn toward two foreign courts
        figs = [F(1000, gy, 360, "c_king", "point", -90, 4060), F(1400, gy, 360, "c_king", "point", 90, 4061)]

        def props(ctx, P, t):
            K.wood_hall(ctx, P, 420, gy, 420, 4062, tiers=3, col="#8a6a4a")
            K.wood_hall(ctx, P, 1980, gy, 420, 4063, tiers=2, col="#6a5a4a")
        return figs, props
    if kind == "kakey":       # verse novel Kakey: the queen carried over the sea by a giant Garuda-bird
        def props(ctx, P, t):
            K._water_band(ctx, P, 900, 1060, seed=42)
            bx, by = 600 + t * 80, 560 + math.sin(t * 0.8) * 30
            fl = math.sin(t * 2.5)
            for side in (-1, 1):
                sheet(ctx, path_poly([(bx, by), (bx + side * 380, by - 160 - fl * 80), (bx + side * 420, by - 60 - fl * 40),
                                      (bx + side * 120, by + 40)]), "#c9a34a", seed=4070 + side, edge=False)
            sheet(ctx, path_ellipse(bx, by, 120, 60), "#a4442e", seed=4072)
            sheet(ctx, path_ellipse(bx + 140, by - 40, 40, 34), "#a4442e", seed=4073)
            cast.draw(ctx, bx - 20, by - 40, 160, "c_dancer", "sit", t, 90, None, P, cutout=False)
            K.boat(ctx, P, 1800, 990, 300, 4074, "canoe", -1, t, crew=1)
        return [], props
    if kind == "rebuild":     # Ang Duong's revival: a bridge and a monastery hall being raised
        figs = [F(500 + k * 200, gy, 280, "c_man", "carry_shoulder", 90, 4080 + k, vx=12) for k in range(3)]

        def props(ctx, P, t):
            K._water_band(ctx, P, 980, 1060, seed=43)
            sheet(ctx, path_poly([(1300, 960), (2050, 960), (2050, 930), (1300, 930)]), K.TEAK, seed=4090)   # bridge deck
            for k in range(6):
                x = 1330 + k * 140
                sheet(ctx, path_poly([(x - 8, 1050), (x + 8, 1050), (x + 8, 930), (x - 8, 930)]), shade(K.TEAK, -0.2),
                      seed=4091 + k)
            K.wood_hall(ctx, P, 1700, 900, 420 * (0.5 + 0.5 * smooth(t / 8)), 4099, tiers=2)
        return figs, props
    if kind == "coronation":  # 1864 coronation at Oudong: king from behind, French and Siamese representatives
        figs = [F(1200, gy, 360, "c_king", "sit", 180, 4100)]
        figs += [F(500 + k * 140, gy, 300, "fr_officer", "stand", 60, 4110 + k) for k in range(2)]
        figs += [F(1750 + k * 140, gy, 300, "c_noble", "bow", -60, 4120 + k) for k in range(2)]

        def props(ctx, P, t):
            src(ctx, "#4a3420")
            ctx.set_line_width(6)
            ctx.move_to(1260, gy - 160)
            ctx.line_to(1260, gy - 560)
            ctx.stroke()
            for k in range(5):
                w = 170 - k * 30
                yy = gy - 560 + k * 26
                sheet(ctx, path_poly([(1260 - w, yy), (1260 + w, yy), (1260 + w * 0.4, yy - 50), (1260 - w * 0.4, yy - 50)]),
                      shade("#efe6d2", -0.06 * k), seed=4130 + k)
        return figs, props
    if kind == "hide_leaves":  # Kon Eth hides palm-leaf bundles inside a stupa (closing of chapter 8)
        figs = [F(900, gy, 420, "eth", "carry_box", 60, 11)]

        def props(ctx, P, t):
            stupa(ctx, P, 1500, gy, 700, 4140, 0, door=True)
            for k in range(3):
                sheet(ctx, path_poly([(1440 + k * 30, gy - 60 - k * 18), (1560 + k * 10, gy - 60 - k * 18),
                                      (1560 + k * 10, gy - 76 - k * 18), (1440 + k * 30, gy - 76 - k * 18)]),
                      K.LEAF, seed=4150 + k, edge=False)
        return figs, props
    return _prev_content(kind, P)


K._content = _content


def make_mural(kind, tod="golden", alive=(0.15, 0.35, 0.82, 0.96), legend=False, mouth_fn=None):
    """Living mural: a painted monastery wall (plaster, lacquer-red border) whose scene comes to life."""
    sc = K.make_relief(kind, "wood", tod, alive, legend, mouth_fn)
    x0, y0, x1, y1 = K.PANEL

    def wall(ctx):
        ctx.set_source(lin(0, 0, 0, SH, [(0, "#3a2418"), (1, "#20140c")]))
        ctx.paint()
        sheet(ctx, path_poly([(x0 - 110, y0 - 110), (x1 + 110, y0 - 110), (x1 + 110, y1 + 110), (x0 - 110, y1 + 110)]),
              "#e8dcc4", seed=4200)
        wc._tex(ctx, "bloom", 0.35, 4, 1.5)
        for k, (pad, col, w) in enumerate(((-60, LACQUER, 26), (-30, wc.GOLD, 6))):
            src(ctx, col, 0.9)
            ctx.set_line_width(w)
            ctx.rectangle(x0 + pad, y0 + pad, x1 - x0 - 2 * pad, y1 - y0 - 2 * pad)
            ctx.stroke()
        src(ctx, "#f2e8d4")
        ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
        ctx.fill()
    sc["layers"] = [(_k("mural"), wall, 0.5)]
    return sc
