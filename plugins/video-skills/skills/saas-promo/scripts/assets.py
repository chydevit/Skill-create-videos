"""Prepare the promo's pictures -> <project>/assets/cards/cNN.(jpg|png) + assets/manifest.json

python assets.py <project>/promo.json

"cards" in promo.json is a list of image or video files (globs work, paths are relative to the project folder).
A video gives one still: at "at" seconds when the entry is {"file": ..., "at": 12.5}, otherwise at 30 % of its length.
{"file": ..., "wall": false} keeps a picture out of the bento wall (it only flies in the 3D swirl).
{"file": ..., "tag": "x"} files a picture under a chapter ("chapters": [{"tag": "x", ...}]): that chapter shows it first.
"music" (optional): the song is measured here (tempo, and the drop = the biggest lift in energy, snapped to a kick),
unless promo.json gives "bpm" and "musicDrop" (song seconds). The video starts "musicStart" s into the song, or by
default just early enough that its first cut lands on the drop. -> manifest "music": {start, bpm, drop}.
"hero", "backdrop" and "logo" (all optional) are copied the same way. Pictures are scaled to at most 1400 px wide.
"""
import glob, json, os, shutil, subprocess, sys

CFG_PATH = os.path.abspath(sys.argv[1])
P = os.path.dirname(CFG_PATH)
CFG = json.load(open(CFG_PATH))
A = f'{P}/assets'
VIDEO = {'.mp4', '.mov', '.m4v', '.webm', '.mkv', '.avi'}
IMAGE = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', '.tif', '.tiff', '.heic'}


def resolve(p):
    p = os.path.expanduser(p)
    return p if os.path.isabs(p) else os.path.join(P, p)


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height:format=duration',
                          '-of', 'json', path], capture_output=True, text=True).stdout
    js = json.loads(out or '{}')
    st = (js.get('streams') or [{}])[0]
    return st.get('width', 0), st.get('height', 0), float(js.get('format', {}).get('duration') or 0)


