"""Chaktomuk film sets and cast (watercolor + ink + gold leaf).  All scenes are artistic reconstructions.
Set space is SW x SH = 2400 x 1350; ground / water line is around y = 900-1000.

  make_angkor_dusk(people, mouth_fn)                     Angkor Wat at dusk from the moat, a few lamps, one monk
  make_river(tod, mode, rain, people, mouth_fn)          wide river; mode: procession | trade | war | race | quiet
  make_confluence(tod, labels, people, mouth_fn)         the four arms of water meeting (oblique aerial)
  make_workshop(tod, carved, people, mouth_fn)           riverside carving shed with a new teak pillar
  make_hill(tod, shrine, people, mouth_fn)               Daun Penh's small hill with a shrine
  make_palace(tod, decay, people, mouth_fn)              wooden palace on raised earthworks, dike and canal
  make_wat(tod, people, mouth_fn)                        wooden monastery: monks teaching boys
  make_market(tod, people, mouth_fn)                     riverside market with a junk offshore
  make_floodplain(tod, falling, people, mouth_fn)        stilt houses; water level falls over the shot, rice appears
  make_modern(tod)                                       Phnom Penh riverfront today with Wat Phnom (painted)
  make_reversal()                                        schematic: Tonle Sap flow reversal
  make_relief(kind, panel, tod, alive, legend)           living manuscript (palm leaf) or living carved teak panel
"""
import math

import cast
import paper as PP
import wc
from core import (EN_SERIF, KM_SANS, SH, SW, clamp, draw_text, ellipse, glow, lin, mix, poly, rad, rng, shade,
                  smooth, src)
from paper import TOD, jag, path_ellipse, path_poly, sheet
from sets import F, _birds, _comb, _key, _mist, grp, people_dyn

V = "k2"
RIVER, SAFFRON, LOTUS, TEAK, TEAK_L, LEAF, GOLD = (wc.WC["river"], wc.WC["saffron"], wc.WC["lotus"], wc.WC["teak"],
                                                    wc.WC["teak_l"], wc.WC["leaf"], wc.GOLD)
SAND = "#b9a39b"

cast.CAST.update({
    "eth": dict(km="កូនឥដ្ឋ", en="Kon Eth (fictional guide)", era="chaktomuk", B=cast.CHILD, skin="b", hair="short",
                hair_c="#15100c", wrap=("skirt_knee", "#8a5a32", "stripes"), top=("sash", "#e08a2e"),
                orn=["bronze_bangle"], face=dict(brow=0.75, jaw=0.86, nose=0.85, lips=1.05, child=True)),
    "father": dict(km="ជាងឈើ", en="Master woodcarver", era="chaktomuk", B=cast.ADULT_M, skin="a", hair="cloth_head",
                   hair_c="#a4442e", wrap=("skirt_knee", "#5a3a22", "stripes"), orn=[],
                   face=dict(brow=1.2, jaw=1.05, nose=1.1, beard=True)),
    "c_king": dict(km="ស្ដេច (គំនូរ)", en="King (stylised, no portrait)", era="chaktomuk", B=cast.ADULT_M, skin="c",
                   hair="topknot", hair_c="#c9a34a", wrap=("skirt_long", "#a4442e", "stripes"), top=("sash", "#c9a34a"),
                   orn=["gold_ear", "gold_neck", "bronze_bangle"], face=dict(brow=1.0, jaw=1.0, nose=1.0)),
    "c_noble": dict(km="មន្ត្រី", en="Official", era="chaktomuk", B=cast.ADULT_M, skin="b", hair="topknot",
                    hair_c="#16110d", wrap=("skirt_long", "#c9743a", "stripes"), top=("sash", "#efe6d2"),
                    orn=["gold_ear"], face=dict(brow=1.1, jaw=1.0, nose=1.0)),
    "c_man": dict(km="អ្នកភូមិ", en="Villager", era="chaktomuk", B=cast.ADULT_M, skin="e", hair="tied_back",
                  hair_c="#16110d", wrap=("skirt_knee", "#5e7286", "stripes"), orn=[], face=dict(brow=1.2, jaw=1.1, nose=1.1)),
    "c_woman": dict(km="ស្ត្រីអ្នកភូមិ", en="Village woman", era="chaktomuk", B=cast.ADULT_F, skin="c", hair="bun",
                    hair_c="#15100c", wrap=("skirt_long", "#a4442e", "stripes"), orn=["gold_ear"],
                    face=dict(brow=0.8, jaw=0.92, nose=0.95, lips=1.1)),
    "trader": dict(km="ឈ្មួញស្រី", en="Woman trader", era="chaktomuk", B=cast.ADULT_F, skin="d", hair="bun",
                   hair_c="#15100c", wrap=("skirt_long", "#c9743a", "stripes"), orn=["gold_ear"],
                   face=dict(brow=0.8, jaw=0.92, nose=0.95, lips=1.1)),
    "daunpenh": dict(cast.CAST["f_grandma"], km="ដូនពេញ (រឿងព្រេង)", en="Daun Penh (legend)",
                     wrap=("skirt_long", "#efe6d2", "stripes"), top=("poncho", "#e08a2e")),
    "c_soldier": dict(km="ទាហាន", en="Soldier", era="chaktomuk", B=cast.ADULT_M, skin="b", hair="cloth_head",
                      hair_c="#a4442e", wrap=("skirt_knee", "#5a3a22", "stripes"), orn=[],
                      face=dict(brow=1.3, jaw=1.1, nose=1.05)),
    "c_child": dict(km="ក្មេង", en="Child", era="chaktomuk", B=cast.CHILD, skin="c", hair="short", hair_c="#16110d",
                    wrap=("loin", "#c9743a"), orn=[], face=dict(brow=0.7, jaw=0.85, nose=0.8, child=True)),
    "c_dancer": dict(km="អ្នករាំ", en="Dancer", era="chaktomuk", B=cast.ADULT_F, skin="d", hair="bun",
                     hair_c="#15100c", wrap=("skirt_long", "#c9a34a", "stripes"), top=("sash", "#a4442e"),
                     orn=["gold_ear", "gold_neck", "bronze_bangle"], face=dict(brow=0.8, jaw=0.9, nose=0.95, lips=1.1)),
})


def _k(name, **kw):
    return _key(name, v=V, **kw)


# ---------------------------------------------------------------- vegetation and buildings
def tree(ctx, P, x, y, h, seed=0, col=None):
    R = rng(seed)
    c = col or P["near"]
    tw = h * 0.045
    lean = (R.random() - 0.5) * h * 0.08
    sheet(ctx, path_poly([(x - tw, y), (x - tw * 0.6 + lean, y - h * 0.62), (x + tw * 0.6 + lean, y - h * 0.62),
                          (x + tw, y)]), mix("#4a3a2a", c, 0.25), seed=seed)
    for i in range(9):
        a = -math.pi * (0.1 + 0.8 * R.random())
        rr = h * (0.18 + 0.12 * R.random())
        cx = x + lean + math.cos(a) * h * 0.22 * R.random() * 1.6
        cy = y - h * 0.7 + math.sin(a) * h * 0.18
        pts = [(cx + math.cos(k / 14 * 6.283) * rr * (0.8 + 0.3 * R.random()),
                cy + math.sin(k / 14 * 6.283) * rr * 0.75 * (0.8 + 0.3 * R.random())) for k in range(14)]
        sheet(ctx, path_poly(pts, True), mix(c, P["light"], 0.12 * R.random() + (0.1 if i > 6 else 0)), seed=seed + i,
              edge=(i % 3 == 0))


