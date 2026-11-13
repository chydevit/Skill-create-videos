"""saas-promo soundtrack -> <project>/build/mix.wav (-14 LUFS, -1 dBTP)

python audio.py <project>/promo.json        (needs build/cues.json from the plan stage)

Two buses:
  bed  an original ambient synth bed in four parts that follow the scenes (tense Dm add9 + rising hats under the swirl,
       bright Bbmaj9 + plucked 16ths and a soft kick on the meadow, dark Gm9 + sub pulse under the orb, a wide Fmaj9 with
       shimmer on the finale), all in code.  Or the user's own track: promo.json "music", started where assets.py says (manifest "music".start: the
       first cut on the song's drop) or at "musicStart".
  fx   one sound effect per cue from the scene (typing keys, glyph clicks, neon blips, whooshes, riser, impacts, glitch...).
       promo.json "sfxDir" is a folder of sound files; the names in SFX below are tried first, anything missing is synthesised.
"""
import json, os, subprocess, sys
import numpy as np
from scipy import signal

CFG_PATH = os.path.abspath(sys.argv[1])
P = os.path.dirname(CFG_PATH)
CFG = json.load(open(CFG_PATH))
TL = json.load(open(f'{P}/build/cues.json'))
SR = 48000
DUR = TL['dur']
N = int(round(SR * DUR))
S = TL['sections']
rng = np.random.default_rng(7)


def resolve(p):
    p = os.path.expanduser(p)
    return p if os.path.isabs(p) else os.path.join(P, p)
def load(path, ss=0.0, dur=None):
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-ss', str(ss), '-i', path]
    if dur is not None: cmd += ['-t', str(dur)]
    raw = subprocess.run(cmd + ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
def db(x): return 10 ** (x / 20)
def m2f(m): return 440.0 * 2 ** ((m - 69) / 12)
def st(x, pan=0.5): return np.stack([x * np.sqrt(1 - pan), x * np.sqrt(pan)], 1)
def sos(kind, f, order=2): return signal.butter(order, f, kind, fs=SR, output='sos')
def lp(x, f, order=4): return signal.sosfilt(sos('low', f, order), x, axis=0)
def hp(x, f, order=2): return signal.sosfilt(sos('high', f, order), x, axis=0)
def bp(x, lo, hi): return signal.sosfilt(sos('band', [lo, hi]), x, axis=0)
def place(bus, clip, t):
    i = int(round(t * SR)); j0 = max(0, -i); i = max(0, i)
    n = min(len(clip) - j0, len(bus) - i)
    if n > 0: bus[i:i + n] += clip[j0:j0 + n]
def fade(c, a=0.01, b=0.02):
    c = c.copy(); ka, kb = min(int(a * SR), len(c)), min(int(b * SR), len(c))
    if ka: c[:ka] *= np.linspace(0, 1, ka)[:, None]
    if kb: c[-kb:] *= np.linspace(1, 0, kb)[:, None]
    return c
def rms_norm(c, target):
    act = c[np.abs(c).max(1) > 1e-4]
    r = np.sqrt(np.mean(act ** 2)) if len(act) else 1
    return c * (db(target) / max(r, 1e-9))

# ---------------------------------------------------------------- bed
def saw(f, n): return 2 * ((f * np.arange(n) / SR + rng.random()) % 1.0) - 1
def pad(notes, t0, t1, cutoff, attack=0.35, release=0.6):
    n = int((t1 - t0 + release) * SR); out = np.zeros((n, 2))
    for m in notes:
        for cents, pan in ((-8, 0.2), (0, 0.5), (8, 0.8)):
            out += st(saw(m2f(m) * 2 ** (cents / 1200), n), pan)
    out = lp(out, cutoff) / (len(notes) * 3)
    e = np.ones(n); ka = int(attack * SR); hold = int((t1 - t0) * SR)
    e[:ka] = np.linspace(0, 1, ka); e[hold:] = np.linspace(1, 0, n - hold) ** 2
    return out * e[:, None]
def pluck(f, dur=0.35):
    t = np.arange(int(dur * SR)) / SR
    x = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)) * np.exp(-t / 0.09)
    x[:48] *= np.linspace(0, 1, 48); return x
