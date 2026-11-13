"""Write <project>/<title>.srt subtitles from build/timeline.json."""
import json
import os
import re
import sys

P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
tl = json.load(open(os.path.join(P, "build", "timeline.json")))


def ts(t):
    ms = int(round(t * 1000))
    return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)


subs = []
for s in tl["scenes"]:
    for e in s["events"]:
        if e["type"] == "speech":
            g = s["start"] + e["t"]
            subs.append([g, g + e["dur"] + 0.3, e["text"]])
subs.sort()
slug = re.sub(r"[^A-Za-z0-9]+", "_", tl.get("title", "episode")).strip("_") or "episode"
lang = tl.get("language", "english")
out = os.path.join(P, slug + ("" if lang == "english" else "_" + lang) + ".srt")
with open(out, "w") as f:
    for k, (a, b, text) in enumerate(subs):
        if k + 1 < len(subs):
            b = min(b, subs[k + 1][0] - 0.02)
        f.write("%d\n%s --> %s\n%s\n\n" % (k + 1, ts(a), ts(b), text))
print("wrote", out, len(subs), "cues")
