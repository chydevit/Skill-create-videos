#!/bin/bash
# Check that this computer has the tools the skills need.   ./doctor.sh
ok() { printf '  \033[32m✓\033[0m %s\n' "$1"; }
no() { printf '  \033[31m✗\033[0m %s   → %s\n' "$1" "$2"; }
opt() { printf '  \033[33m–\033[0m %s   → %s\n' "$1" "$2"; }
echo "Needed by every skill:"
command -v ffmpeg >/dev/null && ffmpeg -hide_banner -encoders 2>/dev/null | grep -q libx264 && ok "ffmpeg with libx264" || no "ffmpeg with libx264" "brew install ffmpeg"
if command -v node >/dev/null; then v=$(node -p 'process.versions.node.split(".")[0]'); [ "$v" -ge 22 ] && ok "Node $(node -v)" || no "Node $(node -v) (22+ needed)" "brew install node"; else no "Node 22+" "brew install node"; fi
CH=""; for c in "$CHROME_PATH" "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" "/Applications/Chromium.app/Contents/MacOS/Chromium" /usr/bin/google-chrome /usr/bin/chromium; do [ -n "$c" ] && [ -x "$c" ] && { CH=$c; break; }; done
[ -n "$CH" ] && ok "Chrome / Chromium" || no "Google Chrome or Chromium" "install Chrome, or set CHROME_PATH"
PY=""; for p in "$PROMO_PY" "$HOME/.claude/skills/khmer-2d-animation/.venv-vox/bin/python" "$HOME/voxcpm-env/bin/python" python3; do [ -n "$p" ] && command -v "$p" >/dev/null 2>&1 && "$p" -c 'import numpy, scipy' 2>/dev/null && { PY=$p; break; }; done
[ -n "$PY" ] && ok "Python with numpy + scipy ($PY)" || no "Python with numpy + scipy (saas-promo, portfolio-reel, brand-promo)" "pip install numpy scipy, or set PROMO_PY"
echo "Optional:"
command -v qrencode >/dev/null && ok "qrencode (QR code on the portfolio-reel app card)" || opt "qrencode (QR code on the portfolio-reel app card)" "brew install qrencode"
command -v blender >/dev/null || [ -x /Applications/Blender.app/Contents/MacOS/Blender ] && ok "Blender (brand-loop)" || opt "Blender 4.2+ (brand-loop only)" "https://www.blender.org"
V=""; for p in "$VOX_PY" "$HOME/.claude/skills/khmer-2d-animation/.venv-vox/bin/python" "$HOME/voxcpm-env/bin/python"; do [ -n "$p" ] && [ -x "$p" ] && "$p" -c 'import voxcpm' 2>/dev/null && { V=$p; break; }; done
[ -n "$V" ] && ok "VoxCPM2 narration (brand-promo)" || opt "VoxCPM2 narration (brand-promo only)" "pip install voxcpm soundfile, set VOX_PY"
