"""Environment building blocks: sky, lighting, ground, trees, flowers, house ..."""
import math

import bpy
import numpy as np

import bl_util as U
from bl_util import mat, sphere, cyl, box, empty, obj

PI = math.pi


def setup_render(preview=False):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.fps = U.FPS
    if preview:
        sc.render.resolution_x, sc.render.resolution_y = 960, 540
        sc.eevee.taa_render_samples = 8
    else:
        sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
        sc.eevee.taa_render_samples = 16
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    try:
        sc.eevee.use_shadows = True
        sc.eevee.shadow_ray_count = 1
        sc.eevee.shadow_step_count = 4
    except AttributeError:
        pass
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 94
    sc.render.film_transparent = False


def sky(top="#4FA8F0", horizon="#CDEBFF", strength=1.0, ground="#8BC34A"):
    w = bpy.data.worlds.new("sky")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0
    cr.elements[0].color = U.rgb(horizon)
    cr.elements[1].position = 0.45
    cr.elements[1].color = U.rgb(top)
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    # Generated for the world is the view direction; use its Z
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 1.0
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    return w


def sun_light(energy=3.0, color="#FFF3DC", rot=(50, 0, -35), angle=8):
    L = bpy.data.lights.new("sun", "SUN")
    L.energy = energy
    L.color = U.rgb(color)[:3]
    L.angle = math.radians(angle)
    ob = bpy.data.objects.new("sun", L)
    U.link(ob)
    ob.rotation_euler = tuple(math.radians(a) for a in rot)
    return ob


def fill_light(energy=60, loc=(0, -6, 4), color="#FFFFFF", size=6):
    L = bpy.data.lights.new("fill", "AREA")
    L.energy = energy
    L.size = size
    L.color = U.rgb(color)[:3]
    try:
        L.use_shadow = False
    except AttributeError:
        pass
    ob = bpy.data.objects.new("fill", L)
    U.link(ob)
    ob.location = loc
    d = -np.array(loc, dtype=float)
    from mathutils import Vector
    ob.rotation_euler = Vector(d).to_track_quat("-Z", "Y").to_euler()
    return ob


def ground(c1="#7ED957", c2="#5DBB3F", radius=80):
    g = cyl("ground", (0, 0, -0.02), radius, 0.02, U.noise_mat(c1, c2, 0.35, 0.95, "grass"),
            seg=64)
    return g


def hills(colors=("#6CC04A", "#8BD35F", "#5AAE3C"), far=18, n=9, seed=3):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x = -30 + 60 * k / (n - 1) + rng.uniform(-3, 3)
        y = far + rng.uniform(0, 10)
        r = rng.uniform(7, 13)
        sphere("hill%d" % k, (x, y, -r * 0.55), (r, r * 0.7, r * 0.75),
               mat(colors[k % len(colors)], 0.95), seg=48)


def cloud(loc, s=1.0, name="cloud"):
    g = empty(name, loc)
    m = mat("#FFFFFF", 0.9, emit=0.35)
    for k, (x, z, r) in enumerate(((0, 0, 1.0), (1.0, -0.2, 0.75), (-1.0, -0.25, 0.7),
                                   (0.5, 0.35, 0.7), (-0.45, 0.3, 0.65))):
        sphere(name + "_%d" % k, (x * s, 0, z * s), r * s, m, g, seg=24)
    return g


def clouds(A, n=6, seed=1, z=(6, 10), y=(20, 35)):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x0 = rng.uniform(-25, 25)
        c = cloud((x0, rng.uniform(*y), rng.uniform(*z)), rng.uniform(1.2, 2.2), "cloud%d" % k)
        A.set(c, "location", 0, x0 + 0.12 * A.t)


