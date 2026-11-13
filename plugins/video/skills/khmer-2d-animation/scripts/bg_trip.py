"""Road-trip environments (registered into backgrounds.ENVIRONMENTS).

Layer contract for packs (bg_trip, bg_heritage, bg_town): fn(ctx, layer, t, tod) in world coordinates with layers
SKY 0.05, BG 0.25, MG 0.6, GROUND 1.0, OVER 1.0 (drawn after the characters), FG 1.3, SCREEN (screen space, after
the tint). OVER/SCREEN are only called for functions marked with @extra. B.CUR holds the shot's "bg" params plus
lt (shot-local time) and dur.

Environments:
  van_road    the white van driving along a road (side view, scrolling scenery). params: scenery town_night |
              country | forest_wall | city_evening, speed (px/s), van_x, van_y (road line under the wheels),
              van_s (scale), lights (headlights on), parked (no scrolling)
  van_inside  cut-away side view inside the van: seats, driver, windows with scenery scrolling past. params:
              outside night | dawn | country | forest | city, speed. Seat rows (facing right) at x = ROWS; seated
              people go at y ~935 with legs "chair"; the lower wall panel in OVER hides laps and legs.
  map_route   cartoon map of Cambodia with Kampong Cham and Siem Reap; the route draws itself with a little van.
              params: dir go | back, t0, t1 (draw window in shot time)
  photo_end   the group in front of the parked van at Angkor Wat in golden light; at `snap` seconds a camera flash
              and a white photo frame appear. params: snap, backdrop angkor | plain, van_x
  rest_stop   roadside rest stop at sunrise: breakfast stall "ហាងបាយ", toilet block "បន្ទប់ទឹក" (men's door blue,
              women's pink), the van. params: view yard | toilets | breakfast; yard: van_x, van_s, door_k;
              toilets: door_open [t0, t1] (men's door, shot time; doors at x 520..710 and 1210..1400, apron y 900);
              breakfast: tables/chairs like `restaurant` (tables in OVER, seated cast at y 935), stall (false hides it)
  memories    polaroid photos of the trip dropping onto a warm board. params: photos [[path, x, y, rot], ...]
              (paths relative to the project root), step (s between photos)
"""
import math
import os

import cairocffi as cairo

import backgrounds as B
from drawutil import (OUTLINE, circle, clamp, curve, ease_io, ellipse, ellipse_path, fill_stroke, lerp, lin_grad, line,
                      poly, poly_path, rad_grad, rng, rrect, rrect_path, shade, smooth_path, src)

BOL = B.BOL
VAN_WHITE = "#f4f5f2"
ROWS = [1460, 1150, 840, 530, 220]  # van_inside seat rows (person x), front (driver) first


def extra(fn):
    """Mark an environment as drawing the extra OVER (in front of characters) / SCREEN (screen-space) layers."""
    fn.extra_layers = True
    return fn


def _lt(t):
    return float(B.CUR.get("lt", t))


# --------------------------------------------------------------------------- the van

def _van_body_path(ctx):
    ctx.new_path()
    ctx.move_to(-420, -72)
    ctx.line_to(-420, -398)
    ctx.curve_to(-420, -420, -408, -432, -386, -432)
    ctx.line_to(236, -432)
    ctx.curve_to(262, -432, 274, -424, 286, -410)
    ctx.line_to(392, -262)
    ctx.curve_to(402, -248, 420, -240, 428, -222)
    ctx.curve_to(438, -200, 440, -150, 438, -98)
    ctx.curve_to(437, -82, 428, -72, 412, -72)
    ctx.close_path()


VAN_WINDOWS = [[(-396, -404), (-222, -404), (-222, -292), (-396, -292)],
               [(-204, -404), (-36, -404), (-36, -292), (-204, -292)],
               [(-18, -404), (134, -404), (134, -292), (-18, -292)],
               [(152, -404), (244, -404), (326, -292), (152, -292)]]


def _window_paths(ctx):
    for w in VAN_WINDOWS:
        ctx.new_sub_path()
        poly_path(ctx, w)


def van_back(ctx, cx, gy, s=1.0, facing=1, dark="#2f3540"):
    """Interior seen through the windows (draw BEFORE the people inside)."""
    ctx.save()
    ctx.translate(cx, gy)
    ctx.scale(s * facing, s)
    ctx.new_path()
    _window_paths(ctx)
    src(ctx, dark)
    ctx.fill()
    for x0 in (-396, -204, -18):  # seat backs (low, so they never read as hats behind heads)
        rrect(ctx, x0 + 14, -322, 40, 40, 10, "#4b525d", 0)
    ctx.restore()


def wheel(ctx, x, y, r, t, spin=0.0):
    circle(ctx, x, y, r, "#26262b", BOL)
    circle(ctx, x, y, r * 0.56, "#c9ccd3", BOL * 0.8)
    a0 = spin * t / r
    for k in range(5):
        a = a0 + k * 2 * math.pi / 5
        circle(ctx, x + math.cos(a) * r * 0.34, y + math.sin(a) * r * 0.34, r * 0.07, "#8a8f98", 0)
    circle(ctx, x, y, r * 0.16, "#9aa0aa", 1.5)


