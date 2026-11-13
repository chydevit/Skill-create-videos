"""Soft kids-cartoon look for the character rig (bible rig key "look": "kids").

Same skeleton, poses, timing, lip-sync and props as rig.py, drawn differently:
thin dark-brown outlines, natural skin with cel shading, big eyes with irises and highlights,
brows, ears, a small nose, volumetric hair with shine, collared shirts / T-shirts / polos,
shorts / jeans / skirts, and rounded clogs, sneakers or sandals.

Extra rig keys (all optional):
  "eyes":     iris colour (default dark brown)
  "footwear": {"type": "clogs" | "sneakers" | "sandals", "color": "#..."}
  hair.style: short | curly | long | bob | bun | bun_top | ponytail | none
  top.style:  tshirt | polo | shirt | longsleeve | blouse ;  bottom.style: shorts | longpants | pants | skirt | sampot
"""
import math
import zlib

import cairocffi as cairo

import rig as RG
from drawutil import (clamp, ellipse_path, flower, hexc, ik2, lerp, mix, poly_path, rrect, rrect_path, shade, smooth,
                      smooth_path, src, stripe_pattern)

KO = (0.22, 0.13, 0.09)  # outline: dark brown
KW = 3.0                 # outline width (character units, ~430 tall)
SKIN = "#F0C09A"
HAIR = "#241a16"

KBUILDS = {
    # R head radius, sw shoulder width, sh shoulder y, wa waist y, hip y, a1/a2 arm bones, aw/lw limb widths
    "adult_m": dict(R=64, sw=112, sh=-314, wa=-208, hip=-190, a1=77, a2=71, aw=24, lw=37, neck=16),
    "adult_f": dict(R=62, sw=100, sh=-302, wa=-206, hip=-186, a1=73, a2=67, aw=21, lw=33, neck=15),
    "elder_m": dict(R=64, sw=112, sh=-300, wa=-196, hip=-180, a1=74, a2=68, aw=24, lw=36, neck=14, stoop=5),
    "elder_f": dict(R=62, sw=100, sh=-292, wa=-194, hip=-176, a1=70, a2=64, aw=21, lw=33, neck=13, stoop=5),
    "teen": dict(R=64, sw=102, sh=-280, wa=-184, hip=-168, a1=69, a2=63, aw=21, lw=33, neck=14),
    "child": dict(R=70, sw=90, sh=-206, wa=-126, hip=-114, a1=52, a2=48, aw=20, lw=30, neck=10),
}


def build_of(rig):
    b = dict(KBUILDS.get(rig.get("build", "adult_m"), KBUILDS["adult_m"]))
    if rig.get("female") and rig.get("build") in ("teen", "child"):
        b["sw"] *= 0.94
    k = float(rig.get("stretch") or 1.0)  # taller body (torso, legs, arms) under the same head, e.g. the tallest friend
    if k != 1.0:
        for key in ("sh", "wa", "hip", "a1", "a2"):
            b[key] *= k
    return b


def is_female(rig):
    return rig.get("build", "").endswith("_f") or bool(rig.get("female"))


def skin_of(rig):
    s = rig.get("skin")
    return s if s and s.upper() != RG.SKIN.upper() else SKIN


def head_y(b):
    return b["sh"] - b["R"] * 0.98 - b["neck"]


def character_height(rig):
    b = build_of(rig)
    return -head_y(b) + b["R"] * 1.05


def head_center(rig, x, y, scale):
    b = build_of(rig)
    return x, y + head_y(b) * scale, b["R"] * scale


# --------------------------------------------------------------------------- primitives (brown outline)

def _fs(ctx, fill, ol=KW):
    if fill is not None:
        if isinstance(fill, cairo.Pattern):
            ctx.set_source(fill)
        else:
            src(ctx, fill)
        if ol:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if ol:
        src(ctx, KO)
        ctx.set_line_width(ol)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()
    else:
        ctx.new_path()


def kpoly(ctx, pts, fill, ol=KW):
    ctx.new_path()
    poly_path(ctx, pts)
    _fs(ctx, fill, ol)


def kell(ctx, x, y, rx, ry, fill, ol=KW, rot=0.0):
    ctx.new_path()
    ellipse_path(ctx, x, y, max(0.1, rx), max(0.1, ry), rot)
    _fs(ctx, fill, ol)


def kline(ctx, pts, w, col=KO, a=1.0, cap=cairo.LINE_CAP_ROUND):
    ctx.new_path()
    poly_path(ctx, pts, close=False)
    src(ctx, col, a)
    ctx.set_line_width(w)
    ctx.set_line_cap(cap)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()


def kcurve(ctx, p0, c1, p1, w, col=KO, a=1.0):
    ctx.new_path()
    ctx.move_to(*p0)
    ctx.curve_to(p0[0] + (c1[0] - p0[0]) * 0.66, p0[1] + (c1[1] - p0[1]) * 0.66,
                 p1[0] + (c1[0] - p1[0]) * 0.66, p1[1] + (c1[1] - p1[1]) * 0.66, *p1)
    src(ctx, col, a)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()


def klimb(ctx, pts, width, fill, ol=KW, cap=cairo.LINE_CAP_ROUND):
    ctx.new_path()
    poly_path(ctx, pts, close=False)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_cap(cap)
    if ol:
        src(ctx, KO)
        ctx.set_line_width(width + 2 * ol)
        ctx.stroke_preserve()
    src(ctx, fill)
    ctx.set_line_width(width)
    ctx.stroke()


def cel(ctx, path_fn, fill, shadow, x_cut, rect):
    """Fill a shape, then a cel-shadow band (x > x_cut) inside it, then the outline."""
    path_fn()
    ctx.save()
    ctx.clip_preserve()
    _fs(ctx, fill, 0)
    ctx.new_path()
    ctx.rectangle(x_cut, rect[1], rect[2], rect[3])
    src(ctx, shadow)
    ctx.fill()
    ctx.restore()
    path_fn()
    _fs(ctx, None)


# --------------------------------------------------------------------------- head

def _sph(cx, R, phi, a, k):
    r = math.radians(phi + a)
    return cx + R * k * math.sin(r), math.cos(r)


def head_path(ctx, cx, cy, R, s):
    ctx.new_path()
    ctx.arc(cx, cy, R, math.pi, 2 * math.pi)
    chin = cx + R * 0.12 * s
    ctx.curve_to(cx + R * 1.01, cy + R * 0.45, cx + R * (0.62 + 0.18 * s), cy + R * 0.98, chin, cy + R * 1.02)
    ctx.curve_to(cx - R * (0.62 - 0.18 * s), cy + R * 0.98, cx - R * 1.01, cy + R * 0.45, cx - R, cy)
    ctx.close_path()


def draw_ear(ctx, x, y, R, skin, d):
    kell(ctx, x, y, R * 0.15, R * 0.21, skin, KW * 0.9)
    kcurve(ctx, (x + d * R * 0.04, y - R * 0.10), (x - d * R * 0.08, y), (x + d * R * 0.03, y + R * 0.10), R * 0.025,
           shade(skin, -0.32))


def _hair_cols(hcol):
    hi = mix(hcol, "#b8927c", 0.38) if sum(hexc(hcol)) < 1.0 else shade(hcol, 0.3)
    return hcol, shade(hcol, -0.35), hi


def _hairline(cx, cy, R, s, c, style):
    """Lower edge of the hair cap as a function of x (screen), for the face-forward side."""
    fx = cx + R * 0.45 * s
    fw = R * (0.82 * abs(c) + 0.58 * abs(s))
    d = 1 if s >= 0 else -1
    back = c < -0.25
    nape = 0.32 if style in ("short", "curly") else 0.55

    def f(x):
        if back:
            return cy + R * (0.58 if style not in ("long", "bob") else 1.2)
        u = (x - fx) / max(1.0, fw)
        side_back = d * u < 0
        if abs(u) > 1.0:
            extra = min(1.0, (abs(u) - 1.0) * 2.5)
            base = cy + R * 0.04
            if side_back:
                return base + R * nape * abs(s) * extra
            return base
        if style == "curly":
            y = cy - R * 0.20 + R * 0.24 * u * u + R * 0.075 * abs(math.sin(u * math.pi * 2.2))
        elif style in ("long", "bob"):
            y = cy - R * 0.44 + R * 0.40 * abs(u - 0.12 * d) ** 0.85
        elif style in ("bun", "bun_top", "ponytail"):
            y = cy - R * 0.38 + R * 0.40 * u * u
        elif style == "bangs":
            y = cy - R * 0.14 + R * 0.04 * abs(math.sin(u * math.pi * 3)) + R * 0.16 * max(0, abs(u) - 0.6) / 0.4
        else:  # short, side-swept fringe with small tufts
            y = cy - R * 0.40 + R * 0.34 * u * u + R * 0.20 * smooth((u * d + 0.5) / 1.3) \
                + R * 0.06 * abs(math.sin(u * 5.5 + 0.6))
        return y
    return f


