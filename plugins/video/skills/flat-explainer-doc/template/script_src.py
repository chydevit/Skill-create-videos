"""Shot list (flat explainer).  The timeline is built from the real lengths of the synthesised lines.

Scenes: SV("scenes/x.svg", ...) loads an SVG set (parallax layers + animated sprites, see engine/svgscene.py).
Graphic grammar (engine/explainer.py): E.timeline, E.chapter_title, E.map_card, E.portal, E.panels, E.big_text,
E.tag / E.title_tag / E.caption overlays (attach with E.with_over, or E.set_tags for labels that follow the camera).
Shot helpers: S (any shot), SV (svg scene shot), CH (chapter title), MAP (framed map), PH / MC (authentic photo /
museum card from archive/, credited).
Transitions (trans=): fade (default), cut, blob, iris, wipe, ripple, lotus, ink.
Music moods: wonder, ancient, tension, warm, discovery, outro (engine/synthscore.py) or any pinpeat mood.
SFX: sfx=["pop", ("whoosh", 1.2)] - name or (name, seconds into the shot).

SAMPLE CONTENT (the Human Era) - replace the SHOTS section with your film; keep the helpers and the assembly.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, ROOT)

import soundfile as sf  # noqa: E402

import audio  # noqa: E402
import cards  # noqa: E402
import explainer as E  # noqa: E402
import film  # noqa: E402
import photos  # noqa: E402
import synthscore  # noqa: E402
from core import SH, SW, EN_SERIF  # noqa: E402
from narration import N, WHO, VOICES  # noqa: E402
from svgscene import svg_scene  # noqa: E402

PROJECT = json.load(open(os.path.join(ROOT, "project.json")))
GAP = 0.35            # explainer pace: tighter than the documentary engine's 0.45
FPS = PROJECT.get("fps", 24)
film.POST[:] = [0.12, 0.35]   # flat look: almost no grain, light vignette
synthscore.install(audio)
import depth  # noqa: E402
depth.install(film)            # 2.5D camera: dolly + depth of field (cam(..., dolly=, dof=))
BADGES = PROJECT.get("badges", False)   # evidence badges off by default in this style (turn on for school use)
_MAN = None


def man():
    global _MAN
    if _MAN is None:
        try:
            _MAN = {os.path.basename(e["file"]): e for e in json.load(open(os.path.join(ROOT, "archive", "manifest.json")))}
        except Exception:
            _MAN = {}
    return _MAN


def have(f):
    return os.path.exists(os.path.join(ROOT, "archive", "img", f))


def credit(f):
    return man().get(f, {}).get("attribution_line")


SHOTS = []
CHAPTERS = []
USED = set()


def S(lines=(), vis=None, cam=None, badge=None, note=None, pre=0.4, post=0.6, min_d=0.0, xin=0.5, music=None,
      amb=None, sfx=(), fade_in=0.0, fade_out=0.0, tag=None, trans=None, guide=False):
    SHOTS.append(dict(lines=list(lines), vis=vis, cam=cam or dict(a=(SW / 2, SH / 2, 1.0), b=(SW / 2, SH / 2, 1.06)),
                      badge=badge if BADGES else None, note=note if BADGES else None, pre=pre, post=post,
                      min_d=min_d, xin=xin, music=music, amb=amb, sfx=list(sfx), fade_in=fade_in, fade_out=fade_out,
                      tag=tag, trans=trans, guide=guide))


def cam(a, b=None, e="io", dolly=None, dof=None):
    """Camera move from a=(cx, cy, zoom) to b in set coordinates (2400 x 1350). zoom 1.0 = whole set.
    2.5D: dolly=(c0, c1) pushes the camera THROUGH the depth planes (near layers rush past, far ones barely move);
    dof=(focus_depth, px) or (f0, f1, px) blurs layers away from the focus plane (rack focus when f0 != f1)."""
    d = dict(a=a, b=b or a, ease=e)
    if dolly:
        d["dolly"] = dolly
    if dof:
        d["dof"] = dof
    return d


def SV(lines, svg, camv=None, swap=None, tags=(), overs=(), badge="recon", **kw):
    """SVG scene shot. tags: E.tag(..., space="set") labels that stick to the set; overs: screen-space overlays."""
    def vis():
        sc = svg_scene(svg, swap=swap)
        if tags:
            E.set_tags(sc, *tags)
        if overs:
            E.with_over(sc, *overs)
        return sc
    S(lines, vis, camv, badge=badge, **kw)


def CH(small, big, bar=(0.0, 0.1), labels=("", ""), under=None, music=None, amb=None, trans="iris", post=3.2):
    CHAPTERS.append(len(SHOTS))
    S([], lambda: E.chapter_title(small, big, bar, labels, under), pre=0, post=post, xin=0.8, music=music, amb=amb,
      tag="chapter", trans=trans, sfx=[("chime", 0.5)])


def MAP(lines, svg, title=None, pins=(), boxes=(), zoom=(1.0, 1.1), focus=(0.5, 0.5), banner=None, routes=(), **kw):
    """Framed map. banner: title banner top-centre; routes: dashed arrows dict(pts=[(lon, lat)...], at, dur)."""
    S(lines, lambda: E.map_card(svg, title, pins, boxes, zoom, focus=focus, banner=banner, routes=routes), badge="map",
      note="Natural Earth (public domain) · positions approximate", **kw)


def PH(f, lines, z=(1.0, 1.12), fx=(0.5, 0.5), fy=(0.5, 0.5), contain=None, badge="photo", cap=None, **kw):
    """Authentic photo with a Ken Burns move (archive/img/<f>, credited from archive/manifest.json)."""
    if not have(f):
        S(lines, lambda: E.big_text([(N[lines[0]][1], 40, "#ffffff")]), **kw)
        return
    USED.add(f)
    e = man().get(f, {})
    c = cap or e.get("object_name") or e.get("title")
    S(lines, lambda: photos.photo(f, z, fx, fy, contain), badge=badge, note="%s  ·  %s" % (c, credit(f)), **kw)


def MC(f, lines, km=None, en=None, date=None, inst=None, found=None, note=None, badge="artifact", focus=(0.5, 0.5),
       z=(1.0, 1.15), side="r", **kw):
    if not have(f):
        return
    USED.add(f)
    e = man().get(f, {})
    card = dict(km=km or e.get("object_name_km") or "", en=en or e.get("object_name") or e.get("title"),
                date=date or e.get("object_date"), inst=inst or e.get("holding_institution"),
                found=found or e.get("find_place"), note=note, credit=credit(f))
    S(lines, lambda: photos.museum_card(f, card, z, focus, side), badge=badge, **kw)


TITLE_KM, TITLE_EN = PROJECT["title_km"], PROJECT["title_en"]
C = E.COL

# ================================================================ SHOTS (sample: the Human Era)
NIGHT = {"#7fd6c9": "#1b1640", "#d7f0b4": "#2c2058", "#fbe9a6": "#4a2a5e", "#fff4c4": "#f4f0ff",
         "#9fcf8a": "#2a3a5a", "#7dbb6c": "#22324e", "#e8c46a": "#3a2f52", "#d9ad4f": "#2f2646",
         "#f3c48a": "#7a5a8a", "#e6a46a": "#5a4272", "#c9784a": "#45325e", "#ffffff": "#8a7ab8"}

# cold open: slow push into the fire circle
SV(["o1"], "scenes/fire_night.svg", cam((1200, 700, 1.0), (1200, 720, 1.25)), pre=1.2, fade_in=1.8, xin=0,
   music="ancient", amb="lamp")
SV(["t1"], "scenes/fire_night.svg", cam((1700, 1000, 1.9), (1750, 1020, 2.05)), trans="cut", badge="guide")

# a timeline in ordinary years ...
S(["a1", "a2"], lambda: E.timeline("Timeline", -2600, 2300,
      events=[dict(year=-2300, label="First Empires", color=C["orange"], at=2.0, icon="scenes/village_day.svg"),
              dict(year=2026, label="Present Day", color=C["green"], at=2.6, icon="scenes/village_day.svg")],
      ticks=[(-2300, "-2300"), (1, "Year 1"), (2026, "2026")],
      segments=[(-2600, 1, "BCE", C["teal"]), (1, 2300, "CE", C["green"])]),
  trans="wipe", music="wonder", sfx=[("pop", 2.0), ("pop", 2.6)])
# ... the idea ...
S(["a3"], lambda: E.big_text([("Cesare Emiliani · 1993", 44, C["lime"]), ("+ 10,000", 170, "#ffffff"),
                              ("years", 44, "#c9c2e8")]), trans="iris", sfx=[("pop", 0.5)])
# ... and the same span in the Human Era
S(["a4"], lambda: E.timeline("Human Era Timeline", 0, 12600,
      events=[dict(year=500, label="Göbekli Tepe", color=C["magenta"], at=1.8),
              dict(year=10001, label="Year 1 CE", color=C["teal"], at=2.3),
              dict(year=12026, label="Present Day", color=C["green"], at=2.8, icon="scenes/village_day.svg")],
      ticks=[(0, "Year 0"), (12026, "12,026")],
      segments=[(0, 10001, "", C["violet"]), (10001, 12600, "", C["green"])],
      bg=("#1a0f2a", "#3a1f4a"), title_color=C["violet"]), trans="wipe", sfx=[("pop", 1.8), ("pop", 2.8)])

CH("From the Ice Age to", "THE FIRST VILLAGES", bar=(0.0, 0.06), labels=("Year 1 HE", "Now"),
   under=lambda: svg_scene("scenes/fire_night.svg"), music="warm")
SV(["a5"], "scenes/village_day.svg", cam((1100, 760, 1.15), (1300, 700, 1.0)),
   tags=[E.tag("First villages", 760, 560, C["magenta"], at=1.2, space="set", depth=0.5)], sfx=[("pop", 1.2)])
MAP(["a6"], "scenes/map_anatolia.svg", "Present-Day Türkiye",
    pins=[dict(lon=38.92, lat=37.22, label="Göbekli Tepe", color=C["magenta"], at=0.8)], zoom=(1.0, 1.25),
    focus=(0.62, 0.42), trans="iris", sfx=[("pop", 0.8)])
SV(["a7"], "scenes/village_day.svg", cam((1200, 675, 1.0), (1250, 700, 1.08)),
   overs=[E.portal(lambda: svg_scene("scenes/fire_night.svg"), 520, 330, 210, at=0.6)], sfx=[("magic", 0.6)])
SV(["t2"], "scenes/village_day.svg", cam((1800, 980, 1.6), (1700, 900, 1.35)), badge="guide",
   overs=[E.caption("12,026", 900, 230, 150, "#ffffff", at=1.0)], post=2.0, fade_out=1.5, sfx=[("pop", 1.0)])

# ================================================================ CREDITS
S([], lambda: E.big_text([(TITLE_EN, 64, "#ffffff"), (TITLE_KM, 50, C["lime"]),
                          ("An original flat-animation explainer · narration in Khmer, English subtitles", 26,
                           "#c9c2e8"),
                          ("Maps: Natural Earth (public domain) · Facts: docs/fact_sheet.md", 24, "#9a92c0"),
                          ("Khmer narration should be reviewed by a native speaker before publication", 24,
                           "#9a92c0")]),
  pre=0, post=8.0, xin=1.0, music="outro", tag="credits", amb="none")


# ================================================================ timeline assembly (keep as is)
def narr_wav(key):
    from narrate import wav_for
    return wav_for(key)


_DUR = {}


def line_dur(key):
    if key not in _DUR:
        p = narr_wav(key)
        _DUR[key] = sf.info(p).duration if os.path.exists(p) else len(N[key][0]) * 0.0747
    return _DUR[key]


# Optional chapter start times (s), one per CH(), e.g. from the brief.  Holds are stretched so each chapter starts
# on time (narration is never cut).  END_TARGET (project.json "end_target") does the same for the credits.
TARGETS = []
_EXTRA = None


def _layout(extra):
    t = 0.0
    starts = []
    for i, s in enumerate(SHOTS):
        xin = s["xin"] if i > 0 else 0.0
        start = max(0.0, t - xin) if i > 0 else 0.0
        lt = s["pre"] + sum(line_dur(k) + GAP for k in s["lines"])
        dur = max(lt - (GAP if s["lines"] else 0) + s["post"] + extra.get(i, 0.0), s["min_d"])
        starts.append(start)
        t = start + dur
    return starts


def _extras():
    global _EXTRA
    if _EXTRA is not None:
        return _EXTRA
    extra = {}
    goals = list(TARGETS[:len(CHAPTERS)])
    bounds = [0] + CHAPTERS[:len(goals)]
    if PROJECT.get("end_target"):
        goals.append(PROJECT["end_target"])
        bounds.append(len(SHOTS) - 1)
    for k, tgt in enumerate(goals):
        starts = _layout(extra)
        nxt = bounds[k + 1]
        deficit = tgt - starts[nxt]
        body = [i for i in range(bounds[k], nxt) if SHOTS[i]["lines"]]
        if deficit > 0 and body:
            for i in body:
                extra[i] = extra.get(i, 0.0) + deficit / len(body)
    _EXTRA = extra
    return extra


def build():
    extra = _extras()
    t = 0.0
    out, placements, cues = [], [], []
    for i, s in enumerate(SHOTS):
        xin = s["xin"] if i > 0 else 0.0
        start = max(0.0, t - xin) if i > 0 else 0.0
        lt = s["pre"]
        for k in s["lines"]:
            d = line_dur(k)
            placements.append(dict(key=k, t=start + lt, dur=d, wav=narr_wav(k), who=WHO.get(k, "nar")))
            cues.append(dict(start=start + lt, end=start + lt + d + 0.15, en=N[k][1], km=N[k][0], key=k,
                             who=WHO.get(k, "nar")))
            lt += d + GAP
        dur = max(lt - (GAP if s["lines"] else 0) + s["post"] + extra.get(i, 0.0), s["min_d"])
        out.append(dict(make=s["vis"], start=start, dur=dur, cam=s["cam"], badge=s["badge"], badge_note=s["note"],
                        xin=xin, fade_in=s["fade_in"], fade_out=s["fade_out"], music=s["music"], amb=s["amb"],
                        sfx=s["sfx"], tag=s["tag"], lines=s["lines"], trans=s["trans"]))
        t = start + dur
    return out, placements, _split_cues(cues)


def _split_cues(cues, limit=84):
    import re
    out = []
    for c in cues:
        en = c["en"]
        if len(en) <= limit:
            out.append(c)
            continue
        parts = re.split(r"(?<=[.;:,!?])\s+", en)
        chunks, cur = [], ""
        for p in parts:
            if cur and len(cur) + len(p) + 1 > limit:
                chunks.append(cur)
                cur = p
            else:
                cur = (cur + " " + p).strip()
        if cur:
            chunks.append(cur)
        tot = sum(len(x) for x in chunks)
        t0, span = c["start"], c["end"] - c["start"]
        for j, ch in enumerate(chunks):
            d = span * len(ch) / tot
            out.append(dict(c, start=t0, end=t0 + d - (0.04 if j < len(chunks) - 1 else 0), en=ch))
            t0 += d
    return out


def timeline(burn=True):
    import film
    shots, _, cues = build()
    return film.Timeline(shots, cues, burn=burn)


if __name__ == "__main__":
    shots, pl, cues = build()
    tot = shots[-1]["start"] + shots[-1]["dur"]
    print("shots: %d  lines: %d  runtime: %d:%02d" % (len(shots), len(pl), tot // 60, tot % 60))
    for i in CHAPTERS:
        print("  chapter at %d:%02d" % (shots[i]["start"] // 60, shots[i]["start"] % 60))
    print("not placed:", [k for k in N if k not in {p["key"] for p in pl}])