def van_front(ctx, cx, gy, s=1.0, t=0.0, facing=1, lights=False, spin=0.0, shadow=True):
    """Van body with see-through windows (draw AFTER the people inside)."""
    ctx.save()
    ctx.translate(cx, gy)
    ctx.scale(s * facing, s)
    if shadow:
        ctx.new_path()
        ellipse_path(ctx, 10, 2, 470, 22)
        ctx.set_source_rgba(0, 0, 0, 0.22)
        ctx.fill()
    if lights:  # headlight beam
        ctx.new_path()
        ctx.move_to(430, -175)
        ctx.line_to(1250, -330)
        ctx.line_to(1250, 30)
        ctx.close_path()
        ctx.set_source(lin_grad(430, 0, 1250, 0, [(0, (1, 0.96, 0.75, 0.55)), (1, (1, 0.96, 0.75, 0.0))]))
        ctx.fill()
    # body (even-odd: windows stay open) with a soft lower shade and a side stripe
    ctx.save()
    _van_body_path(ctx)
    _window_paths(ctx)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.clip()
    ctx.new_path()
    ctx.rectangle(-460, -460, 920, 470)
    src(ctx, VAN_WHITE)
    ctx.fill()
    ctx.rectangle(-460, -150, 920, 100)
    src(ctx, "#dfe2e2")
    ctx.fill()
    ctx.rectangle(-460, -228, 920, 22)
    src(ctx, "#8fa3b8")
    ctx.fill()
    ctx.rectangle(-460, -205, 920, 7)
    src(ctx, "#c2ccd6")
    ctx.fill()
    ctx.restore()
    _van_body_path(ctx)
    fill_stroke(ctx, None, BOL)
    # glass: light tint + reflection streak
    for w in VAN_WINDOWS:
        poly(ctx, w, (0.80, 0.90, 0.98, 0.20), BOL * 0.8)
        x0 = min(p[0] for p in w)
        poly(ctx, [(x0 + 20, -404), (x0 + 50, -404), (x0 + 22, -330), (x0 + 4, -330)], (1, 1, 1, 0.22), 0)
    poly(ctx, [(262, -426), (392, -262), (378, -252), (250, -420)], (0.70, 0.84, 0.96, 0.9), BOL * 0.7)
    for x in (-18, 134, 150, 338):
        line(ctx, [(x, -410 if x < 300 else -250), (x, -80)], 2.2, "#b9bdc2")
    for x in (96, 300):
        rrect(ctx, x, -270, 26, 9, 4, "#9da3aa", 1.2)
    poly(ctx, [(330, -306), (362, -318), (366, -290), (334, -284)], "#2f3540", 1.6)
    ellipse(ctx, 422, -172, 14, 22, "#fff3b0" if lights else "#f2f2e6", 1.8)
    rrect(ctx, -424, -196, 12, 40, 3, "#d8333a", 1.4)
    rrect(ctx, 380, -98, 64, 26, 8, "#b9bdc2", BOL * 0.8)
    rrect(ctx, -436, -98, 50, 26, 8, "#b9bdc2", BOL * 0.8)
    for wx in (-262, 262):
        ctx.new_path()
        ctx.arc(wx, -50, 70, math.pi, 2 * math.pi)
        ctx.close_path()
        fill_stroke(ctx, "#3a3f47", BOL * 0.8)
        wheel(ctx, wx, -50, 52, t, spin)
    ctx.restore()


def van(ctx, cx, gy, s=1.0, t=0.0, facing=1, lights=False, spin=0.0, shadow=True):
    """Whole parked van (no visible passengers)."""
    van_back(ctx, cx, gy, s, facing)
    van_front(ctx, cx, gy, s, t, facing, lights, spin, shadow)


def van_icon(ctx, x, y, s, facing=1):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * facing, s)
    rrect(ctx, -34, -30, 64, 26, 6, VAN_WHITE, 2.4)
    poly(ctx, [(30, -30), (42, -14), (42, -4), (30, -4)], VAN_WHITE, 2.4)
    for wx in (-28, -12, 4):
        rrect(ctx, wx, -26, 12, 9, 2, "#6aa8d8", 0)
    for wx in (-20, 22):
        circle(ctx, wx, -3, 7, "#26262b", 1.8)
    ctx.restore()


# --------------------------------------------------------------------------- scrolling scenery

def _scroll(lt, speed, k, span):
    return -(lt * speed * k) % span


def street_lamp(ctx, x, gy, h, on=True):
    line(ctx, [(x, gy), (x, gy - h)], 9, OUTLINE)
    line(ctx, [(x, gy), (x, gy - h)], 5, "#7d8590")
    curve(ctx, (x, gy - h), (x + 10, gy - h - 26), (x + 48, gy - h - 20), 5, "#7d8590")
    if on:
        ctx.new_path()
        ctx.arc(x + 48, gy - h - 12, 70, 0, 2 * math.pi)
        ctx.set_source(rad_grad(x + 48, gy - h - 12, 4, 70, [(0, (1, 0.9, 0.6, 0.55)), (1, (1, 0.9, 0.6, 0.0))]))
        ctx.fill()
    ellipse(ctx, x + 48, gy - h - 14, 16, 7, "#ffe9a0" if on else "#d9d9d9", 1.6)


