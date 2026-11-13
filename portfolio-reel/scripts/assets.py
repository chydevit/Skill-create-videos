"""Prepare the reel's media -> <project>/assets/ + assets/manifest.json

python assets.py <project>/promo.json

- avatar: a portrait photo (or a still from a video), cropped to a square. Give "crop": [x, y, size] in pixels for the
  face, or the centre square (a little above the middle) is used. -> assets/avatar.jpg (900 x 900)
- logo (optional): the picture inside the profile card's circle; the avatar is used when it is missing.
- sections[].clips[]: each an image or a video ({"file": ..., "at": seconds}). A video becomes 30 fps JPEG frames for
  "seconds" s (default 5.5) from "at" (default 25 % into it), scaled so the long side is 720 px; an image is one JPEG.
Paths are relative to the project folder.
"""
import json, os, shutil, subprocess, sys

CFG_PATH = os.path.abspath(sys.argv[1])
P = os.path.dirname(CFG_PATH)
CFG = json.load(open(CFG_PATH))
A = f'{P}/assets'
VIDEO = {'.mp4', '.mov', '.m4v', '.webm', '.mkv', '.avi'}


def resolve(p):
    p = os.path.expanduser(p)
    return p if os.path.isabs(p) else os.path.join(P, p)


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height:format=duration',
                          '-of', 'json', path], capture_output=True, text=True).stdout
    js = json.loads(out or '{}'); st = (js.get('streams') or [{}])[0]
    return st.get('width', 0), st.get('height', 0), float(js.get('format', {}).get('duration') or 0)


def ff(*args):
    r = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit('ffmpeg failed: ' + r.stderr.strip()[:400])


def entry(item):
    return (item, {}) if isinstance(item, str) else (item['file'], item)


shutil.rmtree(A, ignore_errors=True)
os.makedirs(f'{A}/clips', exist_ok=True)
man = {'sections': []}

# ---------------------------------------------------------------- avatar and logo
if CFG.get('avatar'):
    f, opt = entry(CFG['avatar'])
    src = resolve(f)
    w, h, dur = probe(src)
    pre = ['-ss', f"{opt.get('at', dur * 0.3):.3f}"] if os.path.splitext(src)[1].lower() in VIDEO else []
    if opt.get('crop'):
        x, y, s = opt['crop']
    else:
        s = min(w, h); x = (w - s) // 2; y = max(0, int((h - s) * 0.35))
    ff(*pre, '-i', src, '-frames:v', '1', '-vf', f'crop={s}:{s}:{x}:{y},scale=900:900', '-q:v', '2', f'{A}/avatar.jpg')
    man['avatar'] = 'avatar.jpg'
if CFG.get('logo'):
    src = resolve(entry(CFG['logo'])[0])
    ff('-i', src, '-frames:v', '1', '-vf', "scale='min(800,iw)':-2", f'{A}/logo.png')
    man['logo'] = 'logo.png'

# ---------------------------------------------------------------- section clips
for k, sec in enumerate(CFG.get('sections', [])):
    clips = []
    for i, item in enumerate(sec.get('clips', [])[:3]):
        f, opt = entry(item)
        src = resolve(f)
        if not os.path.exists(src):
            raise SystemExit(f'clip not found: {src}')
        cid = f's{k}c{i}'
        vf = "scale='if(gt(iw,ih),720,-2)':'if(gt(iw,ih),-2,720)'"
        if os.path.splitext(src)[1].lower() in VIDEO:
            _, _, dur = probe(src)
            secs = float(opt.get('seconds', 5.5))
            at = float(opt.get('at', max(0.0, min(dur * 0.25, dur - secs))))
            os.makedirs(f'{A}/clips/{cid}', exist_ok=True)
            ff('-ss', f'{at:.3f}', '-t', f'{secs:.3f}', '-i', src, '-an', '-vf', f'fps=30,{vf}', '-q:v', '3', f'{A}/clips/{cid}/%04d.jpg')
            n = len(os.listdir(f'{A}/clips/{cid}'))
            w, h, _ = probe(f'{A}/clips/{cid}/0001.jpg')
            clips.append({'id': cid, 'kind': 'video', 'dir': f'clips/{cid}', 'n': n, 'w': w, 'h': h, 'from': os.path.basename(src)})
        else:
            ff('-i', src, '-frames:v', '1', '-vf', "scale='if(gt(iw,ih),min(1280,iw),-2)':'if(gt(iw,ih),-2,min(1280,ih))'", '-q:v', '2', f'{A}/clips/{cid}.jpg')
            w, h, _ = probe(f'{A}/clips/{cid}.jpg')
            clips.append({'id': cid, 'kind': 'image', 'src': f'clips/{cid}.jpg', 'w': w, 'h': h, 'from': os.path.basename(src)})
    man['sections'].append({'title': sec.get('title', ''), 'clips': clips})

json.dump(man, open(f'{A}/manifest.json', 'w'), indent=1)
n_clips = sum(len(s['clips']) for s in man['sections'])
print(f"{len(man['sections'])} sections, {n_clips} clips" + (', avatar' if 'avatar' in man else ' (no avatar: a plain disc)') +
      (', logo' if 'logo' in man else ''))