def draw_hair_cap(ctx, rig, cx, cy, R, phi):
    hair = rig["hair"]
    style = hair.get("style", "short")
    if style in ("none", "shaved"):
        return
    s, c = math.sin(math.radians(phi)), math.cos(math.radians(phi))
    hcol, hdark, hhi = _hair_cols(hair.get("color", HAIR))
    vol = {"curly": 1.13, "long": 1.08, "bob": 1.09, "short": 1.07, "bangs": 1.09}.get(style, 1.05)
    vx, vy = cx - R * 0.03 * s, cy - R * 0.05
    f = _hairline(cx, cy, R, s, c, style)
    xs = [cx - R * 1.4 + i * R * 2.8 / 48 for i in range(49)]
    edge = [(x, f(x)) for x in xs]

    def clip_region():
        ctx.new_path()
        ctx.move_to(cx - R * 1.4, cy - R * 2.0)
        ctx.line_to(cx + R * 1.4, cy - R * 2.0)
        for p in reversed(edge):
            ctx.line_to(*p)
        ctx.close_path()

    def volume():
        ctx.new_path()
        if style == "curly":
            for k in range(13):
                a = math.pi + k * math.pi / 12
                rr = R * (0.30 if k % 2 else 0.26)
                ctx.new_sub_path()
                ctx.arc(vx + math.cos(a) * R * 0.92, vy + math.sin(a) * R * 0.92, rr, 0, 2 * math.pi)
            ctx.new_sub_path()
            ctx.arc(vx, vy + R * 0.02, R * 0.98, 0, 2 * math.pi)
        elif style == "short":  # tousled top: a few soft lobes on the crown
            for k in range(6):
                a = math.pi * 1.12 + k * math.pi * 0.152 + 0.1 * s
                ctx.new_sub_path()
                ctx.arc(vx + math.cos(a) * R * 0.86, vy + math.sin(a) * R * 0.86, R * (0.27 if k % 2 else 0.24), 0,
                        2 * math.pi)
            ctx.new_sub_path()
            ellipse_path(ctx, vx, vy, R * vol, R * vol * 0.98)
        else:
            ellipse_path(ctx, vx, vy, R * vol, R * vol * 0.98)

    # outline first (double width): the fill below hides the inner half and the lobes' inner edges
    ctx.save()
    clip_region()
    ctx.clip()
    volume()
    src(ctx, KO)
    ctx.set_line_width(KW * 2)
    ctx.stroke()
    ctx.restore()
    ctx.save()
    clip_region()
    ctx.clip()
    volume()
    ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    src(ctx, hcol)
    ctx.fill()
    # cel shadow on the back/right side (inside the hair volume only)
    volume()
    ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    ctx.clip()
    ctx.new_path()
    ellipse_path(ctx, vx - R * 0.25, vy - R * 0.22, R * vol, R * vol)
    ctx.rectangle(cx - R * 2, cy - R * 2, R * 4, R * 4)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    src(ctx, hdark, 0.55)
    ctx.fill()
    ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    # strands + shine
    if c > -0.25:
        for k in (-0.5, -0.1, 0.3):
            x0 = cx + R * (k + 0.5 * s)
            kcurve(ctx, (x0 + R * 0.25, cy - R * 0.95), (x0 - R * 0.05, cy - R * 0.6), (x0 - R * 0.12, cy - R * 0.32),
                   R * 0.03, hdark, 0.8)
    kcurve(ctx, (cx - R * 0.62 - R * 0.2 * s, cy - R * 0.55), (cx - R * 0.42 - R * 0.2 * s, cy - R * 0.92),
           (cx - R * 0.02 - R * 0.2 * s, cy - R * 0.98), R * 0.085, hhi, 0.75)
    if style == "curly":
        for k in range(6):
            a = math.pi * 1.1 + k * math.pi * 0.16
            x0, y0 = vx + math.cos(a) * R * 0.75, vy + math.sin(a) * R * 0.75
            ctx.new_path()
            ctx.arc(x0, y0, R * 0.13, a - 2.2, a + 0.6)
            src(ctx, hdark)
            ctx.set_line_width(R * 0.03)
            ctx.stroke()
    ctx.restore()
    # hairline edge (clipped to the hair volume)
    ctx.save()
    volume()
    ctx.clip()
    kline(ctx, edge, KW)
    ctx.restore()


def draw_hair_back_k(ctx, rig, cx, cy, R, phi, sh_y):
    """Hair that hangs behind the head and shoulders (long, bob, ponytail, buns)."""
    hair = rig["hair"]
    style = hair.get("style", "short")
    s, c = math.sin(math.radians(phi)), math.cos(math.radians(phi))
    hcol, hdark, hhi = _hair_cols(hair.get("color", HAIR))
    d = 1 if s >= 0 else -1
    x0 = cx - R * 0.35 * s
    if style == "long":
        pts = [(x0 - R * 1.02, cy - R * 0.1), (x0 - R * 1.12, cy + R * 1.2), (x0 - R * 0.95, cy + R * 2.05),
               (x0 - R * 0.2, cy + R * 2.25), (x0 + R * 0.6, cy + R * 2.15), (x0 + R * 1.05, cy + R * 1.5),
               (x0 + R * 1.05, cy - R * 0.1)]
        ctx.new_path()
        smooth_path(ctx, pts)
        _fs(ctx, hcol)
        for k in (-0.5, 0.0, 0.5):
            kcurve(ctx, (x0 + R * k, cy + R * 0.4), (x0 + R * (k + 0.1), cy + R * 1.3), (x0 + R * k * 0.8, cy + R * 2.0),
                   R * 0.03, hdark, 0.7)
    elif style in ("bob", "bangs"):
        pts = [(x0 - R * 1.08, cy - R * 0.1), (x0 - R * 1.12, cy + R * 0.85), (x0 - R * 0.7, cy + R * 0.98),
               (x0 + R * 0.7, cy + R * 0.98), (x0 + R * 1.12, cy + R * 0.85), (x0 + R * 1.08, cy - R * 0.1)]
        ctx.new_path()
        poly_path(ctx, pts)
        _fs(ctx, hcol)
    elif style == "ponytail":
        bx = cx - d * R * 0.95 * abs(s) - R * 0.1 * s
        sway = math.sin(phi * 0.02) * R * 0.05
        ctx.new_path()
        ctx.move_to(bx - R * 0.18, cy - R * 0.45)
        ctx.curve_to(bx - d * R * 0.6, cy - R * 0.1, bx - d * R * 0.5 + sway, cy + R * 0.9, bx - d * R * 0.25 + sway,
                     cy + R * 1.35)
        ctx.curve_to(bx - d * R * 0.05, cy + R * 0.8, bx + R * 0.1, cy - R * 0.1, bx + R * 0.18, cy - R * 0.45)
        ctx.close_path()
        _fs(ctx, hcol)
    if style in ("bun", "bun_top"):
        bx, by, br, dep = RG._bun_pos(cx, cy, R * 1.02, phi, style)
        if (style == "bun" and dep < 0.25) or (style == "bun_top" and dep < -0.2):
            _bun(ctx, rig, bx, by, br, phi)


def _bun(ctx, rig, bx, by, br, phi):
    hcol, hdark, hhi = _hair_cols(rig["hair"].get("color", HAIR))
    kell(ctx, bx, by, br, br * 0.92, hcol)
    kcurve(ctx, (bx - br * 0.55, by - br * 0.1), (bx - br * 0.1, by - br * 0.75), (bx + br * 0.5, by - br * 0.35),
           br * 0.14, hhi, 0.7)
    kcurve(ctx, (bx - br * 0.4, by + br * 0.35), (bx + br * 0.1, by + br * 0.05), (bx + br * 0.55, by + br * 0.3),
           br * 0.08, hdark, 0.8)
    fl = rig["hair"].get("flower")
    if fl:
        side = 1 if math.sin(math.radians(phi)) >= 0 else -1
        flower(ctx, bx + side * br * 0.55, by + br * 0.5, br * 0.42, fl)


def draw_side_locks(ctx, rig, cx, cy, R, phi):
    """Long / bob hair strands framing the face (front and 3/4 views only)."""
    hair = rig["hair"]
    if hair.get("style") not in ("long", "bob", "bangs"):
        return
    s, c = math.sin(math.radians(phi)), math.cos(math.radians(phi))
    if c < 0.3:
        return
    hcol, hdark, hhi = _hair_cols(hair.get("color", HAIR))
    long_ = hair.get("style") == "long"
    for a in (-84, 84):
        x, vis = _sph(cx, R, phi, a, 1.0)
        if vis < -0.2:
            continue
        side = 1 if a > 0 else -1
        y0, y1 = cy - R * 0.30, cy + R * (1.45 if long_ else 0.88)
        w = R * (0.20 if long_ else 0.24)
        pts = [(x - side * w * 0.55, y0), (x + side * w * 0.65, y0 - R * 0.05), (x + side * w * 0.75, cy + R * 0.5),
               (x + side * w * 0.45, y1 - R * 0.12), (x + side * w * 0.05, y1), (x - side * w * 0.35, y1 - R * 0.25),
               (x - side * w * 0.45, cy + R * 0.35)]
        ctx.new_path()
        smooth_path(ctx, pts)
        _fs(ctx, hcol)
        kcurve(ctx, (x, y0 + R * 0.15), (x + side * w * 0.2, cy + R * 0.6), (x + side * w * 0.1, y1 - R * 0.2), R * 0.02,
               hdark, 0.8)


