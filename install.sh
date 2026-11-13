#!/bin/bash
# Install the skills by linking each one into ~/.claude/skills, so they work in every Claude Code project.
# (The other way is the plugin marketplace: /plugin marketplace add chydevit/Skill-create-videos. Use one, not both.)
#   ./install.sh            link every skill (edits and `git pull` take effect at once)
#   ./install.sh --copy     copy instead of link
#   ./install.sh --remove   remove the links this script made
set -euo pipefail
cd "$(dirname "$0")"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$DEST"
for d in plugins/*/skills/*/; do
  d=${d%/}; name=$(basename "$d"); [ -f "$d/SKILL.md" ] || continue
  target="$DEST/$name"
  if [ "${1:-}" = --remove ]; then
    [ -L "$target" ] && rm "$target" && echo "removed /$name" || echo "skip $name (not a link made by this script)"
    continue
  fi
  if [ -e "$target" ] && [ ! -L "$target" ]; then echo "skip $name: $target exists and is not a link (remove it first)"; continue; fi
  rm -f "$target"
  if [ "${1:-}" = --copy ]; then cp -R "$PWD/$d" "$target"; else ln -s "$PWD/$d" "$target"; fi
  chmod +x "$d"/scripts/*.sh 2>/dev/null || true
  echo "installed /$name -> $target"
done
[ "${1:-}" = --remove ] || cat <<'MSG'

Done. Check your tools with ./doctor.sh, then start a new Claude Code session and type:
  /portfolio-reel make an intro reel with me.jpg and my three best clips
  /saas-promo make a promo from the screenshots in shots/
  /generate-logo animate logo.png
  /brand-promo make a showreel from these 5 videos and my logo
  /brand-loop make a looping background in my logo's colours
MSG
