"""Shot list (TEMPLATE).  Builds the timeline from the real lengths of the narration and of the guides' lines.
Replace only the SHOTS section (between OPENING and CREDITS); see references/look.md for every helper.

Present day (warm colour): the elder (Yeay Sophal) and her granddaughter (Malis) at a memorial.  Memory (grey pencil and
charcoal): Sophal's story and the history.  Colour slowly returns at the end.
Shot helpers: S (any scene), AP (authentic photo as an old print in a family album), MF (framed photo beside a candle),
M (map), CH (hand-written pencil chapter card), GUIDE (Malis or Sophal speaks on screen), NOTE (notebook page).
Badges: recon / memory / symbol / photo / document / map / map_recon / text / guide.
No violence is depicted.  Victims' photographs (S-21 portraits) are not used.  Real people appear only in authentic
photographs, never animated.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, ROOT)

import soundfile as sf  # noqa: E402

import cards  # noqa: E402
import maps  # noqa: E402
import memory as MEM  # noqa: E402
import sets60 as Y  # noqa: E402
import sets70 as Z  # noqa: E402
import sets75 as T  # noqa: E402
from core import SH, SW, W, H, clamp, text_surface  # noqa: E402
from narration import N, WHO  # noqa: E402
from sets import F, grp  # noqa: E402

GAP = 0.5
FPS = 24
_MAN = None
PROJECT = json.load(open(os.path.join(ROOT, "project.json")))
PROJECT_KM, PROJECT_EN = PROJECT["title_km"], PROJECT["title_en"]


def man():
    global _MAN
    if _MAN is None:
        try:
            _MAN = {os.path.basename(e["file"]): e for e in json.load(open(os.path.join(ROOT, "archive", "manifest.json")))
                    if e.get("file")}
        except Exception:
            _MAN = {}
    return _MAN


def have(f):
    return bool(f) and os.path.exists(os.path.join(ROOT, "archive", "img", f))


def credit(f):
    return man().get(f, {}).get("attribution_line")


SHOTS = []
CHAPTERS = []
USED = set()


def S(lines=(), vis=None, cam=None, badge=None, note=None, pre=0.6, post=1.0, min_d=0.0, xin=1.0, music=None,
      amb=None, sfx=(), fade_in=0.0, fade_out=0.0, tag=None, trans=None, era="past", dark=0.0, ink_mode="full"):
    if trans == "smoke":
        xin = max(xin, 2.2)
    elif trans == "page":
        xin = max(xin, 1.2)
    elif trans == "redraw":
        xin = max(xin, 1.6)
    SHOTS.append(dict(lines=list(lines), vis=vis, cam=cam or dict(a=(SW / 2, SH / 2, 1.0), b=(SW / 2, SH / 2, 1.07)),
                      badge=badge, note=note, pre=pre, post=post, min_d=min_d, xin=xin, music=music, amb=amb,
                      sfx=list(sfx), fade_in=fade_in, fade_out=fade_out, tag=tag, trans=trans, era=era, dark=dark,
                      ink=ink_mode))


def cam(a, b=None, e="io"):
    return dict(a=a, b=b or a, ease=e)


def _card(f, **over):
    e = man().get(f, {})
    c = dict(km=e.get("object_name_km") or "", en=e.get("object_name") or e.get("title"), date=e.get("object_date"),
             credit=credit(f), note=e.get("authenticity_short"))
    c.update({k: v for k, v in over.items() if v is not None})
    return c


def _path(f):
    return os.path.join(ROOT, "archive", "img", f)


def _kw(ov):
    return {k: ov.pop(k) for k in list(ov) if k in S.__code__.co_varnames}


def AP(f, lines, tilt=-0.015, side="r", badge="photo", focus=(0.5, 0.5), z=(1.0, 1.07), **ov):
    kw = _kw(ov)
    kw.setdefault("trans", "page")
    if not have(f):
        raise SystemExit("missing archive image " + f)
    USED.add(f)
    card = _card(f, **ov)
    S(lines, lambda: MEM.album_photo(_path(f), card, tilt, z, focus, side, seed=len(SHOTS)), badge=badge,
      ink_mode=None, **kw)


def MF(f, lines, badge="photo", focus=(0.5, 0.5), **ov):
    kw = _kw(ov)
    kw.setdefault("trans", "smoke")
    USED.add(f)
    card = _card(f, **ov)
    S(lines, lambda: MEM.memorial_frame(_path(f), card, focus=focus, seed=len(SHOTS)), badge=badge, ink_mode=None,
      **kw)


def M(lines, va, vb, els, badge="map", note=None, **kw):
    kw.setdefault("trans", "redraw")
    S(lines, lambda: dict(maps.map_scene(va, vb, els), ink="tone"), badge=badge,
      note=note or "Relief from SRTM-derived tiles · rivers: Natural Earth · modern borders for orientation only",
      ink_mode="tone", **kw)


CH_CAM = cam((SW / 2, SH / 2, 1.0), (SW / 2 + 20, SH / 2, 1.03))


def CH(num, km, en, years, under=None, music=None, amb=None, sfx=(), dark=0.0):
    CHAPTERS.append(len(SHOTS))
    S([], lambda: MEM.pencil_chapter(num, km, en, years, under), CH_CAM, pre=0, post=5.4, xin=1.3, music=music,
      amb=amb, tag="chapter", trans="page", sfx=sfx, dark=dark)


def NOTE(lines, title_km, title_en, rows, foot=None, **kw):
    kw.setdefault("trans", "page")
    S(lines, lambda: MEM.sources_differ(title_km, title_en, rows, foot), badge="text", ink_mode=None, **kw)


def QUOTE(lines, km, en, who, **kw):
    """A survivor's words, hand-copied onto a notebook page, with the source."""
    def vis():
        def over(ctx, t, d):
            MEM.paper(ctx, MEM.PAPER, 911, lines=True, margin=True)
            s1 = text_surface("«" + km + "»", 40, MEM.GRAPHITE, MEM.KM_HAND, "", width=1420)
            MEM.write_on(ctx, s1, 250, 200, clamp((t - 0.3) / 5.0))
            s2 = text_surface("“" + en + "”", 36, "#3a3630", MEM.EN_HAND, "", width=1420)
            MEM.write_on(ctx, s2, 250, 230 + s1.get_height(), clamp((t - 2.5) / 5.0), 0.92)
            s3 = text_surface(who, 26, "#5a554c", "Helvetica Neue", "", width=1420)
            ctx.set_source_surface(s3, 250, 270 + s1.get_height() + s2.get_height())
            ctx.paint_with_alpha(clamp((t - 4.0) / 1.0))
        return dict(layers=[], over=over, ink=None)
    kw.setdefault("trans", "page")
    S(lines, vis, badge="text", note="Testimony quoted from the DC-Cam history; read aloud by the narrator",
      ink_mode=None, **kw)