def draw_eye(ctx, x, ey, R, sq, expr, blink, look, iris, female, side, skin):
    rx, ry = R * 0.165 * sq, R * 0.205
    lw = R * 0.042
    closed = blink or expr in ("laughing", "grin", "sleepy", "yawn", "crying")
    if closed:
        if expr in ("laughing", "grin") and not blink:  # ^ ^
            kcurve(ctx, (x - rx * 1.05, ey + ry * 0.15), (x, ey - ry * 0.95), (x + rx * 1.05, ey + ry * 0.15), lw)
        else:  # gentle closed lid
            kcurve(ctx, (x - rx * 1.05, ey - ry * 0.05), (x, ey + ry * 0.7), (x + rx * 1.05, ey - ry * 0.05), lw)
            if female:
                kline(ctx, [(x + side * rx * 0.95, ey - ry * 0.02), (x + side * rx * 1.35, ey - ry * 0.25)], lw * 0.7)
        return
    k = {"surprised": 1.14, "afraid": 1.12, "angry": 0.92, "determined": 0.95, "calm": 0.95}.get(expr, 1.0)
    rx, ry = rx * k, ry * k
    lid = {"calm": 0.32, "sad": 0.30, "worried": 0.22, "angry": 0.30, "determined": 0.22, "shy": 0.18,
           "thinking": 0.12}.get(expr, 0.0)
    lx, ly = look
    if expr == "thinking":
        lx, ly = 0.55, -0.7
    elif expr == "shy":
        ly = 0.6
    elif expr == "pout":
        lx, ly = -0.55, -0.55
    ctx.save()
    kell(ctx, x, ey, rx, ry, "#ffffff", 0)
    ctx.new_path()
    ellipse_path(ctx, x, ey, rx, ry)
    ctx.clip()
    ir = R * (0.125 if expr not in ("surprised", "afraid") else 0.10)
    ix, iy = x + lx * rx * 0.45, ey + ry * 0.12 + ly * ry * 0.35
    kell(ctx, ix, iy, ir * sq ** 0.5, ir, iris, 0)
    kell(ctx, ix, iy + ir * 0.25, ir * 0.75 * sq ** 0.5, ir * 0.62, shade(iris, 0.18), 0)
    kell(ctx, ix, iy, ir * 0.52 * sq ** 0.5, ir * 0.52, (0.07, 0.05, 0.04), 0)
    kell(ctx, ix - ir * 0.38, iy - ir * 0.42, ir * 0.33, ir * 0.33, "#ffffff", 0)
    kell(ctx, ix + ir * 0.35, iy + ir * 0.32, ir * 0.13, ir * 0.13, "#ffffff", 0)
    if lid > 0:  # eyelid (skin) coming down over the top, slanted for angry / sad
        tilt = {"angry": 0.35, "determined": 0.25, "sad": -0.3, "worried": -0.25}.get(expr, 0.0) * side
        yl = ey - ry + 2 * ry * lid
        ctx.new_path()
        ctx.move_to(x - rx * 1.3, ey - ry * 1.4)
        ctx.line_to(x + rx * 1.3, ey - ry * 1.4)
        ctx.line_to(x + rx * 1.3, yl - tilt * ry * 0.9)
        ctx.line_to(x - rx * 1.3, yl + tilt * ry * 0.9)
        ctx.close_path()
        src(ctx, skin)
        ctx.fill()
        kline(ctx, [(x - rx * 1.3, yl + tilt * ry * 0.9), (x + rx * 1.3, yl - tilt * ry * 0.9)], lw * 0.9)
    ctx.restore()
    kell(ctx, x, ey, rx, ry, None, KW * 0.7)
    # upper lash line
    ctx.new_path()
    ctx.save()
    ctx.translate(x, ey)
    ctx.scale(rx, ry)
    ctx.arc(0, 0, 1.0, math.pi * 1.08, math.pi * 1.92)
    ctx.restore()
    src(ctx, KO)
    ctx.set_line_width(lw)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    if female:
        ox, oy = x + side * rx * 0.92, ey - ry * 0.45
        kline(ctx, [(ox, oy), (ox + side * rx * 0.42, oy - ry * 0.32)], lw * 0.8)
        kline(ctx, [(ox - side * rx * 0.05, oy - ry * 0.18), (ox + side * rx * 0.3, oy - ry * 0.62)], lw * 0.6)


def draw_brow(ctx, x, ey, R, sq, expr, side, i, col):
    by = ey - R * 0.34
    w = R * 0.15 * sq
    di, do, arch = 0.0, 0.0, -0.05
    if expr in ("happy", "smile", "laughing", "grin"):
        di, do, arch = -0.02, 0.0, -0.09
    elif expr == "pout":
        di, do, arch = -0.06, 0.03, -0.03
    elif expr in ("sad", "worried", "crying", "afraid", "shy"):
        di, do, arch = -0.08, 0.05, -0.02
    elif expr in ("angry", "determined"):
        di, do, arch = 0.09, -0.05, 0.0
    elif expr in ("surprised",):
        di, do, arch = -0.10, -0.08, -0.10
    elif expr == "thinking":
        di, do, arch = (-0.10, -0.06, -0.08) if i == 0 else (0.03, 0.02, -0.02)
    elif expr in ("sleepy", "calm", "yawn"):
        di, do, arch = 0.02, 0.03, -0.03
    inner = (x - side * w, by + R * di)
    outer = (x + side * w * 1.05, by + R * do)
    mid = ((inner[0] + outer[0]) / 2, (inner[1] + outer[1]) / 2 + R * arch)
    kcurve(ctx, inner, mid, outer, R * 0.062, col)


