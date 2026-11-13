"""brand-loop: a seamless studio loop of glossy liquid blobs in a brand's colours (Blender EEVEE).

blender -b --factory-startup --python scene.py -- [options]
  --out DIR          frame folder (default ./frames)
  --res WxH          default 3840x2160 (landscape only)
  --samples N        EEVEE samples (default 16)
  --dur S            loop length in seconds (default 10)
  --fps N            default 60
  --frames a,b,c     render only these frames (stills, for previews)
  --range a-b        render this frame range (inclusive) as an animation (resumable, several processes can share --out)
  --cool  c1,..,c5   the cool blob family, dark -> light (default: KumNit blues/cyan)
  --warm  c1,c2,c3   the warm blob family, dark -> light (default: orange/amber/yellow)
  --paper c1,c2      backdrop centre and corner colours (default: warm off-white)
  look knobs: --key --fill --wash --emit --world --fstop --ringamt --ringbump --exposure --glow --mbres

The two families each merge with themselves (metaballs) and never touch each other. Everything moves with sin/cos
of whole multiples of the loop phase, so frame N is identical to frame 0 and the clip loops with no seam.
"""
import bpy, math, sys, os, time
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
opt, i = {}, 0
while i < len(argv):
    has_val = i + 1 < len(argv) and not argv[i + 1].startswith('--')
    opt[argv[i].lstrip('-')] = argv[i + 1] if has_val else '1'
    i += 2 if has_val else 1
num = lambda k, d: float(opt.get(k, d))

W, H = (int(v) for v in opt.get('res', '3840x2160').split('x'))
FPS = int(opt.get('fps', 60))
DUR = num('dur', 10)
N = int(round(FPS * DUR))            # frames in one loop; frame N == frame 0
OUT = os.path.abspath(opt.get('out', 'frames'))
TAU = math.tau