def forest_band(ctx, P, y, n, h0, seed, col, x0=-80, x1=None):
    x1 = x1 or SW + 80
    R = rng(seed)
    gap = (x1 - x0) / n
    for i in range(n):
        tree(ctx, P, x0 + i * gap + R.random() * gap * 0.6, y + R.random() * 20, h0 * (0.8 + 0.4 * R.random()),
             seed + i * 7, mix(col, P["haze"], 0.1 * R.random()))


def wood_hall(ctx, P, x, y, s, seed=0, tiers=2, gable=True, col=None):
    """Khmer wooden hall on pillars: platform, pillar row, stacked roofs with upswept finials and carved gable."""
    wood = col or TEAK
    sheet(ctx, path_poly([(x - s * 0.62, y), (x + s * 0.62, y), (x + s * 0.62, y - s * 0.12), (x - s * 0.62, y - s * 0.12)]),
          shade(wood, -0.25), seed=seed)
    fy = y - s * 0.12
    for k in range(7):
        px = x - s * 0.54 + k * s * 0.18
        sheet(ctx, path_poly([(px - s * 0.018, fy), (px + s * 0.018, fy), (px + s * 0.018, fy - s * 0.5),
                              (px - s * 0.018, fy - s * 0.5)]), shade(wood, -0.1 + 0.05 * (k % 2)), seed=seed + k,
              edge=False)
    sheet(ctx, path_poly([(x - s * 0.58, fy - s * 0.5), (x + s * 0.58, fy - s * 0.5), (x + s * 0.58, fy - s * 0.56),
                          (x - s * 0.58, fy - s * 0.56)]), wood, seed=seed + 9)
    ry = fy - s * 0.56
    for t in range(tiers):
        w = s * (0.78 - t * 0.2)
        h = s * (0.32 - t * 0.04)
        roof = mix("#7a3a22", P["light"], 0.08 * t)
        sheet(ctx, path_poly([(x - w, ry), (x - w * 0.15, ry - h), (x + w * 0.15, ry - h), (x + w, ry)]), roof,
              seed=seed + 20 + t)
        for side in (-1, 1):   # upswept finials (chovea)
            ex = x + side * w
            ctx.new_path()
            ctx.move_to(ex, ry)
            ctx.curve_to(ex + side * s * 0.05, ry - s * 0.02, ex + side * s * 0.07, ry - s * 0.08, ex + side * s * 0.05,
                         ry - s * 0.12)
            src(ctx, GOLD, 0.95)
            ctx.set_line_width(max(2, s * 0.012))
            ctx.stroke()
        ry -= h * 0.62
    if gable:   # carved gable triangle with gold edge
        gy = fy - s * 0.56
        tri = [(x - s * 0.22, gy - 4), (x, gy - s * 0.3), (x + s * 0.22, gy - 4)]
        sheet(ctx, path_poly(tri), shade(wood, 0.1), seed=seed + 40)
        wc.gold_line(ctx, path_poly(tri), max(1.5, s * 0.006), 0.9)
        src(ctx, shade(wood, -0.45), 0.6)
        ctx.set_line_width(1.5)
        for k in range(4):
            ctx.new_path()
            ctx.arc(x, gy - s * 0.1, s * (0.03 + k * 0.02), math.pi, 2 * math.pi)
            ctx.stroke()


def stilt_house(ctx, P, x, y, s, seed=0):
    PP.stilt_house(ctx, P, x, y, s, seed)


def boat(ctx, P, x, y, L, seed=0, kind="canoe", f=1, t=0.0, lantern=False, crew=0, who="c_man"):
    """River boats: canoe | barge (royal, with roofed pavilion) | race (long, many paddlers) | junk (Chinese) | war."""
    bob = math.sin(t * 1.3 + seed) * L * 0.006
    y = y + bob
    if kind == "junk":
        hull = [(x - L * 0.5 * f, y - L * 0.12), (x - L * 0.42 * f, y + L * 0.03), (x + L * 0.42 * f, y + L * 0.03),
                (x + L * 0.52 * f, y - L * 0.16), (x + L * 0.45 * f, y - L * 0.08), (x - L * 0.45 * f, y - L * 0.07)]
        sheet(ctx, path_poly(hull, True), "#5a3a22", seed=seed)
        for k, (mx, mh) in enumerate(((-0.15, 0.6), (0.12, 0.5))):
            px = x + L * mx * f
            src(ctx, "#3a2a1a")
            ctx.set_line_width(L * 0.008)
            ctx.move_to(px, y - L * 0.07)
            ctx.line_to(px, y - L * mh)
            ctx.stroke()
            sail = [(px - L * 0.02 * f, y - L * (mh - 0.02)), (px + L * 0.2 * f, y - L * (mh - 0.05)),
                    (px + L * 0.18 * f, y - L * 0.14), (px - L * 0.02 * f, y - L * 0.12)]
            sheet(ctx, path_poly(sail), "#b8946a" if k else "#a8845a", seed=seed + 5 + k)
            src(ctx, "#6a4a2a", 0.6)
            ctx.set_line_width(1.6)
            for j in range(6):
                u = (j + 1) / 7
                ctx.move_to(sail[0][0] + (sail[3][0] - sail[0][0]) * u, sail[0][1] + (sail[3][1] - sail[0][1]) * u)
                ctx.line_to(sail[1][0] + (sail[2][0] - sail[1][0]) * u, sail[1][1] + (sail[2][1] - sail[1][1]) * u)
            ctx.stroke()
        return
    long_ = {"canoe": 1.0, "barge": 1.1, "race": 1.6, "war": 1.3}.get(kind, 1.0)
    hull = [(x - L * 0.5 * long_ * f, y - L * 0.07), (x - L * 0.4 * long_ * f, y + L * 0.03),
            (x + L * 0.4 * long_ * f, y + L * 0.03), (x + L * 0.52 * long_ * f, y - L * 0.1),
            (x + L * 0.44 * long_ * f, y - L * 0.02), (x - L * 0.44 * long_ * f, y - L * 0.01)]
    col = {"barge": "#7a2e1e", "race": "#a4442e", "war": "#3a2a1a"}.get(kind, "#6a4a2a")
    sheet(ctx, path_poly(hull, True), col, seed=seed)
    if kind in ("barge", "race"):
        wc.gold_line(ctx, path_poly([(x - L * 0.44 * long_ * f, y - L * 0.02), (x + L * 0.44 * long_ * f, y - L * 0.03)]),
                     2.5, 0.9)
        ctx.new_path()   # naga prow
        hx = x + L * 0.52 * long_ * f
        ctx.move_to(hx, y - L * 0.1)
        ctx.curve_to(hx + L * 0.05 * f, y - L * 0.2, hx - L * 0.02 * f, y - L * 0.26, hx + L * 0.04 * f, y - L * 0.3)
        src(ctx, GOLD, 0.95)
        ctx.set_line_width(L * 0.02)
        ctx.stroke()
    if kind == "barge":
        sheet(ctx, path_poly([(x - L * 0.12, y - L * 0.02), (x + L * 0.12, y - L * 0.02), (x + L * 0.12, y - L * 0.16),
                              (x - L * 0.12, y - L * 0.16)]), "#c9743a", seed=seed + 3)
        sheet(ctx, path_poly([(x - L * 0.18, y - L * 0.16), (x + L * 0.18, y - L * 0.16), (x + L * 0.06, y - L * 0.26),
                              (x - L * 0.06, y - L * 0.26)]), "#7a3a22", seed=seed + 4)
    n = crew or {"race": 12, "war": 8, "barge": 6}.get(kind, 0)
    for k in range(n):
        ox = x - L * 0.36 * long_ * f + k * (L * 0.72 * long_ / max(1, n - 1)) * f
        ph = math.sin(t * (4.0 if kind == "race" else 2.0) + k * 0.15 + seed)
        src(ctx, "#2a1a10", 0.95)
        ellipse(ctx, ox, y - L * 0.08, L * 0.018, L * 0.03)
        ctx.fill()
        ctx.set_line_width(L * 0.006)
        ctx.move_to(ox, y - L * 0.06)
        ctx.line_to(ox - L * 0.03 * f + ph * L * 0.025 * f, y + L * 0.08)
        ctx.stroke()
    if lantern:
        lx = x + L * 0.3 * long_ * f
        glow(ctx, lx, y - L * 0.14, L * 0.25, "#ffc070", 0.5 + 0.1 * math.sin(t * 7 + seed))
        src(ctx, "#ffe2a0", 0.95)
        ellipse(ctx, lx, y - L * 0.14, L * 0.015, L * 0.022)
        ctx.fill()


