"""Longvek film sets (watercolor + ink + gold leaf), built on chaktomuk.py.  All scenes are artistic reconstructions.

  make_fortress(tod, view, mist, gate_open, smoke, people, mouth_fn)
      view: approach (river, rampart, bamboo, city behind) | gate (close on the wooden gate) | today (ramparts under
            trees, a modern wat) | siege (dusk, smoke, embers)
  make_cutaway()                     schematic: rampart earth layers, moat, thorny bamboo hedge
  make_angkor_noon(people, mouth_fn) Angkor Wat at golden noon with carvers' scaffolds in the north gallery
  elephant(), bull()                 animals for processions and the Preah Ko legend
  extra living-relief kinds (patched into chaktomuk._content):
      usurp, return, battle, krishna_bana, vishnu_asuras, coins (legend), preahko (legend), iberian, procession
"""
import math

import cast
import chaktomuk as K
import paper as PP
import wc
from core import SH, SW, clamp, ellipse, glow, lin, mix, poly, rad, rng, shade, smooth, src
from paper import TOD, jag, path_ellipse, path_poly, sheet
from sets import F, _birds, _comb, _key, _mist, grp, people_dyn

V = "l2"
BAMBOO, RAMPART, SAFFRON, RIVER_B = "#6f8a3a", "#8a4a2e", wc.WC["saffron"], "#4f7f96"

cast.CAST.update({
    "iberian": dict(cast.CAST["zh_envoy"], km="ជនអឺរ៉ុប (គំនូរ)", en="Iberian adventurer (silhouette)",
                    hair="short", hair_c="#2a1a10", wrap=("robe", "#2a2a3a"), top=("robe_top", "#3a3a4a"),
                    face=dict(brow=1.2, jaw=1.1, nose=1.2, beard=True)),
    "friar": dict(cast.CAST["monk"], km="បព្វជិតអឺរ៉ុប", en="Dominican friar (stylised)", hair="short",
                  hair_c="#3a2a1a", wrap=("robe", "#efe6d6"), top=("robe_top", "#1e1a17")),
})


def _k(name, **kw):
    return _key(name, v=V, **kw)


# ---------------------------------------------------------------- bamboo, animals
def bamboo_clump(ctx, P, x, y, h, seed=0, col=None, dense=12):
    """A clump of thorny bamboo: arching culms with nodes, leaf sprays and a few thorny side-branches."""
    R = rng(seed)
    c = col or BAMBOO
    for i in range(dense):
        bx = x + (R.random() - 0.5) * h * 0.25
        lean = (R.random() - 0.5) * h * 0.45
        top = (bx + lean, y - h * (0.75 + 0.3 * R.random()))
        ctx.new_path()
        ctx.move_to(bx, y)
        ctx.curve_to(bx, y - h * 0.4, top[0] - lean * 0.3, top[1] + h * 0.2, *top)
        src(ctx, mix(c, "#c8b46a", 0.25 * R.random()), 0.95)
        ctx.set_line_width(max(2, h * 0.018))
        ctx.stroke()
        for k in range(5):   # nodes
            u = (k + 1) / 6
            nx = bx + (top[0] - bx) * u ** 1.4
            ny = y + (top[1] - y) * u
            src(ctx, shade(c, -0.4), 0.8)
            ctx.set_line_width(max(1.5, h * 0.01))
            ctx.move_to(nx - h * 0.012, ny)
            ctx.line_to(nx + h * 0.012, ny)
            ctx.stroke()
        for k in range(4):   # leaf sprays
            u = 0.55 + 0.45 * R.random()
            lx = bx + (top[0] - bx) * u
            ly = y + (top[1] - y) * u
            for j in range(4):
                a = R.random() * math.pi * 2
                L = h * (0.06 + 0.04 * R.random())
                sheet(ctx, path_poly([(lx, ly), (lx + math.cos(a + 0.2) * L * 0.5, ly + math.sin(a + 0.2) * L * 0.5),
                                      (lx + math.cos(a) * L, ly + math.sin(a) * L),
                                      (lx + math.cos(a - 0.2) * L * 0.5, ly + math.sin(a - 0.2) * L * 0.5)]),
                      mix(c, P["light"], 0.2 * R.random()), seed=seed + i * 20 + k * 4 + j, edge=False, texture=False)


def bamboo_wall(ctx, P, x0, x1, y, h, seed=0):
    x = x0
    k = 0
    while x < x1:
        bamboo_clump(ctx, P, x, y, h * (0.85 + 0.3 * ((k * 37) % 10) / 10), seed + k * 13, dense=9)
        x += h * 0.22
        k += 1