def draw_mouth_k(ctx, cx, cy, R, phi, expr, vis_name, openness, skin):
    mx, vis = _sph(cx, R, phi, 4, 0.82)
    if vis < 0.05:
        return
    my = cy + R * 0.66
    sq = 0.55 + 0.45 * vis
    u = R * 0.22
    lw = R * 0.036
    inside = "#7a2d28"

    def open_mouth(w, h, smile=True, teeth=True, tongue=True, frown=False, tongue_y=0.72):
        ctx.new_path()
        if frown:
            ctx.move_to(mx - w, my + h * 0.35)
            ctx.curve_to(mx - w * 0.6, my - h * 0.75, mx + w * 0.6, my - h * 0.75, mx + w, my + h * 0.35)
            ctx.curve_to(mx + w * 0.5, my + h * 0.55, mx - w * 0.5, my + h * 0.55, mx - w, my + h * 0.35)
        else:
            ctx.move_to(mx - w, my - h * 0.35)
            ctx.curve_to(mx - w * 0.4, my - h * (0.45 if smile else 0.55), mx + w * 0.4,
                         my - h * (0.45 if smile else 0.55), mx + w, my - h * 0.35)
            ctx.curve_to(mx + w * 0.85, my + h * 0.95, mx - w * 0.85, my + h * 0.95, mx - w, my - h * 0.35)
        ctx.close_path()
        ctx.save()
        ctx.clip_preserve()
        _fs(ctx, inside, 0)
        if teeth and not frown:
            ctx.new_path()
            ctx.rectangle(mx - w * 1.2, my - h * 0.8, w * 2.4, h * 0.62)
            src(ctx, "#ffffff")
            ctx.fill()
        if tongue:
            kell(ctx, mx + w * 0.1, my + h * tongue_y, w * 0.55, h * 0.42, "#e8807a", 0)
        ctx.restore()
        ctx.new_path()
        if frown:
            ctx.move_to(mx - w, my + h * 0.35)
            ctx.curve_to(mx - w * 0.6, my - h * 0.75, mx + w * 0.6, my - h * 0.75, mx + w, my + h * 0.35)
            ctx.curve_to(mx + w * 0.5, my + h * 0.55, mx - w * 0.5, my + h * 0.55, mx - w, my + h * 0.35)
        else:
            ctx.move_to(mx - w, my - h * 0.35)
            ctx.curve_to(mx - w * 0.4, my - h * (0.45 if smile else 0.55), mx + w * 0.4,
                         my - h * (0.45 if smile else 0.55), mx + w, my - h * 0.35)
            ctx.curve_to(mx + w * 0.85, my + h * 0.95, mx - w * 0.85, my + h * 0.95, mx - w, my - h * 0.35)
        ctx.close_path()
        _fs(ctx, None, lw * 0.8)

    speaking = vis_name and vis_name != "rest" and openness > 0.05
    if speaking:
        u = R * 0.40
        o = clamp(openness, 0.15, 1.0)
        shapes = {"A": (0.62, 0.70), "E": (0.70, 0.42), "I": (0.62, 0.30), "O": (0.40, 0.60), "U": (0.28, 0.40),
                  "FV": (0.52, 0.25), "LR": (0.50, 0.48)}
        if vis_name == "MBP":
            kline(ctx, [(mx - u * 0.42 * sq, my), (mx + u * 0.42 * sq, my)], lw)
            return
        if vis_name == "TH":  # tongue tip between the teeth
            open_mouth(u * 0.5 * sq, u * 0.42, smile=expr in ("happy", "smile"), teeth=True, tongue=True, tongue_y=0.05)
            return
        if vis_name == "L":  # tongue raised behind the top teeth
            open_mouth(u * 0.48 * sq, u * 0.62, smile=expr in ("happy", "smile"), teeth=True, tongue=True, tongue_y=0.12)
            return
        w, h = shapes.get(vis_name, (0.5, 0.45))
        open_mouth(u * w * sq, u * h * (0.5 + 0.6 * o), smile=expr in ("happy", "smile", "laughing"),
                   teeth=vis_name in ("E", "I", "FV", "A"), tongue=vis_name in ("A", "LR", "O"))
        return
    if expr in ("happy", "smile", "shy"):
        w = u * (0.62 if expr == "happy" else 0.48) * sq
        kcurve(ctx, (mx - w, my - u * 0.12), (mx, my + u * (0.55 if expr == "happy" else 0.38)), (mx + w, my - u * 0.12),
               lw)
        if expr == "happy":
            for sd in (-1, 1):
                kline(ctx, [(mx + sd * w * 1.02, my - u * 0.2), (mx + sd * w * 1.12, my - u * 0.02)], lw * 0.7)
    elif expr == "laughing":
        open_mouth(u * 0.80 * sq, u * 0.95)
    elif expr == "grin":  # wide closed grin, teeth showing
        w, h = u * 0.95 * sq, u * 0.62
        ctx.new_path()
        ctx.move_to(mx - w, my - h * 0.3)
        ctx.curve_to(mx - w * 0.4, my - h * 0.05, mx + w * 0.4, my - h * 0.05, mx + w, my - h * 0.3)
        ctx.curve_to(mx + w * 0.8, my + h * 0.9, mx - w * 0.8, my + h * 0.9, mx - w, my - h * 0.3)
        ctx.close_path()
        _fs(ctx, "#ffffff", lw * 0.8)
        kcurve(ctx, (mx - w * 0.92, my - h * 0.12), (mx, my + h * 0.42), (mx + w * 0.92, my - h * 0.12), lw * 0.45)
        for sd in (-1, 1):
            kline(ctx, [(mx + sd * w * 1.0, my - h * 0.42), (mx + sd * w * 1.12, my - h * 0.2)], lw * 0.7)
    elif expr == "pout":  # small pushed-out frown
        kcurve(ctx, (mx - u * 0.26 * sq, my + u * 0.16), (mx, my - u * 0.06), (mx + u * 0.26 * sq, my + u * 0.16), lw)
        kcurve(ctx, (mx - u * 0.12 * sq, my + u * 0.30), (mx, my + u * 0.36), (mx + u * 0.12 * sq, my + u * 0.30),
               lw * 0.6, shade(skin, -0.3))
    elif expr in ("calm", "neutral"):
        kcurve(ctx, (mx - u * 0.32 * sq, my), (mx, my + u * 0.18), (mx + u * 0.32 * sq, my), lw)
    elif expr in ("sad", "worried"):
        kcurve(ctx, (mx - u * 0.42 * sq, my + u * 0.25), (mx, my - u * 0.2), (mx + u * 0.42 * sq, my + u * 0.25), lw)
    elif expr == "angry":
        w, h = u * 0.62 * sq, u * 0.42
        ctx.new_path()
        rrect_path(ctx, mx - w, my - h * 0.5, w * 2, h, h * 0.35)
        _fs(ctx, "#ffffff", lw * 0.8)
        kline(ctx, [(mx - w, my), (mx + w, my)], lw * 0.5)
        for k in (-0.5, 0.0, 0.5):
            kline(ctx, [(mx + w * k, my - h * 0.5), (mx + w * k, my + h * 0.5)], lw * 0.4)
    elif expr in ("surprised", "yawn"):
        open_mouth(u * (0.30 if expr == "surprised" else 0.40) * sq, u * (0.55 if expr == "surprised" else 0.85),
                   smile=False, teeth=False, tongue=expr == "yawn")
    elif expr == "afraid":
        pts = []
        for i in range(7):
            pts.append((mx - u * 0.55 * sq + i * u * 1.1 * sq / 6, my + (u * 0.1 if i % 2 else -u * 0.1)))
        kline(ctx, pts, lw)
    elif expr == "crying":
        open_mouth(u * 0.58 * sq, u * 0.55, smile=False, teeth=False, tongue=False, frown=True)
    elif expr == "thinking":
        kline(ctx, [(mx - u * 0.18 * sq, my + u * 0.08), (mx + u * 0.25 * sq, my - u * 0.02)], lw)
    elif expr == "determined":
        kline(ctx, [(mx - u * 0.36 * sq, my + u * 0.05), (mx + u * 0.36 * sq, my + u * 0.05)], lw)
    elif expr == "sleepy":
        kcurve(ctx, (mx - u * 0.2 * sq, my + u * 0.05), (mx, my + u * 0.2), (mx + u * 0.2 * sq, my + u * 0.05), lw)
    else:
        kcurve(ctx, (mx - u * 0.4 * sq, my), (mx, my + u * 0.3), (mx + u * 0.4 * sq, my), lw)


def draw_mask(ctx, cx, cy, R, phi, col):
    """Surgical face mask over nose and mouth, with ear loops."""
    pts = []
    for a, yk in ((-62, 0.36), (-30, 0.30), (0, 0.27), (30, 0.30), (62, 0.36), (58, 0.80), (30, 0.98), (0, 1.02),
                  (-30, 0.98), (-58, 0.80)):
        x, vis = _sph(cx, R, phi, a, 0.98)
        pts.append((x, cy + R * yk))
    ctx.new_path()
    smooth_path(ctx, pts)
    ctx.save()
    ctx.clip_preserve()
    _fs(ctx, col, 0)
    for k in (0.46, 0.62, 0.78):
        x0, _ = _sph(cx, R, phi, -55, 0.98)
        x1, _ = _sph(cx, R, phi, 55, 0.98)
        kline(ctx, [(x0, cy + R * k), (x1, cy + R * (k + 0.02))], R * 0.018, shade(col, -0.18))
    ctx.new_path()
    ctx.rectangle(cx + R * 0.25, cy, R * 2, R * 2)
    src(ctx, shade(col, -0.10), 0.6)
    ctx.fill()
    ctx.restore()
    ctx.new_path()
    smooth_path(ctx, pts)
    _fs(ctx, None, KW * 0.9)
    for a in (-80, 80):
        ex, vis = _sph(cx, R, phi, a, 0.96)
        if vis > -0.3:
            mx, _ = _sph(cx, R, phi, 62 if a > 0 else -62, 0.98)
            kline(ctx, [(mx, cy + R * 0.40), (ex, cy + R * 0.16)], R * 0.02, shade(col, -0.25))
            kline(ctx, [(mx, cy + R * 0.76), (ex, cy + R * 0.32)], R * 0.02, shade(col, -0.25))


def draw_powder_face(ctx, cx, cy, R, s, k):
    """White face powder over the skull, a little patchy at the edges."""
    ctx.save()
    head_path(ctx, cx, cy, R, s)
    ctx.clip()
    ctx.new_path()
    ellipse_path(ctx, cx + s * R * 0.12, cy + R * 0.18, R * 0.92, R * 0.82)
    ctx.set_source_rgba(1, 1, 1, 0.88 * k)
    ctx.fill()
    for i, (dx, dy, rr) in enumerate(((-0.62, -0.05, 0.30), (0.70, 0.10, 0.26), (0.05, 0.78, 0.30), (-0.35, 0.62, 0.22),
                                      (0.48, 0.66, 0.20), (0.10, -0.55, 0.26))):
        ctx.new_path()
        ctx.arc(cx + s * R * 0.12 + dx * R, cy + R * 0.18 + dy * R, rr * R, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.70 * k)
        ctx.fill()
    ctx.restore()


def draw_poof(ctx, cx, cy, R, dt):
    """Powder cloud bursting around a head, dt seconds after the dab (fades out by ~1.1 s)."""
    if dt < 0 or dt > 1.1:
        return
    grow = 1 - (1 - min(1.0, dt / 0.35)) ** 2
    a = 1.0 if dt < 0.45 else max(0.0, 1 - (dt - 0.45) / 0.65)
    for i in range(11):
        ang = i * 2 * math.pi / 11 + 0.3
        rr = R * (0.28 + 0.10 * ((i * 7) % 3))
        dist = R * (0.35 + 0.85 * grow) * (0.85 + 0.15 * ((i * 5) % 4) / 3)
        x, y = cx + math.cos(ang) * dist, cy + R * 0.2 + math.sin(ang) * dist * 0.8 - dt * R * 0.25
        ctx.new_path()
        ctx.arc(x, y, rr * (0.6 + 0.6 * grow), 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.92 * a)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.80, 0.78, 0.84, 0.55 * a)
        ctx.set_line_width(2.0)
        ctx.stroke()
    if dt < 0.5:
        ctx.new_path()
        ctx.arc(cx, cy + R * 0.2, R * (0.4 + 0.5 * grow), 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.85 * (1 - dt / 0.5))
        ctx.fill()


