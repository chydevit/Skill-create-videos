"""Scene kit: Python helpers that emit SVG for flat-explainer sets (2400x1350), so a film's ~30 sets can be written
as short functions instead of hand-placed paths.  Use it from scenes_src/*.py; each scene writes scenes/<name>.svg.

    from kit import *
    s = Scene("night_ruins", light=(1400, 600), rim="#ffb347", dark="#12051a 0.8 1250", haze="#2a1850 0.45")
    s.layer("bg", sky(["#170c30", "#3a1446", "#7a1f44"]), stars(120, 700))
    s.layer("char", person(900, 1150, 420, "guide", view="back", arms=dict(r=(150, 20)), hold=dict(r="torch")))
    s.save()

person(): parametric reference-style character - rubber-hose limbs from joint angles, so any pose is one line:
    arms=dict(l=(shoulder_deg, elbow_deg), r=(...))   0 = hanging down, 90 = horizontal outward/forward,
                                                       180 = straight up; elbow adds bend in the same sense
    legs="stand" | "walk" | "sit" | "kneel" | ("walk", phase 0..1)
    view="front" | "right" | "left" | "back" | "right3" (3/4) | "left3"
    style: "guide" | "woman" | "man" | "elder" | "child" | "shaman" + overrides (top=, skin=, hair=...)
    hold=dict(r="torch"|"bowl"|"chisel"|"spear"|"bundle"|"tablet"|"skull"|"basket"|"straw")  (basket goes on head)
    anim / rim / depth: passed through as data-* attributes (sprites)
"""
import math
import random

R = random.Random(7)


def esc(v):
    return ("%.1f" % v).rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


def mix(a, b, t):
    a, b = a.lstrip("#"), b.lstrip("#")
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * t) for x, y in zip(ca, cb))


def shade(c, k=0.78, toward="#3b1f6e", t=0.18):
    return mix(mix(c, "#000000", 1 - k), toward, t)


def attrs(**kw):
    out = []
    for k, v in kw.items():
        if v is None or v is False:
            continue
        out.append('%s="%s"' % (k.replace("_", "-"), v))
    return " ".join(out)


def g(*children, **kw):
    a = attrs(**kw)
    return "<g%s>%s</g>" % ((" " + a) if a else "", "".join(children))


def path(d, fill="none", **kw):
    return '<path d="%s" fill="%s" %s/>' % (d, fill, attrs(**kw))


def circle(x, y, r, fill, **kw):
    return '<circle cx="%s" cy="%s" r="%s" fill="%s" %s/>' % (esc(x), esc(y), esc(r), fill, attrs(**kw))


def ellipse(x, y, rx, ry, fill, **kw):
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" %s/>' % (esc(x), esc(y), esc(rx), esc(ry), fill,
                                                                      attrs(**kw))


def rect(x, y, w, h, fill, rx=0, **kw):
    return '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" %s/>' % (
        esc(x), esc(y), esc(w), esc(h), esc(rx), fill, attrs(**kw))


def poly(pts, fill, **kw):
    return path("M" + " L".join("%.1f %.1f" % p for p in pts) + " Z", fill, **kw)


def stroke(d, col, w, **kw):
    return path(d, "none", stroke=col, stroke_width=w, stroke_linecap="round", stroke_linejoin="round", **kw)


# ------------------------------------------------------------------ backgrounds
_GID = [0]
DEFAULT_RIM = [None]      # set by Scene(rim=...) so generated characters get the scene's rim light


def gid(p="g"):
    _GID[0] += 1
    return "%s%d" % (p, _GID[0])


class Scene:
    def __init__(self, name, light=(300, 0), rim=None, dark=None, dark_reveal=None, dark_lights=None, haze=None,
                 light_depth=None, defs=""):
        self.name, self.layers, self.defs = name, [], [defs]
        DEFAULT_RIM[0] = rim
        self.root = dict(data_light="%d,%d" % light, data_rim_chars=rim, data_dark=dark,
                         data_dark_reveal=dark_reveal, data_dark_lights=dark_lights, data_haze=haze,
                         data_light_depth=light_depth)

    def define(self, s):
        self.defs.append(s)
        return self

    def layer(self, lid, *children, depth=None, **kw):
        self.layers.append(g(*children, id=lid, data_depth=depth, **kw))
        return self

    def svg(self):
        return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                'viewBox="0 0 2400 1350" %s><defs>%s</defs>%s</svg>' % (attrs(**self.root), "".join(self.defs),
                                                                         "".join(self.layers)))

    def save(self, folder="scenes"):
        import os
        os.makedirs(folder, exist_ok=True)
        p = os.path.join(folder, self.name + ".svg")
        open(p, "w").write(self.svg())
        return p


def lingrad(stops, vertical=True, gid_=None):
    i = gid_ or gid("lg")
    st = "".join('<stop offset="%s" stop-color="%s"/>' % (o, c) for o, c in stops)
    xy = 'x1="0" y1="0" x2="0" y2="1"' if vertical else 'x1="0" y1="0" x2="1" y2="0"'
    return i, '<linearGradient id="%s" %s>%s</linearGradient>' % (i, xy, st)