def elephant(ctx, P, x, y, h, t=0.0, f=1, col="#7a7470", seed=0, rider=None):
    for j, (dx, ph) in enumerate(((-0.4, 0), (-0.22, math.pi), (0.25, math.pi), (0.42, 0))):
        lx = x + dx * h * f + math.sin(t * 2.2 + seed + ph) * h * 0.05
        sheet(ctx, path_poly([(lx - h * 0.09, y - h * 0.55), (lx + h * 0.09, y - h * 0.55), (lx + h * 0.08, y),
                              (lx - h * 0.08, y)]), shade(col, -0.1 if j % 2 else 0.0), seed=seed + j)
    sheet(ctx, path_ellipse(x, y - h * 0.62, h * 0.62, h * 0.36), col, seed=seed + 5)
    hx = x + h * 0.62 * f
    sheet(ctx, path_ellipse(hx, y - h * 0.78, h * 0.24, h * 0.24), col, seed=seed + 6)
    sheet(ctx, path_ellipse(hx - h * 0.1 * f, y - h * 0.78, h * 0.16, h * 0.22), shade(col, -0.12), seed=seed + 7)
    k = math.sin(t * 2.2 + seed)
    ctx.new_path()
    ctx.move_to(hx + h * 0.14 * f, y - h * 0.7)
    ctx.curve_to(hx + h * 0.32 * f, y - h * 0.55, hx + h * 0.3 * f, y - h * 0.35, hx + h * (0.3 + 0.05 * k) * f, y - h * 0.18)
    src(ctx, col)
    ctx.set_line_width(h * 0.08)
    ctx.stroke()
    sheet(ctx, path_poly([(x - h * 0.3, y - h * 0.95), (x + h * 0.3, y - h * 0.95), (x + h * 0.26, y - h * 0.85),
                          (x - h * 0.26, y - h * 0.85)]), "#a4442e", seed=seed + 8)   # saddle cloth
    if rider:
        cast.draw(ctx, x, y - h * 0.92, h * 0.6, rider, "sit", t, 90 * f, None, P, cutout=False)


def bull(ctx, P, x, y, h, t=0.0, f=1, col="#efe6d6", seed=0, glow_a=0.0):
    if glow_a:
        glow(ctx, x, y - h * 0.6, h * 1.4, "#ffe08a", glow_a)
    for j, dx in enumerate((-0.38, -0.2, 0.22, 0.4)):
        lx = x + dx * h * f + math.sin(t * 2 + j) * h * 0.03
        sheet(ctx, path_poly([(lx - h * 0.05, y - h * 0.5), (lx + h * 0.05, y - h * 0.5), (lx + h * 0.04, y),
                              (lx - h * 0.04, y)]), shade(col, -0.15), seed=seed + j)
    sheet(ctx, path_ellipse(x, y - h * 0.6, h * 0.55, h * 0.25), col, seed=seed + 5)
    sheet(ctx, path_ellipse(x - h * 0.05 * f, y - h * 0.82, h * 0.16, h * 0.1), shade(col, -0.05), seed=seed + 6)  # hump
    hx = x + h * 0.6 * f
    sheet(ctx, path_ellipse(hx, y - h * 0.72, h * 0.16, h * 0.12), col, seed=seed + 7)
    for side in (-1, 1):   # horns
        ctx.new_path()
        ctx.move_to(hx, y - h * 0.8)
        ctx.curve_to(hx + side * h * 0.1, y - h * 0.95, hx + side * h * 0.16, y - h * 0.95, hx + side * h * 0.14, y - h * 1.02)
        src(ctx, "#c9a34a")
        ctx.set_line_width(h * 0.03)
        ctx.stroke()


