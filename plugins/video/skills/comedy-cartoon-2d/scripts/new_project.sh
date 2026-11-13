#!/bin/sh
# Scaffold a cartoon project from the skill's template.
#   new_project.sh <dir>                          starter film (3 shots) to replace with your own
#   new_project.sh <dir> --example getaway-car    the full 90 s comedy example (voices included, builds offline)
#   new_project.sh <dir> --example team-story     the 2.5 min Khmer story example (builds offline)
#   new_project.sh <dir> --example kimlong        Office series Episode 7, 3:44 Khmer story with the series cast (builds offline)
set -e
SKD="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$1"
if [ -z "$DEST" ]; then echo "usage: $0 <dir> [--example <name>]" >&2; exit 1; fi
if [ -e "$DEST/src/shots.mjs" ]; then echo "$DEST already has a project (src/shots.mjs); not overwriting" >&2; exit 1; fi
mkdir -p "$DEST"
cp -R "$SKD/template/." "$DEST/"
if [ "$2" = "--example" ]; then
  EX="$SKD/examples/$3"
  [ -d "$EX" ] || { echo "no example '$3' (have: $(ls "$SKD/examples"))" >&2; exit 1; }
  cp -R "$EX/src/." "$DEST/src/"   # shots.mjs + any film-specific modules (sets, extra cast, scene folders)
  cp "$EX/film.json" "$DEST/film.json"
  cp "$EX/voices/"* "$DEST/voices/"
  rm -f "$DEST/build/vox/"*.wav; mkdir -p "$DEST/build/vox"
  cp "$EX/vox/"*.wav "$DEST/build/vox/"
fi
cd "$DEST" && npm install --silent --no-audit --no-fund
echo "project ready: $DEST  (npm run stills -- 1.5 4 | npm run build)"
