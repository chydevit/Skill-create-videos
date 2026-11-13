"""Create a new memory-drawing documentary project from the template.

usage: new_memory_doc.py <project_dir> [--name slug] [--title-en "..."] [--title-km "..."] [--no-geo]
                         [--example democratic_kampuchea]

Copies engine/ into the project (every film is self-contained and can be patched freely), adds the template
(narration.py, script_src.py, make.py, pipeline.py, project.json, build/, docs/, research/, archive/) and the locked
voices (nar, elder, youth), links .venv to the render environment of the khmer-history-doc skill, and fetches map
data with that skill's fetch_geo.py.  --example democratic_kampuchea starts from the full 15-minute film instead."""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.expanduser("~/.claude/skills/khmer-history-doc")   # shared render + VoxCPM2 environments, geo fetcher


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--name")
    ap.add_argument("--title-en")
    ap.add_argument("--title-km")
    ap.add_argument("--no-geo", action="store_true")
    ap.add_argument("--example", choices=["democratic_kampuchea"])
    a = ap.parse_args()
    dst = os.path.abspath(os.path.expanduser(a.project))
    if os.path.exists(os.path.join(dst, "script_src.py")):
        sys.exit("%s already has a script_src.py: not overwriting" % dst)
    os.makedirs(dst, exist_ok=True)
    ign = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")
    shutil.copytree(os.path.join(SK, "engine"), os.path.join(dst, "engine"), ignore=ign, dirs_exist_ok=True)
    shutil.copytree(os.path.join(SK, "template"), dst, ignore=ign, dirs_exist_ok=True)
    for d in ("audio/voices", "audio/narr", "build", "film", "subtitles", "source/raw", "archive/img", "geo", "docs",
              "research"):
        os.makedirs(os.path.join(dst, d), exist_ok=True)
    if a.example:
        ex = os.path.join(SK, "examples", a.example)
        for f in ("narration.py", "script_src.py", "project.json"):
            shutil.copy(os.path.join(ex, f), os.path.join(dst, f))
        for d in ("docs", "research", "archive"):
            shutil.copytree(os.path.join(ex, d), os.path.join(dst, d), ignore=ign, dirs_exist_ok=True)
        shutil.copy(os.path.join(ex, "seeds.json"), os.path.join(dst, "audio", "seeds.json"))
        v = os.path.join(dst, "audio", "voices")       # the example names its guides sophal / malis
        shutil.copy(os.path.join(v, "elder.wav"), os.path.join(v, "sophal.wav"))
        shutil.copy(os.path.join(v, "youth.wav"), os.path.join(v, "malis.wav"))

    pj = os.path.join(dst, "project.json")
    p = json.load(open(pj))
    if not a.example or a.name:
        p["name"] = a.name or re.sub(r"[^a-z0-9]+", "_", os.path.basename(dst).lower()).strip("_")
    if a.title_en:
        p["title_en"] = a.title_en
    if a.title_km:
        p["title_km"] = a.title_km
    json.dump(p, open(pj, "w"), ensure_ascii=False, indent=2)

    venv = os.path.join(dst, ".venv")
    if not os.path.exists(venv) and os.path.isdir(os.path.join(BASE, ".venv")):
        os.symlink(os.path.join(BASE, ".venv"), venv)
    py = os.path.join(venv, "bin", "python")
    if not os.path.exists(py):
        print("WARNING: no render environment: run %s/scripts/setup.sh first" % BASE)
    if not a.no_geo:
        subprocess.run([py if os.path.exists(py) else sys.executable, os.path.join(BASE, "scripts", "fetch_geo.py"), dst],
                       check=True)
    print("project ready: %s\n  cd %s && .venv/bin/python make.py info" % (dst, dst))


if __name__ == "__main__":
    main()
