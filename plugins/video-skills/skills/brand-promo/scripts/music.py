"""Original synth score for the promo (synthesised from scratch with numpy/scipy, no samples): <project>/build/music.wav

python music.py <project>/promo.json

128 bpm, F minor, bars start at 0.075 s so they land on the edit's cuts (W = number of works):
  bars 0-3 intro, riser into the title drop (bar 4) | bars 5..4+3W light groove under the spotlights
  bar 5+3W break | bars 6+3W..7+3W full drop under the rush, snare roll | bar 8+3W pre | bar 9+3W final hit, chord rings out
"""
import os, subprocess, sys, json
import numpy as np
from scipy import signal

P = os.path.dirname(os.path.abspath(sys.argv[1]))
WORKS = len(json.load(open(f'{P}/assets/manifest.json'))['works'])
SR = 48000
BPM = 128.0
BEAT = 60 / BPM
BAR = 4 * BEAT
T0 = 0.075
BRK, END = 5 + 3 * WORKS, 9 + 3 * WORKS          # break bar and final-hit bar
DUR = T0 + END * BAR + 7.4
N = int(SR * DUR)
rng = np.random.default_rng(7)

def at(bar, beat=0.0): return T0 + bar * BAR + beat * BEAT
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def bus(): return np.zeros((N, 2), np.float32)

def add(b, x, t, gain=1.0, pan=0.0):
    i = int(round(t * SR))
    if i >= N: return
    x = x[:N - i]
    if x.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        b[i:i + len(x), 0] += x * gain * l * 1.414
        b[i:i + len(x), 1] += x * gain * r * 1.414
    else:
        b[i:i + len(x)] += x * gain

def lp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, min(fc, SR * 0.45), 'low', fs=SR, output='sos'), x, axis=0)
def hp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, 'high', fs=SR, output='sos'), x, axis=0)
def bp(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, hi], 'band', fs=SR, output='sos'), x, axis=0)

# ------------------------------------------------------------------ oscillators (band-limited)
def _blep(p, dt):
    out = np.zeros_like(p)
    m = p < dt; x = p[m] / dt[m]; out[m] = x + x - x * x - 1
    m = p > 1 - dt; x = (p[m] - 1) / dt[m]; out[m] = x * x + x + x + 1
    return out
def saw(freq, n, phase0=0.0):
    f = np.broadcast_to(np.asarray(freq, np.float64), (n,))
    dt = f / SR
    p = (phase0 + np.cumsum(dt)) % 1.0
    return 2 * p - 1 - _blep(p, dt)
def square(freq, n, phase0=0.0, pw=0.5):
    return 0.5 * (saw(freq, n, phase0) - saw(freq, n, phase0 + pw))
def env_adsr(n, a, d, s, r_start, r):
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    rel = t > r_start
    e[rel] *= np.exp(-(t[rel] - r_start) / max(r, 1e-4))
    return e

# ------------------------------------------------------------------ drums
def kick(hard=1.0):
    n = int(0.5 * SR); t = np.arange(n) / SR
    f = 46 + 120 * np.exp(-t * 32)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    click = lp(rng.standard_normal(n) * np.exp(-t * 400), 5000)
    return np.tanh((body * 1.1 + click * 0.25 * hard) * 1.4)
def snare_gated():
    n = int(0.6 * SR); t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 186 * t) * np.exp(-t * 22) * 0.6
    noise = bp(rng.standard_normal(n), 900, 7500) * np.exp(-t * 16)
    dry = tone + noise
    ir_n = int(0.9 * SR); ti = np.arange(ir_n) / SR
    ir = rng.standard_normal((ir_n, 2)) * np.exp(-ti / 0.35)[:, None] * 0.06
    wet = np.stack([signal.fftconvolve(dry, ir[:, c])[:n] for c in range(2)], 1)
    gate = np.clip((0.30 - t) / 0.05, 0, 1)[:, None]           # the 80s gated tail
    out = wet * gate * 1.4 + dry[:, None] * 0.8
    return out / np.abs(out).max()