def lin(h):
    h = h.strip().lstrip('#')
    c = [int(h[k:k + 2], 16) / 255 for k in (0, 2, 4)]
    return [((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for v in c]
def srgb(h): return tuple(lin(h)) + (1.0,)
def to_hex(c):
    s = [(12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055) for v in c]
    return '#' + ''.join(f'{max(0, min(255, round(v * 255))):02x}' for v in s)
def ramp_colors(hexes, n):
    """n colours spread over the given ones (dark -> light), interpolated in linear light"""
    cs = [lin(h) for h in hexes]
    if len(cs) == 1: cs = cs * 2
    out = []
    for k in range(n):
        x = k / (n - 1) * (len(cs) - 1); a = min(int(x), len(cs) - 2); f = x - a
        out.append(to_hex([cs[a][j] * (1 - f) + cs[a + 1][j] * f for j in range(3)]))
    return out

# palette: cool family (5 shades), warm family (3 shades), backdrop
DEEP, BLUE, AZURE, SKY, CYAN = ramp_colors(opt.get('cool', '#012da4,#0065fc,#0179fe,#019ffe,#01dbf7').split(','), 5)
ORANGE, AMBER, YELLOW = ramp_colors(opt.get('warm', '#fe7601,#fe9000,#fdb801').split(','), 3)
PAPER0, PAPER1 = (opt.get('paper', '#fcfbf8,#f2eae0').split(',') + ['#f2eae0'])[:2]

# ---------------------------------------------------------------- render settings
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.resolution_percentage = 100
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 0, N - 1
sc.render.film_transparent = False
sc.render.filter_size = 1.5
sc.display_settings.display_device = 'sRGB'
sc.view_settings.view_transform = opt.get('view', 'Standard')
sc.view_settings.look = 'None'
sc.view_settings.exposure = num('exposure', 0.0)

ee = sc.eevee
ee.taa_render_samples = int(num('samples', 16))
ee.use_raytracing = True
ee.ray_tracing_method = 'SCREEN'
rto = ee.ray_tracing_options
rto.resolution_scale = opt.get('rtscale', '1')
rto.trace_max_roughness = 0.5
rto.screen_trace_quality = 1.0
rto.screen_trace_thickness = 0.05
rto.use_denoise = True
ee.use_shadows = True
ee.shadow_ray_count = int(num('shadowrays', 2))
ee.shadow_step_count = 10
ee.use_fast_gi = True
ee.fast_gi_method = 'GLOBAL_ILLUMINATION'
ee.use_bokeh_jittered = opt.get('jitter', '1') == '1'
ee.bokeh_max_size = 200
ee.bokeh_threshold = 1.0
ee.bokeh_overblur = 5

world = bpy.data.worlds.new('World'); sc.world = world
if world.node_tree is None:
    world.use_nodes = True
# studio environment: bright overhead, warm off-white horizon, darker warm floor. The blobs reflect it,
# which reads as a glossy liquid surface (bright top, horizon line, warm underside)
wn, wl = world.node_tree.nodes, world.node_tree.links
bgn = wn['Background']
wtc = wn.new('ShaderNodeTexCoord'); wsep = wn.new('ShaderNodeSeparateXYZ')
wl.new(wtc.outputs['Generated'], wsep.inputs[0])
wmap = wn.new('ShaderNodeMapRange'); wmap.inputs['From Min'].default_value = -1; wmap.inputs['From Max'].default_value = 1
wl.new(wsep.outputs['Z'], wmap.inputs['Value'])
wramp = wn.new('ShaderNodeValToRGB'); wl.new(wmap.outputs['Result'], wramp.inputs[0])
cr = wramp.color_ramp; cr.interpolation = 'EASE'
cr.elements[0].position = 0.0; cr.elements[0].color = srgb('#a99c8e')
cr.elements[1].position = 0.47; cr.elements[1].color = srgb('#e9e0d5')
e = cr.elements.new(0.56); e.color = srgb('#fbf8f4')
e = cr.elements.new(0.8); e.color = srgb('#ffffff')
wl.new(wramp.outputs['Color'], bgn.inputs['Color'])
bgn.inputs['Strength'].default_value = num('world', 0.55)

# ---------------------------------------------------------------- loop clock
# an Empty whose x goes 0 -> 1 over the loop; shaders read it through Object texture coords
clock = bpy.data.objects.new('Clock', None); sc.collection.objects.link(clock)
for f in range(0, N + 1):
    clock.location = (f / N, 0, 0); clock.keyframe_insert('location', index=0, frame=f)

# ---------------------------------------------------------------- camera
cam_d = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', cam_d)
sc.collection.objects.link(cam); sc.camera = cam
cam_d.lens = 50; cam_d.sensor_width = 36; cam_d.sensor_fit = 'HORIZONTAL'
cam_d.clip_start = 0.05; cam_d.clip_end = 20
CAM_D = 1.2
cam.rotation_euler = (math.radians(90), 0, 0)
cam_d.dof.use_dof = True
cam_d.dof.focus_distance = CAM_D
cam_d.dof.aperture_fstop = num('fstop', 2.0)
for f in range(0, N + 1):                     # a barely-there drift for parallax
    ph = TAU * f / N
    cam.location = (0.006 * math.sin(ph), -CAM_D, 0.004 * math.sin(ph + 1.3))
    cam.keyframe_insert('location', frame=f)

# ---------------------------------------------------------------- node helpers
def nodes_of(mat):
    if mat.node_tree is None:
        mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    return nt.nodes, nt.links

def math_node(nodes, links, op, a=None, b=None, va=0.0, vb=0.0, vc=0.0, clamp=False, c=None):
    n = nodes.new('ShaderNodeMath'); n.operation = op; n.use_clamp = clamp
    n.inputs[0].default_value = va; n.inputs[1].default_value = vb; n.inputs[2].default_value = vc
    if a is not None: links.new(a, n.inputs[0])
    if b is not None: links.new(b, n.inputs[1])
    if c is not None: links.new(c, n.inputs[2])
    return n.outputs[0]

def vmath(nodes, links, op, a=None, b=None, vb=(0, 0, 0)):
    n = nodes.new('ShaderNodeVectorMath'); n.operation = op
    if a is not None: links.new(a, n.inputs[0])
    if b is not None: links.new(b, n.inputs[1])
    else: n.inputs[1].default_value = vb
    return n.outputs['Value'] if op in ('LENGTH', 'DOT_PRODUCT', 'DISTANCE') else n.outputs['Vector']

def mixrgb(nodes, links, fac=None, a=None, b=None, blend='MIX'):
    n = nodes.new('ShaderNodeMix'); n.data_type = 'RGBA'; n.blend_type = blend; n.clamp_factor = True
    ins = {s.identifier: s for s in n.inputs}
    if isinstance(fac, (int, float)): ins['Factor_Float'].default_value = fac
    elif fac is not None: links.new(fac, ins['Factor_Float'])
    for key, v in (('A_Color', a), ('B_Color', b)):
        if isinstance(v, tuple): ins[key].default_value = v
        elif v is not None: links.new(v, ins[key])
    return [o for o in n.outputs if o.identifier == 'Result_Color'][0]

def clock_phase(nodes, links):
    """loop phase 0..1, read from the Clock empty: P_world - P_clocklocal = clock location"""
    geo = nodes.new('ShaderNodeNewGeometry')
    tc = nodes.new('ShaderNodeTexCoord'); tc.object = clock
    d = vmath(nodes, links, 'SUBTRACT', geo.outputs['Position'], tc.outputs['Object'])
    sep = nodes.new('ShaderNodeSeparateXYZ'); links.new(d, sep.inputs[0])
    return sep.outputs['X']

# ---------------------------------------------------------------- backdrop
BACK_Y = num('backy', 0.36)
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, BACK_Y, 0), rotation=(math.radians(90), 0, 0))
back = bpy.context.active_object; back.name = 'Backdrop'