def shop_house(ctx, x, gy, w, h, col, lit, seed):
    r = rng(seed)
    rrect(ctx, x, gy - h, w, h, 2, col, BOL * 0.8)
    for k in range(2):
        for j in range(max(1, int(w // 70))):
            wx, wy = x + 16 + j * 70, gy - h + 24 + k * 80
            if wy > gy - 120:
                continue
            on = lit and r.random() < 0.6
            rrect(ctx, wx, wy, 40, 46, 3, "#ffd77a" if on else shade(col, -0.35), BOL * 0.5)
    rrect(ctx, x + 8, gy - 58, w - 16, 58, 2, "#ffcf6a" if lit else shade(col, -0.3), BOL * 0.6)
    poly(ctx, [(x - 6, gy - 62), (x + w + 6, gy - 62), (x + w + 14, gy - 86), (x - 14, gy - 86)],
         ["#d8333a", "#2f7fc0", "#3a9a5a", "#e9a43a"][seed % 4], BOL * 0.6)


def laterite_wall(ctx, x0, x1, gy, h):
    rrect(ctx, x0, gy - h, x1 - x0, h, 2, "#9a5a3c", BOL)
    r = rng(int(x0) & 0xffff)
    y = gy - h + 18
    row = 0
    while y < gy - 4:
        line(ctx, [(x0, y), (x1, y)], 1.6, "#7d4630")
        x = x0 + (row % 2) * 30
        while x < x1:
            line(ctx, [(x, y - 18), (x, y)], 1.4, "#7d4630")
            x += 60
        y += 18
        row += 1
    for _ in range(int((x1 - x0) / 80)):
        ellipse(ctx, r.uniform(x0, x1), r.uniform(gy - h, gy - 6), r.uniform(8, 20), r.uniform(4, 9), "#6f8f4a", 0)


HOUSES = (300, 240, 280, 260, 320, 250)


def scenery(ctx, layer, kind, t, tod, lt, speed, road_y):
    hz = 600
    night = kind == "town_night" or tod == "night"
    if layer == "SKY":
        B.sky(ctx, t, tod, hz)
    elif layer == "BG":
        off = _scroll(lt, speed, 0.10, 3000)
        ctx.save()
        ctx.translate(off - 1500, 0)
        if kind in ("town_night", "city_evening"):
            for k in range(30):
                x = -520 + k * 180
                h = 120 + (k * 53) % 140
                rrect(ctx, x, hz + 40 - h, 170, h, 2, "#2d3a5c" if night else "#b9a8c8", BOL * 0.5)
                if night:
                    for j in range(3):
                        if (k + j) % 3 == 0:
                            rrect(ctx, x + 20 + j * 48, hz + 60 - h, 18, 20, 2, "#ffd77a", 0)
        elif kind == "forest_wall":
            for k in range(36):
                B.tree(ctx, -520 + k * 150, hz + 60, 0.9 + (k % 3) * 0.15, "#3f7f3a", "#5a4030", seed=k)
        else:
            B.hills(ctx, hz + 20, "#8fbf8a", 40, 7)
            for k in range(14):
                B.sugar_palm(ctx, -400 + k * 430, hz + 40, 150 + (k % 3) * 30, t)
        ctx.restore()
    elif layer == "MG":
        span = 2400
        off = _scroll(lt, speed, 0.45, span)
        ctx.save()
        ctx.translate(off - span, 0)
        for rep in range(3):
            bx = rep * span
            if kind in ("town_night", "city_evening"):
                for k, w in enumerate(HOUSES):
                    x = bx - 400 + sum(HOUSES[:k]) + k * 30
                    col = ["#4a5a7c", "#5c4a6c", "#4c6a6a"][k % 3] if night else ["#f0c58a", "#e8a798", "#b7d3a8"][k % 3]
                    shop_house(ctx, x, road_y - 140, w, 250 + (k * 37) % 90, col, True, k + rep)
            elif kind == "forest_wall":
                for k in range(8):
                    x = bx - 400 + k * 320
                    line(ctx, [(x, road_y - 140), (x, -200)], 34, OUTLINE)
                    line(ctx, [(x, road_y - 140), (x, -200)], 28, "#8a6a4f")
                    B.tree(ctx, x + 150, road_y - 120, 1.4, "#4f9a3d", seed=k + rep)
                laterite_wall(ctx, bx - 400, bx + span, road_y - 120, 120)
            else:
                for k in range(6):
                    x = bx - 300 + k * 420
                    B.sugar_palm(ctx, x, road_y - 140, 300 + (k % 2) * 60, t)
                    line(ctx, [(x + 200, road_y - 140), (x + 200, road_y - 480)], 7, "#7a5a3a")
                line(ctx, [(bx - 400, road_y - 470), (bx + span, road_y - 470)], 1.5, "#333333")
        ctx.restore()
    elif layer == "GROUND":
        verge = "#3d5a3a" if night else ("#7fb55a" if kind != "forest_wall" else "#6f9a4a")
        ctx.new_path()
        ctx.rectangle(B.X0, road_y - 140, B.X1 - B.X0, 60)
        src(ctx, verge)
        ctx.fill()
        ctx.new_path()
        ctx.rectangle(B.X0, road_y - 84, B.X1 - B.X0, 1200)
        src(ctx, "#3b3f46" if night else "#5d6168")
        ctx.fill()
        line(ctx, [(B.X0, road_y - 84), (B.X1, road_y - 84)], 6, "#c9c3b4")
        off = _scroll(lt, speed, 1.0, 260)
        for k in range(-3, 14):
            x = B.X0 + off + k * 260
            rrect(ctx, x, road_y + 60, 130, 10, 4, "#f2e6a0", 0)
        if night and kind == "town_night":
            off2 = _scroll(lt, speed, 1.0, 1100)
            for k in range(-1, 4):
                street_lamp(ctx, B.X0 + off2 + k * 1100, road_y - 84, 360)
    elif layer == "FG":
        off = _scroll(lt, speed, 1.3, 1700)
        for k in range(-1, 3):
            x = B.X0 + off + k * 1700
            if kind == "country":
                B.bush(ctx, x, 1110, 1.6, "#4c8f35")
            elif kind == "forest_wall":
                B.bush(ctx, x, 1110, 1.8, "#3f7f3a")


@extra
def _van_road(ctx, layer, t, tod):
    lt = _lt(t)
    parked = bool(B.CUR.get("parked", False))
    speed = 0.0 if parked else float(B.CUR.get("speed", 700))
    kind = B.CUR.get("scenery", "country")
    vx = float(B.CUR.get("van_x", 960))
    vy = float(B.CUR.get("van_y", 960))
    vs = float(B.CUR.get("van_s", 1.0))
    lights = bool(B.CUR.get("lights", tod == "night"))
    bob = 0 if parked else math.sin(lt * 9) * 1.5
    if layer in ("SKY", "BG", "MG", "FG"):
        scenery(ctx, layer, kind, t, tod, lt, speed, vy)
    elif layer == "GROUND":
        scenery(ctx, layer, kind, t, tod, lt, speed, vy)
        van_back(ctx, vx, vy + bob, vs)
    elif layer == "OVER":
        van_front(ctx, vx, vy + bob, vs, lt, 1, lights, speed)


# --------------------------------------------------------------------------- inside the van

def _outside_strip(ctx, kind, lt, speed, y0, y1):
    """Scenery seen through the side windows (moving right-to-left)."""
    night = kind == "night"
    ctx.new_path()
    ctx.rectangle(B.X0, y0, B.X1 - B.X0, y1 - y0)
    if night:
        ctx.set_source(lin_grad(0, y0, 0, y1, [(0, "#0e1a3a"), (1, "#24345e")]))
    elif kind == "dawn":
        ctx.set_source(lin_grad(0, y0, 0, y1, [(0, "#9a8fd0"), (0.45, "#ffa98a"), (1, "#ffe2a8")]))
    elif kind == "city":
        ctx.set_source(lin_grad(0, y0, 0, y1, [(0, "#f6b26b"), (1, "#ffe1b0")]))
    else:
        ctx.set_source(lin_grad(0, y0, 0, y1, [(0, "#7cc8f0"), (1, "#d8f0fb")]))
    ctx.fill()
    span = 900
    off = -(lt * speed * 0.6) % span
    for k in range(-1, 5):
        x = B.X0 + off + k * span
        if night:
            for j in range(4):
                rrect(ctx, x + j * 210, y1 - 120 - (j % 2) * 30, 150, 140, 2, "#22305a", 0)
                rrect(ctx, x + j * 210 + 30, y1 - 100 - (j % 2) * 30, 22, 24, 2, "#ffd77a", 0)
            circle(ctx, x + 480, y0 + 40, 10, "#ffe9a0", 0)
        elif kind == "forest":
            for j in range(5):
                B.tree(ctx, x + j * 180, y1 + 20, 0.75, "#4f9a3d", seed=j)
        elif kind == "city":
            for j in range(4):
                rrect(ctx, x + j * 220, y1 - 130 - (j % 2) * 20, 190, 150, 2, ["#f0c58a", "#e8a798", "#b7d3a8"][j % 3], 2)
        elif kind == "dawn":  # low sun over the paddies, palms in warm morning shade
            circle(ctx, x + 520, y1 - 70, 34, "#fff0b0", 0)
            ctx.new_path()
            ctx.rectangle(x, y1 - 50, span, 50)
            src(ctx, "#a7b85a")
            ctx.fill()
            for j in range(3):
                B.sugar_palm(ctx, x + 120 + j * 300, y1 - 30, 150 + j * 20, lt, "#5d8a48")
        else:
            ctx.new_path()
            ctx.rectangle(x, y1 - 50, span, 50)
            src(ctx, "#8cc95a")
            ctx.fill()
            for j in range(3):
                B.sugar_palm(ctx, x + 120 + j * 300, y1 - 30, 150 + j * 20, lt)


INSIDE_WINDOWS = [(70, 380), (410, 690), (720, 1000), (1030, 1310), (1340, 1560)]


@extra
def _van_inside(ctx, layer, t, tod):
    lt = _lt(t)
    kind = B.CUR.get("outside", "country")
    speed = float(B.CUR.get("speed", 700))
    wy0, wy1 = 470, 668
    if layer == "GROUND":
        ctx.new_path()
        ctx.rectangle(B.X0, -200, B.X1 - B.X0, 1500)
        src(ctx, "#d9d3c4")
        ctx.fill()
        ctx.new_path()
        ctx.rectangle(B.X0, -200, B.X1 - B.X0, 640)  # headliner
        src(ctx, "#e8e3d6")
        ctx.fill()
        line(ctx, [(B.X0, 440), (B.X1, 440)], 4, "#b9b2a2")
        ctx.save()
        ctx.new_path()
        for x0, x1 in INSIDE_WINDOWS:
            ctx.new_sub_path()
            rrect_path(ctx, x0, wy0, x1 - x0, wy1 - wy0, 18)
        ctx.new_sub_path()  # windscreen (front, slanted)
        poly_path(ctx, [(1600, wy0 - 40), (1760, wy0 - 40), (2100, wy1 + 120), (1600, wy1 + 120)])
        ctx.clip()
        _outside_strip(ctx, kind, lt, speed, wy0 - 60, wy1 + 130)
        ctx.restore()
        for x0, x1 in INSIDE_WINDOWS:
            rrect(ctx, x0, wy0, x1 - x0, wy1 - wy0, 18, None, BOL)
            poly(ctx, [(x0 + 30, wy0 + 6), (x0 + 70, wy0 + 6), (x0 + 30, wy1 - 6), (x0 + 6, wy1 - 6)], (1, 1, 1, 0.12), 0)
        poly(ctx, [(1600, wy0 - 40), (1760, wy0 - 40), (2100, wy1 + 120), (1600, wy1 + 120)], None, BOL)
        ctx.new_path()
        ctx.rectangle(B.X0, 900, B.X1 - B.X0, 400)
        src(ctx, "#5b5f66")
        ctx.fill()
        for x in ROWS:  # seat backs behind each row (people face right)
            sx = x - 105
            rrect(ctx, sx - 34, 650, 68, 250, 22, "#4f5866", BOL)
            rrect(ctx, sx - 26, 600, 52, 52, 14, "#5d6776", BOL * 0.9)
            line(ctx, [(sx - 10, 650), (sx - 10, 600)], 4, "#9aa3ab")
            rrect(ctx, sx - 30, 860, x - sx + 70, 40, 12, "#4f5866", BOL)
        poly(ctx, [(1560, 780), (1960, 700), (2440, 700), (2440, 1300), (1560, 1300)], "#3f444c", BOL)
    elif layer == "OVER":
        # near-side lower panel of the cut-away van (hides laps and legs)
        ctx.new_path()
        ctx.rectangle(B.X0, 828, B.X1 - B.X0, 500)
        ctx.set_source(lin_grad(0, 828, 0, 1080, [(0, "#f2f1ec"), (1, "#d8dad8")]))
        ctx.fill_preserve()
        src(ctx, OUTLINE)
        ctx.set_line_width(BOL)
        ctx.stroke()
        line(ctx, [(B.X0, 850), (B.X1, 850)], 10, "#8fa3b8")
        for x in (380, 1010):
            line(ctx, [(x, 860), (x, 1080)], 2.4, "#b9bdc2")
        wx = ROWS[0] + 120  # steering wheel in front of the driver
        ctx.save()
        ctx.translate(wx, 740)
        ctx.rotate(-0.45)
        ctx.new_path()
        ellipse_path(ctx, 0, 0, 22, 64)
        src(ctx, OUTLINE)
        ctx.set_line_width(16)
        ctx.stroke_preserve()
        src(ctx, "#2b2f36")
        ctx.set_line_width(10)
        ctx.stroke()
        ctx.restore()
        line(ctx, [(wx + 12, 760), (wx + 80, 820)], 14, "#2b2f36")


# --------------------------------------------------------------------------- map

LON0, LON1, LAT0, LAT1 = 101.9, 108.1, 9.9, 15.1
MAP_BOX = (300, 60, 1620, 1020)
CAMBODIA = [(102.35, 13.60), (102.75, 13.85), (103.0, 14.35), (103.6, 14.42), (104.4, 14.36), (105.0, 14.25),
            (105.5, 14.50), (106.1, 14.70), (106.6, 14.50), (107.1, 14.40), (107.55, 14.60), (107.5, 13.90),
            (107.6, 13.40), (107.5, 12.80), (107.6, 12.30), (107.0, 12.00), (106.4, 11.70), (105.95, 11.65),
            (106.20, 11.30), (105.90, 10.95), (105.40, 10.95), (105.00, 10.90), (104.45, 10.42), (103.90, 10.55),
            (103.60, 10.50), (103.10, 10.90), (103.00, 11.40), (102.92, 11.65), (102.70, 12.10), (102.50, 12.60),
            (102.30, 13.00)]
MEKONG = [(105.90, 15.1), (105.95, 14.2), (105.97, 13.52), (106.02, 12.49), (105.75, 12.15), (105.46, 11.99),
          (105.10, 11.70), (104.92, 11.56), (105.05, 11.20), (105.10, 10.95), (105.3, 10.3)]
ROUTE = [(105.46, 11.99), (105.20, 12.08), (104.93, 12.17), (104.90, 12.45), (104.89, 12.71), (104.55, 12.95),
         (104.33, 13.10), (104.10, 13.25), (103.86, 13.36)]
KC, SR = (105.46, 11.99), (103.86, 13.36)


def _proj(lon, lat):
    x0, y0, x1, y1 = MAP_BOX
    s = min((x1 - x0) / (LON1 - LON0), (y1 - y0) / (LAT1 - LAT0) * 1.03)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return cx + (lon - (LON0 + LON1) / 2) * s, cy - (lat - (LAT0 + LAT1) / 2) * s * 1.025


def _pin(ctx, x, y, col, t):
    b = abs(math.sin(t * 3)) * 6
    ctx.new_path()
    ctx.move_to(x, y)
    ctx.curve_to(x - 22, y - 30 - b, x - 22, y - 58 - b, x, y - 58 - b)
    ctx.curve_to(x + 22, y - 58 - b, x + 22, y - 30 - b, x, y)
    ctx.close_path()
    fill_stroke(ctx, col, BOL)
    circle(ctx, x, y - 44 - b, 8, "#ffffff", 1.5)


def _along(pts, k):
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    lens = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs]
    total = sum(lens) * k
    out = [pts[0]]
    for (a, b), l in zip(segs, lens):
        if total <= l:
            f = total / max(l, 1e-6)
            out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
            return out, math.atan2(b[1] - a[1], b[0] - a[0])
        out.append(b)
        total -= l
    a, b = segs[-1]
    return out, math.atan2(b[1] - a[1], b[0] - a[0])


@extra
def _map_route(ctx, layer, t, tod):
    if layer != "SKY":
        return
    import bg_angkor
    import textrender as TR
    lt = _lt(t)
    dur = float(B.CUR.get("dur", 4.0))
    direction = B.CUR.get("dir", "go")
    t0 = float(B.CUR.get("t0", 0.6))
    t1 = float(B.CUR.get("t1", max(t0 + 1.0, dur - 0.8)))
    ctx.new_path()
    ctx.rectangle(B.X0, -300, B.X1 - B.X0, 1700)
    src(ctx, "#bfe3f2")
    ctx.fill()
    r = rng(3)
    for _ in range(40):
        x, y = r.uniform(0, 1920), r.uniform(700, 1080)
        line(ctx, [(x, y), (x + 30, y)], 2, "#ffffff", 0.5)
    land = [_proj(101.0, 15.6), _proj(109.0, 15.6), _proj(109.0, 10.6), _proj(106.9, 10.4), _proj(106.4, 9.6),
            _proj(105.0, 9.6), _proj(104.8, 10.35), _proj(104.45, 10.42), _proj(102.92, 11.65), _proj(102.6, 12.0),
            _proj(101.0, 12.3)]
    poly(ctx, land, "#f3e6c4", BOL)
    pts = [_proj(*p) for p in CAMBODIA]
    ctx.new_path()
    smooth_path(ctx, pts, tension=0.35)
    ctx.set_source(lin_grad(0, 100, 0, 1000, [(0, "#bfe3a0"), (1, "#a6d68a")]))
    ctx.fill_preserve()
    src(ctx, "#5a7a3a")
    ctx.set_line_width(5)
    ctx.stroke()
    lx, ly = _proj(104.05, 12.85)  # Tonle Sap
    ctx.save()
    ctx.translate(lx, ly)
    ctx.rotate(-0.62)
    ctx.new_path()
    ellipse_path(ctx, 0, 0, 92, 34)
    fill_stroke(ctx, "#6fb7e0", 3)
    ctx.restore()
    ctx.new_path()
    smooth_path(ctx, [_proj(*p) for p in MEKONG], close=False)
    src(ctx, "#6fb7e0")
    ctx.set_line_width(9)
    ctx.stroke()
    for lon, lat in ((103.3, 12.2), (106.6, 13.2), (104.3, 11.7), (106.0, 12.8), (103.9, 11.2)):
        x, y = _proj(lon, lat)
        B.sugar_palm(ctx, x, y, 70, t)
    ax, ay = _proj(103.87, 13.62)
    bg_angkor.angkor_wat(ctx, ax, ay, 0.11, bg_angkor.STONE, 1.6)
    k = ease_io(clamp((lt - t0) / max(0.1, t1 - t0), 0, 1))
    rp = [_proj(*p) for p in (ROUTE if direction == "go" else list(reversed(ROUTE)))]
    if k > 0:
        drawn, ang = _along(rp, k)
        ctx.save()
        ctx.set_dash([22, 14])
        line(ctx, drawn, 11, "#ffffff")
        line(ctx, drawn, 7, "#e8572a")
        ctx.restore()
        hx, hy = drawn[-1]
        van_icon(ctx, hx, hy + 6, 1.15, 1 if math.cos(ang) >= 0 else -1)
    for (lon, lat), km, col in ((KC, "កំពង់ចាម", "#e8403f"), (SR, "សៀមរាប", "#2f7fd8")):
        x, y = _proj(lon, lat)
        _pin(ctx, x, y, col, lt + lon)
        if B.TEXT_DIR:
            s_ = TR.render(km, 46, B.TEXT_DIR, color="#ffffff")
            pad = 12
            dx = 34 if lon > 105 else -s_.get_width() - 34
            rrect(ctx, x + dx - pad, y - 74, s_.get_width() + 2 * pad, s_.get_height() + 4, 14, col, BOL * 0.8)
            ctx.set_source_surface(s_, x + dx, y - 72)
            ctx.paint()
    cx, cy = 1760, 170
    circle(ctx, cx, cy, 54, "#fff8e6", BOL)
    poly(ctx, [(cx, cy - 46), (cx + 12, cy), (cx - 12, cy)], "#d8333a", 1.5)
    poly(ctx, [(cx, cy + 46), (cx + 12, cy), (cx - 12, cy)], "#6b6b6b", 1.5)


# --------------------------------------------------------------------------- ending

@extra
def _photo_end(ctx, layer, t, tod):
    lt = _lt(t)
    snap = float(B.CUR.get("snap", 3.0))
    vx = float(B.CUR.get("van_x", 980))
    hz = 600
    if layer == "SKY":
        import bg_angkor
        B.sky(ctx, t, tod, hz)
        bg_angkor.birds(ctx, t, 5)
    elif layer == "BG":
        B.hills(ctx, hz + 20, "#7aa86a", 30, 11)
        if B.CUR.get("backdrop", "angkor") == "angkor":
            import bg_angkor
            bg_angkor.angkor_wat(ctx, 960, hz + 70, 0.55, bg_angkor.STONE, BOL * 0.8)
        for x in (-250, 180, 1720, 2150):
            B.sugar_palm(ctx, x, hz + 80, 280, t)
    elif layer == "MG":
        ctx.new_path()
        ctx.rectangle(B.X0, hz + 60, B.X1 - B.X0, 900)
        src(ctx, "#9cc66a")
        ctx.fill()
    elif layer == "GROUND":
        ctx.new_path()
        ctx.rectangle(B.X0, 700, B.X1 - B.X0, 600)
        ctx.set_source(lin_grad(0, 700, 0, 1080, [(0, "#d9c79f"), (1, "#c7ad7d")]))
        ctx.fill()
        van(ctx, vx, 790, 0.95, lt, 1, False, 0)
    elif layer == "SCREEN" and lt >= snap:
        a = clamp(1 - (lt - snap) / 0.45, 0, 1)
        if a > 0:
            ctx.set_source_rgba(1, 1, 1, a * 0.95)
            ctx.paint()
        k = ease_io(clamp((lt - snap - 0.15) / 0.6, 0, 1))
        if k > 0:
            ctx.save()
            ctx.set_source_rgba(1, 1, 1, k)
            ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
            ctx.rectangle(0, 0, 1920, 1080)
            ctx.rectangle(70, 60, 1780, 880)
            ctx.fill()
            ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
            ctx.set_source_rgba(0, 0, 0, 0.18 * k)
            ctx.rectangle(70, 60, 1780, 8)
            ctx.rectangle(70, 60, 8, 880)
            ctx.fill()
            ctx.restore()


_IMG_CACHE = {}


def _image(path):
    if path not in _IMG_CACHE:
        try:
            _IMG_CACHE[path] = cairo.ImageSurface.create_from_png(path)
        except Exception:
            _IMG_CACHE[path] = None
    return _IMG_CACHE[path]


def polaroid(ctx, img, x, y, w, rot, alpha=1.0):
    h = w * 9 / 16
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.push_group()
    rrect(ctx, -w / 2 - 10, -h / 2 - 8, w + 36, h + 90, 4, (0, 0, 0, 0.25), 0)
    rrect(ctx, -w / 2 - 18, -h / 2 - 18, w + 36, h + 90, 4, "#fffdf6", 2)
    if img is not None:
        ctx.save()
        ctx.rectangle(-w / 2, -h / 2, w, h)
        ctx.clip()
        ctx.translate(-w / 2, -h / 2)
        ctx.scale(w / img.get_width(), h / img.get_height())
        ctx.set_source_surface(img, 0, 0)
        ctx.paint()
        ctx.restore()
    else:
        rrect(ctx, -w / 2, -h / 2, w, h, 0, "#9fc8e8", 0)
    rrect(ctx, -34, -h / 2 - 34, 68, 28, 3, (0.95, 0.85, 0.5, 0.75), 0)  # tape
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha)
    ctx.restore()


@extra
def _memories(ctx, layer, t, tod):
    lt = _lt(t)
    if layer == "SKY":
        ctx.new_path()
        ctx.rectangle(B.X0, -300, B.X1 - B.X0, 1700)
        ctx.set_source(lin_grad(0, 0, 0, 1080, [(0, "#ffe7c4"), (1, "#f6c99a")]))
        ctx.fill()
        r = rng(9)
        for _ in range(70):
            x, y = r.uniform(0, 1920), (r.uniform(-200, 1080) + lt * r.uniform(20, 50)) % 1280 - 200
            col = r.choice(["#e8403f", "#2f7fd8", "#f5c623", "#8e5cc9", "#3a9a5a", "#f06ea9"])
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(r.uniform(0, 3) + lt)
            rrect(ctx, -6, -3, 12, 6, 1, col, 0)
            ctx.restore()
    elif layer == "MG":
        root = os.path.dirname(os.path.dirname(B.TEXT_DIR)) if B.TEXT_DIR else "."
        step = float(B.CUR.get("step", 0.45))
        for i, item in enumerate(B.CUR.get("photos", [])):
            path, x, y, rot = item[0], float(item[1]), float(item[2]), float(item[3])
            k = clamp((lt - 0.3 - i * step) / 0.5, 0, 1)
            if k <= 0:
                continue
            e = ease_io(k)
            sc = lerp(1.6, 1.0, e)
            ctx.save()
            ctx.translate(x, y)
            ctx.scale(sc, sc)
            polaroid(ctx, _image(os.path.join(root, path)), 0, 0, float(B.CUR.get("photo_w", 470)),
                     rot * e + (1 - e) * rot * 3, e)
            ctx.restore()


# --------------------------------------------------------------------------- roadside rest stop

def _sign(ctx, km, cx, cy, size, bg, w=None, fg="#ffffff"):
    """Board with a Khmer word centred on (cx, cy)."""
    import textrender as TR
    surf = TR.render(km, size, B.TEXT_DIR, color=fg) if B.TEXT_DIR else None
    tw = surf.get_width() if surf else size * len(km) * 0.35
    th = surf.get_height() if surf else size * 1.4
    bw = w or tw + size * 0.9
    rrect(ctx, cx - bw / 2, cy - th / 2 - 6, bw, th + 12, 12, bg, BOL)
    if surf:
        ctx.set_source_surface(surf, cx - tw / 2, cy - th / 2)
        ctx.paint()


def _man_icon(ctx, x, y, s, col):
    circle(ctx, x, y - 34 * s, 11 * s, col, 0)
    rrect(ctx, x - 13 * s, y - 20 * s, 26 * s, 30 * s, 6 * s, col, 0)
    for dx in (-6, 6):
        rrect(ctx, x + dx * s - 4.5 * s, y + 6 * s, 9 * s, 26 * s, 3 * s, col, 0)


def _woman_icon(ctx, x, y, s, col):
    circle(ctx, x, y - 34 * s, 11 * s, col, 0)
    poly(ctx, [(x - 6 * s, y - 21 * s), (x + 6 * s, y - 21 * s), (x + 19 * s, y + 14 * s), (x - 19 * s, y + 14 * s)], col, 0)
    for dx in (-5, 5):
        rrect(ctx, x + dx * s - 3.5 * s, y + 12 * s, 7 * s, 20 * s, 3 * s, col, 0)


def toilet_block(ctx, ox, base, s=1.0, door_open=0.0):
    """Small public toilet building ("បន្ទប់ទឹក"): men's door left (blue), women's door right (pink).
    Local units: 1260 wide, wall 525 high above `base`; doors 190 x 400. door_open 0..1 opens the men's door."""
    ctx.save()
    ctx.translate(ox, base)
    ctx.scale(s, s)
    rrect(ctx, -630, -525, 1260, 525, 4, "#f4f1e8", BOL)                       # white upper wall
    ctx.new_path()
    ctx.rectangle(-630, -230, 1260, 230)
    src(ctx, "#7cc8c8")                                                       # turquoise tiles
    ctx.fill()
    for k in range(1, 6):
        line(ctx, [(-630, -230 + k * 38), (630, -230 + k * 38)], 1.6, "#5fb0b2")
    for k in range(-15, 16):
        line(ctx, [(k * 42, -230), (k * 42, 0)], 1.2, "#5fb0b2")
    line(ctx, [(-630, -230), (630, -230)], 5, "#4a9a9c")
    rrect(ctx, -630, -525, 1260, 525, 4, None, BOL)
    rrect(ctx, -670, -565, 1340, 44, 6, "#c9c4b8", BOL)                       # flat roof slab
    for vx in (-560, -90, 90, 560):                                            # vent blocks
        for j in range(3):
            rrect(ctx, vx - 34 + j * 24, -505, 18, 30, 3, "#d9d3c4", 1.5)
    for side, x0 in ((0, -440), (1, 250)):
        rrect(ctx, x0 - 12, -412, 214, 412, 4, "#e6e1d4", BOL)              # door frame
        if side == 0 and door_open > 0.01:
            rrect(ctx, x0, -400, 190, 400, 2, "#3d4450", 2)                     # dark inside
            w = 190 * (1 - 0.82 * door_open)
            poly(ctx, [(x0, -400), (x0 + w, -386), (x0 + w, -14), (x0, 0)], "#3f7fd0", BOL)
        else:
            col = "#3f7fd0" if side == 0 else "#ee7fae"
            rrect(ctx, x0, -400, 190, 400, 3, col, BOL)
            rrect(ctx, x0 + 18, -380, 154, 160, 6, shade(col, 0.12), 2)
            rrect(ctx, x0 + 18, -190, 154, 160, 6, shade(col, 0.12), 2)
            circle(ctx, x0 + 166, -200, 8, "#f2d36b", 2)
            circle(ctx, x0 + 95, -300, 46, "#ffffff", BOL * 0.8)               # icon plate
            (_man_icon if side == 0 else _woman_icon)(ctx, x0 + 95, -295, 1.0, "#2f5fa8" if side == 0 else "#d8467f")
    # hand-wash basin with a little mirror between the doors
    rrect(ctx, -70, -350, 140, 110, 10, "#dff3fb", BOL * 0.8)
    line(ctx, [(-40, -335), (-10, -262)], 4, (1, 1, 1, 0.9))
    poly(ctx, [(-90, -190), (90, -190), (70, -150), (-70, -150)], "#ffffff", BOL * 0.8)
    line(ctx, [(0, -150), (0, -40)], 14, "#d9d3c4")
    line(ctx, [(20, -205), (20, -226), (-4, -226)], 6, "#9aa3ab")
    _sign(ctx, "បន្ទប់ទឹក", 0, -462, 52, "#2f5fa8", w=330)
    ctx.restore()


def water_jar(ctx, x, base, s=1.0):
    ctx.save()
    ctx.translate(x, base)
    ctx.scale(s, s)
    ctx.new_path()
    ctx.move_to(-40, -150)
    ctx.curve_to(-110, -120, -100, -10, -50, 0)
    ctx.line_to(50, 0)
    ctx.curve_to(100, -10, 110, -120, 40, -150)
    ctx.close_path()
    fill_stroke(ctx, "#b8653a", BOL)
    ellipse(ctx, 0, -150, 44, 12, "#8f4a28", BOL * 0.8)
    line(ctx, [(-80, -90), (80, -90)], 4, "#d98a5a")
    ctx.restore()


def food_stall(ctx, cx, base, s=1.0, t=0.0):
    """Roadside breakfast stall: zinc roof, striped valance, sign "ហាងបាយ", counter with pots."""
    ctx.save()
    ctx.translate(cx, base)
    ctx.scale(s, s)
    for px in (-280, 280):
        rrect(ctx, px - 11, -430, 22, 430, 4, "#8a5a3c", BOL * 0.8)
    rrect(ctx, -250, -330, 500, 160, 2, "#f6e7c8", BOL * 0.6)                 # back wall
    for k, col in enumerate(("#d8443a", "#f2a23a", "#3f9a5a")):
        rrect(ctx, -220 + k * 160, -310, 120, 60, 6, col, 2)                 # menu boards
    rrect(ctx, -250, -175, 500, 175, 8, "#3f7fd0", BOL)                       # counter
    line(ctx, [(-250, -140), (250, -140)], 6, "#f4f1e8")
    for x, w, h, col in ((-150, 110, 74, "#c9ccd2"), (20, 92, 60, "#e8e4da"), (150, 80, 50, "#c9ccd2")):
        rrect(ctx, x - w / 2, -175 - h, w, h, 10, col, BOL * 0.8)              # pots and rice cooker
        line(ctx, [(x - w / 2 - 8, -175 - h), (x + w / 2 + 8, -175 - h)], 6, OUTLINE)
    for i in range(3):
        k = (t * 0.5 + i / 3.0) % 1.0
        ctx.new_path()
        ctx.arc(-150 + (i - 1) * 18 + math.sin(k * 6 + i) * 6, -260 - k * 110, 10 + k * 14, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.55 * (1 - k))
        ctx.fill()
    poly(ctx, [(-330, -470), (330, -470), (360, -420), (-360, -420)], "#aab3bd", BOL)  # zinc roof
    for k in range(-8, 9):
        line(ctx, [(k * 40, -468), (k * 43, -422)], 1.6, "#8f99a4")
    for k in range(18):                                                        # striped valance
        x0 = -360 + k * 40
        poly(ctx, [(x0, -420), (x0 + 40, -420), (x0 + 40, -392), (x0 + 20, -380), (x0, -392)],
             "#e8433a" if k % 2 == 0 else "#ffffff", 1.6)
    _sign(ctx, "ហាងបាយ", 0, -510, 46, "#e8433a", w=250)
    ctx.restore()


def _rest_stop_scene(ctx, layer, t, tod, view, lt):
    hz = 610
    if layer == "SKY":
        B.sky(ctx, t, tod, hz)
    elif layer == "BG":
        B.hills(ctx, hz + 20, "#9cc08f" if tod != "sunrise" else "#a9b98a", 34, 12)
        for k in range(12):
            B.sugar_palm(ctx, -420 + k * 270 + (k % 3) * 40, hz + 46, 140 + (k % 3) * 30, t,
                         "#5d8a48" if tod == "sunrise" else "#3f8f3a")
    elif layer == "MG":
        ctx.new_path()
        ctx.rectangle(B.X0, hz + 40, B.X1 - B.X0, 260)
        src(ctx, "#9cc65e" if tod == "sunrise" else "#8cc95a")
        ctx.fill()
        if view == "yard":
            for x, h in ((-300, 420), (560, 470), (2150, 440)):
                B.sugar_palm(ctx, x, 860, h, t, "#4d8a45")
            B.tree(ctx, 1150, 840, 1.25, "#4fa83d", seed=3)
        elif view == "toilets":
            for x, h in ((-80, 480), (2060, 470)):
                B.sugar_palm(ctx, x, 900, h, t, "#4d8a45")
            B.tree(ctx, 1900, 880, 1.3, "#4fa83d", seed=5)
        else:  # breakfast: the van and the toilets across the yard, beyond the stall
            B.sugar_palm(ctx, 1500, 760, 380, t, "#4d8a45")
            toilet_block(ctx, 1630, 772, 0.30)
            van(ctx, 1310, 775, 0.36, lt, -1, False, 0, True)
    elif layer == "GROUND":
        ctx.new_path()
        ctx.rectangle(B.X0, 850, B.X1 - B.X0, 500)
        ctx.set_source(lin_grad(0, 850, 0, 1100, [(0, "#d9bf92"), (1, "#c9a878")]))
        ctx.fill()
        r = rng(77)
        for _ in range(60):
            x, y = r.uniform(B.X0, B.X1), r.uniform(880, 1080)
            ellipse(ctx, x, y, r.uniform(6, 16), r.uniform(2, 4), (0.62, 0.48, 0.32, 0.35), 0)
        if view == "yard":
            food_stall(ctx, 930, 870, 0.72, lt)
            toilet_block(ctx, 1660, 880, 0.62, float(B.CUR.get("door_k", 0.0)))
            water_jar(ctx, 2090, 884, 0.6)
            van(ctx, float(B.CUR.get("van_x", 250)), 905, float(B.CUR.get("van_s", 0.92)), lt, 1, False, 0, True)
        elif view == "toilets":
            rrect(ctx, B.X0, 893, B.X1 - B.X0, 22, 2, "#cfc8b8", BOL * 0.8)  # concrete apron
            d0, d1 = (B.CUR.get("door_open") or [99.0, 99.0])[:2]
            k = clamp((lt - d0) / 0.35, 0, 1) * (1 - clamp((lt - d1) / 0.35, 0, 1))
            toilet_block(ctx, 960, 900, 1.0, k)
            water_jar(ctx, 1720, 905, 1.0)
            B.bush(ctx, 170, 905, 1.4, "#4c8f35")
        else:
            import bg_town as BT
            ctx.new_path()
            ctx.rectangle(B.X0, 780, B.X1 - B.X0, 600)
            ctx.set_source(lin_grad(0, 780, 0, 1080, [(0, "#d7cfbf"), (1, "#c2b8a6")]))  # concrete floor
            ctx.fill()
            line(ctx, [(B.X0, 780), (B.X1, 780)], 3, "#a99f8c")
            if B.CUR.get("stall", True):  # stall: false keeps the counter out of a close shot
                food_stall(ctx, 560, 785, 0.95, lt)
            for px in (-60, 1840):
                rrect(ctx, px - 14, -200, 28, 990, 4, "#8a5a3c", BOL * 0.8)   # posts holding the awning
            tabs, w, chairs = BT.table_conf()
            BT.draw_chairs(ctx, chairs, "plastic", ("#d8433a", "#2f7fc0"))
    elif layer == "OVER":
        if view == "breakfast":
            import bg_town as BT
            tabs, w, chairs = BT.table_conf()
            BT.draw_tables(ctx, tabs, w, "cloth", "restaurant", t, True)
            for k in range(-14, 64):                                         # the awning edge above the diners
                x0 = -560 + k * 50
                poly(ctx, [(x0, -260), (x0 + 50, -260), (x0 + 50, 60), (x0 + 25, 84), (x0, 60)],
                     "#e8433a" if k % 2 == 0 else "#ffffff", 1.6)
            line(ctx, [(B.X0, 60), (B.X1, 60)], BOL, OUTLINE)
    elif layer == "FG":
        if view == "yard":
            for x in (-420, 2300):
                B.bush(ctx, x, 1120, 1.8, "#4c8f35")


@extra
def _rest_stop(ctx, layer, t, tod):
    _rest_stop_scene(ctx, layer, t, tod, B.CUR.get("view", "yard"), _lt(t))


def with_van(envs, base):
    """`base` environment plus the white van parked in the scene (params van_x, van_y, van_s, van_facing)."""
    fn = envs[base]

    @extra
    def _wrapped(ctx, layer, t, tod):
        if layer in ("OVER", "SCREEN") and not getattr(fn, "extra_layers", False):
            return
        fn(ctx, layer, t, tod)
        if layer == "GROUND":
            van(ctx, float(B.CUR.get("van_x", 1760)), float(B.CUR.get("van_y", 860)), float(B.CUR.get("van_s", 0.82)),
                _lt(t), int(B.CUR.get("van_facing", -1)), False, 0)
    return _wrapped


def register(envs):
    envs.update({
        "van_road": _van_road,
        "van_inside": _van_inside,
        "map_route": _map_route,
        "photo_end": _photo_end,
        "memories": _memories,
        "rest_stop": _rest_stop,
    })
    if "hotel" in envs:
        envs["hotel_van"] = with_van(envs, "hotel")
