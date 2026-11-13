"""Score, ambience and mix.  Instruments come from sound.py's synthesised pinpeat set
(roneat, kong, khloy, tro, chapei, skor, ching) plus a soft string-like pad.  Each chapter has its own motif
(a short pentatonic cell) and instrument colour; music ducks under the voices; master at -16 LUFS."""
import math
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sound as S  # noqa: E402

SR = S.SR


def _midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def _place(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= len(buf) or len(x) == 0:
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += np.asarray(x[:j - i], dtype=np.float64) * g


def _fade(y, fi=2.0, fo=3.0):
    n = len(y)
    a, b = min(n // 2, int(fi * SR)), min(n // 2, int(fo * SR))
    if a:
        y[:a] *= np.linspace(0, 1, a)
    if b:
        y[-b:] *= np.linspace(1, 0, b)
    return y


# motif = scale-degree cell; lead instrument; tempo; extras
MOTIFS = {
    "opening": dict(root=57, scale=[0, 2, 4, 7, 9], cell=[4, 3, 2, 0, 1, 2], lead="khloy", bpm=60, pad=1.0, gong=True),
    "land": dict(root=55, scale=[0, 2, 4, 7, 9], cell=[0, 2, 3, 2, 4, 3], lead="chapei", bpm=72, pad=0.7, perc="ching"),
    "legend": dict(root=52, scale=[0, 3, 5, 7, 10], cell=[0, 1, 3, 2, 1, 0], lead="tro", bpm=58, pad=0.8, skor=True),
    "port": dict(root=60, scale=[0, 2, 4, 7, 9], cell=[2, 4, 5, 4, 2, 3], lead="roneat", bpm=96, pad=0.6, perc="ching",
                 skor=True),
    "water": dict(root=57, scale=[0, 2, 4, 7, 9], cell=[0, 4, 3, 1, 2, 0], lead="roneat", bpm=66, pad=0.9, bells=True),
    "fleet": dict(root=50, scale=[0, 2, 3, 7, 9], cell=[0, 0, 2, 3, 4, 2], lead="kong", bpm=88, pad=0.8, skor=True,
                  gong=True),
    "envoys": dict(root=55, scale=[0, 2, 4, 7, 9], cell=[4, 2, 1, 2, 0, 1], lead="kong", bpm=70, pad=0.8, gong=True),
    "india": dict(root=52, scale=[0, 1, 4, 5, 7], cell=[0, 2, 3, 4, 3, 1], lead="khloy", bpm=64, pad=1.0, bells=True),
    "life": dict(root=60, scale=[0, 2, 4, 7, 9], cell=[0, 2, 4, 2, 3, 1], lead="chapei", bpm=100, pad=0.5,
                 perc="ching"),
    "kings": dict(root=55, scale=[0, 2, 4, 7, 9], cell=[4, 4, 3, 2, 3, 0], lead="kong", bpm=66, pad=1.0, gong=True),
    "decline": dict(root=50, scale=[0, 3, 5, 7, 10], cell=[3, 2, 0, 1, 0, 0], lead="khloy", bpm=56, pad=1.0, tro=True),
    "legacy": dict(root=57, scale=[0, 2, 4, 7, 9], cell=[4, 3, 2, 0, 1, 2], lead="roneat", bpm=70, pad=1.0, gong=True,
                   bells=True),
    "credits": dict(root=57, scale=[0, 2, 4, 7, 9], cell=[0, 2, 4, 3, 2, 0], lead="khloy", bpm=64, pad=1.0),
    # --- French Protectorate chapters (a distinct motif per chapter; darker tones for 'rubber' and 'war') ---
    "treaty": dict(root=55, scale=[0, 2, 4, 7, 9], cell=[4, 2, 1, 0, 2, 0], lead="kong", bpm=60, pad=1.0, gong=True,
                   tro=True),
    "capital": dict(root=57, scale=[0, 2, 4, 7, 9], cell=[0, 2, 4, 2, 0, 4], lead="roneat", bpm=84, pad=0.7,
                    perc="ching"),
    "revolt": dict(root=52, scale=[0, 3, 5, 7, 10], cell=[0, 3, 2, 3, 0, 0], lead="tro", bpm=80, pad=0.8, skor=True),
    "union": dict(root=55, scale=[0, 2, 4, 7, 9], cell=[2, 4, 3, 2, 4, 5], lead="roneat", bpm=72, pad=0.8, bells=True),
    "angkor": dict(root=52, scale=[0, 2, 4, 7, 9], cell=[4, 3, 4, 7, 4, 2], lead="khloy", bpm=62, pad=1.0, gong=True,
                   bells=True),
    "rubber": dict(root=48, scale=[0, 3, 5, 7, 10], cell=[0, 0, 3, 2, 0, 0], lead="tro", bpm=52, pad=1.0, skor=True,
                   tro=True),
    "city": dict(root=60, scale=[0, 2, 4, 7, 9], cell=[0, 2, 4, 5, 4, 2], lead="chapei", bpm=104, pad=0.5,
                 perc="ching"),
    "voice": dict(root=57, scale=[0, 2, 4, 7, 9], cell=[0, 2, 4, 3, 4, 7], lead="khloy", bpm=70, pad=0.8, bells=True),
    "war": dict(root=47, scale=[0, 3, 5, 6, 10], cell=[0, 3, 2, 0, 3, 0], lead="kong", bpm=50, pad=1.0, skor=True,
                gong=True, tro=True),
    "road": dict(root=55, scale=[0, 2, 4, 7, 9], cell=[0, 2, 4, 2, 4, 7], lead="roneat", bpm=78, pad=0.9, skor=True),
    "independence": dict(root=57, scale=[0, 2, 4, 7, 9], cell=[0, 4, 7, 4, 2, 0], lead="kong", bpm=72, pad=1.0,
                         gong=True, bells=True),
    # --- 1945: the Japanese period (distinct motif per chapter; darker in 'risingsun' (ch.5) and 'august' (ch.8)) ---
    "storm45": dict(root=50, scale=[0, 3, 5, 7, 10], cell=[0, 3, 2, 0, 5, 3], lead="khloy", bpm=58, pad=1.0, taiko=True,
                    tro=True),
    "twomasters": dict(root=55, scale=[0, 2, 3, 7, 9], cell=[2, 0, 2, 3, 1, 0], lead="kong", bpm=66, pad=0.9,
                       skor=True),
    "coup": dict(root=48, scale=[0, 3, 5, 7, 10], cell=[0, 0, 3, 0, 2, 0], lead="tro", bpm=92, pad=0.8, taiko=True,
                 skor=True),
    "kampuchea": dict(root=57, scale=[0, 2, 4, 7, 9], cell=[0, 2, 4, 7, 4, 9], lead="roneat", bpm=80, pad=0.9,
                      gong=True, bells=True),
    "script": dict(root=55, scale=[0, 2, 4, 7, 9], cell=[4, 2, 4, 5, 2, 0], lead="khloy", bpm=64, pad=0.9, bells=True),
    "risingsun": dict(root=47, scale=[0, 1, 5, 7, 8], cell=[0, 1, 0, 5, 3, 0], lead="tro", bpm=52, pad=1.0, tro=True,
                      skor=True),
    "thanh": dict(root=52, scale=[0, 2, 3, 7, 9], cell=[0, 2, 3, 4, 3, 1], lead="chapei", bpm=70, pad=0.8),
    "greenshirts": dict(root=55, scale=[0, 2, 4, 7, 9], cell=[0, 0, 4, 4, 2, 0], lead="kong", bpm=108, pad=0.6,
                        perc="ching", taiko=True),
    "august": dict(root=45, scale=[0, 1, 5, 6, 10], cell=[0, 1, 0, 3, 1, 0], lead="kong", bpm=48, pad=1.0, taiko=True,
                   gong=True, tro=True),
    "noprotector": dict(root=52, scale=[0, 2, 3, 7, 8], cell=[3, 2, 0, 2, 4, 3], lead="khloy", bpm=60, pad=1.0),
    "return45": dict(root=50, scale=[0, 2, 3, 7, 10], cell=[4, 3, 2, 0, 1, 0], lead="tro", bpm=56, pad=1.0, skor=True),
    "whatwas": dict(root=55, scale=[0, 2, 4, 7, 9], cell=[0, 4, 2, 3, 1, 2], lead="roneat", bpm=64, pad=1.0, bells=True),
}


def score(mood, d, seed=0):
    import music60
    import music70
    if mood in music70.MOODS:
        return music70.score(mood, d, seed)
    if mood in music60.MOODS:
        return music60.score(mood, d, seed)
    m = MOTIFS[mood]
    r = np.random.default_rng(seed + sum(map(ord, mood)))
    n = int(d * SR) + SR * 6
    y = np.zeros(n)
    beat = 60.0 / m["bpm"]
    sc, sl = m["scale"], len(m["scale"])

    def note(deg, octv=0):
        o, k = divmod(deg, sl)
        return _midi(m["root"] + 12 * (o + octv) + sc[k])
    t = 1.0
    phrase = 0
    while t < d:
        cell = list(m["cell"])
        if phrase % 4 == 2:      # variation: invert the tail
            cell = cell[:3] + [max(0, 2 * cell[2] - c) for c in cell[3:]]
        if phrase % 4 == 3:
            cell = [c + 1 for c in cell]
        for i, deg in enumerate(cell):
            tp = t + i * beat
            f = note(deg, 1)
            if m["lead"] == "khloy":
                _place(y, S.khloy(f, beat * 1.8, 0.4, seed=i + phrase), tp)
            elif m["lead"] == "roneat":
                _place(y, S.roneat(f, 0.8, 0.45), tp)
                _place(y, S.roneat(f * 2, 0.5, 0.1), tp + beat / 2)
            elif m["lead"] == "kong":
                _place(y, S.kong(f / 2, 1.8, 0.45), tp)
            elif m["lead"] == "chapei":
                _place(y, S.chapei(f / 2, 0.9, 0.5, seed=i), tp)
            elif m["lead"] == "tro":
                _place(y, S.tro(f, beat * 1.9, 0.3), tp)
        if m.get("pad"):
            root = note(0, -1) if phrase % 2 == 0 else note(3, -1)
            _place(y, S.pad([root, root * 1.5, root * 2], beat * len(cell) + 1.5, 0.45 * m["pad"]), t)
        if m.get("tro"):
            _place(y, S.tro(note(0, 0), beat * len(cell), 0.18), t)
        if m.get("perc") == "ching":
            for b in range(len(cell)):
                _place(y, S.ching(b % 2 == 0, 0.25), t + b * beat)
        if m.get("skor"):
            for b in range(len(cell)):
                if b % 2 == 0:
                    _place(y, S.skor(0.4, 110, 0.35), t + b * beat)
        if m.get("taiko"):   # deep taiko-like strokes
            for b in range(len(cell)):
                if b % 3 == 0:
                    _place(y, S.sfx_drum_hit(phrase * 7 + b) * 0.55, t + b * beat)
        if m.get("gong") and phrase % 4 == 0:
            _place(y, S.sfx_gong(_midi(m["root"] - 24), 6.0) * 0.35, t)
        if m.get("bells") and phrase % 2 == 1:
            _place(y, S.sfx_bell(note(4, 2), 3.0) * 0.12, t + beat * 2)
        t += beat * (len(cell) + 2 + (2 if phrase % 2 else 0))   # breathing space between phrases
        phrase += 1
    y = y[:int(d * SR)]
    pk = np.max(np.abs(y)) or 1
    return _fade(y / pk * 0.6, 2.5, 3.0)


def ambience(kind, d, seed=0):
    d = max(d, 0.6)
    if kind in (None, "none"):
        return np.zeros(int(d * SR))
    if kind == "delta":
        y = S.ambience("river", d, seed) * 0.8 + S._scatter(d, seed + 1, S.sfx_bird, 0.35, 0.35)
    elif kind == "port":
        y = S.ambience("market", d, seed) * 0.6 + S.ambience("river", d, seed + 2) * 0.5
    elif kind == "sea":
        y = S._wind(d, seed, 1.2) * 0.8 + S._water(d, seed + 1) * 1.2
    elif kind == "lamp":
        y = S.ambience("night", d, seed) * 0.4 + S._scatter(d, seed + 1, S.sfx_fire, 0.2, 0.25)
    elif kind == "workshop":
        y = S.ambience("market", d, seed) * 0.4 + S._scatter(d, seed + 1, S.sfx_tool_hit, 0.9, 0.18)
    else:
        y = S.ambience(kind, d, seed)
    return _fade(np.asarray(y, dtype=np.float64), 1.0, 1.2)


def _load(path):
    w, sr = sf.read(path, dtype="float64")
    if w.ndim > 1:
        w = w.mean(1)
    if sr != SR:
        w = signal.resample_poly(w, SR, sr)
    return w


def mix(shots, placements, total, out_wav, log=print):
    n = int((total + 1.0) * SR)
    voice = np.zeros(n)
    music = np.zeros(n)
    amb = np.zeros(n)
    sfx = np.zeros(n)
    for p in placements:
        if os.path.exists(p["wav"]):
            w = S.hp(_load(p["wav"]), 70)
            g = 0.8 if p.get("who", "nar") == "nar" else 0.74
            _place(voice, w / (np.max(np.abs(w)) or 1) * g, p["t"])
        else:
            log("  missing voice %s" % p["key"])
    cues = [(s["start"], s["music"]) for s in shots if s.get("music")]
    for i, (t0, mood) in enumerate(cues):
        t1 = cues[i + 1][0] + 3.0 if i + 1 < len(cues) else total
        if mood != "silence":
            _place(music, score(mood, t1 - t0, seed=i), t0)
    cur = None
    for s in shots:
        cur = s.get("amb") or cur
        if s.get("tag") == "credits":
            cur = "none"
        _place(amb, ambience(cur, s["dur"] + 1.5, seed=int(s["start"])), max(0, s["start"] - 0.5))
        tr = s.get("trans")
        if tr == "ripple":
            _place(sfx, S.sfx_splash(int(s["start"])) * 0.35, max(0, s["start"] - s.get("xin", 1)))
        elif tr == "lotus":
            _place(sfx, S.sfx_chime(int(s["start"])) * 0.4, max(0, s["start"] - s.get("xin", 1)))
        elif tr == "ink":
            _place(sfx, S.sfx_whoosh(int(s["start"]), 0.8) * 0.3, max(0, s["start"] - s.get("xin", 1)))
        elif tr == "shutter":
            _place(sfx, S.sfx_camera(int(s["start"])) * 0.6, max(0, s["start"] - s.get("xin", 1)))
        elif tr == "reel":
            import music60
            _place(sfx, music60.sfx_projector(s.get("xin", 1.2) + 0.4, int(s["start"])) * 0.8,
                   max(0, s["start"] - s.get("xin", 1)))
        elif tr == "news":
            import music70
            _place(sfx, music70.sfx_page(int(s["start"])) * 0.8, max(0, s["start"] - s.get("xin", 1)))
            _place(sfx, S.sfx_paper(2) * 0.4, max(0, s["start"] - s.get("xin", 1) * 0.6))
        elif tr == "page":
            import music70
            _place(sfx, music70.sfx_page(int(s["start"]) + 1) * 0.7, max(0, s["start"] - s.get("xin", 1)))
        elif tr == "static":
            import music70
            _place(sfx, music70.sfx_static(s.get("xin", 1.0) + 0.3, int(s["start"])) * 0.45,
                   max(0, s["start"] - s.get("xin", 1)))
        if s.get("tag") == "chapter":
            import music70
            _place(sfx, music70.sfx_chapter(50 if "sting_dark" not in (s.get("sfx") or []) else 43) * 0.4,
                   s["start"] + 0.2)
        for name in s.get("sfx") or []:
            if name == "hit":
                _place(sfx, S.sfx_drum_hit(int(s["start"])) * 0.8, s["start"])
            elif name == "gun":   # distant gunfire bursts
                for j, dt in enumerate((0.4, 0.55, 0.62, 1.6, 1.7, 2.9)):
                    _place(sfx, S.sfx_thud(j) * 0.5, s["start"] + dt)
                    _place(sfx, S.sfx_drum_hit(j + 3) * 0.25, s["start"] + dt)
            elif name == "thunder":
                _place(sfx, S.lp(S._rng(int(s["start"])).standard_normal(int(3.5 * SR)), 120)
                       * np.exp(-np.linspace(0, 4, int(3.5 * SR))) * 1.4, s["start"] + 1.3)
            elif name == "shutter":
                _place(sfx, S.sfx_camera(int(s["start"]) + 5) * 0.55, s["start"] + 1.2)
            elif name == "radio":
                import music70
                _place(sfx, music70.sfx_static(1.2, int(s["start"]) + 9) * 0.3, s["start"] + 0.1)
            elif name == "plane":   # distant aircraft drone
                _place(sfx, S.lp(S._rng(int(s["start"])).standard_normal(int(6 * SR)), 180)
                       * np.sin(np.linspace(0, np.pi, int(6 * SR))) * 0.9, s["start"] + 0.5)
            elif name == "bell":
                _place(sfx, S.sfx_bell(660, 3.0) * 0.4, s["start"] + 0.3)
            elif name == "monbell":   # a distant monastery bell
                _place(sfx, S.lp(S.sfx_bell(196, 6.0), 1800) * 0.55, s["start"] + 0.6)
            elif name == "match":     # a match struck, then the soft breath of a flame
                _place(sfx, S.sfx_swish(int(s["start"])) * 0.35, s["start"] + 0.2)
                _place(sfx, S.sfx_fire(int(s["start"])) * 0.12, s["start"] + 0.5)
        if tr == "smoke":
            _place(sfx, S.sfx_whoosh(int(s["start"]), 1.4) * 0.12, max(0, s["start"] - s.get("xin", 1)))
        if s.get("badge") in ("text", "inscription"):
            _place(sfx, S.sfx_paper(1) * 0.25, s["start"] + 0.2)
    env = np.convolve(np.abs(voice), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    active = np.convolve((env > 0.01).astype(float), np.ones(int(0.6 * SR)) / int(0.6 * SR), mode="same")
    duck_m = 1.0 - 0.80 * np.clip(active, 0, 1)
    duck_a = 1.0 - 0.55 * np.clip(active, 0, 1)
    mixd = voice + music * 0.24 * duck_m + amb * 0.16 * duck_a + sfx * 0.5
    import pyloudnorm as pyln
    L = pyln.Meter(SR).integrated_loudness(mixd)
    g = 10 ** ((-16.0 - L) / 20)
    mixd = mixd * g
    if np.max(np.abs(mixd)) > 0.89:
        mixd = np.tanh(mixd / 0.89) * 0.89
    log("  mix loudness %.1f LUFS -> -16, peak %.2f" % (L, np.max(np.abs(mixd))))
    sf.write(out_wav, np.stack([mixd, mixd], 1).astype(np.float32), SR)


def envelope(wav_path, fps=24):
    """Per-frame mouth opening (0..1) from a voice clip, for the guide's lip-sync."""
    w = _load(wav_path)
    hop = SR // fps
    n = len(w) // hop + 1
    e = np.array([np.sqrt(np.mean(w[i * hop:(i + 1) * hop] ** 2)) if i * hop < len(w) else 0 for i in range(n)])
    e = e / (np.percentile(e, 95) or 1)
    return np.clip(e * 1.1 - 0.08, 0, 1)
