"""Timings for the promo, measured from the narration: <project>/build/tm.json (read by scene.mjs and audio.py).

python plan.py <project>/promo.json

Rules: each work's own sound starts 0.12 s after its narration line ends and stops just before the next spotlight;
the break's big second word lands on the last word of the "next" line; the three rush words land on the first three
phrases of the "rush" line (split at its pauses). Without narration everything falls back to fixed timings.
"""
import json, os, subprocess, sys
import numpy as np

CFG_PATH = os.path.abspath(sys.argv[1])
P = os.path.dirname(CFG_PATH)
MAN = json.load(open(f'{P}/assets/manifest.json'))
N = len(MAN['works'])
BAR, T0 = 4 * 60 / 128, 0.075
B = lambda n: T0 + n * BAR
S = [B(5 + 3 * k) for k in range(N)]
BREAK, HIT = B(5 + 3 * N), B(9 + 3 * N)
VOX = f'{P}/build/vox'

def env(k):
    f = f'{VOX}/{k}.wav'
    if not os.path.exists(f): return None
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32); h = 160
    return 20 * np.log10(np.array([np.sqrt(np.mean(x[i:i + h] ** 2)) for i in range(0, len(x) - h, h)]) + 1e-9)   # 10 ms steps
def speech(k):
    e = env(k)
    if e is None: return None
    loud = np.where(e > max(-45, e.max() - 32))[0]
    return float(loud[0] * 0.01), float((loud[-1] + 1) * 0.01)
def phrase_starts(k):
    """start times (s, in the clip) of the phrases between pauses of 90 ms or more; a phrase must get loud
    within 150 ms (so a breathy word ending after a gap is not taken for a new phrase)"""
    e = env(k)
    if e is None: return []
    mx = e.max(); on = e > max(-45, mx - 30)
    starts, quiet, first = [], 0, True
    for i, v in enumerate(on):
        if v:
            if (first or quiet >= 9) and e[i:i + 15].max() > mx - 20: starts.append(i * 0.01)
            first, quiet = False, 0
        else: quiet += 1
    return starts
def onsets(k):
    """word onsets: the energy jumps 8 dB or more within 40 ms up to a loud level"""
    e = env(k)
    if e is None: return []
    mx, out = e.max(), []
    for i in range(1, len(e)):
        if e[i] > mx - 14 and e[i] - e[max(0, i - 4):i].min() >= 8 and (not out or i * 0.01 - out[-1] > 0.1):
            out.append(i * 0.01)
    return out

tm = {'trim': {}}
ends = [(speech(f'n1{k + 1}') or (0, 1.6))[1] for k in range(N)]
tm['bite'] = [round(s + 0.15 + e + 0.12, 3) for s, e in zip(S, ends)]
nxt = [s + 0.1 for s in S[1:]] + [BREAK - 0.025]
tm['blen'] = [round(max(1.0, min(3.6, n - b)), 3) for b, n in zip(tm['bite'], nxt)]
NEXT0 = BREAK + 0.075
sp8 = speech('r08')
if sp8:
    tm['trim']['r08'] = round(max(0.0, sp8[0] - 0.03), 3)
    on = onsets('r08')                               # the big word lands on the line's last strong onset
    last = on[-1] if len(on) > 1 else max(sp8[0], sp8[1] - 0.45)
    tm['next'] = [round(NEXT0, 3), round(NEXT0 + last - tm['trim']['r08'], 3)]
    r09 = max(BREAK + 2.025, NEXT0 + sp8[1] - tm['trim']['r08'] + 0.2)
else:
    tm['next'] = [round(NEXT0, 3), round(NEXT0 + 1.1, 3)]; r09 = BREAK + 2.025
sp9 = speech('r09')
if sp9:
    tm['trim']['r09'] = round(max(0.0, sp9[0] - 0.03), 3)
    ph = [p - tm['trim']['r09'] for p in phrase_starts('r09')]
    if len(ph) < 3:                                  # not enough pauses: spread the words over the line
        d = sp9[1] - sp9[0]; ph = [0, d * 0.36, d * 0.62]
    tm['wva'] = [round(r09 + p, 3) for p in ph[:3]]
else:
    tm['wva'] = [round(r09 + d, 3) for d in (0, 0.9, 1.7)]
tm['r09'] = round(r09, 3)
tm['spot'] = [round(s + 0.15, 3) for s in S]
tm['N'], tm['BREAK'], tm['HIT'], tm['DUR'] = N, round(BREAK, 3), round(HIT, 3), round(HIT + 6.425, 3)
os.makedirs(f'{P}/build', exist_ok=True)
json.dump(tm, open(f'{P}/build/tm.json', 'w'), indent=1)
print('timings:', json.dumps({k: tm[k] for k in ('bite', 'blen', 'next', 'wva', 'DUR')}))
