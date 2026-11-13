"""Toon 3D kit for the flat-explainer look in Blender (EEVEE, Blender 4.2+ / 5.x).

Everything is unlit-looking flat colour: the light that reaches a surface is quantized into a few hard bands
(deep / shade / mid / lit / hot) and a warm rim is added on the silhouette - but only where the surface is lit.
Point lights therefore paint the reference's concentric light rings on the ground for free.
View transform must be "Standard" so the hex colours come out exactly.
"""
import math
import random

import bpy
from mathutils import Vector

FPS = 60


# ------------------------------------------------------------------ colour
def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgba(h, a=1.0):
    h = h.lstrip("#")
    return tuple(lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (a,)


def hexmix(a, b, t):
    a, b = a.lstrip("#"), b.lstrip("#")
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * t) for x, y in zip(ca, cb))


def shade_of(c, night=False):
    """Shadow tone the reference way: darker and pushed toward violet."""
    return hexmix(hexmix(c, "#000000", 0.38), "#3b1f6e", 0.30 if not night else 0.45)


# ------------------------------------------------------------------ materials
_M = {}


def _inp(node, name, kind=None):
    for i in node.inputs:
        if i.name == name and (kind is None or i.type == kind):
            return i
    raise KeyError(name)


def _out(node, name, kind=None):
    for o in node.outputs:
        if o.name == name and (kind is None or o.type == kind):
            return o
    raise KeyError(name)


def set_ramp(ramp, stops):
    """Fill a ColorRamp with (position, hex) stops. Elements are created in order (assigning positions to
    existing elements re-sorts them mid-loop and can leave a stray default stop)."""
    els = ramp.color_ramp.elements
    while len(els) > 1:
        els.remove(els[-1])
    els[0].position = stops[0][0]
    els[0].color = rgba(stops[0][1])
    for pos, c in stops[1:]:
        e = els.new(pos)
        e.color = rgba(c)


def toon(color, shade=None, deep=None, hot=None, rim="#ffb347", rim_k=0.85, steps=None, night=False, name=None):
    """Banded toon material.  steps: optional explicit [(threshold, hex), ...] ramp on received light."""
    key = name or "toon_%s_%s_%s_%s_%s_%s" % (color, shade, deep, hot, rim, night)
    if key in _M:
        return _M[key]
    shade = shade or shade_of(color, night)
    deep = deep or hexmix(shade, "#0d0618", 0.55 if night else 0.25)
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    N, L = nt.nodes, nt.links
    out = N.new("ShaderNodeOutputMaterial")
    dif = N.new("ShaderNodeBsdfDiffuse")
    dif.inputs["Color"].default_value = (1, 1, 1, 1)
    s2r = N.new("ShaderNodeShaderToRGB")
    L.new(dif.outputs[0], s2r.inputs[0])
    bw = N.new("ShaderNodeRGBToBW")
    L.new(s2r.outputs["Color"], bw.inputs[0])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    st = steps or ([(0.0, deep), (0.012, shade), (0.09, color)] + ([(0.55, hot)] if hot else []))
    set_ramp(ramp, st)
    L.new(bw.outputs[0], ramp.inputs["Fac"])
    # lit mask for the rim (only lit surfaces get the rim)
    lit = N.new("ShaderNodeMath")
    lit.operation = "GREATER_THAN"
    lit.inputs[1].default_value = 0.09
    L.new(bw.outputs[0], lit.inputs[0])
    lw = N.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.42
    rr = N.new("ShaderNodeMath")
    rr.operation = "GREATER_THAN"
    rr.inputs[1].default_value = rim_k
    L.new(lw.outputs["Facing"], rr.inputs[0])
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(rr.outputs[0], mul.inputs[0])
    L.new(lit.outputs[0], mul.inputs[1])
    mix = N.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    L.new(mul.outputs[0], _inp(mix, "Factor", "VALUE"))
    L.new(ramp.outputs["Color"], _inp(mix, "A", "RGBA"))
    _inp(mix, "B", "RGBA").default_value = rgba(rim) if rim else (0, 0, 0, 1)
    if not rim:                      # no rim: threshold above 1 so the facing test never passes
        rr.inputs[1].default_value = 2.0
    em = N.new("ShaderNodeEmission")
    L.new(_out(mix, "Result", "RGBA"), em.inputs["Color"])
    L.new(em.outputs[0], out.inputs["Surface"])
    _M[key] = m
    return m


def no_shadow(ob):
    for attr in ("visible_shadow",):
        if hasattr(ob, attr):
            setattr(ob, attr, False)
    return ob


