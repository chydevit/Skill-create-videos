#!/bin/bash
# brand-loop: a seamless looping background of glossy liquid blobs in your brand colours (Blender EEVEE).
#
# usage: loop.sh [options]
#   --name NAME        file prefix (default brand-loop)            --out DIR   output folder (default ./<name>)
#   --cool "c1,..,c5"  cool blob family, dark -> light            --warm "c1,c2,c3"  warm blob family
#   --paper "c1,c2"    backdrop centre/corner colours             --logo FILE  take --cool/--warm from a logo
#   --dur S            loop length (default 10)                   --fps N     (default 60)
#   --res WxH          3840x2160 (default) or 1920x1080           --jobs N    Blender processes (default 2)
#   --preview          six 960x540 stills on one sheet, about a minute (no video)
#   --keep-frames      keep the PNG frames after encoding (re-encode without re-rendering)
# Writes <name>-4k60-loop.mp4 (H.264), -loop-hevc10.mp4 (10-bit), -1080p60-loop.mp4, a still and a keyframe sheet.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
die() { echo "error: $*" >&2; exit 1; }
NAME=brand-loop; OUT=""; COOL=""; WARM=""; PAPER=""; LOGO=""; DUR=10; FPS=60; RES=3840x2160; JOBS=2; PREVIEW=0; KEEP=0
while [ $# -gt 0 ]; do
  case $1 in
    --name) NAME=$2; shift 2 ;; --out) OUT=$2; shift 2 ;; --cool) COOL=$2; shift 2 ;; --warm) WARM=$2; shift 2 ;;
    --paper) PAPER=$2; shift 2 ;; --logo) LOGO=$2; shift 2 ;; --dur) DUR=$2; shift 2 ;; --fps) FPS=$2; shift 2 ;;
    --res) RES=$2; shift 2 ;; --jobs) JOBS=$2; shift 2 ;; --preview) PREVIEW=1; shift ;; --keep-frames) KEEP=1; shift ;;
    -h|--help) sed -n '2,14p' "$0"; exit 0 ;; *) die "unknown option $1" ;;
  esac
done
command -v blender >/dev/null || [ -x /Applications/Blender.app/Contents/MacOS/Blender ] || die "Blender 4.2+ is required"
BL=$(command -v blender || echo /Applications/Blender.app/Contents/MacOS/Blender)
command -v ffmpeg >/dev/null || die "ffmpeg is required"
if [ -n "$LOGO" ] && [ -z "$COOL$WARM" ]; then
  line=$(python3 "$HERE/palette.py" "$LOGO" | tail -1); echo "palette from logo: $line"
  COOL=$(echo "$line" | sed -E 's/.*--cool "([^"]+)".*/\1/'); WARM=$(echo "$line" | sed -E 's/.*--warm "([^"]+)".*/\1/')
fi
OUT=${OUT:-$PWD/$NAME}; mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
LOOK=(--dur "$DUR" --fps "$FPS")
[ -n "$COOL" ] && LOOK+=(--cool "$COOL"); [ -n "$WARM" ] && LOOK+=(--warm "$WARM"); [ -n "$PAPER" ] && LOOK+=(--paper "$PAPER")
N=$(python3 -c "print(round($DUR*$FPS))")

if [ $PREVIEW = 1 ]; then
  T="$OUT/.preview"; rm -rf "${T:?}"; mkdir -p "$T"
  F=$(python3 -c "n=$N;print(','.join(str(round(n*k/6)) for k in range(6)))")
  "$BL" -b --factory-startup --python "$HERE/scene.py" -- --res 960x540 --samples 12 --mbres 0.003 "${LOOK[@]}" --out "$T" --frames "$F" 2>&1 | grep -E "STILL|Error" || true
  ffmpeg -nostdin -v error -y -pattern_type glob -i "$T/still_*.png" -vf "tile=3x2:padding=4:color=black" -frames:v 1 "$OUT/$NAME-preview.png"
  rm -rf "${T:?}"; echo "preview -> $OUT/$NAME-preview.png"; exit 0