def tree(loc, s=1.0, leaf="#4CAF50", name="tree", apples=0, seed=0):
    g = empty(name, loc)
    g.scale = (s, s, s)
    cyl(name + "_trunk", (0, 0, 0), 0.18, 1.5, mat("#8D5A3B", 0.8), g, r2=0.7)
    lm = mat(leaf, 0.7)
    lm2 = mat(U_shift(leaf), 0.7)
    rng = np.random.default_rng(seed)
    for k, (x, y, z, r) in enumerate(((0, 0, 2.0, 0.95), (0.7, 0.1, 1.7, 0.7), (-0.7, 0.05, 1.75, 0.7),
                                      (0.3, -0.35, 2.5, 0.65), (-0.35, 0.3, 2.55, 0.65),
                                      (0, 0.4, 1.6, 0.7))):
        sphere(name + "_leaf%d" % k, (x, y, z), r, lm if k % 2 == 0 else lm2, g)
    am = mat("#E53935", 0.35, coat=0.4)
    for k in range(apples):
        a = rng.uniform(0, 2 * PI)
        z = rng.uniform(1.5, 2.6)
        rr = 0.9 - abs(z - 2.0) * 0.3
        sphere(name + "_apple%d" % k, (rr * math.cos(a), -abs(rr * math.sin(a)) - 0.3, z), 0.1,
               am, g, seg=16)
    return g


def U_shift(hexcol, f=0.85):
    h = hexcol.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % (int(r * f), int(g * f), min(255, int(b * f + 10)))


def bush(loc, s=0.5, color="#43A047", name="bush"):
    g = empty(name, loc)
    m = mat(color, 0.8)
    for k, (x, z, r) in enumerate(((0, 0.5, 0.8), (0.7, 0.35, 0.6), (-0.7, 0.35, 0.6))):
        sphere(name + "_%d" % k, (x * s, 0, z * s), r * s, m, g, seg=20)
    return g


def flower(loc, color, s=1.0, name="flower", petals=6, center="#FFEB3B"):
    """Flower with a stem; the head faces the camera (-Y). Returns the head empty."""
    g = empty(name, loc)
    g.scale = (s, s, s)
    h = 0.35
    cyl(name + "_stem", (0, 0, 0), 0.018, h, mat("#388E3C", 0.7), g, seg=8)
    for sd in (-1, 1):
        sphere(name + "_lf%d" % sd, (sd * 0.05, 0, h * 0.35), (0.06, 0.02, 0.025),
               mat("#43A047", 0.7), g, rot=(0, -sd * 0.5, 0), seg=12)
    head = empty(name + "_head", (0, 0, h), g, rot=(0.25, 0, 0))
    pm = mat(color, 0.5)
    for k in range(petals):
        a = 2 * PI * k / petals
        sphere(name + "_p%d" % k, (0.06 * math.cos(a), 0, 0.06 * math.sin(a)),
               (0.055, 0.02, 0.035), pm, head, rot=(0, -a, 0), seg=14)
    sphere(name + "_c", (0, -0.012, 0), (0.04, 0.025, 0.04), mat(center, 0.5), head, seg=14)
    return g


def flower_field(n, area, seed, colors=("#E53935", "#FFEB3B", "#EC407A", "#AB47BC", "#FFFFFF",
                                         "#FF9800"), s=(0.6, 1.0), avoid=()):
    rng = np.random.default_rng(seed)
    x0, x1, y0, y1 = area
    k = 0
    while k < n:
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        if any(abs(x - ax) < aw and abs(y - ay) < ah for ax, ay, aw, ah in avoid):
            continue
        flower((x, y, 0), colors[k % len(colors)], rng.uniform(*s), "ff%d_%d" % (seed, k))
        k += 1


def fence(x0, x1, y, name="fence", color="#FFFFFF", h=0.7):
    m = mat(color, 0.6)
    n = int((x1 - x0) / 0.6) + 1
    for k in range(n):
        x = x0 + k * (x1 - x0) / (n - 1)
        box(name + "_post%d" % k, (x, y, h / 2), (0.08, 0.08, h), m, bevel=0.3)
        cyl(name + "_cap%d" % k, (x, y, h), 0.04, 0.06, m, r2=0.0, seg=4, rot=(0, 0, PI / 4))
    for z in (h * 0.4, h * 0.8):
        box(name + "_rail%.2f" % z, ((x0 + x1) / 2, y + 0.05, z), (x1 - x0, 0.04, 0.08), m,
            bevel=0.3)


