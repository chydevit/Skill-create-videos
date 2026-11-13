"""Paper-cut reconstruction sets (built for 'Funan'; add new make_* builders per film). Every make_* returns a scene dict for film.draw_scene.
All are artistic reconstructions (badged as such by the shot list)."""
import hashlib
import math

import numpy as np

import cast
import paper as PP
from core import (SH, SW, PAL, clamp, ellipse, glow, hexc, lin, mix, overlay_texture, poly, rad, rng, smooth, spline,
                  src)
from paper import TOD, sheet, path_poly, path_ellipse, jag

V = "f2"


def _key(name, **kw):
    return name + "_" + hashlib.sha1((V + repr(sorted(kw.items()))).encode()).hexdigest()[:10]


def _comb(*fns):
    def dyn(ctx, t, d, depth):
        for f in fns:
            if f:
                f(ctx, t, d, depth)
    return dyn


def F(x, y, h, who, pose="idle", yaw=90, seed=0, **kw):
    d = dict(x=x, y=y, h=h, who=who, pose=pose, yaw=yaw, seed=seed)
    d.update(kw)
    return d


def grp(depth, *items):
    return dict(depth=depth, items=list(items))


def people_dyn(groups, P, mouth_fn=None):
    """groups: [dict(depth, items=[F(...)])]. Items may carry vx, vy (px/s), boat=True (drawn standing in a boat),
    talk=True (mouth driven by mouth_fn(t) = guide's voice envelope)."""
    def dyn(ctx, t, d, depth):
        for g in groups:
            if g["depth"] != depth:
                continue
            its = [dict(it, x=it["x"] + it.get("vx", 0) * t, y=it["y"] + it.get("vy", 0) * t) for it in g["items"]]
            for it in sorted(its, key=lambda q: q["y"]):
                bob = math.sin(t * 1.3 + it.get("seed", 0)) * it["h"] * 0.008 if it.get("boat") else 0
                if it.get("boat"):
                    PP.boat(ctx, P, it["x"], it["y"] + bob + it["h"] * 0.03, it["h"] * 1.5, it.get("seed", 0),
                            load=it.get("load", True), f=1 if it.get("yaw", 90) >= 0 else -1)
                m = mouth_fn(t) if (it.get("talk") and mouth_fn) else None
                cast.draw(ctx, it["x"], it["y"] + bob, it["h"], it["who"], it.get("pose", "idle"),
                          t + it.get("seed", 0) * 0.37, it.get("yaw", 90), it.get("expr"), P, seed=it.get("seed", 0),
                          hz=it.get("hz", 0.0), mouth=m, silhouette=it.get("sil"), outline=not it.get("sil"),
                          perforate=it.get("perforate", False), cutout=not it.get("sil"))
    return dyn


# ================================================================ 1. MEKONG DELTA AT DAWN (opening, closing)
def make_delta(tod="dawn", people=None, mouth_fn=None, sun=(0.62, 0.5), lotus_n=6, mist_a=0.45, boats=True):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.6, sun, 70, 8, 3)
        PP.clouds(ctx, P, 5, (0.08, 0.32), 4)

    def far(ctx):
        PP.ridge(ctx, P, 790, 60, mix(P["far"], P["haze"], 0.35), 5, peaks=[(1650, 170, 160), (1820, 90, 120)])
        for i, x in enumerate(range(60, SW, 150)):
            PP.palm(ctx, P, x + (i % 3) * 30, 810, 120 + (i % 4) * 25, "sugar" if i % 3 else "coconut", 10 + i,
                    mix(P["far"], P["mid"], 0.4))

    def mid(ctx):
        PP.water(ctx, P, 800, SH + 40, 6)
        for i, x in enumerate((180, 520, 940, 1500, 2050, 2300)):
            PP.palm(ctx, P, x, 880 + (i % 2) * 20, 70, "nipa", 30 + i, mix(P["mid"], P["near"], 0.3))

    def near(ctx):
        R = rng(7)
        for i in range(lotus_n):
            PP.lotus(ctx, P, 120 + i * 420 + R.random() * 120, 1240 + R.random() * 60, 70 + R.random() * 30,
                     0.6 + 0.4 * R.random(), 50 + i)
        PP.palm(ctx, P, 60, SH + 40, 900, "coconut", 61, P["near"])
        PP.palm(ctx, P, SW - 80, SH + 60, 980, "coconut", 62, P["near"])

    layers = [(_key("dl_sky", tod=tod, s=sun), sky_, 0.0), (_key("dl_far", tod=tod), far, 0.3),
              (_key("dl_mid", tod=tod), mid, 0.6), (_key("dl_near", tod=tod, n=lotus_n), near, 1.0)]

    def fx(ctx, t, d, depth):
        if depth == 0.3:
            _mist(ctx, t, 800, 120, P["haze"], mist_a, 2, 8)
            _birds(ctx, t, 500, 380, 7, P["shadow"])
        if depth == 0.6:
            PP.water_fx(ctx, t, P, 820, SH, 3, 16, 60)
            if boats:
                PP.boat(ctx, P, (300 + t * 22) % (SW + 400) - 200, 960, 220, 3)
        if depth == 1.0:
            _mist(ctx, t, 1150, 80, P["haze"], mist_a * 0.5, 5, 12)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.3, 0.6, 1.0])


def _mist(ctx, t, y, h, color, a, seed, speed):
    R = rng(seed)
    for i in range(8):
        cx = (R.random() * SW * 1.4 + t * speed * (0.6 + R.random())) % (SW * 1.4) - SW * 0.2
        cy = y + (R.random() - 0.5) * h
        rx, ry = SW * (0.15 + 0.2 * R.random()), h * (0.3 + 0.3 * R.random())
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(rx, ry)
        ctx.set_source(rad(0, 0, 0, 1, [(0, color, a), (1, color, 0)]))
        ctx.arc(0, 0, 1, 0, 6.283)
        ctx.fill()
        ctx.restore()


def _birds(ctx, t, x0, y0, n, color, speed=30):
    R = rng(3)
    for i in range(n):
        x = x0 + R.random() * 300 + t * speed * (0.9 + 0.2 * R.random())
        y = y0 + R.random() * 80 + math.sin(t * 0.8 + i) * 6
        fl = math.sin(t * 7 + i)
        s = 8
        src(ctx, color, 0.8)
        ctx.set_line_width(2)
        ctx.move_to(x - s, y - fl * s * 0.5)
        ctx.curve_to(x - s * 0.5, y - s * 0.3, x - s * 0.2, y, x, y)
        ctx.curve_to(x + s * 0.2, y, x + s * 0.5, y - s * 0.3, x + s, y - fl * s * 0.5)
        ctx.stroke()


# ================================================================ 2. BEFORE FUNAN: delta village, rice and flood
def make_lowland(tod="day", flood=0.0, people=None, mouth_fn=None):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.55, (0.25, 0.3), 60, 7, 8)
        PP.clouds(ctx, P, 6, (0.06, 0.3), 9)

    def far(ctx):
        PP.ridge(ctx, P, 720, 40, mix(P["far"], P["haze"], 0.3), 11)
        for i, x in enumerate(range(40, SW, 210)):
            PP.palm(ctx, P, x, 740, 140 + (i % 3) * 30, "sugar", 70 + i, mix(P["far"], P["mid"], 0.5))

    def fields(ctx):
        y0 = 760
        for r_ in range(7):   # paddies as paper strips separated by bunds
            yy = y0 + r_ * 60 * (1 + r_ * 0.25)
            colr = mix("#7a9a4a", "#c8b46a", (r_ % 3) * 0.25)
            pts = jag([(-30, yy), (SW + 30, yy + 10 * math.sin(r_))], 2, r_, 50)
            sheet(ctx, path_poly(pts + [(SW + 30, SH + 30), (-30, SH + 30)]), colr, shadow=0.5, seed=r_, edge=True)
            src(ctx, mix(colr, "#2a4a1a", 0.4), 0.6)
            R = rng(r_)
            for k in range(int(40 + r_ * 12)):
                x = R.random() * SW
                ctx.set_line_width(1.5 + r_ * 0.4)
                ctx.move_to(x, yy + 12 + r_ * 4)
                ctx.line_to(x - 3, yy - 2 - r_ * 2)
                ctx.move_to(x, yy + 12 + r_ * 4)
                ctx.line_to(x + 4, yy - r_ * 2)
                ctx.stroke()
        for k, (x, s) in enumerate(((420, 150), (700, 120), (1880, 160))):
            PP.stilt_house(ctx, P, x, 860 + k * 10, s, 80 + k)

    layers = [(_key("lw_sky", tod=tod), sky_, 0.0), (_key("lw_far", tod=tod), far, 0.3),
              (_key("lw_f", tod=tod), fields, 0.65)]

    def fx(ctx, t, d, depth):
        if depth == 0.65 and flood > 0:
            lvl = 1300 - flood * smooth(t / max(d, 1)) * 480
            ctx.rectangle(0, lvl, SW, SH - lvl)
            ctx.set_source(lin(0, lvl, 0, SH, [(0, P["water"], 0.85), (1, mix(P["water"], P["shadow"], 0.3), 0.92)]))
            ctx.fill()
            PP.water_fx(ctx, t, P, lvl, SH, 9, 14, 40)
        if depth == 0.0:
            _birds(ctx, t, 300, 300, 6, P["shadow"])
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.3, 0.65])