def radgrad(stops, gid_=None):
    i = gid_ or gid("rg")
    st = "".join('<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (o, c, a) for o, c, a in stops)
    return i, '<radialGradient id="%s" cx="0.5" cy="0.5" r="0.5">%s</radialGradient>' % (i, st)


def sky(cols, scene=None):
    """Vertical gradient sky. cols top -> bottom."""
    n = len(cols) - 1
    i, d = lingrad([(round(k / n, 3), c) for k, c in enumerate(cols)])
    return d.join(['<defs>', '</defs>']) + rect(0, 0, 2400, 1350, "url(#%s)" % i)


def halo(x, y, r, col="#ffd36b", a=0.85, **kw):
    i, d = radgrad([(0, col, a), (0.4, col, a * 0.4), (1, col, 0)])
    return "<defs>%s</defs>" % d + circle(x, y, r, "url(#%s)" % i, **kw)


def stars(n, ymax, col="#cbb8ff", seed=3):
    r = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = r.uniform(0, 2400), r.uniform(0, ymax)
        if r.random() < 0.2:
            s = r.uniform(5, 9)
            out.append(path("M%.0f %.0f l%.1f %.1f l%.1f %.1f l-%.1f %.1f l-%.1f -%.1f z" % (
                x, y - s, s * .3, s * .7, s * .7, s * .3, s * .7, s * .3, s * .3, s * .7), col, opacity="0.85"))
        else:
            out.append(circle(x, y, round(r.uniform(2, 4), 1), col, opacity="%.2f" % r.uniform(.35, .8)))
    return "".join(out)


def pebbles(x0, y0, x1, y1, n, col, size=(10, 22), seed=5, op=0.9):
    r = random.Random(seed)
    out = []
    for _ in range(n):
        w = r.uniform(*size) * 2
        out.append(rect(r.uniform(x0, x1), r.uniform(y0, y1), w, w * 0.42, col, rx=w * 0.21, opacity=op))
    return "".join(out)


def ground(y, col, wav=40, seed=1, x0=-50, x1=2450):
    r = random.Random(seed)
    pts, x = [], x0
    d = "M%d %d" % (x0, y)
    while x < x1:
        nx = x + r.uniform(260, 520)
        d += " Q%.0f %.0f %.0f %.0f" % ((x + nx) / 2, y + r.uniform(-wav, wav), nx, y + r.uniform(-wav / 3, wav / 3))
        x = nx
    return path(d + " L%d 1400 L%d 1400 Z" % (x1, x0), col)


def mesas(y, col, top, seed=2, hmin=60, hmax=220):
    r = random.Random(seed)
    out, pts, x = [], [], -50
    while x < 2500:
        w, h = r.uniform(180, 420), r.uniform(hmin, hmax)
        pts += ["L%.0f %.0f" % (x, y), "L%.0f %.0f" % (x + 30, y - h), "L%.0f %.0f" % (x + w - 30, y - h),
                "L%.0f %.0f" % (x + w, y)]
        out.append(rect(x + 30, y - h, w - 60, 10, top, rx=5))
        x += w + r.uniform(40, 200)
    return path("M-50 1400 %s L2500 %d L2500 1400 Z" % (" ".join(pts), y), col) + "".join(out)


def hills(y, col, stripe=None, stripe2=None, seed=4, n=5, rmin=200, rmax=420):
    r = random.Random(seed)
    out = []
    for i in range(n):
        cx = r.uniform(-100, 2500)
        rx, ry = r.uniform(rmin, rmax), r.uniform(rmin * 0.6, rmax * 0.7)
        out.append(ellipse(cx, y, rx, ry, col))
        out.append(path("M%.0f %.0f A%.0f %.0f 0 0 1 %.0f %.0f Z" % (cx, y - ry, rx, ry, cx + rx, y), shade(col, 0.85)))
        if stripe:
            for k in range(2):
                w = rx * (0.55 + k * 0.2)
                out.append(rect(cx - w * r.uniform(0.2, 0.6), y - ry * (0.7 - k * 0.25), w, ry * 0.12,
                                stripe if k == 0 else (stripe2 or shade(col, 0.7)), rx=ry * 0.06))
    return "".join(out)


def bush(cx, cy, s, c1="#0f6b4a", c2="#167a44", berries=None, seed=0):
    r = random.Random(seed)
    o = []
    for i in range(9):
        a = math.pi + i / 8 * math.pi
        x, y = cx + math.cos(a) * s * 0.9, cy + math.sin(a) * s * 0.7
        o.append('<path d="M%.0f %.0f q%.0f %.0f 0 %.0f q%.0f %.0f 0 %.0f z" fill="%s" transform="rotate(%.0f %.0f %.0f)"/>'
                 % (x, y, -s * .25, -s * .35, -s * .7, s * .25, s * .35, s * .7, c1 if i % 2 else c2,
                    math.degrees(a) + 90, x, y))
    o.append(ellipse(cx, cy - s * .2, s * .95, s * .6, c2))
    o.append(ellipse(cx - s * .2, cy - s * .35, s * .55, s * .4, c1))
    if berries:
        for _ in range(3):
            o.append(circle(cx + r.uniform(-s * .6, s * .6), cy - r.uniform(s * .1, s * .6), s * .1, berries))
    return "".join(o)


def grass_tuft(x, y, s, col):
    return path("M%.0f %.0f q-%.0f -%.0f %.0f -%.0f q%.0f %.0f %.0f %.0f q%.0f -%.0f %.0f -%.0f q-%.0f %.0f 0 %.0f Z" % (
        x, y, s * .2, s * .9, s * .1, s * 1.7, s * .1, s * .8, s * .3, s, s * .2, s * 1.1, s * .6, s * 1.3,
        s * .2, s * 1.0, s * 1.3), col)


def palm(x, y, h, trunk="#5a3a2a", leaf="#167a44", leaf2="#0f6b4a"):
    o = [stroke("M%.0f %.0f q%.0f -%.0f %.0f -%.0f" % (x, y, h * .15, h * .5, h * .08, h), trunk, h * .06)]
    tx, ty = x + h * .08, y - h
    for i, a in enumerate((-160, -120, -60, -20, -95, 200, 20)):
        ar = math.radians(a)
        ex, ey = tx + math.cos(ar) * h * .5, ty + math.sin(ar) * h * .3 + h * .08
        o.append(path("M%.0f %.0f Q%.0f %.0f %.0f %.0f Q%.0f %.0f %.0f %.0f Z" % (
            tx, ty, (tx + ex) / 2, ty - h * .18, ex, ey, (tx + ex) / 2, ty - h * .04, tx, ty),
            leaf if i % 2 else leaf2))
    return "".join(o)


def t_pillar(x, y, h, col="#c97a4a", relief=None, rim=None, flip=False):
    """Göbekli-style T pillar seen from the front-side. relief: 'fox'|'snake'|'boar'|'vulture'|'arms'."""
    w = h * 0.22
    hd = h * 0.24
    d = shade(col, 0.72)
    o = [rect(x - w / 2, y - h, w, h, col, rx=6),
         rect(x + w * 0.1, y - h, w * 0.4, h, d, rx=6),
         rect(x - w * 1.45, y - h - hd, w * 2.9, hd, col, rx=10),
         rect(x + w * 0.1, y - h - hd, w * 1.35, hd, d, rx=10)]
    rc = mix(col, "#ffffff", 0.18)
    if relief == "fox":
        o.append(path("M%.0f %.0f q%.0f -%.0f %.0f 0 q-%.0f %.0f -%.0f 0 z" % (
            x - w * .4, y - h * .55, w * .4, w * .35, w * .85, w * .4, w * .2, w * .85), rc))
        o.append(poly([(x - w * .45, y - h * .56), (x - w * .55, y - h * .66), (x - w * .3, y - h * .6)], rc))
    elif relief == "snake":
        o.append(stroke("M%.0f %.0f q%.0f %.0f 0 %.0f q-%.0f %.0f 0 %.0f q%.0f %.0f 0 %.0f" % (
            x, y - h * .85, w * .35, w * .3, w * .6, w * .35, w * .3, w * .6, w * .35, w * .3, w * .6), rc, w * .12))
    elif relief == "boar":
        o.append(ellipse(x, y - h * .5, w * .38, w * .2, rc))
        o.append(poly([(x - w * .38, y - h * .5), (x - w * .55, y - h * .47), (x - w * .36, y - h * .44)], rc))
    elif relief == "vulture":
        o.append(path("M%.0f %.0f l%.0f -%.0f l%.0f %.0f l-%.0f %.0f z" % (
            x - w * .4, y - h * .62, w * .4, w * .3, w * .4, w * .3, w * .4, w * .1), rc))
    elif relief == "arms":
        for s in (-1, 1):
            o.append(stroke("M%.0f %.0f q%.0f %.0f %.0f %.0f" % (x + s * w * .45, y - h * .75, s * w * .1, h * .2,
                                                                  -s * w * .35, h * .3), rc, w * .1))
    o.append(rect(x - w * .5, y - h * .25, w, w * .14, rc, rx=4))
    grp = g(*o, transform="translate(%.0f 0) scale(-1 1) translate(%.0f 0)" % (x * 2, 0) if flip else None,
            data_rim=rim)
    return grp


def round_house(x, y, s, wall="#e8925a", wall_d="#c96a3a", roof="#f5b37a", door="#5a1e2a"):
    w, h = 220 * s, 120 * s
    return "".join([ellipse(x, y, w, h * .4, shade(wall, .7)),
                    rect(x - w, y - h, 2 * w, h, wall), rect(x + w * .25, y - h, w * .75, h, wall_d),
                    ellipse(x, y - h, w, h * .4, roof),
                    rect(x - 26 * s, y - h * .7, 52 * s, h * .7, door, rx=26 * s),
                    pebbles(x - w * .9, y - h * .9, x + w * .1, y - h * .25, 5, roof, (6, 12), seed=int(x)),
                    poly([(x + w * .1, y - h * 1.4), (x + w, y - h * 1.4), (x + w, y)], "#5a1e3a", opacity="0.18")])


def box_house(x, y, w, h, wall="#f0c9b8", side="#d9a896", roof="#fbe3d6", door="#5a2a3a", ladder=True):
    """Çatalhöyük-style flat-roofed mud-brick house front (2D), roof hatch with ladder."""
    o = [rect(x, y - h, w, h, wall), rect(x + w, y - h + 12, w * .18, h - 12, side),
         poly([(x, y - h), (x + w * .18, y - h - w * .12), (x + w * 1.18, y - h - w * .12), (x + w, y - h)], roof),
         rect(x + w * .3, y - h * .6, w * .16, h * .22, door, rx=4)]
    if ladder:
        lx = x + w * .62
        o.append(stroke("M%.0f %.0f l%.0f -%.0f M%.0f %.0f l%.0f -%.0f" % (
            lx, y - h - w * .06, w * .04, h * .45, lx + w * .14, y - h - w * .06, w * .04, h * .45), "#7a4a2a", 6))
        for k in range(3):
            o.append(stroke("M%.0f %.0f h%.0f" % (lx + w * .01 * k, y - h - w * .06 - k * h * .14, w * .14),
                            "#7a4a2a", 5))
    return "".join(o)


def skull(x, y, s, bone="#f3e6cf", bone_d="#d9c39a", eye="#3a1830", deco=None):
    o = [ellipse(x, y, 60 * s, 55 * s, bone), path("M%.0f %.0f a%.0f %.0f 0 0 1 %.0f %.0f l-%.0f %.0f z" % (
        x + 10 * s, y - 52 * s, 50 * s, 55 * s, 48 * s, 60 * s, 40 * s, 20 * s), bone_d),
        rect(x - 34 * s, y + 30 * s, 62 * s, 40 * s, bone, rx=12 * s),
        ellipse(x - 24 * s, y + 4 * s, 16 * s, 18 * s, eye), ellipse(x + 20 * s, y + 4 * s, 14 * s, 17 * s, eye),
        poly([(x - 4 * s, y + 18 * s), (x + 4 * s, y + 18 * s), (x, y + 30 * s)], eye)]
    for k in range(4):
        o.append(rect(x - 26 * s + k * 14 * s, y + 46 * s, 4 * s, 16 * s, bone_d))
    if deco:   # plastered / painted skull (Neolithic plastered skulls)
        o.append(path("M%.0f %.0f q%.0f -%.0f %.0f 0" % (x - 40 * s, y - 20 * s, 40 * s, 30 * s, 80 * s), "none",
                      stroke=deco, stroke_width=10 * s, stroke_linecap="round"))
        for k in range(3):
            o.append(circle(x - 20 * s + k * 20 * s, y - 34 * s, 6 * s, deco))
    return "".join(o)


def bones(x, y, s, col="#f3e6cf", seed=1, n=9):
    r = random.Random(seed)
    o = []
    for _ in range(n):
        bx, by = x + r.uniform(-220, 220) * s, y + r.uniform(-60, 60) * s
        a = r.uniform(0, 180)
        L = r.uniform(40, 90) * s
        o.append(g(rect(-L / 2, -6 * s, L, 12 * s, col, rx=6 * s), circle(-L / 2, -6 * s, 9 * s, col),
                   circle(-L / 2, 6 * s, 9 * s, col), circle(L / 2, -6 * s, 9 * s, col), circle(L / 2, 6 * s, 9 * s, col),
                   transform="translate(%.0f %.0f) rotate(%.0f)" % (bx, by, a)))
    return "".join(o)


# ------------------------------------------------------------------ characters
STYLES = {
    "guide": dict(skin="#c98a5e", hair="#2b1d4f", top="#f0b43a", bottom="#1f5560", shoe="#3b2236",
                  scarf="#d63c3c", pack="#2e8a78", body="shirt", hairdo="short"),
    "woman": dict(skin="#d4573a", hair="#3b1f6e", top="#1f7a8c", bottom=None, shoe=None, spots="#2b93a6",
                  belt="#f2c14e", body="dress", hairdo="bun", earrings="#f2c14e", lips="#9e2a2a"),
    "man": dict(skin="#c9643c", hair="#3b1f6e", top="#f0a83a", bottom="#b5772f", shoe=None, spots="#f7c25a",
                belt="#f2c14e", body="tunic", hairdo="beard", band="#f2c14e"),
    "elder": dict(skin="#b8603e", hair="#d9cfe8", top="#7a3a68", bottom="#5a2a50", shoe=None, spots="#9a5a88",
                  body="tunic", hairdo="beard"),
    "child": dict(skin="#d06a44", hair="#3b1f6e", top="#e2682a", bottom=None, shoe=None, body="dress",
                  hairdo="short", scale=0.62),
    "shaman": dict(skin="#c9643c", hair="#3b1f6e", top="#2e8a78", bottom="#1f5560", shoe=None, spots="#f2c14e",
                   body="tunic", hairdo="beard", horns="#f3e6cf", cape="#3aa08a"),
    "worker": dict(skin="#a8583a", hair="#2b1d4f", top="#e8925a", bottom="#7a3a2a", shoe=None, body="tunic",
                   hairdo="short"),
}


def _arm(sx, sy, side, ang, elb, L1, L2):
    a1 = math.radians(ang)
    ex, ey = sx + side * math.sin(a1) * L1, sy + math.cos(a1) * L1
    a2 = math.radians(ang + elb)
    hx, hy = ex + side * math.sin(a2) * L2, ey + math.cos(a2) * L2
    return (ex, ey), (hx, hy)


def _prop(kind, hx, hy, side, ang):
    s = side
    if kind == "torch":
        return (stroke("M%.0f %.0f l%.0f -%.0f" % (hx, hy + 30, s * 18, 190), "#3b2a5a", 22) +
                g(path("M%.0f %.0f c30 40 40 80 0 110 c-40 -30 -30 -70 0 -110 z" % (hx + s * 22, hy - 260), "#ff7a2e"),
                  path("M%.0f %.0f c16 24 20 46 0 64 c-20 -18 -16 -40 0 -64 z" % (hx + s * 22, hy - 215), "#ffe27a"),
                  data_anim="flicker pulse", data_amp="0.1", data_period="0.5"))
    if kind == "bowl":
        return path("M%.0f %.0f h110 c0 50 -24 70 -55 70 c-31 0 -55 -20 -55 -70 z" % (hx - 55, hy - 30), "#2e8a78") + \
            path("M%.0f %.0f h110 c-4 -10 -106 -10 -110 0 z" % (hx - 55, hy - 30), "#f2c14e")
    if kind == "chisel":
        return stroke("M%.0f %.0f l%.0f %.0f" % (hx, hy, s * 90, -40), "#6b3f22", 16) + \
            poly([(hx + s * 86, hy - 50), (hx + s * 120, hy - 60), (hx + s * 96, hy - 30)], "#9aa7b8")
    if kind == "spear":
        return stroke("M%.0f %.0f l%.0f -%.0f" % (hx - s * 20, hy + 200, s * 60, 480), "#6b3f22", 12) + \
            poly([(hx + s * 40, hy - 280), (hx + s * 58, hy - 340), (hx + s * 30, hy - 290)], "#2a1c4f")
    if kind == "bundle":
        o = []
        for k in range(7):
            o.append(stroke("M%.0f %.0f l%.0f -%.0f" % (hx, hy, s * (k * 10 - 30), 170), "#d9a43a", 6))
            o.append(ellipse(hx + s * (k * 10 - 30), hy - 180, 9, 22, "#f2c14e"))
        return "".join(o)
    if kind == "tablet":
        return rect(hx - 60, hy - 90, 120, 150, "#d9824a", rx=14) + rect(hx - 44, hy - 72, 88, 10, "#b8603a") + \
            rect(hx - 44, hy - 50, 60, 10, "#b8603a") + rect(hx - 44, hy - 28, 75, 10, "#b8603a")
    if kind == "skull":
        return skull(hx, hy - 40, 0.75, deco="#e2682a")
    if kind == "straw":
        return stroke("M%.0f %.0f l%.0f %.0f" % (hx, hy, s * 160, 220), "#d9a43a", 9)
    return ""


def person(x, y, h, style="woman", view="front", arms=None, legs="stand", hold=None, face="calm", flip=False,
           anim=None, rim="scene", depth=None, swap=None, **over):
    if rim == "scene":
        rim = DEFAULT_RIM[0]
    st = dict(STYLES[style])
    st.update(over)
    k = h / 1000.0 * st.get("scale", 1.0) / (st.get("scale", 1.0))
    skin, skin_d = st["skin"], shade(st["skin"])
    top, top_d = st["top"], shade(st["top"])
    hair, hair_d = st["hair"], shade(st["hair"], 0.7)
    arms = dict(dict(l=(8, 4), r=(8, 4)), **(arms or {}))
    hold = hold or {}
    side_view = view in ("right", "left")
    o = []
    # ----- legs
    sit = legs == "sit"
    kneel = legs == "kneel"
    walk_ph = None
    if isinstance(legs, tuple):
        walk_ph = legs[1]
    elif legs == "walk":
        walk_ph = 0.25
    hipy = 640
    if sit:
        hipy = 820
        o.append(path("M300 940 C300 890 360 862 430 862 C500 862 560 890 560 940 C560 975 510 990 430 990 C350 990 300 975 300 940 Z",
                      st.get("bottom") or top_d))
    elif kneel:
        hipy = 760
        fwd = -1 if view in ("left", "left3") else 1
        for s, c in ((-1, skin_d), (1, skin)):
            hx = 430 + s * 30
            o.append(stroke("M%.0f %.0f Q%.0f %.0f %.0f %.0f L%.0f %.0f" % (
                hx, hipy, hx + fwd * 90, hipy + 60, hx + fwd * 110, 950, hx - fwd * 90, 975),
                st.get("bottom") if st["body"] == "shirt" else c, 80))
    else:
        for s, c in ((-1, skin_d), (1, skin)):
            hx = 430 + s * 42
            if walk_ph is not None:
                sw = math.sin(walk_ph * 2 * math.pi) * 90 * s
                d = "M%.0f %.0f Q%.0f %.0f %.0f %.0f" % (hx, hipy, hx + sw * .4, 820, hx + sw, 975)
            else:
                d = "M%.0f %.0f Q%.0f %.0f %.0f %.0f" % (hx, hipy, hx + s * 6, 820, hx + s * 4, 975)
            col = st.get("bottom") if st["body"] == "shirt" else c
            o.append(stroke(d, col, 84))
            fx = hx + (math.sin(walk_ph * 2 * math.pi) * 90 * s if walk_ph is not None else s * 4)
            if st.get("shoe"):
                o.append(ellipse(fx + (24 if not side_view else 36) * (1 if view != "left" else -1), 985, 58, 26,
                                 st["shoe"]))
            else:
                o.append(ellipse(fx + (16 if view != "left" else -16), 984, 42, 18, c))
    by = hipy - 640    # body offset (sitting lowers the torso)
    # ----- torso
    T = lambda d, c: o.append(path(d, c))  # noqa: E731
    if st["body"] == "dress":
        T("M%d %d C%d %d %d %d 430 %d C%d %d %d %d %d %d L%d %d H%d Z" % (
            358, 420 + by, 358, 390 + by, 390, 372 + by, 372 + by, 470, 372 + by, 502, 390 + by, 502, 420 + by,
            526, 780 + by, 334), top)
        T("M430 %d C470 %d 502 %d 502 %d L526 %d H444 C462 %d 458 %d 430 %d Z" % (
            372 + by, 372 + by, 390 + by, 420 + by, 780 + by, 660 + by, 500 + by, 372 + by), top_d)
    else:
        bot = 700 if st["body"] == "tunic" else 650
        T("M350 %d C350 %d 386 %d 430 %d C474 %d 510 %d 510 %d L522 %d H338 Z" % (
            420 + by, 388 + by, 370 + by, 370 + by, 370 + by, 388 + by, 420 + by, bot + by), top)
        T("M430 %d C474 %d 510 %d 510 %d L522 %d H446 C464 %d 460 %d 430 %d Z" % (
            370 + by, 370 + by, 388 + by, 420 + by, bot + by, 600 + by, 480 + by, 370 + by), top_d)
        if st["body"] == "tunic" and st.get("bottom"):
            o.append(poly([(338, 620 + by), (522, 620 + by), (530, 720 + by), (330, 720 + by)], st["bottom"]))
        if st["body"] == "shirt":
            o.append(rect(340, 610 + by, 180, 50, st["bottom"], rx=10))
    if st.get("spots"):
        rr = random.Random(len(style))
        for _ in range(5):
            o.append(circle(rr.uniform(370, 480), rr.uniform(450, 700) + by, 15, st["spots"]))
    if st.get("belt"):
        o.append(rect(352, 540 + by, 156, 18, st["belt"], rx=8))
    if st.get("cape"):
        o.insert(0, path("M340 %d L300 %d H560 L520 %d Z" % (400 + by, 760 + by, 400 + by), st["cape"]))
    if view == "back" and st.get("pack"):
        o.append(rect(368, 400 + by, 124, 200, st["pack"], rx=34))
        o.append(rect(386, 500 + by, 88, 64, shade(st["pack"]), rx=18))
    elif st.get("pack") and view != "back":
        o.append(rect(372, 390 + by, 14, 190, st["pack"], rx=7) + rect(474, 390 + by, 14, 190, shade(st["pack"]),
                                                                       rx=7))
    if st.get("scarf"):
        o.append(path("M378 %d C398 %d 462 %d 482 %d L496 %d C468 %d 392 %d 364 %d Z" % (
            370 + by, 398 + by, 398 + by, 370 + by, 394 + by, 430 + by, 430 + by, 394 + by), st["scarf"]))
    # ----- head
    hcx, hcy = 430, 250 + by
    o.append(rect(412, 300 + by, 36, 80, skin_d))
    head = []
    if view == "back":
        head.append(circle(hcx, hcy, 98, hair))
        head.append(path("M%d %d A98 98 0 0 1 %d %d A98 98 0 0 1 %d %d Z" % (hcx, hcy - 98, hcx + 98, hcy, hcx, hcy + 98),
                         hair_d))
        head.append(ellipse(hcx - 96, hcy + 8, 16, 22, skin_d))
        head.append(ellipse(hcx + 96, hcy + 8, 16, 22, skin_d))
    else:
        fx = {"front": 0, "right3": 26, "left3": -26, "right": 52, "left": -52}[view]
        head.append(path("M%d %d C%d %d %d %d %d %d C%d %d %d %d %d %d C%d %d %d %d %d %d C%d %d %d %d %d %d Z" % (
            hcx, hcy - 100, hcx + 64, hcy - 100, hcx + 102, hcy - 52, hcx + 102, hcy + 6,
            hcx + 102, hcy + 66, hcx + 58, hcy + 98, hcx, hcy + 98,
            hcx - 58, hcy + 98, hcx - 102, hcy + 66, hcx - 102, hcy + 6,
            hcx - 102, hcy - 52, hcx - 64, hcy - 100, hcx, hcy - 100), skin))
        head.append(path("M%d %d C%d %d %d %d %d %d C%d %d %d %d %d %d C%d %d %d %d %d %d Z" % (
            hcx + 40, hcy - 92, hcx + 86, hcy - 70, hcx + 104, hcy - 20, hcx + 100, hcy + 20,
            hcx + 94, hcy + 70, hcx + 60, hcy + 96, hcx + 14, hcy + 98,
            hcx + 64, hcy + 60, hcx + 74, hcy - 20, hcx + 40, hcy - 92), skin_d))
        if view in ("front", "right3", "left3"):
            for s in (-1, 1):
                if (view == "right3" and s == 1) or (view == "left3" and s == -1):
                    continue
                head.append(ellipse(hcx + s * 100, hcy + 10, 16, 22, skin_d))
        else:
            head.append(ellipse(hcx - fx * 0.4, hcy + 10, 18, 24, skin_d))
        # nose for 3/4 and profile
        if view != "front":
            sgn = 1 if fx > 0 else -1
            head.append(path("M%d %d q%d %d 0 %d" % (hcx + fx + sgn * 30, hcy + 4, sgn * 24, 18, 34), skin))
        ink = "#1c1230"
        eyes = [(-34, 0), (34, 0)] if view == "front" else ([(fx - 30, 0), (fx + 28, 0)] if view in ("right3", "left3")
                                                            else [(fx + (14 if fx > 0 else -14), 0)])
        for ex, _ in eyes:
            if face in ("sleepy", "calm"):
                head.append(path("M%d %d h34 a17 13 0 0 1 -34 0 z" % (hcx + ex - 17, hcy + 14), ink))
            elif face == "happy":
                head.append(stroke("M%d %d q14 -14 28 0" % (hcx + ex - 14, hcy + 22), ink, 8))
            else:   # open / surprised / focus
                head.append(ellipse(hcx + ex, hcy + 16, 9, 12, ink))
            bd = -6 if face in ("worry", "sad") else (6 if face == "angry" else 0)
            head.append(rect(hcx + ex - 22, hcy - 16, 44, 13, hair, rx=6,
                             transform="rotate(%d %d %d)" % (bd * (1 if ex < 0 else -1), hcx + ex, hcy - 10)))
        mx = hcx + (fx * 0.9 if view != "front" else 0)
        if face in ("open", "surprised", "happy", "talk"):
            head.append(ellipse(mx, hcy + 62, 16, 13, "#7a2a2e"))
        elif st.get("lips"):
            head.append(ellipse(mx, hcy + 60, 20, 10, st["lips"]))
        # hair
        if st["hairdo"] in ("short", "beard", "bun", "long"):
            head.append(path("M%d %d C%d %d %d %d %d %d C%d %d %d %d %d %d C%d %d %d %d %d %d C%d %d %d %d %d %d Z" % (
                hcx - 108, hcy + 20, hcx - 122, hcy - 70, hcx - 60, hcy - 128, hcx + 4, hcy - 126,
                hcx + 80, hcy - 124, hcx + 124, hcy - 70, hcx + 108, hcy + 4,
                hcx + 86, hcy - 42, hcx + 30, hcy - 64, hcx - 20, hcy - 56,
                hcx - 60, hcy - 50, hcx - 92, hcy - 20, hcx - 108, hcy + 20), hair))
        if st["hairdo"] == "bun":
            head.append(circle(hcx + 46 - fx * .3, hcy - 120, 58, mix(hair, "#ffffff", 0.12)))
        if st["hairdo"] == "long":
            head.append(path("M%d %d C%d %d %d %d %d %d L%d %d C%d %d %d %d %d %d Z" % (
                hcx - 106, hcy + 10, hcx - 120, hcy + 120, hcx - 100, hcy + 200, hcx - 70, hcy + 230,
                hcx - 50, hcy + 180, hcx - 80, hcy + 120, hcx - 86, hcy + 60, hcx - 90, hcy + 10), hair))
        if st["hairdo"] == "beard" and view != "back":
            head.append(path("M%d %d C%d %d %d %d %d %d C%d %d %d %d %d %d C%d %d %d %d %d %d Z" % (
                hcx - 80 + fx * .5, hcy + 30, hcx - 76 + fx * .5, hcy + 120, hcx - 30 + fx * .5, hcy + 168,
                hcx + fx * .5, hcy + 170, hcx + 40 + fx * .5, hcy + 168, hcx + 78 + fx * .5, hcy + 120,
                hcx + 80 + fx * .5, hcy + 30, hcx + 40 + fx * .5, hcy + 70, hcx - 40 + fx * .5, hcy + 70,
                hcx - 80 + fx * .5, hcy + 30), hair))
            head.append(stroke("M%d %d q24 10 48 0" % (mx - 24, hcy + 74), mix(hair, "#ffffff", 0.2), 9))
        if st.get("band"):
            head.append(rect(hcx - 104, hcy - 58, 208, 22, st["band"], rx=10))
        if st.get("earrings") and view == "front":
            for s in (-1, 1):
                head.append(circle(hcx + s * 104, hcy + 40, 11, st["earrings"]))
    if st.get("horns"):
        for s in (-1, 1):
            head.append(path("M%d %d q%d -%d %d -%d q-%d %d -%d %d z" % (
                hcx + s * 60, hcy - 90, s * 30, 90, s * 110, 140, s * 50, 40, s * 120, 120), st["horns"]))
            head.append(path("M%d %d q%d -%d %d -%d" % (hcx + s * 120, hcy - 190, s * 30, 40, s * 70, 30), "none",
                             stroke=st["horns"], stroke_width=16, stroke_linecap="round"))
    o.extend(head)
    # ----- arms (drawn after the body; back arm first)
    order = ("l", "r")
    arm_col = {"l": top if st["body"] == "shirt" else skin, "r": top_d if st["body"] == "shirt" else skin_d}
    sh_y = 400 + by
    for side_key in order:
        side = -1 if side_key == "l" else 1
        ang, elb = arms[side_key]
        sx = 430 + side * (70 if not side_view else 20)
        L1, L2 = 160, 148
        # front view: arms open outward; turned views: both arms reach toward the facing direction
        facing = {"right": 1, "right3": 1, "left": -1, "left3": -1}.get(view)
        dirn = facing if facing else side
        (ex, ey), (hx, hy) = _arm(sx, sh_y, dirn, ang, elb, L1, L2)
        if side_view and side_key == "l":    # far arm in profile: tucked a bit behind
            col = shade(arm_col["l"], 0.85)
        else:
            col = arm_col[side_key]
        o.append(stroke("M%.0f %.0f Q%.0f %.0f %.0f %.0f" % (sx, sh_y, ex, ey, hx, hy), col, 72))
        o.append(circle(hx, hy, 32, skin if side_key == "l" else skin_d))
        if hold.get(side_key):
            o.append(_prop(hold[side_key], hx, hy, dirn, ang))
    if hold.get("head") == "basket":
        o.append(path("M300 %d H560 L540 %d H320 Z" % (60 + by, 122 + by), "#c07a2e"))
        o.append(path("M306 %d C340 %d 520 %d 554 %d Z" % (62 + by, 6 + by, 6 + by, 62 + by), "#f2c14e"))
    sc = h / 1000.0
    tr = "translate(%.1f %.1f) scale(%s%.4f %.4f) translate(-430 -1000)" % (x, y, "-" if flip else "", sc, sc)
    kw = dict(transform=tr)
    outer = dict(data_anim=anim.split("|")[0] if anim else None, data_rim=rim, data_depth=depth)
    if anim and "|" in anim:   # "bob|data-amp=3,data-period=2"
        import re as _re
        for kv in _re.split(r",(?=data-)", anim.split("|")[1]):
            a_, b_ = kv.split("=")
            outer[a_.replace("-", "_")] = b_
    return g(g(*o, **kw), **outer)


def include(file, x, y, h, pose=None, poses=None, flip=False, swap=None, anim=None, depth=None, **extra):
    """Place a hand-drawn character file (chars/guide.svg, villager.svg, man.svg) like ten_sec_v4 does."""
    kw = dict(data_include=file, data_x=x, data_y=y, data_h=h, data_pose=pose, data_poses=poses,
              data_flip="1" if flip else None, data_swap=swap, data_depth=depth)
    if anim:
        a, _, rest = anim.partition("|")
        kw["data_anim"] = a
        if rest:
            import re as _re
            for kv in _re.split(r",(?=data-)", rest):
                k_, v_ = kv.split("=")
                kw[k_.replace("-", "_")] = v_
    kw.update(extra)
    return "<g %s/>" % attrs(**kw)
