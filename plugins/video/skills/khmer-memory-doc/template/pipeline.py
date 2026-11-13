"""Finish the film unattended (ASR scores are cached per clip in build/asr_scores.jsonl): ASR (reusing partial scores), reseed weak lines once, render, web, docs, backup.
Run detached:  VOXCPM_MPS_DTYPE=bfloat16 nohup .venv/bin/python pipeline.py > build/pipeline.log 2>&1 &"""
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
PY = os.path.join(ROOT, ".venv", "bin", "python")
THR = 0.78


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def run(args, **kw):
    log("$", " ".join(args))
    subprocess.run(args, check=True, **kw)


def asr_score(keys):
    """Score the current wav of each key; returns {key: (score, hyp)}."""
    from narration import N
    from narrate import vox_python, wav_for
    from khnum import speak
    jobs = [{"id": k, "wav": wav_for(k), "text": speak(N[k][0])} for k in keys if os.path.exists(wav_for(k))]
    if not jobs:
        return {}
    jp, op = "build/asr_jobs_p.json", "build/asr_out_p.json"
    json.dump(jobs, open(jp, "w"), ensure_ascii=False)
    with open("build/asr_progress_p.log", "w") as lf:
        subprocess.run([vox_python(), "engine/asr_check.py", jp, op], check=True, stdout=lf, stderr=subprocess.DEVNULL)
    res = {r["id"]: (r["score"], r["hyp"]) for r in json.load(open(op))}
    with open(SCORES, "a") as f:   # remember each score against the exact clip it was measured on
        for j in jobs:
            if j["id"] in res:
                f.write(json.dumps({"id": j["id"], "wav": os.path.basename(j["wav"]), "score": res[j["id"]][0],
                                    "hyp": res[j["id"]][1]}, ensure_ascii=False) + "\n")
    return res


SCORES = "build/asr_scores.jsonl"


def known_scores():
    """Scores of clips that still exist and are still the current take of their line."""
    from narrate import wav_for
    from narration import N
    out = {}
    if os.path.exists(SCORES):
        for ln in open(SCORES):
            r = json.loads(ln)
            if r["id"] in N and os.path.basename(wav_for(r["id"])) == r["wav"]:
                out[r["id"]] = (r["score"], r["hyp"])
    return out


def main():
    from narration import N
    from narrate import SEEDS_FILE, seeds
    # 0. synthesise any missing lines (edited lines get new clips)
    run([PY, "make.py", "narrate"])
    # 1. ASR: reuse the scores already logged, score the rest
    scores = known_scores()
    rest = [k for k in N if k not in scores]
    log("ASR: %d reused, scoring %d" % (len(scores), len(rest)))
    scores.update(asr_score(rest))

    # 2. one reseed round for weak lines; keep the better take
    low = [k for k in N if scores.get(k, (0,))[0] < THR]
    log("low lines:", [(k, round(scores[k][0], 3)) for k in low])
    if low:
        old = seeds()
        sd = dict(old)
        for k in low:
            sd[k] = sd.get(k, 7) + 101
        json.dump(sd, open(SEEDS_FILE, "w"), indent=1)
        run([PY, "make.py", "narrate"])
        new = asr_score(low)
        sd = seeds()
        for k in low:
            if new.get(k, (0,))[0] >= scores[k][0]:
                scores[k] = new[k]
                log("  %s improved -> %.3f" % (k, new[k][0]))
            else:
                sd[k] = old.get(k, 7)
                log("  %s kept original (%.3f vs new %.3f)" % (k, scores[k][0], new.get(k, (0,))[0]))
        json.dump(sd, open(SEEDS_FILE, "w"), indent=1)

    # report
    vals = [scores[k][0] for k in N if k in scores]
    md = ["# Narration ASR round-trip check", "",
          "Khmer Whisper (seanghay/whisper-small-khmer-v2) transcribes each line; score = character similarity.", "",
          "Lines: %d · mean %.3f · below %.2f: %d" % (len(vals), sum(vals) / len(vals), THR,
                                                     sum(v < THR for v in vals)), "",
          "| line | score | heard |", "|---|---|---|"]
    for k in sorted(scores, key=lambda k: scores[k][0]):
        md.append("| %s | %.3f | %s |" % (k, scores[k][0], scores[k][1].replace("|", "/")))
    open("docs/asr_report.md", "w").write("\n".join(md))
    log("ASR mean %.3f, low after reseed: %s" % (sum(vals) / len(vals), [k for k in N if scores[k][0] < THR]))

    # 3. render (subs + mix + picture + mux), web copy, docs
    env = dict(os.environ, WORKERS=os.environ.get("WORKERS", "5"))
    run([PY, "make.py", "all"], env=env)
    run([PY, "make.py", "web"])
    run([PY, "make.py", "docs"])

    # 4. backup next to the earlier films
    name = json.load(open("project.json"))["name"]
    dst = os.path.expanduser("~/Movies/khmer_history_docs")
    ddir = os.path.join(dst, name.replace("_doc", "") + "_docs")
    os.makedirs(ddir, exist_ok=True)
    for f in ("film/%s.mp4" % name, "film/%s_web.mp4" % name, "subtitles/%s_en.srt" % name,
              "subtitles/%s_km.srt" % name):
        if os.path.exists(f):
            shutil.copy(f, dst)
    for f in os.listdir("docs"):
        if f.endswith(".md"):
            shutil.copy(os.path.join("docs", f), os.path.join(ddir, f))
    log("PIPELINE DONE")


if __name__ == "__main__":
    main()