# ================================================================ 3. SHADOW-PUPPET SCREEN (legend chapter)
def make_puppet(figures, title=None, fire=True, mouth_fn=None):
    """Sbek-style performance: a glowing cloth screen; leather puppets in silhouette with punched patterns.
    figures: list of dict(kind='person'|'ship'|'naga'|'tree'|'arrow'|'palace', x, y, s, ...)."""
    P = TOD["lamp"]

    def screen(ctx):
        ctx.set_source_rgb(*hexc("#120a06"))
        ctx.paint()
        ctx.set_source(rad(SW / 2, SH * 0.55, 100, SW * 0.6, [(0, "#f6d8a0"), (0.55, "#d89a52"), (1, "#5a3018")]))
        ctx.rectangle(110, 70, SW - 220, SH - 230)
        ctx.fill()
        ctx.save()
        ctx.rectangle(110, 70, SW - 220, SH - 230)
        ctx.clip()
        overlay_texture(ctx, "weave", 0.25, 1.0, 3)
        overlay_texture(ctx, "paper", 0.3, 1.5, 4)
        ctx.restore()
        src(ctx, "#2a1608")   # frame posts
        for x in (90, SW - 130):
            ctx.rectangle(x, 40, 40, SH)
            ctx.fill()
        ctx.rectangle(60, 50, SW - 120, 30)
        ctx.fill()
        ctx.rectangle(60, SH - 170, SW - 120, 30)
        ctx.fill()

    layers = [(_key("pp_screen"), screen, 0.5)]
    ink = "#1a0e08"

    def dyn(ctx, t, d, depth):
        if depth != 0.5:
            return
        flick = 0.92 + 0.08 * math.sin(t * 13) * math.sin(t * 7.3)
        ctx.save()
        ctx.rectangle(110, 70, SW - 220, SH - 230)
        ctx.clip()
        for f_ in figures:
            k = f_["kind"]
            at = f_.get("at", 0.0)
            a = smooth((t - at) / 0.8) * (1 - smooth((t - f_.get("until", 1e9)) / 0.8))
            if a <= 0:
                continue
            x = f_["x"] + f_.get("vx", 0) * max(0, t - at)
            y = f_["y"] + math.sin(t * 1.4 + f_.get("seed", 0)) * 6   # puppets sway on their rods
            ctx.push_group()
            if k == "person":
                cast.draw(ctx, x, y, f_["s"], f_["who"], f_.get("pose", "idle"), t, f_.get("yaw", 90),
                          silhouette=ink, outline=False, cutout=False, perforate=True, seed=f_.get("seed", 0))
            elif k == "ship":
                PP.ship(ctx, P, x, y, f_["s"], "funan", f_.get("seed", 0), t, f_.get("f", 1))
            elif k == "naga":
                _naga(ctx, x, y, f_["s"], t)
            elif k == "tree":
                PP.palm(ctx, P, x, y, f_["s"], "coconut", f_.get("seed", 0), ink)
            elif k == "arrow":
                p = clamp((t - at) / f_.get("fly", 1.2))
                ax = f_["x"] + (f_["x2"] - f_["x"]) * p
                ay = f_["y"] + (f_["y2"] - f_["y"]) * p - math.sin(p * math.pi) * 80
                ctx.set_line_width(6)
                src(ctx, ink)
                ctx.move_to(ax - 70, ay + 6)
                ctx.line_to(ax, ay)
                ctx.stroke()
                poly(ctx, [(ax + 18, ay - 1), (ax - 4, ay - 10), (ax - 4, ay + 9)])
                ctx.fill()
            elif k == "waves":
                for i in range(7):
                    wx = x + i * 160 + math.sin(t + i) * 20
                    ctx.new_path()
                    ctx.arc(wx, y, 70, math.pi, 2 * math.pi)
                    ctx.set_line_width(10)
                    src(ctx, ink)
                    ctx.stroke()
            elif k == "palace":
                PP.brick_shrine(ctx, P, x, y, f_["s"], 3)
            pat = ctx.pop_group()
            # silhouette everything in leather-dark ink (the group's alpha is the puppet's shape)
            src(ctx, ink, a)
            ctx.mask(pat)
        ctx.restore()
        # lamp flicker and the dalang's glow
        src(ctx, "#ffb040", 0.06 * (1 - flick) * 6)
        ctx.paint()
        if fire:
            glow(ctx, SW / 2, SH - 60, 380, "#ff9a40", 0.35 * flick)

    def over(ctx, t, d):
        if title:
            from core import draw_text, KM_SANS, EN_SERIF, W
            a = smooth((t - 0.5) / 0.8) * clamp((d - t) / 0.6)
            draw_text(ctx, title[0], W / 2, 70, 34, "#f6d8a0", "mc", a, shadow=0.8, font=KM_SANS, weight="Bold")
            draw_text(ctx, title[1], W / 2, 112, 24, "#e8c890", "mc", a, shadow=0.8, font=EN_SERIF, weight="SemiBold")
    return dict(layers=layers, dyn=dyn, dyn_depths=[0.5], over=over)


def _naga(ctx, x, y, s, t):
    """Seven-headed naga silhouette (for the Khmer Preah Thong - Neang Neak story)."""
    src(ctx, "#1a0e08")
    ctx.set_line_width(s * 0.12)
    ctx.set_line_cap(1)
    ctx.move_to(x - s * 2.2, y + s * 0.4)
    for k in range(24):
        u = k / 23
        ctx.line_to(x - s * 2.2 + u * s * 2.2, y + s * 0.4 + math.sin(u * 9 + t * 1.5) * s * 0.18)
    ctx.stroke()
    for k in range(7):
        a = -math.pi / 2 + (k - 3) * 0.28
        hx, hy = x + math.cos(a) * s * 0.9, y - s * 0.2 + math.sin(a) * s * 0.9
        ctx.set_line_width(s * 0.1)
        ctx.move_to(x, y + s * 0.2)
        ctx.line_to(hx, hy)
        ctx.stroke()
        ellipse(ctx, hx, hy, s * 0.14, s * 0.1, a + 1.57)
        ctx.fill()


# ================================================================ 4. OC EO PORT
def make_port(tod="day", people=None, mouth_fn=None, ships=True):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.5, (0.8, 0.22), 60, 7, 12)
        PP.clouds(ctx, P, 6, (0.05, 0.3), 13)

    def far(ctx):
        PP.ridge(ctx, P, 660, 30, mix(P["far"], P["haze"], 0.4), 14, peaks=[(600, 200, 170)])   # Ba The hill
        PP.water(ctx, P, 660, 900, 15, mix(P["water"], P["haze"], 0.3), 3)

    def town(ctx):
        # palisade and houses on piles along the waterfront
        for k in range(10):
            PP.stilt_house(ctx, P, 140 + k * 235, 820 + (k % 2) * 16, 105 + (k % 3) * 12, 100 + k,
                           roof=["#b08a4a", "#a8783a", "#c09a5a"][k % 3])
        PP.brick_shrine(ctx, P, 1900, 760, 160, 120)
        PP.water(ctx, P, 860, SH + 40, 16, P["water"], 4)
        # wooden jetty
        for k in range(12):
            x = 700 + k * 70
            sheet(ctx, path_poly([(x, 880), (x + 10, 880), (x + 10, 990), (x, 990)]), "#4a3220", shadow=0.4,
                  seed=k, edge=False, texture=False)
        sheet(ctx, path_poly([(680, 872), (1520, 872), (1520, 892), (680, 892)]), "#7a5a36", shadow=0.8, seed=3)
        # goods on the jetty
        for k in range(7):
            x = 760 + k * 105
            if k % 2:
                cast.pot(ctx, x, 872, 34, ["#a8744a", "#8a5a3a"][k % 2], P)
            else:
                sheet(ctx, path_poly([(x - 26, 872), (x + 26, 872), (x + 22, 836), (x - 22, 836)]), "#9a7a4a",
                      shadow=0.4, seed=k, edge=False)

    layers = [(_key("po_sky", tod=tod), sky_, 0.0), (_key("po_far", tod=tod), far, 0.3),
              (_key("po_town", tod=tod), town, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.3:
            _birds(ctx, t, 900, 300, 6, P["shadow"])
            if ships:
                PP.ship(ctx, P, 1700 - t * 10, 760, 380, "sail", 2, t, -1)
        if depth == 0.6:
            PP.water_fx(ctx, t, P, 900, SH, 5, 18, 50)
            if ships:
                PP.ship(ctx, P, 420 + t * 14, 1080, 720, "sail", 1, t)
                PP.ship(ctx, P, 1800 - t * 8, 1180, 640, "funan", 4, t, -1)
                PP.boat(ctx, P, (2200 - t * 40) % (SW + 400) - 200, 1290, 260, 6)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.3, 0.6, 1.0])


# ================================================================ 5. OPEN SEA (fleets, embassies)
def make_sea(tod="golden", fleet="funan", n=5, people=None, mouth_fn=None):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.5, (0.7, 0.42), 80, 8, 20)
        PP.clouds(ctx, P, 7, (0.05, 0.38), 21)

    def sea(ctx):
        PP.water(ctx, P, SH * 0.5, SH + 40, 22, P["water"], 6)

    layers = [(_key("se_sky", tod=tod), sky_, 0.0), (_key("se_sea", tod=tod), sea, 0.4)]

    def fx(ctx, t, d, depth):
        if depth == 0.4:
            PP.water_fx(ctx, t, P, SH * 0.5, SH, 7, 30, 70)
            R = rng(9)
            for i in range(n):
                k = i / max(1, n - 1)
                L = 220 + k * 520
                x = (300 + i * 420 + R.random() * 200 + t * (16 + 10 * k)) % (SW + 600) - 300
                y = SH * 0.55 + k * 520
                PP.ship(ctx, P, x, y, L, fleet if fleet != "mixed" else ("funan" if i % 2 else "sail"), i, t)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.4])