def lotus_tower(ctx, P, x, yb, h, w, col, seed=0):
    prof = [(0.0, 1.0), (0.18, 1.08), (0.4, 1.12), (0.62, 0.95), (0.8, 0.62), (0.93, 0.3), (1.0, 0.0)]
    left = [(x - w * r, yb - h * u) for u, r in prof]
    right = [(x + w * r, yb - h * u) for u, r in reversed(prof[:-1])]
    sheet(ctx, path_poly(left + right, smooth=True), col, seed=seed)


def angkor_wat(ctx, P, cx, base_y, s=1.0, col=None, seed=0):
    col = col or mix(SAND, P["shadow"], 0.38)
    for j, (w0, hh) in enumerate(((760, 60), (600, 70), (430, 80))):
        yb = base_y - j * 70 * s
        sheet(ctx, path_poly([(cx - w0 * s, yb), (cx + w0 * s, yb), (cx + (w0 - 14) * s, yb - hh * s),
                              (cx - (w0 - 14) * s, yb - hh * s)]), shade(col, 0.04 * j), seed=seed + j)
    top = base_y - 210 * s
    for k, (dx, h, w) in enumerate(((-370, 250, 48), (370, 250, 48), (-180, 300, 56), (180, 300, 56), (0, 430, 72))):
        lotus_tower(ctx, P, cx + dx * s, top + (0 if k == 4 else 40 * s), h * s, w * s, shade(col, 0.05 * (k % 2)),
                    seed + 10 + k)


def _water_band(ctx, P, y0, y1=SH + 40, col=None, seed=0):
    c = col or mix(RIVER, P["water"], 0.45)
    ctx.set_source(lin(0, y0, 0, y1, [(0, mix(c, P["sky1"], 0.3)), (1, mix(c, P["shadow"], 0.25))]))
    ctx.rectangle(-40, y0, SW + 80, y1 - y0)
    ctx.fill()
    wc._tex(ctx, "bloom", 0.35, seed % 4 + 1, 1.6)


# ---------------------------------------------------------------- 1. ANGKOR WAT AT DUSK (half-empty)
def make_angkor_dusk(people=None, mouth_fn=None, tod="dusk"):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.6, (0.62, 0.42), 60, 7, 101)
        PP.clouds(ctx, P, 4, (0.05, 0.25), 102)

    def temple(ctx):
        forest_band(ctx, P, 820, 10, 200, 110, mix(P["far"], P["mid"], 0.4), x0=-80, x1=420)
        forest_band(ctx, P, 820, 10, 200, 120, mix(P["far"], P["mid"], 0.4), x0=1980, x1=SW + 80)
        angkor_wat(ctx, P, 1200, 830, 1.0, seed=111)

    def moat(ctx):
        _water_band(ctx, P, 860, col=mix("#4f7f96", P["water"], 0.5), seed=3)
        ctx.save()
        ctx.rectangle(0, 862, SW, SH - 862)
        ctx.clip()
        ctx.translate(0, 860 * 2 + 4)
        ctx.scale(1, -1)
        angkor_wat(ctx, P, 1200, 830, 1.0, col=mix("#4f7f96", P["sky1"], 0.25), seed=111)
        ctx.restore()
        src(ctx, mix("#4f7f96", P["sky1"], 0.4), 0.5)
        ctx.rectangle(0, 860, SW, SH - 860)
        ctx.fill()
        sheet(ctx, path_poly(jag([(-40, 852), (SW + 40, 856)], 2, 130, 40) + [(SW + 40, 868), (-40, 868)]),
              mix(wc.WC["laterite"], P["mid"], 0.5), seed=131)
        for i in range(5):
            PP.lotus(ctx, P, 260 + i * 470, 1220 + (i % 2) * 40, 55, 0.5, 140 + i)

    layers = [(_k("ad_sky"), sky_, 0.0), (_k("ad_t"), temple, 0.35), (_k("ad_m"), moat, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.35:
            _birds(ctx, t, 500, 320, 6, P["shadow"])
            for k, x in enumerate((900, 1500)):   # a few lamps still burning
                fl = 0.8 + 0.2 * math.sin(t * 8 + k)
                glow(ctx, x, 800, 60 * fl, "#ffc070", 0.55)
            cast.draw(ctx, 1320, 830, 70, "monk" if "monk" in cast.CAST else "c_man", "walk_slow",
                      t, -90, None, P, cutout=False)
        if depth == 0.6:
            PP.water_fx(ctx, t, P, 880, 1180, 8, 10, 40)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.35, 0.6])


