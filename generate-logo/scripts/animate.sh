#!/bin/bash
# generate-logo: turn a logo image into 5-second animated logo reveals.
#
# usage: animate.sh <logo.png|jpg|webp|svg> [options]
#   --styles a,b,..   liquid,neon,bounce,lens,rise or "all" (default: all)
#   --out DIR         output folder (default: ./<name>-animations)
#   --name NAME       file name prefix (default: from the logo file name)
#   --size WxH        1920x1080 (default), or "square" (1080x1080), "vertical" (1080x1920), any WxH
#   --fps N           frames per second (default 60)
#   --bg MODE         auto (default) | light | dark | #rrggbb   (neon is always dark)
#   --text "A|B"      add a wordmark to the right of the logo; "|" splits it into two colours
#   --font NAME       wordmark font (default Arial, bold)    --text-colors "#hex,#hex"
#   --prores          also write a ProRes 4444 .mov with alpha (large files)
#   --no-alpha        skip the transparent WebM
#   --preview         only render a keyframe sheet per style (fast check, no video)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)

die() { echo "error: $*" >&2; exit 1; }
[ $# -ge 1 ] || { sed -n '2,17p' "$0"; exit 1; }
LOGO=$1; shift
[ -f "$LOGO" ] || die "logo not found: $LOGO"
LOGO=$(cd "$(dirname "$LOGO")" && pwd)/$(basename "$LOGO")

STYLES=all; OUT=""; NAME=""; SIZE=1920x1080; FPS=60; BG=auto; TEXT=""; FONT=""; TEXTCOLORS=""
PRORES=0; ALPHA=1; PREVIEW=0
while [ $# -gt 0 ]; do
  case $1 in
    --styles) STYLES=$2; shift 2 ;;
    --out) OUT=$2; shift 2 ;;
    --name) NAME=$2; shift 2 ;;
    --size) SIZE=$2; shift 2 ;;
    --fps) FPS=$2; shift 2 ;;
    --bg) BG=$2; shift 2 ;;
    --text) TEXT=$2; shift 2 ;;
    --font) FONT=$2; shift 2 ;;
    --text-colors) TEXTCOLORS=$2; shift 2 ;;
    --prores) PRORES=1; shift ;;
    --no-alpha) ALPHA=0; shift ;;
    --preview) PREVIEW=1; shift ;;
    *) die "unknown option $1" ;;
  esac