def clap():
    n = int(0.3 * SR); t = np.arange(n) / SR
    e = sum(np.exp(-np.clip(t - d, 0, None) * 140) * (t >= d) for d in (0, 0.011, 0.022)) + 0.5 * np.exp(-t * 18) * (t > 0.03)
    return bp(rng.standard_normal(n), 900, 4000) * e
def hat(open_=False):
    n = int((0.32 if open_ else 0.06) * SR); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7500, 4) * np.exp(-t * (9 if open_ else 70))
def crash(length=2.6):
    n = int(length * SR); t = np.arange(n) / SR
    metal = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f in (3120, 4710, 5930, 7230, 8440)) * 0.08
    x = (hp(rng.standard_normal(n), 4200, 2) + metal) * np.exp(-t * 1.6)
    return np.stack([x, np.roll(x, 140)], 1)
def riser(length, lo=300, hi=9000):
    n = int(length * SR); blocks = 96; out = np.zeros(n); x = rng.standard_normal(n)
    edges = np.linspace(0, n, blocks + 1).astype(int); zi = None
    for k in range(blocks):
        c = lo * (hi / lo) ** (k / blocks)
        sos = signal.butter(2, [c * 0.7, min(c * 1.4, SR * 0.45)], 'band', fs=SR, output='sos')
        if zi is None: zi = signal.sosfilt_zi(sos) * 0
        out[edges[k]:edges[k + 1]], zi = signal.sosfilt(sos, x[edges[k]:edges[k + 1]], zi=zi)
    return out * np.linspace(0, 1, n) ** 2.2

# ------------------------------------------------------------------ harmony (one chord per bar, 4-bar loop)
CHORDS = [  # name, bass root (midi), chord tones (midi)
    ('Fm', 41, [53, 56, 60, 65]), ('Db', 37, [49, 53, 56, 61]), ('Eb', 39, [51, 55, 58, 63]), ('Cm', 36, [48, 51, 55, 60])]
def chord_of(bar): return CHORDS[bar % 4]

# hook: 4-bar phrase (beat offset, length in beats, midi)
HOOK = [(0, .5, 72), (.5, .5, 75), (1, 1, 77), (2.5, .5, 75), (3, 1, 72),
        (4, .5, 68), (4.5, .5, 72), (5, 1.5, 77), (6.5, .5, 75), (7, 1, 73),
        (8, .5, 70), (8.5, .5, 75), (9, 1, 79), (10.5, .5, 77), (11, 1, 75),
        (12, .5, 72), (12.5, .5, 75), (13, 1, 79), (14, 1, 77), (15, 1, 72)]

def section(bar):
    if bar < 2: return 'intro'
    if bar < 3: return 'intro2'
    if bar == 3: return 'riser'
    if bar == 4: return 'drop'
    if bar < BRK: return 'build'
    if bar == BRK: return 'break'
    if bar < BRK + 3: return 'drop'
    if bar == BRK + 3: return 'pre'
    return 'end'

drums, bass_b, pad_b, arp_b, lead_b, fx_b = bus(), bus(), bus(), bus(), bus(), bus()
K, SN, CL = kick(), snare_gated(), clap()
kicks = []

