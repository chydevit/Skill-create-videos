#!/usr/bin/env python3
"""Create a flat-explainer documentary project.

usage: new_explainer.py <project_dir> [--name slug] [--title-en "..."] [--title-km "..."]

Builds on the khmer-history-doc engine (voices, ASR QC, music, subtitles, render, mux): copies that engine into the
project, adds this skill's svgscene.py + explainer.py, patches film.py (flat post-processing switch, iris / wipe
transitions), then adds the template (narration.py, script_src.py, scenes/, chars/, docs/)."""
import argparse
import json
import os
import re
import shutil
import sys

SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KH = os.path.expanduser("~/.claude/skills/khmer-history-doc")


def patch_film(path):
    s = open(path).read()
    if "POST = [" in s:
        return
    rep = [
        ('_LAYERS = {}\n', '_LAYERS = {}\nPOST = [0.8, 1.0]  # grain, vignette; explainer projects set [0.12, 0.35]\n'),
        ('post(ctx, fi, grain=0.8, vignette=1.0)', 'post(ctx, fi, grain=POST[0], vignette=POST[1])'),
        ('    _POST["th"] = np.arctan2(dy, dx)\n', '    _POST["th"] = np.arctan2(dy, dx)\n    _POST["x"] = x2 / ww\n'),
        ('    else:\n        m = np.full(A["r"].shape, p, np.float32)',
         '    elif kind == "iris":\n        m = np.clip((p * 1.08 - A["r"]) / 0.012, 0, 1)\n'
         '    elif kind == "blob":  # liquid ink-blob iris with a wobbling edge (reference transition)\n'
         '        th = A["th"]\n'
         '        wob = 1 + 0.16 * np.sin(5 * th + 7 * p) + 0.09 * np.sin(9 * th - 11 * p) + 0.05 * np.sin(17 * th + 3 * p)\n'
         '        m = np.clip((p * 1.3 * wob - A["r"]) / 0.01, 0, 1)\n'
         '    elif kind == "wipe":\n        m = np.clip((p * 1.12 - A["x"]) / 0.04, 0, 1)\n'
         '    else:\n        m = np.full(A["r"].shape, p, np.float32)'),
        ('if kind in ("ripple", "lotus", "ink"):', 'if kind in ("ripple", "lotus", "ink", "iris", "wipe", "blob"):'),
        # a frame that raises must fail the render, not leave ffmpeg waiting and the pool hanging
        ('    for fi in range(f0, f1):\n        ctx.save()\n        tl.render_frame(ctx, fi)\n',
         '    for fi in range(f0, f1):\n        ctx.save()\n        try:\n            tl.render_frame(ctx, fi)\n'
         '        except Exception as e:\n            p.kill()\n'
         '            raise RuntimeError("frame %d (t=%.2fs) failed: %r" % (fi, fi / FPS, e))\n'),
    ]
    for a, b in rep:
        if a not in s:
            sys.exit("film.py patch failed (engine changed?): %r" % a[:60])
        s = s.replace(a, b, 1)
    open(path, "w").write(s)


def patch_audio(path):
    s = open(path).read()
    if "explainer sfx" in s:
        return
    rep = [
        ('        if s.get("tag") == "chapter":\n',
         '        if tr in ("iris", "wipe", "blob"):\n'
         '            _place(sfx, S.sfx_whoosh(int(s["start"]), 0.6) * 0.3, max(0, s["start"] - s.get("xin", 1)))\n'
         '        if s.get("tag") == "chapter":\n'),
        ('        for name in s.get("sfx") or []:\n',
         '        for name in s.get("sfx") or []:\n'
         '            dt = 0.0  # explainer sfx: ("pop", 1.2) plays any sound.SFX name at start + 1.2 s\n'
         '            if isinstance(name, (tuple, list)):\n'
         '                name, dt = name\n'
         '            if name not in ("hit", "bell"):\n'
         '                _place(sfx, S.make_sfx(name, int(s["start"] + dt)) * 0.45, s["start"] + dt)\n'
         '                continue\n'),
    ]
    for a, b in rep:
        if a not in s:
            sys.exit("audio.py patch failed (engine changed?): %r" % a[:60])
        s = s.replace(a, b, 1)
    open(path, "w").write(s)