# ---------------------------------------------------------------- 1. THE FORTRESS
def make_fortress(tod="dawn", view="approach", mist=0.5, gate_open=0.0, smoke=0.0, people=None, mouth_fn=None):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.55, (0.72, 0.36), 60, 7, 1501)
        PP.clouds(ctx, P, 4, (0.04, 0.25), 1502, mix(P["sky0"], P["shadow"], 0.25) if smoke else None)

    def city(ctx):
        K.forest_band(ctx, P, 720, 18, 150, 1503, mix(P["far"], P["mid"], 0.5))
        if view != "today":
            for k, (x, s, tiers) in enumerate(((700, 260, 2), (1250, 420, 3), (1800, 280, 2), (2200, 200, 1),
                                               (300, 200, 1))):
                K.wood_hall(ctx, P, x, 760, s, 1510 + k, tiers=tiers)
        else:   # present-day Wat Trolaeng Keng (painted, simplified) among trees
            K.wood_hall(ctx, P, 1450, 760, 300, 1520, tiers=2, col="#e8d8b8")
            K.forest_band(ctx, P, 780, 14, 260, 1530, mix(P["mid"], P["near"], 0.3))

    def rampart(ctx):
        top = 830
        pts = jag([(-40, top), (SW + 40, top + 6)], 6, 1540, 40)
        sheet(ctx, path_poly(pts + [(SW + 40, 960), (-40, 960)]),
              mix(RAMPART, P["mid"], 0.5 if view == "today" else 0.15), seed=1541)
        if view == "today":
            K.forest_band(ctx, P, 860, 20, 260, 1550, mix(P["near"], P["mid"], 0.3))
        else:
            bamboo_wall(ctx, P, -40, SW + 40, top + 10, 230, 1560)
        # moat
        ctx.set_source(lin(0, 960, 0, 1040, [(0, mix(RIVER_B, P["sky1"], 0.25)), (1, mix(RIVER_B, P["shadow"], 0.25))]))
        ctx.rectangle(-40, 960, SW + 80, 80)
        ctx.fill()
        sheet(ctx, path_poly(jag([(-40, 1040), (SW + 40, 1036)], 4, 1570, 40) + [(SW + 40, SH + 40), (-40, SH + 40)]),
              mix(RAMPART, "#b8945a", 0.5), seed=1571)
        if view in ("gate", "approach", "siege"):   # gate tower over a causeway
            gx = 1200
            sheet(ctx, path_poly([(gx - 90, 1045), (gx + 90, 1045), (gx + 70, 960), (gx - 70, 960)]), shade(RAMPART, 0.1),
                  seed=1580)
            sheet(ctx, path_poly([(gx - 120, 960), (gx + 120, 960), (gx + 120, 700), (gx - 120, 700)]), K.TEAK, seed=1581)
            K.wood_hall(ctx, P, gx, 700, 300, 1582, tiers=2, gable=True)

    def river(ctx):
        K._water_band(ctx, P, 1100, seed=20)

    layers = [(_k("ft_sky", tod=tod, s=smoke > 0), sky_, 0.0), (_k("ft_city", tod=tod, td=view == "today"), city, 0.3),
              (_k("ft_r", tod=tod, vw=view), rampart, 0.6)]
    if view == "approach":
        layers.append((_k("ft_river", tod=tod), river, 1.0))

    def fx(ctx, t, d, depth):
        if depth == 0.3 and mist:
            _mist(ctx, t, 800, 160, P["haze"], mist * (1 - 0.6 * smooth(t / max(d, 1))), 3, 9)
        if depth == 0.6:
            if view in ("gate", "approach", "siege"):   # gate leaves swing open
                g = clamp(gate_open + (smooth(t / max(d, 1)) if gate_open < 0 else 0))
                for side in (-1, 1):
                    w = 115 * (1 - 0.85 * g)
                    x0 = 1200 + side * 2
                    sheet(ctx, path_poly([(x0, 950), (x0 + side * w, 950), (x0 + side * w, 715), (x0, 715)]),
                          shade(K.TEAK, -0.2), seed=1590 + side, texture=False)
                    if g < 0.9:
                        lx = x0 + side * w * 0.5
                        src(ctx, K.LOTUS, 0.9)
                        ellipse(ctx, lx, 830, 16, 22)
                        ctx.fill()
            if smoke:
                for j in range(14):
                    ph = (t * 0.06 + j / 14) % 1
                    x = (j * 190 + t * 12) % SW
                    src(ctx, "#3a3438", 0.55 * smoke * (1 - ph))
                    ellipse(ctx, x, 820 - ph * 600, 80 + ph * 260, 50 + ph * 160)
                    ctx.fill()
                for j in range(30):
                    ph = (t * 0.3 + j / 30) % 1
                    src(ctx, "#ffb050", 0.8 * (1 - ph) * smoke)
                    ctx.arc((j * 83) % SW + math.sin(t + j) * 20, 900 - ph * 500, 3, 0, 6.283)
                    ctx.fill()
                glow(ctx, 1200, 820, 700, "#ff8a30", 0.2 * smoke)
        if depth == 1.0:
            PP.water_fx(ctx, t, P, 1110, SH, 5, 14, 40)
            for k in range(3):
                K.boat(ctx, P, (k * 760 + t * 30) % (SW + 400) - 200, 1180 + k * 50, 280, 1600 + k, "canoe",
                       1 if k % 2 else -1, t, crew=2)
    deps = [0.0, 0.3, 0.6] + ([1.0] if view == "approach" else [])
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=deps)


