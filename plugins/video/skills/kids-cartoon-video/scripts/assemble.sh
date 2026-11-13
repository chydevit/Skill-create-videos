#!/bin/zsh
# usage: assemble.sh <project_dir>  -> final MP4 + SRT in the project folder
SK=${0:A:h}
python3 $SK/assemble.py ${1:A} && python3 $SK/make_srt.py ${1:A}