for bar in range(END):
    sec = section(bar)
    name, root, tones = chord_of(bar)
    # ---------------- drums
    if sec == 'drop':
        for b in range(4):
            add(drums, K, at(bar, b), 0.95); kicks.append(at(bar, b))
        for b in (1, 3):
            add(drums, SN, at(bar, b), 0.55); add(drums, CL, at(bar, b), 0.25, -0.1)
        for s in range(16):
            add(drums, hat(open_=(s % 4 == 2)), at(bar, s / 4), 0.11 if s % 4 == 2 else (0.07 if s % 2 else 0.05), 0.35)
    elif sec in ('build', 'build2'):
        for b in (0, 2):
            add(drums, K, at(bar, b), 0.85); kicks.append(at(bar, b))
        add(drums, SN, at(bar, 2), 0.45)
        for s in range(8 if sec == 'build' else 16):
            add(drums, hat(), at(bar, s / (2 if sec == 'build' else 4)), 0.06, 0.35)
    elif sec == 'intro2':
        for s in range(8): add(drums, hat(), at(bar, s / 2 + 0.5 * 0), 0.035 + 0.01 * (s % 2), 0.35)
    if sec == 'riser' or bar == BRK + 2:
        n_roll = 16
        for s in range(n_roll):
            beat = (4 - n_roll / 4) + s / 4
            add(drums, SN, at(bar, beat), 0.14 + 0.45 * s / n_roll)
    # ---------------- bass
    if sec == 'drop':
        steps, nl = 16, 0.11
    elif sec in ('build', 'build2', 'intro2', 'riser'):
        steps, nl = 8, 0.2
    else:
        steps = 0
    for s in range(steps):
        if sec == 'riser' and s >= 6: break
        m = root + (12 if (steps == 16 and s % 2) else 0)
        n = int(nl * SR); f = mtof(m)
        x = 0.6 * saw(f, n) + 0.5 * square(f * 0.5, n) * 0.6
        e = env_adsr(n, 0.004, 0.08, 0.55, nl * 0.75, 0.02)
        bright = lp(x, 1800) * np.exp(-np.arange(n) / SR / 0.05) + lp(x, 420)
        add(bass_b, bright * e, at(bar, s * 4 / steps), 0.42)
    # ---------------- pad (supersaw chord)
    if sec != 'end':
        n = int(BAR * SR) + int(0.25 * SR)
        x = np.zeros(n)
        for m in tones:
            for d in (-0.13, -0.06, 0, 0.07, 0.12):
                x += saw(mtof(m + d), n, rng.uniform())
        e = env_adsr(n, 0.25 if bar < 2 else 0.04, 0.6, 0.8, BAR - 0.05, 0.2)
        cut = {'intro': 700 + 500 * bar, 'intro2': 1500, 'build': 1700, 'riser': 2200, 'break': 900, 'build2': 1600, 'pre': 1200 + 300 * 0}.get(sec, 2600)
        y = hp(lp(x * e, cut, 2), 160) / 12
        st = np.stack([y, np.roll(y, int(0.013 * SR))], 1)
        add(pad_b, st, at(bar), 0.55 if sec == 'drop' else 0.65)
    # ---------------- arp (16ths over the chord)
    if sec not in ('end', 'break', 'pre'):
        order = [0, 1, 2, 3, 2, 1, 2, 3]
        for s in range(16):
            m = tones[order[s % 8]] + 12
            n = int(0.16 * SR); f = mtof(m)
            x = square(f, n, pw=0.3) * np.exp(-np.arange(n) / SR / 0.06)
            cut = {'intro': 600 + 900 * (bar + s / 16), 'intro2': 2600 + 700 * (bar - 2 + s / 16), 'build': 4200}.get(sec, 5200)
            add(arp_b, lp(x, cut), at(bar, s / 4), 0.16, 0.25 if s % 2 else -0.25)
    # ---------------- lead hook (left out: the narration runs through the drop)
    if False:
        up = 12 if sec == 'drop2' and bar >= 20 else 0
        phrase_bar = (bar - 8) % 4
        for off, ln, m in HOOK:
            if int(off // 4) != phrase_bar: continue
            n = int((ln * BEAT + 0.25) * SR); f = mtof(m + up)
            t = np.arange(n) / SR
            vib = f * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.15) / 0.2, 0, 1))
            x = 0.55 * saw(vib, n) + 0.35 * saw(vib * 1.004, n) + 0.3 * square(vib * 0.5, n)
            e = env_adsr(n, 0.008, 0.2, 0.7, ln * BEAT, 0.12)
            add(lead_b, lp(x * e, 3800), at(bar, off % 4), 0.2)

