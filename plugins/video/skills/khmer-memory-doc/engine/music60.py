"""Original 1960s-style instrumental score, synthesised (no recordings, nothing copied).
Colours of the era's Phnom Penh pop and newsreels: surf/twang guitar, combo organ, brass, strings, vibraphone,
bass guitar and a drum kit playing twist, cha-cha, bolero and march grooves; plus sparse, tense textures
(drone, ticking, low piano) for the late chapters.  Each cue is generated from a mood recipe and a seed."""
import numpy as np
from scipy import signal

import sound as S

SR = S.SR


def _t(d):
    return np.arange(int(max(d, 0.01) * SR)) / SR


def _midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def _place(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= len(buf) or i < 0 or len(x) == 0:
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[:j - i] * g


def _env(n, a=0.005, d=0.3, s=0.0, r=0.05, sus=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    dec = s + (1 - s) * np.exp(-(t - a).clip(0) / max(d, 1e-4))
    e = np.where(t < a, e, dec)
    k = min(n, int(r * SR))
    if k > 1:
        e[-k:] *= np.linspace(1, 0, k)
    return e


# ------------------------------------------------------------------ instruments
def kick(v=1.0):
    t = _t(0.35)
    f = 50 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * v


def snare(v=1.0, seed=0):
    t = _t(0.25)
    n = S.bp(np.random.default_rng(seed).standard_normal(len(t)), 1500, 6000) * np.exp(-t * 18)
    return (n * 0.8 + 0.4 * np.sin(2 * np.pi * 185 * t) * np.exp(-t * 25)) * v


def rim(v=1.0):
    t = _t(0.06)
    return np.sin(2 * np.pi * 1700 * t) * np.exp(-t * 90) * v


def hat(v=1.0, open_=False, seed=0):
    d = 0.25 if open_ else 0.05
    t = _t(d)
    return S.hp(np.random.default_rng(seed).standard_normal(len(t)), 7000) * np.exp(-t * (12 if open_ else 70)) * v * 0.5


def shaker(v=1.0, seed=0):
    t = _t(0.09)
    return S.bp(np.random.default_rng(seed).standard_normal(len(t)), 4000, 9000) * np.sin(np.pi * t / 0.09) * v * 0.4


def bass(f, d, v=1.0):
    t = _t(d)
    y = signal.sawtooth(2 * np.pi * f * t) * 0.6 + np.sin(2 * np.pi * f * t)
    y = S.lp(y, 700)
    return y * _env(len(t), 0.004, 0.35, 0.35, 0.04) * v * 0.6


def twang(f, d, v=1.0, seed=0, trem=True):
    """Bright plucked electric guitar with tremolo (Karplus-Strong)."""
    n = int(d * SR)
    p = max(2, int(SR / f))
    buf = np.random.default_rng(seed).uniform(-1, 1, p)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.998 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    out = S.hp(out, 180)
    if trem:
        out *= 1 - 0.35 * (0.5 + 0.5 * np.sin(2 * np.pi * 6.5 * np.arange(n) / SR))
    out[-min(n, 400):] *= np.linspace(1, 0, min(n, 400))
    return out * v * 0.55


def organ(freqs, d, v=1.0, perc=True):
    t = _t(d)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 6.2 * t)
    y = 0
    for f in freqs:
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        y = y + np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph) + 0.18 * np.sin(4 * ph)
    y = y / len(freqs)
    e = _env(len(t), 0.008, 0.6, 0.75, 0.06)
    if perc:
        y = y + 0.4 * np.sin(2 * np.pi * freqs[0] * 3 * t) * np.exp(-t * 14)
    return y * e * v * 0.35


def brass(freqs, d, v=1.0):
    t = _t(d)
    y = 0
    for f in freqs:
        for det in (0.997, 1.003):
            y = y + signal.sawtooth(2 * np.pi * f * det * t)
    y = y / (2 * len(freqs))
    cutoff_env = 600 + 2600 * np.exp(-t * 6)
    # time-varying lowpass approximated by blending two filtered copies
    lo, hi = S.lp(y, 700), S.lp(y, 3200)
    k = (cutoff_env - 600) / 2600
    y = lo * (1 - k) + hi * k
    return y * _env(len(t), 0.03, 0.4, 0.7, 0.12) * v * 0.55


