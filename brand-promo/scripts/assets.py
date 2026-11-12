"""Cut everything the promo shows out of the brand's own videos, plus the logo animation frames.

python assets.py <project>/promo.json      (re-running skips anything already extracted)

For each work: a 6.4 s picture clip that starts 2 s before its sound bite, the 4 s sound bite itself with a
30 fps loudness envelope (it drives the "Sound on" bars), two extra silent clips for the rush, and three stills.
The logo animation (an alpha .mov/.webm, e.g. /generate-logo liquid with --prores, or its -alpha.webm) is cropped
square around the finished mark and scaled to 1000x1000 frames.
"""
import json, os, subprocess, sys
import numpy as np

CFG_PATH = os.path.abspath(sys.argv[1])
P = os.path.dirname(CFG_PATH)
CFG = json.load(open(CFG_PATH))
A = os.path.join(P, 'assets')
LEAD, BITE, CLIP = 2.0, 4.0, 6.4
SR = 48000

def ff(*a): subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', *a], check=True)
def probe(path):
    js = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height',
                                    '-of', 'json', path], capture_output=True, text=True, check=True).stdout)
    v = next(s for s in js['streams'] if s['codec_type'] == 'video')
    return v['width'], v['height'], float(js['format']['duration']), any(s['codec_type'] == 'audio' for s in js['streams'])
def mmss(sec): return f'{int(sec // 60)}:{int(sec % 60):02d}'
def audio(path, ss, dur, sr=12000):
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{ss:.3f}', '-t', f'{dur:.3f}', '-i', path, '-vn', '-ac', '1',
                          '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)
def auto_bite(path, dur):
    """a sentence start near 35 % of the video: the end of the quietest 0.3 s inside a 6 s window"""
    t0 = max(0.0, min(dur * 0.35, dur - 10))
    x = audio(path, t0, 6.0); h = 600
    if len(x) < h * 10: return t0
    e = np.convolve(x ** 2, np.ones(h * 3) / (h * 3), 'valid')[::h]
    return round(t0 + (int(np.argmin(e[:-8])) + 3) * h / 12000, 2)
def frames(dst, src, ss, dur, scale):
    if os.path.isdir(dst) and os.listdir(dst): return
    os.makedirs(dst, exist_ok=True)
    ff('-ss', f'{max(0, ss):.3f}', '-t', f'{dur:.3f}', '-i', src, '-vf', f'fps=30,{scale},format=yuvj420p', '-q:v', '2', f'{dst}/%04d.jpg')

os.makedirs(f'{A}/clips', exist_ok=True); os.makedirs(f'{A}/bites', exist_ok=True); os.makedirs(f'{A}/stills', exist_ok=True)
works, levels, stills_by_work, rush, vertical, vertical_stills = [], {}, [], [], [], []
si = 0
for k, w in enumerate(CFG['works']):
    src = os.path.expanduser(w['video'])
    vw, vh, dur, has_audio = probe(src)
    vert = vh > vw
    sc = 'scale=620:-2:flags=lanczos' if vert else 'scale=1100:-2:flags=lanczos'
    bite = float(w['sound']) if 'sound' in w else auto_bite(src, dur) if has_audio else dur * 0.35
    bite = min(max(bite, LEAD), max(LEAD, dur - BITE - 0.5))
    name = f'p{k + 1}'
    frames(f'{A}/clips/{name}', src, bite - LEAD, CLIP, sc)
    sound = has_audio and not w.get('mute', False)
    if sound:
        wav = f'{A}/bites/{name}.wav'
        ff('-ss', f'{bite:.3f}', '-t', f'{BITE:.3f}', '-i', src, '-vn', '-ac', '2', '-ar', str(SR),
           '-af', f'afade=t=in:d=0.12,afade=t=out:st={BITE - 0.45:.2f}:d=0.45', wav)
        x = audio(wav, 0, BITE); hop = 400; n = len(x) // hop
        rms = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1))
        levels[name] = [round(float(v), 3) for v in np.clip((20 * np.log10(rms + 1e-6) + 42) / 36, 0, 1)]
    names = [name]
    for j, frac in enumerate((0.2, 0.62)):        # two extra silent clips for the rush, away from the bite
        t = dur * frac
        if abs(t - bite) < 6: t = min(dur - 5, t + 8)
        rn = f'r{k + 1}{"ab"[j]}'; frames(f'{A}/clips/{rn}', src, t, 4.0, sc); names.append(rn)
    rush.append(names)
    if vert: vertical.extend(names)
    mine = []
    for frac in (0.12, 0.42, 0.72):
        out = f'{A}/stills/s{si:02d}.jpg'
        if not os.path.exists(out):
            ff('-ss', f'{dur * frac:.2f}', '-i', src, '-frames:v', '1', '-vf',
               ('scale=-2:760' if vert else 'scale=760:-2') + ':flags=lanczos,format=yuvj420p', '-q:v', '2', out)
        if vert: vertical_stills.append(si)
        mine.append(si); si += 1
    stills_by_work.append(mine)
    works.append({'clip': name, 'vert': vert, 'sound': sound, 'len': mmss(dur), 'bite': bite})
    print(f'work {k + 1}: {os.path.basename(src)} {"9:16" if vert else "16:9"} {mmss(dur)}, sound bite at {bite:.2f} s')