# ================================================================ 6. PALACE / RECEPTION (Chinese envoys)
def make_palace(tod="golden", people=None, mouth_fn=None):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.5, (0.2, 0.3), 60, 7, 30)
        PP.ridge(ctx, P, 700, 40, mix(P["far"], P["haze"], 0.3), 31)
        # walled city: a wooden palisade on an earthen bank (Chinese records mention walled cities)
        sheet(ctx, path_poly(jag([(-30, 760), (SW + 30, 760)], 3, 32) + [(SW + 30, 860), (-30, 860)]), "#8a6a3c",
              shadow=0.8, seed=32)
        for k in range(70):
            x = k * 36
            sheet(ctx, path_poly([(x, 760), (x + 14, 690), (x + 28, 760)]), "#6a4a2a", shadow=0.4, seed=k,
                  edge=False, texture=False)

    def hall(ctx):
        # raised timber hall with a tiered roof
        sheet(ctx, path_poly([(500, 980), (1900, 980), (1900, 1010), (500, 1010)]), "#5a3a22", shadow=1.0, seed=40)
        for k in range(9):
            x = 560 + k * 165
            sheet(ctx, path_poly([(x, 980), (x + 26, 980), (x + 26, 560), (x, 560)]), "#7e3520", shadow=0.6, seed=41 + k)
        for k in range(3):
            w = 860 - k * 200
            y = 560 - k * 120
            sheet(ctx, path_poly(jag([(1200 - w, y), (1200 - w * 0.55, y - 140), (1200 + w * 0.55, y - 140),
                                      (1200 + w, y)], 3, 50 + k, 30)), ["#b08a4a", "#a8783a", "#c09a5a"][k], shadow=1.0,
                  seed=50 + k)
            PP.punch(ctx, path_poly([(1200 - w * 0.9, y - 10), (1200 + w * 0.9, y - 10), (1200 + w * 0.5, y - 120),
                                     (1200 - w * 0.5, y - 120)]), "lozenge", 60 + k, "#f6d8a0", 0.25, 7, 46)
        sheet(ctx, path_poly([(400, 1010), (2000, 1010), (2100, SH + 30), (300, SH + 30)]), "#c8a878", shadow=0.6,
              seed=70)
        overlay_texture(ctx, "weave", 0.0, 1.0, 1)

    layers = [(_key("pa_bg", tod=tod), bg, 0.2), (_key("pa_hall", tod=tod), hall, 0.6)]
    return dict(layers=layers, dyn=people_dyn(people or [], P, mouth_fn), dyn_depths=[0.2, 0.6])


# ================================================================ 7. TEMPLE / INSCRIPTION (Indian ideas)
def make_temple(tod="golden", people=None, mouth_fn=None, stele=True):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.55, (0.75, 0.35), 70, 7, 80)
        PP.ridge(ctx, P, 760, 60, mix(P["far"], P["haze"], 0.3), 81, peaks=[(500, 150, 200)])
        for i, x in enumerate((150, 380, 2100, 2300)):
            PP.palm(ctx, P, x, 860, 420 + (i % 2) * 80, "sugar", 82 + i, mix(P["mid"], P["near"], 0.5))

    def site(ctx):
        sheet(ctx, path_poly(jag([(-30, 900), (SW + 30, 900)], 3, 85) + [(SW + 30, SH + 30), (-30, SH + 30)]),
              "#b8945a", shadow=0.6, seed=85)
        PP.brick_shrine(ctx, P, 1200, 900, 520, 86)
        if stele:   # inscribed stone stele before the sanctuary
            sheet(ctx, path_poly([(1560, 1000), (1700, 1000), (1700, 760), (1680, 730), (1580, 730), (1560, 760)]),
                  "#7a7468", shadow=1.0, seed=87)
            src(ctx, "#4a4438", 0.7)
            ctx.set_line_width(2)
            R = rng(88)
            for k in range(14):
                y = 760 + k * 16
                x = 1580
                while x < 1680:
                    w = 6 + R.random() * 10
                    ctx.move_to(x, y)
                    ctx.line_to(x + w, y)
                    x += w + 4
                ctx.stroke()
        for k in range(6):
            PP.lotus(ctx, P, 300 + k * 360, 1260, 60, 0.8, 90 + k)

    layers = [(_key("te_bg", tod=tod), bg, 0.2), (_key("te_site", tod=tod, st=stele), site, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.6:
            for k in range(6):   # incense smoke
                ph = (t * 0.15 + k / 6) % 1
                src(ctx, "#e8e0d0", 0.18 * (1 - ph))
                ellipse(ctx, 1200 + math.sin(t + k) * 20 + ph * 40, 860 - ph * 300, 14 + ph * 50, 10 + ph * 40)
                ctx.fill()
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.2, 0.6])


# ================================================================ 8. WORKSHOP / MARKET (life and crafts)
def make_workshop(tod="day", people=None, mouth_fn=None):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.5, (0.3, 0.3), 60, 6, 100)
        PP.ridge(ctx, P, 760, 40, mix(P["far"], P["haze"], 0.3), 99)
        for k in range(6):
            PP.stilt_house(ctx, P, 160 + k * 420, 800, 130, 101 + k)

    def floor(ctx):
        sheet(ctx, path_poly(jag([(-30, 860), (SW + 30, 860)], 3, 110) + [(SW + 30, SH + 30), (-30, SH + 30)]),
              "#b8945a", shadow=0.6, seed=110)
        # awning
        sheet(ctx, path_poly([(500, 560), (1900, 560), (2000, 660), (400, 660)]), "#b5562f", shadow=1.0, seed=111)
        PP.punch(ctx, path_poly([(520, 570), (1880, 570), (1970, 650), (430, 650)]), "flower", 112, "#f6d8a0", 0.35, 10, 60)
        for x in (450, 1950):
            sheet(ctx, path_poly([(x - 10, 660), (x + 10, 660), (x + 10, 1100), (x - 10, 1100)]), "#5a3a22", shadow=0.6,
                  seed=x)
        # low tables with beads, gold and pots
        for k, x in enumerate((700, 1200, 1700)):
            sheet(ctx, path_poly([(x - 170, 1050), (x + 170, 1050), (x + 170, 1080), (x - 170, 1080)]), "#7a5a36",
                  shadow=0.8, seed=120 + k)
            R = rng(130 + k)
            for j in range(26):
                c = ["#c4502a", "#3f6fa8", "#e0b84a", "#2a7a6a", "#efe6d2"][j % 5]
                ellipse(ctx, x - 150 + R.random() * 300, 1040 - R.random() * 14, 7, 6)
                src(ctx, c)
                ctx.fill()
        for k in range(4):
            cast.pot(ctx, 1950 + k * 70, 1180, 50, ["#a8744a", "#8a5a3a"][k % 2], P)

    layers = [(_key("ws_bg", tod=tod), bg, 0.2), (_key("ws_floor", tod=tod), floor, 0.6)]
    return dict(layers=layers, dyn=people_dyn(people or [], P, mouth_fn), dyn_depths=[0.2, 0.6])


# ================================================================ 9. CHINESE MONASTERY (translation of sutras)
def make_monastery(people=None, mouth_fn=None):
    P = TOD["lamp"]

    def room(ctx):
        ctx.set_source(lin(0, 0, 0, SH, [(0, "#3a2414"), (1, "#1a100a")]))
        ctx.paint()
        for k in range(5):   # lattice windows
            x = 220 + k * 420
            sheet(ctx, path_poly([(x, 240), (x + 280, 240), (x + 280, 640), (x, 640)]), "#e8c890", shadow=0.8, seed=k)
            src(ctx, "#4a2a14")
            ctx.set_line_width(8)
            for j in range(1, 6):
                ctx.move_to(x + j * 280 / 6, 240)
                ctx.line_to(x + j * 280 / 6, 640)
                ctx.move_to(x, 240 + j * 400 / 6)
                ctx.line_to(x + 280, 240 + j * 400 / 6)
            ctx.stroke()
        sheet(ctx, path_poly([(0, 900), (SW, 900), (SW, SH), (0, SH)]), "#5a3a22", shadow=0.4, seed=9)
        for k in range(3):   # low writing tables with scrolls
            x = 600 + k * 600
            sheet(ctx, path_poly([(x - 200, 1000), (x + 200, 1000), (x + 200, 1030), (x - 200, 1030)]), "#3a2414",
                  shadow=0.8, seed=20 + k)
            sheet(ctx, path_poly([(x - 120, 990), (x + 120, 990), (x + 120, 1000), (x - 120, 1000)]), "#efe2c6", shadow=0.3,
                  seed=30 + k)

    layers = [(_key("mo_room"), room, 0.5)]

    def fx(ctx, t, d, depth):
        glow(ctx, 1200, 700, 900, "#ffb060", 0.12 + 0.02 * math.sin(t * 5))
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.5])