def kick():
    t = np.arange(int(0.3 * SR)) / SR; f = 42 + 80 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12)
def hat():
    n = int(0.05 * SR); return hp(rng.standard_normal(n), 7000) * np.exp(-np.arange(n) / SR / 0.012)
def sub(f=49.0):
    t = np.arange(int(0.45 * SR)) / SR; return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.18) * np.minimum(t / 0.01, 1)
def reverb(x, sec=2.4, wet=0.28):
    n = int(sec * SR); env = np.exp(-np.arange(n) / SR / (sec / 5))
    ir = np.stack([rng.standard_normal(n) * env, rng.standard_normal(n) * env], 1); ir = lp(ir, 5000) / np.sqrt(n) * 6
    w = np.stack([signal.fftconvolve(x[:, k], ir[:, k])[:len(x)] for k in range(2)], 1)
    return x * (1 - wet) + w * wet

def make_bed():
    a, b, c, d, e = S['intro'], S['meadow'], S['orb'], S['fin'], DUR
    bed = np.zeros((N + 3 * SR, 2))
    place(bed, pad([50, 57, 62, 64, 65], a, b, 900) * 0.9, a + 0.15)                    # Dm add9, tense
    for i, tt in enumerate(np.arange(1.0, b - 0.05, 0.125)):                              # hats rising into the cut
        place(bed, st(hat() * (0.12 + 0.5 * (tt - 1) / (b - 1)) * (0.6 if i % 2 else 1), 0.35 + 0.3 * (i % 2)), tt)
    place(bed, pad([46, 53, 57, 60, 62], b, c, 2400, attack=0.05), b)                      # Bbmaj9, bright
    arp = [65, 69, 72, 74, 77, 74, 72, 69]
    for i, tt in enumerate(np.arange(b + 0.02, c - 0.1, 0.125)):
        place(bed, st(pluck(m2f(arp[i % 8])) * 0.35, 0.3 if i % 2 else 0.7), tt)
    for tt in np.arange(b, c - 0.2, 0.5): place(bed, st(kick() * 0.55), tt)
    place(bed, pad([43, 50, 58, 62, 69], c, d, 1100, attack=0.1), c)                        # Gm9, dark
    for tt in np.arange(c, d - 0.1, 0.5): place(bed, st(sub() * 0.7), tt)
    place(bed, pad([41, 48, 57, 64, 67, 72], d, e + 0.5, 3200, attack=0.06, release=1.0), d)  # Fmaj9, wide
    t = np.arange(int((e - d + 0.5) * SR)) / SR
    sh = sum(np.sin(2 * np.pi * m2f(m) * t) for m in (84, 91)) * (0.5 + 0.5 * np.sin(2 * np.pi * 5 * t)) * np.minimum(t / 0.4, 1) * 0.05
    place(bed, st(sh), d)
    bed = reverb(bed)[:N]
    out = np.ones(N); k = int(0.5 * SR); out[-k:] = np.linspace(1, 0, k) ** 1.5
    return rms_norm(bed * out[:, None], -25)

if CFG.get('music'):
    MAN = json.load(open(f'{P}/assets/manifest.json'))
    start = (MAN.get('music') or {}).get('start', CFG.get('musicStart', 0))
    bed = load(resolve(CFG['music']), start, DUR)
    bed = np.vstack([bed, np.zeros((max(0, N - len(bed)), 2))])[:N]
    bed = rms_norm(fade(bed, 0.03, 1.4 if DUR > 20 else 0.6), -21)
    bed_kind = 'your music'
else:
    bed = make_bed(); bed_kind = 'synth bed'
bed *= db(CFG.get('musicLevel', 0))

