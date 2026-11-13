"""Environment pack: bg_heritage (registered into backgrounds.ENVIRONMENTS). See module docstring of bg_trip.py for the layer contract.

Siem Reap heritage sites for the 2-day trip film (flat cartoon, sandstone + laterite, no text, no people):
  palilay      Preah Palilay: one ruined prasat on a stepped laterite base in tall dipterocarp forest (morning/day)
  preah_khan   bg {"view": "corridor"} enfilade of receding doorways (default) | "roots" giant tree over a gallery wall
  srah_srang   landing terrace (naga balustrade, two lions, steps) over the calm reservoir
  west_baray   bg {"view": "boat"} long boat (hull in OVER) | "mebon" island temple, cast on a jetty |
               "bank" embankment with low sun + golden path (sunset/evening/day)
               extra params: {"boat": true} seats the cast in the boat on any view; {"canopy": true} boat roof;
               {"moving": false} stops the water scrolling
  south_gate   bg {"view": "gate"} frontal gate + causeway rows | "causeway" side view along a row
               ({"side": "deva"|"asura"} picks the row for "causeway")
  bayon        bg {"view": "towers"} many face towers | "face" a big smiling face behind the cast ({"face_x": 1000})
  terraces     bg {"which": "elephants"} Terrace of the Elephants | "leper" Terrace of the Leper King
Any of them: {"birds": true} adds birds.
Static, expensive drawing is recorded once into cairo RecordingSurfaces (_cached) and replayed each frame (vector-sharp).
"""
import math

import cairocffi as cairo

import backgrounds as B
import bg_angkor as A
from drawutil import (OUTLINE, blob, circle, clamp, curve, ease_io, ellipse, ellipse_path, fill_stroke, flower, hexc,
                      lerp, lin_grad, line, mix, poly, poly_path, rad_grad, rng, rrect, shade, smooth, smooth_path,
                      src)

BOL = B.BOL

STONE = "#a89a7c"
STONE_LT = "#bfb294"
STONE_DK = "#857759"
LATERITE = "#a5603f"
LAT_DK = "#7b4630"
MOSS = "#5f7a3e"
JOINT = "#6b5f47"
VOID = "#2a2118"
BARK = "#b3a891"
ROOT = "#d6cdb9"


def extra(fn):
    """Mark an environment as drawing the extra OVER (in front of characters) / SCREEN (screen-space) layers."""
    fn.extra_layers = True
    return fn


# =========================================================================== generic helpers

_REC = {}


def _rec(key, draw):
    """Record static drawing once into a vector RecordingSurface (cached per process)."""
    rec = _REC.get(key)
    if rec is None:
        rec = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, None)
        g = cairo.Context(rec)
        draw(g)
        _REC[key] = rec
    return rec


def _cached(ctx, key, draw):
    """Record static drawing once (vector RecordingSurface) and replay it every frame."""
    rec = _rec(key, draw)
    ctx.save()
    ctx.set_source_surface(rec, 0, 0)
    ctx.paint()
    ctx.restore()
    return rec


def _raster(ctx, key, draw, x0, y0, w, h, k=1.5):
    """Bake very heavy static drawing (grouped reliefs) into an image at k x resolution and blit it each frame."""
    img = _REC.get(key)
    if img is None:
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w * k), int(h * k))
        g = cairo.Context(img)
        g.scale(k, k)
        g.translate(-x0, -y0)
        draw(g)
        _REC[key] = img
    ctx.save()
    ctx.translate(x0, y0)
    ctx.scale(1.0 / k, 1.0 / k)
    ctx.set_source_surface(img, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint()
    ctx.restore()


def _param(name, default):
    v = B.CUR.get(name)
    return default if v is None else v


def _night(tod):
    return tod == "night"


def _warm(tod):
    return tod in ("sunset", "evening", "sunrise")


def _sky(ctx, t, tod, hz, clouds=True, sun=None, sun_r=58, ncloud=7, glow=220):
    p = B.TOD.get(tod, B.TOD["day"])
    ctx.new_path()
    ctx.rectangle(B.X0, -300, B.X1 - B.X0, hz + 520)
    ctx.set_source(lin_grad(0, -100, 0, hz + 40, [(0, p["sky"][0]), (1, p["sky"][1])]))
    ctx.fill()
    if tod == "night":
        r = rng(99)
        ctx.new_path()
        for _ in range(120):
            x, y = r.uniform(B.X0, B.X1), r.uniform(-150, hz - 120)
            ctx.new_sub_path()
            ctx.arc(x, y, r.uniform(1.0, 2.2), 0, 2 * math.pi)
        src(ctx, "#fffbe6", 0.85)
        ctx.fill()
        circle(ctx, 1500, 150, 52, "#fdf6d8", 0)
        circle(ctx, 1522, 138, 46, p["sky"][0], 0)
    if p.get("sun"):
        sx, sy, sc = p["sun"]
        x, y = sun if sun else (B.X0 + (B.X1 - B.X0) * sx, hz * sy)
        ctx.new_path()
        ctx.arc(x, y, glow, 0, 2 * math.pi)
        ctx.set_source(rad_grad(x, y, sun_r * 0.6, glow, [(0, hexc(sc) + (0.55,)), (1, hexc(sc) + (0.0,))]))
        ctx.fill()
        circle(ctx, x, y, sun_r, sc, 0)
    if clouds and tod != "night":
        r = rng(7)
        for i in range(ncloud):
            cx = (r.uniform(B.X0, B.X1) + t * r.uniform(4, 10)) % (B.X1 - B.X0) + B.X0
            cy = r.uniform(60, hz * 0.55)
            B.cloud(ctx, cx, cy, r.uniform(0.6, 1.25), tod)


def _maybe_birds(ctx, t, tod, **kw):
    if B.CUR.get("birds"):
        A.birds(ctx, t, col="#2b2530" if tod != "night" else "#0b0b12", **kw)


def _spline(pts, n=8):
    out = []
    m = len(pts)
    for i in range(m - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, m - 1)]
        for k in range(n):
            u = k / n
            u2, u3 = u * u, u * u * u
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u3) for j in (0, 1)))
    out.append(tuple(pts[-1]))
    return out


def _tube(ctx, pts, widths, fill, ol=BOL):
    """Outlined ribbon along a polyline with a width per point (roots, naga bodies, trunks)."""
    n = len(pts)
    L, R = [], []
    for i in range(n):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / d, dx / d
        w = widths[i] / 2
        L.append((pts[i][0] + nx * w, pts[i][1] + ny * w))
        R.append((pts[i][0] - nx * w, pts[i][1] - ny * w))
    poly(ctx, L + R[::-1], fill, ol)
    return L, R


def _taper(ctx, pts, w0, w1, fill, ol=BOL, n=8, hi=None):
    sp = _spline(pts, n)
    k = len(sp) - 1
    ws = [w0 + (w1 - w0) * (i / k) for i in range(k + 1)]
    L, R = _tube(ctx, sp, ws, fill, ol)
    if hi:  # light ridge along one side
        line(ctx, [((l[0] * 0.7 + c[0] * 0.3), (l[1] * 0.7 + c[1] * 0.3)) for l, c in zip(L, sp)][1:-2],
             max(1.5, (w0 + w1) * 0.08), hi, 0.8)
    return sp


