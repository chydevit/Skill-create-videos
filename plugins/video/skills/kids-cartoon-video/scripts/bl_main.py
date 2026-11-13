"""Build and render one scene of the episode.

blender -b --factory-startup --python bl_main.py -- --project DIR --scene 0 [--preview]
        [--still 12.5 30] [--start F --end F]
"""
import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector, Euler  # noqa: E402

import bl_util as U  # noqa: E402
import bl_chars as C  # noqa: E402
import bl_env as E  # noqa: E402
import bl_hud  # noqa: E402
from bl_hud import HUD  # noqa: E402
from bl_scenes import SCENE_CLASSES  # noqa: E402

BUILD = None


def parse():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--scene", type=int, required=True)
    p.add_argument("--preview", action="store_true")
    p.add_argument("--still", type=float, nargs="*")
    p.add_argument("--start", type=int, default=None)
    p.add_argument("--end", type=int, default=None)
    p.add_argument("--out", default=None)
    p.add_argument("--save", action="store_true")
    return p.parse_args(argv)


def clear():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras,
                 bpy.data.curves, bpy.data.actions):
        for d in list(coll):
            coll.remove(d)


def norm(s):
    return "".join(ch for ch in s.lower() if ch.isalnum())


def camera_track(cam, A, cams, shots, first):
    nf = A.nf
    loc = np.zeros((nf, 3))
    tgt = np.zeros((nf, 3))
    l0, t0 = shots[first]
    loc[:] = l0
    tgt[:] = t0
    for t, shot, d in sorted(cams):
        if shot not in shots:
            print("WARN unknown shot", shot)
            continue
        i0 = min(int(t * U.FPS), nf - 1)
        cl, ct = loc[i0].copy(), tgt[i0].copy()
        nl, nt = np.array(shots[shot][0]), np.array(shots[shot][1])
        u = U.smooth((A.t - t) / max(d, 0.05))[:, None]
        sel = A.t >= t
        loc[sel] = (cl + (nl - cl) * u)[sel]
        tgt[sel] = (ct + (nt - ct) * u)[sel]
    # gentle drift so the picture never feels frozen
    loc[:, 0] += 0.07 * np.sin(2 * math.pi * A.t / 11.0)
    loc[:, 2] += 0.03 * np.sin(2 * math.pi * A.t / 13.0)
    tgt[:, 2] += 0.015 * np.sin(2 * math.pi * A.t / 9.0)
    rx, ry, rz = np.zeros(nf), np.zeros(nf), np.zeros(nf)
    prev = Euler((0, 0, 0))
    for i in range(nf):
        d = Vector(tgt[i]) - Vector(loc[i])
        e = d.to_track_quat("-Z", "Y").to_euler("XYZ", prev)
        rx[i], ry[i], rz[i] = e
        prev = e
    for k in range(3):
        A.set(cam, "location", k, loc[:, k])
    A.set(cam, "rotation_euler", 0, rx)
    A.set(cam, "rotation_euler", 1, ry)
    A.set(cam, "rotation_euler", 2, rz)