# ---------------------------------------------------------------- 2. RAMPART CUT-AWAY (schematic)
def make_cutaway():
    def base(ctx):
        from core import EN_SERIF, KM_SANS, draw_text
        ctx.set_source(lin(0, 0, 0, SH, [(0, "#efe6d2"), (1, "#e2d4b4")]))
        ctx.paint()
        wc._tex(ctx, "bloom", 0.4, 2, 2.0)
        P = TOD["day"]
        for k, col in enumerate(("#a0603a", "#8a4a2e", "#9a6a44", "#7a4228")):   # rampart layers
            y0 = 900 - k * 70
            sheet(ctx, path_poly([(500 + k * 60, 1050 - k * 0), (1500 - k * 60, 1050), (1400 - k * 70, y0), (600 + k * 70, y0)]),
                  col, seed=1700 + k)
        bamboo_wall(ctx, P, 700, 1350, 700, 380, 1710)
        ctx.set_source(lin(0, 980, 0, 1100, [(0, "#6f9fb6"), (1, "#3e6a80")]))
        ctx.rectangle(1500, 980, 600, 120)
        ctx.fill()
        sheet(ctx, path_poly([(-40, 1050), (500, 1050), (500, 1250), (-40, 1250)]), "#b8945a", seed=1720)
        sheet(ctx, path_poly([(1500, 1100), (2440, 1100), (2440, 1250), (1500, 1250)]), "#b8945a", seed=1721)
        for x, y, km, en in ((1000, 1000, "កំពែងដី", "Earthen rampart"), (1000, 420, "របងឫស្សីបន្លា", "Thorny bamboo hedge"),
                             (1800, 1040, "គូទឹក", "Moat"), (250, 1150, "ក្នុងទីក្រុង", "Inside the city")):
            draw_text(ctx, km, x, y, 40, "#2a1a10", "mc", 1, font=KM_SANS, weight="Bold")
            draw_text(ctx, en, x, y + 48, 32, "#5a3a22", "mc", 1, font=EN_SERIF, weight="SemiBold")

    return dict(layers=[(_k("cutaway"), base, 0.5)], dyn_depths=[0.5])


# ---------------------------------------------------------------- 3. ANGKOR WAT AT GOLDEN NOON (with scaffolds)
def make_angkor_noon(people=None, mouth_fn=None, tod="golden"):
    sc = K.make_angkor_dusk(people=people, mouth_fn=mouth_fn, tod=tod)
    P = TOD[tod]
    base = sc["dyn"]

    def dyn(ctx, t, d, depth):
        base(ctx, t, d, depth)
        if depth == 0.35:   # bamboo scaffold against the north gallery (right wing)
            src(ctx, "#6a5030", 0.9)
            ctx.set_line_width(4)
            for k in range(6):
                x = 1620 + k * 50
                ctx.move_to(x, 830)
                ctx.line_to(x, 620)
            for k in range(4):
                ctx.move_to(1600, 820 - k * 60)
                ctx.line_to(1900, 820 - k * 60)
            ctx.stroke()
    sc["dyn"] = dyn
    return sc


# ---------------------------------------------------------------- 4. EXTRA RELIEF KINDS
_base_content = K._content


