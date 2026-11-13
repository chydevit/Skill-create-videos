"""Original, sparse and reflective score for 'The Khmer Republic: Cambodia 1970-1975' (synthesised; nothing copied).
Instruments: tro (Khmer bowed fiddle), khim (hammered dulcimer, paired strings), soft piano, low strings, a quiet
drone; pulses (heartbeat, clock tick, low drum) carry the quiet tension of chapters 8-10; a gentle mournful close.
Each cue is generated from a mood recipe and a seed."""
import numpy as np
from scipy import signal

import sound as S
from music60 import _env, _midi, _place, _t, piano, reverb, strings, drone

SR = S.SR
PENT_MIN = [0, 3, 5, 7, 10]
PENT_MAJ = [0, 2, 4, 7, 9]
KH_MODE = [0, 2, 3, 7, 8]      # a plaintive pentatonic colour
MIN = [0, 2, 3, 5, 7, 8, 10]


def khim(f, d=1.6, v=1.0, seed=0):
    """Hammered dulcimer: two slightly detuned strings per course, bright attack, bell-like decay."""
    t = _t(d)
    y = 0
    for det in (0.997, 1.003):
        ph = 2 * np.pi * f * det * t
        y = y + (np.sin(ph) + 0.45 * np.sin(2 * ph) * np.exp(-t * 6) + 0.2 * np.sin(3 * ph) * np.exp(-t * 9))
    hit = S.bp(np.random.default_rng(seed).standard_normal(len(t)), f * 2, min(9000, f * 8)) * np.exp(-t * 60) * 0.5
    y = (y / 2 + hit) * np.exp(-t * 2.2)
    y[:30] *= np.linspace(0, 1, 30)
    return y * v * 0.45


def tro70(f, d, v=1.0):
    t = _t(d)
    vib = 1 + 0.009 * np.sin(2 * np.pi * 5.2 * t) * np.clip(t * 1.5, 0, 1)
    y = signal.sawtooth(2 * np.pi * np.cumsum(f * vib) / SR)
    y = S.lp(y, f * 4.5) + 0.05 * S.bp(np.random.default_rng(int(f)).standard_normal(len(t)), f, f * 4)
    e = np.minimum(1, t / 0.25) * np.minimum(1, (d - t) / 0.35).clip(0, 1)
    return y * e * v * 0.42


def heartbeat(v=1.0):
    t = _t(0.5)
    a = np.sin(2 * np.pi * 48 * t) * np.exp(-t * 22)
    b = np.zeros_like(a)
    k = int(0.18 * SR)
    b[k:] = a[:len(a) - k] * 0.7
    return S.lp(a + b, 200) * v


def tick(v=1.0):
    t = _t(0.03)
    return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 200) * v * 0.4


def lowdrum(v=1.0):
    t = _t(0.9)
    f = 60 + 30 * np.exp(-t * 12)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4) * v