def bobo_flight(bobo, A, flights, scene):
    P = bobo.P
    home = np.array(scene.bobo_home, dtype=float)
    off = home + np.array([6.5, 1.5, 1.0])
    cur_start = off if scene.bobo_start_hidden else home
    P["x"][:], P["y"][:], P["z"][:] = cur_start
    perch_until = []
    for t, action, arg in sorted(flights, key=lambda f: f[0]):
        i0 = min(int(t * U.FPS), A.nf - 1)
        cur = np.array([P["x"][i0], P["y"][i0], P["z"][i0]])
        after = A.t >= t
        if action == "loop":
            d = 2.6
            u = np.clip((A.t - t) / d, 0, 1)
            su = U.smooth(u)
            P["x"][after] = (cur[0] + 0.8 * np.sin(2 * math.pi * su))[after]
            P["y"][after] = (cur[1] - 0.3 * np.sin(2 * math.pi * su))[after]
            P["z"][after] = (cur[2] + 0.45 * (1 - np.cos(2 * math.pi * su)))[after]
            w = U.window(A.t, t, t + d, 0.2)
            P["flap_freq"] += 5 * w
            P["flap_amp"] += 0.4 * w
            P["spin"] += 2 * math.pi * su * after
            continue
        if action == "fly_in":
            target, d, perch = home, 1.8, False
        elif action == "fly_to":
            spot = scene.spots.get(arg)
            if spot is None:
                C.bird_action(bobo, A, "jump", t, 0.9, None)
                continue
            target, d, perch = np.array(spot[:3]), 1.7, spot[3]
        else:
            continue
        # leave a perch
        P["perch"][after] = 0
        u = U.smooth((A.t - t) / d)
        pos = cur[None, :] + (target - cur)[None, :] * u[:, None]
        pos[:, 2] += 0.35 * np.sin(math.pi * np.clip((A.t - t) / d, 0, 1))
        P["x"][after], P["y"][after], P["z"][after] = pos[after].T
        w = U.window(A.t, t, t + d, 0.25)
        P["flap_freq"] += 6 * w
        P["flap_amp"] += 0.5 * w
        P["ry"] += 0.3 * np.sign(target[0] - cur[0]) * w
        P["rx"] += 0.2 * w
        if perch:
            P["perch"] = np.maximum(P["perch"], U.smooth((A.t - (t + d - 0.3)) / 0.3))