def _taper_poly(pts, w0, w1, n=8):
    """Spline through pts and the outline polygon of a tapered ribbon along it (for _union)."""
    sp = _spline(pts, n)
    k = len(sp) - 1
    L, R = [], []
    for i, (x, y) in enumerate(sp):
        a, b = sp[max(i - 1, 0)], sp[min(i + 1, k)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / d, dx / d
        w = (w0 + (w1 - w0) * i / k) / 2
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    return sp, L + R[::-1], L, R


def _union(ctx, shapes, fill, ol=BOL, shadow=None):
    """Draw several overlapping shapes as one outlined mass: shapes are point lists ("poly") or
    ("smooth", pts). Outline everything first at double width, then fill everything (internal edges vanish)."""
    def path(sh):
        ctx.new_path()
        if isinstance(sh, tuple) and sh[0] == "smooth":
            smooth_path(ctx, sh[1])
        else:
            poly_path(ctx, sh)
    if shadow:
        ctx.save()
        ctx.translate(shadow[0], shadow[1])
        for sh in shapes:
            path(sh)
            ctx.set_source_rgba(0.16, 0.11, 0.06, shadow[2])
            ctx.fill()
        ctx.restore()
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for sh in shapes:
        path(sh)
        src(ctx, OUTLINE)
        ctx.set_line_width(ol * 2)
        ctx.stroke()
    for sh in shapes:
        path(sh)
        if isinstance(fill, cairo.Pattern):
            ctx.set_source(fill)
        else:
            src(ctx, fill)
        ctx.fill()


def _courses(ctx, x0, y0, x1, y1, ch, seed, col=JOINT, lw=1.4, jmin=40, jmax=120, a=0.7):
    """Stone coursing: horizontal joints every ch plus staggered vertical joints (one stroke)."""
    r = rng(seed)
    ctx.new_path()
    y = y0
    while y < y1 - 1:
        ctx.move_to(x0, y)
        ctx.line_to(x1, y)
        yy = min(y + ch, y1)
        x = x0 + r.uniform(0, jmax)
        while x < x1:
            ctx.move_to(x, y)
            ctx.line_to(x, yy)
            x += r.uniform(jmin, jmax)
        y += ch
    src(ctx, col, a)
    ctx.set_line_width(lw)
    ctx.stroke()


def _spots(ctx, x0, y0, x1, y1, n, seed, col, a, rmin=4, rmax=18, flat=0.6):
    r = rng(seed)
    ctx.new_path()
    for _ in range(n):
        rr = r.uniform(rmin, rmax)
        ellipse_path(ctx, r.uniform(x0, x1), r.uniform(y0, y1), rr, rr * flat, r.uniform(0, 3))
    src(ctx, col, a)
    ctx.fill()


def _weather(ctx, x0, y0, x1, y1, seed, dens=1.0, moss=True):
    """Lichen, stains and moss on stone (call while clipped to the stone shape)."""
    area = max(1.0, (x1 - x0) * (y1 - y0)) / 10000.0
    _spots(ctx, x0, y0, x1, y1, int(area * 1.6 * dens), seed, "#3d3a2c", 0.13, 6, 26)
    _spots(ctx, x0, y0, x1, y1, int(area * 1.2 * dens), seed + 1, "#efe6cc", 0.14, 4, 16)
    if moss:
        _spots(ctx, x0, y0, x1, y1, int(area * 0.8 * dens), seed + 2, MOSS, 0.32, 5, 22)


def _pores(ctx, x0, y0, x1, y1, seed, dens=1.0, col=LAT_DK):
    area = max(1.0, (x1 - x0) * (y1 - y0)) / 1000.0
    _spots(ctx, x0, y0, x1, y1, int(area * 1.4 * dens), seed, col, 0.55, 1.2, 3.2, 0.8)


def _clip_rect(ctx, x, y, w, h):
    ctx.save()
    ctx.new_path()
    ctx.rectangle(x, y, w, h)
    ctx.clip()


def _stone_rect(ctx, x, y, w, h, col=STONE, seed=0, ch=26, ol=BOL, weather=1.0, joints=True, lat=False):
    rrect(ctx, x, y, w, h, 2, col, ol)
    _clip_rect(ctx, x, y, w, h)
    if joints:
        _courses(ctx, x, y + ch, x + w, y + h, ch, seed, shade(col, -0.35), 1.3, ch * 1.6, ch * 4.2, 0.6)
    if lat:
        _pores(ctx, x, y, x + w, y + h, seed + 3)
    if weather:
        _weather(ctx, x, y, x + w, y + h, seed + 7, weather)
    ctx.restore()
    line(ctx, [(x + 3, y + 2.5), (x + w - 3, y + 2.5)], 2.5, shade(col, 0.22), 0.9)


def _shade_right(ctx, x, y, w, h, a=0.12):
    ctx.new_path()
    ctx.rectangle(x, y, w, h)
    ctx.set_source_rgba(0.08, 0.05, 0.02, a)
    ctx.fill()


def _clump(ctx, x, y, rad, col, seed, ol=2.0, hi=0.16, n=6):
    r = rng(seed)
    cs = [(x + r.uniform(-0.6, 0.6) * rad, y + r.uniform(-0.35, 0.35) * rad, rad * r.uniform(0.45, 0.68))
          for _ in range(n)]
    ctx.new_path()
    for cx, cy, cr in cs:
        ctx.new_sub_path()
        ctx.arc(cx, cy, cr, 0, 2 * math.pi)
    if ol:
        src(ctx, OUTLINE)
        ctx.set_line_width(ol * 2)
        ctx.stroke_preserve()
    src(ctx, col)
    ctx.fill()
    if hi:
        ctx.new_path()
        for cx, cy, cr in cs[:3]:
            ellipse_path(ctx, cx - cr * 0.25, cy - cr * 0.3, cr * 0.5, cr * 0.32)
        src(ctx, shade(col, hi))
        ctx.fill()


def _block(ctx, x, y, w, h, rot=0.0, col=STONE, seed=0, moss=0.5, ol=BOL):
    """A loose sandstone block with a lit top and a shaded side, (x, y) = bottom centre."""
    r = rng(seed)
    d = min(w, h) * 0.32
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    poly(ctx, [(-w / 2, -h), (-w / 2 + d, -h - d * 0.55), (w / 2 + d, -h - d * 0.55), (w / 2, -h)], shade(col, 0.16), ol)
    poly(ctx, [(w / 2, -h), (w / 2 + d, -h - d * 0.55), (w / 2 + d, -d * 0.55), (w / 2, 0)], shade(col, -0.2), ol)
    rrect(ctx, -w / 2, -h, w, h, 3, col, ol)
    if moss > 0 and r.random() < moss + 0.3:
        ctx.new_path()
        ellipse_path(ctx, r.uniform(-0.2, 0.2) * w, -h - d * 0.2, w * r.uniform(0.25, 0.45), d * 0.4)
        src(ctx, MOSS, 0.75)
        ctx.fill()
    if r.random() < 0.6:  # the lifting-peg holes seen on Angkor blocks
        for hx in (-0.22, 0.22):
            circle(ctx, hx * w, -h * 0.5, max(1.5, w * 0.025), shade(col, -0.5), 0)
    ctx.restore()


def _rubble(ctx, cx, cy, n, s, seed, col=STONE, spread=1.0):
    r = rng(seed)
    items = []
    for i in range(n):
        items.append((cy + r.uniform(-30, 20) * s * spread, cx + r.uniform(-150, 150) * s * spread,
                      r.uniform(60, 120) * s, r.uniform(36, 64) * s, r.uniform(-0.35, 0.35), i))
    for yy, xx, w, h, rot, i in sorted(items):
        _block(ctx, xx, yy, w, h, rot, shade(col, r.uniform(-0.08, 0.08)), seed * 31 + i)


def _tall_trunk(ctx, x, base, w, col=BARK, top=-320, lean=0.0, seed=0, ol=BOL, buttress=True):
    """Dipterocarp trunk: tall, straight, pale, with flared buttress roots; runs out of frame at the top."""
    r = rng(seed)
    if buttress:
        for sd, k in ((-1, 1.0), (1, 0.85), (-1, 0.55), (1, 0.45)):
            fx = x + sd * w * (1.1 + 0.9 * k) * r.uniform(0.9, 1.1)
            poly(ctx, [(x + sd * w * 0.15, base - w * (1.2 + 1.3 * k)), (fx, base + 4), (x + sd * w * 0.25, base + 4)],
                 shade(col, -0.05 if sd > 0 else 0.03), ol)
    pts = [(x - w * 0.5, base + 4), (x - w * 0.36 + lean, top), (x + w * 0.36 + lean, top), (x + w * 0.5, base + 4)]
    poly(ctx, pts, col, ol)
    ctx.save()
    ctx.new_path()
    poly_path(ctx, pts)
    ctx.clip()
    ctx.new_path()
    poly_path(ctx, [(x + w * 0.12, base + 4), (x + w * 0.1 + lean, top), (x + w * 0.5 + lean, top), (x + w * 0.6, base + 4)])
    ctx.set_source_rgba(0.1, 0.07, 0.03, 0.16)
    ctx.fill()
    ctx.new_path()
    for k in range(int(6 + w / 12)):
        xx = x + r.uniform(-0.4, 0.4) * w
        y0 = r.uniform(top, base - 60)
        ctx.move_to(xx, y0)
        ctx.line_to(xx + lean * (r.uniform(40, 260) / max(1, base - top)), y0 + r.uniform(40, 260))
    src(ctx, shade(col, -0.25), 0.5)
    ctx.set_line_width(max(1.2, w * 0.03))
    ctx.stroke()
    _spots(ctx, x - w, top, x + w, base, int(w * 0.6), seed + 5, "#eef0e4", 0.35, w * 0.06, w * 0.2, 0.5)
    _spots(ctx, x - w, top, x + w, base, int(w * 0.25), seed + 6, MOSS, 0.35, w * 0.08, w * 0.25, 0.6)
    ctx.restore()


def _fern(ctx, x, y, s, t=0.0, col="#3f8a3a", seed=0, n=7):
    r = rng(seed)
    for k in range(n):
        a = -math.pi * (0.12 + 0.76 * k / max(1, n - 1)) + r.uniform(-0.08, 0.08) + math.sin(t * 0.9 + k + seed) * 0.03
        L = s * r.uniform(150, 230)
        ex, ey = x + math.cos(a) * L, y + math.sin(a) * L * 0.8
        mx, my = x + math.cos(a) * L * 0.55, y + math.sin(a) * L * 0.8 * 0.55 - L * 0.22
        pts = [(x, y), (mx, my), (ex, ey)]
        sp = _taper(ctx, pts, 20 * s, 2 * s, shade(col, -0.06 * (k % 3)), BOL * 0.7, 6)
        ctx.new_path()
        for i in range(2, len(sp) - 1):
            px, py = sp[i]
            qx, qy = sp[i - 1]
            dx, dy = px - qx, py - qy
            d = math.hypot(dx, dy) or 1
            nx, ny = -dy / d, dx / d
            ll = 16 * s * (1 - i / len(sp))
            ctx.move_to(px, py)
            ctx.line_to(px + nx * ll + dx * 0.4, py + ny * ll + dy * 0.4)
            ctx.move_to(px, py)
            ctx.line_to(px - nx * ll + dx * 0.4, py - ny * ll + dy * 0.4)
        src(ctx, shade(col, -0.3), 0.8)
        ctx.set_line_width(2.2 * s)
        ctx.stroke()


def _ground_root(ctx, pts, w0, w1=8, col=ROOT, seed=0):
    """A surface root lying on the ground: soft shadow, body, light ridge."""
    ctx.save()
    ctx.translate(4, 7)
    _taper(ctx, pts, w0 * 1.1, w1, (0.15, 0.11, 0.06), 0)
    ctx.restore()
    ctx.push_group()
    _taper(ctx, pts, w0, w1, col, BOL, hi=shade(col, 0.35))
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(1.0)


def _shafts(ctx, t, beams, col=(1.0, 0.96, 0.78)):
    for i, (x, w, a, slant) in enumerate(beams):
        k = a * (0.85 + 0.15 * math.sin(t * 0.35 + i * 1.7))
        ctx.new_path()
        poly_path(ctx, [(x, -260), (x + w, -260), (x + w * 1.6 + slant, 1120), (x + slant, 1120)])
        ctx.set_source(lin_grad(0, -260, 0, 1120, [(0, col + (k,)), (0.7, col + (k * 0.6,)), (1, col + (0.0,))]))
        ctx.fill()


def _dapple(ctx, t, y0, y1, seed, n=26, a=0.22, col=(1.0, 0.95, 0.7), x0=None, x1=None):
    r = rng(seed)
    x0 = B.X0 if x0 is None else x0
    x1 = B.X1 if x1 is None else x1
    for i in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        f = (y - y0) / max(1, y1 - y0)
        w = r.uniform(40, 110) * (0.45 + f)
        x += math.sin(t * 0.3 + i * 2.1) * 8
        k = a * (0.7 + 0.3 * math.sin(t * 0.45 + i))
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(1, 0.3)
        ctx.new_path()
        ctx.arc(0, 0, w, 0, 2 * math.pi)
        ctx.set_source(rad_grad(0, 0, 0, w, [(0, col + (k,)), (0.6, col + (k * 0.6,)), (1, col + (0.0,))]))
        ctx.fill()
        ctx.restore()


def _litter(ctx, y0, y1, n, seed, cols, x0=None, x1=None, smin=3, smax=10):
    r = rng(seed)
    x0 = B.X0 if x0 is None else x0
    x1 = B.X1 if x1 is None else x1
    groups = [[] for _ in cols]
    for _ in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        f = (y - y0) / max(1, y1 - y0)
        s = smin + (smax - smin) * f
        groups[r.randrange(len(cols))].append((x, y, s * r.uniform(0.7, 1.3), r.uniform(0, 3.1)))
    for c, items in zip(cols, groups):
        ctx.new_path()
        for x, y, s, a in items:
            ellipse_path(ctx, x, y, s, s * 0.45, a)
        src(ctx, c)
        ctx.fill()


def _tufts(ctx, y0, y1, n, seed, col="#4c7f35", x0=None, x1=None, s0=0.6, s1=1.4):
    r = rng(seed)
    x0 = B.X0 if x0 is None else x0
    x1 = B.X1 if x1 is None else x1
    ctx.new_path()
    for _ in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        s = s0 + (y - y0) / max(1, y1 - y0) * (s1 - s0)
        for k in range(-2, 3):
            ctx.move_to(x + k * 4 * s, y)
            ctx.line_to(x + k * 8 * s, y - (18 - abs(k) * 3) * s)
    src(ctx, col)
    ctx.set_line_width(2.4)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()


def _pediment(ctx, cx, base, w, h, col, ol=BOL, inner=True):
    """Khmer flame-arch pediment with curled naga ends."""
    def path(k):
        ww, hh = w * k, h * k
        ctx.new_path()
        ctx.move_to(cx - ww / 2, base)
        ctx.curve_to(cx - ww * 0.5, base - hh * 0.6, cx - ww * 0.2, base - hh * 0.82, cx, base - hh)
        ctx.curve_to(cx + ww * 0.2, base - hh * 0.82, cx + ww * 0.5, base - hh * 0.6, cx + ww / 2, base)
        ctx.close_path()
    # flame tips along the rim
    for k in range(1, 8):
        u = k / 8.0
        a = math.pi * u
        px, py = cx - math.cos(a) * w * 0.5 * (1 - 0.1 * math.sin(a)), base - math.sin(a) * h * 0.95
        poly(ctx, [(px - w * 0.03, py + h * 0.02), (px - math.cos(a) * w * 0.06, py - h * 0.12),
                   (px + w * 0.03, py + h * 0.02)], col, ol * 0.6)
    path(1.0)
    fill_stroke(ctx, col, ol)
    if inner:
        path(0.72)
        fill_stroke(ctx, shade(col, -0.16), ol * 0.6)
        circle(ctx, cx, base - h * 0.32, w * 0.07, shade(col, 0.08), ol * 0.5)
    for sd in (-1, 1):
        ex = cx + sd * w * 0.52
        circle(ctx, ex, base - h * 0.06, w * 0.055, shade(col, 0.05), ol * 0.7)
        circle(ctx, ex + sd * w * 0.012, base - h * 0.07, w * 0.02, shade(col, -0.3), 0)


def _colonnette(ctx, x, y0, y1, w, col, ol=BOL):
    rrect(ctx, x - w / 2, y0, w, y1 - y0, w * 0.2, col, ol)
    ctx.new_path()
    n = max(3, int((y1 - y0) / (w * 2.2)))
    for k in range(1, n):
        yy = y0 + (y1 - y0) * k / n
        ctx.move_to(x - w / 2, yy)
        ctx.line_to(x + w / 2, yy)
    src(ctx, shade(col, -0.35), 0.8)
    ctx.set_line_width(max(1.0, w * 0.12))
    ctx.stroke()
    line(ctx, [(x - w * 0.15, y0 + 4), (x - w * 0.15, y1 - 4)], max(1, w * 0.18), shade(col, 0.25), 0.8)


def _doorway(ctx, cx, base, ow, oh, col=STONE, ol=BOL, dark=VOID, ped=True, inner=None):
    """Khmer doorway: dark opening, sandstone frame, colonnettes, carved lintel and flame pediment."""
    fw = max(4.0, ow * 0.14)
    rrect(ctx, cx - ow / 2 - fw, base - oh - fw, ow + 2 * fw, oh + fw, 2, shade(col, 0.1), ol)
    rrect(ctx, cx - ow / 2, base - oh, ow, oh, 1, dark, ol * 0.8)
    if inner:  # light seen through the passage
        rrect(ctx, cx - ow * 0.28, base - oh * 0.72, ow * 0.56, oh * 0.72, 1, inner, 0)
    for sd in (-1, 1):
        _colonnette(ctx, cx + sd * (ow / 2 + fw * 1.55), base - oh, base, fw * 0.95, shade(col, 0.14), ol * 0.7)
    lw, lh = ow + fw * 5.2, max(6.0, oh * 0.16)
    ly = base - oh - fw - lh
    rrect(ctx, cx - lw / 2, ly, lw, lh, 2, shade(col, 0.06), ol)
    ctx.new_path()
    for k in range(9):  # carved garland band
        xx = cx - lw * 0.42 + lw * 0.84 * k / 8
        ctx.move_to(xx, ly + lh * 0.3)
        ctx.curve_to(xx + lw * 0.05, ly + lh * 0.9, xx + lw * 0.05, ly + lh * 0.9, xx + lw * 0.105, ly + lh * 0.3)
    src(ctx, shade(col, -0.35), 0.8)
    ctx.set_line_width(max(1.0, ol * 0.5))
    ctx.stroke()
    circle(ctx, cx, ly + lh * 0.5, lh * 0.32, shade(col, 0.12), ol * 0.5)
    if ped:
        _pediment(ctx, cx, ly, lw * 0.9, oh * 0.5, col, ol)
    return ly


def _baluster_window(ctx, x, y, w, h, col=STONE, n=5, ol=BOL):
    """Window with the turned stone balusters typical of Angkor galleries."""
    rrect(ctx, x - 8, y - 8, w + 16, h + 16, 2, shade(col, 0.1), ol)
    rrect(ctx, x, y, w, h, 1, VOID, ol * 0.8)
    bw = w / (n * 1.6)
    for k in range(n):
        bx = x + w * (k + 0.5) / n
        rrect(ctx, bx - bw / 2, y, bw, h, bw * 0.4, shade(col, 0.05), ol * 0.6)
        ctx.new_path()
        for j in range(1, 6):
            yy = y + h * j / 6
            ellipse_path(ctx, bx, yy, bw * 0.62, bw * 0.22)
        fill_stroke(ctx, shade(col, 0.12), ol * 0.45)


def _devata(ctx, x, base, h, col=STONE, ol=1.6, sx=1.0, seed=0):
    """Small carved devata (standing female relief) in a shallow niche, (x, base) = feet."""
    s = h / 100.0
    ctx.save()
    ctx.translate(x, base)
    ctx.scale(s * sx, s)
    w = ol / s
    lt = shade(col, 0.12)
    dk = shade(col, -0.22)
    ctx.new_path()
    ctx.move_to(-22, 2)
    ctx.line_to(-22, -94)
    ctx.curve_to(-22, -108, -6, -112, 0, -118)
    ctx.curve_to(6, -112, 22, -108, 22, -94)
    ctx.line_to(22, 2)
    ctx.close_path()
    fill_stroke(ctx, shade(col, -0.08), w * 0.8)

    def fig(c, o):
        poly(ctx, [(-7, -94), (-5, -106), (-2, -97), (0, -111), (2, -97), (5, -106), (7, -94)], c, o)
        ellipse(ctx, 0, -86, 6, 7.5, c, o)
        blob(ctx, [(-9, -77), (9, -77), (7, -67), (4, -59), (-4, -59), (-7, -67)], c, o)
        poly(ctx, [(-5, -60), (5, -60), (11, -46), (8, -8), (-8, -8), (-11, -46)], c, o)
        line(ctx, [(-8, -75), (-15, -64), (-9, -72)], 3.4, c)
        line(ctx, [(8, -75), (13, -62), (14, -50)], 3.4, c)
        poly(ctx, [(-8, -8), (-1, -8), (-2, -2), (-15, -2)], c, o)
        poly(ctx, [(8, -8), (1, -8), (2, -2), (15, -2)], c, o)
    ctx.save()
    ctx.translate(1.8, 1.8)
    fig(shade(col, -0.45), 0)
    ctx.restore()
    fig(lt, w * 0.7)
    line(ctx, [(-6, -58), (6, -58)], 1.6, dk)
    poly(ctx, [(-2, -58), (2, -58), (3, -16), (0, -12), (-3, -16)], shade(col, 0.02), w * 0.5)
    curve(ctx, (-6, -76), (0, -70), (6, -76), 1.4, dk)
    for sd in (-1, 1):
        circle(ctx, sd * 6.5, -82, 1.6, dk, 0)
    flower(ctx, -10, -73, 3.2, lt, shade(col, -0.1), w * 0.4)
    ctx.restore()


# =========================================================================== forest pieces (palilay / preah khan)

def _forest_back(g, seed, hz, haze="#a4c6aa", trunk="#bcc8b4", leaf=("#7fa87c", "#8db88a", "#6f9a70")):
    """Misty far forest: a wall of pale crowns, a few far trunks, undergrowth and the high canopy."""
    r = rng(seed)
    g.new_path()
    g.rectangle(B.X0, 300, B.X1 - B.X0, 1100)
    g.set_source(lin_grad(0, 300, 0, hz + 160, [(0, mix(haze, "#ffffff", 0.25)), (1, haze)]))
    g.fill()
    for k in range(80):  # far crowns
        y = r.uniform(170, 560)
        _clump(g, r.uniform(B.X0 - 100, B.X1 + 100), y, r.uniform(60, 130),
               mix(leaf[k % len(leaf)], haze, 0.62 - 0.25 * (y - 170) / 390.0), seed * 300 + k, ol=0, hi=0.06)
    x = B.X0 - 40
    while x < B.X1 + 40:  # far trunks
        w = r.uniform(12, 30)
        top = r.uniform(-280, 200)
        poly(g, [(x - w / 2, hz + 160), (x - w * 0.36, top), (x + w * 0.36, top), (x + w / 2, hz + 160)],
             mix(trunk, haze, r.uniform(0.0, 0.4)), 0)
        x += r.uniform(70, 190)
    for k in range(46):  # high canopy
        _clump(g, r.uniform(B.X0 - 100, B.X1 + 100), r.uniform(-170, 110), r.uniform(70, 150),
               leaf[r.randrange(len(leaf))], seed * 100 + k, ol=0, hi=0.1)
    for k in range(46):  # undergrowth
        _clump(g, r.uniform(B.X0, B.X1), hz + r.uniform(20, 130), r.uniform(40, 90),
               mix(leaf[k % len(leaf)], haze, 0.3), seed * 200 + k, ol=0, hi=0.08)


def _canopy_top(g, seed, cols=("#3f7a3f", "#4f8c45", "#356b38", "#5a9a4a"), y0=-160, y1=40, n=40, ol=2.0):
    r = rng(seed)
    for k in range(n):
        _clump(g, r.uniform(B.X0 - 100, B.X1 + 100), r.uniform(y0, y1), r.uniform(70, 140),
               cols[r.randrange(len(cols))], seed * 77 + k, ol=ol)


def _liana(ctx, x, y0, y1, t, seed, col="#4d6b2c", w=4.0):
    sw = math.sin(t * 0.6 + seed) * 10
    curve(ctx, (x, y0), (x + 40 + sw, (y0 + y1) / 2), (x + 10 + sw * 1.6, y1), w + 2 * 1.4, OUTLINE)
    curve(ctx, (x, y0), (x + 40 + sw, (y0 + y1) / 2), (x + 10 + sw * 1.6, y1), w, col)
    for k in range(6):
        u = (k + 1) / 7
        px = lerp(x, x + 10 + sw * 1.6, u) + math.sin(u * math.pi) * (24 + sw * 0.5)
        py = lerp(y0, y1, u)
        ellipse(ctx, px + (8 if k % 2 else -8), py, 9, 5, "#5f9a45", 1.4, rot=0.6 if k % 2 else -0.6)


# ---------------------------------------------------------------------------- palilay

def _tier(g, cx, yb, hw, h, col, seed, ol=BOL, niche=True, antefix=True):
    rrect(g, cx - hw, yb - h, 2 * hw, h, 1, col, ol)
    _clip_rect(g, cx - hw, yb - h, 2 * hw, h)
    _courses(g, cx - hw, yb - h + h / 3, cx + hw, yb, h / 3, seed, shade(col, -0.35), 1.2, 20, 60, 0.55)
    _weather(g, cx - hw, yb - h, cx + hw, yb, seed + 1, 1.4)
    g.restore()
    for sd in (-1, 1):  # redented corner pilasters
        x0 = cx + sd * hw
        poly(g, [(x0, yb - h), (x0 - sd * hw * 0.16, yb - h), (x0 - sd * hw * 0.16, yb), (x0, yb)],
             shade(col, -0.1 if sd > 0 else 0.06), ol * 0.7)
    rrect(g, cx - hw * 1.07, yb - h - h * 0.16, hw * 2.14, h * 0.18, 1, shade(col, 0.08), ol * 0.8)
    if niche:  # false door
        rrect(g, cx - hw * 0.16, yb - h * 0.78, hw * 0.32, h * 0.66, 2, shade(col, -0.07), ol * 0.45)
        line(g, [(cx, yb - h * 0.74), (cx, yb - h * 0.16)], max(1, ol * 0.4), shade(col, -0.3), 0.7)
        _pediment(g, cx, yb - h * 0.78, hw * 0.46, h * 0.34, col, ol * 0.5, inner=False)
    if antefix:
        for sd in (-1, 1):
            A.prang(g, cx + sd * hw * 0.9, yb - h - h * 0.12, hw * 0.16, h * 0.95, shade(col, 0.06), ol * 0.6,
                    detail=False)


def _palilay_temple(g, cx, gy):
    col = STONE
    # stepped laterite base
    y = gy
    for i, (hw, h) in enumerate(((440, 56), (360, 52), (285, 48))):
        _stone_rect(g, cx - hw, y - h, 2 * hw, h, LATERITE, 40 + i, 18, BOL, 0.8, True, True)
        for sd in (-1, 1):  # broken corners
            ex = cx + sd * hw
            poly(g, [(ex, y - h - 2), (ex - sd * 34, y - h - 2), (ex - sd * 18, y - h + 16), (ex + sd * 2, y - h + 22)],
                 shade(LATERITE, -0.15), BOL * 0.7)
        y -= h
    top = y
    # front stair with cheek walls
    poly(g, [(cx - 96, gy + 2), (cx - 80, top), (cx + 80, top), (cx + 96, gy + 2)], shade(col, -0.12), BOL)
    poly(g, [(cx - 74, gy + 2), (cx - 62, top), (cx + 62, top), (cx + 74, gy + 2)], shade(col, 0.06), BOL)
    g.new_path()
    for k in range(1, 12):
        yy = gy - (gy - top) * k / 12.0
        hw = lerp(74, 62, k / 12.0)
        g.move_to(cx - hw, yy)
        g.line_to(cx + hw, yy)
    src(g, shade(col, -0.4), 0.8)
    g.set_line_width(2.2)
    g.stroke()
    for k in range(12):
        yy = gy - (gy - top) * (k + 0.5) / 12.0
        hw = lerp(74, 62, (k + 0.5) / 12.0)
        line(g, [(cx - hw + 3, yy + 3), (cx + hw - 3, yy + 3)], 2.5, shade(col, 0.2), 0.7)
    # sanctuary (clipped by a jagged collapse line at the top)
    jag = [(cx - 240, 280), (cx - 130, 266), (cx - 96, 244), (cx - 80, 206), (cx - 62, 196), (cx - 50, 158),
           (cx - 30, 148), (cx - 12, 122), (cx + 6, 134), (cx + 22, 116), (cx + 40, 142), (cx + 56, 170),
           (cx + 72, 180), (cx + 86, 220), (cx + 104, 244), (cx + 130, 266), (cx + 240, 280)]
    g.save()
    g.new_path()
    poly_path(g, jag + [(cx + 240, gy), (cx - 240, gy)])
    g.clip()
    py = top
    rrect(g, cx - 152, py - 30, 304, 30, 2, shade(col, 0.05), BOL)          # plinth mouldings
    rrect(g, cx - 140, py - 46, 280, 18, 2, shade(col, -0.04), BOL * 0.8)
    by = py - 46
    bh = 250
    _stone_rect(g, cx - 118, by - bh, 236, bh, col, 51, 24, BOL, 1.3)
    for sd in (-1, 1):
        x0 = cx + sd * 118
        poly(g, [(x0, by - bh), (x0 - sd * 20, by - bh), (x0 - sd * 20, by), (x0, by)],
             shade(col, -0.12 if sd > 0 else 0.07), BOL * 0.8)
    _shade_right(g, cx + 30, by - bh, 88, bh, 0.1)
    _doorway(g, cx, by, 60, 128, col, BOL, inner=None)
    for bx, byy, bw, bhh in ((cx - 100, by - 170, 28, 20), (cx + 74, by - 60, 30, 22), (cx + 80, by - 214, 24, 18)):
        rrect(g, bx, byy, bw, bhh, 1, shade(col, -0.45), BOL * 0.6)   # missing blocks
    cy = by - bh
    rrect(g, cx - 140, cy - 20, 280, 22, 2, shade(col, 0.1), BOL)
    yb = cy - 18
    sil = [(cx - 140, cy - 20, 280, 40)]
    for i, (hw, h) in enumerate(((108, 58), (92, 50), (78, 44), (66, 38), (56, 33), (46, 28))):
        _tier(g, cx, yb, hw, h, shade(col, 0.02 * i), 60 + i)
        sil.append((cx - hw * 1.07, yb - h * 1.16, hw * 2.14, h * 1.16 + 1))
        yb -= h + h * 0.16
    A.prang(g, cx, yb, 34, 60, shade(col, 0.05), BOL, detail=False)
    sil.append((cx - 34, yb - 60, 68, 60))
    g.restore()
    # broken top edge: exposed rubble core + outline, clipped to the tower silhouette
    g.save()
    g.new_path()
    g.new_path()
    for rx, ry, rw, rh in sil:
        g.rectangle(rx, ry, rw, rh)
    g.clip()
    g.new_path()
    poly_path(g, jag, close=False)
    src(g, shade(col, -0.3))
    g.set_line_width(14)
    g.stroke_preserve()
    src(g, OUTLINE)
    g.set_line_width(BOL)
    g.stroke()
    g.restore()
    # plants growing on the ruin
    for px, py_, s in ((cx - 30, 150, 1.0), (cx + 60, 176, 0.8), (cx - 76, 208, 0.7), (cx + 96, 236, 0.6)):
        g.new_path()
        for k in range(-3, 4):
            g.move_to(px + k * 3 * s, py_)
            g.line_to(px + k * 7 * s, py_ - (22 - abs(k) * 4) * s)
        src(g, "#4f8a35")
        g.set_line_width(2.6)
        g.stroke()
    line(g, [(cx + 22, 122), (cx + 44, 76), (cx + 38, 40)], 7, OUTLINE)
    line(g, [(cx + 22, 122), (cx + 44, 76), (cx + 38, 40)], 4, "#7a5a3a")
    for k, (lx, ly, lr) in enumerate(((cx + 38, 36, 30), (cx + 64, 58, 22), (cx + 16, 62, 20))):
        _clump(g, lx, ly, lr, "#5a9a45", 900 + k, ol=1.6)
    for (x0, x1, yy) in ((cx - 440, cx + 440, gy - 56), (cx - 360, cx + 360, gy - 108), (cx - 285, cx + 285, top)):
        _spots(g, x0, yy - 4, x1, yy + 4, 26, int(x0), MOSS, 0.6, 6, 16, 0.4)


def _palilay_mg(g):
    r = rng(5)
    for k in range(34):  # undergrowth behind the temple
        _clump(g, r.uniform(B.X0, B.X1), 790 - r.uniform(0, 70), r.uniform(50, 100),
               ("#4c8a45", "#5a9a4c", "#437d3d")[k % 3], 300 + k, ol=2.0)
    for x, w in ((-360, 78), (-110, 56), (250, 66), (1660, 60), (1900, 86), (2230, 64)):
        _tall_trunk(g, x, 795, w, BARK, seed=x + 1000)
    _palilay_temple(g, 960, 792)
    _rubble(g, 470, 806, 4, 0.85, 7)
    _rubble(g, 1450, 804, 5, 0.85, 8)
    _block(g, 640, 688, 70, 40, 0.06, STONE, 21)
    _block(g, 1290, 688, 64, 40, -0.08, STONE, 22)
    for x, s in ((120, 0.9), (1780, 1.0), (540, 0.6), (1360, 0.65)):
        _fern(g, x, 800, s, 0.0, "#3f8a3a", int(x) + 3)
    _canopy_top(g, 51, y0=-200, y1=-40, n=44)


def _palilay_ground(g):
    g.new_path()
    g.rectangle(B.X0, 780, B.X1 - B.X0, 520)
    g.set_source(lin_grad(0, 780, 0, 1080, [(0, "#7d8350"), (1, "#5b6a38")]))
    g.fill()
    g.new_path()  # trodden laterite path to the stair
    g.move_to(700, 1300)
    g.curve_to(820, 1000, 880, 860, 880, 790)
    g.line_to(1040, 790)
    g.curve_to(1040, 860, 1110, 1000, 1240, 1300)
    g.close_path()
    g.set_source(lin_grad(0, 790, 0, 1080, [(0, "#a98a5e"), (1, "#9b7a50")]))
    g.fill()
    _litter(g, 790, 1090, 900, 61, ("#b07a3a", "#8f5a2e", "#c9a14a", "#6f5a32", "#a8b05a"))
    _tufts(g, 800, 1080, 70, 62, "#4c7f35", s0=0.6, s1=1.4)
    for pts, w0 in (([(40, 1010), (170, 990), (300, 1012), (400, 1040)], 44),
                    ([(60, 930), (170, 900), (270, 892)], 30),
                    ([(1870, 960), (1770, 930), (1680, 936)], 32)):
        _ground_root(g, pts, w0, 10, "#a0957c")
    _block(g, 210, 860, 120, 60, 0.15, STONE, 63)
    _block(g, 1700, 870, 110, 56, -0.1, STONE, 64)
    _block(g, 1790, 830, 80, 44, 0.3, STONE, 65)


def _palilay_fg(g):
    _tall_trunk(g, -40, 1130, 200, "#a59a82", top=-400, lean=-10, seed=77)
    _fern(g, 1980, 1110, 1.5, 0.0, "#2f7a30", 81, 8)
    _fern(g, 120, 1120, 1.1, 0.0, "#2f7a30", 82, 6)


@extra
def _palilay(ctx, layer, t, tod):
    hz = 640
    if layer == "SKY":
        _sky(ctx, t, tod, hz, ncloud=4)
        _maybe_birds(ctx, t, tod, n=4, y0=60, y1=260)
    elif layer == "BG":
        _cached(ctx, ("palilay", "BG"), lambda g: _forest_back(g, 11, hz))
    elif layer == "MG":
        _cached(ctx, ("palilay", "MG"), _palilay_mg)
        _shafts(ctx, t, [(1180, 120, 0.16, -420), (320, 90, 0.11, -300), (1720, 70, 0.10, -380)])
        A.mist(ctx, t, 760, 0.12, seed=9)
    elif layer == "GROUND":
        _cached(ctx, ("palilay", "GROUND"), _palilay_ground)
        _dapple(ctx, t, 800, 1080, 5, 24, 0.24)
    elif layer == "FG":
        _cached(ctx, ("palilay", "FG"), _palilay_fg)
        _liana(ctx, 1840, -40, 380, t, 3)


# =========================================================================== preah khan

PK_VX, PK_VY = 960, 540
PK_FL, PK_SP, PK_AP, PK_HW = 420, 520, 860, 820     # floor drop, wall springing, vault apex, half width (at f=1)
PK_DW, PK_DH, PK_T = 220, 760, 0.12                 # door half width, door height, wall thickness factor
PK_F0, PK_R, PK_N = 0.52, 0.8, 13


def _pk_door(f, k):
    dk = 0.975 ** k
    x0, x1 = PK_VX - PK_DW * f * dk, PK_VX + PK_DW * f * dk
    fl = PK_VY + PK_FL * f
    return x0, x1, fl - PK_DH * f * dk, fl


def _pk_wall_face(g, k, f, col, texture=True):
    """Wall k of the enfilade: a big face with door k cut out, frame, lintel and the jamb reveals."""
    x0, x1, top, fl = _pk_door(f, k)
    g.new_path()
    g.rectangle(B.X0 - 100, -400, B.X1 - B.X0 + 200, 1800)
    g.rectangle(x0, top, x1 - x0, fl - top)
    g.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    src(g, col)
    g.fill()
    g.set_fill_rule(cairo.FILL_RULE_WINDING)
    if texture and f > 0.1:
        g.save()
        g.new_path()
        g.rectangle(B.X0 - 100, -400, B.X1 - B.X0 + 200, 1800)
        g.rectangle(x0, top, x1 - x0, fl - top)
        g.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        g.clip()
        g.set_fill_rule(cairo.FILL_RULE_WINDING)
        ch = 44 * f
        _courses(g, x0 - 900 * f, fl - 1400 * f, x1 + 900 * f, fl, ch, 300 + k, shade(col, -0.3), max(0.8, 2.2 * f),
                 ch * 1.5, ch * 4, 0.6)
        _weather(g, x0 - 600 * f, top - 500 * f, x1 + 600 * f, fl, 310 + k, 0.8)
        for sd in (-1, 1):  # small devatas flanking the door
            _devata(g, PK_VX + sd * (PK_DW + 150) * f, fl - 70 * f, 300 * f, col, max(0.8, 2.2 * f), 1.0, k)
        g.restore()
    fw = 26 * f
    ol = max(0.8, BOL * min(1.0, f * 1.6))
    g.new_path()  # sandstone frame + lintel
    g.rectangle(x0 - fw, top - fw, x1 - x0 + 2 * fw, fl - top + fw)
    g.rectangle(x0, top, x1 - x0, fl - top)
    g.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    fill_stroke(g, shade(col, 0.1), ol)
    g.set_fill_rule(cairo.FILL_RULE_WINDING)
    lh = 40 * f
    rrect(g, x0 - fw * 2.4, top - fw - lh, x1 - x0 + fw * 4.8, lh, 2, shade(col, 0.06), ol)
    g.new_path()
    for j in range(7):
        xx = x0 - fw * 2 + (x1 - x0 + fw * 4) * (j + 0.5) / 7
        g.move_to(xx - 10 * f, top - fw - lh * 0.3)
        g.curve_to(xx, top - fw - lh * 0.9, xx, top - fw - lh * 0.9, xx + 10 * f, top - fw - lh * 0.3)
    src(g, shade(col, -0.35), 0.8)
    g.set_line_width(max(0.8, 2 * f))
    g.stroke()
    if f > 0.15:
        _pediment(g, PK_VX, top - fw - lh, (x1 - x0) * 1.1, 150 * f, shade(col, 0.02), ol, inner=f > 0.3)
    f2 = f * (1 - PK_T)  # jamb reveals (wall thickness) seen inside the opening
    a0, a1, atop, afl = _pk_door(f2, k)
    rev = mix(col, "#fff2cf", 0.25)
    poly(g, [(x0, top), (a0, atop), (a0, afl), (x0, fl)], shade(rev, 0.04), ol * 0.7)
    poly(g, [(x1, top), (a1, atop), (a1, afl), (x1, fl)], shade(rev, -0.08), ol * 0.7)
    poly(g, [(x0, top), (x1, top), (a1, atop), (a0, atop)], shade(rev, -0.25), ol * 0.7)
    poly(g, [(x0, fl), (x1, fl), (a1, afl), (a0, afl)], mix(rev, "#ffffff", 0.15), ol * 0.7)


def _pk_floor_strip(g, f_far, f_near, col):
    yf, yn = PK_VY + PK_FL * f_far, PK_VY + PK_FL * f_near
    g.new_path()
    g.rectangle(B.X0 - 100, yf, B.X1 - B.X0 + 200, yn - yf + 2)
    src(g, col)
    g.fill()


def _pk_enfilade(g):
    fs = [PK_F0 * PK_R ** k for k in range(PK_N + 2)]
    g.new_path()
    g.rectangle(B.X0 - 100, -400, B.X1 - B.X0 + 200, 1800)
    src(g, "#fff6da")
    g.fill()
    xN0, xN1, topN, flN = _pk_door(fs[PK_N], PK_N)
    for k in range(4):  # the far end: greenery in bright light
        circle(g, PK_VX - 12 + k * 9, topN + 4 + (k % 2) * 3, 7, "#cfe3a8", 0)
    for k in range(PK_N, 0, -1):
        u = 1 - (k - 1) / (PK_N - 1)          # 1 near, 0 far
        col = mix("#e3d2a6", "#8b7c60", u ** 0.9)
        floor_col = mix("#f2e4bd", "#a3926f", u ** 0.9)
        _pk_floor_strip(g, fs[k + 1], fs[k] * (1 - PK_T), floor_col)
        _pk_wall_face(g, k, fs[k], col, texture=k <= 5)
        if k in (3, 6, 9):  # light falling through a collapsed vault onto the chamber floor
            x0, x1, top, fl = _pk_door(fs[k], k)
            g.new_path()
            ellipse_path(g, PK_VX, PK_VY + PK_FL * fs[k] * 1.08, (x1 - x0) * 0.42, 6 * fs[k] * 4)
            src(g, "#fff3c8", 0.5)
            g.fill()
    gx, gy = PK_VX, (topN + flN) / 2  # glow of the bright far end over the nearer frames
    g.new_path()
    g.arc(gx, gy, 360, 0, 2 * math.pi)
    g.set_source(rad_grad(gx, gy, 0, 360, [(0, (1, 0.97, 0.85, 0.75)), (0.35, (1, 0.95, 0.8, 0.25)),
                                           (1, (1, 0.95, 0.8, 0.0))]))
    g.fill()
    _pk_floor_strip(g, fs[1], PK_F0 * (1 - PK_T), mix("#e3d2a6", "#9a8a6a", 0.85))  # chamber-0 floor


def _pk_room(g):
    f0, F = PK_F0, 1.9
    vx = PK_VX

    def P(f, h=0.0, side=0):  # point on a side wall (side -1/1) at depth f and height h above the floor
        return (vx + side * PK_HW * f, PK_VY + (PK_FL - h) * f)

    def sp(f):
        return PK_VY - PK_SP * f

    def ap(f):
        return PK_VY - PK_AP * f

    floor0 = PK_VY + PK_FL * f0
    hw0 = PK_HW * f0
    g.new_path()  # floor
    poly_path(g, [(vx - hw0, floor0), (vx + hw0, floor0), (vx + PK_HW * F, PK_VY + PK_FL * F),
                  (vx - PK_HW * F, PK_VY + PK_FL * F)])
    g.set_source(lin_grad(0, floor0, 0, 1080, [(0, "#b3a27f"), (1, "#8f8064")]))
    g.fill()
    g.new_path()
    for k in range(-5, 6):
        g.move_to(vx + k * 150 * f0, floor0)
        g.line_to(vx + k * 150 * F, PK_VY + PK_FL * F)
    f = f0
    while f < F:
        f *= 1.16
        g.move_to(vx - PK_HW * f, PK_VY + PK_FL * f)
        g.line_to(vx + PK_HW * f, PK_VY + PK_FL * f)
    src(g, "#6e6249", 0.55)
    g.set_line_width(2)
    g.stroke()
    _spots(g, B.X0, floor0, B.X1, 1100, 60, 701, "#5d553f", 0.12, 10, 40, 0.3)
    _litter(g, floor0 + 10, 1090, 60, 702, ("#8f6a3a", "#a98a4a", "#6f5a32"))
    for side in (-1, 1):  # side walls
        pts = [P(f0, 0, side), (vx + side * hw0, sp(f0)), (vx + side * PK_HW * F, sp(F)), P(F, 0, side)]
        g.new_path()
        poly_path(g, pts)
        g.set_source(lin_grad(vx + side * hw0, 0, vx + side * PK_HW * 1.3, 0,
                              [(0, "#9c8d6f"), (1, "#75684f" if side < 0 else "#6c604a")]))
        g.fill_preserve()
        g.save()
        g.clip()
        g.new_path()
        for h in range(40, 1200, 46):  # courses converge to the vanishing point
            a, b = P(f0, h, side), P(F, h, side)
            g.move_to(*a)
            g.line_to(*b)
        r = rng(710 + side)
        f = f0
        while f < F:
            f *= r.uniform(1.06, 1.14)
            x = vx + side * PK_HW * f
            g.move_to(x, sp(f))
            g.line_to(x, PK_VY + PK_FL * f)
        src(g, "#54493a", 0.45)
        g.set_line_width(2)
        g.stroke()
        _weather(g, B.X0, -300, B.X1, 1200, 720 + side, 0.5)
        for f in (0.6, 0.76, 0.98, 1.3):  # carved devatas along the wall
            x, y = P(f, 60, side)
            _devata(g, x - side * 6 * f, y, 330 * f, "#9a8b6c", 2.0, 0.42, int(f * 10))
        if side > 0:  # a side doorway on the right wall with daylight beyond
            fa, fb = 0.70, 0.86
            q = [P(fa, 460, 1), P(fb, 460, 1), P(fb, 0, 1), P(fa, 0, 1)]
            poly(g, [P(fa - 0.025, 500, 1), P(fb + 0.03, 500, 1), P(fb + 0.03, 0, 1), P(fa - 0.025, 0, 1)],
                 shade("#9c8d6f", 0.1), BOL)
            poly(g, q, "#3a3026", BOL)
            g.new_path()
            poly_path(g, [(q[0][0] + 14, q[0][1] + 30), (q[1][0] - 4, q[1][1] + 30), (q[2][0] - 4, q[2][1] - 4),
                          (q[3][0] + 14, q[3][1] - 4)])
            g.set_source(lin_grad(0, q[0][1], 0, q[3][1], [(0, "#d9eab0"), (1, "#a9c47a")]))
            g.fill()
        g.restore()
        g.new_path()
        poly_path(g, pts, close=False)
        fill_stroke(g, None, BOL)
    for side in (-1, 1):  # corbelled vault (stepped)
        pts = [(vx + side * hw0, sp(f0)), (vx, ap(f0)), (vx, ap(F)), (vx + side * PK_HW * F, sp(F))]
        poly(g, pts, "#5a4e3e" if side < 0 else "#4f4436", BOL)
        g.new_path()
        for u in (0.18, 0.36, 0.54, 0.72, 0.88):
            a = (vx + side * hw0 * (1 - u), sp(f0) + (ap(f0) - sp(f0)) * u)
            b = (vx + side * PK_HW * F * (1 - u), sp(F) + (ap(F) - sp(F)) * u)
            g.move_to(*a)
            g.line_to(*b)
        src(g, "#2e271f", 0.7)
        g.set_line_width(3)
        g.stroke()
    hole = [(1120, 120), (1140, 90), (1132, 60), (1158, 30), (1150, -10), (1200, 0), (1240, 20), (1262, 10),
            (1300, 40), (1340, 50), (1372, 80), (1410, 90), (1400, 130), (1370, 150), (1340, 190), (1316, 202),
            (1280, 180), (1240, 178), (1200, 150), (1160, 146)]  # collapsed blocks in the vault: daylight
    g.new_path()
    poly_path(g, hole)
    g.set_source(lin_grad(0, -60, 0, 150, [(0, "#f6f9e6"), (1, "#d9ebb6")]))
    g.fill_preserve()
    fill_stroke(g, None, BOL)
    for k, (lx, ly, lr) in enumerate(((1170, -40, 30), (1250, -36, 26), (1330, -6, 30), (1400, 40, 22))):
        _clump(g, lx, ly, lr, ("#5a9a45", "#4f8c45")[k % 2], 730 + k, ol=1.5)
    curve(g, (1236, 30), (1262, 110), (1244, 220), 3.4, "#4d6b2c")
    curve(g, (1330, 50), (1318, 140), (1336, 260), 3.0, "#4d6b2c")
    steps = []  # back wall with the first doorway (stepped corbel gable)
    n = 7
    for i in range(n + 1):
        u = i / n
        steps.append((vx - hw0 * (1 - u), sp(f0) + (ap(f0) - sp(f0)) * u))
    gable = []
    for i in range(n):
        gable += [steps[i], (steps[i][0], steps[i + 1][1])]
    gable.append((vx, ap(f0)))
    outer = [(vx - hw0, floor0)] + gable + [(2 * vx - x, y) for x, y in reversed(gable)] + [(vx + hw0, floor0)]
    x0, x1, top, fl = _pk_door(f0, 0)
    g.new_path()
    poly_path(g, outer)
    g.rectangle(x0, top, x1 - x0, fl - top)
    g.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    g.set_source(lin_grad(vx - hw0, 0, vx + hw0, 0, [(0, "#9f9073"), (1, "#8a7c61")]))
    g.fill_preserve()
    g.save()
    g.clip()
    g.set_fill_rule(cairo.FILL_RULE_WINDING)
    _courses(g, vx - hw0, floor0 - 500, vx + hw0, floor0, 25, 740, "#5b4f3c", 1.6, 30, 90, 0.55)
    _courses(g, vx - hw0, ap(f0), vx + hw0, floor0 - 500, 25, 741, "#5b4f3c", 1.6, 30, 90, 0.55)
    _weather(g, vx - hw0, ap(f0), vx + hw0, floor0, 742, 1.2)
    for sd in (-1, 1):
        _devata(g, vx + sd * 290, floor0 - 210, 190, "#a19275", 2.2, 1.0, 5 + sd)
    g.restore()
    g.set_fill_rule(cairo.FILL_RULE_WINDING)
    g.new_path()
    poly_path(g, outer)
    fill_stroke(g, None, BOL)
    _pk_door0(g, f0)
    _rubble(g, 360, 900, 5, 0.9, 751)  # fallen blocks along the walls
    _rubble(g, 1620, 930, 6, 1.0, 752)
    _block(g, 250, 1000, 150, 80, 0.08, "#a39474", 753)


def _pk_door0(g, f0):
    """Door 0 frame/lintel/pediment and reveals (the wall fill itself is drawn by _pk_room)."""
    x0, x1, top, fl = _pk_door(f0, 0)
    col = "#9a8b6e"
    fw = 26 * f0
    g.new_path()
    g.rectangle(x0 - fw, top - fw, x1 - x0 + 2 * fw, fl - top + fw)
    g.rectangle(x0, top, x1 - x0, fl - top)
    g.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    fill_stroke(g, shade(col, 0.12), BOL)
    g.set_fill_rule(cairo.FILL_RULE_WINDING)
    for sd in (-1, 1):
        _colonnette(g, PK_VX + sd * (x1 - x0) / 2 + sd * fw * 1.9, top, fl, fw * 1.1, shade(col, 0.16), BOL * 0.8)
    lh = 40 * f0
    ly = top - fw - lh
    rrect(g, x0 - fw * 3, ly, x1 - x0 + fw * 6, lh, 2, shade(col, 0.08), BOL)
    g.new_path()
    for j in range(9):
        xx = x0 - fw * 2.5 + (x1 - x0 + fw * 5) * (j + 0.5) / 9
        g.move_to(xx - 8, ly + lh * 0.3)
        g.curve_to(xx, ly + lh * 0.95, xx, ly + lh * 0.95, xx + 8, ly + lh * 0.3)
    src(g, shade(col, -0.4), 0.8)
    g.set_line_width(1.8)
    g.stroke()
    circle(g, PK_VX, ly + lh / 2, lh * 0.32, shade(col, 0.14), BOL * 0.6)
    _pediment(g, PK_VX, ly, (x1 - x0) * 1.25, 130, shade(col, 0.03), BOL)
    f2 = f0 * (1 - PK_T)
    a0, a1, atop, afl = _pk_door(f2, 0)
    rev = mix(col, "#fff2cf", 0.2)
    poly(g, [(x0, top), (a0, atop), (a0, afl), (x0, fl)], shade(rev, 0.06), BOL * 0.8)
    poly(g, [(x1, top), (a1, atop), (a1, afl), (x1, fl)], shade(rev, -0.1), BOL * 0.8)
    poly(g, [(x0, top), (x1, top), (a1, atop), (a0, atop)], shade(rev, -0.3), BOL * 0.8)
    poly(g, [(x0, fl), (x1, fl), (a1, afl), (a0, afl)], mix(rev, "#ffffff", 0.1), BOL * 0.8)


def _pk_motes(ctx, t):
    r = rng(77)
    ctx.new_path()
    for i in range(26):
        u = r.random()
        x0 = r.uniform(1230, 1560)
        y = (r.uniform(0, 900) - t * r.uniform(4, 10)) % 900 + 60
        x = x0 + (y - 60) * 0.18 + math.sin(t * 0.5 + i) * 10
        ctx.new_sub_path()
        ctx.arc(x, y, 1.5 + u * 2, 0, 2 * math.pi)
    src(ctx, "#fff6d8", 0.55)
    ctx.fill()


# ---------------------------------------------------------------------------- preah khan: tree on the gallery

TX_PK = 1272
CASCADES_PK = [  # (points relative to the trunk, top width, bottom width): roots pouring down the gallery wall
    ([(-300, 450), (-380, 500), (-420, 580), (-430, 680), (-446, 806)], 56, 40),
    ([(-220, 450), (-262, 530), (-258, 620), (-270, 720), (-276, 806)], 66, 44),
    ([(-140, 460), (-170, 550), (-162, 640), (-180, 730), (-174, 806)], 70, 46),
    ([(-60, 470), (-80, 560), (-70, 650), (-92, 740), (-86, 806)], 74, 48),
    ([(10, 470), (0, 570), (14, 660), (-2, 806)], 84, 54),
    ([(80, 470), (96, 560), (84, 650), (100, 740), (92, 806)], 74, 48),
    ([(150, 460), (180, 550), (170, 640), (186, 730), (178, 806)], 70, 46),
    ([(230, 450), (270, 530), (262, 620), (276, 720), (280, 806)], 66, 44),
    ([(300, 450), (390, 500), (430, 580), (444, 680), (466, 806)], 56, 40),
]
CROSS_PK = [([(-300, 560), (-210, 610), (-120, 690), (-60, 770)], 34, 24),
            ([(260, 590), (170, 660), (110, 770)], 32, 22),
            ([(-100, 610), (-10, 660), (80, 640), (170, 700)], 26, 20)]


def _pk_tree(g):
    tx = TX_PK
    _taper(g, [(tx - 40, 300), (tx - 260, 40), (tx - 420, -160)], 120, 60, ROOT, BOL, hi="#ece6d6")
    _taper(g, [(tx + 40, 240), (tx + 280, 20), (tx + 400, -200)], 110, 50, ROOT, BOL, hi="#ece6d6")
    mass = [(tx - 112, -420), (tx - 122, 250), (tx - 160, 330), (tx - 260, 392), (tx - 360, 432), (tx - 390, 468),
            (tx - 300, 500), (tx - 150, 516), (tx, 526), (tx + 150, 516), (tx + 300, 500), (tx + 390, 468),
            (tx + 360, 432), (tx + 260, 392), (tx + 160, 330), (tx + 128, 250), (tx + 112, -420)]
    roots = []
    for pts, w0, w1 in CASCADES_PK + CROSS_PK:
        roots.append(_taper_poly([(tx + dx, y) for dx, y in pts], w0, w1))
    shapes = [("smooth", mass)] + [r_[1] for r_ in roots]
    g.push_group()
    _union(g, shapes, ROOT, BOL, shadow=(12, 7, 0.28))
    # carved-looking detail: light ridges + dark grooves along each root, bark streaks on the trunk
    for sp, P, L, R in roots:
        line(g, [(l[0] * 0.65 + c[0] * 0.35, l[1] * 0.65 + c[1] * 0.35) for l, c in zip(L, sp)][1:-1], 5, "#f3eee2", 0.9)
        line(g, [(r_[0] * 0.8 + c[0] * 0.2, r_[1] * 0.8 + c[1] * 0.2) for r_, c in zip(R, sp)][2:-1], 2.2, "#8f8572", 0.7)
    g.save()
    g.new_path()
    smooth_path(g, mass)
    g.clip()
    _shade_right(g, tx + 40, -420, 400, 1000, 0.13)
    g.new_path()
    r = rng(840)
    for k in range(18):
        xx = tx + r.uniform(-120, 120)
        y0 = r.uniform(-400, 300)
        g.move_to(xx, y0)
        g.curve_to(xx + 6, y0 + 60, xx - 6, y0 + 120, xx + r.uniform(-8, 8), y0 + r.uniform(100, 240))
    for k in range(9):  # buttress ridges flowing into the roots
        x0 = tx + (k - 4) * 34
        g.move_to(tx + (k - 4) * 12, 280)
        g.curve_to(x0, 360, x0 + (k - 4) * 28, 420, x0 + (k - 4) * 46, 520)
    src(g, "#a49a85", 0.6)
    g.set_line_width(3)
    g.stroke()
    _spots(g, tx - 160, -400, tx + 160, 440, 40, 841, "#f4f0e4", 0.4, 6, 22, 0.5)
    g.restore()
    _spots(g, tx - 420, 380, tx + 440, 800, 30, 842, MOSS, 0.0, 8, 26, 0.6)
    g.pop_group_to_source()
    g.paint()
    _canopy_top(g, 845, ("#3f7a3f", "#4f8c45", "#356b38", "#5a9a4a"), -200, 60, 40)
    for k, x in enumerate((780, 1010, 1560, 1780, 1900)):  # thin aerial roots hanging from the crown
        curve(g, (x, 40), (x + 18, 220), (x + 6, 380 + k * 30), 3.2, "#8e8370")


def _root_flare(g, x, y, w, length, side, col=ROOT):
    """Root foot spreading on the ground from the wall base; clipped at y so it joins the MG root seamlessly."""
    pts = [(x, y - 20), (x + side * length * 0.35, y + 16), (x + side * length * 0.75, y + 30), (x + side * length, y + 36)]
    sp, P, L, R = _taper_poly(pts, w, 10)
    g.save()
    g.new_path()
    g.rectangle(B.X0, y, B.X1 - B.X0, 400)
    g.clip()
    g.save()
    g.translate(5, 8)
    poly(g, P, (0.15, 0.11, 0.06), 0)
    g.restore()
    poly(g, P, col, BOL)
    line(g, [(l[0] * 0.6 + c[0] * 0.4, l[1] * 0.6 + c[1] * 0.4) for l, c in zip(L, sp)][2:-2], 4, "#f3eee2", 0.8)
    g.restore()


def _pk_gallery(g):
    col = STONE
    gy = 800
    _stone_rect(g, B.X0, 540, B.X1 - B.X0, 222, col, 801, 26, BOL, 1.4)  # long gallery wall
    rrect(g, B.X0, 760, B.X1 - B.X0, 42, 2, shade(col, -0.06), BOL)
    rrect(g, B.X0, 748, B.X1 - B.X0, 16, 2, shade(col, 0.08), BOL * 0.8)
    rrect(g, B.X0, 516, B.X1 - B.X0, 28, 2, shade(col, 0.1), BOL)
    g.save()  # corbelled roof in three steps
    for i, (y0, h, ins) in enumerate(((482, 36, 0), (448, 36, 14), (418, 32, 30))):
        _stone_rect(g, B.X0 + ins, y0, B.X1 - B.X0 - 2 * ins, h, shade(col, -0.04 + 0.04 * i), 810 + i, h, BOL * 0.9, 1.6)
    rrect(g, B.X0, 404, B.X1 - B.X0, 16, 4, shade(col, 0.12), BOL * 0.8)
    for x in range(-500, 2460, 160):
        A.prang(g, x, 406, 9, 26, shade(col, 0.08), BOL * 0.6, detail=False)
    g.restore()
    _rubble(g, 230, 410, 3, 0.5, 815)
    for x in (-250, 130, 1820, 2190):
        _baluster_window(g, x - 60, 588, 120, 136, col, 5)
    gx = 600  # gopura (doorway pavilion) on the left
    _stone_rect(g, gx - 170, 380, 340, 420, shade(col, 0.04), 820, 26, BOL, 1.2)
    _shade_right(g, gx + 70, 380, 100, 420, 0.1)
    _doorway(g, gx, gy, 116, 250, col, BOL, inner="#cfe0a6")
    g.save()
    g.new_path()
    poly_path(g, [(gx - 200, 400), (gx - 200, 300), (gx - 120, 250), (gx - 70, 262), (gx - 40, 214), (gx + 10, 232),
                  (gx + 60, 196), (gx + 110, 250), (gx + 200, 270), (gx + 200, 400)])
    g.clip()
    yb = 384
    for i, (hw, h) in enumerate(((150, 56), (122, 50), (96, 44), (72, 40))):
        _tier(g, gx, yb, hw, h, shade(col, 0.03 * i), 830 + i)
        yb -= h * 1.16
    g.restore()
    _pk_tree(g)


def _pk_roots_ground(g):
    g.new_path()
    g.rectangle(B.X0, 790, B.X1 - B.X0, 520)
    g.set_source(lin_grad(0, 790, 0, 1080, [(0, "#a8956c"), (1, "#8a7a52")]))
    g.fill()
    _spots(g, B.X0, 800, B.X1, 1090, 50, 851, "#6f8a45", 0.35, 20, 80, 0.25)
    _litter(g, 800, 1090, 500, 852, ("#b07a3a", "#8f5a2e", "#c9a14a", "#6f5a32"))
    _tufts(g, 800, 1080, 60, 853, "#4c7f35", s0=0.6, s1=1.4)
    tx = TX_PK
    for pts, w0 in (([(tx - 100, 800), (tx - 170, 826), (tx - 250, 836)], 40),
                    ([(tx + 70, 800), (tx + 120, 830), (tx + 200, 846)], 44),
                    ([(tx + 330, 800), (tx + 400, 818), (tx + 480, 824)], 34),
                    ([(tx - 330, 800), (tx - 390, 816), (tx - 460, 820)], 30)):
        _ground_root(g, pts, w0, 10)
    _rubble(g, 230, 850, 4, 0.8, 854)
    _block(g, 1840, 900, 130, 66, -0.12, STONE, 855)
    _block(g, 380, 1010, 160, 80, 0.06, STONE, 856)


@extra
def _preah_khan(ctx, layer, t, tod):
    view = str(_param("view", "corridor"))
    if view == "roots":
        hz = 640
        if layer == "SKY":
            _sky(ctx, t, tod, hz, ncloud=4)
            _maybe_birds(ctx, t, tod, n=4, y0=60, y1=260)
        elif layer == "BG":
            _cached(ctx, ("pk_roots", "BG"), lambda g: _forest_back(g, 23, hz))
        elif layer == "MG":
            _cached(ctx, ("pk_roots", "MG"), _pk_gallery)
            _shafts(ctx, t, [(1500, 110, 0.13, -380), (300, 80, 0.09, -300)])
        elif layer == "GROUND":
            _cached(ctx, ("pk_roots", "GROUND"), _pk_roots_ground)
            _dapple(ctx, t, 800, 1080, 15, 20, 0.2)
        elif layer == "FG":
            _cached(ctx, ("pk_roots", "FG"), lambda g: (_fern(g, -30, 1110, 1.4, 0, "#2f7a30", 861, 7),
                                                         _fern(g, 2000, 1120, 1.2, 0, "#2f7a30", 862, 6)))
            _liana(ctx, 120, -40, 300, t, 7)
    else:  # corridor
        if layer == "SKY":
            ctx.new_path()
            ctx.rectangle(B.X0, -300, B.X1 - B.X0, 1700)
            src(ctx, "#3d342a")
            ctx.fill()
        elif layer == "MG":
            _cached(ctx, ("pk_corr", "MG"), _pk_enfilade)
        elif layer == "GROUND":
            _cached(ctx, ("pk_corr", "GROUND"), _pk_room)
            k = 0.22 * (0.85 + 0.15 * math.sin(t * 0.35))
            ctx.new_path()
            poly_path(ctx, [(1140, 130), (1330, 200), (1720, 960), (1390, 1000)])
            ctx.set_source(lin_grad(0, 80, 0, 1000, [(0, (1, 0.96, 0.8, k)), (1, (1, 0.96, 0.8, k * 0.25))]))
            ctx.fill()
            ctx.save()
            ctx.translate(1520, 930)
            ctx.scale(1, 0.25)
            ctx.new_path()
            ctx.arc(0, 0, 230, 0, 2 * math.pi)
            ctx.set_source(rad_grad(0, 0, 0, 230, [(0, (1, 0.96, 0.8, 0.35)), (1, (1, 0.96, 0.8, 0.0))]))
            ctx.fill()
            ctx.restore()
            _pk_motes(ctx, t)
        elif layer == "FG":
            _cached(ctx, ("pk_corr", "FG"), lambda g: (_block(g, 60, 1130, 260, 120, 0.05, "#8f8164", 871),
                                                        _block(g, 1900, 1140, 220, 110, -0.08, "#8f8164", 872)))


# =========================================================================== guardians & water pieces

def _naga_hood(ctx, x, base, h, col=STONE, ol=BOL):
    """Seven-headed rearing naga seen from the front, (x, base) = where the body rises from the balustrade."""
    s = h / 100.0
    ctx.save()
    ctx.translate(x, base)
    ctx.scale(s, s)
    w = ol / s
    lt = shade(col, 0.12)
    dk = shade(col, -0.4)
    cy = -50
    ctx.new_path()  # halo / hood behind the heads, flame-edged
    n = 15
    for k in range(n + 1):
        off = (k / n - 0.5) * 2.6
        for rr, da in ((50, -0.05), (57, 0.04)):
            ctx.line_to(math.sin(off + da) * rr, cy - math.cos(off + da) * rr)
    ctx.line_to(0, cy + 6)
    ctx.close_path()
    fill_stroke(ctx, shade(col, -0.08), w * 0.8)
    ctx.new_path()  # rearing neck
    ctx.move_to(-14, 2)
    ctx.curve_to(-17, -18, -12, -32, -10, cy + 6)
    ctx.line_to(10, cy + 6)
    ctx.curve_to(12, -32, 17, -18, 14, 2)
    ctx.close_path()
    fill_stroke(ctx, col, w)
    rrect(ctx, -6, cy + 8, 12, -cy - 8, 5, lt, w * 0.6)
    ctx.new_path()
    for k in range(1, 7):
        ctx.move_to(-6, -k * 6)
        ctx.line_to(6, -k * 6)
    src(ctx, dk, 0.5)
    ctx.set_line_width(w * 0.4)
    ctx.stroke()
    for i in (0, 6, 1, 5, 2, 4, 3):  # seven cobra heads fanning out
        off = (i - 3) * 0.37
        L = 40 if i != 3 else 44
        dx, dy = math.sin(off), -math.cos(off)
        hx, hy = dx * L, cy + dy * L
        _taper(ctx, [(dx * 4, cy + 6), (dx * L * 0.55, cy + dy * L * 0.55), (hx - dx * 6, hy - dy * 6)], 11, 9, col,
               w * 0.8, 4)
        ctx.save()
        ctx.translate(hx, hy)
        ctx.rotate(off)
        poly(ctx, [(-3, 4), (0, 12), (3, 4)], col, w * 0.5)  # crest behind
        blob(ctx, [(-6.5, 6), (-7, -3), (-4.5, -11), (0, -14), (4.5, -11), (7, -3), (6.5, 6)], lt, w * 0.7)
        circle(ctx, -3.6, -5, 1.7, dk, 0)
        circle(ctx, 3.6, -5, 1.7, dk, 0)
        curve(ctx, (-3, -11), (0, -9.5), (3, -11), w * 0.4, dk)
        ctx.restore()
    ctx.restore()


def _lion(ctx, x, base, h, col=STONE, ol=BOL, facing=1):
    """Khmer guardian lion (singha) sitting upright, seen from the front, (x, base) = bottom centre."""
    s = h / 100.0
    ctx.save()
    ctx.translate(x, base)
    ctx.scale(s * facing, s)
    w = ol / s
    lt = shade(col, 0.12)
    dk = shade(col, -0.4)
    curve(ctx, (14, -14), (40, -30), (30, -62), 7 + 2 * w, OUTLINE)  # tail
    curve(ctx, (14, -14), (40, -30), (30, -62), 7, col)
    circle(ctx, 30, -64, 6, lt, w * 0.7)
    for sd in (-1, 1):  # haunches
        ellipse(ctx, sd * 17, -14, 15, 14, shade(col, -0.05), w)
    blob(ctx, [(-19, -4), (19, -4), (22, -40), (14, -62), (-14, -62), (-22, -40)], col, w)  # chest
    ellipse(ctx, 0, -40, 10, 16, lt, 0)
    for sd in (-1, 1):  # front legs and paws
        rrect(ctx, sd * 9.5 - 4.5, -46, 9, 44, 4, col, w * 0.8)
        ellipse(ctx, sd * 9.5, -3, 7, 4, lt, w * 0.7)
    for k in range(14):  # curly mane
        a = k * 2 * math.pi / 14
        circle(ctx, math.cos(a) * 21, -76 + math.sin(a) * 19, 6.5, shade(col, -0.08 + 0.06 * (k % 2)), w * 0.7)
    ellipse(ctx, 0, -76, 17, 15, col, w)
    for sd in (-1, 1):
        ellipse(ctx, sd * 6.5, -80, 4.2, 3.4, "#e8e0cc", w * 0.6)
        circle(ctx, sd * 6.5, -80, 1.7, dk, 0)
        curve(ctx, (sd * 11, -86), (sd * 6, -90), (sd * 1.5, -86), w * 0.8, dk)
    ellipse(ctx, 0, -73, 6, 3.6, shade(col, -0.15), w * 0.6)
    ellipse(ctx, 0, -66, 9, 4.6, "#4a3a2c", w * 0.6)  # open mouth
    for sd in (-1, 1):
        poly(ctx, [(sd * 6, -68), (sd * 4, -64), (sd * 2.5, -68)], "#f0e8d4", 0)
    ctx.restore()


WATER = {"day": ("#a9d8ee", "#3f8fc4"), "morning": ("#c4e4f0", "#4d98c6"), "interior": ("#a9d8ee", "#3f8fc4"),
         "evening": ("#f2b38a", "#5b5b92"), "sunset": ("#ffbe6e", "#4a3f80"), "sunrise": ("#ffc890", "#5a6aa8"),
         "night": ("#2b4677", "#0c1736"), "ancient": ("#a9d8ee", "#3f8fc4")}


def _water_fill(ctx, tod, y0, y1, mid=None):
    top, bot = WATER.get(tod, WATER["day"])
    ctx.new_path()
    ctx.rectangle(B.X0 - 100, y0, B.X1 - B.X0 + 200, y1 - y0)
    stops = [(0, top), (1, bot)] if mid is None else [(0, top), (mid, mix(top, bot, 0.55)), (1, bot)]
    ctx.set_source(lin_grad(0, y0, 0, min(y1, 1100), stops))
    ctx.fill()


def _ripples(ctx, t, tod, y0, y1, n=110, seed=3, flow=0.0, a=0.38, x0=None, x1=None):
    """Short horizontal ripple strokes, longer/thicker nearer; flow (px/s at the bottom) scrolls them left."""
    r = rng(seed)
    col = "#ffe6c0" if _warm(tod) else ("#9fb6e0" if _night(tod) else "#ffffff")
    x0 = B.X0 - 200 if x0 is None else x0
    x1 = B.X1 + 200 if x1 is None else x1
    span = x1 - x0
    for band in range(3):
        ctx.new_path()
        for i in range(n // 3):
            u = (band + r.random()) / 3.0
            y = y0 + 4 + (y1 - y0 - 4) * u ** 1.6
            L = 10 + 120 * u
            sp = flow * (0.1 + 0.9 * u)
            x = (r.uniform(0, span) - t * sp + math.sin(t * 0.8 + i) * 6 * (0.3 + u)) % span + x0
            ctx.move_to(x, y)
            ctx.line_to(x + L, y)
        src(ctx, col, a)
        ctx.set_line_width(1.4 + band * 1.2)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()


def _sun_path(ctx, t, tod, sx, y0, y1, n=90, seed=21):
    """Golden glitter path on the water under a low sun."""
    col = "#ffe08a" if _warm(tod) else "#fffbe8"
    ctx.save()
    ctx.translate(sx, y0)
    ctx.scale(1, 0.18)
    ctx.new_path()
    ctx.arc(0, 0, 420, 0, 2 * math.pi)
    c = hexc(col)
    ctx.set_source(rad_grad(0, 0, 0, 420, [(0, c + (0.55,)), (1, c + (0.0,))]))
    ctx.fill()
    ctx.restore()
    r = rng(seed)
    for i in range(n):
        u = r.random()
        y = y0 + 3 + (y1 - y0) * u ** 1.25
        hw = 16 + (y - y0) * 0.5
        dx = r.gauss(0, 0.42) * hw
        L = 14 + 70 * u
        k = clamp(1 - abs(dx) / (hw * 1.3), 0, 1) * (0.55 + 0.45 * math.sin(t * 2.0 + i * 1.7))
        if k > 0.02:
            line(ctx, [(sx + dx - L / 2, y), (sx + dx + L / 2, y)], 2 + 3.5 * u, col, 0.85 * k)


def _reflect(ctx, rec, axis, alpha, tint, y0, y1):
    """Mirror a recorded drawing about y = axis into the water band y0..y1, tinted towards the water colour."""
    ctx.save()
    ctx.new_path()
    ctx.rectangle(B.X0 - 200, y0, B.X1 - B.X0 + 400, y1 - y0)
    ctx.clip()
    ctx.push_group()
    ctx.translate(0, 2 * axis)
    ctx.scale(1, -1)
    ctx.set_source_surface(rec, 0, 0)
    ctx.paint()
    ctx.identity_matrix() if False else None
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha)
    ctx.new_path()
    ctx.rectangle(B.X0 - 200, y0, B.X1 - B.X0 + 400, y1 - y0)
    src(ctx, tint, 0.18)
    ctx.fill()
    ctx.restore()


def _shore(g, y, seed, col="#4f7d4a", palms=True, x0=None, x1=None, scale=1.0):
    """Low far tree line sitting on y."""
    r = rng(seed)
    x0 = B.X0 - 200 if x0 is None else x0
    x1 = B.X1 + 200 if x1 is None else x1
    g.new_path()
    g.rectangle(x0, y - 8 * scale, x1 - x0, 10 * scale)
    src(g, col)
    g.fill()
    x = x0
    while x < x1:
        _clump(g, x, y - r.uniform(6, 16) * scale, r.uniform(10, 24) * scale, shade(col, r.uniform(-0.1, 0.12)),
               seed + int(x), ol=0, hi=0.08, n=4)
        x += r.uniform(14, 34) * scale
    if palms:
        for k in range(int((x1 - x0) / 160)):
            px = r.uniform(x0, x1)
            B.sugar_palm(g, px, y - 4, r.uniform(40, 80) * scale, 0.0, shade(col, 0.05), 0)


# =========================================================================== srah srang

SS_VY, SS_H = 560, 230


def _ss(X, z):
    return (960 + X / z, SS_VY + SS_H / z)


def _ss_far(g, tod):
    hz = 584
    _water_fill(g, tod, hz - 2, 1300, 0.35)
    rec = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, None)
    rg = cairo.Context(rec)
    dark = _warm(tod)
    col = "#3f5a46" if dark else "#507e4a"
    _shore(rg, hz, 401, col, True)
    for x, h in ((-260, 120), (380, 150), (820, 110), (1600, 140), (2150, 130)):  # a few taller trees
        _clump(rg, x, hz - h * 0.6, h * 0.45, shade(col, 0.06), 402 + x, ol=0)
    blob(rg, [(1180, hz + 10), (1210, hz - 6), (1290, hz - 10), (1330, hz + 10)], "#8a9a5a", 0)  # the islet
    for k, (ix, ih) in enumerate(((1235, 40), (1262, 52), (1296, 36))):
        _clump(rg, ix, hz - ih, ih * 0.5, shade(col, 0.1), 410 + k, ol=0)
    _reflect(g, rec, hz, 0.4, WATER.get(tod, WATER["day"])[1], hz, hz + 140)
    g.set_source_surface(rec, 0, 0)
    g.paint()