MOODS = {
    #  lead: tro|khim|piano|mix ; pad: strings|drone|both|None ; pulse: None|heart|tick|drum ; dens: notes per bar
    "dawn70": dict(bpm=64, root=55, scale=PENT_MAJ, prog=[0, 5, 3, 4], lead="khim", pad="strings", dens=0.7, arp=True),
    "pressure": dict(bpm=60, root=50, scale=KH_MODE, prog=[0, 0, 5, 3], lead="tro", pad="strings", dens=0.45),
    "march18": dict(bpm=66, root=48, scale=MIN, prog=[0, 5, 0, 4], lead="piano", pad="drone", pulse="tick", dens=0.35),
    "twocamb": dict(bpm=54, root=50, scale=KH_MODE, prog=[0, 3, 0, 4], lead="tro", pad="drone", dens=0.35),
    "border": dict(bpm=70, root=45, scale=MIN, prog=[0, 0, 5, 4], lead="piano", pad="both", pulse="drum", dens=0.3),
    "republic": dict(bpm=72, root=57, scale=PENT_MAJ, prog=[0, 3, 4, 0], lead="mix", pad="strings", dens=0.7, arp=True),
    "chenla": dict(bpm=62, root=47, scale=MIN, prog=[0, 5, 3, 4], lead="tro", pad="both", pulse="drum", dens=0.35),
    "politics": dict(bpm=76, root=52, scale=MIN, prog=[0, 3, 5, 4], lead="piano", pad="strings", dens=0.5, arp=True),
    "bombing": dict(bpm=56, root=43, scale=KH_MODE, prog=[0, 0, 5, 3], lead="tro", pad="drone", pulse="heart", dens=0.25),
    "siege": dict(bpm=58, root=45, scale=MIN, prog=[0, 5, 0, 4], lead="piano", pad="both", pulse="heart", dens=0.22),
    "fall": dict(bpm=50, root=41, scale=KH_MODE, prog=[0, 0, 3, 0], lead="piano", pad="drone", dens=0.16),
    "mourn": dict(bpm=54, root=50, scale=KH_MODE, prog=[0, 3, 4, 0], lead="mix", pad="strings", dens=0.45, arp=True),
    # Democratic Kampuchea 1975-79: very sparse and reflective; near-silence for S-21; gentle hope at the close
    "remember": dict(bpm=54, root=55, scale=PENT_MAJ, prog=[0, 5, 3, 4], lead="khim", pad="strings", dens=0.42, arp=True),
    "april": dict(bpm=56, root=50, scale=KH_MODE, prog=[0, 3, 0, 4], lead="tro", pad="strings", dens=0.32),
    "exodus": dict(bpm=50, root=48, scale=KH_MODE, prog=[0, 0, 5, 3], lead="tro", pad="drone", dens=0.26),
    "zero": dict(bpm=48, root=46, scale=MIN, prog=[0, 5, 0, 4], lead="piano", pad="drone", dens=0.18),
    "coop": dict(bpm=52, root=45, scale=KH_MODE, prog=[0, 0, 3, 0], lead="tro", pad="drone", dens=0.22),
    "state": dict(bpm=50, root=47, scale=MIN, prog=[0, 3, 5, 4], lead="piano", pad="strings", dens=0.2),
    "targets": dict(bpm=48, root=50, scale=KH_MODE, prog=[0, 3, 4, 0], lead="tro", pad="strings", dens=0.22),
    "purge": dict(bpm=46, root=41, scale=KH_MODE, prog=[0, 0, 3, 0], lead="piano", pad="drone", dens=0.12),
    "war75": dict(bpm=52, root=43, scale=MIN, prog=[0, 5, 0, 4], lead="tro", pad="both", pulse="drum", dens=0.18),
    "after": dict(bpm=54, root=52, scale=PENT_MAJ, prog=[0, 3, 4, 0], lead="mix", pad="strings", dens=0.35, arp=True),
    "hope": dict(bpm=58, root=55, scale=PENT_MAJ, prog=[0, 5, 3, 4], lead="khim", pad="strings", dens=0.5, arp=True),
    "credits75": dict(bpm=58, root=55, scale=PENT_MAJ, prog=[0, 5, 3, 4], lead="mix", pad="strings", dens=0.45,
                      arp=True),
    "credits70": dict(bpm=60, root=55, scale=PENT_MAJ, prog=[0, 5, 3, 4], lead="khim", pad="strings", dens=0.6, arp=True),
}


def _note(m, deg, octv=0):
    sc = m["scale"]
    o, k = divmod(deg, len(sc))
    return _midi(m["root"] + 12 * (o + octv) + sc[k])