# ---------------------------------------------------------------- guide lip-sync
_ENV = {}


def mouth_for(key, offset=0.6):
    def fn(t):
        if key not in _ENV:
            from narrate import wav_for
            p = wav_for(key)
            if os.path.exists(p):
                import audio
                _ENV[key] = audio.envelope(p, FPS)
            else:
                _ENV[key] = None
        env = _ENV[key]
        i = int((t - offset) * FPS)
        if env is None:
            import math
            return max(0.0, math.sin(t * 9)) * 0.7 if 0 <= t - offset < line_dur(key) else 0.0
        return float(env[i]) if 0 <= i < len(env) else 0.0
    return fn


GUIDE_NOTE = "Yeay Sophal and Malis are fictional, drawn from many survivors' stories"


def GUIDE(key, scene_fn, camv, **kw):
    kw.setdefault("note", GUIDE_NOTE)
    kw.setdefault("era", "present")
    S([key], lambda: scene_fn(mouth_for(key, kw.get("pre", 0.6))), camv, badge="guide", **kw)


def elder(x, y, h, pose="idle", yaw=40, talk=False, **kw):
    return F(x, y, h, "sophal_old", pose, yaw, 11, talk=talk, expr=kw.pop("expr", "calm"), **kw)


def youth(x, y, h, pose="idle", yaw=-40, talk=False, **kw):
    return F(x, y, h, "malis", pose, yaw, 12, talk=talk, expr=kw.pop("expr", "neutral"), **kw)