def _ss_balustrade_pts(X, z0, z1, n):
    zs = [z0 + (z1 - z0) * k / (n - 1) for k in range(n)]
    return zs


def _ss_balustrade(g, X, z0, z1, hood=True, col=STONE):
    zs = [z0 + (z1 - z0) * k / 15.0 for k in range(16)]
    for z in reversed(zs):  # dwarf posts
        x, y = _ss(X, z)
        rrect(g, x - 9 / z, y - 40 / z, 18 / z, 40 / z, 3, shade(col, -0.05), BOL)
        rrect(g, x - 12 / z, y - 44 / z, 24 / z, 7 / z, 2, shade(col, 0.08), BOL * 0.8)
    pts = [(_ss(X, z)[0], _ss(X, z)[1] - 56 / z) for z in zs]
    ws = [30 / z for z in zs]
    L, R = _tube(g, pts, ws, col, BOL)
    g.new_path()  # scale marks along the naga body
    for i in range(len(pts) - 1):
        (xa, ya), (xb, yb) = pts[i], pts[i + 1]
        for k in range(3):
            u = (k + 0.5) / 3
            xm, ym = lerp(xa, xb, u), lerp(ya, yb, u)
            wm = lerp(ws[i], ws[i + 1], u)
            g.move_to(xm - wm * 0.25, ym - wm * 0.1)
            g.line_to(xm, ym + wm * 0.15)
            g.line_to(xm + wm * 0.25, ym - wm * 0.1)
    src(g, shade(col, -0.3), 0.55)
    g.set_line_width(1.6)
    g.stroke()
    line(g, [(p[0], p[1] - w * 0.28) for p, w in zip(pts, ws)], 2.5, shade(col, 0.25), 0.8)
    if hood:
        x, y = pts[-1]
        _naga_hood(g, x, y + 14, 190, col)


