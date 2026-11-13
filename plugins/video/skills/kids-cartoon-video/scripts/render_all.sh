#!/bin/zsh
# usage: render_all.sh <project_dir>
# Renders every scene at 1080p in two parallel queues (resumes skipped frames),
# encodes each scene to build/segments/segNN.mp4. Keeps the Mac awake while running.
# PREVIEW=1 render_all.sh P  -> quick 960x540 low-sample test render
SK=${0:A:h}
P=${1:A}
PV=""; [[ -n $PREVIEW ]] && PV="--preview"
N=$(python3 -c "import json;print(len(json.load(open('$P/build/timeline.json'))['scenes']))")
mkdir -p $P/build/segments $P/build/logs
queue() {
  for i in "$@"; do
    name=$(python3 -c "import json;print(json.load(open('$P/build/timeline.json'))['scenes'][$i]['name'])")
    dir=$P/build/frames/$(printf %02d $i)_$name
    echo "[$(date +%T)] start scene $i $name"
    blender -b --factory-startup --python $SK/bl_main.py -- --project $P --scene $i $PV \
      > $P/build/logs/scene$i.log 2>&1
    ffmpeg -v error -y -framerate 24 -i $dir/f_%04d.jpg -c:v libx264 -preset slow -crf 16 \
      -pix_fmt yuv420p $P/build/segments/seg$(printf %02d $i).mp4 \
      && echo "[$(date +%T)] done scene $i" || echo "[$(date +%T)] ERROR encoding scene $i"
  done
}
A=(); B=()
for ((i=0; i<N; i++)); do (( i % 2 )) && B+=($i) || A+=($i); done
caffeinate -ims zsh -c "$(typeset -f queue); P=$P; SK=$SK; PV=$PV; queue ${A[*]}" > $P/build/logs/queueA.log 2>&1 &
caffeinate -ims zsh -c "$(typeset -f queue); P=$P; SK=$SK; PV=$PV; queue ${B[*]}" > $P/build/logs/queueB.log 2>&1 &
wait
cat $P/build/logs/queue*.log
