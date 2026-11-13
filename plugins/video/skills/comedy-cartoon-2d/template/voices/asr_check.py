"""Khmer Whisper QC: transcribe every dialogue clip and score it against the script (character similarity).
Run with the VoxCPM venv:  $VOX_PY voices/asr_check.py   -> prints a table, writes build/vox/asr.json
Low scores (< ~0.6) are worth re-rolling with a new seed in lines.json "seeds".
Compare takes:  $VOX_PY voices/asr_check.py <id> ...  -> scores build/vox/<id>.wav and every saved take
build/vox_keep/<id>.*.wav (e.g. <id>.s7.wav, <id>.s21.wav) side by side, to keep the best one."""
import difflib, glob, json, os, re, sys
import soundfile as sf, numpy as np
from transformers import pipeline

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(f"{P}/voices/lines.json"))
asr = pipeline("automatic-speech-recognition", model="seanghay/whisper-small-khmer-v2", device="mps")
norm = lambda s: re.sub(r"[\s​។!?,.()…\-]|[A-Za-z]", "", s)

def score(wav, line):
    x, sr = sf.read(wav, dtype="float32")
    if x.ndim > 1: x = x.mean(axis=1)
    if sr != 16000:
        n = int(len(x) * 16000 / sr); x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)
    heard = asr({"raw": x, "sampling_rate": 16000})["text"]
    ref = line[3] if len(line) > 3 and line[3] else line[1]
    return difflib.SequenceMatcher(None, norm(ref), norm(heard)).ratio(), heard

if len(sys.argv) > 1:  # compare the current clip and the saved takes of the given lines
    for lid in sys.argv[1:]:
        for wav in [f"{P}/build/vox/{lid}.wav"] + sorted(glob.glob(f"{P}/build/vox_keep/{lid}.*.wav")):
            if not os.path.exists(wav): continue
            s, heard = score(wav, d["lines"][lid])
            print(f"{os.path.relpath(wav, f'{P}/build'):24} {s:.2f}  {heard}", flush=True)
    sys.exit()

out = {}
for lid, line in d["lines"].items():
    wav = f"{P}/build/vox/{lid}.wav"
    if not os.path.exists(wav): continue
    s, heard = score(wav, line)
    out[lid] = {"score": round(s, 2), "heard": heard}
    print(f"{lid:4} {s:.2f}  {'LOW ' if s < 0.6 else '    '}{heard}", flush=True)
json.dump(out, open(f"{P}/build/vox/asr.json", "w"), ensure_ascii=False, indent=1)