def house(loc, name="house", wall="#FFF59D", roof="#E53935", door_col="#42A5F5"):
    g = empty(name, loc)
    W, D, H = 3.0, 1.9, 2.25
    box(name + "_walls", (0, 0, H / 2), (W, D, H), mat(wall, 0.7), g, bevel=0.03)
    obj(name + "_roof", U.mesh_prism(), (0, 0, H), (W / 2 + 0.18, D / 2 + 0.22, 1.15),
        m=mat(roof, 0.5), parent=g)
    box(name + "_chim", (0.85, 0.2, H + 0.85), (0.28, 0.28, 0.7), mat("#8D6E63", 0.7), g, bevel=0.1)
    # door on the front (-Y) with a hinge pivot
    dw, dh = 0.72, 1.78
    hinge = empty(name + "_hinge", (-dw / 2, -D / 2 - 0.01, 0.0), g)
    box(name + "_door", (dw / 2, -0.02, dh / 2), (dw, 0.05, dh), mat(door_col, 0.5), hinge, bevel=0.2)
    sphere(name + "_knob", (dw - 0.1, -0.06, dh * 0.5), 0.035, mat("#FFC107", 0.2, metal=0.8), hinge)
    fm = mat("#FFFFFF", 0.6)
    for sx in (-1, 1):
        box(name + "_frame%d" % sx, (sx * (dw / 2 + 0.04), -D / 2 - 0.01, dh / 2 + 0.04),
            (0.07, 0.06, dh + 0.08), fm, g, bevel=0.2)
    box(name + "_framet", (0, -D / 2 - 0.01, dh + 0.06), (dw + 0.15, 0.06, 0.08), fm, g, bevel=0.2)
    box(name + "_dark", (0, -D / 2 - 0.002, dh / 2), (dw, 0.02, dh), mat("#3E2723", 0.9), g, bevel=0.0)
    for sx in (-1, 1):
        wx, wz = sx * 0.95, 1.35
        box(name + "_win%d" % sx, (wx, -D / 2 - 0.01, wz), (0.55, 0.05, 0.55),
            mat("#B3E5FC", 0.15, emit=0.2), g, bevel=0.2)
        box(name + "_winf%d" % sx, (wx, -D / 2, wz), (0.65, 0.04, 0.65), fm, g, bevel=0.2)
        box(name + "_winx%d" % sx, (wx, -D / 2 - 0.04, wz), (0.55, 0.02, 0.04), fm, g, bevel=0.3)
        box(name + "_winy%d" % sx, (wx, -D / 2 - 0.04, wz), (0.04, 0.02, 0.55), fm, g, bevel=0.3)
        flower((wx - 0.15, -D / 2 - 0.2, 0), "#EC407A", 0.9, name + "_fl%d" % sx)
        flower((wx + 0.15, -D / 2 - 0.2, 0), "#FFEB3B", 0.8, name + "_fm%d" % sx)
    # path
    cyl(name + "_path", (0, -D / 2 - 1.2, 0.0), (0.5, 1.2), 0.012, mat("#F2D8A7", 0.9), g, seg=32)
    return g, hinge


def barn(loc, name="barn"):
    g = empty(name, loc)
    W, D, H = 3.2, 2.4, 2.2
    red = mat("#D84343", 0.7)
    white = mat("#FFFFFF", 0.6)
    box(name + "_walls", (0, 0, H / 2), (W, D, H), red, g, bevel=0.02)
    obj(name + "_roof", U.mesh_prism(), (0, 0, H), (W / 2 + 0.15, D / 2 + 0.2, 1.3),
        m=mat("#6D4C41", 0.6), parent=g)
    box(name + "_door", (0, -D / 2 - 0.02, 0.8), (1.2, 0.05, 1.6), mat("#B71C1C", 0.7), g, bevel=0.1)
    for a in (0.93, -0.93):
        box(name + "_x%.1f" % a, (0, -D / 2 - 0.05, 0.8), (1.9, 0.04, 0.1), white, g,
            rot=(0, a, 0), bevel=0.2)
    box(name + "_trim", (0, -D / 2 - 0.04, 0.8), (1.3, 0.03, 1.7), white, g, bevel=0.05)
    box(name + "_trimi", (0, -D / 2 - 0.045, 0.8), (1.1, 0.03, 1.5), mat("#B71C1C", 0.7), g, bevel=0.05)
    box(name + "_loft", (0, -D / 2 - 0.02, H + 0.4), (0.6, 0.05, 0.5), white, g, bevel=0.2)
    return g


