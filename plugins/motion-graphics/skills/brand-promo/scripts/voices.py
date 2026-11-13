"""Narration for the promo with VoxCPM2 (local; Apple MPS or CUDA). Writes <project>/build/vox/<id>.wav.

python voices.py <project>/promo.json        (needs a Python with `voxcpm` installed: $VOX_PY, see find_vox_python)

Lines (promo.json voice.lines) and where they play:
  intro -> r01 (0.5 s)   ring -> n02 (3.7 s)   title -> r04 (on the title drop)   works[k] -> n1{k+1} (as spotlight k opens)
  next -> r08 (the break: its LAST word lands on the big second word)   rush -> r09 (its first three phrases land on
  the three rush words)   end -> r10 (as the logo's name appears)
The voice is designed once from voice.design + voice.sample (or cloned from voice.ref) and every line is cloned from it,
so the whole read sounds like one person. Existing clips are kept: delete a .wav to redo that line (or the voice).
"""
import json, os, subprocess, sys

CFG_PATH = os.path.abspath(sys.argv[1])
P = os.path.dirname(CFG_PATH)
CFG = json.load(open(CFG_PATH))
HERE = os.path.dirname(os.path.abspath(__file__))
V = CFG.get('voice')
if not V or not V.get('lines'):
    print('no voice.lines in promo.json: the promo will have no narration'); sys.exit(0)

def find_vox_python():
    for p in (os.environ.get('VOX_PY'), os.path.expanduser('~/.claude/skills/khmer-2d-animation/.venv-vox/bin/python'),
              os.path.expanduser('~/voxcpm-env/bin/python')):
        if p and os.path.exists(p) and subprocess.run([p, '-c', 'import voxcpm, torch'], capture_output=True).returncode == 0:
            return p
    sys.exit('VoxCPM2 not found. Install once:  python3.12 -m venv ~/voxcpm-env && ~/voxcpm-env/bin/pip install voxcpm soundfile\n'
             '(or set VOX_PY to a python that has voxcpm), or put your own recordings in build/vox/<id>.wav')

out = f'{P}/build/vox'; os.makedirs(out, exist_ok=True)
L = V['lines']
ids = {'r01': L.get('intro'), 'n02': L.get('ring'), 'r04': L.get('title'), 'r08': L.get('next'), 'r09': L.get('rush'), 'r10': L.get('end')}
for k, s in enumerate(L.get('works', [])): ids[f'n1{k + 1}'] = s
ids = {k: v for k, v in ids.items() if v}
ref = os.path.expanduser(V['ref']) if V.get('ref') else f'{out}/narrator.wav'
sample = V.get('refText') if V.get('ref') else V.get('sample', 'Every great story starts with a simple idea, and we love helping it come to life.')
jobs = {'voices': [] if V.get('ref') else [{'voice_id': 'narrator', 'design': V.get('design', 'A warm, confident narrator for a modern brand video, clear and friendly'),
                                             'sample_text': sample, 'out_wav': ref, 'seed': V.get('seed', 4242)}],
        'lines': [{'id': k, 'text': t, 'ref_wav': ref, 'ref_text': sample, 'out_wav': f'{out}/{k}.wav', 'seed': V.get('seeds', {}).get(k, 7),
                   'clone_mode': 'both'} for k, t in ids.items()]}
json.dump(jobs, open(f'{out}/jobs.json', 'w'), ensure_ascii=False, indent=1)
todo = sum(not os.path.exists(j['out_wav']) for j in jobs['voices'] + jobs['lines'])
print(f'{len(ids)} lines, {todo} to synthesise (model load ~2 min, then 10-60 s per line)')
if todo:
    log = f'{out}/tts.log'
    with open(log, 'w') as lf:                       # progress bars go to the log, finished lines to the screen
        p = subprocess.Popen([find_vox_python(), f'{HERE}/tts_vox.py', f'{out}/jobs.json'], stdout=subprocess.PIPE, stderr=lf, text=True)
        for line in p.stdout:
            if line.startswith('{'): print(line.rstrip(), flush=True)
    if p.wait() != 0:
        sys.exit('VoxCPM2 failed, see ' + log + ':\n' + ''.join(open(log).readlines()[-15:]))