def strings(freqs, d, v=1.0):
    t = _t(d)
    y = 0
    for f in freqs:
        for det in (0.996, 1.0, 1.004):
            vib = 1 + 0.003 * np.sin(2 * np.pi * (5 + det) * t)
            y = y + signal.sawtooth(2 * np.pi * np.cumsum(f * det * vib) / SR)
    y = S.lp(y / (3 * len(freqs)), 2200)
    e = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.8).clip(0, 1)
    return y * e * v * 0.4


def vibes(f, d, v=1.0):
    t = _t(d)
    y = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 8)
    y *= np.exp(-t * 1.6) * (1 - 0.3 * (0.5 + 0.5 * np.sin(2 * np.pi * 5.5 * t)))
    y[:60] *= np.linspace(0, 1, 60)
    return y * v * 0.5


def piano(f, d, v=1.0):
    t = _t(d)
    y = sum(np.sin(2 * np.pi * f * k * t) * np.exp(-t * (1.2 + k * 0.9)) / k for k in (1, 2, 3, 4, 5))
    y[:40] *= np.linspace(0, 1, 40)
    return y * v * 0.5


def drone(f, d, v=1.0):
    t = _t(d)
    y = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.5 * t + 0.3 * np.sin(2 * np.pi * 0.1 * t))
    y += 0.3 * S.lp(np.random.default_rng(3).standard_normal(len(t)), 300)
    e = np.minimum(1, t / 3) * np.minimum(1, (d - t) / 3).clip(0, 1)
    return y * e * v * 0.3