done
case $SIZE in square) SIZE=1080x1080 ;; vertical) SIZE=1080x1920 ;; landscape|hd) SIZE=1920x1080 ;; esac
[[ $SIZE =~ ^[0-9]+x[0-9]+$ ]] || die "--size must be WxH, square or vertical"
WIDTH=${SIZE%x*}; HEIGHT=${SIZE#*x}
[ "$STYLES" = all ] && STYLES=liquid,neon,bounce,lens,rise
IFS=, read -r -a STYLE_LIST <<< "$STYLES"
for s in "${STYLE_LIST[@]}"; do [ -f "$HERE/styles/$s.mjs" ] || die "unknown style '$s' (have: $(ls "$HERE/styles" | sed 's/\.mjs//' | tr '\n' ' '))"; done
if [ -z "$NAME" ]; then NAME=$(basename "${LOGO%.*}" | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9_-'); NAME=${NAME:-logo}; fi
OUT=${OUT:-$PWD/$NAME-animations}
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)

command -v node >/dev/null || die "node is required (v22+)"
command -v ffmpeg >/dev/null || die "ffmpeg is required"
WORK=$(mktemp -d "${TMPDIR:-/tmp}/genlogo.XXXXXX")
trap 'rm -rf "${WORK:?}"' EXIT

json_str() { node -e 'process.stdout.write(JSON.stringify(process.argv[1]))' "$1"; }
SHEET_TIMES="0.3,0.6,0.9,1.2,1.5,1.8,2.1,2.5,3.0,4.98"
made=()

for STYLE in "${STYLE_LIST[@]}"; do
  echo "== $STYLE"
  base="$OUT/$NAME-5s-$STYLE"
  cfg="$WORK/$STYLE.json"
  colors="[]"
  [ -n "$TEXTCOLORS" ] && colors=$(node -e 'process.stdout.write(JSON.stringify(process.argv[1].split(",").map(s=>s.trim())))' "$TEXTCOLORS")
  cat > "$cfg" <<EOF
{ "style": "$STYLE", "theme": $(json_str "$BG"), "width": $WIDTH, "height": $HEIGHT,
  "logoFile": $(json_str "$(basename "$LOGO")"), "text": $(json_str "$TEXT"), "font": $(json_str "${FONT:-Arial}"),
  "textColors": $colors }
EOF
  if [ $PREVIEW = 1 ]; then
    node "$HERE/render.mjs" --config "$cfg" --logo "$LOGO" --out "$WORK/$STYLE-sheet" --times "$SHEET_TIMES" --info "$base-info.json"
    ffmpeg -v error -y -pattern_type glob -i "$WORK/$STYLE-sheet/t_*.png" -vf "scale=480:-1,tile=5x2:padding=6:color=white" -frames:v 1 "$base-preview.png"
    made+=("$base-preview.png")
    continue
  fi
  node "$HERE/render.mjs" --config "$cfg" --logo "$LOGO" --out "$WORK/$STYLE-bg" --fps "$FPS" --info "$base-info.json"
  node "$HERE/sfx.mjs" "$base-info.json" "$base-sfx.wav" >/dev/null
  ffmpeg -v error -y -framerate "$FPS" -i "$WORK/$STYLE-bg/f_%04d.png" -i "$base-sfx.wav" \
    -vf "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p,noise=c0s=2:c0f=u" \
    -c:v libx264 -preset slow -crf 14 -profile:v high -tune film \
    -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
    -c:a aac -b:a 256k -movflags +faststart "$base.mp4"
  made+=("$base.mp4")
  frames=$(ls "$WORK/$STYLE-bg" | wc -l | tr -d ' ')
  picks=$(node -e 'const f=+process.argv[1],n=+process.argv[2];process.stdout.write(process.argv[3].split(",").map(t=>"eq(n\\,"+Math.min(n-1,Math.round(+t*f))+")").join("+"))' "$FPS" "$frames" "$SHEET_TIMES")
  ffmpeg -v error -y -framerate "$FPS" -i "$WORK/$STYLE-bg/f_%04d.png" -vf "select='$picks',scale=480:-1,tile=5x2:padding=6:color=white" \
    -frames:v 1 -fps_mode passthrough "$base-keyframes.png"
  rm -rf "${WORK:?}/$STYLE-bg"
  if [ $ALPHA = 1 ] || [ $PRORES = 1 ]; then
    node "$HERE/render.mjs" --config "$cfg" --logo "$LOGO" --out "$WORK/$STYLE-alpha" --fps "$FPS" --transparent
    if [ $ALPHA = 1 ]; then
      ffmpeg -v error -y -framerate "$FPS" -i "$WORK/$STYLE-alpha/f_%04d.png" -i "$base-sfx.wav" \
        -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 0 -crf 18 -row-mt 1 -auto-alt-ref 0 -deadline good -cpu-used 2 \
        -c:a libopus -b:a 160k "$base-alpha.webm"
      made+=("$base-alpha.webm")
    fi
    if [ $PRORES = 1 ]; then
      ffmpeg -v error -y -framerate "$FPS" -i "$WORK/$STYLE-alpha/f_%04d.png" -i "$base-sfx.wav" \
        -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le -alpha_bits 16 -vendor apl0 \
        -color_primaries bt709 -color_trc bt709 -colorspace bt709 -c:a pcm_s24le "$base-alpha.mov"
      made+=("$base-alpha.mov")
    fi
    rm -rf "${WORK:?}/$STYLE-alpha"
  fi
done

# one overview image with a row per style
sheets=()
for STYLE in "${STYLE_LIST[@]}"; do
  f="$OUT/$NAME-5s-$STYLE-keyframes.png"; [ $PREVIEW = 1 ] && f="$OUT/$NAME-5s-$STYLE-preview.png"
  [ -f "$f" ] && sheets+=(-i "$f")
done
if [ ${#sheets[@]} -ge 4 ]; then
  n=$(( ${#sheets[@]} / 2 ))
  ffmpeg -v error -y "${sheets[@]}" -filter_complex "vstack=inputs=$n" "$OUT/$NAME-5s-overview.png"
  made+=("$OUT/$NAME-5s-overview.png")
fi
echo
echo "done -> $OUT"
for f in "${made[@]}"; do echo "  $(basename "$f")"; done
