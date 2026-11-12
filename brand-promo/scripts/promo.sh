#!/bin/bash
# brand-promo: render a dark kinetic studio showreel from <project>/promo.json.
#
# usage: promo.sh <project>/promo.json [--preview] [--from STAGE] [--jobs N]
#   stages, in order: assets voices plan music mix render encode
#   --preview   cut the assets, plan the timings and render a 12-still contact sheet (no video, a few seconds)
#   --from S    start at stage S (earlier results are kept, e.g. --from mix after changing an effect)
#   --jobs N    parallel Chrome renderers (default 2)
# Output: <project>/out/<name>-1080p60.mp4 (+ -contact.png). Needs ffmpeg, Node 22+, Chrome, and a Python with
# numpy + scipy ($PROMO_PY); narration needs VoxCPM2 ($VOX_PY), otherwise the promo is made without a narrator.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
die() { echo "error: $*" >&2; exit 1; }
[ $# -ge 1 ] || { sed -n '2,10p' "$0"; exit 1; }
CFG=$(cd "$(dirname "$1")" && pwd)/$(basename "$1"); shift
[ -f "$CFG" ] || die "config not found: $CFG"
P=$(dirname "$CFG")
PREVIEW=0; FROM=assets; JOBS=2
while [ $# -gt 0 ]; do
  case $1 in --preview) PREVIEW=1; shift ;; --from) FROM=$2; shift 2 ;; --jobs) JOBS=$2; shift 2 ;; *) die "unknown option $1" ;; esac
done
for py in "${PROMO_PY:-}" "${VOX_PY:-}" "$HOME/.claude/skills/khmer-2d-animation/.venv-vox/bin/python" "$HOME/voxcpm-env/bin/python" python3; do
  [ -n "$py" ] && command -v "$py" >/dev/null 2>&1 && "$py" -c 'import numpy, scipy' 2>/dev/null && { PY=$py; break; }
done
[ -n "${PY:-}" ] || die "need a Python with numpy and scipy: pip install numpy scipy (or set PROMO_PY)"
command -v ffmpeg >/dev/null || die "ffmpeg is required"
command -v node >/dev/null || die "node is required (v22+)"
NAME=$("$PY" -c 'import json,sys;print(json.load(open(sys.argv[1])).get("name","promo"))' "$CFG")
mkdir -p "$P/build" "$P/out"
STAGES=(assets voices plan music mix render encode)
run=0
for st in "${STAGES[@]}"; do
  [ "$st" = "$FROM" ] && run=1
  [ $run = 1 ] || continue
  if [ $PREVIEW = 1 ] && [[ $st =~ ^(voices|music|mix|encode)$ ]]; then continue; fi
  echo "== $st"
  case $st in
    assets) "$PY" "$HERE/assets.py" "$CFG" ;;
    voices) "$PY" "$HERE/voices.py" "$CFG" ;;
    plan)   "$PY" "$HERE/plan.py" "$CFG" ;;
    music)  "$PY" "$HERE/music.py" "$CFG" ;;
    mix)    "$PY" "$HERE/audio.py" "$CFG" ;;
    render)
      if [ $PREVIEW = 1 ]; then
        rm -rf "${P:?}/build/stills"
        DUR=$("$PY" -c 'import json,sys;print(json.load(open(sys.argv[1]))["DUR"])' "$P/build/tm.json")
        TIMES=$("$PY" -c 'import json,sys;t=json.load(open(sys.argv[1]));B=lambda n:0.075+n*1.875
s=[1.3,5.0,8.4]+[B(5+3*k)+3.2 for k in range(t["N"])]+[t["next"][1]+0.3,t["wva"][-1]+0.6,t["HIT"]+2.4,t["DUR"]-0.3]
print(",".join(f"{x:.2f}" for x in s[:12]))' "$P/build/tm.json")
        node "$HERE/render.mjs" --project "$P" --out "$P/build/stills" --times "$TIMES"
        ffmpeg -nostdin -v error -y -pattern_type glob -i "$P/build/stills/t_*.png" -vf "scale=640:-1,tile=4x3:padding=4:color=black" -frames:v 1 "$P/out/$NAME-preview.png"
        echo "preview -> $P/out/$NAME-preview.png"
      else
        rm -rf "${P:?}/build/frames"; mkdir -p "$P/build/frames"
        TOTAL=$("$PY" -c 'import json,sys;print(round(json.load(open(sys.argv[1]))["DUR"]*60))' "$P/build/tm.json")
        STEP=$(( (TOTAL + JOBS - 1) / JOBS )); pids=()
        for j in $(seq 0 $((JOBS - 1))); do
          a=$((j * STEP)); b=$(( a + STEP < TOTAL ? a + STEP : TOTAL ))
          node "$HERE/render.mjs" --project "$P" --out "$P/build/frames" --from $a --to $b > "$P/build/render-$j.log" 2>&1 & pids+=($!)
        done
        for p in "${pids[@]}"; do wait "$p" || die "a renderer failed: see $P/build/render-*.log"; done
        n=$(ls "$P/build/frames" | wc -l | tr -d ' '); [ "$n" = "$TOTAL" ] || die "rendered $n of $TOTAL frames"
      fi ;;
    encode)
      ffmpeg -nostdin -v error -y -framerate 60 -start_number 0 -i "$P/build/frames/f_%05d.png" -i "$P/build/mix.wav" \
        -vf "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p" \
        -c:v libx264 -preset slow -crf 17 -profile:v high -tune animation -g 60 -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
        -c:a aac -b:a 256k -shortest -movflags +faststart "$P/out/$NAME-1080p60.mp4"
      ffmpeg -nostdin -v error -y -i "$P/out/$NAME-1080p60.mp4" -vf "fps=1,scale=384:-1,tile=10x6:padding=3:color=black" -frames:v 1 "$P/out/$NAME-contact.png"
      ffprobe -v error -show_entries format=duration,size -of compact "$P/out/$NAME-1080p60.mp4"
      echo "done -> $P/out/$NAME-1080p60.mp4" ;;
  esac
done