# ================================================================ 10. CHENLA: brick temples inland
def make_chenla(tod="golden", people=None, mouth_fn=None):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.55, (0.3, 0.35), 70, 7, 140)
        PP.ridge(ctx, P, 720, 90, mix(P["far"], P["haze"], 0.3), 141, peaks=[(1700, 160, 260)])
        tp = 760
        for i in range(30):
            x = i * 85
            sheet(ctx, path_ellipse(x, tp + (i % 3) * 10, 80, 60), mix(P["mid"], P["near"], (i % 4) * 0.2), shadow=0.6,
                  seed=150 + i, edge=False)

    def temples(ctx):
        sheet(ctx, path_poly(jag([(-30, 940), (SW + 30, 940)], 3, 160) + [(SW + 30, SH + 30), (-30, SH + 30)]),
              "#9a8a5a", shadow=0.6, seed=160)
        for k, (x, s) in enumerate(((700, 380), (1250, 520), (1800, 400))):
            PP.brick_shrine(ctx, P, x, 950, s, 170 + k)

    layers = [(_key("ch_bg", tod=tod), bg, 0.25), (_key("ch_t", tod=tod), temples, 0.6)]
    return dict(layers=layers, dyn=people_dyn(people or [], P, mouth_fn), dyn_depths=[0.25, 0.6])


# ===============================================================================================================
# ======================  FRENCH PROTECTORATE SETS (1863-1953)  =================================================
# All are artistic paper-cut reconstructions (badged recon). Real people/places use authentic photographs.

FR_BLUE = "#1f3f8c"
FR_RED = "#c8322a"
WALL = "#e4d7b4"
LAT = "#b5724a"   # laterite road / red earth


# ---------------------------------------------------------------- flags
def _wave(x, t, k):
    return math.sin(t * 2.2 + k) * 4 + math.sin(t * 3.7 + k) * 2


def _tricolor(ctx, x, y, w, t, pole=True):
    h = w * 0.66
    if pole:
        src(ctx, "#3a2a1a")
        ctx.rectangle(x - 3, y - h * 1.9, 6, h * 2.4)
        ctx.fill()
    for i, c in enumerate((FR_BLUE, "#f4efe4", FR_RED)):
        sw = _wave(x, t, i)
        poly(ctx, [(x + i * w / 3, y - h + sw), (x + (i + 1) * w / 3, y - h - sw * 0.5),
                   (x + (i + 1) * w / 3, y + sw * 0.5), (x + i * w / 3, y + sw)])
        src(ctx, c)
        ctx.fill()


def _khflag(ctx, x, y, w, t, pole=True):
    """Cambodian flag: blue / red (double) / blue bands with a white temple in the centre."""
    h = w * 0.62
    if pole:
        src(ctx, "#e8dcc0")
        ctx.rectangle(x - 4, y - h * 1.6, 8, h * 2.4)
        ctx.fill()
    bands = [(0.0, 0.25, FR_BLUE), (0.25, 0.75, FR_RED), (0.75, 1.0, FR_BLUE)]
    for a, b, c in bands:
        sw = _wave(x, t, a * 6)
        poly(ctx, [(x, y - h + h * a + sw), (x + w, y - h + h * a - sw * 0.6),
                   (x + w, y - h + h * b - sw * 0.6), (x, y - h + h * b + sw)])
        src(ctx, c)
        ctx.fill()
    # white three-tower temple glyph in the red band
    cx, cy = x + w * 0.5, y - h * 0.5
    src(ctx, "#f4efe4")
    for dx, th in ((-w * 0.11, h * 0.16), (0, h * 0.22), (w * 0.11, h * 0.16)):
        poly(ctx, [(cx + dx - w * 0.03, cy + h * 0.12), (cx + dx, cy - th), (cx + dx + w * 0.03, cy + h * 0.12)])
        ctx.fill()
    ctx.rectangle(cx - w * 0.14, cy + h * 0.1, w * 0.28, h * 0.05)
    ctx.fill()


# ---------------------------------------------------------------- French river gunboat (reconstruction)
def _steamboat(ctx, P, x, y, L, t, f=1, smoke=True):
    hull = "#33383f"
    bob = math.sin(t * 0.9) * L * 0.004
    y = y + bob
    pts = [(x - L * 0.5 * f, y - L * 0.05), (x - L * 0.46 * f, y + L * 0.05), (x + L * 0.44 * f, y + L * 0.05),
           (x + L * 0.52 * f, y - L * 0.02), (x + L * 0.48 * f, y - L * 0.06), (x - L * 0.46 * f, y - L * 0.06)]
    sheet(ctx, path_poly(pts, True), hull, shadow=0.9, seed=7)
    src(ctx, "#c23b33", 0.9)   # red waterline stripe
    ctx.rectangle(x - L * 0.46 * f, y + L * 0.02, L * 0.92 * f, L * 0.03)
    ctx.fill()
    # deckhouse amidships
    sheet(ctx, path_poly([(x - L * 0.22 * f, y - L * 0.06), (x + L * 0.2 * f, y - L * 0.06),
                          (x + L * 0.2 * f, y - L * 0.2), (x - L * 0.22 * f, y - L * 0.2)]), "#5a5e63", shadow=0.6, seed=8)
    src(ctx, "#1a1c20", 0.85)   # row of ports
    for k in range(5):
        ctx.rectangle(x - L * 0.18 * f + k * L * 0.08 * f, y - L * 0.16, L * 0.04, L * 0.05)
        ctx.fill()
    # funnel
    fx0 = x - L * 0.02 * f
    sheet(ctx, path_poly([(fx0 - L * 0.045, y - L * 0.2), (fx0 + L * 0.045, y - L * 0.2),
                          (fx0 + L * 0.04, y - L * 0.42), (fx0 - L * 0.04, y - L * 0.42)]), "#2a2d31", shadow=0.4, seed=9)
    src(ctx, "#c23b33", 0.85)
    ctx.rectangle(fx0 - L * 0.045, y - L * 0.4, L * 0.09, L * 0.03)
    ctx.fill()
    # mast + tricolor at the stern
    mx = x - L * 0.42 * f
    src(ctx, "#2a2a2a")
    ctx.set_line_width(max(1.5, L * 0.006))
    ctx.move_to(mx, y - L * 0.06)
    ctx.line_to(mx, y - L * 0.46)
    ctx.stroke()
    _tricolor(ctx, mx, y - L * 0.4, L * 0.16, t, pole=False)
    # bow gun
    gx = x + L * 0.42 * f
    src(ctx, "#1f2124")
    ctx.set_line_width(max(2, L * 0.02))
    ctx.move_to(gx, y - L * 0.09)
    ctx.line_to(gx + L * 0.12 * f, y - L * 0.11)
    ctx.stroke()
    if smoke:
        for k in range(7):
            ph = (t * 0.22 + k / 7.0) % 1.0
            a = 0.3 * (1 - ph)
            src(ctx, mix("#4a4a4a", P.get("haze", "#999999"), 0.3), a)
            rr = L * (0.05 + ph * 0.22)
            ellipse(ctx, fx0 - f * ph * L * 0.3 + math.sin(t + k) * 8, y - L * 0.46 - ph * L * 0.5, rr, rr * 0.8)
            ctx.fill()


# ================================================================ 11. RIVER AT DAWN (gunboat; opening, ch.1)
def make_river(tod="dawn", gunboat=True, people=None, mouth_fn=None, khflag=False):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.58, (0.42, 0.42), 70, 8, 210)
        PP.clouds(ctx, P, 6, (0.08, 0.34), 211)

    def far(ctx):
        PP.ridge(ctx, P, 770, 50, mix(P["far"], P["haze"], 0.4), 212)
        for i, x in enumerate(range(40, SW, 150)):
            PP.palm(ctx, P, x + (i % 3) * 24, 800, 110 + (i % 4) * 26, "sugar" if i % 2 else "coconut", 213 + i,
                    mix(P["far"], P["mid"], 0.45))
        if khflag:
            _khflag(ctx, 180, 790, 150, 0.0)

    def mid(ctx):
        PP.water(ctx, P, 840, SH + 40, 214)

    layers = [(_key("rv_sky", tod=tod), sky_, 0.0), (_key("rv_far", tod=tod, kf=khflag), far, 0.35),
              (_key("rv_mid", tod=tod), mid, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.35:
            _mist(ctx, t, 820, 110, P["haze"], 0.5, 2, 7)
            _birds(ctx, t, 500, 360, 6, P["shadow"])
        if depth == 0.6:
            PP.water_fx(ctx, t, P, 860, SH, 3, 16, 60)
            if gunboat:
                _steamboat(ctx, P, 760 + t * 7, 1040, 520, t, 1)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.35, 0.6, 1.0])