def pair(talker="youth", sp="kneel_pray", mp="idle", se="calm", me="neutral"):
    """Sophal and Malis at the incense pot by the memorial path."""
    return [grp(0.9, elder(1420, 1250, 430, sp, 60, talk=talker == "elder", expr=se),
                youth(1250, 1262, 420, mp, 30, talk=talker == "youth", expr=me))]


def MEMO(lines, fn, camv=None, note="Memory: Yeay Sophal's story is a fictional composite", **kw):
    """Sophal remembers (voice over a grey memory scene)."""
    S(lines, fn, camv, badge="memory", note=note, **kw)


MEM_CAM_Q = cam((1350, 1010, 1.75), (1330, 1000, 1.85))
MEM_CAM_S = cam((1460, 980, 1.8), (1450, 975, 1.9))


def Q(key, **kw):     # Malis asks, at the memorial
    GUIDE(key, lambda m: T.make_memorial("morning", people=pair("youth", me="neutral"), mouth_fn=m), MEM_CAM_Q, **kw)


def A(key, **kw):     # Sophal answers, at the memorial
    GUIDE(key, lambda m: T.make_memorial("morning", people=pair("elder", sp="kneel"), mouth_fn=m), MEM_CAM_S, **kw)


# ---------------------------------------------------------------- geography
P_ = dict(pp=(104.921, 11.569), bb=(103.20, 13.10), kcham=(105.46, 11.99), takeo=(104.78, 10.99),
          kthom=(104.89, 12.71), sreap=(103.86, 13.36), kampot=(104.18, 10.61), pursat=(103.92, 12.54),
          ksom=(103.52, 10.63), kratie=(106.02, 12.49), snuol=(106.43, 12.08), svay=(105.80, 11.09),
          ktral=(103.97, 10.22), saigon=(106.70, 10.78), kchhmar=(105.62, 12.18), svrieng=(105.80, 11.09),
          preyveng=(105.33, 11.48))


def mk(key, km, en, at=0.5, side="r", **kw):
    lon, lat = P_[key]
    d = dict(k="marker", lon=lon, lat=lat, km=km, en=en, at=at, side=side)
    d.update(kw)
    return d


CAMBODIA = Z.CAMBODIA
ROUTE = "#ff9a2a"
KH = (104.9, 12.6, 7.4)


def arrow_from_pp(to, at, draw=2.2, color=ROUTE):
    x0, y0 = P_["pp"]
    x1, y1 = to
    mid = ((x0 + x1) / 2 + (y1 - y0) * 0.08, (y0 + y1) / 2 - (x1 - x0) * 0.08)
    return dict(k="line", pts=[(x0, y0), mid, (x1, y1)], at=at, draw=draw, color=color, lw=5, dash=[10, 7])


# ---------------------------------------------------------------- colour returns at the end
_LOOK = []


def LOOK(t):
    col = 0.0
    for (t0, c0, t1, c1) in _LOOK:
        if t >= t0:
            q = min(1.0, (t - t0) / max(0.1, t1 - t0))
            col = c0 + (c1 - c0) * q
    return dict(dark=0.0, color=col)


def _set_look(shots):
    del _LOOK[:]
    if len(CHAPTERS) >= 2:
        t10 = shots[CHAPTERS[-2]]["start"]         # last chapter: a hint of colour comes back into memory
        _LOOK.append((t10, 0.0, t10 + 50.0, 0.4))
    cl = [s for s in shots if "m10" in (s.get("lines") or [])]
    if cl:
        tz = cl[0]["start"]
        _LOOK.append((tz, 0.4, tz + 12.0, 1.0))


