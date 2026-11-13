"""Ambient synth score for explainer films (warm detuned pads, plucked arpeggio with echo, soft sub, bells).

install(audio) makes audio.score() use these moods; any other mood name still gets the pinpeat score.
Moods: wonder, ancient, tension, warm, discovery, outro (add your own to SYNTH).
"""
import numpy as np
from scipy import signal

import sound as S

SR = S.SR

# chords: (root midi, intervals); progression cycles; arp = notes per beat (0 = none)
SYNTH = {
    "wonder": dict(bpm=76, prog=[(57, (0, 4, 7, 11)), (53, (0, 4, 7, 11)), (60, (0, 4, 7, 9)), (55, (0, 4, 7, 9))],
                   arp=2, bright=1400, bells=True),
    "ancient": dict(bpm=64, prog=[(50, (0, 3, 7, 10)), (48, (0, 4, 7, 9)), (46, (0, 4, 7, 11)), (45, (0, 3, 7))],
                    arp=1, bright=900, bells=False),
    "tension": dict(bpm=88, prog=[(45, (0, 3, 7)), (46, (0, 4, 7)), (45, (0, 3, 7)), (43, (0, 4, 7, 10))],
                    arp=4, bright=1100, bells=False),
    "warm": dict(bpm=70, prog=[(53, (0, 4, 7, 9)), (55, (0, 4, 7)), (57, (0, 3, 7, 10)), (50, (0, 3, 7, 10))],
                 arp=2, bright=1600, bells=True),
    "discovery": dict(bpm=96, prog=[(60, (0, 4, 7, 11)), (57, (0, 3, 7, 10)), (53, (0, 4, 7, 11)), (55, (0, 4, 7))],
                      arp=4, bright=2200, bells=True),
    "outro": dict(bpm=68, prog=[(53, (0, 4, 7, 11)), (55, (0, 4, 7, 9)), (57, (0, 3, 7, 10)), (52, (0, 3, 7))],
                  arp=2, bright=1300, bells=True),
}


def _hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _saw(f, n, ph=0.0):
    t = np.arange(n) / SR
    return 2 * ((f * t + ph) % 1.0) - 1


def _env(n, a, r):
    e = np.ones(n)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def _pad(notes, d, bright, rng):
    n = int(d * SR)
    y = np.zeros(n)
    for m in notes:
        for det in (-0.09, 0.0, 0.08):
            y += _saw(_hz(m + det), n, rng.random()) * 0.22
    b, a = signal.butter(2, bright / (SR / 2), "low")
    y = signal.lfilter(b, a, y)
    lfo = 0.85 + 0.15 * np.sin(2 * np.pi * 0.11 * np.arange(n) / SR + rng.random() * 6)
    return y * lfo * _env(n, 1.6, 2.2) / max(1, len(notes))


def _pluck(f, d=0.9):
    n = int(d * SR)
    t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t))
    return y * np.exp(-t * 5.5) * _env(n, 0.004, 0.05)


def _bell(f, d=3.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 2)
    return y * np.exp(-t * 1.4) * 0.5


def _place(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[:j - i] * g


def synth_score(mood, d, seed=0):
    m = SYNTH[mood]
    rng = np.random.default_rng(seed + sum(map(ord, mood)))
    n = int(d * SR) + SR * 4
    pad, arp, low = np.zeros(n), np.zeros(n), np.zeros(n)
    beat = 60.0 / m["bpm"]
    bar = beat * 4
    t, k = 0.0, 0
    while t < d:
        root, iv = m["prog"][k % len(m["prog"])]
        notes = [root + i for i in iv]
        _place(pad, _pad(notes, bar * 2 + 2.0, m["bright"], rng), t)
        nl = int((bar * 2 + 1.5) * SR)
        tt = np.arange(nl) / SR
        _place(low, np.sin(2 * np.pi * _hz(root - 12) * tt) * _env(nl, 0.8, 1.5) * 0.5, t)
        if m["arp"]:
            step = beat / m["arp"]
            seq = [notes[i % len(notes)] + 12 * (1 + (i // len(notes)) % 2) for i in range(int(bar * 2 / step))]
            for i, nt in enumerate(seq):
                if rng.random() < 0.12:
                    continue
                _place(arp, _pluck(_hz(nt)), t + i * step, 0.22 + 0.06 * rng.random())
        if m["bells"] and k % 2 == 1:
            _place(arp, _bell(_hz(notes[-1] + 24)), t + beat * 2, 0.10)
        t += bar * 2
        k += 1
    # echo on the arpeggio (dotted eighth)
    dl = int(beat * 0.75 * SR)
    echo = arp.copy()
    for g in (0.38, 0.18, 0.08):
        echo[dl:] += arp[:-dl] * g if dl < len(arp) else 0
        dl += int(beat * 0.75 * SR)
    y = pad * 1.0 + echo * 0.8 + low * 0.55
    b, a = signal.butter(1, 40 / (SR / 2), "high")
    y = signal.lfilter(b, a, y)[:int(d * SR)]
    pk = np.max(np.abs(y)) or 1
    y = y / pk * 0.6
    fi, fo = min(len(y) // 2, int(2.0 * SR)), min(len(y) // 2, int(3.0 * SR))
    if fi:
        y[:fi] *= np.linspace(0, 1, fi)
    if fo:
        y[-fo:] *= np.linspace(1, 0, fo)
    return y


def install(audio):
    if getattr(audio, "_synth_installed", False):
        return
    orig = audio.score

    def score(mood, d, seed=0):
        return synth_score(mood, d, seed) if mood in SYNTH else orig(mood, d, seed)
    audio.score = score
    audio._synth_installed = True