RING_C = (0.0, BACK_Y, 0.01)          # ripple centre: behind the middle of the frame
RINGS_PER_LOOP = int(num('rings', 2))
RING_GAP = num('ringgap', 0.17)        # metres between rings
RING_W = num('ringw', 0.014)           # ring half-width (metres)

mat = bpy.data.materials.new('Backdrop'); back.data.materials.append(mat)
nodes, links = nodes_of(mat)
out = nodes.new('ShaderNodeOutputMaterial')
diff = nodes.new('ShaderNodeBsdfDiffuse')
emit = nodes.new('ShaderNodeEmission'); emit.inputs['Strength'].default_value = num('emit', 0.26)
add = nodes.new('ShaderNodeAddShader')
links.new(emit.outputs[0], add.inputs[0]); links.new(diff.outputs[0], add.inputs[1])
links.new(add.outputs[0], out.inputs['Surface'])
geo = nodes.new('ShaderNodeNewGeometry')
rel = vmath(nodes, links, 'SUBTRACT', geo.outputs['Position'], vb=RING_C)
sep = nodes.new('ShaderNodeSeparateXYZ'); links.new(rel, sep.inputs[0])
cmb = nodes.new('ShaderNodeCombineXYZ')
links.new(sep.outputs['X'], cmb.inputs['X']); links.new(sep.outputs['Z'], cmb.inputs['Y'])
r = vmath(nodes, links, 'LENGTH', cmb.outputs[0])
# warm gradient: brightest just above centre, warmer toward the corners and lower-right
g = math_node(nodes, links, 'MULTIPLY', r, vb=1.05)
g = math_node(nodes, links, 'MULTIPLY_ADD', sep.outputs['X'], vb=0.22, c=g)
g = math_node(nodes, links, 'MULTIPLY_ADD', sep.outputs['Z'], vb=-0.30, c=g, clamp=True)
ramp = nodes.new('ShaderNodeValToRGB'); links.new(g, ramp.inputs[0])
ramp.color_ramp.interpolation = 'EASE'
ramp.color_ramp.elements[0].color = srgb(PAPER0); ramp.color_ramp.elements[1].color = srgb(PAPER1)
# ripple rings: soft pulses travelling outward (RINGS_PER_LOOP per loop), faded in and out by radius
ph = clock_phase(nodes, links)
u = math_node(nodes, links, 'SUBTRACT', math_node(nodes, links, 'MULTIPLY', ph, vb=RINGS_PER_LOOP),
              math_node(nodes, links, 'DIVIDE', r, vb=RING_GAP))