def _ss_terrace(g, near_only=False):
    col = "#cbbd9b"
    if not near_only:
        g.new_path()  # grassy bank beside the landing
        g.rectangle(B.X0 - 100, 788, B.X1 - B.X0 + 200, 600)
        g.set_source(lin_grad(0, 788, 0, 1080, [(0, "#8db060"), (1, "#6f9a48")]))
        g.fill()
        _tufts(g, 800, 1080, 50, 431, "#4c7f35", s0=0.6, s1=1.4)
        a, b, c, d = _ss(-620, 1.0), _ss(620, 1.0), _ss(620, 0.42), _ss(-620, 0.42)
        g.new_path()
        poly_path(g, [(a[0], a[1]), (b[0], b[1]), c, d])
        g.set_source(lin_grad(0, 790, 0, 1080, [(0, col), (1, "#b4a582")]))
        g.fill_preserve()
        g.save()
        g.clip()
        g.new_path()
        for k in range(-7, 8):
            p0, p1 = _ss(k * 88, 1.0), _ss(k * 88, 0.42)
            g.move_to(*p0)
            g.line_to(*p1)
        iz = 1.0
        while iz > 0.42:
            p0, p1 = _ss(-700, iz), _ss(700, iz)
            g.move_to(*p0)
            g.line_to(*p1)
            iz = 1 / (1 / iz + 0.22)
        src(g, "#8f8164", 0.55)
        g.set_line_width(1.8)
        g.stroke()
        _weather(g, -600, 790, 2500, 1100, 433, 0.12, moss=False)
        g.restore()
        line(g, [_ss(-620, 1.0), _ss(620, 1.0)], 3, OUTLINE)
        # stone steps going down to the water between the stair cheek walls
        y = _ss(0, 1.0)[1]
        for i in range(5):  # treads (light) and risers (shadow) seen over the edge
            z = 1.0 + 0.03 * (i + 1)
            xl, xr = _ss(-330, z)[0], _ss(330, z)[0]
            rrect(g, xl, y - 6, xr - xl, 6, 1, shade(col, 0.12 - 0.04 * i), 1.4)
            rrect(g, xl, y - 9, xr - xl, 3, 0, shade(col, -0.3), 0)
            y -= 9
        xl, xr = _ss(-330, 1.18)[0], _ss(330, 1.18)[0]
        line(g, [(xl + 6, y + 1), (xr - 6, y + 1)], 3, "#ffffff", 0.7)
        for sd in (-1, 1):  # guardian lions at the top of the steps
            x, y = _ss(sd * 470, 0.97)
            rrect(g, x - 44, y - 34, 88, 34, 3, shade(STONE, 0.05), BOL)
            rrect(g, x - 38, y - 44, 76, 12, 3, shade(STONE, 0.12), BOL * 0.8)
            _lion(g, x, y - 44, 170, STONE, BOL, 1)
        for sd in (-1, 1):
            _ss_balustrade(g, sd * 640, 0.42, 1.0, True)
    else:
        for sd in (-1, 1):
            _ss_balustrade(g, sd * 640, 0.42, 0.56, False)