# ---------------------------------------------------------------- 2. THE RIVER
def make_river(tod="night", mode="procession", rain=0.0, people=None, mouth_fn=None, moon=False):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.55, (0.75, 0.25) if moon or tod == "night" else (0.3, 0.42), 55, 7, 201)
        PP.clouds(ctx, P, 6 if tod == "storm" else 4, (0.04, 0.3), 202,
                  mix(P["sky0"], P["shadow"], 0.3) if tod == "storm" else None)
        if tod == "night":
            R = rng(203)
            for k in range(120):
                src(ctx, "#f6eed8", 0.3 + 0.5 * R.random())
                ctx.arc(R.random() * SW, R.random() * SH * 0.5, 0.8 + R.random() * 1.5, 0, 6.283)
                ctx.fill()

    def banks(ctx):
        forest_band(ctx, P, 760, 22, 170, 210, mix(P["far"], P["mid"], 0.5))
        sheet(ctx, path_poly(jag([(-40, 780), (SW + 40, 785)], 3, 211, 40) + [(SW + 40, 800), (-40, 800)]),
              mix(RIVER, P["mid"], 0.5), seed=212)
        for k, x in enumerate((220, 640, 1900, 2250)):
            stilt_house(ctx, P, x, 800, 100, 213 + k)
        for k, x in enumerate((420, 1100, 2080)):
            PP.palm(ctx, P, x, 800, 300, "sugar", 220 + k, mix(P["mid"], P["near"], 0.4))

    def water(ctx):
        _water_band(ctx, P, 800, seed=5)

    layers = [(_k("rv_sky", tod=tod, m=moon), sky_, 0.0), (_k("rv_b", tod=tod), banks, 0.3),
              (_k("rv_w", tod=tod), water, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.0 and moon:
            glow(ctx, SW * 0.75, SH * 0.25, 240, "#fff4d8", 0.35)
        if depth == 0.6:
            PP.water_fx(ctx, t, P, 820, SH, 4, 16 if mode != "race" else 30, 60)
            lam = tod in ("night", "dusk") or moon
            if mode == "procession":
                for k in range(5):
                    x = (k * 520 + t * 40) % (SW + 800) - 400
                    boat(ctx, P, x, 1000 + (k % 2) * 90, 360 if k != 2 else 460, 300 + k,
                         "barge" if k == 2 else "canoe", 1, t, lantern=lam, crew=3)
            elif mode == "trade":
                boat(ctx, P, 1500 + t * 10, 930, 520, 310, "junk", -1, t)
                for k in range(3):
                    boat(ctx, P, (k * 700 + t * 30) % (SW + 400) - 200, 1100 + k * 40, 300, 320 + k, "canoe", 1, t, crew=2)
            elif mode == "war":
                for k in range(4):
                    boat(ctx, P, (k * 560 + t * 60) % (SW + 600) - 300, 960 + (k % 2) * 120, 420, 330 + k, "war",
                         1 if k % 2 else -1, t, crew=8)
            elif mode == "race":
                for k in range(3):
                    boat(ctx, P, 300 + t * (160 + k * 15), 960 + k * 120, 520, 340 + k, "race", 1, t, lantern=moon)
            if rain:
                wc.rain(ctx, t, rain, 9)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.3, 0.6])


# ---------------------------------------------------------------- 3. THE CONFLUENCE (oblique aerial)
def make_confluence(tod="dawn", labels=False, city=True, people=None, mouth_fn=None):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.38, (0.78, 0.22), 60, 7, 401)
        PP.clouds(ctx, P, 4, (0.03, 0.2), 402)

    def land(ctx):
        ctx.set_source(lin(0, 480, 0, SH, [(0, mix(P["far"], P["mid"], 0.4)), (1, mix(P["mid"], P["near"], 0.3))]))
        ctx.rectangle(-40, 480, SW + 80, SH)
        ctx.fill()
        wc._tex(ctx, "bloom", 0.4, 2, 2.0)
        water = mix(RIVER, P["water"], 0.4)
        arms = [  # upper Mekong (from back-right), Tonle Sap (back-left), lower Mekong (front-right), Bassac (front-left)
            [(1450, 480), (1640, 480), (1420, 820), (1250, 830)],
            [(700, 480), (820, 480), (1180, 800), (1080, 840)],
            [(1300, 860), (1500, 840), (2400, 1350), (1950, 1350)],
            [(1150, 870), (1250, 900), (950, 1350), (650, 1350)],
        ]
        for k, pts in enumerate(arms):
            sheet(ctx, path_poly(pts, True), mix(water, P["sky1"], 0.12 * (k % 2)), seed=410 + k, edge=False)
        sheet(ctx, path_ellipse(1250, 850, 230, 70), water, seed=415, edge=False)   # the meeting basin
        # the little hill (Phnom) with a shrine on the west bank
        sheet(ctx, path_ellipse(820, 960, 110, 50), mix(P["mid"], P["near"], 0.3), seed=420)
        sheet(ctx, path_poly([(800, 930), (840, 930), (840, 905), (820, 885), (800, 905)]), SAND, seed=421)
        if city:   # wooden capital on the west bank
            for k in range(7):
                x = 500 + (k % 4) * 120
                y = 760 + (k // 4) * 80
                sheet(ctx, path_poly([(x - 40, y), (x + 40, y), (x + 20, y - 34), (x - 20, y - 34)]), "#7a3a22", seed=430 + k)
            wood = [(380, 820), (700, 830), (760, 880), (420, 900)]
            src(ctx, wc.WC["laterite"], 0.35)
            poly(ctx, wood)
            ctx.fill()
        for k in range(14):   # floodplain fields
            x, y = 1700 + (k % 5) * 120, 600 + (k // 5) * 60
            sheet(ctx, path_poly([(x, y), (x + 100, y + 6), (x + 96, y + 50), (x - 4, y + 44)]),
                  mix("#8aa060", "#c8b46a", (k % 3) * 0.3), seed=440 + k, edge=False)

    layers = [(_k("cf_sky", tod=tod), sky_, 0.0), (_k("cf_l", tod=tod, c=city), land, 0.5)]

    def fx(ctx, t, d, depth):
        if depth == 0.5:
            PP.water_fx(ctx, t, P, 860, 1300, 4, 12, 40)
            for k in range(4):
                bx = (900 + k * 300 + t * (20 + k * 6)) % 1600 + 500
                boat(ctx, P, bx, 1000 + k * 70, 120, 450 + k, "canoe", 1 if k % 2 else -1, t)
            if labels:
                for k, (x, y, km, en) in enumerate(((1560, 560, "ទន្លេមេគង្គខាងលើ", "Upper Mekong"),
                                                    (740, 560, "ទន្លេសាប", "Tonle Sap"),
                                                    (2000, 1180, "ទន្លេមេគង្គខាងក្រោម", "Lower Mekong"),
                                                    (720, 1200, "ទន្លេបាសាក់", "Bassac"))):
                    a = smooth((t - 0.8 - k * 0.7) / 0.6)
                    if a <= 0:
                        continue
                    draw_text(ctx, km, x, y, 40, "#fff4dc", "mc", a, shadow=0.9, font=KM_SANS, weight="Bold")
                    draw_text(ctx, en, x, y + 44, 30, "#f1d98c", "mc", a, shadow=0.9, font=EN_SERIF, weight="SemiBold")
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.5])