u = math_node(nodes, links, 'SUBTRACT', math_node(nodes, links, 'FRACT', math_node(nodes, links, 'ADD', u, vb=0.5)), vb=0.5)
z = math_node(nodes, links, 'DIVIDE', u, vb=RING_W / RING_GAP)
ring = math_node(nodes, links, 'EXPONENT', math_node(nodes, links, 'MULTIPLY', math_node(nodes, links, 'MULTIPLY', z, z), vb=-1.0))
env_in = math_node(nodes, links, 'SMOOTH_MIN', math_node(nodes, links, 'DIVIDE', r, vb=0.12), vb=1.0, vc=0.5)
env_out = math_node(nodes, links, 'EXPONENT', math_node(nodes, links, 'MULTIPLY', r, vb=-2.4))
env = math_node(nodes, links, 'MULTIPLY', math_node(nodes, links, 'MAXIMUM', env_in, vb=0.0), env_out)
ringv = math_node(nodes, links, 'MULTIPLY', ring, env)
shade = math_node(nodes, links, 'MULTIPLY', ringv, vb=num('ringamt', 0.25))
col = mixrgb(nodes, links, shade, ramp.outputs['Color'], srgb(opt.get('ringcolor', '#e6dbcf')), 'MIX')
links.new(col, diff.inputs['Color']); links.new(col, emit.inputs['Color'])
bump = nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = num('ringbump', 0.3)
bump.inputs['Distance'].default_value = 0.003
links.new(ringv, bump.inputs['Height']); links.new(bump.outputs['Normal'], diff.inputs['Normal'])

# ---------------------------------------------------------------- lights
def area(name, loc, target, size, energy, color='#ffffff', shape='RECTANGLE', sy=None, spec=1.0, diffuse=1.0, shadow=True):
    d = bpy.data.lights.new(name, 'AREA'); d.shape = shape; d.size = size
    if sy is not None: d.size_y = sy
    d.energy = energy; d.color = srgb(color)[:3]; d.specular_factor = spec; d.diffuse_factor = diffuse
    d.use_shadow = shadow
    d.use_shadow_jitter = opt.get('shadowjitter', '0') == '1'
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return o

area('Key', (-0.62, -1.0, 0.72), (0, 0.05, 0), num('keysize', 0.7), num('key', 10), '#fffaf3', 'ELLIPSE', sy=num('keysize', 0.7) * 0.8)
area('Fill', (1.2, -0.55, -0.1), (0, 0, 0), 1.2, num('fill', 3), '#f1f5ff', spec=0.5)
area('Wash', (0.0, -1.8, 0.15), (0, BACK_Y, 0), 2.2, num('wash', 8), '#fff6ec', spec=0.0)
# reflection-only softboxes: they light nothing, they only show up as soft reflections on the gloss
area('TopBox', (0.1, -0.35, 0.95), (0, 0.0, 0), 1.5, num('topbox', 40), '#ffffff', sy=0.55, diffuse=0.0, shadow=False)
area('RimBox', (0.85, 0.25, -0.75), (0, 0.0, 0), 1.2, num('rimbox', 18), '#fff3e6', sy=0.3, diffuse=0.0, shadow=False)