def hay(loc, name="hay"):
    cyl(name, loc, 0.35, 0.6, mat("#FFD54F", 0.9), rot=(PI / 2, 0, 0.3), seg=24)


def sun_disc(loc, r=2.2, face=True, color="#FFE14D", name="sunball"):
    g = empty(name, loc)
    sphere(name + "_b", (0, 0, 0), r, U.flat(color, strength=1.4), g)
    for k in range(12):
        a = 2 * PI * k / 12
        obj(name + "_ray%d" % k, U.mesh_cyl(8, 1, 0), (1.25 * r * math.cos(a), 0, 1.25 * r * math.sin(a)),
            (0.25 * r, 0.25 * r, 0.45 * r), (0, PI / 2 - a, 0), U.flat(color, strength=1.2), g)
        bpy.data.objects[name + "_ray%d" % k].rotation_euler = (0, PI / 2 - a, 0)
    if face:
        dark = U.flat("#8D5A00")
        for sx in (-1, 1):
            sphere(name + "_e%d" % sx, (sx * 0.35 * r, -r * 0.93, 0.2 * r), (0.1 * r, 0.05 * r, 0.16 * r),
                   dark, g)
            sphere(name + "_c%d" % sx, (sx * 0.55 * r, -r * 0.8, -0.15 * r), (0.15 * r, 0.05 * r, 0.1 * r),
                   U.flat("#FF8A65"), g)
        obj(name + "_m", U.mesh_torus(0.35 * r, 0.05 * r, 20, 8, PI, PI), (0, -r * 0.95, -0.15 * r), 1,
            m=dark, parent=g)
    return g


def butterfly(name="butterfly", color="#1E88E5"):
    g = empty(name, (0, 0, 0))
    body = mat("#263238", 0.5)
    wm = mat(color, 0.35, emit=0.15)
    wm2 = mat("#90CAF9", 0.35)
    cyl(name + "_body", (0, 0, -0.06), 0.012, 0.12, body, g, seg=8)
    wings = []
    for s in (-1, 1):
        w = empty(name + "_w%d" % s, (0, 0, 0), g)
        sphere(name + "_wu%d" % s, (s * 0.055, 0, 0.025), (0.055, 0.006, 0.045), wm, w, seg=16)
        sphere(name + "_wl%d" % s, (s * 0.04, 0, -0.03), (0.035, 0.006, 0.03), wm, w, seg=16)
        sphere(name + "_wd%d" % s, (s * 0.06, -0.004, 0.03), (0.018, 0.004, 0.015), wm2, w, seg=10)
        wings.append((s, w))
    return g, wings


def swing_set(loc, name="swings"):
    g = empty(name, loc)
    m = mat("#FF7043", 0.5)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(name + "_leg%d%d" % (sx, sy), (sx * 1.2, sy * 0.45, 0), 0.05, 2.05, m, g,
                rot=(sy * 0.22, 0, 0))
    cyl(name + "_top", (-1.25, 0, 2.0), 0.06, 2.5, m, g, rot=(0, PI / 2, 0))
    seats = []
    for k, x in enumerate((-0.5, 0.5)):
        p = empty(name + "_piv%d" % k, (x, 0, 1.98), g)
        for sx in (-1, 1):
            cyl(name + "_rope%d%d" % (k, sx), (sx * 0.2, 0, -1.5), 0.012, 1.5, mat("#795548", 0.8), p, seg=6)
        box(name + "_seat%d" % k, (0, 0, -1.5), (0.5, 0.22, 0.05), mat(["#29B6F6", "#FFCA28"][k], 0.5), p)
        seats.append(p)
    return g, seats