json.dump({'lead': LEAD, 'bite': BITE, 'levels': levels}, open(f'{A}/bites/levels.json', 'w'))

# ------------------------------------------------------------------ the logo animation
logo = CFG['brand'].get('logoAnimation') or CFG['brand'].get('logo')
if not logo: sys.exit('promo.json: brand.logoAnimation (alpha .mov/.webm) or brand.logo (transparent PNG) is required')
logo = os.path.expanduser(logo)
L = f'{A}/logo'
dec = ['-c:v', 'libvpx-vp9'] if logo.endswith('.webm') else []        # the native VP9 decoder drops alpha
if not (os.path.isdir(L) and os.listdir(L)):
    os.makedirs(L, exist_ok=True)
    lw, lh, ldur, _ = probe(logo) if not logo.lower().endswith(('.png', '.webp')) else (*map(int, subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', logo], capture_output=True, text=True).stdout.strip().split(',')[:2]), 0, False)
    last = ['-sseof', '-0.1'] if ldur else []
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', *dec, *last, '-i', logo, '-frames:v', '1', '-vf', 'format=rgba',
                          '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(lh, lw, 4)[:, :, 3]
    ys, xs = np.where(a > 24)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    bw, bh, cx, cy = x1 - x0 + 1, y1 - y0 + 1, (x0 + x1) / 2, (y0 + y1) / 2
    S = int(max(bw / 0.514, bh / 0.598)) // 2 * 2                # same framing as the K reveal it was designed on
    pad = S
    vf = f'format=rgba,pad=iw+{2 * pad}:ih+{2 * pad}:{pad}:{pad}:color=black@0,crop={S}:{S}:{int(cx + pad - S / 2)}:{int(cy + pad - S / 2)},scale=1000:1000:flags=lanczos'
    ff(*dec, '-i', logo, '-vf', (vf + ',fps=60') if ldur else vf, *([] if ldur else ['-frames:v', '1']), f'{L}/%04d.png')
    json.dump({'w': round(bw * 1000 / S, 1), 'h': round(bh * 1000 / S, 1), 'cx': 500, 'cy': 500}, open(f'{L}/mark.json', 'w'))
    print(f'logo: mark {bw}x{bh} px, {len(os.listdir(L)) - 1} frames')
mark = json.load(open(f'{L}/mark.json'))
# its sound: brand.logoSfx, else the generate-logo sidecar next to the animation (<name>-sfx.wav)
sfx = CFG['brand'].get('logoSfx')
if not sfx:
    base = os.path.basename(logo).split('-alpha')[0]
    cand = os.path.join(os.path.dirname(logo), base + '-sfx.wav')
    sfx = cand if os.path.exists(cand) else None
if sfx: ff('-i', os.path.expanduser(sfx), '-ar', str(SR), '-ac', '2', f'{A}/logo-sfx.wav')
elif os.path.exists(f'{A}/logo-sfx.wav'): os.remove(f'{A}/logo-sfx.wav')

# ------------------------------------------------------------------ manifest
order = [s for i in range(3) for ws in stills_by_work for s in ws[i:i + 1]]
man = {
    'clips': {d: len(os.listdir(f'{A}/clips/{d}')) for d in sorted(os.listdir(f'{A}/clips')) if os.path.isdir(f'{A}/clips/{d}')},
    'vertical': vertical, 'stills': sorted(os.listdir(f'{A}/stills')), 'vertical_stills': vertical_stills,
    'ring': order[:10], 'rush': [n for i in range(3) for names in rush for n in names[i:i + 1]],
    'works': works, 'logo': {'frames': len([f for f in os.listdir(L) if f.endswith('.png')]), **mark},
    'logoSfx': os.path.exists(f'{A}/logo-sfx.wav'),
}
json.dump(man, open(f'{A}/manifest.json', 'w'), indent=1)
print('assets ok:', len(works), 'works,', len(man['stills']), 'stills,', man['logo']['frames'], 'logo frames')