# ---------------------------------------------------------------- blobs
# a lone metaball (stiffness 2, threshold 0.6) shows its surface at 0.575 x its radius
TH, STIFF = 0.6, 2.0
VIS = math.sqrt(1 - (TH / STIFF) ** (1 / 3))
# Blender won't tessellate metaballs finer than 5 mm (in object space). The blobs are built 10x larger
# and their objects scaled by 0.1, so the surface mesh can be ~1 mm in the scene: smooth highlights.
MBS = 0.1

def unit(v):
    l = math.sqrt(sum(x * x for x in v)); return tuple(x / l for x in v)

def drift(c, *terms):
    """fixed centre plus periodic wandering: terms are (axis, amplitude, whole cycles per loop, phase)"""
    def f(ph):
        p = list(c)
        for ax, amp, k, phi in terms:
            a = unit(ax); s = amp * math.sin(k * ph + phi)
            for j in range(3): p[j] += a[j] * s
        return p
    return f

def around(parent, rad, k, phi, u=(1, 0, 0), w=(0, 0, 1), breathe=0.0):
    """circles its parent k times per loop (a bulge sliding round a blob)"""
    u, w = unit(u), unit(w)
    def f(ph):
        p = parent(ph); a = k * ph + phi; rr = rad * (1 + breathe * math.sin(ph + phi * 0.7))
        return [p[j] + rr * (u[j] * math.cos(a) + w[j] * math.sin(a)) for j in range(3)]
    return f

def toward(parent, d, base, amp, k, phi, sway=0.0):
    """rocks to and fro along d from its parent: merges when close, pinches off when far"""
    d = unit(d)
    def f(ph):
        p = parent(ph); s = base + amp * math.sin(k * ph + phi)
        q = [p[j] + d[j] * s for j in range(3)]
        q[1] += sway * math.sin(ph + phi)
        return q
    return f

# x right, y depth (+ away from camera; focus plane y=0), z up. The frame at y=0 is 0.864 x 0.486 m.
Hm = drift((-0.335, 0.05, -0.15), ((1, 0, .4), .016, 1, 0.0), ((0, .3, 1), .012, 1, 1.9))
Cm = drift((0.305, 0.03, 0.135), ((1, .2, .3), .016, 1, 3.6), ((0, .2, 1), .014, 1, 0.8))
Om = drift((0.195, 0.0, -0.12), ((1, 0, .2), .016, 1, 5.5), ((0, .3, 1), .013, 1, 0.3))
P1 = drift((-0.275, 0.0, 0.172), ((1, 0, .2), .022, 1, 2.0), ((0, .5, 1), .016, 1, 4.1))
S1 = toward(Hm, (0.72, -0.1, 0.69), 0.205, 0.055, 1, 0.3, sway=0.015)
BLOBS = [
    # cool family
    dict(fam='Cool', v=0.122, pos=Hm, col=(DEEP, AZURE), wob=.035),
    dict(fam='Cool', v=0.066, pos=around(Hm, 0.078, 1, 0.6, (1, 0, 0), (0, -.4, .9), .12), col=(SKY, CYAN), wob=.05),
    dict(fam='Cool', v=0.056, pos=around(Hm, 0.08, -1, 2.5, (.9, .3, 0), (0, 0, 1), .1), col=(BLUE, AZURE), wob=.05),
    dict(fam='Cool', v=0.047, pos=S1, col=(BLUE, SKY), wob=.06),
    dict(fam='Cool', v=0.017, pos=around(S1, 0.066, 2, 0.0, (1, 0, 0), (0, -.3, .95), .15), col=(AZURE, CYAN), wob=.06),
    dict(fam='Cool', v=0.074, pos=Cm, col=(AZURE, CYAN), wob=.04),
    dict(fam='Cool', v=0.045, pos=around(Cm, 0.048, 1, 2.0, (1, 0, 0), (0, -.3, .95), .15), col=(CYAN, CYAN), wob=.05),
    dict(fam='Cool', v=0.031, pos=toward(Cm, (-0.76, 0, -0.55), 0.148, 0.045, 1, 3.4, sway=0.01), col=(SKY, CYAN), wob=.06),
    dict(fam='Cool', v=0.032, pos=drift((0.05, 0.21, 0.205), ((1, 0, 0), .04, 1, 4.4), ((0, 0, 1), .018, 1, 2.0)), col=(SKY, CYAN), wob=.05),
    dict(fam='Cool', v=0.060, pos=drift((0.268, -0.40, -0.152), ((1, 0, .3), .012, 1, 1.4), ((0, 0, 1), .01, 1, 5.0)), col=(BLUE, SKY), wob=.03),
    # warm family
    dict(fam='Warm', v=0.068, pos=Om, col=(ORANGE, AMBER), wob=.04),
    dict(fam='Warm', v=0.040, pos=around(Om, 0.042, 1, 4.0, (1, 0, 0), (0, -.3, .95), .15), col=(AMBER, YELLOW), wob=.05),
    dict(fam='Warm', v=0.036, pos=toward(Om, (0.8, 0, 0.6), 0.148, 0.045, 1, 1.2, sway=0.012), col=(AMBER, YELLOW), wob=.06),
    dict(fam='Warm', v=0.028, pos=P1, col=(ORANGE, YELLOW), wob=.05),
    dict(fam='Warm', v=0.016, pos=toward(P1, (0.9, 0, 0.4), 0.056, 0.02, 1, 0.5), col=(AMBER, YELLOW), wob=.06),
    dict(fam='Warm', v=0.026, pos=drift((-0.02, 0.21, -0.205), ((1, 0, 0), .04, 1, 0.9), ((0, 0, 1), .02, 1, 3.3)), col=(AMBER, YELLOW), wob=.05),
]