def main():
    global BUILD
    args = parse()
    BUILD = os.path.join(os.path.abspath(args.project), "build")
    bl_hud.TEXT_CACHE = os.path.join(BUILD, "text")
    tl = json.load(open(os.path.join(BUILD, "timeline.json")))
    sd = tl["scenes"][args.scene]
    nf = sd["frames"]
    print("Scene", args.scene, sd["name"], "frames", nf)
    clear()
    E.setup_render(args.preview)
    sc = bpy.context.scene
    sc.frame_start = 1
    sc.frame_end = nf
    A = U.Anim(nf)

    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    U.link(cam)
    cam.data.lens = 35
    cam.data.sensor_width = 36
    cam.data.sensor_fit = "HORIZONTAL"
    cam.data.clip_start = 0.05
    cam.data.clip_end = 300
    sc.camera = cam
    hud = HUD(cam, A, tl.get("ui"))

    events = sorted(sd["events"], key=lambda e: e["t"])
    set_name = sd.get("set", sd["name"])
    if set_name not in SCENE_CLASSES:
        raise SystemExit("unknown set %r; available: %s" % (set_name, sorted(SCENE_CLASSES)))
    Scn = SCENE_CLASSES[set_name]
    scene = Scn(A, hud, events)
    scene.build()

    chars = {}
    for name, (pos, rz) in scene.kids.items():
        chars[name] = C.Kid(name, pos, rz)
    chars["bobo"] = C.Bobo(scene.bobo_home)
    for ch in chars.values():
        ch.init_pose(A)
    for a in scene.animals.values():
        a.init_pose(A)
    kids = [c for c in chars.values() if c.kind == "kid"]
    allc = list(chars.values())

    speeches, cams, cards, flights, turns = [], [], [], [], []
    # walks first so actions know where everybody stands
    for e in events:
        if e["type"] == "walk":
            who, target, d = e["args"][:3]
            if who in chars:
                C.walk(chars[who], A, e["t"], d, target)
    for e in events:
        typ, t = e["type"], e["t"]
        a = e.get("args", [])
        if typ == "speech":
            speeches.append(e)
        elif typ == "turn":
            if e.get("show", True):
                turns.append((t, t + e["dur"]))
        elif typ == "act":
            who, act, d = a[0], a[1], a[2]
            ch = chars.get(who)
            if ch is None:
                continue
            if ch.kind == "kid":
                C.kid_action(ch, A, act, t, d, a[3:], allc)
            else:
                C.bird_action(ch, A, act, t, d, a[3:])
        elif typ == "face":
            who, mood, d = a
            ch = chars.get(who)
            if ch is None:
                continue
            if ch.kind == "kid":
                C.kid_mood(ch, A, mood, t, d)
            else:
                C.bird_mood(ch, A, mood, t, d)
        elif typ == "card":
            cards.append((t, a[0], a[1], a[2], a[3]))
        elif typ == "cam":
            cams.append((t, a[0], a[1]))
        elif typ == "prop":
            name, action = a[0], a[1]
            if name == "bobo":
                flights.append((t, action, a[2] if len(a) > 2 else None))
            elif name == "fx":
                hud.stars(t)
            elif name in scene.animals:
                C.animal_action(scene.animals[name], A, action, t)
            else:
                scene.prop(name, action, t, a[2:])

    for k, ch in enumerate(kids):
        C.idle_kid(ch, A, k * 1.7 + 0.3)
    bobo_flight(chars["bobo"], A, flights, scene)
    C.speech_drive(allc, A, speeches)
    for k, ch in enumerate(allc):
        if ch.kind == "kid":
            C.finish_kid(ch, A, 10 + k)
        else:
            C.finish_bird(ch, A, 20 + k)
    for an in scene.animals.values():
        C.finish_animal(an, A, speeches)
    if hasattr(scene, "finish"):
        scene.finish()
    for ch in allc:
        ch.write(A)
    for an in scene.animals.values():
        an.write(A)

    camera_track(cam, A, cams, scene.shots, scene.first_shot)

    # ---------------------------------------------------------- overlay
    t_end = nf / U.FPS
    slots = {"top": [], "title": []}
    for c in cards:
        slots["title" if c[4] == "title" else "top"].append(c)
    sentence_windows = []
    for slot in slots.values():
        slot.sort()
        for i, (t0, text, color, dur, style) in enumerate(slot):
            t1 = min(t0 + dur, t_end - 0.3)
            if i + 1 < len(slot):
                t1 = min(t1, slot[i + 1][0] - 0.05)
            hud.card(text, color, t0, t1, style)
            if style == "sentence":
                sentence_windows.append((t0, t1, norm(text)))
    caps = []
    for sp in speeches:
        if not sp["cap"]:
            continue
        t0 = sp["t"]
        dup = any(a - 0.3 <= t0 <= b and n == norm(sp["text"]) for a, b, n in sentence_windows)
        if dup:
            continue
        caps.append([t0, t0 + max(sp["dur"] + 0.35, 1.3), sp["text"], sp["who"]])
    for i in range(len(caps) - 1):
        caps[i][1] = min(caps[i][1], caps[i + 1][0] - 0.03)
    for c in caps:
        for t0, t1 in turns:
            if c[0] < t0 < c[1]:
                c[1] = t0 - 0.03
    for t0, t1, text, who in caps:
        hud.caption(text, who, t0, t1)
    for t0, t1 in turns:
        hud.turn(t0, t1)

    # overlay and far-away decoration must not cast shadows into the set
    def no_shadow(ob):
        try:
            ob.visible_shadow = False
        except AttributeError:
            pass
        for c in ob.children:
            no_shadow(c)
    no_shadow(hud.root)
    for ob in bpy.data.objects:
        if ob.name.startswith(("cloud", "scloud", "sunball")):
            no_shadow(ob)

    nk = A.write()
    print("keys written", nk, "objects", len(bpy.data.objects))

    if args.save:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BUILD, "scene%d.blend" % args.scene))

    if args.still:
        os.makedirs(os.path.join(BUILD, "tests"), exist_ok=True)
        sc.render.image_settings.file_format = "PNG"
        for st in args.still:
            f = int(st * U.FPS) + 1
            sc.frame_set(f)
            sc.render.filepath = os.path.join(BUILD, "tests", "s%d_%s_%05.1f.png" % (
                args.scene, sd["name"], st))
            t = time.time()
            bpy.ops.render.render(write_still=True)
            print("still", st, "render %.2fs" % (time.time() - t))
        return

    out = args.out or os.path.join(BUILD, "frames", "%02d_%s" % (args.scene, sd["name"]))
    os.makedirs(out, exist_ok=True)
    sc.frame_start = args.start or 1
    sc.frame_end = args.end or nf
    # skip frames already rendered (resume support)
    sc.render.use_overwrite = False
    sc.render.filepath = os.path.join(out, "f_")
    t = time.time()
    bpy.ops.render.render(animation=True)
    print("rendered in %.1fs" % (time.time() - t))


main()