def score(mood, d, seed=0):
    m = MOODS[mood]
    r = np.random.default_rng(seed + sum(map(ord, mood)))
    n = int(d * SR) + SR * 6
    y = np.zeros(n)
    beat = 60.0 / m["bpm"]
    bar = beat * 4
    t, b = 0.8, 0
    while t < d:
        root_deg = m["prog"][b % len(m["prog"])]
        if m.get("pad") in ("strings", "both"):
            ch = [_note(m, root_deg, -2), _note(m, root_deg + 2, -1), _note(m, root_deg + 4, -1)]
            _place(y, strings(ch, bar + 0.8, 0.5), t)
        if m.get("pad") in ("drone", "both") and b % 2 == 0:
            _place(y, drone(_note(m, root_deg, -2), bar * 2 + 1.0, 0.9), t)
        # melody: a few notes per bar, falling phrases, rests
        k = int(round(4 * m["dens"] + r.random() * 1.2))
        deg = root_deg + int(r.integers(2, 6))
        for i in range(max(0, k)):
            if r.random() < 0.25:
                continue
            tp = t + (i * 4 / max(1, k)) * beat + r.normal() * 0.03
            dd = beat * (4 / max(1, k)) * (1.4 if m["lead"] == "tro" else 1.0)
            f = _note(m, deg, 0)
            lead = m["lead"] if m["lead"] != "mix" else ("khim" if (b + i) % 3 else "tro")
            if lead == "khim":
                _place(y, khim(f, 2.2, 0.55, seed + b * 7 + i), tp)
                if m.get("arp"):
                    _place(y, khim(f * 1.5, 1.6, 0.2, seed + b * 11 + i), tp + beat / 2)
            elif lead == "tro":
                _place(y, tro70(f, dd * 0.95, 0.45), tp)
            else:
                _place(y, piano(f, 2.8, 0.5), tp)
                if m.get("arp") and r.random() < 0.5:
                    _place(y, piano(f / 2, 2.8, 0.25), tp)
            deg += int(r.choice([-1, -1, -2, 1, 0]))
        p = m.get("pulse")
        if p == "heart":
            for q in range(2):
                _place(y, heartbeat(0.55), t + q * bar / 2)
        elif p == "tick":
            for q in range(8):
                _place(y, tick(0.5 if q % 2 == 0 else 0.3), t + q * beat / 2)
        elif p == "drum":
            _place(y, lowdrum(0.45), t)
            _place(y, lowdrum(0.25), t + beat * 2.5)
        t += bar
        b += 1
    fade = np.ones(n)
    k = int(2.5 * SR)
    end = min(n, int(d * SR) + int(1.5 * SR))
    fade[max(0, end - k):end] = np.linspace(1, 0, min(k, end))
    fade[end:] = 0
    y = reverb(y * fade, 2.4, 0.32, seed)
    return y / (np.max(np.abs(y)) or 1) * 0.8


# ------------------------------------------------------------------ SFX
def sfx_static(d=1.0, seed=0):
    t = _t(d)
    n = np.random.default_rng(seed).standard_normal(len(t))
    n = S.bp(n, 300, 6000)
    crack = (np.random.default_rng(seed + 1).random(len(t)) > 0.9993) * 4.0
    sweep = np.sin(2 * np.pi * (600 + 900 * t / d) * t) * 0.15
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 0.7
    return (n * 0.6 + crack + sweep) * e * 0.5


def sfx_page(seed=0):
    t = _t(0.9)
    n = S.bp(np.random.default_rng(seed).standard_normal(len(t)), 500, 7000)
    e = np.exp(-((t - 0.35) / 0.18) ** 2) + 0.4 * np.exp(-((t - 0.62) / 0.06) ** 2)
    return n * e * 0.55


def sfx_chapter(root=50):
    """Soft chapter accent: a low string swell under a single khim note (no fanfare)."""
    y = strings([_midi(root - 12), _midi(root - 5), _midi(root)], 2.6, 0.6).copy()
    _place(y, khim(_midi(root + 12), 2.4, 0.5, 3), 0.15)
    return reverb(y, 2.0, 0.3)