# ---------------------------------------------------------------- 4. RIVERSIDE CARVING WORKSHOP
def make_workshop(tod="dawn", carved=1.0, people=None, mouth_fn=None, angkor=False):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.55, (0.72, 0.36), 60, 7, 501)
        if angkor:
            angkor_wat(ctx, P, 600, 760, 0.45, seed=502)
        forest_band(ctx, P, 780, 16, 170, 503, mix(P["far"], P["mid"], 0.5))
        _water_band(ctx, P, 790, 930, seed=7)
        sheet(ctx, path_poly(jag([(-40, 930), (SW + 40, 925)], 3, 504, 40) + [(SW + 40, SH + 40), (-40, SH + 40)]),
              mix(RIVER, "#b8945a", 0.5), seed=505)

    def shed(ctx):
        for x in (850, 2150):
            sheet(ctx, path_poly([(x - 12, 1260), (x + 12, 1260), (x + 12, 560), (x - 12, 560)]), "#5a4028", seed=x)
        pts = jag([(760, 620), (1500, 470), (2280, 610)], 6, 9, 30)
        sheet(ctx, path_poly(pts + [(2300, 560), (1500, 400), (740, 560)]), "#b8945a", seed=510)
        R = rng(511)
        for k in range(60):   # wood shavings
            x, y = 1100 + R.random() * 900, 1200 + R.random() * 120
            src(ctx, TEAK_L, 0.8)
            ctx.new_path()
            ctx.arc(x, y, 6 + R.random() * 6, R.random() * 3, R.random() * 3 + 2.5)
            ctx.set_line_width(2)
            ctx.stroke()
        for k in range(3):    # timber stack
            sheet(ctx, path_poly([(1850, 1250 - k * 40), (2250, 1250 - k * 40), (2250, 1215 - k * 40), (1850, 1215 - k * 40)]),
                  shade(TEAK, 0.06 * k), seed=520 + k)

    layers = [(_k("ws_bg", tod=tod, a=angkor), bg, 0.25), (_k("ws_shed", tod=tod), shed, 0.7)]

    def fx(ctx, t, d, depth):
        if depth == 0.7:   # the new teak pillar with a lotus emerging as he carves
            px, top, bot = 1560, 640, 1260
            sheet(ctx, path_poly([(px - 46, bot), (px + 46, bot), (px + 46, top), (px - 46, top)]), TEAK, seed=530,
                  texture=True)
            ctx.save()
            ctx.rectangle(px - 46, top, 92, bot - top)
            ctx.clip()
            wc._tex(ctx, "grain", 0.7, 2, 1.0)
            ctx.restore()
            c = clamp(carved * (0.3 + 0.7 * smooth(t / max(d, 1))))
            cy = 860
            for k in range(7):
                if k / 7 > c:
                    break
                a = -math.pi / 2 + (k - 3) * 0.32
                L = 70 * (0.8 + 0.2 * (1 - abs(k - 3) / 3))
                tx, ty = px + math.cos(a) * L * 0.6, cy + math.sin(a) * L
                ctx.new_path()
                ctx.move_to(px, cy + 20)
                ctx.curve_to(px + math.cos(a - 0.4) * L * 0.4, cy + math.sin(a - 0.4) * L * 0.6, tx, ty, tx, ty)
                ctx.curve_to(tx, ty, px + math.cos(a + 0.4) * L * 0.4, cy + math.sin(a + 0.4) * L * 0.6, px, cy + 20)
                src(ctx, shade(TEAK, 0.25 if k % 2 else 0.12))
                ctx.fill_preserve()
                src(ctx, shade(TEAK, -0.5), 0.8)
                ctx.set_line_width(1.6)
                ctx.stroke()
            if c > 0.9:
                wc.gold_line(ctx, path_poly([(px - 40, cy + 30), (px + 40, cy + 30)]), 2, 0.9)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.25, 0.7])


# ---------------------------------------------------------------- 5. DAUN PENH'S HILL
def make_hill(tod="mist", shrine=True, people=None, mouth_fn=None):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.55, (0.3, 0.3), 60, 7, 601)
        forest_band(ctx, P, 800, 18, 160, 602, mix(P["far"], P["mid"], 0.5))
        _water_band(ctx, P, 820, 960, seed=8)

    def hill(ctx):
        pts = [(400, 1100)]
        for k in range(21):
            u = k / 20
            pts.append((400 + u * 1600, 1100 - math.sin(u * math.pi) ** 1.4 * 330))
        pts += [(2000, 1100)]
        sheet(ctx, path_poly(pts, True), mix(P["mid"], P["near"], 0.3), seed=610)
        for k in range(8):
            tree(ctx, P, 520 + k * 190, 1060 - math.sin((k + 0.5) / 8 * math.pi) ** 1.4 * 250, 160, 620 + k, P["near"])
        if shrine:   # small wooden shrine (legend) on the summit
            wood_hall(ctx, P, 1200, 790, 200, 630, tiers=1)
        sheet(ctx, path_poly([(-40, 1100), (SW + 40, 1100), (SW + 40, SH + 40), (-40, SH + 40)]),
              mix(RIVER, "#b8945a", 0.5), seed=640)

    layers = [(_k("hl_bg", tod=tod), bg, 0.25), (_k("hl_h", tod=tod, s=shrine), hill, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.25:
            _mist(ctx, t, 860, 160, P["haze"], 0.5, 3, 8)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.25, 0.6])


# ---------------------------------------------------------------- 6. WOODEN PALACE ON EARTHWORKS
def make_palace(tod="golden", decay=0.0, people=None, mouth_fn=None):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.55, (0.7, 0.3), 60, 7, 701)
        forest_band(ctx, P, 760, 18, 170, 702, mix(P["far"], P["mid"], 0.5))
        _water_band(ctx, P, 780, 860, seed=9)

    def site(ctx):
        sheet(ctx, path_poly([(-40, 860), (SW + 40, 860), (SW + 40, 900), (-40, 900)]), shade(wc.WC["laterite"], -0.1),
              seed=710)   # dike
        sheet(ctx, path_poly([(300, 1000), (2100, 1000), (2000, 900), (400, 900)]), mix(wc.WC["laterite"], "#b8945a", 0.4),
              seed=711)   # raised earthwork
        sheet(ctx, path_poly([(-40, 1000), (SW + 40, 1000), (SW + 40, 1060), (-40, 1060)]), mix(RIVER, P["water"], 0.5),
              seed=712, edge=False)   # canal
        sheet(ctx, path_poly([(-40, 1060), (SW + 40, 1060), (SW + 40, SH + 40), (-40, SH + 40)]), mix(P["mid"], "#b8945a", 0.4),
              seed=713)
        if decay < 0.5:
            wood_hall(ctx, P, 1200, 910, 640, 720, tiers=3)
            wood_hall(ctx, P, 620, 920, 360, 730, tiers=2)
            wood_hall(ctx, P, 1790, 920, 360, 740, tiers=2)
        else:   # only posts and the earth mound remain
            for k in range(9):
                x = 760 + k * 110
                h = 60 + (k * 37) % 90
                sheet(ctx, path_poly([(x - 10, 905), (x + 10, 905), (x + 8, 905 - h), (x - 8, 905 - h)]), shade(TEAK, -0.3),
                      seed=750 + k)

    layers = [(_k("pl_bg", tod=tod), bg, 0.25), (_k("pl_s", tod=tod, d=decay >= 0.5), site, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.6:
            PP.water_fx(ctx, t, P, 1005, 1055, 6, 8, 16)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.25, 0.6])


# ---------------------------------------------------------------- 7. WOODEN MONASTERY
def make_wat(tod="day", people=None, mouth_fn=None, lesson=True):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.55, (0.25, 0.3), 60, 7, 801)
        forest_band(ctx, P, 800, 16, 200, 802, mix(P["far"], P["mid"], 0.5))
        wood_hall(ctx, P, 1700, 900, 560, 803, tiers=2)
        sheet(ctx, path_poly([(560, 900), (680, 900), (660, 760), (640, 700), (620, 640), (600, 700), (580, 760)]),
              "#e8e0d0", seed=804)   # small whitewashed stupa
        wc.gold_leaf(ctx, path_ellipse(620, 636, 8, 14), 0.9, 1)

    def ground(ctx):
        sheet(ctx, path_poly(jag([(-40, 900), (SW + 40, 905)], 3, 810, 40) + [(SW + 40, SH + 40), (-40, SH + 40)]),
              mix("#c8b48a", P["mid"], 0.3), seed=811)
        # open sala: platform and roof
        sheet(ctx, path_poly([(700, 1180), (1500, 1180), (1500, 1140), (700, 1140)]), shade(TEAK, -0.2), seed=812)
        for x in (720, 1480):
            sheet(ctx, path_poly([(x - 10, 1140), (x + 10, 1140), (x + 10, 860), (x - 10, 860)]), TEAK, seed=813 + x)
        sheet(ctx, path_poly([(640, 870), (1560, 870), (1300, 760), (900, 760)]), "#7a3a22", seed=815)

    layers = [(_k("wt_bg", tod=tod), bg, 0.25), (_k("wt_g", tod=tod), ground, 0.6)]
    cls = [] if not lesson else [grp(0.6, F(1000, 1140, 300, "monk", "sit_talk", 40, 820),
                                     *[F(1180 + k * 90, 1150, 170, "c_child", "sit", -50, 821 + k) for k in range(3)])]
    return dict(layers=layers, dyn=people_dyn(cls + (people or []), P, mouth_fn), dyn_depths=[0.25, 0.6])