def slide(loc, name="slide"):
    g = empty(name, loc)
    m = mat("#29B6F6", 0.4, coat=0.3)
    frame = mat("#FFCA28", 0.5)
    for sx in (-1, 1):
        cyl(name + "_lad%d" % sx, (sx * 0.3, 0.6, 0), 0.04, 1.6, frame, g)
    for k in range(5):
        cyl(name + "_rung%d" % k, (-0.3, 0.6, 0.3 + k * 0.3), 0.025, 0.6, frame, g, rot=(0, PI / 2, 0))
    box(name + "_plat", (0, 0.35, 1.55), (0.7, 0.55, 0.08), frame, g)
    box(name + "_chute", (0, -0.75, 0.82), (0.6, 2.1, 0.06), m, g, rot=(-0.72, 0, 0), bevel=0.4)
    for sx in (-1, 1):
        box(name + "_side%d" % sx, (sx * 0.31, -0.75, 0.9), (0.05, 2.1, 0.15), m, g, rot=(-0.72, 0, 0),
            bevel=0.4)
    return g


def sandbox(loc, name="sandbox"):
    g = empty(name, loc)
    wood = mat("#A1887F", 0.8)
    for k, (x, y, w, d) in enumerate(((0, -0.8, 2.0, 0.12), (0, 0.8, 2.0, 0.12), (-1, 0, 0.12, 1.7),
                                      (1, 0, 0.12, 1.7))):
        box(name + "_b%d" % k, (x, y, 0.1), (w, d, 0.2), wood, g, bevel=0.2)
    box(name + "_sand", (0, 0, 0.08), (1.9, 1.5, 0.12), mat("#FFE0A3", 0.95), g, bevel=0.1)
    cyl(name + "_bucket", (0.4, 0.2, 0.14), 0.12, 0.2, mat("#E53935", 0.4), g, r2=1.3)
    return g


def picnic_blanket(loc, w=2.6, d=1.6, name="blanket"):
    ob = obj(name, U.mesh_box(0.02), (loc[0], loc[1], 0.01), (w / 2, d / 2, 0.01),
             m=U.checker_mat("#E53935", "#FFFFFF", 8.0))
    # simple UVs for the checker: use generated coordinates instead
    m = ob.material_slots[0].material
    nt = m.node_tree
    tc = [n for n in nt.nodes if n.type == "TEX_COORD"][0]
    tex = [n for n in nt.nodes if n.type == "TEX_CHECKER"][0]
    nt.links.new(tc.outputs["Generated"], tex.inputs["Vector"])
    return ob


def basket(loc, name="basket"):
    g = empty(name, loc)
    cyl(name + "_b", (0, 0, 0), (0.3, 0.22), 0.3, mat("#C68B4E", 0.8), g, r2=1.1, seg=24)
    obj(name + "_h", U.mesh_torus(0.26, 0.025, 24, 8, PI, 0), (0, 0, 0.3), 1, (0, 0, 0),
        mat("#A0703E", 0.8), g)
    sphere(name + "_cloth", (0, 0, 0.3), (0.28, 0.2, 0.06), mat("#FFFFFF", 0.8), g)
    return g


def apple(name, loc, r=0.11, parent=None, color="#E53935"):
    g = empty(name, loc, parent)
    sphere(name + "_b", (0, 0, r), (r, r, r * 0.92), mat(color, 0.3, coat=0.5), g, seg=24)
    cyl(name + "_st", (0, 0, r * 1.7), r * 0.08, r * 0.45, mat("#5D4037", 0.7), g, seg=6)
    sphere(name + "_lf", (r * 0.25, 0, r * 2.05), (r * 0.3, r * 0.08, r * 0.14), mat("#43A047", 0.6), g,
           rot=(0, -0.5, 0), seg=10)
    return g


