"""Blender helpers: materials, shared meshes, objects and a per-frame animation store."""
import math

import bmesh
import bpy
import numpy as np
from mathutils import Vector

FPS = 24


# ------------------------------------------------------------------ colors
def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(h, a=1.0):
    h = h.lstrip("#")
    return tuple(srgb_to_lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (a,)


# --------------------------------------------------------------- materials
_mats = {}


def mat(color, rough=0.55, emit=0.0, sheen=0.0, metal=0.0, alpha=1.0, name=None,
        coat=0.0):
    key = name or f"{color}_{rough}_{emit}_{sheen}_{metal}_{alpha}_{coat}"
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgb(color)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if coat:
        b.inputs["Coat Weight"].default_value = coat
    if sheen:
        b.inputs["Sheen Weight"].default_value = sheen
    if emit:
        b.inputs["Emission Color"].default_value = rgb(color)
        b.inputs["Emission Strength"].default_value = emit
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = "BLENDED"
        except AttributeError:
            m.blend_method = "BLEND"
    _mats[key] = m
    return m


def flat(color, alpha=1.0, strength=1.0):
    """Unlit material (emission) used for HUD text and panels."""
    key = f"flat_{color}_{alpha}_{strength}"
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = rgb(color)
    em.inputs["Strength"].default_value = strength
    if alpha < 1:
        try:
            m.surface_render_method = "BLENDED"
        except AttributeError:
            m.blend_method = "BLEND"
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        mix.inputs[0].default_value = alpha
        nt.links.new(tr.outputs[0], mix.inputs[1])
        nt.links.new(em.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs[0])
    else:
        nt.links.new(em.outputs[0], out.inputs[0])
    _mats[key] = m
    return m


def noise_mat(c1, c2, scale=4.0, rough=0.8, name=None):
    key = name or f"noise_{c1}_{c2}_{scale}"
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = scale
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = rgb(c1)
    ramp.color_ramp.elements[1].color = rgb(c2)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[1].position = 0.65
    nt.links.new(tex.outputs["Fac"], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], b.inputs["Base Color"])
    _mats[key] = m
    return m


def checker_mat(c1, c2, scale=6.0):
    key = f"check_{c1}_{c2}_{scale}"
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.9
    b.inputs["Sheen Weight"].default_value = 0.5
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tex = nt.nodes.new("ShaderNodeTexChecker")
    tex.inputs["Scale"].default_value = scale
    tex.inputs["Color1"].default_value = rgb(c1)
    tex.inputs["Color2"].default_value = rgb(c2)
    nt.links.new(tc.outputs["UV"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    _mats[key] = m
    return m


# ------------------------------------------------------------ shared meshes
_meshes = {}


def _placeholder():
    return mat("#FF00FF", name="placeholder")


def _finish(bm, name, smooth=True):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(_placeholder())
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return me


def mesh_sphere(seg=32, rings=16):
    k = f"sphere{seg}"
    if k not in _meshes:
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
        _meshes[k] = _finish(bm, k)
    return _meshes[k]


def mesh_cyl(seg=24, r1=1.0, r2=1.0, smooth=True):
    """Cylinder/cone from z=0 to z=1 (radius r1 at bottom, r2 at top)."""
    k = f"cyl{seg}_{r1}_{r2}_{smooth}"
    if k not in _meshes:
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1,
                              radius2=r2, depth=1.0)
        bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, 0.5))
        me = _finish(bm, k, smooth)
        _meshes[k] = me
    return _meshes[k]


def mesh_box(bevel=0.2, seg=3):
    """Unit cube (-1..1) with rounded edges; bevel is a fraction of the size."""
    k = f"box{bevel}_{seg}"
    if k not in _meshes:
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=2.0)
        if bevel > 0:
            bmesh.ops.bevel(bm, geom=bm.verts[:] + bm.edges[:], offset=bevel,
                            segments=seg, affect="EDGES", profile=0.5)
        me = _finish(bm, k, smooth=bevel > 0)
        _meshes[k] = me
    return _meshes[k]