# ================================================================ 12. CARVER'S WORKSHOP (Kon Eth; opening, ch.5, closing)
def make_carver(tod="day", people=None, mouth_fn=None, panel="lotus"):
    P = TOD[tod]

    def bg(ctx):
        ctx.set_source(lin(0, 0, 0, SH, [(mix_k(P, 0), P["far"]), (0.6, mix(P["mid"], P["shadow"], 0.3)),
                                         (1, mix(P["shadow"], "#000000", 0.2))]) if False else
                       lin(0, 0, 0, SH, [(0, mix(P["far"], P["shadow"], 0.3)), (1, mix(P["shadow"], "#000000", 0.25))]))
        ctx.paint()
        # back wall of plank boards
        for k in range(14):
            x = k * 180
            sheet(ctx, path_poly([(x, 120), (x + 170, 120), (x + 170, 760), (x, 760)]),
                  mix("#7a5a36", P["shadow"], 0.2 + 0.05 * (k % 3)), shadow=0.3, seed=220 + k, edge=False)
        # a big carved pediment panel leaning on the wall (the apprentice's work)
        sheet(ctx, path_poly([(1430, 760), (2050, 760), (2050, 300), (1740, 180), (1430, 300)]), "#9a6a3a",
              shadow=1.0, seed=240)
        PP.punch(ctx, path_poly([(1500, 700), (1980, 700), (1980, 360), (1740, 250), (1500, 360)]), "flower", 241,
                 mix(P["light"], "#ffcf8a", 0.4), 0.3, 11, 64)

    def floor(ctx):
        sheet(ctx, path_poly([(-30, 860), (SW + 30, 860), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix("#8a6a3c", P["shadow"], 0.1), shadow=0.5, seed=250)
        # workbench
        sheet(ctx, path_poly([(360, 1040), (1180, 1040), (1180, 1080), (360, 1080)]), "#6a4a28", shadow=0.9, seed=251)
        for x in (420, 1120):
            sheet(ctx, path_poly([(x - 14, 1080), (x + 14, 1080), (x + 14, SH), (x - 14, SH)]), "#4a3018", shadow=0.5,
                  seed=int(x))
        # a small wooden panel being carved on the bench
        sheet(ctx, path_poly([(560, 1030), (980, 1030), (980, 900), (560, 900)]), "#b5844a", shadow=0.6, seed=252)
        if panel == "lotus":
            PP.lotus(ctx, P, 770, 1010, 70, 0.9, 253)
        # wood shavings + chisels
        R = rng(254)
        for k in range(22):
            x = 380 + R.random() * 820
            src(ctx, mix("#d8b47a", P["shadow"], R.random() * 0.3), 0.7)
            ctx.new_path()
            ctx.arc(x, 1110 + R.random() * 120, 6 + R.random() * 8, 0, 3.14)
            ctx.fill()

    layers = [(_key("cv_bg", tod=tod, p=panel), bg, 0.3), (_key("cv_floor", tod=tod, p=panel), floor, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.3:
            glow(ctx, 600, 500, 700, "#ffcf8a", 0.1 + 0.02 * math.sin(t * 3))
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.3, 0.6])


def mix_k(P, k):
    return 0.0


# ---------------------------------------------------------------- colonial architecture helpers
def _colonial_building(ctx, P, x, y, w, h, seed=0, col=None):
    """A French colonial shophouse/villa: arcaded ground floor, shuttered upper windows, cornice."""
    col = col or mix(WALL, P["mid"], 0.12)
    sheet(ctx, path_poly([(x, y), (x + w, y), (x + w, y - h), (x, y - h)]), col, shadow=0.9, seed=seed)
    # cornice
    sheet(ctx, path_poly([(x - 10, y - h), (x + w + 10, y - h), (x + w + 10, y - h - 24), (x - 10, y - h - 24)]),
          mix(col, P["light"], 0.2), shadow=0.5, seed=seed + 1, edge=False)
    # ground-floor arcade
    narch = max(2, int(w / 150))
    aw = w / narch
    for k in range(narch):
        ax = x + k * aw + aw * 0.5
        src(ctx, mix(col, "#1a120c", 0.6), 0.9)
        ctx.new_path()
        ctx.arc(ax, y - h * 0.34, aw * 0.32, math.pi, 2 * math.pi)
        ctx.rectangle(ax - aw * 0.32, y - h * 0.34, aw * 0.64, h * 0.34)
        ctx.fill()
    # upper shuttered windows
    for k in range(narch):
        wx = x + k * aw + aw * 0.5
        sheet(ctx, path_poly([(wx - aw * 0.22, y - h * 0.5), (wx + aw * 0.22, y - h * 0.5),
                              (wx + aw * 0.22, y - h * 0.84), (wx - aw * 0.22, y - h * 0.84)]),
              mix("#6a7a6a", P["shadow"], 0.2), shadow=0.4, seed=seed + 5 + k, edge=False)
        src(ctx, mix("#4a5a4a", "#000000", 0.2), 0.7)
        for j in range(4):
            yy = y - h * 0.52 - j * h * 0.08
            ctx.rectangle(wx - aw * 0.2, yy, aw * 0.4, h * 0.02)
            ctx.fill()
    # tiled roof hint
    sheet(ctx, path_poly([(x - 16, y - h - 24), (x + w + 16, y - h - 24), (x + w - 30, y - h - 74),
                          (x + 30, y - h - 74)]), "#9a4a32", shadow=0.7, seed=seed + 9)


def _market_dome(ctx, P, x, y, s, seed=0):
    """Phsar Thmei central market: a great ochre art-deco dome over an arched hall (reconstruction)."""
    col = mix("#d6b45a", P["mid"], 0.1)
    # hall
    sheet(ctx, path_poly([(x - s, y), (x + s, y), (x + s, y - s * 0.6), (x - s, y - s * 0.6)]), col, shadow=0.9, seed=seed)
    # big central arch
    src(ctx, mix(col, "#2a1c10", 0.7), 0.92)
    ctx.new_path()
    ctx.arc(x, y - s * 0.3, s * 0.34, math.pi, 2 * math.pi)
    ctx.rectangle(x - s * 0.34, y - s * 0.3, s * 0.68, s * 0.3)
    ctx.fill()
    # stepped dome
    for k in range(5):
        r = s * (0.92 - k * 0.17)
        yy = y - s * 0.6 - k * s * 0.24
        sheet(ctx, path_poly([(x - r, yy), (x + r, yy), (x + r * 0.9, yy - s * 0.22), (x - r * 0.9, yy - s * 0.22)]),
              mix(col, P["light"], 0.06 * k), shadow=0.6, seed=seed + 2 + k)
    # finial
    sheet(ctx, path_poly([(x - s * 0.04, y - s * 1.9), (x + s * 0.04, y - s * 1.9), (x, y - s * 2.1)]),
          mix(col, P["light"], 0.3), shadow=0.3, seed=seed + 8, edge=False)


def _angkor_tower(ctx, P, x, y, s, seed=0, col=None):
    """Lotus-bud 'corn-cob' prasat of Angkor Wat (reconstruction)."""
    col = col or mix("#8a8470", P["mid"], 0.15)
    sheet(ctx, path_poly([(x - s * 0.36, y), (x + s * 0.36, y), (x + s * 0.3, y - s * 1.3), (x - s * 0.3, y - s * 1.3)]),
          col, shadow=0.8, seed=seed)
    for k in range(5):
        w = s * (0.34 - k * 0.05)
        yy = y - s * 1.3 - k * s * 0.3
        sheet(ctx, path_poly([(x - w, yy), (x + w, yy), (x + w * 0.8, yy - s * 0.3), (x - w * 0.8, yy - s * 0.3)]),
              mix(col, P["light"], 0.05 * k), shadow=0.5, seed=seed + 1 + k)
    # lotus-bud finial
    sheet(ctx, path_ellipse(x, y - s * 2.95, s * 0.1, s * 0.22), mix(col, P["light"], 0.2), shadow=0.3, seed=seed + 7,
          edge=False)


# ================================================================ 13. COLONIAL PHNOM PENH (ch.3, 7, 8)
def make_town(tod="day", people=None, mouth_fn=None, variant="street"):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.5, (0.72, 0.28), 60, 7, 300)
        PP.clouds(ctx, P, 6, (0.05, 0.3), 301)

    def blocks(ctx):
        PP.ridge(ctx, P, 720, 30, mix(P["far"], P["haze"], 0.45), 302)
        if variant == "market":
            _market_dome(ctx, P, 1200, 900, 300, 310)
            _colonial_building(ctx, P, 120, 900, 420, 360, 320)
            _colonial_building(ctx, P, 1880, 900, 420, 360, 330)
        else:
            _colonial_building(ctx, P, 90, 900, 520, 400, 320)
            _colonial_building(ctx, P, 700, 900, 460, 360, 328)
            _colonial_building(ctx, P, 1260, 900, 520, 400, 334)
            _colonial_building(ctx, P, 1880, 900, 460, 380, 340)

    def street(ctx):
        sheet(ctx, path_poly(jag([(-30, 980), (SW + 30, 980)], 3, 350) + [(SW + 30, SH + 30), (-30, SH + 30)]),
              mix(LAT, P["shadow"], 0.12), shadow=0.4, seed=350)
        for i, x in enumerate((60, 760, 1560, 2320)):   # tamarind / sugar street trees
            PP.palm(ctx, P, x, 1010, 420 + (i % 2) * 70, "sugar", 352 + i, mix(P["mid"], P["near"], 0.4))

    layers = [(_key("tn_sky", tod=tod), sky_, 0.0), (_key("tn_blk", tod=tod, v=variant), blocks, 0.4),
              (_key("tn_st", tod=tod), street, 0.7)]

    def fx(ctx, t, d, depth):
        if depth == 0.4:
            _birds(ctx, t, 800, 300, 5, P["shadow"])
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.4, 0.7])


