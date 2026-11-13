#!/bin/zsh
# usage: stills.sh <project_dir> <scene_index> <t1> [t2 ...]
# Fast 960x540 test frames -> <project>/build/tests/
SK=${0:A:h}
P=${1:A}; S=$2; shift 2
blender -b --factory-startup --python $SK/bl_main.py -- --project $P --scene $S --preview --still "$@" 2>&1 \
  | grep -E "Error|Traceback|File \"|still|WARN|unknown set" | head -30