def glow(color, strength=1.0, name=None):
    """Pure emissive flat colour (flames, sparks, stars, eyes' catch-lights)."""
    key = name or "glow_%s_%.2f" % (color, strength)
    if key in _M:
        return _M[key]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = rgba(color)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    _M[key] = m
    return m


# ------------------------------------------------------------------ objects
COLL = None


def link(ob):
    (COLL or bpy.context.scene.collection).objects.link(ob)
    return ob


def mesh_obj(name, verts, faces, mat=None, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = link(bpy.data.objects.new(name, me))
    if mat:
        ob.data.materials.append(mat)
    return ob


def prim(kind, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), mat=None, name="p", seg=24, smooth=True, **kw):
    if kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=max(8, seg // 2), location=loc)
    elif kind == "ico":
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=kw.get("sub", 1), location=loc)
    elif kind == "cyl":
        bpy.ops.mesh.primitive_cylinder_add(vertices=seg, location=loc)
    elif kind == "cone":
        bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=kw.get("r1", 1), radius2=kw.get("r2", 0),
                                        depth=kw.get("depth", 2), location=loc)
    elif kind == "cube":
        bpy.ops.mesh.primitive_cube_add(location=loc)
    elif kind == "plane":
        bpy.ops.mesh.primitive_plane_add(location=loc)
    elif kind == "circle":
        bpy.ops.mesh.primitive_circle_add(vertices=seg, fill_type="NGON", location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = scale
    ob.rotation_euler = rot
    if mat:
        ob.data.materials.append(mat)
        if mat.name.startswith("glow_"):
            no_shadow(ob)
    if smooth and kind in ("sphere", "cyl", "cone"):
        bpy.ops.object.shade_smooth()
    if kw.get("bevel"):
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        md = ob.modifiers.new("bev", "BEVEL")
        md.width = kw["bevel"]
        md.segments = kw.get("bseg", 3)
    if COLL and ob.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(ob)
        COLL.objects.link(ob)
    return ob


def tube(name, pts, radius, mat, taper=None):
    """Rubber-hose limb: a bezier curve with a round bevel. pts in local space (3 points: root, bend, tip)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    ob = link(bpy.data.objects.new(name, cu))
    ob.data.materials.append(mat)
    return ob


def set_tube(ob, pts, frame=None):
    for bp, p in zip(ob.data.splines[0].bezier_points, pts):
        bp.co = p
        if frame is not None:
            bp.keyframe_insert("co", frame=frame)
            bp.keyframe_insert("handle_left", frame=frame)
            bp.keyframe_insert("handle_right", frame=frame)


def parent(child, par):
    child.parent = par
    return child


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0)):
    e = link(bpy.data.objects.new(name, None))
    e.location = loc
    e.rotation_euler = rot
    return e


def key_loc(ob, frame, loc):
    ob.location = loc
    ob.keyframe_insert("location", frame=frame)


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ characters
# reference character language: tube limbs, tapered body, sphere head, big hair mass, dot eyes, bar brows
STYLES = {
    "guide": dict(skin="#c98a5e", hair="#2b1d4f", top="#f0b43a", bottom="#1f5560", shoe="#3b2236", scarf="#d63c3c",
                  pack="#2e8a78", kind="guide", h=1.0),
    "woman": dict(skin="#d4573a", hair="#3b1f6e", top="#1f7a8c", bottom="#1f7a8c", shoe="#b24429", spots="#2b93a6",
                  belt="#f2c14e", kind="woman", h=0.95),
    "man": dict(skin="#c9643c", hair="#3b1f6e", top="#f0a83a", bottom="#b5772f", shoe="#a94d2c", spots="#f7c25a",
                belt="#f2c14e", kind="man", h=1.0),
}


class Char:
    """A posable character. Local frame: feet at origin, facing -Y (toward a camera placed at -Y)."""

    def __init__(self, name, style, loc=(0, 0, 0), face=0.0, night=False, rim="#ffb347", sit=False, **over):
        st = dict(STYLES[style])
        st.update(over)
        self.st, self.sit = st, sit
        T = lambda c: toon(c, night=night, rim=rim)      # noqa: E731
        self.root = empty(name, loc, (0, 0, math.radians(face)))
        k = st["h"]
        self.k = k
        hip = 0.85 * k
        body_z0 = 0.45 * k if st["kind"] == "woman" else 0.62 * k
        if sit:
            hip = 0.42 * k
            body_z0 = 0.4 * k
        # legs
        self.legs = []
        for s in (-1, 1):
            if sit:
                pts = [(s * 0.1 * k, 0, hip), (s * 0.28 * k, -0.34 * k, 0.3 * k), (-s * 0.06 * k, -0.46 * k, 0.1 * k)]
            else:
                pts = [(s * 0.1 * k, 0, hip), (s * 0.11 * k, 0, 0.45 * k), (s * 0.11 * k, 0.0, 0.07 * k)]
            col = st["bottom"] if st["kind"] == "guide" else st["skin"]
            lg = parent(tube(name + "_leg%d" % s, pts, 0.072 * k, T(col)), self.root)
            self.legs.append(lg)
            if not sit:
                parent(prim("sphere", (pts[2][0], -0.06 * k, 0.05 * k), (0.09 * k, 0.15 * k, 0.06 * k),
                            mat=T(st["shoe"]), name=name + "_shoe"), self.root)
        # body
        top_z = hip + 0.42 * k if not sit else hip + 0.62 * k
        if st["kind"] == "woman":
            body = prim("cone", (0, 0, (body_z0 + top_z) / 2), mat=T(st["top"]), name=name + "_body", r1=0.3 * k,
                        r2=0.17 * k, depth=top_z - body_z0)
        elif st["kind"] == "man":
            body = prim("cone", (0, 0, (body_z0 + top_z) / 2), mat=T(st["top"]), name=name + "_body", r1=0.27 * k,
                        r2=0.2 * k, depth=top_z - body_z0)
            parent(prim("cyl", (0, 0, body_z0 + 0.06 * k), (0.285 * k, 0.285 * k, 0.09 * k), mat=T(st["bottom"]),
                        name=name + "_wrap"), self.root)
        else:
            body = prim("cone", (0, 0, (hip - 0.05 * k + top_z) / 2), mat=T(st["top"]), name=name + "_body",
                        r1=0.21 * k, r2=0.24 * k, depth=top_z - hip + 0.05 * k)
            parent(prim("cyl", (0, 0, hip), (0.215 * k, 0.215 * k, 0.07 * k), mat=T(st["bottom"]),
                        name=name + "_belt"), self.root)
            parent(prim("cube", (0, 0.24 * k, top_z - 0.25 * k), (0.17 * k, 0.1 * k, 0.22 * k), mat=T(st["pack"]),
                        name=name + "_pack", bevel=0.04 * k), self.root)
            parent(prim("cyl", (0, 0, top_z + 0.01 * k), (0.2 * k, 0.2 * k, 0.04 * k), mat=T(st["scarf"]),
                        name=name + "_scarf"), self.root)
        parent(body, self.root)
        if st.get("belt") and st["kind"] != "guide":
            bz = body_z0 + (top_z - body_z0) * 0.45
            parent(prim("cyl", (0, 0, bz), (0.26 * k, 0.26 * k, 0.025 * k), mat=T(st["belt"]),
                        name=name + "_beltb"), self.root)
        if st.get("spots"):
            rnd = random.Random(len(name))
            for i in range(7):
                a = rnd.uniform(-2.4, 2.4) - math.pi / 2
                z = rnd.uniform(body_z0 + 0.1 * k, top_z - 0.1 * k)
                fr = (z - body_z0) / (top_z - body_z0)
                r = (0.3 if st["kind"] == "woman" else 0.27) * k * (1 - fr) + 0.18 * k * fr
                parent(prim("sphere", (math.cos(a) * r, math.sin(a) * r, z), (0.04 * k, 0.04 * k, 0.04 * k),
                            mat=T(st["spots"]), name=name + "_spot", seg=10), self.root)
        # arms (tubes) + hands
        self.sh = top_z - 0.06 * k
        self.arms, self.hands, self.grips = {}, {}, {}
        for s, side in ((-1, "l"), (1, "r")):
            pts = self.arm_pts(side, "down")
            self.arms[side] = parent(tube(name + "_arm" + side, pts, 0.058 * k, T(st["top"] if st["kind"] == "guide"
                                                                                   else st["skin"])), self.root)
            self.hands[side] = parent(prim("sphere", pts[2], (0.075 * k,) * 3, mat=T(st["skin"]),
                                           name=name + "_hand" + side, seg=12), self.root)
            self.grips[side] = parent(empty(name + "_grip" + side, pts[2]), self.root)   # unscaled: hold props here
        # head
        hz = top_z + 0.3 * k
        self.head = parent(empty(name + "_head", (0, 0, hz)), self.root)
        parent(prim("cyl", (0, 0, top_z + 0.08 * k), (0.06 * k, 0.06 * k, 0.1 * k), mat=T(st["skin"]),
                    name=name + "_neck"), self.root)
        H = lambda ob: parent(ob, self.head)  # noqa: E731
        H(prim("sphere", (0, 0, 0), (0.2 * k, 0.19 * k, 0.21 * k), mat=T(st["skin"]), name=name + "_face"))
        hair = T(st["hair"])
        H(prim("sphere", (0, 0.05 * k, 0.07 * k), (0.215 * k, 0.2 * k, 0.19 * k), mat=hair, name=name + "_hair"))
        if st["kind"] == "woman":
            H(prim("sphere", (0.06 * k, 0.14 * k, 0.2 * k), (0.13 * k,) * 3, mat=T("#55308f"), name=name + "_bun"))
            for s in (-1, 1):
                H(prim("sphere", (s * 0.2 * k, -0.02 * k, -0.04 * k), (0.025 * k,) * 3, mat=glow("#f2c14e", 1.0),
                       name=name + "_ear"))
        if st["kind"] == "man":
            H(prim("sphere", (0, -0.1 * k, -0.12 * k), (0.17 * k, 0.12 * k, 0.16 * k), mat=hair, name=name + "_beard"))
            H(prim("cyl", (0, 0, 0.09 * k), (0.205 * k, 0.205 * k, 0.025 * k), mat=T(st["belt"]),
                   name=name + "_band"))
        if st["kind"] == "guide":
            H(prim("sphere", (-0.03 * k, -0.1 * k, 0.14 * k), (0.16 * k, 0.12 * k, 0.07 * k), mat=hair,
                   name=name + "_fringe"))
        # face: dot eyes + bar brows (flat, unlit dark)
        ink = glow("#1c1230", 1.0)
        for s in (-1, 1):
            H(prim("sphere", (s * 0.075 * k, -0.18 * k, 0.0), (0.022 * k, 0.012 * k, 0.03 * k), mat=ink,
                   name=name + "_eye", seg=10))
            H(prim("cube", (s * 0.08 * k, -0.18 * k, 0.07 * k), (0.045 * k, 0.01 * k, 0.012 * k), mat=T(st["hair"]),
                   name=name + "_brow"))
        H(prim("sphere", (0, -0.19 * k, -0.09 * k), (0.035 * k, 0.012 * k, 0.016 * k), mat=glow("#9e2a2a", 1.0),
               name=name + "_mouth", seg=10))

    # arm targets in local space (elbow, hand) for named poses
    def arm_pts(self, side, pose):
        k, s = self.k, (-1 if side == "l" else 1)
        sh = (s * 0.21 * k, 0, self.sh)
        P = {
            "down": ((s * 0.27 * k, -0.02 * k, self.sh - 0.28 * k), (s * 0.26 * k, -0.04 * k, self.sh - 0.55 * k)),
            "up": ((s * 0.3 * k, -0.05 * k, self.sh + 0.25 * k), (s * 0.26 * k, -0.1 * k, self.sh + 0.55 * k)),
            "point": ((s * 0.36 * k, -0.2 * k, self.sh + 0.12 * k), (s * 0.48 * k, -0.42 * k, self.sh + 0.36 * k)),
            "forward": ((s * 0.26 * k, -0.25 * k, self.sh - 0.2 * k), (s * 0.14 * k, -0.48 * k, self.sh - 0.18 * k)),
            "lap": ((s * 0.3 * k, -0.18 * k, self.sh - 0.3 * k), (s * 0.08 * k, -0.36 * k, self.sh - 0.42 * k)),
            "head": ((s * 0.34 * k, -0.02 * k, self.sh + 0.2 * k), (s * 0.16 * k, -0.04 * k, self.sh + 0.5 * k)),
            "cheer": ((s * 0.38 * k, -0.06 * k, self.sh + 0.24 * k), (s * 0.42 * k, -0.1 * k, self.sh + 0.55 * k)),
        }
        e, h = P[pose]
        return [sh, e, h]

    def pose_arm(self, side, pose, frame=None):
        pts = self.arm_pts(side, pose)
        set_tube(self.arms[side], pts, frame)
        for hd in (self.hands[side], self.grips[side]):
            hd.location = pts[2]
            if frame is not None:
                hd.keyframe_insert("location", frame=frame)
        return pts[2]

    def world(self, local):
        return self.root.matrix_world @ Vector(local)