def draw_head_k(ctx, rig, cx, cy, R, phi, st, skin):
    s, c = math.sin(math.radians(phi)), math.cos(math.radians(phi))
    hair = rig["hair"]
    style = hair.get("style", "short")
    hcol = hair.get("color", HAIR)
    female = is_female(rig)
    d = 1 if s >= 0 else -1
    expr = st.get("expr", "neutral")
    t = st.get("t", 0.0)

    if style in ("bun", "bun_top"):
        pass  # back buns are drawn with the back hair
    # ears behind the head outline (front-ish views)
    ears = []
    for a in (-90, 90):
        ex, vis = _sph(cx, R, phi, a, 0.96)
        ears.append((ex - R * 0.10 * s * (1 if vis > 0.35 else 0), vis, 1 if a > 0 else -1))
    for ex, vis, sd in ears:
        if -0.55 < vis <= 0.35:
            draw_ear(ctx, ex + sd * R * 0.05 * abs(c), cy + R * 0.22, R, skin, sd)
    # skull with cel shading
    shadow = shade(skin, -0.13)
    head_path(ctx, cx, cy, R, s)
    ctx.save()
    ctx.clip_preserve()
    _fs(ctx, shadow, 0)
    ctx.new_path()
    ellipse_path(ctx, cx - R * 0.16, cy - R * 0.12, R * 1.0, R * 1.08)
    src(ctx, skin)
    ctx.fill()
    ctx.restore()
    if st.get("powder"):  # face dusted white with powder (eyes, brows and mouth stay on top)
        draw_powder_face(ctx, cx, cy, R, s, float(st["powder"]))
    head_path(ctx, cx, cy, R, s)
    _fs(ctx, None)
    for ex, vis, sd in ears:
        if vis > 0.35:
            draw_ear(ctx, ex, cy + R * 0.22, R, skin, -d)
    # earrings
    if "earrings" in rig.get("jewelry", []):
        for ex, vis, sd in ears:
            if vis > -0.3:
                kell(ctx, ex, cy + R * 0.45, R * 0.05, R * 0.05, RG.GOLD, 1.4)

    if c > -0.15:
        # blush
        for a in (-36, 36):
            bx, vis = _sph(cx, R, phi, a, 0.74)
            if vis > 0.2:
                kell(ctx, bx, cy + R * 0.47, R * 0.13 * (0.5 + 0.5 * vis), R * 0.065, (0.97, 0.55, 0.52, 0.35), 0)
        # eyes
        iris = rig.get("eyes", "#4a2c1a")
        eyes = []
        for i, a in enumerate((-27, 27)):
            x, vis = _sph(cx, R, phi, a, 0.80)
            if vis > 0.15:
                eyes.append((i, x, vis, -1 if a < 0 else 1))
        ey = cy + R * 0.16
        look = st.get("look", (0.0, 0.0)) or (0.0, 0.0)
        look = (look[0] + s * 0.35, look[1])
        for i, x, vis, side in eyes:
            sq = 0.45 + 0.55 * vis
            draw_eye(ctx, x, ey, R, sq, expr, st.get("blink", False), look, iris, female, side, skin)
        brow_col = shade(hcol, 0.06) if sum(hexc(hcol)) < 1.0 else shade(hcol, -0.3)
        for i, x, vis, side in eyes:
            draw_brow(ctx, x, ey, R, 0.45 + 0.55 * vis, expr, side, i, brow_col)
        # nose
        nx, nvis = _sph(cx, R, phi, 0, 0.97)
        ny = cy + R * 0.43
        if abs(s) > 0.8:
            kpoly(ctx, [(nx - d * R * 0.03, ny - R * 0.09), (nx + d * R * 0.08, ny + R * 0.02), (nx - d * R * 0.02, ny + R * 0.06)],
                  skin, KW * 0.8)
        else:
            kcurve(ctx, (nx - R * 0.035, ny - R * 0.05), (nx + d * R * 0.07, ny + R * 0.02), (nx - R * 0.02, ny + R * 0.06),
                   R * 0.03, shade(skin, -0.35))
        draw_mouth_k(ctx, cx, cy, R, phi, expr, st.get("viseme"), st.get("mouth_open", 0.0), skin)
        if st.get("mask"):
            draw_mask(ctx, cx, cy, R, phi, st["mask"] if isinstance(st["mask"], str) else "#f7f8fa")
        # tears / sweat
        if expr == "crying":
            for i, x, vis, side in eyes:
                ph = (t * 1.4 + x * 0.01) % 1.0
                kline(ctx, [(x, ey + R * 0.12), (x, ey + R * (0.3 + 0.4 * ph))], R * 0.06, (0.45, 0.75, 0.98), 0.85)
        if expr in ("afraid", "worried"):
            x = cx + R * 0.8 * math.sin(math.radians(phi + 55))
            y = cy - R * 0.15 + (t * 30) % 8
            kpoly(ctx, [(x, y - R * 0.13), (x + R * 0.08, y + R * 0.04), (x, y + R * 0.1), (x - R * 0.08, y + R * 0.04)],
                  (0.62, 0.84, 0.98), 1.4)
    draw_hair_cap(ctx, rig, cx, cy, R, phi)
    if style not in ("long", "bob", "bangs"):
        for ex, vis, sd in ears:
            if vis > 0.35:
                draw_ear(ctx, ex, cy + R * 0.22, R, skin, -d)
    draw_side_locks(ctx, rig, cx, cy, R, phi)
    if style in ("bun", "bun_top"):
        bx, by, br, dep = RG._bun_pos(cx, cy, R * 1.02, phi, style)
        front_bun = (style == "bun" and dep >= 0.25) or (style == "bun_top" and dep >= -0.2)
        if front_bun:
            _bun(ctx, rig, bx, by, br, phi)
    if hair.get("flower") and style not in ("bun", "bun_top"):
        fx, vis = _sph(cx, R, phi, -62, 0.86)
        flower(ctx, fx, cy - R * 0.55, R * 0.16, hair["flower"])
    RG.draw_headwear(ctx, rig, cx, cy, R, phi, t)


# --------------------------------------------------------------------------- body

def torso_path_k(ctx, b, F, top_y, bot, female, bulge=1.0):
    w = b["sw"] * (0.72 + 0.28 * abs(F.c)) / 2
    wb = w * (0.90 if female else 0.97) * bulge
    r = b["aw"] * 0.85
    ctx.new_path()
    ctx.move_to(-w + r, top_y)
    ctx.line_to(w - r, top_y)
    ctx.curve_to(w - r * 0.2, top_y, w + 1, top_y + r * 0.4, w + 1, top_y + r)
    ctx.curve_to(w + 3 * bulge, (top_y + bot) / 2, wb + 5, bot - 12, wb + 4, bot)
    ctx.curve_to(wb * 0.4, bot + 5, -wb * 0.4, bot + 5, -wb - 4, bot)
    ctx.curve_to(-wb - 5, bot - 12, -w - 3 * bulge, (top_y + bot) / 2, -w - 1, top_y + r)
    ctx.curve_to(-w - 1, top_y + r * 0.4, -w + r * 0.2, top_y, -w + r, top_y)
    ctx.close_path()
    return w


def draw_torso_k(ctx, rig, b, F, skin):
    top = rig["top"]
    style = top.get("style", "tshirt")
    col = top.get("color", "#3b7fd1")
    female = is_female(rig)
    sh_y = b["sh"]
    bot = b["hip"] + 16
    w = b["sw"] * (0.72 + 0.28 * abs(F.c)) / 2
    fill = col
    if top.get("pattern") == "stripes":
        fill = stripe_pattern(col, shade(col, -0.2), 9)
    cel(ctx, lambda: torso_path_k(ctx, b, F, sh_y, bot, female), fill, shade(col, -0.14), w * 0.38,
        (0, sh_y - 60, w * 2, bot - sh_y + 120))
    # hem fold
    kcurve(ctx, (-w * 0.7, bot - 10), (0, bot - 4), (w * 0.7, bot - 10), 1.6, shade(col, -0.3), 0.7)
    if F.c > -0.1:
        nx = F.x(0, 14)
        dark = shade(col, -0.38)
        if style == "tshirt":
            ctx.new_path()
            ctx.move_to(nx - 17, sh_y + 1)
            ctx.curve_to(nx - 10, sh_y + 16, nx + 10, sh_y + 16, nx + 17, sh_y + 1)
            ctx.close_path()
            _fs(ctx, shade(skin, -0.12), 0)
            kcurve(ctx, (nx - 18, sh_y + 1), (nx, sh_y + 19), (nx + 18, sh_y + 1), 4.2, shade(col, -0.18))
            kcurve(ctx, (nx - 18, sh_y + 1), (nx, sh_y + 19), (nx + 18, sh_y + 1), 1.4, KO, 0.8)
        elif style in ("polo", "shirt"):
            vd = 30 if style == "shirt" else 18
            kpoly(ctx, [(nx - 12, sh_y), (nx + 12, sh_y), (nx, sh_y + vd)], shade(skin, -0.1), 0)
            for sd in (-1, 1):
                kpoly(ctx, [(nx + sd * 2, sh_y + vd - 2), (nx + sd * 15, sh_y - 4), (nx + sd * 26, sh_y - 2),
                            (nx + sd * 20, sh_y + 14)], shade(col, 0.10), KW * 0.8)
            y_end = bot - 6 if style == "shirt" else sh_y + 44
            kline(ctx, [(nx, sh_y + vd), (nx, y_end)], 1.8, dark)
            k = sh_y + vd + 10
            while k < y_end - 4:
                kell(ctx, nx + 4, k, 2.6, 2.6, shade(col, 0.35), 1.0)
                k += 22
            if style == "shirt":  # chest pocket
                px = nx + (-1 if F.s >= 0 else 1) * w * 0.45
                kpoly(ctx, [(px - 12, sh_y + 40), (px + 12, sh_y + 40), (px + 12, sh_y + 62), (px, sh_y + 66),
                            (px - 12, sh_y + 62)], None, 1.6)
        elif style == "blouse":
            kcurve(ctx, (nx - 20, sh_y + 2), (nx, sh_y + 24), (nx + 20, sh_y + 2), 2.0, dark)
        elif style == "longsleeve":
            kcurve(ctx, (nx - 16, sh_y + 1), (nx, sh_y + 15), (nx + 16, sh_y + 1), 3.0, dark)
    else:
        kcurve(ctx, (-w * 0.5, sh_y + 2), (0, sh_y + 8), (w * 0.5, sh_y + 2), 2.2, shade(col, -0.3))
    if top.get("print"):
        pc = top["print"]
        px = F.x(0, 20)
        kell(ctx, px, (sh_y + bot) / 2 - 6, 16, 14, pc, 1.4)