# ---------------- fx: crashes, risers, hits
for bar in (4, BRK + 1):
    add(fx_b, crash(), at(bar), 0.32)
add(fx_b, crash()[::-1].copy(), at(4) - 2.6, 0.22)            # reverse cymbal into the drop
add(fx_b, crash()[::-1].copy(), at(END) - 2.6, 0.3)           # and into the final hit
add(fx_b, riser(BAR), at(3), 0.34, 0)
add(fx_b, riser(2 * BAR, 400, 8000), at(BRK + 2), 0.22)
# drop hit at bar 7 and the final hit at bar 20: kick + snare + sub boom + chord stab
def boom(length=2.5):
    n = int(length * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(38 + 40 * np.exp(-t * 8)) / SR) * np.exp(-t * 1.4)
for bar, g in ((4, 0.7), (END, 1.0)):
    add(drums, K, at(bar), 1.0); add(drums, SN, at(bar), 0.6 * g); add(fx_b, boom(), at(bar), 0.55 * g)
add(fx_b, crash(4.0), at(END), 0.45)
# final chord: Fm(add9) pad + lead octave, long release
n = int(6.0 * SR); x = np.zeros(n)
for m in (41, 53, 56, 60, 67, 72):
    for d in (-0.1, 0, 0.09): x += saw(mtof(m + d), n, rng.uniform())
x = lp(x * env_adsr(n, 0.005, 1.0, 0.45, 2.6, 1.3), 2400) / 9
add(pad_b, np.stack([x, np.roll(x, int(0.011 * SR))], 1), at(END), 0.8)

# ------------------------------------------------------------------ sidechain pump, delay, reverb, master
pump = np.ones(N)
tt = np.arange(N) / SR
for k in kicks:
    i = int(k * SR); j = min(N, i + int(0.3 * SR))
    pump[i:j] = np.minimum(pump[i:j], 1 - 0.55 * np.exp(-(tt[i:j] - k) / 0.09))
for b in (bass_b, pad_b, arp_b): b *= pump[:, None]

def delay(x, t_d, fb=0.35, mix=0.3):
    d = int(t_d * SR); y = x.copy()
    for k in range(1, 6):
        g = mix * fb ** (k - 1)
        sh = np.zeros_like(x); sh[d * k:] = x[:-d * k] if d * k < len(x) else 0
        if k % 2: sh = sh[:, ::-1]                              # ping-pong
        y += sh * g
    return y
arp_b = delay(arp_b, BEAT * 0.75, 0.35, 0.28)
lead_b = delay(lead_b, BEAT * 0.75, 0.3, 0.22)

ir_n = int(2.2 * SR); ti = np.arange(ir_n) / SR
ir = rng.standard_normal((ir_n, 2)) * np.exp(-ti / 0.55)[:, None]
ir = hp(lp(ir, 6000), 220); ir /= np.sqrt((ir ** 2).sum(0))
send = pad_b * 0.25 + lead_b * 0.35 + arp_b * 0.3 + drums * 0.06
wet = np.stack([signal.fftconvolve(send[:, c], ir[:, c])[:N] for c in range(2)], 1) * 0.5

mix = drums * 1.0 + bass_b * 1.0 + pad_b * 0.9 + arp_b * 0.9 + lead_b * 1.0 + fx_b * 1.0 + wet
mix = hp(mix, 28)
mix = np.tanh(mix * 1.15) / np.tanh(1.15)
out = f'{P}/build/music_raw.wav'
os.makedirs(f'{P}/build', exist_ok=True)
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', out],
               input=(mix / max(np.abs(mix).max(), 1e-6) * 0.9).astype(np.float32).tobytes(), check=True)
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', out, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', str(SR),
                f'{P}/build/music.wav'], check=True)
print('music ->', f'{P}/build/music.wav', f'({DUR:.1f} s)')