# ---------------------------------------------------------------- 8. RIVERSIDE MARKET
def make_market(tod="golden", people=None, mouth_fn=None):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.5, (0.3, 0.3), 60, 7, 901)
        _water_band(ctx, P, 740, 880, seed=10)
        forest_band(ctx, P, 740, 10, 140, 902, mix(P["far"], P["mid"], 0.5))
        for k, x in enumerate((300, 2150)):
            wood_hall(ctx, P, x, 880, 260, 903 + k, tiers=1, gable=False)

    def ground(ctx):
        sheet(ctx, path_poly(jag([(-40, 880), (SW + 40, 885)], 3, 910, 40) + [(SW + 40, SH + 40), (-40, SH + 40)]),
              mix(wc.WC["laterite"], "#b8945a", 0.5), seed=911)
        for k, x in enumerate((450, 1000, 1550, 2050)):
            sheet(ctx, path_poly([(x - 170, 1150), (x + 170, 1150), (x + 190, 1210), (x - 190, 1210)]), "#c8a878", seed=920 + k)
            R = rng(930 + k)
            for j in range(10):
                c = ["#3f6fa8", "#efe6d2", "#c9743a", "#5a7a3a", "#a4442e"][j % 5]
                sheet(ctx, path_ellipse(x - 140 + R.random() * 280, 1165 + R.random() * 25, 22, 14), c, seed=940 + j,
                      edge=False)

    layers = [(_k("mk_bg", tod=tod), bg, 0.25), (_k("mk_g", tod=tod), ground, 0.6)]
    crowd = [grp(0.6, F(450, 1150, 250, "trader", "sit_talk", 20, 950), F(1000, 1150, 250, "zh_envoy", "talk", -20, 951),
                 F(1550, 1150, 250, "trader", "sit", 20, 952), F(2050, 1150, 250, "in_merchant", "offer", -20, 953),
                 F(760, 1270, 270, "c_man", "carry_shoulder", 90, 954, vx=25),
                 F(1300, 1280, 260, "c_woman", "carry_pot_head", -90, 955, vx=-20))]

    def fx(ctx, t, d, depth):
        if depth == 0.25:
            boat(ctx, P, 1300 + t * 6, 820, 380, 960, "junk", -1, t)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(crowd + (people or []), P, mouth_fn)), dyn_depths=[0.25, 0.6])


# ---------------------------------------------------------------- 9. FLOODPLAIN: water falls, rice appears
def make_floodplain(tod="day", falling=True, people=None, mouth_fn=None):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.5, (0.7, 0.3), 60, 7, 1001)
        forest_band(ctx, P, 760, 18, 150, 1002, mix(P["far"], P["mid"], 0.5))
        sheet(ctx, path_poly([(-40, 800), (SW + 40, 800), (SW + 40, SH + 40), (-40, SH + 40)]), mix("#8aa060", "#c8b46a", 0.3),
              seed=1003)
        R = rng(1004)
        src(ctx, "#4a6a2a", 0.7)
        ctx.set_line_width(2.5)
        for k in range(500):
            x, y = R.random() * SW, 820 + R.random() * 520
            ctx.move_to(x, y)
            ctx.line_to(x - 4, y - 18 - (y - 800) * 0.04)
            ctx.move_to(x, y)
            ctx.line_to(x + 5, y - 16 - (y - 800) * 0.04)
        ctx.stroke()

    def houses(ctx):
        for k, x in enumerate((300, 900, 1650, 2200)):
            stilt_house(ctx, P, x, 930 + (k % 2) * 20, 150, 1010 + k)

    layers = [(_k("fp_bg", tod=tod), bg, 0.3), (_k("fp_h", tod=tod), houses, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.3:
            q = smooth(t / max(d, 1)) if falling else 0.0
            lvl = 790 + q * 480
            ctx.rectangle(-40, lvl, SW + 80, SH + 40 - lvl)
            ctx.set_source(lin(0, lvl, 0, SH, [(0, mix(RIVER, P["water"], 0.4), 0.92), (1, mix(RIVER, P["shadow"], 0.3), 0.95)]))
            ctx.fill()
            PP.water_fx(ctx, t, P, lvl + 10, SH, 3, 10, 30)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.3, 0.6])


# ---------------------------------------------------------------- 10. MODERN PHNOM PENH RIVERFRONT (closing)
def make_modern(tod="dusk"):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.6, (0.62, 0.48), 80, 7, 1101)
        PP.clouds(ctx, P, 4, (0.05, 0.25), 1102)

    def city(ctx):
        col = mix(P["shadow"], P["far"], 0.4)
        R = rng(1103)
        x = -40
        while x < SW + 40:   # modern skyline silhouette
            w = 60 + R.random() * 120
            h = 80 + R.random() * 260
            sheet(ctx, path_poly([(x, 830), (x + w, 830), (x + w, 830 - h), (x, 830 - h)]), shade(col, 0.05 * R.random()),
                  seed=int(x) + 1110, edge=False)
            x += w + 10
        # Wat Phnom: hill, vihara roofs and the tall white stupa
        sheet(ctx, path_ellipse(700, 840, 260, 90), mix(P["near"], col, 0.4), seed=1120)
        wood_hall(ctx, P, 640, 780, 200, 1121, tiers=2, col="#e8d8b8")
        sheet(ctx, path_poly([(770, 790), (830, 790), (815, 680), (805, 600), (800, 560), (795, 600), (785, 680)]),
              "#efe6d6", seed=1122)
        _water_band(ctx, P, 860, seed=11)
        sheet(ctx, path_poly([(-40, 860), (SW + 40, 860), (SW + 40, 880), (-40, 880)]), shade(col, -0.2), seed=1130)

    layers = [(_k("md_sky", tod=tod), sky_, 0.0), (_k("md_c", tod=tod), city, 0.5)]

    def fx(ctx, t, d, depth):
        if depth == 0.5:
            for k in range(24):   # promenade lamps
                glow(ctx, 60 + k * 100, 850, 26, "#ffd890", 0.6)
            PP.water_fx(ctx, t, P, 890, SH, 6, 12, 50)
            for k in range(3):
                boat(ctx, P, (k * 800 + t * 25) % (SW + 400) - 200, 1050 + k * 80, 260, 1140 + k, "canoe", 1, t,
                     lantern=True, crew=2)
    return dict(layers=layers, dyn=fx, dyn_depths=[0.0, 0.5])


