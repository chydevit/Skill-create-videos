#!/bin/zsh
# usage: build_audio.sh <project_dir>   -> voices, timeline.json, final_audio.wav
SK=${0:A:h}
BPY=$(ls -d /Applications/Blender.app/Contents/Resources/*/python/bin/python3* | head -1)
$BPY $SK/audio_build.py ${1:A}