def draw_vest_k(ctx, rig, b, F, col):
    female = is_female(rig)
    sh_y = b["sh"]
    bot = b["hip"] + 24
    w = b["sw"] * (0.72 + 0.28 * abs(F.c)) / 2
    cel(ctx, lambda: torso_path_k(ctx, b, F, sh_y - 6, bot, female, bulge=1.15), col, shade(col, -0.16), w * 0.38,
        (0, sh_y - 60, w * 2, bot - sh_y + 120))
    if F.c > 0.1:
        nx = F.x(0, 16)
        kline(ctx, [(nx, sh_y + 4), (nx, bot - 4)], 2.4, shade(col, -0.45))
        for k in (0.38, 0.72):
            yy = sh_y + (bot - sh_y) * k
            kline(ctx, [(nx - w * 0.95, yy), (nx + w * 0.95, yy)], 6, "#2a2a30")
            rrect(ctx, nx - 9, yy - 7, 18, 14, 3, "#e9e9ee", 1.4)
    kcurve(ctx, (-w * 0.8, sh_y - 2), (0, sh_y + 16), (w * 0.8, sh_y - 2), 8, shade(col, -0.12))


def _sleeve(style):
    return {"tshirt": 0.40, "polo": 0.40, "shirt": 0.44, "shortsleeve": 0.42, "longsleeve": 0.96, "blouse": 0.96,
            "none": 0.0}.get(style, 0.40)


# finger table: index, middle, ring, pinky -> (extended?, spread angle, length factor)
GESTURES = {
    "open":      dict(f=[(1, -0.10, 1.0), (1, -0.03, 1.08), (1, 0.04, 1.0), (1, 0.12, 0.82)], thumb=("out", 0.85)),
    "wave":      dict(f=[(1, -0.36, 1.0), (1, -0.12, 1.08), (1, 0.12, 1.0), (1, 0.36, 0.82)], thumb=("out", 1.15)),
    "relaxed":   dict(f=[(2, -0.06, 0.9), (2, -0.02, 0.98), (2, 0.03, 0.9), (2, 0.08, 0.76)], thumb=("out", 0.45)),
    "point":     dict(f=[(1, -0.04, 1.08), (0, 0, 0), (0, 0, 0), (0, 0, 0)], thumb=("fold", 0.0)),
    "peace":     dict(f=[(1, -0.26, 1.05), (1, 0.16, 1.1), (0, 0, 0), (0, 0, 0)], thumb=("fold", 0.0)),
    "thumbs_up": dict(f=[(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)], thumb=("up", 0.0)),
    "fist":      dict(f=[(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)], thumb=("fold", 0.0)),
    "ok":        dict(f=[(3, 0, 0), (1, -0.05, 1.05), (1, 0.08, 0.98), (1, 0.2, 0.82)], thumb=("ring", 0.0)),
    "grab":      dict(f=[(4, -0.06, 0.9), (4, -0.02, 0.98), (4, 0.03, 0.9), (4, 0.08, 0.76)], thumb=("out", 0.35)),
    "rock":      dict(f=[(1, -0.14, 1.05), (0, 0, 0), (0, 0, 0), (1, 0.22, 0.9)], thumb=("fold", 0.0)),
    "three":     dict(f=[(1, -0.22, 1.05), (1, -0.02, 1.1), (1, 0.18, 1.0), (0, 0, 0)], thumb=("fold", 0.0)),
    "call":      dict(f=[(0, 0, 0), (0, 0, 0), (0, 0, 0), (1, 0.45, 0.95)], thumb=("out", 1.25)),
    "pinch":     dict(f=[(3, 0, 0), (2, 0.0, 0.8), (2, 0.05, 0.75), (2, 0.1, 0.62)], thumb=("ring", 0.0)),
}


def draw_hand_gesture(ctx, wx, wy, ang, gesture, skin, size, flip=1, ol=KW):
    """Hand with fingers. (wx, wy) wrist, ang = direction wrist -> fingertips, flip = thumb side (+1 / -1)."""
    g = GESTURES.get(gesture, GESTURES["relaxed"])
    sz = size
    ctx.save()
    ctx.translate(wx, wy)
    ctx.rotate(ang)
    ctx.scale(1, flip)
    fw = sz * 0.165
    bases = [(sz * 0.74, -sz * 0.235), (sz * 0.78, -sz * 0.08), (sz * 0.76, sz * 0.075), (sz * 0.70, sz * 0.22)]
    lens = [0.56, 0.62, 0.57, 0.46]
    strokes = []  # (points, width)
    for (kind, a, lf), (bx, by), ln in zip(g["f"], bases, lens):
        L = sz * ln * lf
        if kind == 1:  # straight
            strokes.append(([(bx, by), (bx + math.cos(a) * L, by + math.sin(a) * L)], fw))
        elif kind == 2:  # relaxed: slight curl
            m = (bx + math.cos(a) * L * 0.55, by + math.sin(a) * L * 0.55)
            strokes.append(([(bx, by), m, (m[0] + math.cos(a + 0.55) * L * 0.42, m[1] + math.sin(a + 0.55) * L * 0.42)], fw))
        elif kind == 4:  # grab: strong curl (C shape)
            m = (bx + math.cos(a) * L * 0.45, by + math.sin(a) * L * 0.45)
            strokes.append(([(bx, by), m, (m[0] + math.cos(a + 1.5) * L * 0.4, m[1] + math.sin(a + 1.5) * L * 0.4)], fw))
        elif kind in (0, 3):  # curled into the palm: knuckle bump
            strokes.append(([(bx - sz * 0.02, by), (bx + sz * 0.08, by + sz * 0.02)], fw * 1.15))
    # outline pass (palm + fingers), then fill pass: fingers merge into one smooth silhouette
    for pts, w in strokes:
        kline(ctx, pts, w + 2 * ol, KO)
    kell(ctx, sz * 0.40, 0, sz * 0.42, sz * 0.34, None, ol * 2)
    for pts, w in strokes:
        kline(ctx, pts, w, skin)
    kell(ctx, sz * 0.40, 0, sz * 0.42, sz * 0.34, skin, 0)
    # creases between neighbouring extended fingers
    ext = [k for k, f in enumerate(g["f"]) if f[0] in (1, 2, 4)]
    for k in ext:
        if k + 1 in ext and abs(g["f"][k + 1][1] - g["f"][k][1]) < 0.2:
            (b0x, b0y), (b1x, b1y) = bases[k], bases[k + 1]
            a = (g["f"][k][1] + g["f"][k + 1][1]) / 2
            L = sz * min(lens[k], lens[k + 1]) * 0.55
            mx, my = (b0x + b1x) / 2, (b0y + b1y) / 2
            kline(ctx, [(mx - sz * 0.04, my), (mx + math.cos(a) * L, my + math.sin(a) * L)], ol * 0.55, KO)
    if all(f[0] in (0, 3) for f in g["f"]):  # fist: knuckle lines
        for (bx, by) in bases[:3]:
            kline(ctx, [(bx - sz * 0.05, by + sz * 0.075), (bx + sz * 0.02, by + sz * 0.075)], ol * 0.5, KO)
    # thumb
    tk, ta = g["thumb"]
    tb = (sz * 0.30, -sz * 0.27)
    if tk == "out":
        tip = (tb[0] + math.cos(-ta) * sz * 0.36, tb[1] + math.sin(-ta) * sz * 0.36)
        pts = [tb, ((tb[0] + tip[0]) / 2 + sz * 0.02, (tb[1] + tip[1]) / 2), tip]
    elif tk == "up":
        pts = [tb, (tb[0] + sz * 0.02, tb[1] - sz * 0.22), (tb[0] + sz * 0.0, tb[1] - sz * 0.40)]
    elif tk == "ring":  # thumb tip meets the index tip: ok sign
        pts = [tb, (sz * 0.62, -sz * 0.36), (sz * 0.80, -sz * 0.30)]
    else:  # folded across the palm
        pts = [tb, (sz * 0.52, -sz * 0.16), (sz * 0.66, -sz * 0.06)]
    kline(ctx, pts, sz * 0.21 + 2 * ol, KO)
    kline(ctx, pts, sz * 0.21, skin)
    if tk == "ring":
        ctx.new_path()
        ctx.arc(sz * 0.80, -sz * 0.38, sz * 0.10, 0, 2 * math.pi)
        src(ctx, KO)
        ctx.set_line_width(ol)
        ctx.stroke()
    ctx.restore()


