#!/bin/zsh
# One-time setup/check: Blender, ffmpeg, Khmer TTS (edge-tts) and the text renderer.
SK=${0:A:h:h}
ok=1
command -v blender >/dev/null || { echo "MISSING: blender (brew install --cask blender)"; ok=0; }
command -v ffmpeg >/dev/null || { echo "MISSING: ffmpeg (brew install ffmpeg)"; ok=0; }
BPY=$(ls -d /Applications/Blender.app/Contents/Resources/*/python/bin/python3* 2>/dev/null | head -1)
[[ -x $BPY ]] && echo "blender python: $BPY" || { echo "MISSING: Blender bundled python"; ok=0; }
if [[ ! -x $SK/.venv/bin/edge-tts ]]; then
  python3 -m venv $SK/.venv && $SK/.venv/bin/pip install -q edge-tts || { echo "FAILED: edge-tts install"; ok=0; }
fi
[[ -x $SK/.venv/bin/edge-tts ]] && echo "edge-tts: ok (Khmer voices need internet)"
if [[ ! -x $SK/scripts/render_text || $SK/scripts/render_text.swift -nt $SK/scripts/render_text ]]; then
  swiftc -O $SK/scripts/render_text.swift -o $SK/scripts/render_text || { echo "FAILED: swiftc"; ok=0; }
fi
[[ -x $SK/scripts/render_text ]] && echo "render_text: ok"
ls "/System/Library/Fonts/Supplemental/Khmer MN.ttc" >/dev/null 2>&1 && echo "Khmer font: ok"
(( ok )) && echo "SETUP OK" || { echo "SETUP INCOMPLETE"; exit 1; }