# ---------------------------------------------------------------- effects
def _n(sec): return rng.standard_normal(int(sec * SR))
def _env(n, a, d): t = np.arange(n) / SR; return np.minimum(t / max(a, 1e-4), 1) * np.exp(-np.maximum(t - a, 0) / d)
def _sweep(f0, f1, sec, decay):
    t = np.arange(int(sec * SR)) / SR; f = f1 + (f0 - f1) * np.exp(-t * 6 / sec)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay)
def _whoosh(sec=0.8, lo=300):
    x = _n(sec); n = len(x); out = np.zeros(n); blocks = 40; e = np.linspace(0, n, blocks + 1).astype(int)
    for i in range(blocks):
        c = lo * (10 ** (np.sin(np.pi * i / blocks) * 1.1)); out[e[i]:e[i + 1]] = bp(x[e[i]:e[i + 1]], c * 0.6, min(c * 1.8, 20000))
    return out * np.sin(np.linspace(0, np.pi, n)) ** 2
def synth(kind, v=0):
    r = np.random.default_rng(100 + v)
    if kind in ('glyph', 'key', 'tick'):
        f = {'glyph': 2600, 'key': 1700, 'tick': 3200}[kind] * (0.85 + 0.3 * r.random()); n = int(0.04 * SR)
        x = hp(r.standard_normal(n), 1500) * _env(n, 0.0005, 0.005) + 0.4 * _sweep(f, f * 0.7, 0.04, 0.008)
        if kind == 'key': x += 0.5 * _sweep(320, 180, 0.04, 0.01)
        return x
    if kind == 'blip': f = 800 + 900 * r.random(); return _sweep(f * 1.4, f, 0.12, 0.04)
    if kind == 'pop': return _sweep(950, 320, 0.09, 0.03)
    if kind in ('whoosh', 'swish'): return _whoosh(0.8 if kind == 'whoosh' else 0.35, 300 if kind == 'whoosh' else 600)
    if kind == 'deepwhoosh': return _whoosh(1.0, 120)
    if kind == 'riser':
        n = int(2.4 * SR); t = np.arange(n) / SR; x = np.zeros(n); blocks = 48; e = np.linspace(0, n, blocks + 1).astype(int); nz = _n(2.4)
        for i in range(blocks): c = 250 * 24 ** (i / blocks); x[e[i]:e[i + 1]] = bp(nz[e[i]:e[i + 1]], c * 0.7, min(c * 1.5, 20000))
        x += 0.3 * np.sin(2 * np.pi * np.cumsum(180 * 5 ** (t / 2.4)) / SR)
        return x * (t / 2.4) ** 2.2
    if kind == 'reverse': x = hp(_n(1.2), 1200); return x * np.linspace(0, 1, len(x)) ** 3
    if kind in ('impact', 'boom'):
        b = _sweep(75 if kind == 'impact' else 60, 30, 2.0, 0.6 if kind == 'impact' else 0.45)
        return b + (0.35 if kind == 'impact' else 0.15) * bp(_n(2.0), 40, 400) * _env(int(2.0 * SR), 0.002, 0.2)
    if kind == 'hit':
        dry = bp(_n(0.08), 200, 6000) * _env(int(0.08 * SR), 0.001, 0.03)
        ir = _n(1.6) * np.exp(-np.arange(int(1.6 * SR)) / SR / 0.45); out = signal.fftconvolve(dry, ir) * 0.05
        out[:len(dry)] += dry; return out
    if kind == 'glitch':
        n = int(0.45 * SR); x = np.sign(np.sin(2 * np.pi * r.uniform(200, 900) * np.arange(n) / SR)) * 0.5
        gate = np.repeat(r.random(n // 480 + 1) > 0.5, 480)[:n]; return x * gate * _env(n, 0.002, 0.25)
    if kind == 'sparkle':
        out = np.zeros(int(0.7 * SR))
        for i in range(9):
            f = r.uniform(3000, 7500); s = _sweep(f, f, 0.25, 0.05) * r.uniform(0.4, 1); j = int(r.uniform(0, 0.4) * SR); out[j:j + len(s)] += s
        return out
    raise ValueError(kind)
SFX = {  # kind: file names tried in sfxDir; several names = variants (picked by the cue's "v")
    'glyph': ['Digital Click - 1.mp3', 'Digital Click - 3.mp3', 'Digital Click - 7.mp3', 'Digital Click - 8.mp3'],
    'key': ['click 0.mp3', 'Digital Click - 8.mp3', 'Digital Click - 7.mp3'],
    'tick': ['Digital Click - 3.mp3', 'Digital Click - 1.mp3'],
    'blip': ['UI Beep 4.wav', 'Bips.wav'],
    'pop': ['bubble-pop-293342.mp3'],
    'whoosh': ['Whoosh 3.wav', 'Cool whoosh.wav'],
    'swish': ['QUICK WHOOSH (7).wav', 'Fast whip.wav', 'Fast whoosh.wav'],
    'deepwhoosh': ['DEEP WHOOSH (4).wav', 'Whoosh Deep Short.wav'],
    'riser': ['QUICK RISER (7).wav', 'Riser 4.wav'],
    'reverse': ['REVERSE (16).wav', 'REVERSE (42).wav'],
    'impact': ['BOOM IMPACT (23).wav', 'Cinematic Boom 3.mp3'],
    'boom': ['Cinematic Boom Soft.wav', 'Cinematic Boom 3.mp3'],
    'hit': ['REVERB HIT (12).wav'],
    'glitch': ['CINEMATIC GLITCH (29).wav', 'CINEMATIC GLITCH (1).wav'],
    'sparkle': ['Glittering Clink 02.wav'],
}
SFX_DIR = os.path.expanduser(CFG.get('sfxDir', '') or '')
_cache, used = {}, {'library': 0, 'synth': 0}
def sfx(kind, v=0):
    names = [n for n in SFX.get(kind, []) if SFX_DIR and os.path.exists(os.path.join(SFX_DIR, n))]
    if names:
        name = names[v % len(names)]
        if name not in _cache: _cache[name] = load(os.path.join(SFX_DIR, name))
        used['library'] += 1; return _cache[name]
    used['synth'] += 1; x = synth(kind, v); return st(x)

fx = np.zeros((N, 2))
for c in TL['cues']:
    clip = sfx(c['k'], c.get('v', 0))
    env = np.convolve(np.abs(clip).max(1), np.ones(480) / 480, 'same')
    pk = int(np.argmax(env)) if c.get('al') == 'peak' else 0
    if c.get('pre') and pk > c['pre'] * SR:                  # keep at most `pre` seconds before the peak
        cut = pk - int(c['pre'] * SR); clip = fade(clip[cut:], 0.05, 0); pk -= cut
    clip = clip[:pk + int((c.get('max') or 4.0) * SR)]
    clip = fade(clip, 0.002, 0.08) * (db(c['db']) / max(np.abs(clip).max(), 1e-6))
    place(fx, clip, c['t'] - pk / SR)

fx *= db(CFG.get('sfxLevel', 0))     # e.g. -4 to sit the effects under a song
mix = bed + fx
k = int(0.45 * SR); mix[-k:] *= (np.linspace(1, 0, k) ** 1.6)[:, None]   # lands with the picture's fade to black
raw = f'{P}/build/mix_raw.wav'
def write(path, x): subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', path], input=x.astype(np.float32).tobytes(), check=True)
write(raw, mix)
m = subprocess.run(['ffmpeg', '-nostdin', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1:LRA=9:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
js = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
af = (f"loudnorm=I=-14:TP=-1:LRA=9:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}"
      f":measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', raw, '-af', af, '-ar', str(SR), f'{P}/build/mix.wav'], check=True)
write(f'{P}/build/stem_bed.wav', bed); write(f'{P}/build/stem_fx.wav', fx)
print(f"mix -> {P}/build/mix.wav ({bed_kind}; {len(TL['cues'])} cues: {used['library']} from sfxDir, {used['synth']} synthesised)")