# ---------------------------------------------------------------- 11. TONLE SAP REVERSAL (schematic)
def make_reversal():
    """Schematic: lake + river + Mekong.  First half: rainy season (flow up, lake swells); second half: dry season."""
    def base(ctx):
        ctx.set_source(lin(0, 0, 0, SH, [(0, "#efe6d2"), (1, "#e2d4b4")]))
        ctx.paint()
        wc._tex(ctx, "bloom", 0.4, 3, 2.0)
        src(ctx, mix(RIVER, "#4f7f96", 0.5), 0.9)   # Mekong
        ctx.set_line_width(70)
        ctx.move_to(1900, -40)
        ctx.curve_to(1800, 400, 1750, 700, 1700, 820)
        ctx.curve_to(1650, 1000, 1800, 1200, 1900, SH + 40)
        ctx.stroke()
        ctx.set_line_width(36)                        # Tonle Sap river
        ctx.move_to(1700, 820)
        ctx.curve_to(1400, 700, 1100, 640, 900, 560)
        ctx.stroke()
        draw_text(ctx, "ទន្លេមេគង្គ · Mekong", 1990, 300, 34, "#2a1a10", "ml", 1, font=KM_SANS, weight="Bold")
        draw_text(ctx, "ទន្លេសាប · Tonle Sap river", 1200, 740, 30, "#2a1a10", "mc", 1, font=KM_SANS, weight="Bold")
        draw_text(ctx, "ចតុមុខ · Chaktomuk", 1760, 900, 30, "#7a2e1e", "ml", 1, font=KM_SANS, weight="Bold")

    layers = [(_k("rev_base"), base, 0.5)]

    def dyn(ctx, t, d, depth):
        half = d * 0.5
        wet = t < half
        q = smooth((t if wet else t - half) / (half * 0.6))
        size = (0.6 + 0.6 * q) if wet else (1.2 - 0.6 * q)
        ctx.save()
        ctx.translate(700, 470)
        ctx.scale(size, size)
        sheet(ctx, path_ellipse(0, 0, 320, 170, -0.4), mix(RIVER, "#4f7f96", 0.6), seed=5, edge=True)
        ctx.restore()
        draw_text(ctx, "បឹងទន្លេសាប · Tonle Sap lake", 700, 470, 30, "#fff4dc", "mc", 1, shadow=0.8, font=KM_SANS,
                  weight="Bold")
        lab_km, lab_en = ("រដូវវស្សា · ទឹកហូរចូលបឹង", "Rainy season: the river flows UP into the lake") if wet else \
            ("រដូវប្រាំង · ទឹកហូរចេញពីបឹង", "Dry season: the river flows back DOWN")
        draw_text(ctx, lab_km, 1200, 1120, 44, "#2a1a10", "mc", 1, font=KM_SANS, weight="Bold")
        draw_text(ctx, lab_en, 1200, 1180, 34, "#5a3a22", "mc", 1, font=EN_SERIF, weight="SemiBold")
        for k in range(6):   # flow arrows along the Tonle Sap river
            ph = ((t * 0.5 + k / 6) % 1)
            u = ph if wet else 1 - ph
            x = 1700 - (1700 - 900) * u
            y = 820 - (820 - 560) * u - math.sin(u * math.pi) * 40
            ang = math.atan2(-(820 - 560), -(1700 - 900)) if wet else math.atan2(820 - 560, 1700 - 900)
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(ang)
            src(ctx, "#a4442e", 0.9)
            poly(ctx, [(22, 0), (-14, -14), (-6, 0), (-14, 14)])
            ctx.fill()
            ctx.restore()
    return dict(layers=layers, dyn=dyn, dyn_depths=[0.5])


# ---------------------------------------------------------------- 12. LIVING MANUSCRIPT / LIVING WOOD
PANEL = (330, 300, 2070, 1060)


def _content(kind, P):
    gy = 1040
    if kind == "barge":       # chronicle leaf: the royal barge heads downstream (king seen from behind)
        def props(ctx, P, t):
            _water_band(ctx, P, 960, 1060, seed=12)
            boat(ctx, P, 1200 + math.sin(t * 0.4) * 40, 1000, 900, 1201, "barge", 1, t, crew=6)
            cast.draw(ctx, 1170, 960, 120, "c_king", "sit", t, 180, None, P, cutout=False)
            for k in range(2):
                boat(ctx, P, 520 + k * 1280 + math.sin(t * 0.5 + k) * 20, 1010, 380, 1210 + k, "canoe", 1, t, crew=3)
        return [], props
    if kind == "koki":        # LEGEND: flood river, floating koki tree, Daun Penh and villagers
        figs = [F(560, gy, 330, "daunpenh", "point", 60, 1220), F(800, gy, 320, "c_man", "carry_shoulder", 60, 1221),
                F(980, gy, 320, "c_woman", "offer", 60, 1222)]

        def props(ctx, P, t):
            _water_band(ctx, P, 900, 1060, seed=13)
            tx = 1650 - math.sin(t * 0.3) * 80
            sheet(ctx, path_poly([(tx - 320, 930), (tx + 320, 900), (tx + 330, 960), (tx - 310, 990)]), "#6a4a2a", seed=1230)
            glow(ctx, tx, 940, 160, "#ffe08a", 0.55 + 0.15 * math.sin(t * 2))
            for k in range(4):
                wc.gold_leaf(ctx, path_ellipse(tx - 120 + k * 80, 935, 14, 22), 0.9, k)
            for k in range(5):     # branches
                src(ctx, "#4a3420", 1)
                ctx.set_line_width(8)
                ctx.move_to(tx - 300 + k * 140, 930)
                ctx.line_to(tx - 330 + k * 140, 850)
                ctx.stroke()
        return figs, props
    if kind == "hill_build":  # LEGEND: neighbours raise the hill
        figs = [F(500 + k * 260, gy, 300, ["c_man", "c_woman"][k % 2], "carry_pot_head" if k % 2 else "carry_shoulder",
                  60, 1240 + k) for k in range(4)] + [F(1750, gy, 320, "daunpenh", "pray", -40, 1250)]

        def props(ctx, P, t):
            h = 120 + 120 * smooth(t / 8)
            sheet(ctx, path_ellipse(1500, gy, 420, h), mix(P["mid"], "#8a7a4a", 0.4), seed=1251)
        return figs, props
    if kind == "gable":       # carved teak gable: nagas, lotus and a kinnari
        def props(ctx, P, t):
            tri = [(500, gy), (1200, 420), (1900, gy)]
            sheet(ctx, path_poly(tri), shade(TEAK, 0.1), seed=1260)
            wc.gold_line(ctx, path_poly(tri), 4, 0.9)
            for side in (-1, 1):
                ctx.new_path()
                ctx.move_to(1200 + side * 650, gy - 20)
                for k in range(8):
                    ctx.line_to(1200 + side * (650 - k * 80), gy - 60 - k * 70 + math.sin(t * 2 + k) * 10)
                src(ctx, "#4f7a5a")
                ctx.set_line_width(28)
                ctx.stroke()
            cast.draw(ctx, 1200, gy - 80, 300, "c_dancer", "wave", t, 0, None, P, cutout=False)
        return [], props
    if kind == "scribe":      # a scribe incises a palm leaf
        figs = [F(800, gy, 340, "monk", "write", 50, 1270)]

        def props(ctx, P, t):
            sheet(ctx, path_poly([(1150, 860), (1950, 860), (1950, 920), (1150, 920)]), LEAF, seed=1271)
            n = int(12 * smooth(t / 6))
            src(ctx, "#2a1a10", 0.9)
            ctx.set_line_width(3)
            for k in range(n):
                x = 1180 + k * 62
                ctx.move_to(x, 880)
                ctx.curve_to(x + 12, 868, x + 24, 896, x + 40, 882)
            ctx.stroke()
        return figs, props
    if kind == "reamker":     # Reamker leaf: Rama with his bow, Sita, and the monkey army's banner
        figs = [F(800, gy, 380, "c_king", "shoot_bow", 90, 1280), F(1350, gy, 360, "c_dancer", "pray", -40, 1281),
                F(1700, gy, 340, "c_soldier", "point", -60, 1282)]
        return figs, None
    if kind == "split":       # chronicle leaf: two princes turn away; the leaf tears
        figs = [F(850, gy, 380, "c_king", "talk", -50, 1290), F(1550, gy, 380, "c_king", "point", 50, 1291)]

        def props(ctx, P, t):
            q = smooth((t - 2.0) / 4.0)
            if q > 0:
                ctx.new_path()
                ctx.move_to(1200, PANEL[1])
                for k in range(12):
                    ctx.line_to(1200 + (k % 2 * 2 - 1) * 26 * q, PANEL[1] + (k + 1) * (PANEL[3] - PANEL[1]) / 12 * q)
                src(ctx, "#1a100a", 0.9)
                ctx.set_line_width(5 + 6 * q)
                ctx.stroke()
        return figs, props
    if kind == "eth_lotus":   # closing: Kon Eth fixes his carved lotus to a monastery pillar
        figs = [F(1000, gy, 440, "eth", "craft", 70, 11)]

        def props(ctx, P, t):
            sheet(ctx, path_poly([(1300, gy), (1420, gy), (1420, 360), (1300, 360)]), TEAK, seed=1300)
            for k in range(7):
                a = -math.pi / 2 + (k - 3) * 0.32
                tx, ty = 1360 + math.cos(a) * 40, 640 + math.sin(a) * 60
                src(ctx, LOTUS if k % 2 else shade(LOTUS, 0.2))
                ellipse(ctx, (1360 + tx) / 2, (640 + ty) / 2, 14, 34, a + math.pi / 2)
                ctx.fill()
        return figs, props
    return [], None


