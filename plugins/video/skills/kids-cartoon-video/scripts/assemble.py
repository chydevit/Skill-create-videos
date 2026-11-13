"""Join the rendered scene segments with smooth transitions and add the audio."""
import json
import os
import subprocess

import re
import sys

PROJECT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
BUILD = os.path.join(PROJECT, "build")
tl = json.load(open(os.path.join(BUILD, "timeline.json")))
slug = re.sub(r"[^A-Za-z0-9]+", "_", tl.get("title", "episode")).strip("_") or "episode"
OUT = os.path.join(PROJECT, slug + ("" if tl.get("language", "english") == "english"
                                    else "_" + tl["language"]) + ".mp4")
X = tl["xfade"]
scenes = tl["scenes"]
# a playful mix of cartoon transitions
TRANS = ["circleopen", "wipeleft", "circleopen", "radial", "circleopen",
         "wiperight", "circleopen", "radial"]

cmd = ["ffmpeg", "-y", "-v", "error", "-stats"]
for i in range(len(scenes)):
    cmd += ["-i", os.path.join(BUILD, "segments", "seg%02d.mp4" % i)]
cmd += ["-i", os.path.join(BUILD, "final_audio.wav")]

parts = []
prev = "[0:v]"
for k in range(1, len(scenes)):
    out = "[v%d]" % k
    parts.append("%s[%d:v]xfade=transition=%s:duration=%.3f:offset=%.4f%s"
                 % (prev, k, "circleclose" if k == len(scenes) - 1 else TRANS[(k - 1) % len(TRANS)],
                    X, scenes[k]["start"], out))
    prev = out
# fade in from black at the very start and out at the very end
total = tl["total"]
parts.append("%sfade=t=in:st=0:d=0.6,fade=t=out:st=%.3f:d=1.2,format=yuv420p[vout]"
             % (prev, total - 1.2))
parts.append("[%d:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[aout]" % len(scenes))
cmd += ["-filter_complex", ";".join(parts), "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-r", "24",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        "-t", "%.3f" % total, OUT]
subprocess.run(cmd, check=True)
print("wrote", OUT)