def wob_at(b, i, ph):
    w = b['wob']
    sx = 1 + w * math.sin(ph * 2 + i * 1.7)
    sz = 1 + w * math.sin(ph * 2 + i * 1.7 + 2.1)
    return (sx * MBS, MBS / (sx * sz), sz * MBS)   # keep volume

def blob_material(name, members):
    """colour = blend of each member's own two-tone colour, weighted by closeness (measured in the
    member's own space, so it follows its squash). Merging blobs get liquid-looking gradients."""
    m = bpy.data.materials.new(name)
    nodes, links = nodes_of(m)
    out = nodes.new('ShaderNodeOutputMaterial')
    p = nodes.new('ShaderNodeBsdfPrincipled'); links.new(p.outputs[0], out.inputs['Surface'])
    p.inputs['Roughness'].default_value = num('rough', 0.22)
    p.inputs['Specular IOR Level'].default_value = 0.5
    p.inputs['Coat Weight'].default_value = 1.0
    p.inputs['Coat Roughness'].default_value = num('coatrough', 0.08)
    p.inputs['Coat IOR'].default_value = num('coatior', 1.6)
    p.inputs['Subsurface Weight'].default_value = 0.06
    p.inputs['Subsurface Radius'].default_value = (0.6, 0.6, 0.6)
    p.inputs['Subsurface Scale'].default_value = 0.01
    num_c = num_w = None
    for b, o in members:
        tc = nodes.new('ShaderNodeTexCoord'); tc.object = o
        loc = tc.outputs['Object']
        q = math_node(nodes, links, 'DIVIDE', vmath(nodes, links, 'LENGTH', loc), vb=b['v'] / MBS)
        w = math_node(nodes, links, 'EXPONENT', math_node(nodes, links, 'MULTIPLY', math_node(nodes, links, 'MULTIPLY', q, q), vb=-3.2))
        w = math_node(nodes, links, 'MULTIPLY', w, vb=b['v'] / 0.05)       # bigger blobs dominate the mix
        # two-tone within each blob: deeper toward the lower-left/back, lighter toward the upper-right/front
        g = vmath(nodes, links, 'DOT_PRODUCT', loc, vb=unit((0.55, -0.35, 0.75)))
        g = math_node(nodes, links, 'MULTIPLY_ADD', math_node(nodes, links, 'DIVIDE', g, vb=b['v'] / MBS), vb=0.5, vc=0.5, clamp=True)
        cw = vmath(nodes, links, 'SCALE', mixrgb(nodes, links, g, srgb(b['col'][0]), srgb(b['col'][1])))
        links.new(w, cw.node.inputs['Scale'])
        num_c = cw if num_c is None else vmath(nodes, links, 'ADD', num_c, cw)
        num_w = w if num_w is None else math_node(nodes, links, 'ADD', num_w, w)
    inv = math_node(nodes, links, 'DIVIDE', None, math_node(nodes, links, 'MAXIMUM', num_w, vb=1e-6), va=1.0)
    c = vmath(nodes, links, 'SCALE', num_c); links.new(inv, c.node.inputs['Scale'])
    links.new(c, p.inputs['Base Color'])
    links.new(c, p.inputs['Emission Color'])                 # a little self-light keeps the brand colours vivid
    p.inputs['Emission Strength'].default_value = num('glow', 0.18)
    return m