def make_relief(kind, panel="leaf", tod="golden", alive=(0.12, 0.3, 0.8, 0.95), legend=False, mouth_fn=None):
    """Living manuscript (panel='leaf': figures are soot-incised drawings on a palm leaf that fill with colour) or
    living wood (panel='wood': figures carved in relief in teak).  alive = (start, full, fade, back) as shot fractions."""
    P = TOD[tod]
    figs, props = _content(kind, P)
    x0, y0, x1, y1 = PANEL

    def panel_layer(ctx):
        ctx.set_source(lin(0, 0, 0, SH, [(0, "#2a1a10"), (1, "#140c08")]))
        ctx.paint()
        if panel == "sand":    # sandstone gallery wall (Angkor Wat)
            sheet(ctx, path_poly([(x0 - 90, y0 - 90), (x1 + 90, y0 - 90), (x1 + 90, y1 + 90), (x0 - 90, y1 + 90)]),
                  "#9a8a80", seed=1401)
            from core import overlay_texture
            ctx.save()
            ctx.rectangle(x0 - 90, y0 - 90, x1 - x0 + 180, y1 - y0 + 180)
            ctx.clip()
            overlay_texture(ctx, "stone", 0.55, 1.5, 4)
            ctx.restore()
        elif panel == "leaf":
            import cards
            cards.palm_leaf(ctx, SW / 2, (y0 + y1) / 2, (x1 - x0) + 260, (y1 - y0) + 120, 1.0, 5, holes=False)
        else:
            sheet(ctx, path_poly([(x0 - 90, y0 - 90), (x1 + 90, y0 - 90), (x1 + 90, y1 + 90), (x0 - 90, y1 + 90)]),
                  shade(TEAK, -0.15), seed=1400)
            ctx.save()
            ctx.rectangle(x0 - 90, y0 - 90, x1 - x0 + 180, y1 - y0 + 180)
            ctx.clip()
            wc._tex(ctx, "grain", 0.8, 3, 1.0)
            ctx.restore()
            wc.gold_line(ctx, path_poly([(x0 - 30, y0 - 30), (x1 + 30, y0 - 30), (x1 + 30, y1 + 30), (x0 - 30, y1 + 30)]),
                         3, 0.8)

    layers = [(_k("panel", p=panel), panel_layer, 0.5)]

    def a_of(t, d):
        q = t / max(d, 0.01)
        return smooth((q - alive[0]) / max(0.01, alive[1] - alive[0])) * \
            (1 - smooth((q - alive[2]) / max(0.01, alive[3] - alive[2])))

    def content(ctx, t):
        if props:
            props(ctx, P, t)
        for f in figs:
            cast.draw(ctx, f["x"], f["y"], f["h"], f["who"], f["pose"], t + f["seed"] * 0.37, f["yaw"], None, P,
                      seed=f["seed"], cutout=False, mouth=(mouth_fn(t) if (mouth_fn and f["who"] == "eth") else None))

    def dyn(ctx, t, d, depth):
        a = a_of(t, d) * (0.65 if legend else 1.0)
        ctx.save()
        ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
        ctx.clip()
        ctx.push_group()
        content(ctx, t)
        g = ctx.pop_group()
        if a < 0.999:
            if panel == "leaf":   # soot-filled incised drawing
                for (dx, dy, col, al) in ((1.5, 2, "#fff4dc", 0.35), (0, 0, "#2a1a10", 0.8)):
                    ctx.save()
                    ctx.translate(dx, dy)
                    src(ctx, col, al * (1 - a * 0.9))
                    ctx.mask(g)
                    ctx.restore()
            else:                 # carved teak or sandstone relief
                base = TEAK if panel == "wood" else "#a8968a"
                for (dx, dy, col, al) in ((7, 9, shade(base, -0.55), 0.65), (-3, -3, shade(base, 0.3), 0.9),
                                          (0, 0, shade(base, 0.05), 1.0)):
                    ctx.save()
                    ctx.translate(dx, dy)
                    src(ctx, col, al * (1 - a * 0.9))
                    ctx.mask(g)
                    ctx.restore()
        if a > 0.001:
            ctx.set_source(lin(0, y0, 0, y1, [(0, P["sky0"], 0.85 * a), (0.68, P["sky1"], 0.85 * a), (0.7, P["mid"], 0.9 * a),
                                              (1, P["near"], 0.9 * a)]))
            ctx.paint()
            ctx.save()
            ctx.translate(0, -8 * a)
            ctx.set_source_rgba(0, 0, 0, 0.3 * a)
            ctx.translate(10, 14)
            ctx.mask(g)
            ctx.translate(-10, -14)
            ctx.set_source(g)
            ctx.paint_with_alpha(a)
            ctx.restore()
            if legend:
                src(ctx, "#f0eaf4", 0.25 * a)
                ctx.paint()
        ctx.restore()
    return dict(layers=layers, dyn=dyn, dyn_depths=[0.5])