def mesh_torus(R=1.0, r=0.2, seg=32, ring=12, arc=2 * math.pi, start=0.0):
    k = f"torus{R}_{r}_{seg}_{arc:.3f}_{start:.3f}"
    if k not in _meshes:
        bm = bmesh.new()
        rows = []
        closed = abs(arc - 2 * math.pi) < 1e-6
        n = seg if closed else seg + 1
        for i in range(n):
            a = start + arc * i / seg
            c, s = math.cos(a), math.sin(a)
            row = []
            for j in range(ring):
                b = 2 * math.pi * j / ring
                rr = R + r * math.cos(b)
                # torus lies in the XZ plane (faces -Y), good for smiles
                row.append(bm.verts.new((rr * c, r * math.sin(b), rr * s)))
            rows.append(row)
        for i in range(n if closed else n - 1):
            a, b2 = rows[i], rows[(i + 1) % n]
            for j in range(ring):
                bm.faces.new((a[j], a[(j + 1) % ring], b2[(j + 1) % ring], b2[j]))
        if not closed:
            for row in (rows[0], rows[-1]):
                center = sum((v.co for v in row), Vector()) / ring
                cv = bm.verts.new(center)
                for j in range(ring):
                    try:
                        bm.faces.new((cv, row[(j + 1) % ring], row[j]))
                    except ValueError:
                        pass
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        _meshes[k] = _finish(bm, k)
    return _meshes[k]