def patch_core_make(engine_dir, make_py):
    c = os.path.join(engine_dir, "core.py")
    s = open(c).read()
    if "project fps" not in s:
        a = "FPS = 24\n"
        if a not in s:
            sys.exit("core.py patch failed (engine changed?)")
        s = s.replace(a, "FPS = 24\n", 1)
        s = s.replace('CACHE = os.path.join(ROOT, "build", "cache")\n',
                      'CACHE = os.path.join(ROOT, "build", "cache")\n'
                      'try:  # project fps (explainer projects default to 60 like the reference)\n'
                      '    import json as _json\n'
                      '    FPS = int(_json.load(open(os.path.join(ROOT, "project.json"))).get("fps", 24))\n'
                      'except Exception:\n    pass\n', 1)
        open(c, "w").write(s)
    m = open(make_py).read()
    if "burn_subs" not in m:
        a = "workers=int(os.environ.get(\"WORKERS\", \"6\")), burn=True)"
        if a not in m:
            sys.exit("make.py patch failed (engine changed?)")
        m = m.replace(a, "workers=int(os.environ.get(\"WORKERS\", \"6\")), burn=PROJECT.get(\"burn_subs\", True))")
        open(make_py, "w").write(m)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--name")
    ap.add_argument("--title-en")
    ap.add_argument("--title-km")
    a = ap.parse_args()
    if not os.path.isdir(os.path.join(KH, "engine")):
        sys.exit("needs the khmer-history-doc skill (engine, voices) at %s" % KH)
    dst = os.path.abspath(os.path.expanduser(a.project))
    if os.path.exists(os.path.join(dst, "script_src.py")):
        sys.exit("%s already has a script_src.py: not overwriting" % dst)
    os.makedirs(dst, exist_ok=True)
    ign = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")
    shutil.copytree(os.path.join(KH, "engine"), os.path.join(dst, "engine"), ignore=ign, dirs_exist_ok=True)
    shutil.copy(os.path.join(KH, "template", "make.py"), os.path.join(dst, "make.py"))
    for f in os.listdir(os.path.join(SK, "engine_add")):
        if f.endswith(".py"):
            shutil.copy(os.path.join(SK, "engine_add", f), os.path.join(dst, "engine", f))
    patch_film(os.path.join(dst, "engine", "film.py"))
    patch_audio(os.path.join(dst, "engine", "audio.py"))
    patch_core_make(os.path.join(dst, "engine"), os.path.join(dst, "make.py"))
    shutil.copytree(os.path.join(SK, "template"), dst, ignore=ign, dirs_exist_ok=True)
    for d in ("audio/voices", "audio/narr", "build", "film", "subtitles", "source", "archive/img", "docs"):
        os.makedirs(os.path.join(dst, d), exist_ok=True)
    man = os.path.join(dst, "archive", "manifest.json")
    if not os.path.exists(man):
        open(man, "w").write("[]\n")

    pj = os.path.join(dst, "project.json")
    p = json.load(open(pj))
    p["name"] = a.name or re.sub(r"[^a-z0-9]+", "_", os.path.basename(dst).lower()).strip("_")
    if a.title_en:
        p["title_en"] = a.title_en
    if a.title_km:
        p["title_km"] = a.title_km
    json.dump(p, open(pj, "w"), ensure_ascii=False, indent=2)

    venv = os.path.join(dst, ".venv")
    if not os.path.exists(venv):
        os.symlink(os.path.join(SK, ".venv"), venv)
    print("project ready: %s\n  next: cd %s && .venv/bin/python make.py info && .venv/bin/python make.py shotstills"
          % (dst, dst))


if __name__ == "__main__":
    main()
