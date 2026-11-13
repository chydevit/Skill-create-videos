"""Mix the promo: the score, the narrator, each work's OWN sound in its spotlight, and effects -> <project>/build/mix.wav

python audio.py <project>/promo.json

The score dips about 16 dB under each work's sound and about 5 dB under the narrator; the mix is normalised to
-14 LUFS, -1 dBTP. Effects come from promo.json "sfxDir" (a folder of sound files, see SFX below) when it has them,
otherwise they are synthesised here, so the skill works with no sound library at all.
"""
import os, subprocess, json, sys
import numpy as np
from scipy import signal

CFG_PATH = os.path.abspath(sys.argv[1])
P = os.path.dirname(CFG_PATH)
CFG = json.load(open(CFG_PATH))
MAN = json.load(open(f'{P}/assets/manifest.json'))
TM = json.load(open(f'{P}/build/tm.json'))
SR = 48000
NW = TM['N']; DUR = TM['DUR']; N = int(SR * DUR)
BAR, T0 = 4 * 60 / 128, 0.075
B = lambda n: T0 + n * BAR
SPOT = [B(5 + 3 * k) for k in range(NW)]
BREAK, HIT = TM['BREAK'], TM['HIT']; L0 = HIT - 0.5
BITES, BLEN, NEXT, WVA = TM['bite'], TM['blen'], TM['next'], TM['wva']
VOX = f'{P}/build/vox'
rng = np.random.default_rng(3)

def load(path, ss=0.0, to=None):
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-ss', str(ss), '-i', path]
    if to is not None: cmd += ['-t', str(to - ss)]
    raw = subprocess.run(cmd + ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
def db(x): return 10 ** (x / 20)
def place(bus, clip, t, align='start'):
    if align == 'peak':
        env = np.convolve(np.abs(clip).max(1), np.ones(480) / 480, 'same'); t -= np.argmax(env) / SR
    i = int(round(t * SR)); j0 = max(0, -i); i = max(0, i)
    n = min(len(clip) - j0, N - i)
    if n > 0: bus[i:i + n] += clip[j0:j0 + n]
def norm_rms(c, target_db):
    act = c[np.abs(c).max(1) > 0.02]
    return c * (db(target_db) / (np.sqrt(np.mean(act ** 2)) if len(act) else 0.1))
def fades(c, a=0.012, b=0.012):
    ka, kb = min(int(a * SR), len(c)), min(int(b * SR), len(c))
    if ka: c[:ka] *= np.linspace(0, 1, ka)[:, None]
    if kb: c[-kb:] *= np.linspace(1, 0, kb)[:, None]
    return c
def ff_filter(x, af):
    p = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', af,
                        '-f', 'f32le', '-'], input=x.astype(np.float32).tobytes(), capture_output=True, check=True).stdout
    y = np.frombuffer(p, np.float32).reshape(-1, 2).copy()
    out = np.zeros_like(x); out[:min(len(y), len(x))] = y[:len(x)]; return out

# ---------------------------------------------------------------- narrator
VO = [('r01', 0.5), ('n02', 3.7), ('r04', 7.7)] + [(f'n1{k + 1}', SPOT[k] + 0.15) for k in range(NW)] + \
     [('r08', NEXT[0]), ('r09', TM.get('r09', WVA[0])), ('r10', L0 + 2.9)]
vo = np.zeros((N, 2), np.float32)
for f, t in VO:
    if os.path.exists(f'{VOX}/{f}.wav'):
        place(vo, norm_rms(fades(load(f'{VOX}/{f}.wav', TM.get('trim', {}).get(f, 0))), -19), t)
if np.abs(vo).max() > 0:
    vo = ff_filter(vo, 'highpass=f=90,acompressor=threshold=0.1:ratio=3:attack=5:release=120:makeup=1.4,equalizer=f=3500:t=q:w=1:g=2')

# ---------------------------------------------------------------- each work's own sound, on its "Sound on" chip
src = np.zeros((N, 2), np.float32)
bite_on = np.zeros(N, np.float32)
for k, w in enumerate(MAN['works']):
    f = f'{P}/assets/bites/{w["clip"]}.wav'
    if not w.get('sound') or not os.path.exists(f): continue
    c = fades(load(f, 0, BLEN[k]), 0.12, 0.35)
    place(src, norm_rms(c, -18.5), BITES[k])
    bite_on[int((BITES[k] - 0.1) * SR):int((BITES[k] + BLEN[k] + 0.1) * SR)] = 1