def mesh_star(points=5, r1=1.0, r2=0.45, depth=0.3):
    k = f"star{points}_{r2}_{depth}"
    if k not in _meshes:
        bm = bmesh.new()
        front, back = [], []
        for i in range(points * 2):
            a = math.pi / 2 + math.pi * i / points
            r = r1 if i % 2 == 0 else r2
            front.append(bm.verts.new((r * math.cos(a), -depth / 2, r * math.sin(a))))
            back.append(bm.verts.new((r * math.cos(a), depth / 2, r * math.sin(a))))
        cf = bm.verts.new((0, -depth, 0))
        cb = bm.verts.new((0, depth, 0))
        n = len(front)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((cf, front[i], front[j]))
            bm.faces.new((cb, back[j], back[i]))
            bm.faces.new((front[j], front[i], back[i], back[j]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        _meshes[k] = _finish(bm, k, smooth=False)
    return _meshes[k]


def mesh_rrect(w, h, r, seg=8):
    """Flat rounded rectangle in the XY plane (for HUD panels)."""
    k = f"rrect{w:.3f}_{h:.3f}_{r:.3f}"
    if k not in _meshes:
        bm = bmesh.new()
        pts = []
        r = min(r, w / 2, h / 2)
        for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90),
                           (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
            for i in range(seg + 1):
                a = math.radians(a0 + 90 * i / seg)
                pts.append(bm.verts.new((cx + r * math.cos(a), cy + r * math.sin(a), 0)))
        bm.faces.new(pts)
        _meshes[k] = _finish(bm, k, smooth=False)
    return _meshes[k]


def mesh_prism():
    """Triangular prism (house roof): x in -1..1, base y -1..1 at z=0, ridge at z=1."""
    k = "prism"
    if k not in _meshes:
        bm = bmesh.new()
        v = [bm.verts.new(p) for p in [(-1, -1, 0), (-1, 1, 0), (-1, 0, 1),
                                       (1, -1, 0), (1, 1, 0), (1, 0, 1)]]
        bm.faces.new((v[0], v[2], v[1]))
        bm.faces.new((v[3], v[4], v[5]))
        bm.faces.new((v[0], v[3], v[5], v[2]))
        bm.faces.new((v[1], v[2], v[5], v[4]))
        bm.faces.new((v[0], v[1], v[4], v[3]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        _meshes[k] = _finish(bm, k, smooth=False)
    return _meshes[k]


# ----------------------------------------------------------------- objects
def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def obj(name, mesh, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), m=None,
        parent=None):
    ob = bpy.data.objects.new(name, mesh)
    link(ob)
    if m is not None:
        ob.material_slots[0].link = "OBJECT"
        ob.material_slots[0].material = m
    ob.parent = parent
    ob.location = loc
    ob.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3
    ob.rotation_euler = rot
    return ob


def sphere(name, loc, r, m, parent=None, rot=(0, 0, 0), seg=32):
    s = r if isinstance(r, (tuple, list)) else (r, r, r)
    return obj(name, mesh_sphere(seg, seg // 2), loc, s, rot, m, parent)


def cyl(name, loc, r, h, m, parent=None, rot=(0, 0, 0), r2=None, seg=24,
        smooth=True):
    rr = r if isinstance(r, (tuple, list)) else (r, r)
    me = mesh_cyl(seg, 1.0, 1.0 if r2 is None else r2, smooth)
    return obj(name, me, loc, (rr[0], rr[1], h), rot, m, parent)


def box(name, loc, size, m, parent=None, rot=(0, 0, 0), bevel=0.15):
    return obj(name, mesh_box(bevel), loc, tuple(s / 2 for s in size), rot, m, parent)


def empty(name, loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_size = 0.1
    link(ob)
    ob.parent = parent
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def text_obj(name, body, size, m, font, parent=None, loc=(0, 0, 0), align="CENTER",
             offset=0.0, extrude=0.0):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.font = font
    cu.size = size
    cu.align_x = align
    cu.align_y = "CENTER"
    cu.offset = offset
    cu.extrude = extrude
    cu.space_line = 0.95
    ob = bpy.data.objects.new(name, cu)
    link(ob)
    ob.parent = parent
    ob.location = loc
    ob.data.materials.append(m)
    return ob


# ---------------------------------------------------------------- easing
def clamp01(x):
    return np.clip(x, 0.0, 1.0)


def smooth(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def window(t, t0, t1, ramp=0.25):
    """1 inside [t0,t1] with smooth ramps, 0 outside."""
    if t1 - t0 < 2 * ramp:
        ramp = max((t1 - t0) / 2, 1e-3)
    return smooth((t - t0) / ramp) * smooth((t1 - t) / ramp)


def ease_out_back(x):
    x = clamp01(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def pop_curve(t, t0, t1, tin=0.35, tout=0.22):
    """Scale curve for pop-in / pop-out cards."""
    a = ease_out_back((t - t0) / tin)
    b = smooth((t1 - t) / tout)
    v = np.where(t < t0, 0.0, a) * np.where(t > t1, 0.0, b)
    return np.clip(v, 0, 2)


# ------------------------------------------------------------ anim store
class Anim:
    """Stores a value per frame for every animated channel, written at the end."""

    def __init__(self, nf):
        self.nf = nf
        self.t = np.arange(nf) / FPS
        self.ch = {}

    def get(self, ob, path, idx=0):
        k = (ob.name, path, idx)
        if k not in self.ch:
            base = getattr(ob, path)
            v = base[idx] if hasattr(base, "__len__") else base
            self.ch[k] = [ob, np.full(self.nf, float(v))]
        return self.ch[k][1]

    def set(self, ob, path, idx, values):
        self.get(ob, path, idx)[:] = values

    def write(self):
        count = 0
        for (name, path, idx), (ob, vals) in self.ch.items():
            vals = np.asarray(vals, dtype=np.float64)
            if np.allclose(vals, vals[0], atol=1e-5):
                v = getattr(ob, path)
                if hasattr(v, "__len__"):
                    v[idx] = vals[0]
                else:
                    setattr(ob, path, vals[0])
                continue
            # keep only frames where the value is not in the middle of a
            # straight (linear) run
            keep = np.ones(len(vals), bool)
            if len(vals) > 2:
                d = np.abs(vals[:-2] - 2 * vals[1:-1] + vals[2:])
                keep[1:-1] = d > 1e-5
            frames = np.nonzero(keep)[0]
            ad = ob.animation_data_create()
            if ad.action is None:
                act = bpy.data.actions.new(ob.name + "_act")
                ad.action = act
            ob.keyframe_insert(path, index=idx, frame=1)
            fc = find_fcurve(ob, path, idx)
            kp = fc.keyframe_points
            kp.clear()
            kp.add(len(frames))
            co = np.empty(len(frames) * 2)
            co[0::2] = frames + 1
            co[1::2] = vals[frames]
            kp.foreach_set("co", co)
            kp.foreach_set("interpolation", [1] * len(frames))  # LINEAR
            fc.update()
            count += len(frames)
        return count


def find_fcurve(ob, path, idx):
    ad = ob.animation_data
    act = ad.action
    # Blender 4.4+ layered actions
    try:
        from bpy_extras import anim_utils
        cb = anim_utils.action_get_channelbag_for_slot(act, ad.action_slot)
        fc = cb.fcurves.find(path, index=idx)
        if fc:
            return fc
    except Exception:
        pass
    for fc in getattr(act, "fcurves", []):
        if fc.data_path == path and fc.array_index == idx:
            return fc
    raise RuntimeError("fcurve not found %s %s %d" % (ob.name, path, idx))