def _ss_over(g):
    g.save()
    g.new_path()
    g.rectangle(B.X0, 930, B.X1 - B.X0, 400)
    g.clip()
    _ss_terrace(g, near_only=True)
    g.restore()


def _ss_branch(ctx, t):
    sw = math.sin(t * 0.7) * 6
    _taper(ctx, [(-160, -60), (60, 40), (260, 60 + sw * 0.5), (420, 40 + sw)], 46, 10, "#6a4e36", BOL)
    r = rng(441)
    for k in range(14):
        u = r.uniform(0.15, 1.0)
        x = lerp(-120, 430, u) + sw * u
        y = lerp(-20, 50, u) + r.uniform(-30, 70)
        _clump(ctx, x, y, r.uniform(26, 44), ("#4f8c45", "#5a9a4a", "#3f7a3f")[k % 3], 442 + k, ol=1.8)
    for k in range(5):
        u = r.uniform(0.3, 1.0)
        flower(ctx, lerp(-100, 420, u) + sw * u, r.uniform(20, 110), 11, "#ffffff", "#f7d23e", 1.2)


@extra
def _srah_srang(ctx, layer, t, tod):
    hz = 584
    if layer == "SKY":
        _sky(ctx, t, tod, hz, ncloud=8)
        _maybe_birds(ctx, t, tod, n=6, y0=80, y1=380)
    elif layer == "BG":
        _cached(ctx, ("ss", "BG", tod), lambda g: _ss_far(g, tod))
    elif layer == "MG":
        _ripples(ctx, t, tod, hz + 4, 800, 90, 451, 0.0, 0.32)
        _cached(ctx, ("ss", "MG"), lambda g: [B.lotus(g, x, y, s_, bloom=b) for x, y, s_, b in
                                               ((180, 770, 0.8, True), (330, 782, 0.6, False), (1620, 776, 0.7, True),
                                                (1760, 784, 0.9, False), (1500, 760, 0.5, False))])
    elif layer == "GROUND":
        _cached(ctx, ("ss", "GROUND"), _ss_terrace)
    elif layer == "OVER":
        _cached(ctx, ("ss", "OVER"), _ss_over)
    elif layer == "FG":
        _ss_branch(ctx, t)


# =========================================================================== west baray

BOAT = dict(x0=330, x1=1810, gun=850, far=806, wl=928)


def _boat_bob(t):
    return math.sin(t * 1.7) * 1.6


def _boat_inner(ctx, t, canopy=False):
    b = BOAT
    x0, x1, gy, fy, wl = b["x0"], b["x1"], b["gun"], b["far"], b["wl"]
    ctx.save()
    ctx.translate(0, _boat_bob(t))
    if canopy:
        for px in (330, 1000, 1640):
            rrect(ctx, px - 6, 466, 12, fy - 466, 3, "#8a5a36", BOL * 0.8)
        _boat_roof(ctx)
    ctx.new_path()
    ctx.move_to(x0 + 22, fy + 4)
    ctx.line_to(1540, fy)
    ctx.curve_to(1680, fy - 4, 1760, gy - 60, x1, gy - 92)
    ctx.curve_to(1770, gy - 44, 1680, gy, 1540, gy)
    ctx.line_to(x0, gy - 6)
    ctx.close_path()
    ctx.set_source(lin_grad(0, fy, 0, gy, [(0, "#7a4e30"), (1, "#4e3020")]))
    ctx.fill_preserve()
    fill_stroke(ctx, None, BOL)
    ctx.new_path()
    for k in range(1, 4):
        yy = fy + (gy - fy) * k / 4.0
        ctx.move_to(x0 + 20, yy)
        ctx.line_to(1560, yy - 2)
    src(ctx, "#3a2416", 0.6)
    ctx.set_line_width(2)
    ctx.stroke()
    for xx in (470, 680, 890, 1100, 1310, 1520):  # thwarts (seats)
        poly(ctx, [(xx - 46, fy + 8), (xx + 46, fy + 8), (xx + 54, gy), (xx - 54, gy)], "#b8834f", BOL * 0.8)
        line(ctx, [(xx - 44, fy + 12), (xx + 44, fy + 12)], 2.5, "#d9a86a", 0.9)
    line(ctx, [(x0 + 22, fy + 4), (1540, fy), ], 10 + 2 * BOL, OUTLINE)  # far gunwale rail
    line(ctx, [(x0 + 22, fy + 4), (1540, fy)], 10, "#8a5a36")
    curve(ctx, (1540, fy), (1720, fy - 10), (x1 - 6, gy - 90), 10 + 2 * BOL, OUTLINE)
    curve(ctx, (1540, fy), (1720, fy - 10), (x1 - 6, gy - 90), 10, "#8a5a36")
    ctx.restore()


def _boat_roof(ctx):
    pat_cols = ("#2f7fb8", "#f4f1e8")
    ctx.new_path()
    ctx.move_to(250, 486)
    ctx.curve_to(700, 452, 1200, 452, 1700, 486)
    ctx.line_to(1700, 452)
    ctx.curve_to(1200, 418, 700, 418, 250, 452)
    ctx.close_path()
    fill_stroke(ctx, pat_cols[0], BOL)
    ctx.save()
    ctx.clip()
    for k in range(12):
        x = 250 + k * 125
        ctx.new_path()
        ctx.rectangle(x, 400, 62, 100)
        src(ctx, pat_cols[1])
        ctx.fill()
    ctx.restore()
    ctx.new_path()
    ctx.move_to(250, 486)
    ctx.curve_to(700, 452, 1200, 452, 1700, 486)
    fill_stroke(ctx, None, BOL)
    for k in range(13):
        x = 260 + k * 112
        y = 486 - 34 * math.sin(math.pi * (x - 250) / 1450) * 0.95
        circle(ctx, x, y + 6, 6, pat_cols[0], 1.6)


def _boat_hull(ctx, t, flow=0.0, canopy=False):
    b = BOAT
    x0, x1, gy, wl = b["x0"], b["x1"], b["gun"], b["wl"]
    ctx.save()
    ctx.translate(0, _boat_bob(t))
    if canopy:
        for px in (300, 1690):
            rrect(ctx, px - 7, 470, 14, gy - 470, 3, "#8a5a36", BOL * 0.8)

    def top_edge():
        ctx.move_to(x0, gy - 6)
        ctx.line_to(1540, gy)
        ctx.curve_to(1680, gy - 2, 1770, gy - 40, x1, gy - 92)

    def hull_path():
        ctx.new_path()
        top_edge()
        ctx.curve_to(1780, gy - 30, 1700, wl - 6, 1560, wl)
        ctx.line_to(x0 + 26, wl)
        ctx.curve_to(x0 + 6, wl - 4, x0, wl - 20, x0, gy + 30)
        ctx.close_path()
    hull_path()
    ctx.set_source(lin_grad(0, gy, 0, wl, [(0, "#a06a40"), (1, "#7a4a2a")]))
    ctx.fill()
    ctx.save()
    hull_path()
    ctx.clip()
    ctx.new_path()
    for k in range(1, 4):  # planks
        ctx.save()
        ctx.translate(0, 18 + k * 16)
        top_edge()
        ctx.restore()
    src(ctx, "#5e3a22", 0.7)
    ctx.set_line_width(2)
    ctx.stroke()
    ctx.save()  # painted band
    ctx.translate(0, 20)
    ctx.new_path()
    top_edge()
    ctx.restore()
    src(ctx, "#2f86b8")
    ctx.set_line_width(18)
    ctx.stroke()
    ctx.save()
    ctx.translate(0, 31)
    ctx.new_path()
    top_edge()
    ctx.restore()
    src(ctx, "#f4f1e8")
    ctx.set_line_width(4)
    ctx.stroke()
    ctx.new_path()  # red boot stripe at the waterline
    ctx.rectangle(x0 - 10, wl - 14, 1600, 14)
    src(ctx, "#c0442e")
    ctx.fill()
    ctx.restore()
    hull_path()
    fill_stroke(ctx, None, BOL)
    ctx.new_path()  # gunwale rail
    top_edge()
    src(ctx, OUTLINE)
    ctx.set_line_width(12 + 2 * BOL)
    ctx.stroke()
    ctx.new_path()
    top_edge()
    src(ctx, "#7a4a2a")
    ctx.set_line_width(12)
    ctx.stroke()
    circle(ctx, x1 - 70, gy - 52, 9, "#f4f1e8", 1.6)  # bow eye
    circle(ctx, x1 - 70, gy - 52, 4, OUTLINE, 0)
    # outboard motor on the stern
    mx = x0 - 40
    line(ctx, [(mx + 10, gy - 10), (mx - 120, wl + 16)], 11 + 2 * BOL, OUTLINE)
    line(ctx, [(mx + 10, gy - 10), (mx - 120, wl + 16)], 11, "#5a6270")
    rrect(ctx, mx - 34, gy - 74, 92, 64, 20, "#3e4c62", BOL)
    rrect(ctx, mx - 24, gy - 66, 40, 16, 8, "#6c7f9c", 0)
    rrect(ctx, mx + 4, gy - 16, 50, 20, 5, "#2b3442", BOL * 0.8)
    line(ctx, [(mx + 40, gy - 40), (mx + 150, gy - 58)], 6 + 2 * BOL, OUTLINE)  # tiller
    line(ctx, [(mx + 40, gy - 40), (mx + 150, gy - 58)], 6, "#2b3442")
    # water against the hull, bow wave, prop wash and wake
    ph = t * (2.0 + flow * 0.01)
    ctx.new_path()
    for k in range(60):
        x = x0 + 4 + k * (1560 - x0) / 59.0
        y = wl - 2 + math.sin(x * 0.05 + ph * 3) * 2.5
        (ctx.move_to if k == 0 else ctx.line_to)(x, y)
    src(ctx, "#ffffff", 0.85)
    ctx.set_line_width(5)
    ctx.stroke()
    if flow > 0:
        for k in range(6):
            u = ((t * 1.3 + k / 6.0) % 1.0)
            bx = 1600 + u * 120
            by = wl - 8 - math.sin(u * math.pi) * 26
            ellipse(ctx, bx, by, 14 * (1 - u * 0.5), 8 * (1 - u * 0.5), "#ffffff", 0)
        r = rng(470)
        for k in range(26):  # wake: foam blobs streaming away behind the motor
            u = ((r.random() + t * flow / 1400.0) % 1.0)
            side = 1 if k % 2 else -1
            wx = mx - 120 - u * 900
            wy = wl + 16 + side * u * (60 if side > 0 else 34) + math.sin(t * 3 + k) * 2
            a = 0.85 * (1 - u)
            ctx.new_path()
            ellipse_path(ctx, wx, wy, 26 * (1 - u * 0.4), 7 * (1 - u * 0.3))
            src(ctx, "#ffffff", a)
            ctx.fill()
        for k in range(8):  # churning foam at the propeller
            a_ = t * 9 + k * 0.8
            circle(ctx, mx - 120 + math.cos(a_) * 20, wl + 16 + math.sin(a_) * 6, 9 + (k % 3) * 3, "#ffffff", 0)
    ctx.restore()


def _mebon_tower(g, cx, base, w, col, seed, cut=None):
    """Small sandstone gate tower: body with door, three tiers and a lotus top; cut = jagged ruin height."""
    g.save()
    if cut is not None:
        r = rng(seed)
        pts = [(cx - w * 1.4, base + 10), (cx - w * 1.4, cut + r.uniform(-10, 10))]
        x = cx - w * 1.4
        while x < cx + w * 1.4:
            x += w * r.uniform(0.15, 0.35)
            pts.append((x, cut + r.uniform(-w * 0.3, w * 0.3)))
        pts.append((cx + w * 1.4, base + 10))
        g.new_path()
        poly_path(g, pts)
        g.clip()
    bh = w * 1.5
    _stone_rect(g, cx - w / 2, base - bh, w, bh, col, seed, max(6, w * 0.12), BOL * 0.8, 1.0)
    rrect(g, cx - w * 0.16, base - bh * 0.62, w * 0.32, bh * 0.62, 1, VOID, BOL * 0.6)
    rrect(g, cx - w * 0.6, base - bh - w * 0.1, w * 1.2, w * 0.12, 1, shade(col, 0.08), BOL * 0.7)
    yb = base - bh - w * 0.1
    for i, k in enumerate((0.86, 0.7, 0.54)):
        hh = w * 0.3
        rrect(g, cx - w * k / 2, yb - hh, w * k, hh, 1, shade(col, 0.03 * i), BOL * 0.7)
        rrect(g, cx - w * k * 0.56, yb - hh - w * 0.06, w * k * 1.12, w * 0.07, 1, shade(col, 0.08), BOL * 0.6)
        yb -= hh + w * 0.06
    A.prang(g, cx, yb, w * 0.2, w * 0.55, shade(col, 0.05), BOL * 0.7, detail=False)
    g.restore()