def hand_gesture_for(hold, pose, role):
    if hold == "pockets":
        return "hidden"
    if pose in ("wave", "wave_hip") and role == "near":
        return "wave"
    if hold == "point" and role == "near":
        return "point"
    if hold == "open" and role == "near":
        return "open"
    if pose in ("thumbs_up",) and role == "near":
        return "thumbs_up"
    if pose == "peace" and role == "near":
        return "peace"
    if hold in ("fist",) or pose in ("hips", "hip_one", "wave_hip", "angry", "cheer"):
        if pose == "hip_one" and role == "near":
            return "relaxed"
        if pose == "wave_hip" and role == "near":
            return "wave"
        return "fist"
    if hold in ("sampeah", "give", "dance"):
        return "open"
    if hold in ("carry", "cup", "smoothie", "phone", "selfie", "eat", "suitcase", "flashlight", "photo", "staff",
                "bowl", "flag", "rope", "hip", "shoulder", "backpack", "carve", "lamp", "incense", "plan", "rod",
                "powder", "puff"):
        return "grab"
    return "relaxed"


def draw_hand(ctx, hd, el, b, skin, gesture="relaxed", flip=1, pocket_col=None):
    ang = math.atan2(hd[1] - el[1], hd[0] - el[0])
    if gesture == "hidden":  # hand slipped under the shirt hem into the pocket
        kell(ctx, hd[0], hd[1] - b["aw"] * 0.05, b["aw"] * 0.50, b["aw"] * 0.40, pocket_col or "#3b4a6b", 0)
        kline(ctx, [(hd[0] - b["aw"] * 0.52, hd[1] + b["aw"] * 0.30), (hd[0] + b["aw"] * 0.52, hd[1] + b["aw"] * 0.30)],
              KW)
        return
    wx, wy = hd[0] - math.cos(ang) * b["aw"] * 0.15, hd[1] - math.sin(ang) * b["aw"] * 0.15
    draw_hand_gesture(ctx, wx, wy, ang, gesture, skin, b["aw"] * 1.30, flip, KW * 0.85)


def arm_curve(sh, el, hd, r):
    """Shoulder -> elbow -> hand polyline with the elbow corner rounded off (fillet of radius ~r)."""
    l1 = math.hypot(el[0] - sh[0], el[1] - sh[1])
    l2 = math.hypot(hd[0] - el[0], hd[1] - el[1])
    if l1 < 1e-3 or l2 < 1e-3:
        return [sh, el, hd]
    r = min(r, l1 * 0.45, l2 * 0.45)
    p1 = (el[0] - (el[0] - sh[0]) / l1 * r, el[1] - (el[1] - sh[1]) / l1 * r)
    p2 = (el[0] + (hd[0] - el[0]) / l2 * r, el[1] + (hd[1] - el[1]) / l2 * r)
    pts = [sh]
    for i in range(9):
        u = i / 8
        pts.append(((1 - u) ** 2 * p1[0] + 2 * u * (1 - u) * el[0] + u * u * p2[0],
                    (1 - u) ** 2 * p1[1] + 2 * u * (1 - u) * el[1] + u * u * p2[1]))
    pts.append(hd)
    return pts


def draw_arm_k(ctx, rig, b, arm, F, skin, gesture="relaxed"):
    top = rig["top"]
    sh, el, hd = arm["sh"], arm["el"], arm["hand"]
    pts = arm_curve(sh, el, hd, b["aw"] * 1.1)
    klimb(ctx, pts, b["aw"] * 0.80, skin)
    frac = _sleeve(top.get("style"))
    if frac > 0:
        sl = RG._point_along(pts, frac)
        sc = top.get("sleeve_color") or top.get("color")
        klimb(ctx, sl, b["aw"] * 1.02, sc)
        a, e = sl[-2], sl[-1]
        ang = math.atan2(e[1] - a[1], e[0] - a[0])
        nx, ny = -math.sin(ang), math.cos(ang)
        hw = b["aw"] * 0.51
        kline(ctx, [(e[0] - nx * hw, e[1] - ny * hw), (e[0] + nx * hw, e[1] + ny * hw)], 1.8, shade(sc, -0.35))
    if "bracelets" in rig.get("jewelry", []):
        k = 0.86
        wx, wy = lerp(el[0], hd[0], k), lerp(el[1], hd[1], k)
        kell(ctx, wx, wy, b["aw"] * 0.4, b["aw"] * 0.18, RG.GOLD, 1.2, rot=math.atan2(hd[1] - el[1], hd[0] - el[0]) + 1.57)
    flip = -arm["L"] * (1 if F.c >= 0 else -1)
    draw_hand(ctx, hd, pts[-3], b, skin, gesture, flip, rig["top"].get("color"))


def draw_shoe(ctx, rig, ank, F, b):
    fw_ = rig.get("footwear") or {"type": "sneakers", "color": "#ffffff"}
    kind = fw_.get("type", "sneakers")
    col = fw_.get("color", "#ffffff")
    lw = b["lw"]
    ln = lw * (0.46 + 0.34 * abs(F.s))
    fx = ank[0] + F.s * lw * 0.32
    fy = ank[1] + 6
    if kind == "sandals":
        kell(ctx, fx, fy + 4, ln + 3, lw * 0.13, "#6b4a32", KW * 0.8)
        kell(ctx, fx, fy - 2, ln - 2, lw * 0.16, skin_of(rig), KW * 0.8)
        kline(ctx, [(fx - ln * 0.4, fy - 4), (fx + ln * 0.2, fy - 6)], 3.0, "#6b4a32")
        return
    h = lw * (0.40 if kind == "clogs" else 0.34)
    ctx.new_path()
    ctx.move_to(fx - ln, fy + h * 0.45)
    ctx.curve_to(fx - ln * 1.02, fy - h * 0.6, fx - ln * 0.2, fy - h * 0.95, fx + ln * 0.25 * F.s, fy - h * 0.85)
    ctx.curve_to(fx + ln * 0.9, fy - h * 0.7, fx + ln * 1.08, fy + h * 0.1, fx + ln, fy + h * 0.45)
    ctx.close_path()
    _fs(ctx, col, KW * 0.9)
    sole = shade(col, -0.25) if kind == "clogs" else "#d9d4cc"
    kline(ctx, [(fx - ln * 0.98, fy + h * 0.38), (fx + ln * 0.98, fy + h * 0.38)], h * 0.22, sole)
    if kind == "clogs":
        for k in (-0.35, 0.0, 0.35):
            kell(ctx, fx + ln * k + F.s * ln * 0.25, fy - h * 0.35, h * 0.08, h * 0.08, shade(col, -0.3), 0)
    else:
        acc = fw_.get("accent", "#3b7fd1")
        kline(ctx, [(fx - ln * 0.2, fy - h * 0.1), (fx + ln * 0.4 * (1 if F.s >= 0 else -1), fy - h * 0.45)], 3.0, acc)


def draw_leg_k(ctx, rig, b, lg, F, skin):
    bottom = rig["bottom"]
    bst = bottom.get("style", "shorts")
    hip, knee, ank = lg["hip"], lg["knee"], lg["ankle"]
    klimb(ctx, [hip, knee, ank], b["lw"] * 0.50, skin)
    if bst in ("shorts", "longpants", "pants", "chang_kben"):
        frac = {"shorts": 0.40, "longpants": 0.97, "pants": 0.82, "chang_kben": 0.80}[bst]
        pts = RG._point_along([hip, knee, ank], frac)
        w = b["lw"] * (1.12 if bst == "shorts" else 0.98)
        col = bottom.get("color", "#3b4a6b")
        klimb(ctx, pts, w, col, cap=cairo.LINE_CAP_BUTT)
        a, e = pts[-2], pts[-1]
        ang = math.atan2(e[1] - a[1], e[0] - a[0])
        nx, ny = -math.sin(ang), math.cos(ang)
        kline(ctx, [(e[0] - nx * w * 0.55, e[1] - ny * w * 0.55), (e[0] + nx * w * 0.55, e[1] + ny * w * 0.55)], KW)
        if bst == "longpants":  # jeans seam + cuff
            kline(ctx, RG._point_along([hip, knee, ank], 0.92), 1.4, shade(col, 0.25), 0.7)
            kline(ctx, [(e[0] - nx * w * 0.5, e[1] - ny * w * 0.5 - 7), (e[0] + nx * w * 0.5, e[1] + ny * w * 0.5 - 7)],
                  1.6, shade(col, -0.3))
    draw_shoe(ctx, rig, ank, F, b)


def draw_lower_garment(ctx, rig, b, F, legs_state):
    """Waistband (shorts/pants) or skirt over the top of the legs."""
    bottom = rig["bottom"]
    bst = bottom.get("style", "shorts")
    col = bottom.get("color", "#3b4a6b")
    w = b["sw"] * (0.72 + 0.28 * abs(F.c)) / 2 * (0.92 if is_female(rig) else 0.97)
    if bst in ("skirt", "sampot", "long_sampot"):
        y0 = b["wa"] + 6
        y1 = -40 if bst != "skirt" else b["hip"] * 0.45
        spread = 1.35 if bst == "skirt" else 1.2
        sw_ = sum(l["fwd"] for l in legs_state) * 0.12 if legs_state else 0

        def path():
            ctx.new_path()
            ctx.move_to(-w * 0.98, y0)
            ctx.line_to(w * 0.98, y0)
            ctx.curve_to(w * 1.05, (y0 + y1) / 2, w * spread + sw_, y1 - 10, w * spread + sw_, y1)
            ctx.curve_to(w * 0.5, y1 + 8, -w * 0.5, y1 + 8, -w * spread + sw_, y1)
            ctx.curve_to(-w * spread + sw_, y1 - 10, -w * 1.05, (y0 + y1) / 2, -w * 0.98, y0)
            ctx.close_path()
        cel(ctx, path, col, shade(col, -0.14), w * 0.4, (0, y0 - 20, w * 3, y1 - y0 + 60))
        for k in (-0.4, 0.15):
            kcurve(ctx, (w * k, y0 + 14), (w * (k * 1.2), (y0 + y1) / 2), (w * k * 1.35 + sw_, y1 - 6), 1.6,
                   shade(col, -0.3), 0.7)
        hem = bottom.get("hem")
        if hem:
            kcurve(ctx, (-w * spread + sw_, y1 - 4), (0, y1 + 6), (w * spread + sw_, y1 - 4), 5, hem)
    elif bst in ("shorts", "longpants", "pants", "chang_kben"):
        y0 = b["wa"] + 4
        y1 = b["hip"] + 26
        kpoly(ctx, [(-w * 0.98, y0), (w * 0.98, y0), (w * 1.0, y1), (-w * 1.0, y1)], col, KW)
        kline(ctx, [(F.x(0, 12), y1 - 6), (F.x(0, 12), y1 + 10)], 1.6, shade(col, -0.35))