# ================================================================ OPENING (sample: replace)
S([], lambda: MEM.text_page([
    ("ខ្សែភាពយន្ត នេះ និយាយ អំពី ការបាត់បង់។", 38, "#efe7d2", MEM.KM_HAND),
    ("This film speaks of loss.", 34, "#efe7d2", MEM.EN_HAND),
    ("វា មិន បង្ហាញ រូបភាព ហិង្សា ទេ។ · It shows no graphic images.", 28, "#cfc6b0", MEM.KM_HAND),
    ("សូម ឧទ្ទិស ដល់ ជនរងគ្រោះ និង អ្នក នៅ រស់។ · Dedicated to the victims and the survivors.", 28, "#e8a04a",
     MEM.KM_HAND)]), pre=0, post=0, min_d=10.0, xin=0, fade_in=1.5, amb="none", ink_mode=None)
S([], lambda: T.make_memorial("morning", people=[grp(0.9, elder(900, 1300, 400, "walk_slow", 70, vx=34),
                                                     youth(760, 1310, 400, "walk_slow", 70, vx=34))]),
  cam((1200, 700, 1.05), (1300, 760, 1.25)), badge="guide", note=GUIDE_NOTE, pre=0, post=0, min_d=6.0,
  trans="smoke", era="present", music="remember", amb="delta", sfx=("monbell",))
Q("m0")
A("s0")
S(["o1"], lambda: T.make_memorial("morning", people=pair("none", sp="kneel_pray")), cam((1300, 900, 1.3),
                                                                                        (1350, 920, 1.42)),
  badge="guide", note=GUIDE_NOTE, era="present")
S([], lambda: MEM.title_card(PROJECT_KM, PROJECT_EN, "យើងចងចាំ", "We Remember",
                             lambda: T.make_memorial("morning", people=pair("none", sp="kneel_pray"))),
  cam((1250, 560, 1.15), (1250, 520, 1.22)), pre=0, post=6.5, trans="smoke", era="present")

# ================================================================ 1. SAMPLE CHAPTER (replace)
CH(1, "ជំពូក គំរូ", "A Sample Chapter", "1975",
   under=lambda: T.make_exodus("grey", people=[grp(0.6, *T.crowd(10, 5))]), music="exodus", amb="farm")
Q("q1")
M(["a1"], KH, (104.95, 11.9, 4.6),
  [dict(k="blob", pts=CAMBODIA, at=0.2, fill="#d8cfb0", fa=0.22),
   mk("pp", "ភ្នំពេញ", "Phnom Penh", 0.3, "r", color="#9a3a2a", pulse=True),
   arrow_from_pp(P_["kcham"], 1.0), arrow_from_pp(P_["takeo"], 1.4)],
  badge="map_recon", note="Schematic sample map · modern borders")
MEMO(["s1"], lambda: T.make_exodus("grey", people=[grp(0.6, *T.crowd(8, 9, x0=-200, x1=900),
                                                         F(700, 1250, 340, "mom75", "walk_slow", 90, 25, vx=22),
                                                         F(800, 1258, 220, "vuthy", "walk_slow", 90, 26, vx=22))]),
     cam((900, 1020, 1.6), (1050, 1010, 1.65)))
S([], lambda: T.make_still("shoes"), cam((1200, 760, 1.2), (1190, 760, 1.38)), badge="symbol",
  note="Symbol: those lost on the roads", trans="smoke", min_d=5.0)

# ================================================================ CLOSING (keep)
CHAPTERS.append(len(SHOTS))
GUIDE("m10", lambda m: T.make_altar("morning", lit_at=1.6, people=[grp(0.85, youth(1500, 1450, 820, "kneel_pray", -30,
                                                                                   talk=True))], mouth_fn=m),
      cam((1200, 760, 1.35), (1180, 740, 1.45)), music="hope", amb="delta", sfx=("match",), trans="smoke", pre=3.2,
      post=2.5)
A("s10")
S(["z1"], lambda: T.make_memorial("morning", people=pair("none", sp="kneel_pray")), cam((1250, 720, 1.1),
                                                                                         (1250, 600, 1.2)),
  badge="guide", note=GUIDE_NOTE, era="present", post=2.5)