def _mebon_island(g, cx, wy, dark=False):
    col = STONE if not dark else "#7d6a72"
    lc = ("#4f8c45", "#5a9a4a", "#3f7a3f") if not dark else ("#3a4f40", "#43594a", "#33463a")
    r = rng(480)
    for k in range(9):
        B.sugar_palm(g, cx + r.uniform(-480, 480), wy - 20, r.uniform(180, 250), 0.0, lc[k % 3], BOL * 0.7)
    for k in range(26):
        _clump(g, cx + r.uniform(-500, 500), wy - r.uniform(60, 190), r.uniform(50, 90), lc[k % 3], 481 + k, ol=2.0)
    g.new_path()  # beach
    g.move_to(cx - 600, wy + 6)
    g.curve_to(cx - 560, wy - 22, cx - 300, wy - 26, cx, wy - 26)
    g.curve_to(cx + 300, wy - 26, cx + 560, wy - 22, cx + 600, wy + 6)
    g.close_path()
    fill_stroke(g, "#d8c496" if not dark else "#a08a7a", BOL)
    # enclosure wall with gaps
    for x0_, x1_, top in ((cx - 470, cx - 330, wy - 70), (cx - 300, cx - 60, wy - 74), (cx + 60, cx + 220, wy - 74),
                          (cx + 320, cx + 470, wy - 60)):
        _stone_rect(g, x0_, top, x1_ - x0_, wy - 16 - top, col, int(x0_), 12, BOL * 0.8, 1.2)
    for x0_, x1_ in ((cx - 330, cx - 300), (cx + 220, cx + 320)):
        poly(g, [(x0_, wy - 16), (x0_, wy - 50), (x0_ + 10, wy - 40), (x1_ - 10, wy - 34), (x1_, wy - 46), (x1_, wy - 16)],
             shade(col, -0.12), BOL * 0.7)
    _mebon_tower(g, cx, wy - 16, 74, col, 490)
    _mebon_tower(g, cx - 330, wy - 16, 60, col, 491, cut=wy - 120)
    _mebon_tower(g, cx + 300, wy - 16, 60, col, 492, cut=wy - 92)
    for k in range(5):
        _block(g, cx + r.uniform(-520, 520), wy - 2 + r.uniform(0, 8), r.uniform(26, 40), r.uniform(14, 22),
               r.uniform(-0.3, 0.3), col, 493 + k, ol=BOL * 0.7)


def _wb_jetty(g, tod):
    wood, dk = "#9a6a42", "#6a4428"
    def P(X, z):
        return (960 + X / z, 600 + 200 / z)
    z0, z1 = 1.0, 0.4
    a, b, c, d = P(-380, z0), P(380, z0), P(380, z1), P(-380, z1)
    for sd in (-1, 1):  # posts under the deck
        z = z0
        while z > z1:
            x, y = P(sd * 370, z)
            rrect(g, x - 9 / z * 0.5, y - 4, 18 / z * 0.5, 60 / z * 0.5 + 10, 2, dk, BOL * 0.7)
            z -= 0.12
    g.new_path()
    poly_path(g, [a, b, c, d])
    g.set_source(lin_grad(0, a[1], 0, 1080, [(0, "#b07c4e"), (1, wood)]))
    g.fill_preserve()
    g.save()
    g.clip()
    g.new_path()
    iz = z0
    while iz > z1 * 0.9:
        p0, p1 = P(-400, iz), P(400, iz)
        g.move_to(*p0)
        g.line_to(*p1)
        iz = 1 / (1 / iz + 0.09)
    src(g, "#5a3a22", 0.7)
    g.set_line_width(2.2)
    g.stroke()
    g.new_path()
    for X in (-190, 0, 190):
        p0, p1 = P(X, z0), P(X, z1)
        g.move_to(*p0)
        g.line_to(*p1)
    src(g, "#5a3a22", 0.35)
    g.set_line_width(1.6)
    g.stroke()
    g.restore()
    g.new_path()
    poly_path(g, [a, b, c, d])
    fill_stroke(g, None, BOL)
    for sd in (-1, 1):  # mooring posts
        for z in (1.0, 0.62):
            x, y = P(sd * 380, z)
            rrect(g, x - 8 / z * 0.6, y - 70 / z * 0.6, 16 / z * 0.6, 70 / z * 0.6 + 4, 3, wood, BOL)
            ellipse(g, x, y - 70 / z * 0.6, 8 / z * 0.6, 3 / z * 0.6, shade(wood, 0.2), BOL * 0.6)


def _wb_moored_boat(g):
    g.save()
    g.translate(1980, 872)
    g.scale(-0.55, 0.55)
    g.new_path()
    g.move_to(-700, -10)
    g.line_to(500, 0)
    g.curve_to(640, -4, 720, -60, 760, -110)
    g.curve_to(720, -30, 640, 70, 500, 80)
    g.line_to(-680, 80)
    g.curve_to(-700, 60, -704, 30, -700, -10)
    g.close_path()
    g.set_source(lin_grad(0, -10, 0, 80, [(0, "#a06a40"), (1, "#7a4a2a")]))
    g.fill_preserve()
    fill_stroke(g, None, BOL / 0.55)
    line(g, [(-690, 14), (520, 22)], 16, "#2f86b8")
    line(g, [(-700, -10), (500, 0)], 10, "#7a4a2a")
    g.restore()
    line(g, [(1590, 846), (1640, 880), (1600, 870)], 3, "#d8c08a")


def _wb_shore_band(g, y, tod, seed, period, island=None):
    dark = _warm(tod)
    col = "#40394f" if dark else "#5f8a5a"
    for off in (-period, 0, period):
        g.save()
        g.translate(off, 0)
        _shore(g, y, seed, col, True, B.X0, B.X0 + period, 0.9)
        if island:
            ix = island
            blob(g, [(ix - 110, y + 2), (ix - 80, y - 10), (ix + 80, y - 10), (ix + 110, y + 2)], col, 0)
            for k in range(5):
                _clump(g, ix - 70 + k * 35, y - 20 - (k % 2) * 10, 22, shade(col, 0.08), 600 + k, ol=0, n=4)
            A.prang(g, ix + 8, y - 8, 10, 40, mix(col, "#b0a080", 0.5), 0, detail=False)
        g.restore()


def _wb_low_sun(tod, hz):
    if tod == "sunset":
        return (1380, hz - 36)
    if tod == "sunrise":
        return (1380, hz - 30)
    if tod == "evening":
        return (1380, hz - 140)
    return None


def _wb_sunset_clouds(ctx, t, tod, hz):
    if not _warm(tod):
        return
    r = rng(611)
    for k in range(7):
        x = (r.uniform(B.X0, B.X1) + t * 3) % (B.X1 - B.X0) + B.X0
        y = r.uniform(120, hz - 160)
        w = r.uniform(160, 380)
        ctx.new_path()
        ellipse_path(ctx, x, y, w, r.uniform(10, 20))
        ellipse_path(ctx, x + w * 0.3, y - 10, w * 0.5, r.uniform(9, 16))
        src(ctx, ("#f6a07c", "#d77890", "#ffc48a")[k % 3], 0.75)
        ctx.fill()


@extra
def _west_baray(ctx, layer, t, tod):
    view = str(_param("view", "boat"))
    in_boat = bool(_param("boat", view == "boat"))
    canopy = bool(_param("canopy", False))
    moving = bool(_param("moving", view == "boat"))
    flow = 260.0 if moving else 0.0
    hz = 600
    if layer == "SKY":
        sun = _wb_low_sun(tod, hz) if view == "bank" else None
        _sky(ctx, t, tod, hz, ncloud=6, sun=sun, sun_r=64 if sun else 58, glow=420 if sun else 220)
        _wb_sunset_clouds(ctx, t, tod, hz)
        if B.CUR.get("birds") or (view == "bank" and _warm(tod)):
            A.birds(ctx, t, 6, 5, 150, 420, "#2b2530" if tod != "night" else "#0b0b12", 0.9)
    elif layer == "BG":
        if view == "boat":
            P = B.X1 - B.X0
            off = -((t * 6.0) % P) if moving else 0.0
            ctx.save()
            ctx.translate(off, 0)
            _cached(ctx, ("wb", "shore_boat", _warm(tod)), lambda g: _wb_shore_band(g, hz + 2, tod, 620, P, island=1500))
            ctx.restore()
        else:
            _cached(ctx, ("wb", "shore", view, _warm(tod)), lambda g: _shore(g, hz + 2, 621, "#40394f" if _warm(tod) else "#5f8a5a",
                                                                         True, None, None, 0.7))
    elif layer == "MG":
        if view == "mebon":
            wy = 650
            _cached(ctx, ("wb", "water", tod), lambda g: _water_fill(g, tod, hz + 2, 1300, 0.3))
            isl = _cached(ctx, ("wb", "island", _warm(tod)), lambda g: _mebon_island(g, 1000, wy, _warm(tod)))
            ctx.save()
            ctx.new_path()
            ctx.rectangle(B.X0, wy + 4, B.X1 - B.X0, 1300)
            ctx.clip()
            _reflect(ctx, isl, wy + 4, 0.33, WATER.get(tod, WATER["day"])[1], wy + 4, wy + 300)
            ctx.restore()
            _ripples(ctx, t, tod, hz + 4, 1100, 120, 631, 0.0, 0.34)
        else:
            _cached(ctx, ("wb", "water", tod), lambda g: _water_fill(g, tod, hz + 2, 1300, 0.3))
            sun = _wb_low_sun(tod, hz)
            if view == "bank" and sun:
                _sun_path(ctx, t, tod, sun[0], hz + 2, 800)
            elif view == "bank":
                _sun_path(ctx, t, tod, 1500, hz + 2, 800, 40)
            _ripples(ctx, t, tod, hz + 4, 1100, 140, 632, flow, 0.36)
            if view == "boat" and moving:  # floating water hyacinth drifting past
                r = rng(633)
                span = B.X1 - B.X0 + 600
                for k in range(5):
                    u = r.uniform(0.25, 1.0)
                    y = hz + 10 + 430 * u ** 1.5
                    x = (r.uniform(0, span) - t * flow * 0.6 * (0.1 + 0.9 * u)) % span + B.X0 - 300
                    for j in range(3):
                        ellipse(ctx, x + j * 22 * u, y - (j % 2) * 5 * u, 18 * u + 4, 6 * u + 2, "#4f9a46", 1.5)
                    flower(ctx, x + 20 * u, y - 10 * u, 6 * u + 2, "#c9a0e8", "#f7d23e", 1.0)
            if view == "bank":
                _cached(ctx, ("wb", "fishing", _warm(tod)), lambda g: B.boat(g, 1560, 662, 0.42, 0.0))
    elif layer == "GROUND":
        if in_boat:
            _boat_inner(ctx, t, canopy)
        elif view == "mebon":
            _cached(ctx, ("wb", "jetty"), lambda g: (_wb_moored_boat(g), _wb_jetty(g, tod)))
        elif view == "bank":
            _cached(ctx, ("wb", "bank", _warm(tod)), lambda g: _wb_bank(g, tod))
    elif layer == "OVER":
        if in_boat:
            _boat_hull(ctx, t, flow, canopy)
    elif layer == "FG":
        if view == "bank" and not in_boat:
            for x in (-60, -20, 1940, 1985):
                for k in range(5):
                    a = -1.95 + k * 0.2
                    sw = math.sin(t * 1.1 + k + x) * 8
                    line(ctx, [(x + k * 12, 1110), (x + k * 12 + math.cos(a) * 80 + sw, 1110 + math.sin(a) * 300)], 8,
                         "#3f6f2f" if not _warm(tod) else "#4a4a2f")


def _wb_bank(g, tod):
    warm = _warm(tod)
    g.new_path()  # slope down to the water
    g.move_to(B.X0 - 100, 776)
    g.curve_to(400, 770, 1400, 782, B.X1 + 100, 772)
    g.line_to(B.X1 + 100, 1300)
    g.line_to(B.X0 - 100, 1300)
    g.close_path()
    g.set_source(lin_grad(0, 772, 0, 820, [(0, "#5f8a45"), (1, "#7aa552")]))
    g.fill()
    line(g, [(B.X0, 778), (B.X1, 776)], 3, "#ffffff", 0.45)
    g.new_path()  # the dyke-top path
    g.move_to(B.X0 - 100, 812)
    g.curve_to(500, 804, 1400, 816, B.X1 + 100, 806)
    g.line_to(B.X1 + 100, 1300)
    g.line_to(B.X0 - 100, 1300)
    g.close_path()
    g.set_source(lin_grad(0, 806, 0, 1080, [(0, "#c38358"), (1, "#a96a42")]))
    g.fill()
    g.new_path()
    for y0 in (880, 960, 1030):
        g.move_to(B.X0, y0)
        g.curve_to(600, y0 - 8, 1300, y0 + 10, B.X1, y0 - 4)
    src(g, "#d9a27a", 0.6)
    g.set_line_width(6)
    g.stroke()
    _spots(g, B.X0, 820, B.X1, 1090, 80, 641, "#8f5636", 0.35, 3, 10, 0.6)
    _tufts(g, 790, 820, 70, 642, "#4c7f35", s0=0.6, s1=0.9)
    _tufts(g, 1050, 1090, 30, 643, "#4c7f35", s0=1.2, s1=1.5)
    crown = "#2f4a35" if warm else "#3f8f3a"
    for x, h in ((-380, 560), (150, 620), (1770, 650), (2200, 580)):
        B.sugar_palm(g, x, 814, h, 0.0, crown)


# =========================================================================== bayon faces, giants, garudas, elephants

def _bayon_face(ctx, cx, cy, s, col=STONE, seed=0, sx=1.0, ol=BOL, crown=True, detail=True):
    """Serene Angkor-Thom face (eyes closed, gentle smile) assembled from stone blocks.
    Unit face: ~256 wide with ears, crown top -152 .. chin +152; (cx, cy) = centre, s = scale."""
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s * sx, s)
    w = ol / s
    dk = shade(col, -0.4)
    mid = shade(col, -0.14)
    lt = shade(col, 0.12)
    for sd in (-1, 1):  # ears with long lobes and earrings
        blob(ctx, [(sd * 96, -62), (sd * 120, -58), (sd * 128, -12), (sd * 120, 44), (sd * 116, 94), (sd * 102, 104),
                   (sd * 96, 40), (sd * 92, -30)], shade(col, -0.07), w)
        if detail:
            curve(ctx, (sd * 104, -40), (sd * 118, -8), (sd * 106, 30), w * 0.8, dk)
        ellipse(ctx, sd * 110, 110, 8, 13, lt, w * 0.8)
    face = [(-104, -112), (0, -118), (104, -112), (110, -40), (104, 40), (86, 100), (50, 140), (0, 152),
            (-50, 140), (-86, 100), (-104, 40), (-110, -40)]
    ctx.new_path()
    smooth_path(ctx, face)
    src(ctx, col)
    ctx.fill()
    ctx.save()
    ctx.new_path()
    smooth_path(ctx, face)
    ctx.clip()
    ctx.new_path()
    ctx.rectangle(34, -130, 100, 300)
    ctx.set_source_rgba(0.08, 0.05, 0.02, 0.10)
    ctx.fill()
    for sd in (-1, 1):
        ctx.new_path()
        ellipse_path(ctx, sd * 46, -40, 38, 16)
        ctx.set_source_rgba(0.1, 0.07, 0.03, 0.12)
        ctx.fill()
    ellipse(ctx, -56, 28, 24, 16, shade(col, 0.07), 0)
    blob(ctx, [(-12, -58), (12, -58), (18, -4), (28, 16), (0, 28), (-28, 16), (-18, -4)], lt, 0)
    lw = w * (1.0 if detail else 1.6)
    for sd in (-1, 1):
        curve(ctx, (sd * 88, -52), (sd * 50, -84), (sd * 8, -62), lw * 1.2, dk)
        ctx.new_path()
        ctx.move_to(sd * 78, -38)
        ctx.curve_to(sd * 62, -52, sd * 34, -52, sd * 18, -38)
        ctx.curve_to(sd * 34, -30, sd * 62, -30, sd * 78, -38)
        src(ctx, mid)
        ctx.fill()
        curve(ctx, (sd * 78, -38), (sd * 48, -26), (sd * 18, -38), lw * 1.3, dk)
        if detail:
            curve(ctx, (sd * 74, -47), (sd * 48, -58), (sd * 22, -47), w * 0.6, mid)
            curve(ctx, (sd * 14, 4), (sd * 38, 22), (sd * 12, 30), w * 1.0, dk)
            curve(ctx, (sd * 70, 36), (sd * 80, 62), (sd * 68, 86), w * 0.8, mid)
    if detail:
        curve(ctx, (-10, 31), (0, 35), (10, 31), w * 0.8, dk)
        line(ctx, [(-5, 38), (-6, 52)], w * 0.6, mid)
        line(ctx, [(5, 38), (6, 52)], w * 0.6, mid)
    ctx.new_path()  # upper lip
    ctx.move_to(-56, 66)
    ctx.curve_to(-36, 58, -24, 53, -12, 56)
    ctx.curve_to(-6, 57, -3, 61, 0, 61)
    ctx.curve_to(3, 61, 6, 57, 12, 56)
    ctx.curve_to(24, 53, 36, 58, 56, 66)
    ctx.curve_to(30, 78, -30, 78, -56, 66)
    ctx.close_path()
    fill_stroke(ctx, mid, w * 0.7 if detail else 0)
    ctx.new_path()  # lower lip
    ctx.move_to(-56, 66)
    ctx.curve_to(-30, 78, 30, 78, 56, 66)
    ctx.curve_to(40, 88, 22, 98, 0, 98)
    ctx.curve_to(-22, 98, -40, 88, -56, 66)
    ctx.close_path()
    fill_stroke(ctx, shade(col, -0.04), w * 0.7 if detail else 0)
    curve(ctx, (-56, 66), (0, 80), (56, 66), lw * 1.3, dk)
    for sd in (-1, 1):  # smiling corners
        curve(ctx, (sd * 56, 66), (sd * 64, 63), (sd * 66, 55), lw, dk)
    curve(ctx, (-22, 124), (0, 133), (22, 124), w * 0.8, mid)
    _courses(ctx, -130, -64, 130, 160, 46, seed, dk, w * 0.9, 60, 150, 0.4)
    _weather(ctx, -120, -120, 120, 160, seed + 3, 2.0)
    ctx.restore()
    ctx.new_path()
    smooth_path(ctx, face)
    fill_stroke(ctx, None, w)
    if crown:  # diadem with floral medallions and pendants
        rrect(ctx, -116, -152, 232, 38, 5, shade(col, 0.04), w)
        for k in range(-3, 4):
            flower(ctx, k * 31, -133, 9, lt, mid, w * 0.5)
        for k in range(-4, 5):
            poly(ctx, [(k * 24 - 7, -114), (k * 24, -100), (k * 24 + 7, -114)], lt, w * 0.6)
    ctx.restore()


def _tier_ring(g, cx, yb, hw, h, col, seed=0, ol=BOL):
    rrect(g, cx - hw, yb - h, 2 * hw, h, 1, col, ol)
    _clip_rect(g, cx - hw, yb - h, 2 * hw, h)
    _courses(g, cx - hw, yb - h + h / 2, cx + hw, yb, h / 2, seed, shade(col, -0.35), 1.1, 16, 50, 0.5)
    _weather(g, cx - hw, yb - h, cx + hw, yb, seed + 1, 1.5)
    g.restore()
    _shade_right(g, cx + hw * 0.35, yb - h, hw * 0.65, h, 0.1)
    rrect(g, cx - hw * 1.06, yb - h - h * 0.16, hw * 2.12, h * 0.2, 1, shade(col, 0.08), ol * 0.8)
    for fx in (-0.88, 0.0, 0.88):
        A.prang(g, cx + fx * hw, yb - h - h * 0.1, hw * 0.11, h * 0.85, shade(col, 0.06), ol * 0.6, detail=False)


def _face_tower(g, cx, base, w, col=STONE, seed=0, kind="front", body=0.5, tiers=4, tier_h=0.15, lotus=0.4,
                ol=BOL, detail=True):
    """Bayon-style tower: body with a porch, big face(s) under a diadem, stepped tiers, lotus top. w = tower width."""
    s = w / 270.0
    bh = w * body
    if bh > 0:
        _stone_rect(g, cx - w * 0.52, base - bh, w * 1.04, bh, shade(col, -0.05), seed, max(6, w * 0.07), ol, 1.0)
        rrect(g, cx - w * 0.12, base - bh * 0.8, w * 0.24, bh * 0.8, 2, shade(col, -0.3), ol * 0.7)
        _pediment(g, cx, base - bh * 0.8, w * 0.36, bh * 0.45, shade(col, 0.02), ol * 0.8, inner=False)
    chin = base - bh
    fcy = chin - 152 * s
    top = chin - 300 * s
    rrect(g, cx - w * 0.6, top + 10 * s, w * 1.2, chin - top - 10 * s, 2, shade(col, -0.24), ol)
    if kind == "front":
        for sd in (-1, 1):
            _bayon_face(g, cx + sd * w * 0.5, fcy + 4 * s, s * 0.94, shade(col, -0.17), seed + sd, 0.26, ol, True, detail)
        _bayon_face(g, cx, fcy, s, col, seed, 1.0, ol, True, detail)
    else:  # corner view: two faces turned to the sides
        _bayon_face(g, cx - w * 0.3, fcy, s * 0.96, col, seed - 1, 0.6, ol, True, detail)
        _bayon_face(g, cx + w * 0.3, fcy, s * 0.96, shade(col, -0.13), seed + 1, 0.6, ol, True, detail)
    yb = top + 4 * s
    tw = w * 0.92
    for i in range(tiers):
        hh = w * tier_h
        _tier_ring(g, cx, yb, tw / 2, hh, shade(col, 0.03 * i), seed + 10 + i, ol)
        yb -= hh * 1.18
        tw *= 0.84
    if lotus:
        A.prang(g, cx, yb, tw * 0.36, w * lotus, shade(col, 0.05), ol, detail=False)
    return top


