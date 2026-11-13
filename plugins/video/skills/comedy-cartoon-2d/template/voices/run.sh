#!/bin/sh
# Synthesise missing voices/lines with VoxCPM2 (local, Apple MPS). ~1-2 min model load + ~10-60 s per line.
# Python with `voxcpm` installed: $VOX_PY, else the khmer-2d-animation skill's venv, else ~/voxcpm-env.
cd "$(dirname "$0")/.." || exit 1
for p in "$VOX_PY" "$HOME/.claude/skills/khmer-2d-animation/.venv-vox/bin/python" "$HOME/voxcpm-env/bin/python"; do
  if [ -n "$p" ] && [ -x "$p" ]; then VOX_PY="$p"; break; fi
done
if [ ! -x "$VOX_PY" ]; then
  cat >&2 <<'MSG'
VoxCPM2 python not found. Install it once:
  python3.12 -m venv ~/voxcpm-env && ~/voxcpm-env/bin/pip install voxcpm soundfile
(or set VOX_PY to a python that has `voxcpm` installed)
MSG
  exit 1
fi
if [ "$1" = "--asr" ]; then shift; "$VOX_PY" voices/asr_check.py "$@" 2>&1 | grep -E "^[a-z0-9_./]+ +[0-9]"; exit; fi  # Khmer Whisper check (ids: compare takes)
python3 voices/make_jobs.py || exit 1
"$VOX_PY" voices/tts_vox.py build/vox/jobs.json 2>&1 | grep -E '^\{' | tee build/vox/log.txt