S([], lambda: MEM.text_page([("កុំ ឲ្យ រឿង នេះ កើត ឡើង ម្ដង ទៀត", 52, "#efe7d2", MEM.KM_HAND),
                             ("Never again", 46, "#e8a04a", MEM.EN_HAND)]), pre=0, post=0, min_d=6.0, trans="smoke",
  ink_mode=None)


# ================================================================ CREDITS
def credit_blocks():
    imgs = []
    for f, e in sorted(man().items()):
        if f in USED:
            imgs.append("%s — %s" % ((e.get("object_name") or f)[:80], e.get("attribution_line") or e.get("licence")))
    return [(PROJECT_KM + " · " + PROJECT_EN.upper(),
             ["An educational documentary in pencil-and-charcoal 2D animation, maps and authentic archival images",
              "Narration: Khmer · Subtitles: English and Khmer",
              "Yeay Sophal, Malis and their family are fictional, drawn from many survivors' stories",
              "Dedicated to the victims and to the survivors of Democratic Kampuchea"]),
            ("MAIN REFERENCES", ["TODO: the provided sources and main scholarship, from docs/research_brief.md",
                                 "Full list with links and access dates: docs/research_brief.md"]),
            ("ARCHIVES FOR FURTHER RESEARCH", [
                "Documentation Center of Cambodia · Tuol Sleng Genocide Museum · Bophana Audiovisual Resource Center",
                "TODO: say which sensitive images are NOT shown (e.g. victims' portraits)."]),
            ("ARCHIVAL IMAGES", imgs or ["None"]),
            ("MAP DATA", ["Natural Earth (public domain) · relief: SRTM-derived tiles",
                          "Routes and areas on drawn maps are schematic."]),
            ("MUSIC", ["Original score for tro, khim, strings and a monastery bell, synthesised for this film."]),
            ("NOTE", ["Animated scenes are artistic reconstructions or symbols; no violence is depicted.",
                      "Numbers that are estimates are labelled as estimates.",
                      "The Khmer narration should be reviewed by a native-speaking historian before publication."])]


S([], lambda: dict(cards.scrolling_credits(credit_blocks()), ink="tone"), pre=0, post=34.0, xin=1.5, music="credits75",
  tag="credits", amb="none", ink_mode="tone")


# ---------------------------------------------------------------- timeline assembly
def narr_wav(key):
    from narrate import wav_for
    return wav_for(key)


_DUR = {}


def line_dur(key):
    if key not in _DUR:
        p = narr_wav(key)
        _DUR[key] = sf.info(p).duration if os.path.exists(p) else len(N[key][0]) * 0.074
    return _DUR[key]


TARGETS = [45, 120]     # one start time per CH(...) plus the closing (CHAPTERS.append), from the brief
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


END_TARGET = json.load(open(os.path.join(ROOT, "project.json"))).get("end_target", 866)


def _extras():
    """Spread spare time inside each chapter so chapters start on the brief's schedule (never cut narration)."""
    global _EXTRA
    if _EXTRA is not None:
        return _EXTRA
    extra = {}
    bounds = [0] + CHAPTERS + [len(SHOTS) - 1]
    for k, tgt in enumerate(TARGETS + [END_TARGET]):
        starts = _layout(extra)
        seg = range(bounds[k], bounds[k + 1])
        nxt = bounds[k + 1]
        deficit = tgt - starts[nxt]
        body = [i for i in seg if SHOTS[i]["lines"]]
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
                        sfx=s["sfx"], tag=s["tag"], lines=s["lines"], trans=s["trans"], era=s["era"], dark=s["dark"],
                        ink=s.get("ink", "full")))
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
    _set_look(shots)
    return film.Timeline(shots, cues, burn=burn, look=LOOK)


if __name__ == "__main__":
    shots, pl, cues = build()
    tot = shots[-1]["start"] + shots[-1]["dur"]
    print("shots: %d  lines: %d  runtime: %d:%02d" % (len(shots), len(pl), tot // 60, tot % 60))
    for i in CHAPTERS:
        print("  chapter at %d:%02d" % (shots[i]["start"] // 60, shots[i]["start"] % 60))
    print("not placed:", [k for k in N if k not in {p["key"] for p in pl}])