# ---------------------------------------------------------------- music: ducked under the voice and, more, under the clips
mus = load(f'{P}/build/music.wav', 0, DUR + 0.5)[:N]
mus = np.vstack([mus, np.zeros((N - len(mus), 2), np.float32)]) if len(mus) < N else mus
act = np.convolve((np.abs(vo).max(1) > 0.015).astype(np.float32), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
duck = 1 - np.maximum(0.45 * np.clip(act * 3, 0, 1), 0.84 * bite_on)
k = int(0.15 * SR); duck = np.convolve(duck, np.ones(k) / k, 'same')
fade = np.ones(N); a = int((DUR - 0.9) * SR); fade[a:] = np.linspace(1, 0, N - a) ** 1.5
mus *= (db(-8.0) * duck * fade)[:, None]

# ---------------------------------------------------------------- effects: a library file if there is one, else synthesised
def _n(sec): return rng.standard_normal(int(sec * SR))
def _env(n, a, d): t = np.arange(n) / SR; return np.minimum(t / max(a, 1e-4), 1) * np.exp(-np.maximum(t - a, 0) / d)
def _bp(x, lo, hi): return signal.sosfilt(signal.butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
def _hp(x, f): return signal.sosfilt(signal.butter(2, f, 'high', fs=SR, output='sos'), x)
def _sweep(f0, f1, sec, decay):
    t = np.arange(int(sec * SR)) / SR; f = f1 + (f0 - f1) * np.exp(-t * 6 / sec)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay)
def _whoosh(sec=0.8):
    x = _n(sec); n = len(x); out = np.zeros(n); blocks = 40; e = np.linspace(0, n, blocks + 1).astype(int)
    for i in range(blocks):
        c = 300 * (10 ** (np.sin(np.pi * i / blocks) * 1.1)); out[e[i]:e[i + 1]] = _bp(x[e[i]:e[i + 1]], c * 0.6, min(c * 1.8, 20000))
    return out * np.sin(np.linspace(0, np.pi, n)) ** 2
def synth(kind):
    if kind == 'click': return _hp(_n(0.03), 2000) * _env(int(0.03 * SR), 0.0005, 0.006) + 0.3 * _sweep(2400, 1800, 0.03, 0.01)
    if kind == 'typing':
        out = np.zeros(int(0.6 * SR))
        for i in range(6): j = int((0.02 + i * 0.09 + rng.uniform(0, 0.02)) * SR); c = synth('click') * rng.uniform(0.5, 1); out[j:j + len(c)] += c[:len(out) - j]
        return out
    if kind == 'pop': return _sweep(950, 320, 0.09, 0.03)
    if kind == 'whoosh': return _whoosh(0.8)
    if kind == 'reverse': x = _hp(_n(1.4), 1500); return x * np.linspace(0, 1, len(x)) ** 3
    if kind == 'drop': return _sweep(130, 34, 1.4, 0.6)
    if kind == 'hitwhoosh': w = _whoosh(0.6); b = _sweep(90, 40, 0.6, 0.18); return np.concatenate([w, np.zeros(0)])[:len(w)] + np.pad(b, (len(w) // 2, 0))[:len(w)]
    if kind == 'glitch':
        n = int(0.45 * SR); x = np.sign(np.sin(2 * np.pi * rng.uniform(200, 900) * np.arange(n) / SR)) * 0.5
        gate = np.repeat(rng.random(n // 480 + 1) > 0.5, 480)[:n]; return x * gate * _env(n, 0.002, 0.25)
    if kind == 'boom': return _sweep(70, 30, 2.2, 0.7) + 0.3 * _bp(_n(2.2), 40, 300) * _env(int(2.2 * SR), 0.003, 0.25)
    if kind == 'metal':
        t = np.arange(int(1.3 * SR)) / SR; return sum(np.sin(2 * np.pi * f * t) for f in (517, 1342, 2213, 3171)) * np.exp(-t * 3.2) / 3
    if kind == 'hit':
        dry = _bp(_n(0.08), 200, 6000) * _env(int(0.08 * SR), 0.001, 0.03)
        ir = _n(1.8) * np.exp(-np.arange(int(1.8 * SR)) / SR / 0.5); L = int(2 * SR)
        fit = lambda x: np.pad(x, (0, max(0, L - len(x))))[:L]
        return fit(signal.fftconvolve(dry, ir)) * 0.05 + fit(dry)
    raise ValueError(kind)
SFX = {  # kind: file names tried in sfxDir, in order
    'click': ['Digital Click - 1.mp3'], 'typing': ['typing_keyboard.mp3', 'Keyboard - 4.mp3'], 'pop': ['ui-pop-up-15-197897.mp3', 'bubble-pop-293342.mp3'],
    'pop2': ['ui-pop-up-14-197900.mp3', 'bubble-pop-293342.mp3'], 'whoosh': ['Whoosh 3.wav'], 'whoosh2': ['Whoosh 9.wav'], 'whoosh3': ['Whoosh Deep Light.wav'],
    'airy': ['Whoosh Airy Tonal Tail.wav'], 'main': ['Whoosh Main.wav'], 'short': ['Whoosh Deep Short.wav'], 'reverse': ['REVERSE (16).wav'],
    'drop': ['BASS DROP (10).wav'], 'hitwhoosh': ['HIT WHOOSH (1).wav'], 'glitch': ['CINEMATIC GLITCH (1).wav'], 'boom': ['Cinematic Boom 3.mp3'],
    'boomsoft': ['Cinematic Boom Soft.wav'], 'metal': ['METAL HIT (1).wav'], 'hit': ['REVERB HIT (12).wav'],
}
SYN = {'pop2': 'pop', 'whoosh2': 'whoosh', 'whoosh3': 'whoosh', 'airy': 'whoosh', 'main': 'whoosh', 'short': 'whoosh', 'boomsoft': 'boom'}
SFX_DIR = os.path.expanduser(CFG.get('sfxDir', ''))
def sfx(kind):
    for name in SFX.get(kind, []):
        f = os.path.join(SFX_DIR, name)
        if SFX_DIR and os.path.exists(f): return load(f)
    x = synth(SYN.get(kind, kind)); return np.stack([x, x], 1).astype(np.float32)
CUES = [  # time, kind, peak dBFS, align, max length (s)
    (0.12, 'click', -20, 'start', None), (0.5, 'typing', -25, 'start', 0.55), (1.25, 'airy', -22, 'peak', None),
    (3.25, 'whoosh', -17, 'peak', None), *[(3.3 + i * 0.1, 'pop2', -27, 'start', None) for i in range(5)],
    (7.35, 'reverse', -19, 'peak', None), (B(4), 'drop', -13, 'start', None), (B(4), 'hitwhoosh', -15, 'peak', None),
    (7.9, 'glitch', -19, 'start', 0.6),
    *[(SPOT[k] - 0.05, 'whoosh2' if k % 2 == 0 else 'whoosh3', -18, 'peak', None) for k in range(NW)],
    *[(BITES[k], 'pop', -26, 'start', None) for k in range(NW) if MAN['works'][k].get('sound')],
    (NEXT[0], 'boom', -13, 'peak', None), (NEXT[1], 'metal', -17, 'peak', None),
    (BREAK + 1.825, 'main', -16, 'peak', None), *[(t, 'hitwhoosh', -21, 'peak', None) for t in WVA],
    (HIT - 0.625, 'reverse', -20, 'peak', None), (L0 + 2.6, 'short', -19, 'peak', None),
    (HIT, 'boomsoft', -15, 'peak', None), (HIT, 'hit', -17, 'peak', None),
    *[(L0 + 3.6 + i * 0.08, 'pop', -26, 'start', None) for i in range(len(CFG.get('text', {}).get('chips', [])))],
]
fx = np.zeros((N, 2), np.float32)
for t, kind, peak, align, maxlen in CUES:
    c = sfx(kind)[:int((maxlen or 6) * SR)]
    c = c * (db(peak) / max(np.abs(c).max(), 1e-6))
    tail = int(min(len(c), SR * 0.08)); c[-tail:] *= np.linspace(1, 0, tail)[:, None]
    place(fx, c, t, align)
if os.path.exists(f'{P}/assets/logo-sfx.wav'):           # the logo animation's own sound, from its start
    c = load(f'{P}/assets/logo-sfx.wav'); place(fx, c * (db(-9) / max(np.abs(c).max(), 1e-6)), L0)

mix = mus + vo + src + fx
out = f'{P}/build/mix_raw.wav'
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', out], input=mix.astype(np.float32).tobytes(), check=True)
m = subprocess.run(['ffmpeg', '-nostdin', '-i', out, '-af', 'loudnorm=I=-14:TP=-1:LRA=9:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
js = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
af = (f"loudnorm=I=-14:TP=-1:LRA=9:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}"
      f":measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', out, '-af', af, '-ar', str(SR), f'{P}/build/mix.wav'], check=True)
for name, bus in (('voice', vo), ('source', src), ('music', mus), ('fx', fx)):
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', f'{P}/build/stem_{name}.wav'],
                   input=bus.astype(np.float32).tobytes(), check=True)
print('mix ->', f'{P}/build/mix.wav', '(' + ('library effects' if SFX_DIR and os.path.isdir(SFX_DIR) else 'synthesised effects') + ')')