# ================================================================ 14. ROYAL PALACE, PHNOM PENH (ch.1, 9)
def make_rpalace(tod="golden", people=None, mouth_fn=None):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.5, (0.3, 0.3), 60, 7, 360)
        PP.clouds(ctx, P, 5, (0.05, 0.3), 361)
        # crenellated wall
        sheet(ctx, path_poly([(-30, 820), (SW + 30, 820), (SW + 30, 900), (-30, 900)]),
              mix("#e8d070", P["mid"], 0.1), shadow=0.7, seed=362)

    def hall(ctx):
        base = mix("#f0d888", P["mid"], 0.08)
        # throne-hall body
        sheet(ctx, path_poly([(620, 1000), (1780, 1000), (1780, 640), (620, 640)]), base, shadow=1.0, seed=363)
        # colonnade
        for k in range(9):
            x = 680 + k * 130
            sheet(ctx, path_poly([(x - 18, 1000), (x + 18, 1000), (x + 18, 660), (x - 18, 660)]),
                  mix(base, P["shadow"], 0.2), shadow=0.3, seed=364 + k, edge=False)
        # tiered roof
        for k in range(3):
            w = 640 - k * 150
            yy = 640 - k * 90
            sheet(ctx, path_poly([(1200 - w, yy), (1200 - w * 0.6, yy - 110), (1200 + w * 0.6, yy - 110),
                                  (1200 + w, yy)]), ["#e08a3a", "#d87a30", "#c86a26"][k], shadow=0.9, seed=370 + k)
        # central spire (prasat) + finial
        for k in range(5):
            w = 120 - k * 18
            yy = 370 - k * 54
            sheet(ctx, path_poly([(1200 - w, yy), (1200 + w, yy), (1200 + w * 0.78, yy - 54),
                                  (1200 - w * 0.78, yy - 54)]), mix("#e0b84a", P["light"], 0.06 * k), shadow=0.5,
                  seed=376 + k)
        sheet(ctx, path_poly([(1190, 110), (1210, 110), (1200, 30)]), "#f0d888", shadow=0.3, seed=382, edge=False)
        # ground terrace
        sheet(ctx, path_poly([(400, 1000), (2000, 1000), (2100, SH + 30), (300, SH + 30)]),
              mix("#d8c088", P["shadow"], 0.1), shadow=0.6, seed=383)

    layers = [(_key("rp_bg", tod=tod), bg, 0.2), (_key("rp_hall", tod=tod), hall, 0.6)]
    return dict(layers=layers, dyn=people_dyn(people or [], P, mouth_fn), dyn_depths=[0.2, 0.6])


# ================================================================ 15. RUBBER PLANTATION (ch.6, darker)
def make_plantation(tod="dusk", people=None, mouth_fn=None):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.42, (0.3, 0.22), 50, 6, 400)
        PP.clouds(ctx, P, 7, (0.04, 0.28), 401, col=mix(P["haze"], "#000000", 0.2))

    def grove(ctx):
        sheet(ctx, path_poly([(-30, 740), (SW + 30, 740), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix(LAT, P["shadow"], 0.3), shadow=0.4, seed=402)
        # receding rows of rubber trees
        for row in range(4):
            yy = 760 + row * 150
            hh = 420 + row * 240
            n = 5 + row * 2
            c = mix("#cdb89a", P["shadow"], 0.15 + row * 0.12)
            for k in range(n):
                x = (SW / n) * (k + 0.5) + (row % 2) * 60
                _rubber_tree(ctx, P, x, yy + hh * 0.0, hh, 410 + row * 9 + k, c)

    layers = [(_key("pl_sky", tod=tod), sky_, 0.0), (_key("pl_grove", tod=tod), grove, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.6:
            _mist(ctx, t, 1150, 90, P["haze"], 0.35, 4, 6)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.6])


def _rubber_tree(ctx, P, x, y, h, seed=0, col="#cdb89a"):
    sheet(ctx, path_poly([(x - h * 0.02, y), (x - h * 0.015, y - h * 0.62), (x + h * 0.015, y - h * 0.62),
                          (x + h * 0.02, y)]), mix(col, "#000000", 0.08), shadow=0.5, seed=seed, edge=False)
    # tapping spiral + latex cup
    src(ctx, mix(col, "#5a3a20", 0.6), 0.8)
    ctx.set_line_width(max(1.2, h * 0.006))
    ctx.move_to(x - h * 0.018, y - h * 0.18)
    ctx.line_to(x + h * 0.016, y - h * 0.28)
    ctx.stroke()
    sheet(ctx, path_ellipse(x + h * 0.02, y - h * 0.14, h * 0.02, h * 0.025), "#d8cbb0", shadow=0.3, seed=seed + 1,
          edge=False)
    # sparse canopy
    R = rng(seed + 2)
    for k in range(5):
        cx = x + (R.random() - 0.5) * h * 0.4
        cy = y - h * 0.62 - R.random() * h * 0.3
        sheet(ctx, path_ellipse(cx, cy, h * 0.14, h * 0.1), mix(P["mid"], "#3a4a2a", 0.4), shadow=0.3, seed=seed + 3 + k,
              edge=False)


# ================================================================ 16. ANGKOR WAT (ch.5)
def make_angkor(tod="golden", people=None, mouth_fn=None):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.55, (0.5, 0.32), 80, 8, 440)
        PP.clouds(ctx, P, 6, (0.05, 0.34), 441)

    def temple(ctx):
        PP.ridge(ctx, P, 720, 30, mix(P["far"], P["haze"], 0.45), 442)
        # gallery base
        sheet(ctx, path_poly([(260, 900), (2140, 900), (2140, 760), (260, 760)]), mix("#8a8470", P["mid"], 0.12),
              shadow=0.9, seed=443)
        _angkor_tower(ctx, P, 1200, 760, 260, 450)          # central
        for dx, sc in ((-540, 0.74), (540, 0.74), (-900, 0.6), (900, 0.6)):
            _angkor_tower(ctx, P, 1200 + dx, 760, 260 * sc, 455 + int(dx))
        # causeway
        sheet(ctx, path_poly([(1040, 900), (1360, 900), (1460, SH + 30), (940, SH + 30)]),
              mix("#9a8a5a", P["shadow"], 0.1), shadow=0.5, seed=470)

    def moat(ctx):
        PP.water(ctx, P, 1000, SH + 30, 471, mix(P["water"], P["haze"], 0.2), 4)

    layers = [(_key("ag_sky", tod=tod), sky_, 0.0), (_key("ag_t", tod=tod), temple, 0.5),
              (_key("ag_moat", tod=tod), moat, 0.75)]

    def fx(ctx, t, d, depth):
        if depth == 0.75:
            PP.water_fx(ctx, t, P, 1020, SH, 5, 12, 40)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)),
                dyn_depths=[0.0, 0.5, 0.75, 0.8])


# ================================================================ 17. INTERIOR: signing / press / institute (ch.1,3,8)
def make_office(tod="lamp", variant="sign", people=None, mouth_fn=None):
    P = TOD[tod]

    def room(ctx):
        ctx.set_source(lin(0, 0, 0, SH, [(0, mix("#6a5238", P["shadow"], 0.2)), (1, mix(P["shadow"], "#000000", 0.2))]))
        ctx.paint()
        # shuttered window with light
        for wx in (360, 2040):
            sheet(ctx, path_poly([(wx - 150, 240), (wx + 150, 240), (wx + 150, 640), (wx - 150, 640)]),
                  mix(P["light"], "#c89a5a", 0.4), shadow=0.6, seed=480)
            src(ctx, "#3a2a1a")
            ctx.set_line_width(8)
            for j in range(1, 7):
                ctx.move_to(wx - 150, 240 + j * 400 / 7)
                ctx.line_to(wx + 150, 240 + j * 400 / 7)
            ctx.stroke()
        # wainscot wall + floor
        sheet(ctx, path_poly([(0, 820), (SW, 820), (SW, SH), (0, SH)]), mix("#5a3a22", P["shadow"], 0.15), shadow=0.4,
              seed=481)
        # a long table
        sheet(ctx, path_poly([(560, 1040), (1840, 1040), (1840, 1086), (560, 1086)]), "#3a281a", shadow=1.0, seed=482)
        for x in (640, 1760):
            sheet(ctx, path_poly([(x - 16, 1086), (x + 16, 1086), (x + 16, SH), (x - 16, SH)]), "#241810", shadow=0.4,
                  seed=int(x) + 1)
        if variant == "sign":   # the treaty: two documents + an inkwell on the table
            for dx in (-220, 220):
                sheet(ctx, path_poly([(1200 + dx - 120, 1035), (1200 + dx + 120, 1035), (1200 + dx + 120, 965),
                                      (1200 + dx - 120, 965)]), "#efe6cc", shadow=0.4, seed=483)
                src(ctx, "#6a5a40", 0.6)
                ctx.set_line_width(2)
                for j in range(5):
                    ctx.move_to(1200 + dx - 100, 985 + j * 10)
                    ctx.line_to(1200 + dx + 100, 985 + j * 10)
                ctx.stroke()
            src(ctx, "#c23b33", 0.85)   # red wax seal
            ctx.arc(1200 + 90, 1020, 16, 0, 6.283)
            ctx.fill()
        elif variant == "press":   # newspaper: stacked printed sheets + a press hint
            for k in range(4):
                sheet(ctx, path_poly([(900 - k * 6, 1035 - k * 14), (1160 - k * 6, 1035 - k * 14),
                                      (1160 - k * 6, 965 - k * 14), (900 - k * 6, 965 - k * 14)]), "#eee4cc",
                      shadow=0.3, seed=484 + k)
            sheet(ctx, path_poly([(1340, 1040), (1720, 1040), (1720, 720), (1340, 720)]), "#2a2d31", shadow=0.8,
                  seed=490)
        elif variant == "institute":   # reading room: palm-leaf manuscripts + books
            for k in range(5):
                x = 720 + k * 180
                sheet(ctx, path_poly([(x - 70, 1030), (x + 70, 1030), (x + 70, 1006), (x - 70, 1006)]), "#c8a860",
                      shadow=0.3, seed=492 + k)

    layers = [(_key("of_room", tod=tod, v=variant), room, 0.5)]

    def fx(ctx, t, d, depth):
        if depth == 0.5:
            glow(ctx, 1200, 620, 820, "#ffcf8a", 0.1 + 0.02 * math.sin(t * 4))
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.5, 0.6])


