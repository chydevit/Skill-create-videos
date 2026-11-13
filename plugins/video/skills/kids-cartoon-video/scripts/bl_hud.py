"""On-screen overlay (HUD) attached to the camera: word cards, captions,
"your turn" badge, star bursts and emoji faces."""
import hashlib
import math
import os
import subprocess

import bpy
import bmesh
import numpy as np

import bl_util as U
from bl_util import empty, obj, text_obj, flat, mat, sphere, pop_curve, smooth

FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
KHMER_FONT = "Khmer MN Bold"
RENDER_TEXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "render_text")
TEXT_CACHE = None          # set by bl_main to <project>/build/text
PX_PER_UNIT = 1600         # pixel density of rendered text images
KHMER_SCALE = 0.74         # Khmer MN draws larger than Arial Rounded at the same size


def needs_shaping(text):
    """Blender's text objects cannot shape complex scripts such as Khmer."""
    return any(0x1780 <= ord(ch) <= 0x19FF for ch in text)


def _image_plane(name, png, w, h, parent, loc):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new()
    vs = [bm.verts.new((x * w / 2, y * h / 2, 0)) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    f = bm.faces.new(vs)
    for loop, (u, v) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop[uv].uv = (u, v)
    bm.to_mesh(me)
    bm.free()
    m = bpy.data.materials.new(name + "_m")
    m.use_nodes = True
    try:
        m.surface_render_method = "BLENDED"
    except AttributeError:
        m.blend_method = "BLEND"
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(png, check_existing=True)
    tex.interpolation = "Cubic"
    em = nt.nodes.new("ShaderNodeEmission")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    nt.links.new(tex.outputs["Alpha"], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = parent
    ob.location = loc
    return ob


def shaped_text(name, body, size, color, outline, parent, z, ow, max_w=None):
    """Render text with CoreText to a PNG and show it on a plane.
    Returns (object, content width, content height) in HUD units."""
    font_px = size * PX_PER_UNIT * KHMER_SCALE
    out_px = (size * ow * PX_PER_UNIT) if outline else 0
    key = hashlib.md5(f"{body}|{font_px}|{color}|{outline}|{out_px}|{max_w}".encode()).hexdigest()[:16]
    os.makedirs(TEXT_CACHE, exist_ok=True)
    png = os.path.join(TEXT_CACHE, key + ".png")
    args = [RENDER_TEXT, body, KHMER_FONT, "%.1f" % font_px, color, outline or "#000000",
            "%.1f" % out_px, png]
    if max_w:
        args.append("%.0f" % (max_w * PX_PER_UNIT))
    res = subprocess.run(args, check=True, capture_output=True, text=True).stdout.split()
    W, H = (int(v) for v in res[0].split("x"))
    pad = float(res[1])
    w, h = W / PX_PER_UNIT, H / PX_PER_UNIT
    ob = _image_plane(name, png, w, h, parent, (0, 0, z + 0.008))
    return ob, w - 2 * pad / PX_PER_UNIT, h - 2 * pad / PX_PER_UNIT

HALF_W = 18 / 35          # visible half width at distance 1 (35 mm lens)
HALF_H = HALF_W * 9 / 16

SPEAKER_TINT = {"milo": "#E6501E", "luna": "#8E24AA", "bobo": "#0277BD",
                "narr": "#37474F", "all": "#2E7D32", "ml": "#2E7D32",
                "cat": "#6D4C41", "dog": "#6D4C41", "duck": "#6D4C41", "cow": "#6D4C41"}


def darker(hexcol, f=0.55):
    h = hexcol.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % (int(r * f), int(g * f), int(b * f))


def wrap(text, maxc):
    if len(text) <= maxc or "\n" in text:
        return text
    mid = len(text) // 2
    best = None
    for i, ch in enumerate(text):
        if ch == " " and (best is None or abs(i - mid) < abs(best - mid)):
            best = i
    if best is None:
        return text
    return text[:best] + "\n" + text[best + 1:]


class HUD:
    def __init__(self, cam, A, ui=None):
        self.A = A
        self.ui = ui or {"your_turn": "YOUR TURN!"}
        self.font = bpy.data.fonts.load(FONT_PATH, check_existing=True)
        self.root = empty("hud", (0, 0, -1.0), cam)
        self.n = 0
        self.emojis = {}

    def _name(self, p):
        self.n += 1
        return "%s%03d" % (p, self.n)

    def _text(self, parent, body, size, color, outline=None, z=0.0, ow=0.07, max_w=None):
        """Text with an outline behind it. Returns (text, width, height)."""
        if needs_shaping(body):
            return shaped_text(self._name("img"), body, size, color, outline, parent, z,
                               ow, max_w)
        t = text_obj(self._name("txt"), body, size, flat(color), self.font, parent,
                     (0, 0, z + 0.008))
        if outline:
            o = text_obj(self._name("out"), body, size, flat(outline), self.font, parent,
                         (0, 0, z + 0.004), offset=size * ow)
        bpy.context.view_layer.update()
        d = t.dimensions
        return t, d.x, d.y

    def _pop(self, ob, t0, t1, base=1.0, tin=0.35):
        A = self.A
        v = pop_curve(A.t, t0, t1, tin=tin) * base
        for i in range(3):
            A.set(ob, "scale", i, v)

    # ----------------------------------------------------------- cards
    def card(self, text, color, t0, t1, style):
        g = empty(self._name("card"), (0, 0, 0), self.root)
        white = color.upper() == "#FFFFFF"
        if style == "word":
            g.location = (0, 0.185, 0.02)
            size, pad = 0.085, (0.07, 0.04)
        elif style == "sentence":
            g.location = (0, 0.2, 0.02)
            size, pad = 0.052, (0.06, 0.035)
            if not needs_shaping(text):
                text = wrap(text, 30)
        elif style == "number":
            g.location = (0, 0.165, 0.02)
            size, pad = 0.14, (0.05, 0.02)
        else:  # title
            g.location = (0, 0.04, 0.03)
            size, pad = 0.085, (0.08, 0.05)
        outline = "#E65100" if white else darker(color)
        _, w, h = self._text(g, text, size, color, outline, ow=0.06, max_w=0.85)
        if style == "number":
            r = max(w, h) / 2 + pad[0]
            obj(self._name("disc"), U.mesh_rrect(2 * r, 2 * r, r, 16), (0, 0, 0), 1,
                m=flat("#FFFFFF", 0.95), parent=g)
        elif style == "title":
            obj(self._name("pan"), U.mesh_rrect(w + 2 * pad[0], h + 2 * pad[1], 0.05),
                (0, 0, 0), 1, m=flat("#FFFFFF", 0.35), parent=g)
            for k, (x, y, c) in enumerate(((-1, 1, "#FFD600"), (1, 1, "#FF4081"),
                                           (-1, -1, "#40C4FF"), (1, -1, "#76FF03"))):
                st = obj(self._name("tst"), U.mesh_star(5, 1, 0.45, 0.3),
                         (x * (w / 2 + pad[0]), y * (h / 2 + pad[1] * 0.4), 0.01),
                         0.035, (-math.pi / 2, 0, 0), flat(c), g)
                A = self.A
                A.set(st, "rotation_euler", 2, 0.4 * np.sin(2 * math.pi * 0.5 * A.t + k))
        else:
            obj(self._name("pan"), U.mesh_rrect(w + 2 * pad[0], h + 2 * pad[1], 0.035),
                (0, 0, 0), 1, m=flat("#FFFFFF", 0.93), parent=g)
            obj(self._name("pbd"), U.mesh_rrect(w + 2 * pad[0] + 0.012, h + 2 * pad[1] + 0.012,
                                                 0.041),
                (0, 0, -0.0005), 1, m=flat(color if not white else "#FF9800"), parent=g)
        self._pop(g, t0, t1)
        # keep tall (multi-line) cards inside the top of the frame
        if style != "title":
            top = HALF_H - 0.012 - (h / 2 + pad[1] + 0.006)
            g.location[1] = min(g.location[1], top)
        # gentle float
        A = self.A
        A.set(g, "location", 1, g.location[1] + 0.004 * np.sin(2 * math.pi * 0.6 * A.t))

    def caption(self, text, who, t0, t1):
        g = empty(self._name("cap"), (0, -0.228, 0.01), self.root)
        if not needs_shaping(text):
            text = wrap(text, 36)
        _, w, h = self._text(g, text, 0.036, "#FFFFFF", "#000000", ow=0.04, max_w=0.85)
        obj(self._name("cpan"), U.mesh_rrect(w + 0.06, h + 0.035, 0.025), (0, 0, 0), 1,
            m=flat(SPEAKER_TINT.get(who, "#37474F"), 0.78), parent=g)
        A = self.A
        v = smooth((A.t - t0) / 0.15) * smooth((t1 - A.t) / 0.15)
        v = np.where((A.t < t0) | (A.t > t1), 0.0, v)
        for i in range(3):
            A.set(g, "scale", i, v)

    def turn(self, t0, t1):
        g = empty(self._name("turn"), (0, -0.215, 0.012), self.root)
        _, w, h = self._text(g, self.ui["your_turn"], 0.048, "#FFFFFF", "#BF360C", ow=0.05)
        obj(self._name("tpan"), U.mesh_rrect(w + 0.19, h + 0.045, 0.035), (0, 0, 0), 1,
            m=flat("#FF7043", 0.95), parent=g)
        A = self.A
        # sound-wave dots that fill in one by one
        n = 3
        for k in range(n):
            for sd in (-1, 1):
                d = obj(self._name("dot"), U.mesh_rrect(0.02, 0.02, 0.01, 6),
                        (sd * (w / 2 + 0.03 + k * 0.022), 0, 0.003), 1,
                        m=flat("#FFFFFF"), parent=g)
                tk = t0 + (t1 - t0) * (k + 0.5) / (n + 0.5)
                v = 0.5 + 0.7 * smooth((A.t - tk) / 0.15)
                for i in range(3):
                    A.set(d, "scale", i, v)
        v = pop_curve(A.t, t0, t1) * (1 + 0.04 * np.sin(2 * math.pi * 1.6 * A.t))
        for i in range(3):
            A.set(g, "scale", i, v)

    def stars(self, t0):
        A = self.A
        rng = np.random.default_rng(int(t0 * 100))
        cols = ["#FFD600", "#FFAB00", "#FF4081", "#40C4FF", "#76FF03", "#FFFFFF"]
        for k in range(14):
            a = 2 * math.pi * k / 14 + rng.uniform(-0.2, 0.2)
            r = rng.uniform(0.2, 0.42)
            x0, y0 = r * math.cos(a) * 1.2, r * math.sin(a) * 0.62
            st = obj(self._name("star"), U.mesh_star(5, 1, 0.45, 0.3), (x0, y0, 0.05),
                     1, (-math.pi / 2, 0, 0), flat(cols[k % len(cols)]), self.root)
            tt = t0 + rng.uniform(0, 0.3)
            u = (A.t - tt) / 1.3
            sz = rng.uniform(0.018, 0.032)
            v = np.where((u < 0) | (u > 1), 0.0, np.sin(np.pi * np.clip(u, 0, 1)) ** 0.6 * sz)
            for i in range(3):
                A.set(st, "scale", i, v)
            A.set(st, "location", 1, y0 + 0.06 * np.clip(u, 0, 1))
            A.set(st, "rotation_euler", 2, 3 * np.clip(u, 0, 1) * rng.choice([-1, 1]))

    # ------------------------------------------------------------ emojis
    def build_emojis(self):
        for kind in ("happy", "sad", "excited", "tired", "surprised"):
            g = empty("emoji_" + kind, (0.37, -0.02, 0.05), self.root)
            g.scale = (0, 0, 0)
            make_emoji(g, kind, 0.085)
            self.emojis[kind] = g

    def emoji_track(self, shows, t_end):
        """shows: list of (t, kind or 'none')."""
        A = self.A
        shows = sorted(shows)
        vals = {k: np.zeros(A.nf) for k in self.emojis}
        for i, (t0, kind) in enumerate(shows):
            t1 = shows[i + 1][0] if i + 1 < len(shows) else t_end
            if kind in vals:
                vals[kind] += pop_curve(A.t, t0, t1 - 0.05)
        for k, g in self.emojis.items():
            v = vals[k] * (1 + 0.03 * np.sin(2 * math.pi * 1.2 * A.t))
            for i in range(3):
                A.set(g, "scale", i, v)
            A.set(g, "rotation_euler", 2, 0.12 * np.sin(2 * math.pi * 0.7 * A.t))


def make_emoji(g, kind, r, lit=False):
    """Emoji face in the XY plane of g, looking toward +Z (the camera)."""
    face = mat("#FFD54F", 0.35, emit=0.35) if not lit else mat("#FFD54F", 0.35)
    dark = flat("#4E342E")
    pi = math.pi
    # the face is a sphere flattened toward the viewer
    sphere("emf_" + kind + g.name, (0, 0, 0), (r, r, r * 0.35), face, g)
    red = flat("#C62828")
    ex, ey = 0.36 * r, 0.22 * r
    z = r * 0.36

    def eye(x, y, sx=0.11, sy=0.17):
        sphere("eme" + g.name + str(x), (x, y, z), (sx * r, sy * r, 0.05 * r), dark, g)

    def arc(x, y, R, rot, name, width=0.045):
        # torus arc lying in the XY plane
        a = obj("ema" + name + g.name, U.mesh_torus(R, width * r, 20, 8, pi, pi),
                (x, y, z), 1, (-pi / 2, 0, rot), dark, g)
        return a

    if kind == "happy":
        eye(-ex, ey), eye(ex, ey)
        arc(0, -0.05 * r, 0.45 * r, 0, "m")
    elif kind == "sad":
        eye(-ex, ey * 0.8), eye(ex, ey * 0.8)
        arc(0, -0.45 * r, 0.33 * r, pi, "m")
        sphere("emt" + g.name, (ex + 0.05 * r, -0.05 * r, z), (0.07 * r, 0.12 * r, 0.04 * r),
               flat("#29B6F6"), g)
    elif kind == "excited":
        for x in (-ex, ex):
            obj("ems" + g.name + str(x), U.mesh_star(5, 1, 0.45, 0.3), (x, ey, z), 0.16 * r,
                (-pi / 2, 0, 0), flat("#FF6D00"), g)
        sphere("emm" + g.name, (0, -0.3 * r, z * 0.9), (0.42 * r, 0.26 * r, 0.05 * r), red, g)
        sphere("emmt" + g.name, (0, -0.16 * r, z * 0.95), (0.42 * r, 0.1 * r, 0.05 * r),
               flat("#FFFFFF"), g)
    elif kind == "tired":
        arc(-ex, ey + 0.05 * r, 0.14 * r, 0, "l", 0.035)
        arc(ex, ey + 0.05 * r, 0.14 * r, 0, "r", 0.035)
        sphere("emm" + g.name, (0, -0.4 * r, z), (0.13 * r, 0.1 * r, 0.04 * r), dark, g)
        zz = text_obj("emz" + g.name, "z z", 0.35 * r, flat("#5C6BC0"),
                      bpy.data.fonts.load(FONT_PATH, check_existing=True), g,
                      (0.65 * r, 0.75 * r, z))
    elif kind == "surprised":
        eye(-ex, ey, 0.13, 0.2), eye(ex, ey, 0.13, 0.2)
        sphere("emm" + g.name, (0, -0.42 * r, z), (0.16 * r, 0.2 * r, 0.05 * r), dark, g)
        for x in (-ex, ex):
            obj("emb" + g.name + str(x), U.mesh_torus(0.16 * r, 0.03 * r, 16, 6, pi * 0.2,
                                                      pi * 0.4),
                (x, ey + 0.2 * r, z), 1, (-pi / 2, 0, 0), dark, g)