def _content(kind, P):
    gy = 1040
    if kind == "usurp":   # chronicle leaf: a commoner takes the throne; a prince's boat leaves westward
        figs = [F(700, gy, 360, "c_man", "point", 40, 1801), F(1000, gy, 330, "c_noble", "bow", -50, 1802)]

        def props(ctx, P, t):
            sheet(ctx, path_poly([(560, gy), (840, gy), (840, gy - 160), (560, gy - 160)]), "#c9a34a", seed=1803)
            K._water_band(ctx, P, 960, 1060, seed=21)
            K.boat(ctx, P, 1700 - t * 25, 1010, 360, 1804, "canoe", -1, t, crew=3)
        return figs, props
    if kind == "return":  # chronicle panel: returning army; coronation parasol (king from behind)
        figs = [F(450 + k * 170, gy, 300, "c_soldier", "walk", 90, 1810 + k) for k in range(4)]
        figs += [F(1500, gy, 360, "c_king", "stand", 180, 1820), F(1750, gy, 320, "c_noble", "bow", -60, 1821)]

        def props(ctx, P, t):
            from chaktomuk import boat as _b  # noqa: F401
            src(ctx, "#4a3420")
            ctx.set_line_width(6)
            ctx.move_to(1560, gy - 120)
            ctx.line_to(1560, gy - 520)
            ctx.stroke()
            for k in range(3):
                w = 150 - k * 35
                yy = gy - 520 + k * 30
                sheet(ctx, path_poly([(1560 - w, yy), (1560 + w, yy), (1560 + w * 0.4, yy - 60), (1560 - w * 0.4, yy - 60)]),
                      shade("#c9a34a", -0.1 * k), seed=1822 + k)
        return figs, props
    if kind == "battle":
        figs = [F(1500 + k * 160, gy, 300, "c_soldier", "walk", -90, 1830 + k) for k in range(3)]

        def props(ctx, P, t):
            elephant(ctx, P, 800 + math.sin(t * 0.5) * 30, gy, 420, t, 1, "#8a8480", 1840, rider="c_soldier")
            K._water_band(ctx, P, 1000, 1060, seed=22)
        return figs, props
    if kind == "krishna_bana":   # 16th-c. relief (Angkor Wat, east wing of the north gallery), simplified
        figs = [F(500 + k * 150, gy, 300, "c_soldier", "walk", 90, 1850 + k) for k in range(3)]
        figs += [F(1650 + k * 150, gy, 300, "c_soldier", "walk", -90, 1860 + k) for k in range(3)]

        def props(ctx, P, t):
            elephant(ctx, P, 1200, gy, 360, t, 1, "#8a8480", 1870, rider="c_king")
            for k in range(4):   # musicians' drums
                src(ctx, "#6a4a2a")
                ellipse(ctx, 420 + k * 90, gy - 330, 24, 34)
                ctx.fill()
        return figs, props
    if kind == "vishnu_asuras":
        figs = [F(500 + k * 170, gy, 300, "c_soldier", "walk", -90, 1880 + k) for k in range(3)]
        figs += [F(1300, gy, 420, "c_king", "point", 90, 1890)]

        def props(ctx, P, t):
            for k in range(3):
                sheet(ctx, path_ellipse(1300 + k * 40, 520 - k * 10, 120 - k * 30, 26), "#c9a34a", seed=1891 + k)
        return figs, props
    if kind == "coins":   # LEGEND: silver coins fired into the bamboo; defenders cut the hedge
        figs = [F(1350 + k * 220, gy, 320, "c_man", "harvest", -60, 1900 + k) for k in range(3)]

        def props(ctx, P, t):
            bamboo_wall(ctx, P, 1100, 2100, gy, 360, 1910)
            for j in range(24):
                ph = (t * 0.4 + j / 24) % 1
                x = 380 + ph * 900
                y = gy - 400 - math.sin(ph * math.pi) * 260 + (j % 4) * 30
                glow(ctx, x, y, 22, "#f6f0e0", 0.6)
                src(ctx, "#e8e8f0", 0.95)
                ctx.arc(x, y, 7, 0, 6.283)
                ctx.fill()
        return figs, props
    if kind == "preahko":  # LEGEND: Preah Ko, the sacred bull, and Preah Keo carried away
        figs = [F(1500 + k * 180, gy, 300, "c_soldier", "walk", 90, 1920 + k) for k in range(3)]

        def props(ctx, P, t):
            bull(ctx, P, 1000 + t * 30, gy, 340, t, 1, "#efe6d6", 1930, glow_a=0.5)
            wc.gold_leaf(ctx, path_ellipse(1230 + t * 30, gy - 330, 30, 40), 0.9, 1)
        return figs, props
    if kind == "iberian":  # shadow-puppet style silhouettes at a Khmer court
        figs = [F(700, gy, 380, "iberian", "talk", 60, 1940), F(950, gy, 370, "iberian", "point", 60, 1941),
                F(1600, gy, 360, "c_king", "sit", -90, 1942)]

        def props(ctx, P, t):
            K.boat(ctx, P, 400 + t * 15, 960, 420, 1943, "junk", 1, t)
        return figs, props
    if kind == "procession":
        figs = [F(500 + k * 170, gy, 280, "c_soldier", "walk", 90, 1950 + k) for k in range(3)]

        def props(ctx, P, t):
            elephant(ctx, P, 1350 + t * 20, gy, 380, t, 1, "#8a8480", 1960, rider="c_king")
            for k in range(2):
                K.boat(ctx, P, 1900, gy - 20 + k * 10, 300, 1961 + k, "barge", -1, t, crew=4)
        return figs, props
    return _base_content(kind, P)


K._content = _content