def _giant(g, x, base, h, kind="deva", view="front", col=STONE, part="body", ol=BOL):
    """Seated stone giant of the Angkor Thom causeways holding the naga. part "body" or "hands" (drawn over the naga).
    view "front" faces the camera, "side" faces left. (x, base) = bottom centre, h = height."""
    s = h / 100.0
    g.save()
    g.translate(x, base)
    g.scale(s, s)
    w = ol / s
    lt, dk, mid = shade(col, 0.1), shade(col, -0.42), shade(col, -0.12)
    asura = kind == "asura"
    if part == "hands":
        if view == "front":
            for sd in (-1, 1):
                ellipse(g, sd * 12, -40, 6, 5, lt, w * 0.8)
        else:
            ellipse(g, -26, -43, 6, 5, lt, w * 0.8)
        g.restore()
        return
    if view == "front":
        blob(g, [(-30, 0), (30, 0), (35, -14), (22, -31), (-22, -31), (-35, -14)], shade(col, -0.05), w)
        poly(g, [(-8, -31), (8, -31), (6, -6), (-6, -6)], lt, w * 0.6)
        blob(g, [(-16, -30), (16, -30), (22, -57), (14, -64), (-14, -64), (-22, -57)], col, w)
        curve(g, (-10, -52), (0, -47), (10, -52), w * 0.6, mid)
        for sd in (-1, 1):
            line(g, [(sd * 19, -58), (sd * 27, -45), (sd * 13, -40)], 8 + 2 * w, OUTLINE)
            line(g, [(sd * 19, -58), (sd * 27, -45), (sd * 13, -40)], 8, col)
        rrect(g, -5, -69, 10, 8, 2, col, w * 0.7)
        hx = 0
    else:
        blob(g, [(-34, 0), (16, 0), (22, -14), (14, -32), (-12, -34), (-32, -24)], shade(col, -0.05), w)
        line(g, [(5, -58), (-6, -50), (-20, -45)], 7 + 2 * w, OUTLINE)
        line(g, [(5, -58), (-6, -50), (-20, -45)], 7, shade(col, -0.14))
        blob(g, [(-10, -30), (16, -30), (14, -60), (0, -66), (-12, -60)], col, w)
        line(g, [(-2, -58), (-12, -48), (-26, -43)], 8 + 2 * w, OUTLINE)
        line(g, [(-2, -58), (-12, -48), (-26, -43)], 8, col)
        rrect(g, -7, -70, 9, 8, 2, col, w * 0.7)
        hx = -3
    if view == "front":
        for sd in (-1, 1):
            ellipse(g, sd * 10.5, -76, 2.6, 5, shade(col, -0.06), w * 0.6)
            ellipse(g, sd * 11, -66, 2.2, 4, lt, w * 0.5)
    else:
        ellipse(g, hx + 7, -76, 2.6, 5, shade(col, -0.06), w * 0.6)
    ellipse(g, hx, -76, 11 if asura else 10.5, 12.5, col, w)
    ex = [-4.6, 4.6] if view == "front" else [-7.5]
    if asura:
        for e in ex:
            circle(g, hx + e, -78, 2.8, "#e8e0cc", w * 0.5)
            circle(g, hx + e, -78, 1.3, dk, 0)
            line(g, [(hx + e * 1.9, -84), (hx + e * 0.45, -81)], w * 1.1, dk)
        curve(g, (hx - 8 - (3 if view != "front" else 0), -69), (hx, -72), (hx + 8, -69), w * 1.5, dk)
        for e in (-2.2, 2.2):
            poly(g, [(hx + e - 1.2, -67), (hx + e, -64), (hx + e + 1.2, -67)], "#f0e8d4", 0)
        blob(g, [(hx - 13, -82), (hx - 11, -92), (hx, -97), (hx + 11, -92), (hx + 13, -82)], mid, w * 0.8)
        rrect(g, hx - 13, -87, 26, 5, 2, lt, w * 0.6)
        for k in (-1, 0, 1):
            poly(g, [(hx + k * 7 - 3, -95 + abs(k) * 2), (hx + k * 8, -106 + abs(k) * 4), (hx + k * 7 + 3, -95 + abs(k) * 2)],
                 lt, w * 0.6)
    else:
        for e in ex:
            curve(g, (hx + e - 2.6, -78), (hx + e, -75.5), (hx + e + 2.6, -78), w * 0.9, dk)
        if view == "front":
            curve(g, (hx - 4, -68.5), (hx, -66.5), (hx + 4, -68.5), w * 0.9, dk)
        else:  # 3/4 face turned left: brow, far eye, broad nose, smile
            curve(g, (hx - 12, -82), (hx - 7, -85), (hx - 2, -82), w * 1.1, dk)
            curve(g, (hx - 0.5, -78), (hx + 1.5, -76.5), (hx + 3.5, -78), w * 0.8, dk)
            poly(g, [(hx - 8, -80), (hx - 14.5, -71.5), (hx - 8.5, -70)], lt, w * 0.7)
            curve(g, (hx - 12, -67.5), (hx - 8, -65), (hx - 3, -67.5), w * 1.1, dk)
            ellipse(g, hx + 2, -70, 3.5, 2.6, shade(col, 0.06), 0)
        for i, (hw_, y_) in enumerate(((11, -91), (9, -96), (7, -101), (5, -106))):
            rrect(g, hx - hw_, y_, hw_ * 2, 5.5, 2, lt if i % 2 == 0 else col, w * 0.6)
        poly(g, [(hx - 4, -105), (hx, -116), (hx + 4, -105)], lt, w * 0.6)
    g.restore()


def _naga_seg(g, a, b, wa, wb, col=STONE):
    """A piece of the naga body between two grip points (tube with scale chevrons and a lighter belly)."""
    pts = [a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + abs(a[0] - b[0]) * 0.04), b]
    sp = _spline(pts, 5)
    k = len(sp) - 1
    ws = [wa + (wb - wa) * i / k for i in range(k + 1)]
    L, R = _tube(g, sp, ws, col, BOL * min(1.0, 0.5 + (wa + wb) / 60.0))
    line(g, [((l[0] + c[0]) / 2, (l[1] + c[1]) / 2) for l, c in zip(L, sp)], max(1.0, (wa + wb) * 0.12),
         shade(col, 0.22), 0.8)
    g.new_path()
    for i in range(1, k):
        (x, y), wv = sp[i], ws[i]
        g.move_to(x - wv * 0.2, y + wv * 0.05)
        g.line_to(x, y + wv * 0.28)
        g.line_to(x + wv * 0.2, y + wv * 0.05)
    src(g, shade(col, -0.32), 0.55)
    g.set_line_width(max(0.8, (wa + wb) * 0.04))
    g.stroke()


def _airavata(g, x, base, sc, col=STONE, ol=BOL):
    """Three-headed elephant whose trunks reach the ground like pillars (gate / terrace stair). sc 1 ~ 110 px tall."""
    g.save()
    g.translate(x, base)
    g.scale(sc, sc)
    w = ol / sc
    lt, dk = shade(col, 0.1), shade(col, -0.42)
    heads = [(-34, -70, 17, 21), (34, -70, 17, 21), (0, -74, 20, 24)]
    for sd in (-1, 1):
        ellipse(g, sd * 50, -72, 17, 24, shade(col, -0.1), w)
        curve(g, (sd * 42, -88), (sd * 60, -72), (sd * 44, -54), w * 0.8, dk)
    for hx, hy, rx, ry in heads:
        tw = 13 if hx == 0 else 11
        y0 = hy + ry * 0.4
        rrect(g, hx - tw / 2, y0, tw, -y0 - 3, tw * 0.45, col if hx else lt, w)
        g.new_path()
        yy = y0 + 6
        while yy < -10:
            g.move_to(hx - tw / 2, yy)
            g.line_to(hx + tw / 2, yy)
            yy += 6
        src(g, dk, 0.45)
        g.set_line_width(w * 0.5)
        g.stroke()
        ellipse(g, hx + tw * 0.3, -5, tw * 0.75, 4.5, lt, w * 0.7)
        flower(g, hx + tw * 0.6, -10, 4, lt, shade(col, -0.1), w * 0.4)
    for hx, hy, rx, ry in heads:
        ellipse(g, hx, hy, rx, ry, col if hx else lt, w)
        for sd in (-1, 1):
            circle(g, hx + sd * rx * 0.45, hy - ry * 0.12, 1.8, dk, 0)
            curve(g, (hx + sd * rx * 0.35, hy + ry * 0.5), (hx + sd * rx * 0.75, hy + ry * 0.75),
                  (hx + sd * rx * 0.6, hy + ry * 1.0), w * 1.3, "#efe7d2")
        poly(g, [(hx - rx * 0.5, hy - ry * 0.82), (hx, hy - ry * 1.5), (hx + rx * 0.5, hy - ry * 0.82)], lt, w * 0.7)
        rrect(g, hx - rx * 0.55, hy - ry * 0.95, rx * 1.1, ry * 0.2, 2, shade(col, 0.05), w * 0.6)
    g.restore()


def _garuda(g, x, base, h, col=STONE, ol=BOL):
    """Garuda atlas (bird-man with raised arms holding up the cornice), relief on the terrace wall."""
    s = h / 100.0
    g.save()
    g.translate(x, base)
    g.scale(s, s)
    w = ol / s
    lt, dk = shade(col, 0.1), shade(col, -0.42)
    for sd in (-1, 1):  # wings
        poly(g, [(sd * 12, -64), (sd * 44, -86), (sd * 50, -66), (sd * 46, -46), (sd * 30, -36), (sd * 14, -44)],
             shade(col, -0.06), w)
        g.new_path()
        for k in range(4):
            g.move_to(sd * 16, -58 + k * 4)
            g.line_to(sd * (44 - k * 3), -80 + k * 12)
        src(g, dk, 0.5)
        g.set_line_width(w * 0.6)
        g.stroke()
    for sd in (-1, 1):  # bird legs and claws
        line(g, [(sd * 8, -34), (sd * 19, -18), (sd * 10, -2)], 7 + 2 * w, OUTLINE)
        line(g, [(sd * 8, -34), (sd * 19, -18), (sd * 10, -2)], 7, col)
        for k in (-1, 0, 1):
            line(g, [(sd * 10, -2), (sd * 10 + k * 4 + sd * 3, 1)], 2.2, dk)
    blob(g, [(-12, -34), (12, -34), (15, -62), (-15, -62)], col, w)
    poly(g, [(-12, -36), (12, -36), (8, -22), (-8, -22)], lt, w * 0.6)
    for sd in (-1, 1):  # arms raised to the cornice
        line(g, [(sd * 13, -60), (sd * 24, -80), (sd * 14, -99)], 7 + 2 * w, OUTLINE)
        line(g, [(sd * 13, -60), (sd * 24, -80), (sd * 14, -99)], 7, col)
        ellipse(g, sd * 13, -100, 5, 4, lt, w * 0.7)
    ellipse(g, 0, -73, 9, 9.5, col, w)
    poly(g, [(-3, -73), (7, -71), (1, -62)], lt, w * 0.7)  # hooked beak
    for sd in (-1, 1):
        circle(g, sd * 4, -76, 2.2, "#e8e0cc", w * 0.4)
        circle(g, sd * 4, -76, 1.0, dk, 0)
    poly(g, [(-6, -81), (0, -92), (6, -81)], lt, w * 0.6)
    g.restore()


def _elephant_relief(g, x, y, s, facing, col=STONE):
    g.push_group()
    A.elephant(g, x, y, s, 0.0, walking=False, facing=facing, col="#9c9aa6")
    g.set_operator(cairo.OPERATOR_ATOP)
    g.set_source_rgba(*(hexc(col) + (0.72,)))
    g.paint()
    g.set_operator(cairo.OPERATOR_OVER)
    pat = g.pop_group()
    g.save()
    g.translate(5, 6)
    g.set_source_rgba(0.18, 0.12, 0.06, 0.45)
    g.mask(pat)
    g.restore()
    g.set_source(pat)
    g.paint()


def _relief_figure(g, x, base, h, kind, col):
    """Tiny carved figure for the dense tiers of the Terrace of the Leper King."""
    s = h / 100.0
    g.save()
    g.translate(x, base)
    g.scale(s, s)
    for k, (c, d) in enumerate(((shade(col, -0.42), 3.0), (shade(col, 0.1), 0.0))):
        g.save()
        g.translate(d, d)
        o = 2.2 / s if k else 0
        if kind == "seated":
            blob(g, [(-26, 0), (26, 0), (22, -14), (-22, -14)], c, o)
            poly(g, [(-10, -14), (10, -14), (14, -44), (-14, -44)], c, o)
            line(g, [(-13, -42), (-21, -22), (-14, -14)], 6, c)
            line(g, [(13, -42), (21, -22), (14, -14)], 6, c)
            ellipse(g, 0, -53, 8, 9, c, o)
            poly(g, [(-6, -59), (0, -76), (6, -59)], c, o)
        elif kind == "naga":
            for j in range(5):
                a = (j - 2) * 0.42
                ellipse(g, math.sin(a) * 22, -60 - math.cos(a) * 22, 7, 9, c, o)
            poly(g, [(-10, 0), (10, 0), (8, -50), (-8, -50)], c, o)
        else:  # standing figure (devata, or guardian raising a sword)
            poly(g, [(-11, -2), (11, -2), (9, -36), (-9, -36)], c, o)
            poly(g, [(-9, -36), (9, -36), (12, -44), (-12, -44)], c, o)
            poly(g, [(-7, -44), (7, -44), (11, -64), (-11, -64)], c, o)
            ellipse(g, 0, -72, 7, 8, c, o)
            poly(g, [(-6, -78), (-4, -92), (-1, -82), (0, -96), (1, -82), (4, -92), (6, -78)], c, o)
            line(g, [(-11, -63), (-16, -49), (-9, -44)], 5, c)
            if kind == "warrior":
                line(g, [(11, -63), (19, -56), (21, -92)], 4.5, c)
            else:
                line(g, [(11, -63), (16, -51), (13, -44)], 5, c)
        g.restore()
    g.restore()


# =========================================================================== south gate of angkor thom

SG_VY, SG_H, SG_W = 600, 40, 160


def _sg(X, z):
    return (960 + X / z, SG_VY + SG_H / z)


def _sg_gate(g, cx, base, sc, col=STONE, ol=BOL):
    """South Gate: corbelled passage, three-headed elephants, face tower (local size: 430 wide, ~640 tall)."""
    g.save()
    g.translate(cx, base)
    g.scale(sc, sc)
    _stone_rect(g, -215, -215, 430, 215, shade(col, -0.03), 901, 22, ol, 1.4)
    pts = [(-50, 0), (-50, -150), (-40, -150), (-40, -165), (-30, -165), (-30, -178), (-18, -178), (-18, -190),
           (-8, -190), (-8, -198), (8, -198), (8, -190), (18, -190), (18, -178), (30, -178), (30, -165), (40, -165),
           (40, -150), (50, -150), (50, 0)]
    poly(g, pts, VOID, ol)
    rrect(g, -24, -118, 48, 118, 2, "#cfe0a6", 0)
    rrect(g, -24, -30, 48, 30, 0, "#b9a888", 0)
    for sd in (-1, 1):
        _airavata(g, sd * 134, 0, 1.2, col, ol)
    rrect(g, -232, -232, 464, 20, 2, shade(col, 0.1), ol)
    _face_tower(g, 0, -228, 220, col, 905, "front", body=0.0, tiers=3, tier_h=0.11, lotus=0.3, ol=ol)
    g.restore()


def _sg_wall(g, x0, x1, base, top, ol=BOL):
    _stone_rect(g, x0, top, x1 - x0, base - top, LATERITE, 911 + int(x0), 18, ol, 0.8, True, True)
    rrect(g, x0, top - 10, x1 - x0, 12, 2, shade(LATERITE, 0.12), ol * 0.8)
    r = rng(912 + int(x0))
    for k in range(int((x1 - x0) / 70)):
        _clump(g, r.uniform(x0, x1), top - r.uniform(4, 18), r.uniform(14, 30), ("#4f8c45", "#5a9a4a")[k % 2],
               913 + k, ol=1.5, n=4)


def _sg_jungle(g, base, top, seed):
    r = rng(seed)
    for k in range(60):
        _clump(g, r.uniform(B.X0 - 100, B.X1 + 100), r.uniform(top, base), r.uniform(50, 110),
               ("#4a7f45", "#5a904f", "#3f7040", "#68a05a")[k % 4], seed + k, ol=2.0)


def _sg_gate_mg(g):
    _sg_wall(g, B.X0 - 100, 745, 640, 468)
    _sg_wall(g, 1175, B.X1 + 100, 640, 468)
    _sg_gate(g, 960, 640, 1.0)


def _sg_row(g, side, kind):
    zs = []
    z = 0.2
    while z < 0.98:
        zs.append(z)
        z += 0.03
    figs = []
    for z in zs:
        x, y = _sg(side * (SG_W + 10), z)
        figs.append((z, x, y - 13.0 / z, 52.0 / z))
    top = [(x, yp) for z, x, yp, h in figs]
    bot = [_sg(side * (SG_W + 10), z) for z in zs]
    poly(g, top + bot[::-1], shade(STONE, -0.1), BOL)
    prev = None
    for z, x, yp, h in reversed(figs):
        _giant(g, x, yp, h, kind, "front", STONE, "body", BOL * min(1.0, 0.4 + 0.12 / z))
        gp = (x, yp - 0.40 * h)
        if prev:
            _naga_seg(g, gp, prev[0], 0.13 * h, 0.13 * prev[1])
        _giant(g, x, yp, h, kind, "front", STONE, "hands", BOL * min(1.0, 0.4 + 0.12 / z))
        prev = (gp, h)
    zh = 0.18
    xh, yh = _sg(side * (SG_W + 10), zh)
    yph = yh - 13 / zh
    hh = 50 / zh
    _naga_seg(g, (xh, yph - 0.16 * hh), prev[0], 0.13 * prev[1] * 1.15, 0.13 * prev[1])
    rrect(g, xh - 0.22 * hh, yph - 0.06 * hh, 0.44 * hh, 0.08 * hh, 3, shade(STONE, 0.05), BOL)
    _naga_hood(g, xh, yph - 0.04 * hh, hh, STONE)


def _sg_ground(g):
    a, b = _sg(-SG_W - 40, 1.0), _sg(SG_W + 40, 1.0)
    c, d = _sg(SG_W + 40, 0.06), _sg(-SG_W - 40, 0.06)
    g.new_path()
    poly_path(g, [a, b, c, d])
    g.set_source(lin_grad(0, 640, 0, 1080, [(0, "#c8b893"), (1, "#a99873")]))
    g.fill_preserve()
    g.save()
    g.clip()
    g.new_path()
    for k in range(-4, 5):
        p0, p1 = _sg(k * 40, 1.0), _sg(k * 40, 0.06)
        g.move_to(*p0)
        g.line_to(*p1)
    iz = 1.0
    while iz > 0.06:
        p0, p1 = _sg(-SG_W - 40, iz), _sg(SG_W + 40, iz)
        g.move_to(*p0)
        g.line_to(*p1)
        iz = 1 / (1 / iz + 1.4)
    src(g, "#8a7b5d", 0.5)
    g.set_line_width(1.8)
    g.stroke()
    _spots(g, B.X0, 640, B.X1, 1100, 70, 921, "#7f7458", 0.12, 10, 40, 0.3)
    _tufts(g, 900, 1080, 16, 922, "#6f8a45", s0=1.0, s1=1.4)
    g.restore()
    _sg_row(g, -1, "deva")
    _sg_row(g, 1, "asura")


# causeway view: side view along one row
SGC_VX, SGC_VY, SGC_H, SGC_X = 1980, 600, 60, -560


def _sgc(X, z):
    return (SGC_VX + X / z, SGC_VY + SGC_H / z)


def _sgc_mg(g):
    _sg_wall(g, B.X0 - 100, 1760, 618, 552, BOL * 0.7)
    _sg_wall(g, 1920, B.X1 + 100, 618, 552, BOL * 0.7)
    _sg_gate(g, 1840, 618, 0.42, STONE, BOL / 0.42 * 0.6)