# ================================================================ 18. UMBRELLA PROTEST (ch.9)
def make_protest(tod="day", people=None, mouth_fn=None):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.46, (0.3, 0.3), 55, 7, 500)
        PP.clouds(ctx, P, 7, (0.04, 0.28), 501, col=mix(P["haze"], "#000000", 0.15))

    def plaza(ctx):
        _colonial_building(ctx, P, 160, 820, 2080, 420, 510)
        _tricolor(ctx, 1200, 430, 150, 0.0)
        sheet(ctx, path_poly([(-30, 900), (SW + 30, 900), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix(LAT, P["shadow"], 0.1), shadow=0.4, seed=520)
        # a crowd of saffron umbrellas in the mid-ground
        R = rng(521)
        for k in range(14):
            x = 180 + k * 150 + R.random() * 40
            y = 1120 + (k % 3) * 36
            _umbrella(ctx, x, y, 90 + (k % 3) * 14, mix("#d8902e", P["shadow"], 0.1 * (k % 3)))

    layers = [(_key("pr_sky", tod=tod), sky_, 0.0), (_key("pr_plaza", tod=tod), plaza, 0.55)]
    return dict(layers=layers, dyn=people_dyn(people or [], P, mouth_fn), dyn_depths=[0.0, 0.55])


def _umbrella(ctx, x, y, s, col):
    sheet(ctx, path_poly([(x - s, y), (x + s, y), (x + s * 0.7, y - s * 0.5), (x, y - s * 0.62),
                          (x - s * 0.7, y - s * 0.5)], True), col, shadow=0.5, seed=int(x))
    src(ctx, "#3a2a1a")
    ctx.set_line_width(max(2, s * 0.04))
    ctx.move_to(x, y - s * 0.55)
    ctx.line_to(x, y + s * 0.5)
    ctx.stroke()


# ================================================================ 19. INDEPENDENCE MONUMENT (closing, ch.11)
def make_monument(tod="dawn", people=None, mouth_fn=None, flag=True):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.6, (0.5, 0.4), 90, 8, 560)
        PP.clouds(ctx, P, 5, (0.08, 0.34), 561)

    def plaza(ctx):
        PP.ridge(ctx, P, 780, 28, mix(P["far"], P["haze"], 0.5), 562)
        for i, x in enumerate((120, 2280)):
            PP.palm(ctx, P, x, 900, 520, "sugar", 563 + i, mix(P["mid"], P["near"], 0.4))
        # boulevard
        sheet(ctx, path_poly([(-30, 1040), (SW + 30, 1040), (SW + 30, SH + 30), (-30, SH + 30)]),
              mix(LAT, P["shadow"], 0.08), shadow=0.4, seed=564)
        _monument(ctx, P, 1200, 1040, 300, 570)
        if flag:
            _khflag(ctx, 420, 1000, 150, 0.0)
            _khflag(ctx, 1980, 1000, 150, 0.0)

    layers = [(_key("mn_sky", tod=tod), sky_, 0.0), (_key("mn_plaza", tod=tod, fl=flag), plaza, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.6:
            glow(ctx, 1200, 500, 620, P["sun"], 0.16 + 0.03 * math.sin(t * 2))
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.6])


def _monument(ctx, P, x, y, s, seed=0):
    """Independence Monument (Vann Molyvann, 1958): a tall lotus-tiered sandstone tower on a cruciform base."""
    red = mix("#9a4038", P["mid"], 0.08)
    # cruciform stepped base
    for k in range(3):
        w = s * (1.1 - k * 0.22)
        yy = y - k * s * 0.16
        sheet(ctx, path_poly([(x - w, yy), (x + w, yy), (x + w, yy - s * 0.16), (x - w, yy - s * 0.16)]),
              mix(red, P["light"], 0.04 * k), shadow=0.8, seed=seed + k)
    by = y - s * 0.48
    # tower body
    sheet(ctx, path_poly([(x - s * 0.5, by), (x + s * 0.5, by), (x + s * 0.44, by - s * 0.5), (x - s * 0.44, by - s * 0.5)]),
          red, shadow=0.9, seed=seed + 4)
    # five receding lotus tiers, each ringed with naga-finials (hinted)
    for k in range(5):
        w = s * (0.44 - k * 0.055)
        yy = by - s * 0.5 - k * s * 0.34
        sheet(ctx, path_poly([(x - w, yy), (x + w, yy), (x + w * 0.82, yy - s * 0.34), (x - w * 0.82, yy - s * 0.34)]),
              mix(red, P["light"], 0.05 * k), shadow=0.6, seed=seed + 6 + k)
        # naga horns at the corners
        src(ctx, mix(red, "#000000", 0.3))
        for sg in (-1, 1):
            ctx.move_to(x + sg * w, yy)
            ctx.line_to(x + sg * w * 1.14, yy - s * 0.1)
            ctx.line_to(x + sg * w * 0.96, yy - s * 0.06)
            ctx.close_path()
        ctx.fill()
    # lotus finial
    sheet(ctx, path_ellipse(x, by - s * 0.5 - 5 * s * 0.34 - s * 0.16, s * 0.07, s * 0.2),
          mix(red, P["light"], 0.25), shadow=0.3, seed=seed + 12, edge=False)


# ===============================================================================================================
# ======================  1945: THE JAPANESE PERIOD  ============================================================
TOD["storm"] = dict(sky0="#10141e", sky1="#3a4458", sun="#c8d0e0", water="#26303c", far="#323c4c", mid="#222c36",
                    near="#121a22", light="#b8c4d8", shadow="#06080c", haze="#4a5466")
TOD["rainy"] = dict(sky0="#5a6470", sky1="#a8aeb4", sun="#e0e2e4", water="#55646a", far="#7c868c", mid="#4e5e58",
                    near="#2c3a36", light="#e4e8ea", shadow="#1c2428", haze="#9aa2a8")
TOD["heat"] = dict(sky0="#c89a4a", sky1="#f4e2b0", sun="#fff6d8", water="#8a8458", far="#c8a878", mid="#8a8048",
                   near="#4a4a2a", light="#fff0c8", shadow="#4a3a22", haze="#ecd8a8")
KHAKI = "#7a7248"


def with_rain(scene, amt=1.0, lightning=False, seed=7):
    """Overlay monsoon rain (and optional lightning flashes) on any scene."""
    base = scene.get("dyn")
    depths = list(scene.get("dyn_depths", []))

    def dyn(ctx, t, d, depth):
        if base:
            base(ctx, t, d, depth)
        if depth != 1.3:
            return
        R = rng(seed)
        n = int(260 * amt)
        ctx.set_line_width(2)
        for i in range(n):
            x0 = R.random() * (SW + 400) - 200
            sp = 900 + R.random() * 500
            y = (R.random() * SH + t * sp) % (SH + 200) - 100
            L = 30 + R.random() * 40
            src(ctx, "#d8e0ea", 0.18 + 0.2 * R.random())
            ctx.move_to(x0 + y * 0.12, y)
            ctx.line_to(x0 + (y + L) * 0.12, y + L)
            ctx.stroke()
        if lightning:
            for k in range(6):
                tk = 1.3 + k * 3.7 + (k * 1.9) % 1.3
                a = max(0.0, 1 - abs(t - tk) / 0.12) * 0.5 + max(0.0, 1 - abs(t - tk - 0.22) / 0.08) * 0.3
                if a > 0:
                    src(ctx, "#e8eeff", a)
                    ctx.rectangle(-SW, -SH, SW * 3, SH * 3)
                    ctx.fill()
    return dict(scene, dyn=dyn, dyn_depths=depths + [1.3])


def _truck(ctx, P, x, y, L, t, f=1, lights=True):
    """Military truck with a canvas-covered bed (generic WWII type; reconstruction)."""
    body = mix(KHAKI, P["shadow"], 0.25)
    bob = math.sin(t * 9 + x * 0.01) * L * 0.004
    y = y + bob
    sheet(ctx, path_poly([(x - L * 0.5 * f, y - L * 0.08), (x + L * 0.15 * f, y - L * 0.08),
                          (x + L * 0.15 * f, y - L * 0.36), (x - L * 0.5 * f, y - L * 0.36)], ), mix(body, "#c8b890", 0.15),
          shadow=0.6, seed=601)
    for k in range(4):   # canvas hoops
        hx = x - L * 0.45 * f + k * L * 0.18 * f
        src(ctx, mix(body, "#000000", 0.3), 0.6)
        ctx.set_line_width(max(1.5, L * 0.008))
        ctx.move_to(hx, y - L * 0.08)
        ctx.line_to(hx, y - L * 0.36)
        ctx.stroke()
    cab = [(x + L * 0.16 * f, y - L * 0.06), (x + L * 0.42 * f, y - L * 0.06), (x + L * 0.46 * f, y - L * 0.16),
           (x + L * 0.36 * f, y - L * 0.3), (x + L * 0.16 * f, y - L * 0.3)]
    sheet(ctx, path_poly(cab), body, shadow=0.6, seed=602)
    src(ctx, "#1a1e22", 0.85)
    poly(ctx, [(x + L * 0.22 * f, y - L * 0.2), (x + L * 0.33 * f, y - L * 0.2), (x + L * 0.37 * f, y - L * 0.27),
               (x + L * 0.22 * f, y - L * 0.27)])
    ctx.fill()
    src(ctx, "#2a2a2a")
    ctx.rectangle(min(x - L * 0.5 * f, x + L * 0.46 * f), y - L * 0.09, L * 0.96, L * 0.04)
    ctx.fill()
    for wx in (-0.36, -0.2, 0.32):
        cx = x + wx * L * f
        src(ctx, "#141414")
        ctx.new_path()
        ctx.arc(cx, y - L * 0.02, L * 0.065, 0, 6.283)
        ctx.fill()
        src(ctx, "#5a5a5a")
        ctx.new_path()
        ctx.arc(cx, y - L * 0.02, L * 0.025, 0, 6.283)
        ctx.fill()
    if lights:
        hx, hy = x + L * 0.46 * f, y - L * 0.11
        glow(ctx, hx + L * 0.25 * f, hy + L * 0.03, L * 0.5, "#ffe8a8", 0.35)
        src(ctx, "#fff4c8")
        ctx.new_path()
        ctx.arc(hx, hy, L * 0.02, 0, 6.283)
        ctx.fill()


def _flag_on_pole(ctx, x, top, w, t, d, kind, mode):
    """kind: tricolor | khflag ; mode: up | lower | raise."""
    h = w * 0.64
    src(ctx, "#e8e0cc")
    ctx.rectangle(x - 5, top - 20, 10, 520)
    ctx.fill()
    p = smooth(clamp((t - 0.8) / max(0.1, d - 2.5)))
    if mode == "lower":
        fy = top + h + p * 380
    elif mode == "raise":
        fy = top + h + (1 - p) * 380
    else:
        fy = top + h
    {"tricolor": _tricolor, "khflag": _khflag, "kh45": _khflag45}[kind](ctx, x + 5, fy, w, t, pole=False)


def _khflag45(ctx, x, y, w, t, pole=True):
    """Cambodian flag in use 1863-1948 (and in 1945): red field, blue border, white Angkor Wat."""
    h = w * 0.64
    b = h * 0.12
    for (a0, a1, c) in ((0.0, 1.0, FR_BLUE),):
        sw = _wave(x, t, 1)
        poly(ctx, [(x, y - h + sw), (x + w, y - h - sw * 0.6), (x + w, y - sw * 0.6), (x, y + sw)])
        src(ctx, c)
        ctx.fill()
    sw = _wave(x, t, 2)
    poly(ctx, [(x + b, y - h + b + sw), (x + w - b, y - h + b - sw * 0.6), (x + w - b, y - b - sw * 0.6),
               (x + b, y - b + sw)])
    src(ctx, FR_RED)
    ctx.fill()
    cx, cy = x + w * 0.5, y - h * 0.48
    src(ctx, "#f4efe4")
    for dx, th in ((-w * 0.12, h * 0.15), (-w * 0.06, h * 0.19), (0, h * 0.25), (w * 0.06, h * 0.19), (w * 0.12, h * 0.15)):
        poly(ctx, [(cx + dx - w * 0.025, cy + h * 0.12), (cx + dx, cy - th), (cx + dx + w * 0.025, cy + h * 0.12)])
        ctx.fill()
    ctx.rectangle(cx - w * 0.17, cy + h * 0.1, w * 0.34, h * 0.05)
    ctx.fill()


# ================================================================ 20. PHNOM PENH RIVERFRONT (opening, ch.2, 7, 10)
def make_riverfront(tod="storm", trucks=0, flag=None, flag_mode="up", people=None, mouth_fn=None, rain=0.0,
                    lightning=False, spire=True):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.5, (0.78, 0.22), 50, 7, 640)
        PP.clouds(ctx, P, 8, (0.04, 0.3), 641, col=mix(P["haze"], P["shadow"], 0.25))

    def town(ctx):
        PP.ridge(ctx, P, 700, 24, mix(P["far"], P["haze"], 0.4), 642)
        if spire:   # the Royal Palace throne-hall spire beyond the quay
            for k in range(5):
                w = 70 - k * 11
                yy = 560 - k * 46
                sheet(ctx, path_poly([(1180 - w, yy), (1180 + w, yy), (1180 + w * 0.78, yy - 46),
                                      (1180 - w * 0.78, yy - 46)]), mix("#c8a050", P["mid"], 0.35), shadow=0.4,
                      seed=650 + k)
        _colonial_building(ctx, P, 60, 860, 560, 340, 660, col=mix(WALL, P["shadow"], 0.35))
        _colonial_building(ctx, P, 1460, 860, 480, 320, 670, col=mix(WALL, P["shadow"], 0.38))
        _colonial_building(ctx, P, 1980, 860, 440, 300, 680, col=mix(WALL, P["shadow"], 0.4))
        for i, x in enumerate((700, 860, 1040, 1320)):
            PP.palm(ctx, P, x, 880, 300 + (i % 2) * 60, "sugar", 690 + i, mix(P["mid"], P["near"], 0.4))

    def quay(ctx):
        sheet(ctx, path_poly([(-30, 860), (SW + 30, 860), (SW + 30, 1110), (-30, 1110)]),
              mix(LAT, P["shadow"], 0.45), shadow=0.4, seed=700)
        src(ctx, mix(LAT, "#ffffff", 0.1), 0.25)
        for k in range(30):
            ctx.rectangle(k * 90, 1100, 60, 6)
            ctx.fill()

    def river(ctx):
        PP.water(ctx, P, 1110, SH + 40, 701, mix(P["water"], P["shadow"], 0.2), 4)

    layers = [(_key("rf_sky", tod=tod), sky_, 0.0), (_key("rf_town", tod=tod, sp=spire), town, 0.4),
              (_key("rf_quay", tod=tod), quay, 0.6), (_key("rf_river", tod=tod), river, 0.85)]

    def fx(ctx, t, d, depth):
        if depth == 0.4 and flag:
            _flag_on_pole(ctx, 1700, 360, 150, t, d, flag, flag_mode)
        if depth == 0.6:
            for k in range(trucks):
                x = (-400 + t * 120 + k * 760) % (SW + 900) - 450
                _truck(ctx, P, x, 1060, 520, t + k, 1, lights=tod in ("storm", "night", "dusk"))
        if depth == 0.85:
            PP.water_fx(ctx, t, P, 1130, SH, 9, 16, 50)
    sc = dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.4, 0.6, 0.85])
    return with_rain(sc, rain, lightning) if rain else sc