def reverb(y, secs=1.6, wet=0.22, seed=1):
    n = int(secs * SR)
    ir = np.random.default_rng(seed).standard_normal(n) * np.exp(-np.arange(n) / SR * (6.9 / secs))
    ir = S.lp(ir, 5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    w = signal.fftconvolve(y, ir)[:len(y)]
    return y * (1 - wet) + w * wet * 1.4


# ------------------------------------------------------------------ moods
MAJ = [0, 2, 4, 5, 7, 9, 11]
MIN = [0, 2, 3, 5, 7, 8, 10]
PENTA = [0, 2, 4, 7, 9]

MOODS = {
    #  groove, bpm, root (midi), progression (scale degrees of chord roots), lead, colours
    "sixties_open": dict(groove="bolero", bpm=96, root=57, scale=MAJ, prog=[0, 5, 3, 4], lead="twang", pad="strings",
                         keys="organ"),
    "afterwar": dict(groove="march_soft", bpm=84, root=55, scale=MAJ, prog=[0, 3, 4, 0], lead="brass", pad="strings"),
    "abdication": dict(groove="bolero", bpm=80, root=53, scale=MAJ, prog=[0, 3, 5, 4], lead="vibes", pad="strings"),
    "election": dict(groove="march", bpm=112, root=58, scale=MAJ, prog=[0, 4, 3, 4], lead="brass", pad=None,
                     keys="organ", tense=0.2),
    "neutral": dict(groove="chacha", bpm=116, root=55, scale=MAJ, prog=[0, 5, 1, 4], lead="vibes", pad=None,
                    keys="organ"),
    "build": dict(groove="orch", bpm=100, root=57, scale=MAJ, prog=[0, 3, 4, 5, 3, 4, 0, 0], lead="brass",
                  pad="strings"),
    "golden": dict(groove="twist", bpm=144, root=60, scale=PENTA, prog=[0, 0, 3, 4], lead="twang", pad=None,
                   keys="organ"),
    "visitors": dict(groove="chacha", bpm=108, root=58, scale=MAJ, prog=[0, 3, 1, 4], lead="brass", pad="strings",
                     keys="organ"),
    "strain": dict(groove="slow", bpm=88, root=52, scale=MIN, prog=[0, 5, 3, 4], lead="piano", pad="strings",
                   tense=0.5),
    "tension": dict(groove="tick", bpm=72, root=45, scale=MIN, prog=[0, 0, 5, 4], lead="piano", pad="drone",
                    tense=1.0),
    "end": dict(groove="none", bpm=60, root=43, scale=MIN, prog=[0, 5, 3, 0], lead="piano", pad="drone", tense=1.0),
    "legacy": dict(groove="none", bpm=66, root=57, scale=MAJ, prog=[0, 5, 3, 4], lead="vibes", pad="strings"),
    "credits60": dict(groove="bolero", bpm=92, root=57, scale=MAJ, prog=[0, 5, 3, 4], lead="twang", pad="strings",
                      keys="organ"),
}


def _chord(m, deg, octv=-1):
    sc = m["scale"]
    if len(sc) == 5:   # pentatonic: build triads on a major scale with the same root
        sc = MAJ
    out = []
    for k in (0, 2, 4):
        d = deg + k
        o, j = divmod(d, len(sc))
        out.append(_midi(m["root"] + 12 * (o + octv) + sc[j]))
    return out


def _note(m, deg, octv=0):
    sc = m["scale"]
    o, j = divmod(deg, len(sc))
    return _midi(m["root"] + 12 * (o + octv) + sc[j])


def score(mood, d, seed=0):
    m = MOODS[mood]
    r = np.random.default_rng(seed + sum(map(ord, mood)) * 7)
    n = int(d * SR) + SR * 4
    y = np.zeros(n)
    beat = 60.0 / m["bpm"]
    bar = beat * 4
    sl = len(m["scale"])
    # a 2-bar motif repeated with variation (phrase A A B A)
    motifA = [int(x) for x in r.integers(0, sl + 3, 8)]
    motifB = [int(x) for x in r.integers(1, sl + 4, 8)]
    rhythm = [1, 0, 1, 1, 0, 1, 1, 0] if m["groove"] in ("twist", "chacha", "march") else [1, 0, 0, 1, 0, 0, 1, 0]
    nbars = int(d / bar) + 2
    g = m["groove"]
    tense = m.get("tense", 0.0)
    for b in range(nbars):
        t0 = 0.5 + b * bar
        if t0 > d:
            break
        deg = m["prog"][b % len(m["prog"])]
        ch = _chord(m, deg)
        # ---- drums
        for k in range(8):
            tk = t0 + k * beat / 2
            if g == "twist":
                if k in (0, 4):
                    _place(y, kick(0.9), tk)
                if k in (2, 6):
                    _place(y, snare(0.6, seed=b * 8 + k), tk)
                _place(y, hat(0.5, seed=k), tk)
            elif g == "chacha":
                if k in (0, 4):
                    _place(y, kick(0.7), tk)
                if k in (3, 6, 7):
                    _place(y, rim(0.45), tk)
                _place(y, shaker(0.6, seed=k + b), tk)
            elif g == "bolero":
                if k == 0:
                    _place(y, kick(0.6), tk)
                if k in (2, 3, 6):
                    _place(y, rim(0.3), tk)
                if k % 2 == 0:
                    _place(y, shaker(0.4, seed=k + b), tk)
            elif g in ("march", "march_soft"):
                v = 0.5 if g == "march" else 0.25
                if k in (0, 4):
                    _place(y, kick(0.8 if g == "march" else 0.5), tk)
                _place(y, snare(v * (1.0 if k % 2 == 0 else 0.5), seed=k + b), tk)
            elif g == "orch":
                if k == 0 and b % 2 == 0:
                    _place(y, kick(0.9), tk)
                if k == 4 and b % 4 == 3:
                    _place(y, snare(0.3, seed=b), tk)
            elif g == "slow":
                if k == 0:
                    _place(y, kick(0.5), tk)
                if k == 4:
                    _place(y, rim(0.25), tk)
            elif g == "tick":
                _place(y, hat(0.25, seed=k), tk)
                if k == 0:
                    _place(y, kick(0.55), tk)
                    _place(y, kick(0.35), tk + 0.22)
        # ---- bass
        if g not in ("none", "tick"):
            if g == "twist":
                for k, dd in enumerate((0, 2, 4, 5)):
                    _place(y, bass(_chord(m, deg + dd, -2)[0], beat * 0.9, 0.8), t0 + k * beat)
            elif g in ("chacha", "bolero"):
                for k, off in enumerate((0, 1.5, 2, 3)):
                    _place(y, bass(ch[0 if k % 2 == 0 else 2] / 2, beat * 0.8, 0.8), t0 + off * beat)
            else:
                _place(y, bass(ch[0] / 2, bar * 0.9, 0.7), t0)
        elif g == "tick":
            _place(y, bass(ch[0] / 2, bar, 0.5), t0)
        # ---- harmony
        if m.get("keys") == "organ":
            if g in ("twist", "chacha"):
                for k in (1, 3):
                    _place(y, organ(ch, beat * 0.45, 0.6), t0 + k * beat)
            else:
                _place(y, organ(ch, bar * 0.95, 0.4, perc=False), t0)
        if m.get("pad") == "strings":
            _place(y, strings([f * 2 for f in ch], bar + 0.5, 0.6), t0)
        elif m.get("pad") == "drone" and b % 2 == 0:
            _place(y, drone(ch[0] / 2, bar * 2 + 1, 0.9), t0)
        if g == "orch" and b % 2 == 0:
            _place(y, brass([f * 2 for f in ch], beat * 1.5, 0.5), t0)
        # ---- lead (rests every 4th bar; sparse when tense)
        phrase = (b // 2) % 4
        motif = motifB if phrase == 2 else motifA
        if b % 4 == 3 and tense < 0.9:
            continue
        for k in range(8):
            if not rhythm[k] or (tense >= 0.9 and r.random() < 0.55):
                continue
            tk = t0 + k * beat / 2 + (bar if (b % 2) else 0) * 0
            dg = motif[(k + (b % 2) * 3) % 8] + (1 if phrase == 3 and k > 4 else 0)
            f = _note(m, dg, 0 if m["lead"] in ("brass", "piano") else 1)
            lead = m["lead"]
            if lead == "twang":
                _place(y, twang(f / 2, beat * 1.2, 0.55, seed=k + b), tk)
            elif lead == "vibes":
                _place(y, vibes(f, beat * 2.5, 0.45), tk)
            elif lead == "brass":
                _place(y, brass([f], beat * 0.8, 0.45), tk)
            elif lead == "piano":
                _place(y, piano(f / (2 if tense >= 0.9 else 1), beat * 3, 0.5), tk)
        if tense >= 0.9 and b % 4 == 1:   # tremolo-string swell
            tt = _t(bar * 2)
            sw = strings([ch[0] * 2, ch[0] * 2 * 2 ** (1 / 12)], bar * 2, 0.35) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * tt))
            _place(y, sw, t0)
    y = y[:int(d * SR)]
    y = reverb(y, 1.8 if tense >= 0.9 or g == "none" else 1.2, 0.3 if g in ("none", "tick", "slow") else 0.2, seed)
    pk = np.max(np.abs(y)) or 1
    y = y / pk * 0.6
    fi, fo = min(len(y) // 2, int(2.0 * SR)), min(len(y) // 2, int(3.0 * SR))
    y[:fi] *= np.linspace(0, 1, fi)
    y[-fo:] *= np.linspace(1, 0, fo)
    return y


# ------------------------------------------------------------------ era SFX
def sfx_projector(d=1.6, seed=0):
    t = _t(d)
    n = S.bp(np.random.default_rng(seed).standard_normal(len(t)), 800, 4000)
    clack = (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 24 * t))) * 0.7 + 0.3
    return n * clack * np.minimum(1, t / 0.2) * np.minimum(1, (d - t) / 0.3).clip(0, 1) * 0.35


def sfx_newspaper_spin(seed=0):
    t = _t(1.3)
    n = S.bp(np.random.default_rng(seed).standard_normal(len(t)), 600, 5000)
    sw = (0.5 + 0.5 * np.sin(2 * np.pi * (3 + 6 * t) * t)) * np.minimum(1, t / 0.4) * np.exp(-((t - 0.7) / 0.5) ** 2)
    return n * sw * 0.5


def sfx_sting(root=57):
    """Short brass chord sting for chapter posters."""
    ch = [_midi(root - 12), _midi(root - 5), _midi(root), _midi(root + 4)]
    y = brass(ch, 1.4, 0.8).copy()
    _place(y, kick(0.8), 0.0)
    _place(y, snare(0.4), 0.0)
    return reverb(y, 1.2, 0.25)
