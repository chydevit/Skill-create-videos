"""Render a 3D flat-explainer shot with Blender.

  blender -b --factory-startup --python render3d.py -- --scene fire_night --dur 4.8 --out DIR
        [--fps 60] [--still 1.5 3.0 ...] [--preview] [--samples 16]

Scenes (built procedurally with toon3d): fire_night (Gobekli-style T-pillar circle at night, campfire ring of
villagers, the guide raising a torch; crane past the guide that orbits the fire) and village_day (round mud-brick
village at sunrise; turning orbit around the diorama).  Frames -> DIR/f_0001.png ...
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import toon3d as T  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(name, default=None, n=1, cast=str):
    if name not in argv:
        return default
    i = argv.index(name)
    if n == 1:
        return cast(argv[i + 1])
    out = []
    for v in argv[i + 1:]:
        if v.startswith("--"):
            break
        out.append(cast(v))
    return out


SCENE = arg("--scene", "fire_night")
DUR = arg("--dur", 4.8, cast=float)
FPS = arg("--fps", 60, cast=int)
OUT = arg("--out", "/tmp/r3d")
STILLS = arg("--still", None, n=0, cast=float)
PREVIEW = "--preview" in argv
SAMPLES = arg("--samples", 16, cast=int)
NF = int(round(DUR * FPS))
T.FPS = FPS


def F(t):
    return int(round(t * FPS)) + 1


# ------------------------------------------------------------------ scene setup
def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, NF
    sc.render.resolution_x, sc.render.resolution_y = (960, 540) if PREVIEW else (1920, 1080)
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.eevee.taa_render_samples = 4 if PREVIEW else SAMPLES
    try:
        sc.eevee.use_shadow_jitter_viewport = False
    except AttributeError:
        pass
    try:
        sc.eevee.use_shadows = True
        sc.eevee.shadow_ray_count = 1
        sc.eevee.shadow_step_count = 4
    except AttributeError:
        pass
    sc.render.image_settings.file_format = "PNG"
    sc.render.film_transparent = False
    return sc


def world_gradient(stops, light_col="#000000", light_k=0.0):
    """Screen-space vertical sky gradient for camera rays; near-black ambient for lighting (toon bands)."""
    w = bpy.data.worlds.new("W")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    N, L = nt.nodes, nt.links
    out = N.new("ShaderNodeOutputWorld")
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Generated"], sep.inputs[0])      # world: view direction -> Z = elevation
    mr = N.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -0.02
    mr.inputs["From Max"].default_value = 0.6
    L.new(sep.outputs["Z"], mr.inputs["Value"])
    ramp = N.new("ShaderNodeValToRGB")
    T.set_ramp(ramp, stops)
    L.new(mr.outputs["Result"], ramp.inputs["Fac"])
    bg_cam = N.new("ShaderNodeBackground")
    L.new(ramp.outputs["Color"], bg_cam.inputs["Color"])
    bg_l = N.new("ShaderNodeBackground")
    bg_l.inputs["Color"].default_value = T.rgba(light_col)
    bg_l.inputs["Strength"].default_value = light_k
    lp = N.new("ShaderNodeLightPath")
    mix = N.new("ShaderNodeMixShader")
    L.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
    L.new(bg_l.outputs[0], mix.inputs[1])
    L.new(bg_cam.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs["Surface"])


def point_light(loc, color, power, radius=0.15, name="L"):
    ld = bpy.data.lights.new(name, "POINT")
    ld.color = T.rgba(color)[:3]
    ld.energy = power
    ld.shadow_soft_size = radius
    ob = T.link(bpy.data.objects.new(name, ld))
    ob.location = loc
    return ob


def sun_light(rot, color, strength, name="Sun"):
    ld = bpy.data.lights.new(name, "SUN")
    ld.color = T.rgba(color)[:3]
    ld.energy = strength
    ld.angle = math.radians(0.3)
    ob = T.link(bpy.data.objects.new(name, ld))
    ob.rotation_euler = [math.radians(a) for a in rot]
    return ob


def camera(path, look, lens=35, dof=None):
    """path: [(t, (x,y,z))...] keyframed (smooth); look: [(t, (x,y,z))...] target empty; dof: [(t, dist)] or None."""
    cd = bpy.data.cameras.new("Cam")
    cd.lens = lens
    cd.clip_start, cd.clip_end = 0.05, 3000
    cam = T.link(bpy.data.objects.new("Cam", cd))
    bpy.context.scene.camera = cam
    tgt = T.empty("CamTarget")
    for t, p in path:
        T.key_loc(cam, F(t), p)
    for t, p in look:
        T.key_loc(tgt, F(t), p)
    con = cam.constraints.new("TRACK_TO")
    con.target = tgt
    con.track_axis, con.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
    if dof:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = dof[0]
        for t, dist in dof[1]:
            cd.dof.focus_distance = dist
            cd.dof.keyframe_insert("focus_distance", frame=F(t))
    for ob in (cam, tgt):
        if ob.animation_data and ob.animation_data.action:
            for fc in _fcurves(ob.animation_data.action):
                for kp in fc.keyframe_points:
                    kp.interpolation = "BEZIER"
                    kp.easing = "EASE_IN_OUT"
    return cam


def _fcurves(action):
    """fcurves of an action (Blender 4.4+ layered actions or legacy)."""
    try:
        return list(action.fcurves)
    except AttributeError:
        out = []
        for layer in action.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    out.extend(cb.fcurves)
        return out


def flicker(seed, t, k=1.0):
    return k * (math.sin(t * 13.1 + seed) * 0.5 + math.sin(t * 7.3 + 2 * seed) * 0.3 + math.sin(t * 23.7) * 0.2)


# ------------------------------------------------------------------ props
def t_pillar(loc, face, h=3.2, col="#7a3a48", rim="#ff9a4a", night=True, relief=True):
    m = T.toon(col, night=night, rim=rim)
    root = T.empty("pillar", loc, (0, 0, math.radians(face)))
    T.parent(T.prim("cube", (0, 0, h / 2), (0.22, 0.45, h / 2), mat=m, name="shaft", bevel=0.05), root)
    T.parent(T.prim("cube", (0, 0.15, h + 0.25), (0.26, 0.9, 0.28), mat=m, name="head", bevel=0.06), root)
    if relief:   # a carved fox: raised plates on the shaft's front face
        rm = T.toon(T.hexmix(col, "#ffffff", 0.12), night=night, rim=rim)
        T.parent(T.prim("sphere", (-0.23, 0, h * 0.62), (0.03, 0.26, 0.09), mat=rm, name="fox_b"), root)
        T.parent(T.prim("sphere", (-0.23, -0.26, h * 0.66), (0.03, 0.08, 0.07), mat=rm, name="fox_h"), root)
        T.parent(T.prim("sphere", (-0.23, 0.3, h * 0.7), (0.03, 0.16, 0.05), mat=rm, name="fox_t",
                        rot=(math.radians(-30), 0, 0)), root)
        for z in (0.3, 0.42):
            T.parent(T.prim("cube", (-0.23, 0, h * z), (0.02, 0.3, 0.025), mat=rm, name="band"), root)
    return root


def teardrop(loc, r, h, mat):
    """Flat-cartoon flame: a sphere bottom with a cone tip, pivot at the base."""
    piv = T.empty("flame", loc)
    T.parent(T.prim("sphere", (0, 0, r), (r, r, r), mat=mat, name="fl_b", seg=16), piv)
    T.parent(T.prim("cone", (0, 0, r + h * 0.5), mat=mat, name="fl_t", r1=r * 0.98, r2=0, depth=h, seg=16), piv)
    return piv


def fire(loc, t_on=0.3):
    sc = bpy.context.scene
    root = T.empty("fire", loc)
    logs = T.toon("#5a2c1e", night=True)
    for a in (25, -25):
        T.parent(T.prim("cyl", (0, 0, 0.08), (0.07, 0.07, 0.55), rot=(math.radians(90), 0, math.radians(a)),
                        mat=logs, name="log"), root)
    flames = []
    for (r, h, col, z, y) in ((0.34, 1.0, "#ff5a2e", 0.0, 0.0), (0.24, 0.72, "#ffb02e", 0.0, -0.06),
                              (0.13, 0.42, "#fff1b0", 0.0, -0.12)):
        fl = T.parent(teardrop((0, y, z), r, h, T.glow(col, 1.0)), root)
        flames.append(fl)
    lamp = point_light((loc[0], loc[1], loc[2] + 0.7), "#ff8a3a", 0, 0.03, "FireLight")
    for f in range(1, NF + 1, 2):
        t = (f - 1) / FPS
        on = T.ease((t - t_on) / 1.3)
        for i, fl in enumerate(flames):
            s = (0.25 + 0.75 * on) * (1 + flicker(i * 1.7, t, 0.12))
            fl.scale = (s, s, s * (1 + flicker(i * 3.1, t, 0.1)))
            fl.rotation_euler = (0, 0, t * (0.8 + i))
            fl.keyframe_insert("scale", frame=f)
            fl.keyframe_insert("rotation_euler", frame=f)
        lamp.data.energy = 950 * on * (1 + flicker(0.5, t, 0.08))
        lamp.data.keyframe_insert("energy", frame=f)
    return root, lamp


def sparks(origin, n=14, life=1.5, rise=2.2, spread=0.5, t0=0.0, col="#ffc84a", size=0.035, seed=1):
    rnd = random.Random(seed)
    mat = T.glow(col, 2.0)
    for i in range(n):
        sp = T.prim("ico", origin, (size,) * 3, mat=mat, name="spark", sub=1, smooth=False)
        ph = rnd.random()
        hx, hy = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
        for f in range(1, NF + 1, 2):
            t = (f - 1) / FPS
            if t < t0:
                sp.scale = (0, 0, 0)
            else:
                age = ((t - t0) / life + ph) % 1.0
                sp.location = (origin[0] + hx * spread * age + 0.05 * math.sin(t * 4 + i),
                               origin[1] + hy * spread * age, origin[2] + rise * age)
                k = size * (1 - 0.6 * age) * min(1.0, age * 6)
                sp.scale = (k, k, k)
                sp.keyframe_insert("location", frame=f)
            sp.keyframe_insert("scale", frame=f)


def stars(n=260, r=120, seed=4):
    rnd = random.Random(seed)
    me = T.prim("ico", (0, 0, -50), (1, 1, 1), mat=T.glow("#cbb8ff", 1.0), name="star_src", sub=1, smooth=False).data
    for i in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        el = rnd.uniform(math.radians(8), math.radians(70))
        ob = T.link(bpy.data.objects.new("star", me))
        ob.location = (r * math.cos(a) * math.cos(el), r * math.sin(a) * math.cos(el), r * math.sin(el))
        s = rnd.uniform(0.12, 0.3)
        ob.scale = (s, s, s)


def mesa_ring(r0, r1, col, top, n=16, seed=2, night=True):
    rnd = random.Random(seed)
    for i in range(n):
        a = i / n * 2 * math.pi + rnd.uniform(-0.1, 0.1)
        r = rnd.uniform(r0, r1)
        w, d, h = rnd.uniform(6, 12), rnd.uniform(4, 8), rnd.uniform(3, 9)
        T.prim("cube", (r * math.cos(a), r * math.sin(a), h / 2), (w / 2, d / 2, h / 2), rot=(0, 0, a + 1.57),
               mat=T.toon(col, steps=[(0, col), (0.02, top)], rim=None), name="mesa", bevel=0.35, bseg=1)


def bush(loc, s, c1="#0f6b4a", c2="#167a44", berries=True, seed=0):
    rnd = random.Random(seed)
    root = T.empty("bush", loc)
    for i in range(5):
        T.parent(T.prim("ico", (rnd.uniform(-.5, .5) * s, rnd.uniform(-.4, .4) * s, rnd.uniform(.3, .8) * s),
                        (s * rnd.uniform(.4, .6),) * 3, mat=T.toon(c1 if i % 2 else c2, rim="#ffd27a"),
                        name="leafball", sub=1, smooth=False), root)
    if berries:
        for i in range(4):
            T.parent(T.prim("sphere", (rnd.uniform(-.5, .5) * s, -0.55 * s, rnd.uniform(.4, .9) * s),
                            (0.07 * s,) * 3, mat=T.glow("#f2b53d"), name="berry", seg=8), root)
    return root


# ------------------------------------------------------------------ shots
def fire_night():
    world_gradient([(0.0, "#7a1f44"), (0.35, "#3a1446"), (1.0, "#160b2c")], "#2a1850", 0.02)
    T.prim("circle", (0, 0, 0), (400, 400, 1), mat=T.toon("#a8342f", steps=[
        (0, "#2a0e24"), (0.004, "#4a1430"), (0.02, "#6a1e3a"), (0.06, "#b8393a"), (0.16, "#e8642c"),
        (0.4, "#ffa23a")], rim=None, name="ground"), name="ground", seg=64)
    rnd = random.Random(5)
    for i in range(60):   # pebbles
        a, r = rnd.uniform(0, 6.28), rnd.uniform(2, 14)
        T.prim("sphere", (r * math.cos(a), r * math.sin(a), 0.0), (rnd.uniform(.1, .25), rnd.uniform(.05, .1), .03),
               mat=T.toon("#7a2a44", night=True, rim=None), name="pebble", seg=8)
    stars()
    mesa_ring(40, 70, "#2a1c4f", "#3b2a66", seed=3)
    mesa_ring(26, 34, "#341d52", "#4a2a68", n=12, seed=9)
    # Gobekli-style enclosure: a ring of T-pillars around the gathering
    for i in range(9):
        a = i / 9 * 2 * math.pi + 0.2
        if -2.4 < math.atan2(math.sin(a), math.cos(a)) < -0.6:     # camera corridor
            continue
        t_pillar((7.2 * math.cos(a), 7.2 * math.sin(a), 0), math.degrees(a) + 180, h=rnd.uniform(2.6, 3.4))
    fire((0, 0, 0))
    sparks((0, 0, 1.0), n=16, life=1.6, rise=2.6, t0=0.8, seed=3)
    # villagers around the fire, facing it
    ring = [("woman", {}), ("man", {}), ("woman", dict(top="#c8326f", spots="#e0558a")),
            ("man", dict(top="#2e8a78", spots="#3fae96")), ("woman", dict(top="#e2682a", spots="#f08a4a")),
            ("man", {}), ("woman", dict(top="#5b3fa0", spots="#7a5fc0"))]
    for i, (st, ov) in enumerate(ring):
        a = i / len(ring) * 2 * math.pi + 0.45
        r = 2.4
        c = T.Char("v%d" % i, st, (r * math.cos(a), r * math.sin(a), 0), math.degrees(a) - 90, night=True, sit=True,
                   **ov)
        for s in ("l", "r"):
            c.pose_arm(s, "lap")
        # gentle sway
        for f in range(1, NF + 1, 6):
            t = (f - 1) / FPS
            c.head.rotation_euler = (0, math.sin(t * 1.3 + i) * 0.06, math.sin(t * 0.9 + i) * 0.08)
            c.head.keyframe_insert("rotation_euler", frame=f)
    cheer = T.Char("cheer", "man", (1.0, -1.6, 0), 200, night=True)
    for f, pose in ((1, "down"), (F(1.2), "down"), (F(1.5), "cheer"), (F(2.6), "cheer"), (F(2.9), "head")):
        for s in ("l", "r"):
            cheer.pose_arm(s, pose, f)
    # the guide (Dara): back to camera, turns and raises a torch
    g = T.Char("dara", "guide", (-1.9, -5.6, 0), 161, night=True)   # back to the camera, facing the fire
    g.pose_arm("l", "down", 1)
    g.pose_arm("r", "down", 1)
    g.pose_arm("r", "down", F(1.2))
    hand = g.pose_arm("r", "up", F(1.7))
    g.head.rotation_euler = (0, 0, math.radians(-35))
    g.head.keyframe_insert("rotation_euler", frame=1)
    g.head.rotation_euler = (math.radians(-12), 0, math.radians(8))
    g.head.keyframe_insert("rotation_euler", frame=F(1.6))
    bpy.context.view_layer.update()
    # torch follows the hand
    torch = T.parent(T.prim("cyl", (0, 0, 0.28), (0.025, 0.025, 0.3), mat=T.toon("#3b2a5a", night=True), name="torch"),
                     g.grips["r"])
    tfl = T.parent(teardrop((0, 0, 0.56), 0.07, 0.18, T.glow("#ffb02e")), g.grips["r"])
    T.parent(teardrop((0, -0.01, 0.0), 0.04, 0.1, T.glow("#fff1b0")), tfl)
    tl = point_light((0, 0, 0), "#ff9a3a", 0, 0.02, "TorchLight")
    tl.parent = g.grips["r"]
    tl.location = (0, 0, 0.75)
    for f in range(1, NF + 1, 2):
        t = (f - 1) / FPS
        on = T.ease((t - 1.45) / 0.35)
        tfl.scale = (on * (1 + flicker(2, t, .2)),) * 2 + (on * (1 + flicker(5, t, .25)),)
        tfl.keyframe_insert("scale", frame=f)
        tl.data.energy = 70 * on * (1 + flicker(9, t, .1))
        tl.data.keyframe_insert("energy", frame=f)
    sun_light((60, 0, 200), "#5a4aa0", 0.25, "Moon")
    # camera: low behind Dara, crane up and past her, orbiting to frame the circle (true 3D move)
    camera([(0, (-3.3, -8.6, 1.5)), (DUR * 0.55, (-1.0, -8.2, 2.3)), (DUR, (2.4, -7.0, 3.1))],
           [(0, (-1.2, -3.0, 1.7)), (DUR, (0.3, 0, 0.9))], lens=32,
           dof=(2.0, [(0, 3.2), (1.8, 3.3), (DUR, 7.3)]))


def village_day():
    world_gradient([(0.0, "#f59a3a"), (0.18, "#d9707a"), (0.45, "#7d8aa0"), (1.0, "#4a8ea6")], "#7d8aa0", 0.02)
    T.prim("circle", (0, 0, 0), (400, 400, 1), mat=T.toon("#d2561e", steps=[(0, "#8a2a1a"), (0.01, "#b4401c"),
                                                                       (0.05, "#d2561e"), (0.25, "#ec6f1e")],
                                                    rim=None, name="ground_d"), name="ground", seg=64)
    rnd = random.Random(8)
    for i in range(90):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(1, 18)
        T.prim("sphere", (r * math.cos(a), r * math.sin(a), 0.0), (rnd.uniform(.15, .35), rnd.uniform(.06, .12), .03),
               mat=T.toon("#a8381a", rim=None), name="pebble", seg=8)
    # rolling purple hills: buried spheres, two rings (near low, far big) - reads like the reference's layered hills
    for ring, (r0, r1, smin, smax, col) in enumerate(((24, 32, 5, 8, "#4a4f94"), (55, 75, 14, 22, "#3c3f80"))):
        for i in range(12):
            a = i / 12 * 2 * math.pi + rnd.uniform(-.2, .2)
            r = rnd.uniform(r0, r1)
            sz = rnd.uniform(smin, smax)
            T.prim("sphere", (r * math.cos(a), r * math.sin(a), -sz * 0.55), (sz * 1.3, sz, sz),
                   rot=(0, 0, a), mat=T.toon(col, rim="#ffd27a" if ring == 0 else None), name="hill", seg=32)
            if ring == 0 and i % 2 == 0:   # teal ledge band on near hills
                T.prim("sphere", (r * math.cos(a), r * math.sin(a), -sz * 0.55 + 0.06), (sz * 1.31, sz * 1.01, sz * 0.62),
                       rot=(0, 0, a), mat=T.toon("#3aa08a", rim=None), name="ledge", seg=32)
    # round mud-brick houses
    houses = [(-3.2, 1.5, 1.4), (0.6, 3.2, 1.1), (3.4, 0.6, 1.5), (-0.6, -0.4, 1.0), (-4.6, -2.6, 0.9),
              (4.6, 4.4, 1.2)]
    for (x, y, s) in houses:
        h = 1.3 * s
        T.prim("cyl", (x, y, h / 2), (1.5 * s, 1.5 * s, h / 2), mat=T.toon("#e8925a", rim="#ffe0a0"), name="house",
               seg=32, bevel=0.06)
        T.prim("cyl", (x, y, h + 0.04), (1.5 * s, 1.5 * s, 0.05), mat=T.toon("#f5b37a", rim=None), name="roof",
               seg=32)
        a = math.atan2(-y - 6, -x)
        T.prim("cube", (x + math.cos(a) * 1.5 * s, y + math.sin(a) * 1.5 * s, 0.45 * s), (0.08, 0.32 * s, 0.45 * s),
               rot=(0, 0, a), mat=T.glow("#5a1e2a"), name="door")
    T.prim("cube", (3.4 + 1.7, 0.6, 1.4), (0.05, 0.25, 1.4), rot=(0, math.radians(-14), 0), mat=T.toon("#7a4a2a"),
           name="ladder")
    for i, (x, y, s) in enumerate([(-6, 3, .8), (2, -3.5, .6), (6.5, -1.5, .9), (-2, 5.5, 1.0), (-7, -5, .7),
                                   (8, 3, .8)]):
        bush((x, y, 0), s, seed=i, berries=i % 2 == 0)
    sun = sun_light((62, 0, 125), "#fff0c8", 4.0)
    T.prim("sphere", (-60, -95, 26), (7, 7, 7), mat=T.glow("#fff4d6", 1.0), name="sundisc")
    # villagers doing things
    w = T.Char("carrier", "woman", (-2.6, -2.6, 0), -20)
    w.pose_arm("l", "head")
    w.pose_arm("r", "head")
    T.parent(T.prim("cyl", (0, 0, w.sh + 0.62), (0.32, 0.32, 0.12), mat=T.toon("#c07a2e", rim="#ffe0a0"),
                    name="basket"), w.root)
    T.parent(T.prim("sphere", (0, 0, w.sh + 0.72), (0.3, 0.3, 0.12), mat=T.toon("#f2c14e"), name="grain"), w.root)
    for f in range(1, NF + 1, 3):
        t = (f - 1) / FPS
        w.root.location = (-2.6 + 1.6 * t / DUR, -2.6 - 0.4 * t / DUR, abs(math.sin(t * 6)) * 0.05)
        w.root.keyframe_insert("location", frame=f)
    m = T.Char("worker", "man", (1.6, -1.8, 0), 30)
    for f in range(1, NF + 1, 12):
        t = (f - 1) / FPS
        p = "forward" if int(t * 2.5) % 2 else "down"
        m.pose_arm("l", p, f)
        m.pose_arm("r", p, f)
    w2 = T.Char("offer", "woman", (-0.4, -2.9, 0), -10, top="#c8326f", spots="#e0558a")
    w2.pose_arm("l", "forward")
    w2.pose_arm("r", "forward")
    T.parent(T.prim("cyl", (0, -0.5, w2.sh - 0.2), (0.16, 0.16, 0.07), mat=T.toon("#2e8a78"), name="bowl"), w2.root)
    m2 = T.Char("m2", "man", (-1.4, -3.4, 0), 160, top="#2e8a78", spots="#3fae96")
    g = T.Char("dara", "guide", (3.2, -4.6, 0), 34)
    g.pose_arm("l", "down")
    g.pose_arm("r", "point")
    # camera: turning orbit around the village diorama (the move 2D cannot do)
    pts = []
    for k in range(5):
        u = k / 4
        a = math.radians(-118 + 46 * u)
        pts.append((DUR * u, (12.5 * math.cos(a), 12.5 * math.sin(a), 4.6 - 0.8 * u)))
    camera(pts, [(0, (0, 0, 0.9)), (DUR, (0.3, 0.2, 1.1))], lens=34, dof=(5.6, [(0, 11.5), (DUR, 11.0)]))




# ------------------------------------------------------------------ dioramas (reference isometric shots)
def ortho_camera(center, yaw_from, yaw_to, scale_from, scale_to, elev=35, dist=60):
    """Isometric-style orthographic camera turning slowly around `center` (the reference's diorama shots)."""
    cd = bpy.data.cameras.new("Cam")
    cd.type = "ORTHO"
    cd.clip_start, cd.clip_end = 0.1, 3000
    cam = T.link(bpy.data.objects.new("Cam", cd))
    bpy.context.scene.camera = cam
    tgt = T.empty("CamTarget", center)
    con = cam.constraints.new("TRACK_TO")
    con.target = tgt
    con.track_axis, con.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
    for f in range(1, NF + 1, 3):
        u = T.ease((f - 1) / max(1, NF - 1))
        yaw = math.radians(yaw_from + (yaw_to - yaw_from) * u)
        el = math.radians(elev)
        cam.location = (center[0] + dist * math.cos(yaw) * math.cos(el), center[1] + dist * math.sin(yaw) * math.cos(el),
                        center[2] + dist * math.sin(el))
        cam.keyframe_insert("location", frame=f)
        cd.ortho_scale = scale_from + (scale_to - scale_from) * u
        cd.keyframe_insert("ortho_scale", frame=f)
    return cam


def tile_ground(size, col, steps=None, seed=1, grid=None):
    T.prim("plane", (0, 0, 0), (size, size, 1), mat=T.toon(col, steps=steps, rim=None), name="ground")
    if grid:
        gm = T.toon(grid, rim=None)
        for k in range(-int(size), int(size) + 1, 4):
            T.prim("cube", (k, 0, 0.01), (0.04, size, 0.01), mat=gm, name="gl")
            T.prim("cube", (0, k, 0.01), (size, 0.04, 0.01), mat=gm, name="gl")


def field(x, y, w, d, col="#b8862e", row="#7a9a2a", rot=0):
    root = T.empty("field", (x, y, 0), (0, 0, math.radians(rot)))
    T.parent(T.prim("cube", (0, 0, 0.05), (w / 2, d / 2, 0.05), mat=T.toon(col, rim=None), name="soil"), root)
    for k in range(int(d / 0.6)):
        T.parent(T.prim("cube", (0, -d / 2 + 0.3 + k * 0.6, 0.18), (w / 2 - 0.15, 0.12, 0.12),
                        mat=T.toon(row, rim="#ffe08a"), name="crop", bevel=0.05), root)
    return root


def goat(x, y, rot=0, col="#f3ecdf"):
    root = T.empty("goat", (x, y, 0), (0, 0, math.radians(rot)))
    m = T.toon(col, rim="#ffe0a0")
    T.parent(T.prim("sphere", (0, 0, 0.38), (0.3, 0.16, 0.16), mat=m, name="gb"), root)
    T.parent(T.prim("sphere", (0.32, 0, 0.52), (0.1, 0.08, 0.09), mat=m, name="gh"), root)
    for dx in (-0.18, 0.18):
        for dy in (-0.08, 0.08):
            T.parent(T.prim("cyl", (dx, dy, 0.14), (0.03, 0.03, 0.14), mat=T.toon("#5a3a2a", rim=None), name="gl"),
                     root)
    return root


def enclosure(cx, cy, r, n_pillars, depth=1.2, wall="#c98a5a", pillar="#d9a46a", seed=0):
    """Sunken round enclosure ringed by T-pillars facing inward + two big central pillars."""
    rnd = random.Random(seed)
    rim_m = T.toon(wall, rim="#ffe0a0")
    T.prim("cyl", (cx, cy, -depth / 2 + 0.02), (r + 0.6, r + 0.6, depth / 2), mat=T.toon("#8a4a2a", rim=None),
           name="pit", seg=48)
    T.prim("cyl", (cx, cy, 0.25), (r + 0.9, r + 0.9, 0.25), mat=rim_m, name="wallring", seg=48)
    T.prim("cyl", (cx, cy, 0.27), (r + 0.35, r + 0.35, 0.27), mat=T.toon("#8a4a2a", rim=None), name="hole", seg=48)
    for i in range(n_pillars):
        a = i / n_pillars * 2 * math.pi
        t_pillar((cx + r * math.cos(a), cy + r * math.sin(a), -0.2), math.degrees(a) + 90, h=rnd.uniform(1.6, 2.2),
                 col=pillar, rim="#ffe0a0", night=False, relief=i % 2 == 0)
    for dx in (-0.6, 0.6):
        t_pillar((cx + dx, cy, -0.2), 90, h=3.0, col=pillar, rim="#ffe0a0", night=False, relief=True)


def enclosure_day():
    """Göbekli Tepe / Taş Tepeler hilltop at golden hour: sunken enclosures, gatherers, carvers, fields of wild grain."""
    world_gradient([(0.0, "#f6c46a"), (0.3, "#f3a35a"), (0.7, "#7fb3b0"), (1.0, "#4a8ea6")], "#f3c48a", 0.02)
    tile_ground(120, "#e8b24a", steps=[(0, "#9a5a2a"), (0.01, "#c98a3a"), (0.05, "#e8b24a"), (0.3, "#f6cf6a")],
                grid=None)
    rnd = random.Random(2)
    enclosure(0, 0, 4.2, 12, seed=1)
    enclosure(-9, 6, 3.2, 10, seed=2)
    enclosure(8, 7, 2.8, 9, seed=3)
    for i in range(18):   # round huts around the site
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(11, 22)
        x, y = r * math.cos(a), r * math.sin(a)
        s = rnd.uniform(0.8, 1.3)
        T.prim("cyl", (x, y, 0.4 * s), (1.0 * s, 1.0 * s, 0.4 * s), mat=T.toon("#e0a868", rim="#ffe0a0"),
               name="hut", seg=24)
        T.prim("cyl", (x, y, 0.82 * s), (1.0 * s, 1.0 * s, 0.03), mat=T.toon("#f2c48a", rim=None), name="hutroof",
               seg=24)
    for i in range(8):
        a = rnd.uniform(0, 6.28)
        field(16 * math.cos(a) + rnd.uniform(-3, 3), 16 * math.sin(a), rnd.uniform(3, 5), rnd.uniform(2, 3.5),
              rot=rnd.uniform(0, 90))
    for i in range(10):
        bush((rnd.uniform(-30, 30), rnd.uniform(-30, 30), 0), rnd.uniform(0.8, 1.4), seed=i, berries=False)
    styles = ["man", "woman", "man", "woman", "man"]
    for i in range(26):   # gatherers converging on the site
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(5.5, 14)
        c = T.Char("p%d" % i, styles[i % 5], (r * math.cos(a), r * math.sin(a), 0),
                   math.degrees(math.atan2(-math.sin(a), -math.cos(a))) + 90,
                   top=rnd.choice(["#1f7a8c", "#c8326f", "#2e8a78", "#e2682a", "#f0a83a", "#5b3fa0"]))
        if i % 4 == 0:
            for f in range(1, NF + 1, 15):
                p = "forward" if (f // 15) % 2 else "down"
                c.pose_arm("l", p, f)
                c.pose_arm("r", p, f)
    sun_light((48, 0, 230), "#fff0c8", 4.0)
    ortho_camera((0, 1, 0), -100, -70, 34, 28, elev=38)


def catal_town():
    """Çatalhöyük: houses packed wall to wall, entered by roof hatches and ladders; goats and fields around."""
    world_gradient([(0.0, "#f2d39a"), (1.0, "#9ad0c8")], "#f2d39a", 0.02)
    tile_ground(120, "#c9b04a", steps=[(0, "#7a6a2a"), (0.01, "#a39a3a"), (0.05, "#c9b04a"), (0.3, "#e0c860")])
    rnd = random.Random(4)
    occupied = {}
    wall = T.toon("#f0c9b8", rim="#fff0d8")
    roof = T.toon("#fbe3d6", rim=None)
    hatch = T.glow("#4a2030")
    lad = T.toon("#7a4a2a", rim=None)
    for gx in range(-9, 10):
        for gy in range(-7, 8):
            if gx * gx / 90 + gy * gy / 55 > 1 or rnd.random() < 0.06:
                continue
            h = rnd.choice([1.6, 1.9, 2.2, 2.5])
            x, y = gx * 2.05, gy * 2.05
            T.prim("cube", (x, y, h / 2), (1.0, 1.0, h / 2), mat=wall, name="house", bevel=0.06)
            T.prim("cube", (x, y, h + 0.03), (0.96, 0.96, 0.03), mat=roof, name="roof")
            if rnd.random() < 0.6:
                T.prim("cube", (x + 0.3, y - 0.2, h + 0.06), (0.22, 0.3, 0.02), mat=hatch, name="hatch")
                T.prim("cube", (x + 0.3, y - 0.2, h + 0.5), (0.03, 0.22, 0.6), rot=(math.radians(15), 0, 0), mat=lad,
                       name="ladder")
            occupied[(gx, gy)] = h
    for i in range(30):   # people on roofs
        gx, gy = rnd.choice(sorted(occupied))
        c = T.Char("r%d" % i, rnd.choice(["man", "woman"]), (gx * 2.05 + rnd.uniform(-.5, .5),
                                                           gy * 2.05 + rnd.uniform(-.5, .5), 2.5),
                   rnd.uniform(0, 360), top=rnd.choice(["#1f7a8c", "#c8326f", "#2e8a78", "#e2682a", "#f0a83a"]))
        c.root.scale = (0.8, 0.8, 0.8)
        # stand on the roof of that house: drop to its height (approx 1.6-2.5)
        c.root.location.z = occupied[(gx, gy)] + 0.06
    for i in range(16):
        a = rnd.uniform(0, 6.28)
        goat(26 * math.cos(a) + rnd.uniform(-2, 2), 18 * math.sin(a), rnd.uniform(0, 360))
    for i in range(10):
        a = rnd.uniform(0, 6.28)
        field(30 * math.cos(a), 24 * math.sin(a), rnd.uniform(5, 8), rnd.uniform(3, 5), rot=rnd.uniform(0, 90))
    for i in range(12):
        bush((rnd.uniform(-40, 40), rnd.uniform(-35, 35), 0), rnd.uniform(1, 1.8), seed=i + 30, berries=False)
    sun_light((50, 0, 210), "#fff4dc", 4.0)
    ortho_camera((0, 0, 1), -125, -95, 46, 36, elev=36, dist=90)


def megasite():
    """Trypillia megasite (Talianki/Maidanetske): concentric rings of houses on green steppe."""
    world_gradient([(0.0, "#e8f0c0"), (1.0, "#9ad0e0")], "#e8f0c0", 0.02)
    tile_ground(200, "#8fc04a", steps=[(0, "#4a7a2a"), (0.01, "#6fa03a"), (0.05, "#8fc04a"), (0.3, "#b0d860")])
    rnd = random.Random(6)
    wall = T.toon("#f3e3c0", rim="#ffffff")
    roof = T.toon("#e08a3a", rim="#ffd27a")
    for ring, (rx, ry, n) in enumerate(((44, 30, 70), (36, 24, 56), (22, 15, 34))):
        for i in range(n):
            a = i / n * 2 * math.pi
            x, y = rx * math.cos(a), ry * math.sin(a)
            T.prim("cube", (x, y, 0.5), (1.1, 0.6, 0.5), rot=(0, 0, a), mat=wall, name="lh", bevel=0.05)
            T.prim("cube", (x, y, 1.15), (1.15, 0.55, 0.2), rot=(math.radians(0), 0, a), mat=roof, name="lr",
                   bevel=0.15)
    for i in range(40):
        bush((rnd.uniform(-90, 90), rnd.uniform(-70, 70), 0), rnd.uniform(1.2, 2.4), c1="#2f7a3a", c2="#3f9a4a",
             seed=i, berries=False)
    sun_light((55, 0, 200), "#fff4dc", 4.0)
    ortho_camera((0, 0, 0), -110, -80, 120, 96, elev=50, dist=140)


def uruk_city():
    """Uruk at sunset: a white temple on a high terrace above a dense mud-brick city, river and palms."""
    world_gradient([(0.0, "#ff9a4a"), (0.25, "#e2607a"), (0.6, "#7a4a9a"), (1.0, "#2a2a6a")], "#e2607a", 0.02)
    tile_ground(200, "#e8a24a", steps=[(0, "#8a3a2a"), (0.01, "#b8602a"), (0.05, "#e8a24a"), (0.3, "#f6c46a")])
    T.prim("cube", (0, -26, 0.02), (200, 4, 0.02), mat=T.toon("#3aa0b0", rim=None, steps=[(0, "#2a6a8a"),
                                                                                          (0.02, "#3aa0b0")]),
           name="river")
    rnd = random.Random(9)
    brick = T.toon("#e8b07a", rim="#ffd8a0")
    brick2 = T.toon("#d9945a", rim="#ffd8a0")
    for i in range(260):
        x, y = rnd.uniform(-30, 30), rnd.uniform(-20, 22)
        if abs(x) < 7 and abs(y) < 7:
            continue
        h = rnd.uniform(1.2, 3.2)
        w = rnd.uniform(1.2, 2.4)
        T.prim("cube", (x, y, h / 2), (w / 2, w / 2, h / 2), mat=brick if i % 3 else brick2, name="cb", bevel=0.05)
    # terrace + White Temple
    T.prim("cube", (0, 0, 2.0), (6.5, 6.5, 2.0), mat=T.toon("#d9a46a", rim="#ffe0b0"), name="terrace", bevel=0.2)
    T.prim("cube", (0, 0, 5.5), (4.0, 4.0, 1.5), mat=T.toon("#d9a46a", rim="#ffe0b0"), name="terrace2", bevel=0.15)
    T.prim("cube", (0, 0, 8.0), (3.0, 1.8, 1.0), mat=T.toon("#f6f0e6", rim="#ffffff"), name="temple", bevel=0.08)
    T.prim("cube", (0, -6.5, 3.0), (1.0, 3.5, 0.05), rot=(math.radians(-38), 0, 0),
           mat=T.toon("#c98a5a", rim=None), name="stairs")
    for i in range(30):
        x = rnd.uniform(-60, 60)
        palm3d((x, -29 - rnd.uniform(0, 6), 0), rnd.uniform(3, 5))
    for i in range(14):
        c = T.Char("u%d" % i, rnd.choice(["man", "woman"]), (rnd.uniform(-10, 10), rnd.uniform(-19, -11), 0),
                   rnd.uniform(0, 360), top=rnd.choice(["#1f7a8c", "#c8326f", "#2e8a78", "#e2682a", "#f6f0e6"]))
    sun_light((38, 0, -25), "#ffc890", 4.5)
    camera([(0, (-30, -48, 9)), (DUR, (-6, -50, 12))], [(0, (0, 0, 4)), (DUR, (0, 0, 5))], lens=40)


def palm3d(loc, h):
    root = T.empty("palm", loc)
    T.parent(T.prim("cyl", (0, 0, h / 2), (0.15, 0.15, h / 2), mat=T.toon("#6a4a2a", rim=None), name="trunk"), root)
    for k in range(7):
        a = k / 7 * 2 * math.pi
        T.parent(T.prim("sphere", (math.cos(a) * 0.9, math.sin(a) * 0.9, h - 0.1), (1.0, 0.25, 0.08),
                        rot=(0, math.radians(18), a), mat=T.toon("#167a44" if k % 2 else "#0f6b4a", rim="#ffd27a"),
                        name="frond"), root)
    return root


def crowd_top():
    """Night feast seen from above (the reference's top-down crowd around a fire)."""
    world_gradient([(0.0, "#160b2c"), (1.0, "#160b2c")], "#2a1850", 0.02)
    T.prim("circle", (0, 0, 0), (400, 400, 1), mat=T.toon("#a8342f", steps=[
        (0, "#1a0818"), (0.004, "#3a1230"), (0.02, "#6a1e3a"), (0.06, "#b8393a"), (0.16, "#e8642c"),
        (0.4, "#ffa23a")], rim=None, name="ground_n"), name="ground", seg=64)
    fire((0, 0, 0))
    sparks((0, 0, 1.0), n=16, life=1.6, rise=2.6, t0=0.2, seed=4)
    rnd = random.Random(12)
    for i in range(60):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(2.2, 9) if i > 10 else 2.4
        sit = r < 3.0
        c = T.Char("c%d" % i, rnd.choice(["man", "woman"]), (r * math.cos(a), r * math.sin(a), 0),
                   math.degrees(a) - 90 + rnd.uniform(-30, 30), night=True, sit=sit,
                   top=rnd.choice(["#1f7a8c", "#c8326f", "#2e8a78", "#e2682a", "#f0a83a", "#5b3fa0"]))
        if not sit and i % 3 == 0:
            for f in range(1, NF + 1, 18):
                p = "cheer" if (f // 18 + i) % 2 else "head"
                c.pose_arm("l", p, f)
                c.pose_arm("r", p, f)
    sun_light((60, 0, 200), "#5a4aa0", 0.25, "Moon")
    camera([(0, (0, -9, 14)), (DUR, (2.5, -7.5, 11))], [(0, (0, 0, 0)), (DUR, (0, 0, 0.5))], lens=30)


# ------------------------------------------------------------------ main
if __name__ == "__main__":
    sc = setup()
    {"fire_night": fire_night, "village_day": village_day, "enclosure_day": enclosure_day, "catal_town": catal_town,
     "megasite": megasite, "uruk_city": uruk_city, "crowd_top": crowd_top}[SCENE]()
    os.makedirs(OUT, exist_ok=True)
    if STILLS:
        for t in STILLS:
            sc.frame_set(F(t))
            sc.render.filepath = os.path.join(OUT, "still_%s_%05.2f.png" % (SCENE, t))
            bpy.ops.render.render(write_still=True)
    else:
        sc.render.use_overwrite = False
        sc.render.filepath = os.path.join(OUT, "f_")
        bpy.ops.render.render(animation=True)