# ================================================================ 21. DESK DOCUMENTS (proclamation, ballot)
def make_desk(tod="lamp", variant="proclaim", people=None, mouth_fn=None):
    """Close view of a desk: a typed proclamation beside a palm-leaf manuscript, or referendum ballots."""
    P = TOD[tod]

    def desk(ctx):
        ctx.set_source(lin(0, 0, 0, SH, [(0, "#2a1e14"), (1, "#120c08")]))
        ctx.paint()
        sheet(ctx, path_poly([(-30, 520), (SW + 30, 520), (SW + 30, SH + 30), (-30, SH + 30)]), "#5a3a22", shadow=0.3,
              seed=720)
        if variant == "proclaim":
            # typed proclamation
            sheet(ctx, path_poly([(1180, 600), (1880, 580), (1900, 1260), (1200, 1280)]), "#efe6cc", shadow=1.0, seed=721)
            src(ctx, "#2a2420", 0.75)
            R = rng(722)
            for j in range(22):
                yy = 690 + j * 24
                x = 1250
                while x < 1820:
                    w = 10 + R.random() * 34
                    ctx.rectangle(x, yy - 0.012 * (x - 1200), w, 7)
                    x += w + 8
                ctx.fill()
            src(ctx, "#b03028", 0.85)   # royal seal
            ctx.new_path()
            ctx.arc(1760, 1180, 42, 0, 6.283)
            ctx.fill()
            # palm-leaf manuscript bundle
            for k in range(7):
                yy = 760 + k * 34
                sheet(ctx, path_poly([(300, yy), (1040, yy - 10), (1044, yy + 26), (304, yy + 36)]),
                      mix("#d8c088", "#a8884a", (k % 3) * 0.3), shadow=0.4, seed=730 + k, edge=False)
                src(ctx, "#3a2a18", 0.55)
                for j in range(3):
                    ctx.rectangle(340, yy + 8 + j * 8, 660, 2)
                ctx.fill()
            sheet(ctx, path_poly([(640, 740), (700, 740), (700, 1040), (640, 1040)]), "#7e3520", shadow=0.4, seed=740)
        elif variant == "ballot":
            sheet(ctx, path_poly([(900, 1150), (1500, 1150), (1460, 720), (940, 720)]), "#6a4a2a", shadow=1.0, seed=750)
            src(ctx, "#1a120c")
            ctx.rectangle(1080, 730, 240, 14)
            ctx.fill()
            for k in range(9):
                x = 300 + (k % 5) * 160 + (k // 5) * 1300
                sheet(ctx, path_poly([(x, 1200 - k * 3), (x + 130, 1196), (x + 136, 1080), (x + 6, 1084)]), "#efe6cc",
                      shadow=0.5, seed=760 + k)
        glow(ctx, 900, 500, 900, "#ffcf8a", 0.12)

    layers = [(_key("dk", tod=tod, v=variant), desk, 0.5)]

    def fx(ctx, t, d, depth):
        if depth == 0.5:
            glow(ctx, 900, 480, 700, "#ffd890", 0.06 + 0.03 * math.sin(t * 5.3) * math.sin(t * 2.1))
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.5, 0.6])