def banana(name, loc, s=1.0, parent=None):
    g = empty(name, loc, parent)
    g.scale = (s, s, s)
    obj(name + "_b", U.mesh_torus(0.2, 0.05, 24, 10, PI * 0.55, PI * 1.22), (0, 0, 0.25), 1,
        (0, 0, 0), mat("#FFE135", 0.45), g)
    sphere(name + "_tip", (0.2 * math.cos(PI * 1.22), 0, 0.25 + 0.2 * math.sin(PI * 1.22)), 0.03,
           mat("#6D4C41", 0.7), g, seg=8)
    return g


def bread(name, loc, s=1.0, parent=None):
    g = empty(name, loc, parent)
    g.scale = (s, s, s)
    sphere(name + "_l", (0, 0, 0.1), (0.2, 0.12, 0.11), mat("#D9A05B", 0.6), g)
    for k in range(3):
        sphere(name + "_c%d" % k, (-0.1 + k * 0.1, -0.01, 0.2), (0.03, 0.1, 0.012), mat("#F5D19A", 0.7),
               g, rot=(0, 0.5, 0), seg=10)
    return g


def milk(name, loc, s=1.0, parent=None):
    g = empty(name, loc, parent)
    g.scale = (s, s, s)
    box(name + "_c", (0, 0, 0.17), (0.18, 0.18, 0.34), mat("#FFFFFF", 0.5), g, bevel=0.1)
    box(name + "_lab", (0, -0.092, 0.16), (0.16, 0.01, 0.14), mat("#29B6F6", 0.5), g, bevel=0.1)
    obj(name + "_top", U.mesh_prism(), (0, 0, 0.34), (0.09, 0.09, 0.09), m=mat("#29B6F6", 0.5),
        parent=g, rot=(0, 0, PI / 2))
    return g


def water(name, loc, s=1.0, parent=None):
    g = empty(name, loc, parent)
    g.scale = (s, s, s)
    cyl(name + "_g", (0, 0, 0), 0.1, 0.3, mat("#E1F5FE", 0.05, alpha=0.35, coat=1.0), g, r2=1.15)
    cyl(name + "_w", (0, 0, 0.01), 0.095, 0.22, mat("#4FC3F7", 0.1, emit=0.15), g, r2=1.12)
    sphere(name + "_d", (0.03, -0.1, 0.2), (0.02, 0.01, 0.03), U.flat("#FFFFFF"), g, seg=8)
    return g


def quiz_stage(name="stage"):
    g = empty(name, (0, 0, 0))
    box(name + "_back", (0, 3.2, 2.0), (12, 0.2, 5), mat("#7E57C2", 0.8), g, bevel=0.0)
    cols = ["#FFCA28", "#EF5350", "#29B6F6", "#66BB6A", "#FF7043", "#EC407A"]
    rng = np.random.default_rng(4)
    for k in range(18):
        cyl(name + "_dot%d" % k, (rng.uniform(-5.5, 5.5), 3.08, rng.uniform(0.6, 4.2)),
            rng.uniform(0.1, 0.3), 0.03, mat(cols[k % 6], 0.5, emit=0.3), g, rot=(PI / 2, 0, 0))
    cyl(name + "_floor", (0, 0.4, 0), 4.5, 0.12, mat("#FFB74D", 0.5), g, seg=48)
    cyl(name + "_floor2", (0, 0.4, 0.12), 3.8, 0.02, mat("#FFE082", 0.5), g, seg=48)
    # board
    board = empty(name + "_board", (1.0, 1.1, 0))
    box(name + "_bframe", (0, 0.1, 1.3), (1.9, 0.15, 1.5), mat("#FF7043", 0.4), board, bevel=0.1)
    box(name + "_bface", (0, 0.0, 1.3), (1.65, 0.1, 1.25), mat("#FFFFFF", 0.8), board, bevel=0.05)
    for sx in (-1, 1):
        cyl(name + "_bleg%d" % sx, (sx * 0.8, 0.15, 0), 0.05, 0.6, mat("#FF7043", 0.4), board)
    # light bulbs around the frame
    for k in range(14):
        a = 2 * PI * k / 14
        sphere(name + "_bulb%d" % k, (1.0 * math.cos(a), -0.05, 1.3 + 0.8 * math.sin(a)), 0.04,
               U.flat("#FFF59D", strength=2.0), board, seg=10)
    return g, board
