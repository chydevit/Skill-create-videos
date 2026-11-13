#!/bin/bash
# saas-promo: render a kinetic SaaS / startup promo from <project>/promo.json: ~11 s, or ~50 s with "chapters".
#
# usage: promo.sh <project>/promo.json [--preview] [--from STAGE] [--jobs N]
#   stages, in order: assets plan render mix encode
#   --preview   prepare the pictures and render a 12-still contact sheet (no video, about 10 s)
#   --from S    start at stage S (earlier results are kept, e.g. --from mix after changing a sound: no re-render)
#   --jobs N    parallel Chrome renderers (default 3)
# Output: <project>/out/<name>-1080p60.mp4 (+ -contact.png). Needs ffmpeg, Node 22+, Chrome, and a Python with
# numpy + scipy ($PROMO_PY).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
die() { echo "error: $*" >&2; exit 1; }
[ $# -ge 1 ] || { sed -n '2,10p' "$0"; exit 1; }
CFG=$(cd "$(dirname "$1")" && pwd)/$(basename "$1"); shift
[ -f "$CFG" ] || die "config not found: $CFG"
P=$(dirname "$CFG")
PREVIEW=0; FROM=assets; JOBS=3
while [ $# -gt 0 ]; do
  case $1 in --preview) PREVIEW=1; shift ;; --from) FROM=$2; shift 2 ;; --jobs) JOBS=$2; shift 2 ;; *) die "unknown option $1" ;; esac
done
for py in "${PROMO_PY:-}" "$HOME/.claude/skills/khmer-2d-animation/.venv-vox/bin/python" "$HOME/voxcpm-env/bin/python" python3; do
  [ -n "$py" ] && command -v "$py" >/dev/null 2>&1 && "$py" -c 'import numpy, scipy' 2>/dev/null && { PY=$py; break; }
done
[ -n "${PY:-}" ] || die "need a Python with numpy and scipy: pip install numpy scipy (or set PROMO_PY)"
command -v ffmpeg >/dev/null || die "ffmpeg is required"
command -v node >/dev/null || die "node is required (v22+)"
NAME=$("$PY" -c 'import json,sys;print(json.load(open(sys.argv[1])).get("name","saas-promo"))' "$CFG")
mkdir -p "$P/build" "$P/out"
STAGES=(assets plan render mix encode)
run=0
for st in "${STAGES[@]}"; do
  [ "$st" = "$FROM" ] && run=1
  [ $run = 1 ] || continue
  if [ $PREVIEW = 1 ] && [[ $st =~ ^(plan|mix|encode)$ ]]; then continue; fi
  echo "== $st"
  case $st in
    assets) "$PY" "$HERE/assets.py" "$CFG" ;;
    plan)   node "$HERE/render.mjs" --project "$P" --cues "$P/build/cues.json" ;;
    mix)    "$PY" "$HERE/audio.py" "$CFG" ;;
    render)
      if [ $PREVIEW = 1 ]; then
        rm -rf "${P:?}/build/stills"
        node "$HERE/render.mjs" --project "$P" --out "$P/build/stills" --times auto
        ROWS=$(( ($(ls "$P/build/stills" | wc -l) + 3) / 4 ))
        ffmpeg -nostdin -v error -y -pattern_type glob -i "$P/build/stills/t_*.png" -vf "scale=640:-1,tile=4x$ROWS:padding=4:color=black" -frames:v 1 "$P/out/$NAME-preview.png"
        echo "preview -> $P/out/$NAME-preview.png"
      else
        rm -rf "${P:?}/build/frames"; mkdir -p "$P/build/frames"
        TOTAL=$("$PY" -c 'import json,sys;print(round(json.load(open(sys.argv[1]))["dur"]*60))' "$P/build/cues.json")
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
        -c:v libx264 -preset slow -crf 16 -profile:v high -g 60 -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
        -c:a aac -b:a 256k -shortest -movflags +faststart "$P/out/$NAME-1080p60.mp4"
      CFPS=$("$PY" -c 'import json,sys;print(round(30/json.load(open(sys.argv[1]))["dur"],4))' "$P/build/cues.json")   # ~30 frames whatever the length
      ffmpeg -nostdin -v error -y -i "$P/out/$NAME-1080p60.mp4" -vf "fps=$CFPS,scale=384:-1,tile=6x5:padding=3:color=black" -frames:v 1 "$P/out/$NAME-contact.png"
      ffprobe -v error -show_entries format=duration,size -of compact "$P/out/$NAME-1080p60.mp4"
      echo "done -> $P/out/$NAME-1080p60.mp4" ;;
  esac
done