fams = {}
for i, b in enumerate(BLOBS):
    fam = b['fam']; k = len(fams.setdefault(fam, []))
    name = fam if k == 0 else f'{fam}.{k:03d}'        # same base name = same metaball family (they merge)
    mb = bpy.data.metaballs.new(name + '_mb')
    mb.resolution = 0.006 / MBS; mb.render_resolution = num('mbres', 0.001) / MBS; mb.threshold = TH
    el = mb.elements.new(); el.co = (0, 0, 0); el.radius = b['v'] / VIS / MBS; el.stiffness = STIFF
    o = bpy.data.objects.new(name, mb); sc.collection.objects.link(o)
    fams[fam].append((b, o))
    for f in range(0, N + 1):
        ph = TAU * f / N
        o.location = b['pos'](ph); o.scale = wob_at(b, i, ph)
        o.keyframe_insert('location', frame=f); o.keyframe_insert('scale', frame=f)
for fam, members in fams.items():
    members[0][1].data.materials.append(blob_material(fam + 'Gloss', members))

# the two families must never touch (they would cut through each other instead of merging)
gap = (9, None)
for f in range(0, N, 2):
    ph = TAU * f / N
    for bc, oc in fams['Cool']:
        for bw, ow in fams['Warm']:
            d = math.dist(bc['pos'](ph), bw['pos'](ph)) - (bc['v'] + bw['v']) * 1.12
            if d < gap[0]: gap = (round(d, 4), oc.name, ow.name, f)
print(f'LOOP {N} frames, closest cool/warm clearance {gap[0]} m' + (' WARNING: they touch' if gap[0] < 0 else ''))

os.makedirs(OUT, exist_ok=True)
if 'save' in opt:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(opt['save']))

# ---------------------------------------------------------------- render
ims = sc.render.image_settings
ims.file_format = 'PNG'; ims.color_mode = 'RGB'; ims.color_depth = '8'; ims.compression = 15
sc.render.dither_intensity = 1.0
if 'frames' in opt:
    for f in [int(x) for x in opt['frames'].split(',')]:
        t0 = time.time()
        sc.frame_set(f)
        sc.render.filepath = os.path.join(OUT, f'still_{f:04d}.png')
        bpy.ops.render.render(write_still=True)
        print(f'STILL {f} {time.time() - t0:.1f}s')
elif 'range' in opt:
    a, b = (int(x) for x in opt['range'].split('-'))
    sc.frame_start, sc.frame_end = a, b
    sc.render.filepath = os.path.join(OUT, 'f_')
    sc.render.use_overwrite = False        # several Blender processes can share one folder,
    sc.render.use_placeholder = True       # and a stopped render resumes where it left off
    bpy.ops.render.render(animation=True)