def still(src, dst, at=None, maxw=1400):
    ext = os.path.splitext(src)[1].lower()
    vf = f"scale='min({maxw},iw)':-2"
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y']
    if ext in VIDEO:
        dur = probe(src)[2]
        cmd += ['-ss', f'{(at if at is not None else dur * 0.3):.3f}']
    cmd += ['-i', src, '-frames:v', '1', '-vf', vf]
    if dst.endswith('.jpg'):
        cmd += ['-q:v', '3']
    r = subprocess.run(cmd + [dst], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(dst):
        if shutil.which('sips') and ext in IMAGE:           # e.g. HEIC on macOS
            fmt = 'png' if dst.endswith('.png') else 'jpeg'
            subprocess.run(['sips', '-s', 'format', fmt, '-Z', str(maxw), src, '--out', dst], capture_output=True)
    if not os.path.exists(dst):
        raise SystemExit(f'cannot read {src}: {r.stderr.strip()[:300]}')
    w, h, _ = probe(dst)
    return w, h


entries = []
for item in CFG.get('cards', []):
    at, wall, tag = None, True, None
    if isinstance(item, dict):
        at, wall, tag, item = item.get('at'), item.get('wall', True), item.get('tag'), item['file']
    paths = sorted(glob.glob(resolve(item))) or [resolve(item)]
    for p in paths:
        ext = os.path.splitext(p)[1].lower()
        if not os.path.exists(p):
            print(f'warning: no such card file: {p}', file=sys.stderr)
        elif ext in VIDEO | IMAGE:
            entries.append((p, at, wall, tag))

shutil.rmtree(f'{A}/cards', ignore_errors=True)
os.makedirs(f'{A}/cards', exist_ok=True)
cards = []
for i, (p, at, wall, tag) in enumerate(entries[:40]):
    ext = '.png' if p.lower().endswith('.png') else '.jpg'
    rel = f'cards/c{i:02d}{ext}'
    w, h = still(p, f'{A}/{rel}', at)
    cards.append({'src': rel, 'w': w, 'h': h, 'from': os.path.basename(p), **({} if wall else {'wall': False}), **({'tag': tag} if tag else {})})

man = {'cards': cards}
for key in ('hero', 'backdrop', 'logo'):
    v = CFG.get(key)
    if not v:
        continue
    src = resolve(v)
    if not os.path.exists(src):
        raise SystemExit(f'{key} not found: {src}')
    ext = '.png' if (key == 'logo' or src.lower().endswith('.png')) else '.jpg'
    still(src, f'{A}/{key}{ext}', maxw=1200 if key == 'logo' else 2400)
    man[key] = f'{key}{ext}'



def analyse_music(src, drop=None):
    """Tempo (bpm) and the drop (song seconds) of a track: the drop is the biggest 4 s lift in loudness, snapped to the
    first strong kick near it; the tempo is a comb fit of the onset curve over the 30 s after the drop."""
    import numpy as np
    from scipy import signal
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', src, '-vn', '-ac', '1', '-ar', '22050', '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    sr, hop = 22050, 256; fps = sr / hop
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    f, _, Z = signal.stft(x, sr, nperseg=1024, noverlap=1024 - hop)
    mag = np.log1p(np.abs(Z) * 100)
    flux = np.maximum(0, np.diff(mag, axis=1)).sum(0)
    kick = np.maximum(0, np.diff(mag[f < 150], axis=1)).sum(0)
    if drop is None:
        e = np.log10(np.sqrt(np.convolve(x ** 2, np.ones(sr // 4) / (sr // 4), 'same'))[::hop][:len(flux)] + 1e-6)
        w = int(4 * fps); cs = np.concatenate([[0], np.cumsum(e)])
        i = np.arange(w, len(e) - w); lift = (cs[i + w] - cs[i]) / w - (cs[i] - cs[i - w]) / w
        c = int(i[np.argmax(lift)]); a0 = max(0, c - int(0.5 * fps)); win = kick[a0:c + int(1.2 * fps)]
        pk = signal.find_peaks(win, distance=int(0.2 * fps))[0]
        drop = (a0 + (pk[np.argmax(win[pk])] if len(pk) else c - a0)) / fps      # the strongest kick at the lift
    a = int(drop * fps)
    env = flux / (flux.std() + 1e-9) + kick / (kick.std() + 1e-9)
    seg = env[a:a + int(60 * fps)]
    def score(b):          # comb fit with a free phase: the best-aligned grid of beats at this tempo
        per = 60 / b * fps; ks = np.arange(0, (len(seg) - 4) / per - 1)
        ph = np.arange(0, per, 1.0)
        idx = (ph[:, None] + ks[None, :] * per).astype(int)
        return seg[idx].mean(1).max()
    coarse = max(np.arange(80, 170, 0.1), key=score)
    bpm = max(np.arange(coarse - 0.15, coarse + 0.15, 0.005), key=score)
    return round(float(bpm), 2), round(float(drop), 3)

if CFG.get('music'):
    src = resolve(CFG['music'])
    if not os.path.exists(src):
        raise SystemExit(f'music not found: {src}')
    bpm, drop = CFG.get('bpm'), CFG.get('musicDrop')
    if bpm is None or drop is None:
        est_bpm, est_drop = analyse_music(src, drop)
        bpm, drop = bpm or est_bpm, drop if drop is not None else est_drop
    lead = 1.5 * 240 / bpm if CFG.get('chapters') else 3.3      # the first cut: after 1.5 bars (long mode) or at 3.3 s
    start = CFG.get('musicStart', round(max(0.0, drop - lead), 3))
    man['music'] = {'start': start, 'bpm': bpm, 'drop': drop}
    print(f'music: {bpm} bpm, drop at {drop} s, the video starts {start} s into the song')

json.dump(man, open(f'{A}/manifest.json', 'w'), indent=1)
extra = ', '.join(k for k in ('hero', 'backdrop', 'logo') if k in man)
print(f'{len(cards)} card pictures' + (f' + {extra}' if extra else '') +
      ('' if len(cards) >= 8 else f' (fewer than 8: built-in UI cards fill the rest)'))