# --------------------------------------------------------------------------- main

def draw_character(ctx, character, st, x, y, scale, alpha=1.0):
    rig = character["_rig"] if "_rig" in character else RG.merge_rig(character.get("rig"))
    b = build_of(rig)
    skin = skin_of(rig)
    theta = st.get("theta", 30.0)
    F = RG.Frame(theta)
    t = st.get("t", 0.0)
    legs = st.get("legs", "stand")
    P = RG.resolve_pose(rig, b, st)

    ctx.save()
    if alpha < 1.0:
        ctx.push_group()
    ctx.translate(x, y)
    ctx.scale(scale, scale)
    ctx.new_path()
    ellipse_path(ctx, 0, 0, b["sw"] * 0.72, 12)
    ctx.set_source_rgba(0.25, 0.15, 0.05, 0.14)
    ctx.fill()

    breathe = math.sin(t * 2.1 + zlib.crc32(character.get("character_id", "").encode()) % 7) * 1.4
    bob = 0.0
    if legs in ("walk", "run"):
        bob = -abs(math.sin(st.get("phase", 0.0))) * (5 if legs == "walk" else 10)
    shake = P.get("shake", 0.0)
    ctx.translate(math.sin(t * 40) * shake, 0)

    llen = -b["hip"] - 14
    l1, l2 = llen * 0.52, llen * 0.50
    if legs == "chair":  # sitting on a chair / bench: thighs forward, shins down
        drop = -b["hip"] - (l2 + 14)
        ctx.translate(0, drop)
        st_legs = []
        for i, L in enumerate((-1, 1)):
            lat = L * b["sw"] * 0.2
            hx = F.x(lat, 0)
            kx = hx + F.s * l1 * 0.95
            ky = b["hip"] + 4 + l1 * 0.22 * abs(F.c)
            st_legs.append(dict(hip=(hx, b["hip"]), knee=(kx, ky), ankle=(kx + F.s * 4, ky + l2 - 4 - l1 * 0.22 * abs(F.c)),
                                depth=F.depth(lat, l1), lat=lat, fwd=l1))
        for lg in sorted(st_legs, key=lambda l: l["depth"]):
            draw_leg_k(ctx, rig, b, lg, F, skin)
        draw_lower_garment(ctx, rig, b, F, [])
    elif legs in ("sit", "kneel"):
        sd = (-b["hip"] - 26) if legs == "sit" else (-b["hip"]) * 0.45
        ctx.translate(0, sd)
        bc = rig["bottom"].get("color", "#3b4a6b")
        kell(ctx, F.s * 10, b["hip"] + 4, b["sw"] * 0.8, 28, bc)
        if legs == "sit":
            for side in (-1, 1):
                draw_shoe(ctx, rig, (side * b["sw"] * 0.5 + F.s * 14, b["hip"] + 10), F, b)
    else:
        legs_state = RG._leg_state(b, legs, st.get("phase", 0.0), F, 0)
        for lg in sorted(legs_state, key=lambda l: l["depth"]):
            draw_leg_k(ctx, rig, b, lg, F, skin)
        draw_lower_garment(ctx, rig, b, F, legs_state)

    lean = P.get("lean", 0.0) + b.get("stoop", 0) + (8 if legs == "run" else 0)
    ctx.save()
    ctx.translate(0, b["hip"] + bob - P.get("bounce", 0.0))
    ctx.rotate(math.radians(lean) * F.s)
    squash = 1 - (1 - math.cos(math.radians(lean))) * abs(F.c)
    ctx.scale(1, squash * (1 + breathe * 0.002))
    ctx.translate(0, -b["hip"])

    arms = []
    near_L = 1 if F.s > 0.05 else (-1 if F.s < -0.05 else 1)
    phase = st.get("phase", 0.0)
    for role, L in (("near", near_L), ("far", -near_L)):
        lat_out, fwd, dy = P[role]
        if legs in ("walk", "run") and st.get("pose", "stand") in ("stand", "walk", "run", "idle"):
            amp = 26 if legs == "walk" else 46
            sgn = 1 if role == "near" else -1
            fwd = fwd + amp * math.sin(phase) * sgn
            dy = dy - abs(math.sin(phase)) * (6 if legs == "walk" else 18)
            if legs == "run":
                dy -= 30
        lat = L * (b["sw"] / 2 + lat_out)
        shx = F.x(L * b["sw"] / 2 * 0.97, 0)
        shy = b["sh"] + b["aw"] * 0.45
        tx, ty = F.x(lat, fwd), shy + dy
        pref = (-F.s * 0.8 + L * F.c * 0.35 + 0.0001, 0.6)
        el, hd = ik2(shx, shy, tx, ty, b["a1"], b["a2"], pref)
        sh_depth = F.depth(L * b["sw"] / 2, 0)
        hd_depth = F.depth(lat, fwd)
        front = (sh_depth * 0.5 + hd_depth) > -b["sw"] * 0.18 or (abs(F.s) < 0.62 and F.c > 0)
        arms.append(dict(role=role, sh=(shx, shy), el=el, hand=hd, front=front, L=L))
    near, far = arms
    prop = st.get("prop", rig.get("prop"))
    carry = st.get("carry")
    hold = P.get("hold")
    pose_name = st.get("pose", "stand")

    R = b["R"]
    hx = F.x(0, 4) + P.get("head_tilt", 0) * 0.3
    hy = head_y(b) + P.get("head_dy", 0) + breathe * 0.4 + st.get("nod", 0.0)
    phi = theta + st.get("head_turn", 0)

    draw_hair_back_k(ctx, rig, hx, hy, R, phi, b["sh"])
    for a in arms:
        if not a["front"]:
            draw_arm_k(ctx, rig, b, a, F, skin, hand_gesture_for(hold, pose_name, a["role"]))
    if prop in ("cane", "spear", "hoe"):
        RG.draw_prop(ctx, prop, near["hand"], far["hand"], F, b, t, "back")
    RG.draw_pose_prop(ctx, hold, near["hand"], far["hand"], F, b, t, "back")
    # neck
    nx = F.x(0, 6)
    klimb(ctx, [(nx, hy + R * 0.6), (nx, b["sh"] + 8)], R * 0.40, shade(skin, -0.08), cap=cairo.LINE_CAP_BUTT)
    draw_torso_k(ctx, rig, b, F, skin)
    if st.get("vest"):
        draw_vest_k(ctx, rig, b, F, st["vest"])
    if rig.get("scarf"):
        RG.draw_scarf(ctx, rig, b, F, b["sw"] / 2, t)
    for a in arms:
        if a["front"]:
            draw_arm_k(ctx, rig, b, a, F, skin, hand_gesture_for(hold, pose_name, a["role"]))
    if prop and prop not in ("cane", "spear", "hoe"):
        RG.draw_prop(ctx, prop, near["hand"], far["hand"], F, b, t, "front")
    if carry:
        RG.draw_prop(ctx, carry, near["hand"], far["hand"], F, b, t, "front")
    RG.draw_pose_prop(ctx, hold, near["hand"], far["hand"], F, b, t, "front")

    ctx.save()
    ctx.translate(hx, hy + R)
    ctx.rotate(math.radians(P.get("head_tilt", 0) + math.sin(t * 0.9) * 1.2))
    ctx.translate(-hx, -(hy + R))
    draw_head_k(ctx, rig, hx, hy, R, phi, st, skin)
    ctx.restore()
    RG.draw_pose_prop(ctx, hold, near["hand"], far["hand"], F, b, t, "over_head")
    if st.get("powder_dt") is not None:
        draw_poof(ctx, hx, hy, R, st["powder_dt"])
    ctx.restore()

    if alpha < 1.0:
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(alpha)
    ctx.restore()


def draw_head_only(ctx, rig, cx, cy, R, phi, st):
    """A floating head for model sheets: back hair clipped to shoulder length."""
    ctx.save()
    ctx.new_path()
    ellipse_path(ctx, cx, cy - R * 0.25, R * 1.6, R * 1.38)
    ctx.clip()
    draw_hair_back_k(ctx, rig, cx, cy, R, phi, 0)
    ctx.restore()
    draw_head_k(ctx, rig, cx, cy, R, phi, st, skin_of(rig))