fi

FR="$OUT/frames"; mkdir -p "$FR" "$OUT/logs"
pids=()
for j in $(seq 1 "$JOBS"); do
  "$BL" -b --factory-startup --python "$HERE/scene.py" -- --res "$RES" "${LOOK[@]}" --out "$FR" --range "0-$((N - 1))" > "$OUT/logs/render-$j.log" 2>&1 &
  pids+=($!); sleep 20                       # stagger so they pick different frames
done
for p in "${pids[@]}"; do wait "$p"; done
empty=$(find "$FR" -name 'f_*.png' -size 0 | wc -l | tr -d ' ')     # placeholders left by a killed process
if [ "$empty" != 0 ]; then
  find "$FR" -name 'f_*.png' -size 0 -delete
  "$BL" -b --factory-startup --python "$HERE/scene.py" -- --res "$RES" "${LOOK[@]}" --out "$FR" --range "0-$((N - 1))" > "$OUT/logs/render-fix.log" 2>&1
fi
n=$(ls "$FR"/f_*.png | wc -l | tr -d ' '); [ "$n" = "$N" ] || die "expected $N frames, found $n (see $OUT/logs)"

VF709="scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int"
TAGS=(-color_primaries bt709 -color_trc bt709 -colorspace bt709)
TAG=$([ "${RES%x*}" -ge 3840 ] && echo 4k || echo "${RES#*x}p")
ffmpeg -nostdin -v error -y -framerate "$FPS" -start_number 0 -i "$FR/f_%04d.png" -vf "$VF709,format=yuv420p" \
  -c:v libx264 -preset slow -crf 15 -profile:v high -level:v 5.2 -tune film -g "$FPS" "${TAGS[@]}" -movflags +faststart -an "$OUT/$NAME-${TAG}${FPS}-loop.mp4"
ffmpeg -nostdin -v error -y -framerate "$FPS" -start_number 0 -i "$FR/f_%04d.png" -vf "$VF709,format=yuv420p10le" \
  -c:v libx265 -preset medium -crf 16 -tag:v hvc1 -x265-params "log-level=error:keyint=$FPS" "${TAGS[@]}" -movflags +faststart -an "$OUT/$NAME-${TAG}${FPS}-loop-hevc10.mp4"
if [ "${RES%x*}" -gt 1920 ]; then
  ffmpeg -nostdin -v error -y -framerate "$FPS" -start_number 0 -i "$FR/f_%04d.png" -vf "scale=1920:1080:flags=lanczos,$VF709,format=yuv420p" \
    -c:v libx264 -preset slow -crf 16 -profile:v high -g "$FPS" "${TAGS[@]}" -movflags +faststart -an "$OUT/$NAME-1080p${FPS}-loop.mp4"
fi
cp "$FR/f_0000.png" "$OUT/$NAME-still.png"
ffmpeg -nostdin -v error -y -framerate "$FPS" -start_number 0 -i "$FR/f_%04d.png" \
  -vf "select='not(mod(n\,$((N / 8))))',scale=640:-1,tile=4x2:padding=6:color=white" -frames:v 1 -fps_mode passthrough "$OUT/$NAME-keyframes.png"
# seam check: the step from the last frame back to the first should look like any other step
psnr() { ffmpeg -nostdin -i "$1" -i "$2" -lavfi psnr -f null - 2>&1 | grep -oE "average:[0-9.inf]+" | cut -d: -f2; }
last=$(printf "%s/f_%04d.png" "$FR" $((N - 1))); prev=$(printf "%s/f_%04d.png" "$FR" $((N - 2)))
echo "seam check (PSNR, higher = smaller step): normal step $(psnr "$prev" "$last") dB, loop seam $(psnr "$last" "$FR/f_0000.png") dB"
[ $KEEP = 1 ] || rm -rf "${FR:?}"
ls -la "$OUT" | grep -v logs
