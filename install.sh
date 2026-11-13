#!/bin/bash
# Install the skills in this repo for Claude Code: links each skill folder into ~/.claude/skills,
# so /generate-logo, /brand-promo, /brand-loop, /saas-promo and /portfolio-reel work in every project. Run it again after `git pull` (links stay valid).
#   ./install.sh            link (edits in this repo take effect immediately)
#   ./install.sh --copy     copy instead of link
#   ./install.sh --remove   uninstall
set -euo pipefail
cd "$(dirname "$0")"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$DEST"
for d in */; do
  d=${d%/}; [ -f "$d/SKILL.md" ] || continue
  target="$DEST/$d"
  if [ "${1:-}" = --remove ]; then
    [ -L "$target" ] && rm "$target" && echo "removed /$d" || echo "skip $d (not a link made by this script)"
    continue
  fi
  if [ -e "$target" ] && [ ! -L "$target" ]; then echo "skip $d: $target exists and is not a link (remove it first)"; continue; fi
  rm -f "$target"
  if [ "${1:-}" = --copy ]; then cp -R "$PWD/$d" "$target"; else ln -s "$PWD/$d" "$target"; fi
  chmod +x "$d"/scripts/*.sh 2>/dev/null || true
  echo "installed /$d -> $target"
done
[ "${1:-}" = --remove ] || cat <<'MSG'

Done. Start a new Claude Code session and type:
  /generate-logo animate logo.png
  /brand-promo make a showreel from these 5 videos and my logo
  /brand-loop make a looping background in my logo's colours
  /saas-promo make a SaaS promo from my screenshots
  /portfolio-reel make an intro reel with my photo and my best clips
MSG