def _sgc_ground(g, kind):
    zs = []
    z = 2.15
    while z > 0.27:
        zs.append(z)
        z -= 0.045
    base = [_sgc(SGC_X, z) for z in zs]
    g.new_path()  # causeway floor below the row
    poly_path(g, [(B.X1 + 100, _sgc(SGC_X, 2.6)[1])] + base + [_sgc(SGC_X, 0.22), (B.X0 - 100, _sgc(SGC_X, 0.22)[1]),
                                                              (B.X0 - 100, 1300), (B.X1 + 100, 1300)])
    g.set_source(lin_grad(0, 620, 0, 1080, [(0, "#c8b893"), (1, "#a99873")]))
    g.fill_preserve()
    g.save()
    g.clip()
    g.new_path()
    for X in range(-560, 1400, 70):
        p0, p1 = _sgc(X, 2.6), _sgc(X, 0.08)
        g.move_to(*p0)
        g.line_to(*p1)
    iz = 2.6
    while iz > 0.08:
        p0, p1 = _sgc(-600, iz), _sgc(1400, iz)
        g.move_to(*p0)
        g.line_to(*p1)
        iz = 1 / (1 / iz + 0.6)
    src(g, "#8a7b5d", 0.5)
    g.set_line_width(1.8)
    g.stroke()
    _spots(g, B.X0, 620, B.X1, 1100, 70, 931, "#7f7458", 0.12, 10, 40, 0.3)
    g.restore()
    figs = []
    for z in zs:
        x, y = _sgc(SGC_X, z)
        figs.append((z, x, y - 22.0 / z, 110.0 / z))
    top = [(x, yp) for z, x, yp, h in figs] + [(_sgc(SGC_X, 0.2)[0], _sgc(SGC_X, 0.2)[1] - 110)]
    bot = base + [_sgc(SGC_X, 0.2)]
    poly(g, top + bot[::-1], shade(STONE, -0.08), BOL)
    prev = None
    for z, x, yp, h in figs:  # far to near
        olw = BOL * min(1.0, 0.45 + 0.1 / z)
        _giant(g, x, yp, h, kind, "side", STONE, "body", olw)
        gp = (x - 0.24 * h, yp - 0.43 * h)
        if prev:
            _naga_seg(g, gp, prev[0], 0.13 * h, 0.13 * prev[1])
        _giant(g, x, yp, h, kind, "side", STONE, "hands", olw)
        prev = (gp, h)
    _naga_seg(g, (prev[0][0] - 600, prev[0][1] + 60), prev[0], 0.15 * prev[1], 0.13 * prev[1])


@extra
def _south_gate(ctx, layer, t, tod):
    view = str(_param("view", "gate"))
    wcol = WATER.get(tod, WATER["day"])[1]
    if view == "causeway":
        kind = "asura" if str(_param("side", "deva")) == "asura" else "deva"
        if layer == "SKY":
            _sky(ctx, t, tod, 600, ncloud=6)
            _maybe_birds(ctx, t, tod, n=5, y0=80, y1=360)
        elif layer == "BG":
            _cached(ctx, ("sgc", "BG"), lambda g: _sg_jungle(g, 600, 420, 941))
        elif layer == "MG":
            _cached(ctx, ("sg", "water", tod), lambda g: _water_fill(g, tod, 612, 1300, 0.3))
            rec = _rec(("sgc", "MG"), _sgc_mg)
            _reflect(ctx, rec, 618, 0.3, wcol, 618, 900)
            _ripples(ctx, t, tod, 622, 1000, 80, 951, 0.0, 0.3)
            ctx.save()
            ctx.set_source_surface(rec, 0, 0)
            ctx.paint()
            ctx.restore()
        elif layer == "GROUND":
            _cached(ctx, ("sgc", "GROUND", kind), lambda g: _sgc_ground(g, kind))
    else:
        if layer == "SKY":
            _sky(ctx, t, tod, 640, ncloud=6)
            _maybe_birds(ctx, t, tod, n=5, y0=60, y1=300)
        elif layer == "BG":
            _cached(ctx, ("sg", "BG"), lambda g: _sg_jungle(g, 560, 300, 961))
        elif layer == "MG":
            _cached(ctx, ("sg", "water", tod), lambda g: _water_fill(g, tod, 636, 1300, 0.3))
            rec = _rec(("sg", "MG"), _sg_gate_mg)
            _reflect(ctx, rec, 640, 0.3, wcol, 640, 1000)
            _ripples(ctx, t, tod, 644, 1080, 90, 962, 0.0, 0.3)
            ctx.save()
            ctx.set_source_surface(rec, 0, 0)
            ctx.paint()
            ctx.restore()
            ctx.new_path()  # far end of the causeway behind the ground layer (no gap when the camera moves)
            poly_path(ctx, [_sg(-SG_W - 40, 1.04), _sg(SG_W + 40, 1.04), _sg(SG_W + 40, 0.5), _sg(-SG_W - 40, 0.5)])
            src(ctx, "#c8b893")
            ctx.fill()
        elif layer == "GROUND":
            _cached(ctx, ("sg", "GROUND"), _sg_ground)


# =========================================================================== bayon

def _paved(g, y0, seed, vx=960, vy=560, c0="#c9bb98", c1="#b2a382", step=110):
    g.new_path()
    g.rectangle(B.X0 - 100, y0, B.X1 - B.X0 + 200, 1300 - y0)
    g.set_source(lin_grad(0, y0, 0, 1080, [(0, c0), (1, c1)]))
    g.fill()
    g.new_path()
    d = y0 - vy
    for k in range(-30, 31):
        g.move_to(vx + k * step, y0)
        g.line_to(vx + k * step * (1300 - vy) / d, 1300)
    iz = 1.0
    while vy + d / iz < 1300:
        g.move_to(B.X0 - 100, vy + d / iz)
        g.line_to(B.X1 + 100, vy + d / iz)
        iz *= 0.8
    src(g, shade(c1, -0.3), 0.5)
    g.set_line_width(1.8)
    g.stroke()
    _spots(g, B.X0, y0, B.X1, 1100, 60, seed, "#6f6650", 0.12, 10, 40, 0.3)
    _spots(g, B.X0, y0, B.X1, 1100, 30, seed + 1, MOSS, 0.15, 10, 30, 0.3)


def _bayon_gallery(g, x0, x1, base, h, col, seed, ol=BOL, ped_step=380):
    _stone_rect(g, x0, base - h, x1 - x0, h, shade(col, -0.04), seed, 22, ol, 1.0)
    x = x0 + 120
    while x < x1 - 80:
        _baluster_window(g, x - 40, base - h * 0.75, 80, h * 0.5, col, 4, ol)
        x += 260
    for i, (hh, ins) in enumerate(((26, 0), (24, 10), (20, 22))):
        y0 = base - h - (i + 1) * hh + i * 2
        rrect(g, x0 + ins, y0, x1 - x0 - 2 * ins, hh, 2, shade(col, -0.06 + 0.05 * i), ol * 0.9)
    x = x0 + ped_step * 0.5
    while x < x1:
        _pediment(g, x, base - h + 4, 150, 110, shade(col, 0.04), ol, inner=True)
        x += ped_step


def _bayon_bg(g):
    haze = "#cfdbe0"
    col = mix(STONE, haze, 0.35)
    _bayon_gallery(g, B.X0 - 100, B.X1 + 100, 690, 50, col, 1201, BOL * 0.6, 300)
    for x, base, w, kind, sd in ((250, 650, 130, "front", 1202), (590, 630, 118, "corner", 1203),
                                 (1330, 630, 124, "corner", 1204), (1690, 650, 136, "front", 1205),
                                 (-150, 660, 120, "corner", 1206), (2100, 660, 126, "corner", 1207)):
        _face_tower(g, x, base, w, mix(STONE, haze, 0.4), sd, kind, body=0.6, ol=BOL * 0.6, detail=False)
    _face_tower(g, 960, 660, 230, mix(STONE, haze, 0.2), 1210, "front", body=0.75, tiers=4, ol=BOL * 0.8)


def _bayon_mg(g):
    for x, base, w, kind, sd in ((160, 760, 236, "front", 1222), (560, 730, 190, "corner", 1223),
                                 (1380, 730, 200, "corner", 1224), (1780, 760, 246, "front", 1225)):
        _face_tower(g, x, base, w, STONE, sd, kind, body=0.5)
    _bayon_gallery(g, B.X0 - 100, B.X1 + 100, 800, 70, STONE, 1226)


def _bayon_ground(g):
    _paved(g, 790, 1231)
    rrect(g, B.X0 - 100, 782, B.X1 - B.X0 + 200, 14, 2, shade(STONE, 0.1), BOL)
    _rubble(g, 170, 880, 4, 0.9, 1232)
    _rubble(g, 1790, 900, 5, 1.0, 1233)


def _bayon_face_ground(g, fx):
    col = STONE
    s = 1.72
    cy = 470
    top = cy - 152 * s
    _stone_rect(g, fx - 300, top - 30, 600, 800 - top + 30, shade(col, -0.12), 1241, 30, BOL, 1.2)
    _shade_right(g, fx + 120, top - 30, 180, 830 - top, 0.08)
    _bayon_face(g, fx - 262, cy + 8, s * 0.94, shade(col, -0.2), 1242, 0.24)
    _bayon_face(g, fx, cy, s, col, 1243)
    yb = top - 26
    tw = 580
    for i in range(3):
        _tier_ring(g, fx, yb, tw / 2, 64, shade(col, 0.03 * i), 1244 + i)
        yb -= 76
        tw *= 0.84
    _stone_rect(g, fx - 330, 752, 660, 50, shade(col, 0.04), 1248, 25, BOL, 0.8)
    rrect(g, fx - 340, 744, 680, 14, 2, shade(col, 0.12), BOL)


@extra
def _bayon(ctx, layer, t, tod):
    view = str(_param("view", "towers"))
    if view == "face":
        fx = float(_param("face_x", 1000))
        ox = 1660 if fx < 1250 else 300
        if layer == "SKY":
            _sky(ctx, t, tod, 640, ncloud=5)
            _maybe_birds(ctx, t, tod, n=4, y0=60, y1=260)
        elif layer == "BG":
            _cached(ctx, ("bayon_f", "BG"), lambda g: (_sg_jungle(g, 640, 420, 1251),
                                                       _face_tower(g, 2600 - ox, 680, 150, mix(STONE, "#cfdbe0", 0.35),
                                                                   1252, "corner", body=0.6, ol=BOL * 0.6, detail=False)))
        elif layer == "MG":
            _cached(ctx, ("bayon_f", "MG", ox), lambda g: (_face_tower(g, ox, 790, 290, STONE, 1253, "corner", body=0.55),
                                                           _bayon_gallery(g, B.X0 - 100, B.X1 + 100, 800, 60, STONE, 1254)))
        elif layer == "GROUND":
            _cached(ctx, ("bayon_f", "GROUND", fx), lambda g: (_paved(g, 798, 1255), _bayon_face_ground(g, fx)))
    else:
        if layer == "SKY":
            _sky(ctx, t, tod, 640, ncloud=6)
            _maybe_birds(ctx, t, tod, n=5, y0=40, y1=260)
        elif layer == "BG":
            _cached(ctx, ("bayon_t", "BG"), _bayon_bg)
        elif layer == "MG":
            _cached(ctx, ("bayon_t", "MG"), _bayon_mg)
        elif layer == "GROUND":
            _cached(ctx, ("bayon_t", "GROUND"), _bayon_ground)


# =========================================================================== terraces (elephants / leper king)

def _royal_square(g, seed):
    g.new_path()
    g.rectangle(B.X0 - 100, 788, B.X1 - B.X0 + 200, 520)
    g.set_source(lin_grad(0, 788, 0, 1080, [(0, "#cdb184"), (1, "#b8965f")]))
    g.fill()
    r = rng(seed)
    g.new_path()
    for _ in range(36):
        ellipse_path(g, r.uniform(B.X0, B.X1), r.uniform(810, 1090), r.uniform(50, 160), r.uniform(8, 20))
    src(g, "#8fae5a", 0.4)
    g.fill()
    _spots(g, B.X0, 800, B.X1, 1100, 80, seed + 1, "#9b7a4c", 0.25, 3, 9, 0.6)
    _tufts(g, 800, 1080, 70, seed + 2, "#5f8a3a", s0=0.6, s1=1.4)


def _phimeanakas(g, cx, base, col=LATERITE):
    for i, (hw, h) in enumerate(((210, 46), (175, 42), (140, 40))):
        _stone_rect(g, cx - hw, base - h, 2 * hw, h, shade(col, 0.03 * i), 1301 + i, 14, BOL * 0.7, 0.6, True, True)
        base -= h
    poly(g, [(cx - 30, base + 128), (cx - 22, base), (cx + 22, base), (cx + 30, base + 128)], shade(STONE, -0.05), BOL * 0.7)
    _mebon_tower(g, cx, base, 70, mix(STONE, "#cfdbe0", 0.2), 1305)


def _te_bg(g):
    _sg_jungle(g, 470, 260, 1311)
    _phimeanakas(g, 1520, 470, mix(LATERITE, "#cfdbe0", 0.25))


def _te_wall(g):
    col = STONE
    W0, W1 = B.X0 - 100, B.X1 + 100
    _stone_rect(g, W0, 400, W1 - W0, 400, col, 1321, 30, BOL, 0.8)
    rrect(g, W0, 468, W1 - W0, 282, 0, shade(col, -0.1), BOL * 0.8)  # frieze panel
    g.save()
    g.new_path()
    g.rectangle(W0, 468, W1 - W0, 282)
    g.clip()
    _weather(g, W0, 468, W1, 750, 1322, 1.0)
    g.restore()
    rrect(g, W0, 750, W1 - W0, 22, 2, shade(col, 0.08), BOL * 0.8)
    rrect(g, W0, 770, W1 - W0, 34, 2, shade(col, -0.05), BOL)
    rrect(g, W0, 432, W1 - W0, 38, 2, shade(col, 0.06), BOL * 0.8)
    g.new_path()  # lotus-petal moulding
    x = W0
    while x < W1:
        g.move_to(x, 468)
        g.curve_to(x + 4, 440, x + 20, 440, x + 24, 468)
        x += 24
    src(g, shade(col, -0.3), 0.7)
    g.set_line_width(1.6)
    g.stroke()
    rrect(g, W0, 398, W1 - W0, 36, 2, shade(col, 0.12), BOL)
    for x0_, x1_, y0_, y1_ in ((1180, 1330, 470, 640), (-300, -150, 520, 700), (2150, 2300, 480, 650)):
        blob(g, [(x0_, y0_), (x1_, y0_ + 20), (x1_ - 10, y1_), (x0_ + 20, y1_ - 10)], LATERITE, BOL * 0.7)
        _pores(g, x0_, y0_, x1_, y1_, int(x0_))
    for x in (360, 50, -260, -570):
        _elephant_relief(g, x, 742, 0.95, -1)
    for x in (1560, 1870, 2180, 2490):
        _elephant_relief(g, x, 742, 0.95, 1)
    for sd in (-1, 1):  # garuda atlantes beside the central stair
        for dx in (320, 405):
            _garuda(g, 960 + sd * dx, 746, 276, col)
    pw = 270  # central stair projection
    for sd in (-1, 1):
        poly(g, [(960 + sd * pw, 410), (960 + sd * (pw + 18), 398), (960 + sd * (pw + 18), 802), (960 + sd * pw, 822)],
             shade(col, -0.16), BOL)
    _stone_rect(g, 960 - pw, 410, 2 * pw, 412, shade(col, 0.05), 1331, 30, BOL, 0.8)
    rrect(g, 960 - pw - 14, 394, 2 * pw + 28, 22, 2, shade(col, 0.14), BOL)
    poly(g, [(960 - 92, 822), (960 - 86, 410), (960 + 86, 410), (960 + 92, 822)], shade(col, -0.1), BOL)
    poly(g, [(960 - 74, 822), (960 - 70, 410), (960 + 70, 410), (960 + 74, 822)], shade(col, 0.1), BOL)
    g.new_path()
    for k in range(1, 22):
        yy = 822 - 412 * k / 22.0
        g.move_to(960 - 72, yy)
        g.line_to(960 + 72, yy)
    src(g, shade(col, -0.4), 0.7)
    g.set_line_width(2)
    g.stroke()
    for sd in (-1, 1):
        _airavata(g, 960 + sd * 172, 822, 1.65, col)


def _te_leper(g):
    col = "#a09a82"
    W0, W1 = B.X0 - 100, B.X1 + 100
    top, bot = 250, 800
    _stone_rect(g, W0, top, W1 - W0, bot - top, col, 1401, 30, BOL, 0.5, joints=False)
    for bx0, bx1 in ((-120, 330), (1590, 2040)):  # projecting bays
        _stone_rect(g, bx0, top - 6, bx1 - bx0, bot - top + 22, shade(col, 0.06), 1402 + bx0, 30, BOL, 0.5, joints=False)
        _shade_right(g, bx1 - 16, top - 6, 16, bot - top + 22, 0.25)
    kinds = ("seated", "standing", "warrior", "standing", "naga")
    th = (bot - 40 - (top + 20)) / 5.0
    for i, kind in enumerate(kinds):
        y0 = top + 20 + i * th
        rrect(g, W0, y0 - 4, W1 - W0, 8, 2, shade(col, 0.1), BOL * 0.6)
        x = W0 + 20 + (i % 2) * 27
        while x < W1:
            _relief_figure(g, x, y0 + th - 6, th * 0.8, kind, col)
            x += 54
    rrect(g, W0, bot - 38, W1 - W0, 40, 2, shade(col, -0.05), BOL)
    rrect(g, W0, top - 14, W1 - W0, 22, 2, shade(col, 0.12), BOL)
    _spots(g, W0, top, W1, bot, 140, 1410, MOSS, 0.22, 10, 40, 0.6)
    _spots(g, W0, top, W1, bot, 90, 1411, "#3d3a2c", 0.14, 10, 40, 0.6)
    r = rng(1412)
    for k in range(int((W1 - W0) / 90)):
        _clump(g, r.uniform(W0, W1), top - 18 - r.uniform(0, 10), r.uniform(14, 26), "#5a9a4a", 1413 + k, ol=1.5, n=4)
    _leper_king(g, 960, top - 14, 230, "#b3ae98")


def _leper_king(g, x, base, h, col="#9c9c88"):
    """The seated statue on top of the terrace: one knee raised, calm face with a moustache."""
    s = h / 100.0
    g.save()
    g.translate(x, base)
    g.scale(s, s)
    w = BOL / s
    lt, dk = shade(col, 0.12), shade(col, -0.42)
    rrect(g, -42, -12, 84, 12, 2, shade(STONE, 0.05), w)
    blob(g, [(-36, -12), (10, -12), (14, -24), (-32, -27)], shade(col, -0.04), w)
    line(g, [(-13, -54), (-22, -38), (-27, -26)], 8 + 2 * w, OUTLINE)
    line(g, [(-13, -54), (-22, -38), (-27, -26)], 8, col)
    blob(g, [(-15, -24), (13, -24), (15, -58), (-15, -58)], col, w)
    blob(g, [(4, -12), (27, -12), (31, -42), (19, -48), (8, -30)], shade(col, 0.04), w)
    line(g, [(13, -54), (22, -47), (26, -44)], 8 + 2 * w, OUTLINE)
    line(g, [(13, -54), (22, -47), (26, -44)], 8, col)
    ellipse(g, 27, -44, 5, 4, lt, w * 0.7)
    rrect(g, -5, -63, 10, 7, 2, col, w * 0.7)
    ellipse(g, 0, -72, 10.5, 12.5, col, w)
    ellipse(g, 0, -86, 7, 5.5, shade(col, -0.05), w * 0.8)
    for sd in (-1, 1):
        curve(g, (sd * 7, -74), (sd * 4.5, -72), (sd * 2, -74), w * 0.9, dk)
        ellipse(g, sd * 10.5, -72, 2.4, 4.5, shade(col, -0.06), w * 0.5)
    curve(g, (-6, -65), (0, -67.5), (6, -65), w * 1.4, dk)
    curve(g, (-3, -62.5), (0, -61), (3, -62.5), w * 0.8, dk)
    g.restore()


@extra
def _terraces(ctx, layer, t, tod):
    which = str(_param("which", "elephants"))
    if layer == "SKY":
        _sky(ctx, t, tod, 600, ncloud=6)
        _maybe_birds(ctx, t, tod, n=5, y0=60, y1=240)
    elif layer == "BG":
        _cached(ctx, ("terr", "BG", which), _te_bg if which == "elephants" else (lambda g: _sg_jungle(g, 330, 190, 1431)))
    elif layer == "MG":
        if which == "elephants":
            _raster(ctx, ("terr", "MG", which), _te_wall, B.X0 - 100, 360, B.X1 - B.X0 + 200, 480)
        else:
            _cached(ctx, ("terr", "MG", which), _te_leper)
    elif layer == "GROUND":
        _cached(ctx, ("terr", "GROUND"), lambda g: _royal_square(g, 1441))


def register(envs):
    envs.update({
        "palilay": _palilay,
        "preah_khan": _preah_khan,
        "srah_srang": _srah_srang,
        "west_baray": _west_baray,
        "south_gate": _south_gate,
        "bayon": _bayon,
        "terraces": _terraces,
    })
