"""Shot list for 'Democratic Kampuchea 1975-1979: We Remember' (កម្ពុជាប្រជាធិបតេយ្យ ១៩៧៥–១៩៧៩៖ យើងចងចាំ).
Builds the timeline from the real lengths of the narration and of the guides' lines.

Present day (warm colour): Yeay Sophal and her granddaughter Malis at a memorial.  Memory (grey pencil and
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


def sophal(x, y, h, pose="idle", yaw=40, talk=False, **kw):
    return F(x, y, h, "sophal_old", pose, yaw, 11, talk=talk, expr=kw.pop("expr", "calm"), **kw)


def malis(x, y, h, pose="idle", yaw=-40, talk=False, **kw):
    return F(x, y, h, "malis", pose, yaw, 12, talk=talk, expr=kw.pop("expr", "neutral"), **kw)


def pair(talker="malis", sp="kneel_pray", mp="idle", se="calm", me="neutral"):
    """Sophal and Malis at the incense pot by the memorial path."""
    return [grp(0.9, sophal(1420, 1250, 430, sp, 60, talk=talker == "sophal", expr=se),
                malis(1250, 1262, 420, mp, 30, talk=talker == "malis", expr=me))]


def MEMO(lines, fn, camv=None, note="Memory: Yeay Sophal's story is a fictional composite", **kw):
    """Sophal remembers (voice over a grey memory scene)."""
    S(lines, fn, camv, badge="memory", note=note, **kw)


MEM_CAM_Q = cam((1350, 1010, 1.75), (1330, 1000, 1.85))
MEM_CAM_S = cam((1460, 980, 1.8), (1450, 975, 1.9))


def Q(key, **kw):     # Malis asks, at the memorial
    GUIDE(key, lambda m: T.make_memorial("morning", people=pair("malis", me="neutral"), mouth_fn=m), MEM_CAM_Q, **kw)


def A(key, **kw):     # Sophal answers, at the memorial
    GUIDE(key, lambda m: T.make_memorial("morning", people=pair("sophal", sp="kneel"), mouth_fn=m), MEM_CAM_S, **kw)


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
    if len(CHAPTERS) >= 10:
        t10 = shots[CHAPTERS[9]]["start"]          # chapter 10: a hint of colour comes back into memory
        _LOOK.append((t10, 0.0, t10 + 50.0, 0.4))
    cl = [s for s in shots if "m10" in (s.get("lines") or [])]
    if cl:
        tz = cl[0]["start"]
        _LOOK.append((tz, 0.4, tz + 12.0, 1.0))


# ================================================================ OPENING (0:00 - 0:45)
S([], lambda: MEM.text_page([
    ("ខ្សែភាពយន្ត នេះ និយាយ អំពី អំពើប្រល័យពូជសាសន៍ និង ការបាត់បង់។", 38, "#efe7d2", MEM.KM_HAND),
    ("This film speaks of genocide and loss.", 34, "#efe7d2", MEM.EN_HAND),
    ("វា មិន បង្ហាញ រូបភាព ហិង្សា ទេ។ · It shows no graphic images.", 28, "#cfc6b0", MEM.KM_HAND),
    ("សូម ឧទ្ទិស ដល់ ជនរងគ្រោះ និង អ្នក នៅ រស់។ · Dedicated to the victims and the survivors.", 28, "#e8a04a",
     MEM.KM_HAND)]), pre=0, post=0, min_d=10.0, xin=0, fade_in=1.5, music=None, amb="none", badge=None, ink_mode=None)
S([], lambda: T.make_memorial("morning", people=[grp(0.9, sophal(900, 1300, 400, "walk_slow", 70, vx=34),
                                                     malis(760, 1310, 400, "walk_slow", 70, vx=34))]),
  cam((1200, 700, 1.05), (1300, 760, 1.25)), badge="guide", note=GUIDE_NOTE, pre=0, post=0, min_d=6.0,
  trans="smoke", era="present", music="remember", amb="delta", sfx=("monbell",))
Q("m0")
GUIDE("s0", lambda m: T.make_memorial("morning", people=pair("sophal", sp="kneel_pray"), mouth_fn=m),
      cam((1500, 1040, 1.9), (1520, 1030, 2.0)))
S(["o1"], lambda: T.make_memorial("morning", people=pair("none", sp="kneel_pray")), cam((1300, 900, 1.3),
                                                                                        (1350, 920, 1.42)),
  badge="guide", note=GUIDE_NOTE, era="present")
S(["o2"], lambda: T.make_memorial("morning", people=pair("none", sp="kneel_pray")), cam((1630, 900, 1.6),
                                                                                        (1630, 650, 1.9)),
  badge="recon", note="A memorial stupa (drawn; not a specific site)", era="present")
S([], lambda: MEM.title_card("កម្ពុជាប្រជាធិបតេយ្យ", "Democratic Kampuchea", "១៩៧៥–១៩៧៩ · យើងចងចាំ",
                             "1975–1979 · We Remember",
                             lambda: T.make_memorial("morning", people=pair("none", sp="kneel_pray"))),
  cam((1250, 560, 1.15), (1250, 520, 1.22)), pre=0, post=6.5, trans="smoke", era="present")

# ================================================================ 1. 17 APRIL 1975 (0:45 - 2:00)
FAMILY = lambda x=1100, y=1250: grp(0.85, F(x, y, 360, "dad75", "idle", 20, 21), F(x + 150, y + 8, 340, "mom75", "idle", 10, 22),  # noqa: E731
                                    F(x + 280, y + 4, 330, "sophal_y", "idle", -10, 23),
                                    F(x + 400, y + 10, 220, "vuthy", "idle", -20, 24))
CH(1, "ថ្ងៃទី ១៧ ខែមេសា ឆ្នាំ ១៩៧៥", "17 April 1975", "Phnom Penh",
   under=lambda: Z.make_newsstand("grey", papers=False), music="april", amb="town")
Q("q1")
MEMO(["s1"], lambda: Z.make_newsstand("grey", papers=False, people=[FAMILY()]), cam((1300, 900, 1.45), (1350, 900, 1.55)),
     trans="smoke")
AP("usaf_recon_monivong_bridge_17apr1975.jpg", ["a1"], side="r", focus=(0.5, 0.45), z=(1.0, 1.12))
S(["a2"], lambda: Z.make_newsstand("grey", papers=False, people=[grp(0.85, *[
    F(820 + k * 170, 1250 + (k % 2) * 18, 340, ["pp_man", "pp_woman", "student_m", "pp_woman2", "pp_man2", "student_f",
                                                 "kh_elder"][k], "cheer", 0, 60 + k) for k in range(7)],
    F(300, 1270, 330, "kr_soldier", "walk_slow", 90, 70, vx=30), F(150, 1290, 320, "kr_soldier", "walk_slow", 90, 71,
                                                                   vx=30))]),
  cam((1250, 960, 1.3), (1350, 950, 1.38)), badge="recon",
  note="Reconstruction: Phnom Penh, morning of 17 April 1975 (no violence shown)", trans="redraw")
S(["a3"], lambda: Z.make_newsstand("grey", papers=False, people=[grp(0.85, *T.crowd(9, 41, 34, 1230, 1300, 300, 350,
                                                                                    x0=200, x1=2300),
                                                                    F(1900, 1280, 330, "kr_soldier", "idle", -60, 72))]),
  cam((1350, 930, 1.25), (1250, 930, 1.3)), badge="recon",
  note="Reconstruction: the order to leave (no violence shown)")
AP("usaf_recon_burning_esso_tanks_17apr1975.jpg", ["a4"], side="l", focus=(0.5, 0.5))
MEMO(["s2"], lambda: T.make_still("glasses"), cam((1200, 700, 1.25), (1220, 700, 1.4)), trans="smoke")

# ================================================================ 2. EMPTYING THE CITIES (2:00 - 3:30)
CH(2, "ការជម្លៀស ចេញពី ទីក្រុង", "Emptying the Cities", "April 1975",
   under=lambda: T.make_exodus("grey", people=[grp(0.6, *T.crowd(10, 5))]), music="exodus", amb="farm")
Q("q2")
M(["b1"], KH, (104.95, 11.9, 4.6),
  [dict(k="blob", pts=CAMBODIA, at=0.2, fill="#d8cfb0", fa=0.22),
   mk("pp", "ភ្នំពេញ", "Phnom Penh", 0.3, "r", color="#9a3a2a", pulse=True),
   arrow_from_pp(P_["kcham"], 1.0), arrow_from_pp(P_["takeo"], 1.4), arrow_from_pp(P_["pursat"], 1.8),
   arrow_from_pp(P_["kthom"], 2.2), arrow_from_pp(P_["preyveng"], 2.6), arrow_from_pp(P_["ksom"], 3.0),
   dict(k="note", km="យ៉ាងតិច ២ លាន នាក់ ក្នុង ប្រហែល មួយ សប្ដាហ៍", en="At least two million people in about one week",
        cls="record", at=3.6, x=80, y=760)],
  badge="map_recon", note="Schematic: directions of the April 1975 evacuation (approximate) · modern borders")
S(["b2"], lambda: T.make_exodus("grey", people=[grp(0.6, *T.crowd(18, 7))]), cam((1100, 1000, 1.25), (1350, 980, 1.3)),
  badge="recon", note="Reconstruction: the road out of Phnom Penh, April 1975")
M(["b3"], KH, KH,
  [dict(k="blob", pts=CAMBODIA, at=0.0, fill="#d8cfb0", fa=0.22),
   mk("pp", "ភ្នំពេញ", "Phnom Penh", 0.2, "r", color="#9a3a2a"),
   mk("bb", "បាត់ដំបង", "Battambang", 0.6, "r", pulse=True), mk("kcham", "កំពង់ចាម", "Kampong Cham", 1.0, "r", pulse=True),
   mk("takeo", "តាកែវ", "Takeo", 1.4, "l", pulse=True), mk("sreap", "សៀមរាប", "Siem Reap", 1.8, "r", pulse=True),
   mk("kampot", "កំពត", "Kampot", 2.2, "l", pulse=True)], badge="map")
QUOTE(["b4"], "នៅលើ ផ្លូវ ដ៏ ណែនណាន់តាន់តាប់ ខ្ញុំ ឮ សូរសំឡេង មនុស្សម្នា ស្រែក ហៅ រក ឪពុកម្ដាយ និង បងប្អូន និង សម្រែក ក្មេងៗ យំ ទារ រក បាយ។",
      "On the crowded road, I heard people calling for their parents and relatives, and hungry children crying for "
      "rice.", "ស៊ឹម សុត ហៅ កុយ · Sim Soth (Koy), cyclo driver · testimony in Khamboly Dy, A History of Democratic "
      "Kampuchea (DC-Cam, 2007), p. 16")
S(["b5"], lambda: T.make_still("shoes"), cam((1200, 760, 1.2), (1190, 760, 1.38)), badge="symbol",
  note="Symbol: those lost on the roads", trans="smoke")
MEMO(["s3"], lambda: T.make_exodus("grey", people=[grp(0.6, *T.crowd(8, 9, x0=-200, x1=900),
                                                         F(700, 1250, 340, "mom75", "walk_slow", 90, 25, vx=22),
                                                         F(800, 1258, 220, "vuthy", "walk_slow", 90, 26, vx=22),
                                                         F(560, 1240, 330, "sophal_y", "carry_bundle", 90, 27, vx=22))]),
     cam((900, 1020, 1.6), (1050, 1010, 1.65)))
S(["b6"], lambda: Y.make_village("grey", people=[grp(0.55, *T.workers(6, 11, 1060, 1200, 250, 300, "walk_slow",
                                                                         ("pp_man", "pp_woman", "student_m")),
                                                       *T.workers(4, 12, 1080, 1180, 240, 280, "idle",
                                                                  ("worker_m", "worker_w"), x0=1500, x1=2200))]),
  cam((1250, 900, 1.15), (1250, 900, 1.22)), badge="recon",
  note="Reconstruction: evacuees ('new people') arrive in a village of 'base people'", trans="redraw")
M(["b7"], KH, KH,
  [dict(k="blob", pts=CAMBODIA, at=0.0, fill="#d8cfb0", fa=0.22),
   dict(k="line", pts=[(104.6, 11.1), (104.0, 11.8), (103.6, 12.5)], at=0.5, draw=2.0, color=ROUTE, lw=5),
   dict(k="line", pts=[(105.5, 11.6), (104.6, 12.2), (103.9, 12.6)], at=1.2, draw=2.0, color=ROUTE, lw=5),
   mk("bb", "បាត់ដំបង", "Battambang", 2.4, "r"), mk("pursat", "ពោធិ៍សាត់", "Pursat", 2.6, "l"),
   dict(k="note", km="ការផ្លាស់ទី ជា លើកទីពីរ · ១៩៧៥–១៩៧៧", en="Second wave of forced moves, 1975–1977", cls="record",
        at=3.0, x=80, y=760)],
  badge="map_recon", note="Schematic: main direction of the second forced movement (after ECCC Case 002/01)")

# ================================================================ 3. "YEAR ZERO" (3:30 - 5:00)
CH(3, "«ឆ្នាំសូន្យ»", "“Year Zero”", "1975 – 1979", under=lambda: T.make_still("gate"), music="zero",
   amb="none")
Q("q3")
S(["c1"], lambda: Z.make_empty("grey"), cam((1200, 820, 1.1), (1250, 820, 1.2)), badge="recon",
  note="Reconstruction: Phnom Penh, emptied")
S(["c2"], lambda: T.make_still("notes"), cam((1200, 700, 1.1), (1200, 700, 1.2)), badge="symbol",
  note="Symbol: money abolished; riel notes left in the streets")
S(["c3"], lambda: T.make_classroom("books"), cam((1200, 760, 1.15), (1250, 820, 1.32)), badge="symbol",
  note="Symbol: schools closed", trans="redraw")
S(["c4"], lambda: T.make_still("gate"), cam((1200, 700, 1.1), (1200, 720, 1.25)), badge="symbol",
  note="Symbol: places of worship closed", sfx=("monbell",))
AP("cia_npic_report_dismantling_western_structures_oct1977_text.jpg", [], side="r", badge="document", min_d=6.0,
   focus=(0.5, 0.2))
S(["c5"], lambda: T.make_hall("grey"), cam((1200, 760, 1.12), (1200, 760, 1.2)), badge="recon",
  note="Reconstruction: a communal kitchen and dining hall")
AP("flag_democratic_kampuchea.png", ["c6"], side="r", badge="document", tilt=0.01)
MEMO(["s4"], lambda: T.make_fields("grey", night=True, people=[grp(0.6, *T.workers(9, 31, 1050, 1150, 250, 290, "sit",
                                                                                         ("worker_m", "worker_w")),
                                                                   F(1250, 1190, 300, "sophal_k", "sit", 0, 28),
                                                                   F(1650, 1100, 320, "kr_soldier", "talk", -90, 29))]),
     cam((1250, 900, 1.3), (1250, 900, 1.4)), dark=0.15,
     note="Memory (fictional composite): a night meeting in a cooperative")

# ================================================================ 4. LIFE IN THE COOPERATIVES (5:00 - 6:30)
CH(4, "ជីវិត ក្នុង សហករណ៍", "Life in the Cooperatives", "1975 – 1979",
   under=lambda: T.make_fields("grey", people=[grp(0.6, *T.workers(8, 2))]), music="coop", amb="farm")
Q("q4")
S(["d1"], lambda: T.make_fields("grey", people=[grp(0.6, *T.workers(14, 3))]), cam((1200, 900, 1.15), (1300, 900, 1.25)),
  badge="recon", note="Reconstruction: a cooperative rice field")
S(["d2"], lambda: T.make_fields("grey", dam=True, people=[grp(0.6, *T.workers(14, 4, 900, 1060, 200, 260,
                                                                                 "carry_shoulder", vx=22))]),
  cam((1100, 850, 1.15), (1300, 830, 1.22)), badge="recon", note="Reconstruction: building a dam", trans="redraw")
AP("pol_pot_era_irrigation_canal_2013.jpg", [], side="l", min_d=5.5)
S(["d3"], lambda: T.make_hall("grey", people=[grp(0.6, *T.workers(12, 5, 960, 1000, 260, 280, "sit",
                                                                       ("worker_m", "worker_w", "child_k")))]),
  cam((1200, 900, 1.2), (1250, 900, 1.28)), badge="recon", note="Reconstruction: communal eating")
S(["d4"], lambda: T.make_still("bowl"), cam((1200, 700, 1.15), (1200, 700, 1.32)), badge="symbol",
  note="Symbol: hunger", trans="smoke")
S(["d5"], lambda: T.make_fields("grey", people=[grp(0.6, *T.workers(10, 6, 1000, 1200, 180, 220, "carry_bundle",
                                                                       ("child_k",), vx=18))]),
  cam((1200, 900, 1.2), (1300, 900, 1.26)), badge="recon", note="Reconstruction: a children's work unit",
  trans="redraw")
AP("khmer_rouge_cadre_clothing_museum.jpg", ["d6"], side="r")
MEMO(["s5"], lambda: T.make_fields("grey", dam=True, night=True,
                                    people=[grp(0.6, *T.workers(10, 7, 900, 1060, 200, 250, "carry_shoulder", vx=18),
                                                F(1000, 1100, 270, "sophal_k", "carry_shoulder", 90, 30, vx=18))]),
     cam((1150, 880, 1.35), (1300, 870, 1.42)), dark=0.15,
     note="Memory (fictional composite): a mobile work unit digging by night")

# ================================================================ 5. THE LEADERS AND THE STATE (6:30 - 7:45)
CH(5, "មេដឹកនាំ និង រដ្ឋ", "The Leaders and the State", "1976 – 1979", under=lambda: Y.make_palace60("grey"),
   music="state", amb="none")
Q("q5")
S(["e1"], lambda: Y.make_assembly("grey", hands=False), cam((1200, 740, 1.05), (1200, 720, 1.14)), badge="recon",
  note="Reconstruction: the People's Representative Assembly met only once, April 1976")
AP("sihanouk_un_security_council_jan1979.jpg", ["e2a", "e2b"], side="r",
   note="Photo taken in New York, January 1979, after his release")
AP("ceausescu_pol_pot_khieu_samphan_phnom_penh_may1978.jpg", ["e3"], side="l")
AP("ieng_sary_greeted_by_ceausescu_bucharest_oct1976.jpg", ["e4"], side="r")
AP("map_dk_administrative_zones_1975_78.png", [], side="c", badge="map", min_d=5.0, tilt=0.0)
AP("ieng_sary_talks_with_ceausescu_bucharest_oct1976.jpg", ["e5"], side="l")

# ================================================================ 6. TARGETED GROUPS (7:45 - 9:15)
CH(6, "អ្នក ដែល ត្រូវ គេ កំណត់ គោលដៅ", "Targeted Groups", "1975 – 1979", under=lambda: T.make_classroom("books"),
   music="targets", amb="none")
Q("q6")
MEMO(["s6"], lambda: T.make_still("glasses"), cam((1300, 720, 1.5), (1320, 720, 1.62)), trans="smoke")
S(["f1"], lambda: T.make_fields("grey", people=[grp(0.6, *T.workers(10, 8),
                                                     F(2000, 1150, 300, "kr_soldier", "idle", -80, 80))]),
  cam((1300, 900, 1.15), (1400, 900, 1.2)), badge="recon", note="Reconstruction (no violence shown)")
AP("monks_institut_bouddhique_1930.jpg", ["f2"], side="r", note="Photo from 1930: monks long before the war")
AP("cham_mosque_minaret_kampong_cham_2019.jpg", ["f3"], side="l", note="Modern photo (2019): a Cham mosque today")
M(["f4"], (105.6, 11.6, 4.0), (105.8, 11.4, 3.4),
  [dict(k="blob", pts=CAMBODIA, at=0.0, fill="#d8cfb0", fa=0.22),
   dict(k="line", pts=[(104.9, 11.57), (105.4, 11.3), (106.0, 10.95)], at=0.6, draw=2.2, color=ROUTE, lw=5),
   dict(k="line", pts=[(105.46, 11.99), (105.9, 11.6), (106.3, 11.3)], at=1.2, draw=2.2, color=ROUTE, lw=5),
   mk("saigon", "វៀតណាម", "Vietnam", 2.6, "r"),
   dict(k="note", km="ប្រហែល ១៥០,០០០ នាក់ ត្រូវ បាន បណ្ដេញ ឆ្នាំ ១៩៧៥", en="About 150,000 ethnic Vietnamese expelled, 1975",
        cls="record", at=3.0, x=80, y=760)],
  badge="map_recon", note="Schematic: direction of the 1975 expulsions · modern borders")
NOTE(["f5"], "សាលក្រម អង្គជំនុំជម្រះវិសាមញ្ញ ឆ្នាំ ២០១៨", "What the tribunal found (Case 002/02, 16 Nov 2018)", [
    ("ជនជាតិ វៀតណាម · អំពើប្រល័យពូជសាសន៍", "Vietnamese: genocide. Upheld on appeal, 22 Sep 2022", "final"),
    ("ជនជាតិ ចាម · អំពើប្រល័យពូជសាសន៍", "Cham: genocide found by the Trial Chamber (Nuon Chea); no appeal, he died "
                                        "in 2019", "trial finding"),
    ("ព្រះពុទ្ធសាសនិក · អតីតមន្ត្រីសាធារណរដ្ឋ", "Buddhists, former Republic officials: persecution, a crime "
                                              "against humanity", "upheld")],
    foot="Sources: ECCC Trial Judgement E465 (2018), Supreme Court Chamber F76 (2022)")

# ================================================================ 7. S-21 AND THE SECURITY SYSTEM (9:15 - 10:45)
CH(7, "មន្ទីរ ស-២១", "S-21 and the Security System", "1975 – 1979", under=lambda: T.make_classroom("bars"),
   music="silence", amb="none", dark=0.2)
AP("tuol_sleng_museum_entrance_2013.jpg", ["q7"], side="r", sfx=("monbell",))
AP("tuol_sleng_courtyard_2006.jpg", ["g1"], side="l")
AP("duch_testifies_eccc_jul2009.jpg", ["g2"], side="r", note="Photo: Duch at his trial, July 2009")
S(["g3"], lambda: T.make_classroom("bars"), cam((1200, 820, 1.1), (1200, 860, 1.24)), badge="symbol",
  note="Symbol: an empty room (nothing is depicted)", dark=0.25, trans="redraw")
AP("tuol_sleng_empty_classroom_2013.jpg", ["g4"], side="l")
AP("choeung_ek_stupa_lawn_2017.jpg", ["g5"], side="r")
MF("survivors_bou_meng_chum_mey_vann_nath_aug2010.jpg", ["g6"],
   note="Bou Meng (d. 2026), Chum Mey and Vann Nath (d. 2011) in 2010")
NOTE(["g7"], "មន្ទីរ ឃុំឃាំង ទូទាំង ប្រទេស", "A nationwide system", [
    ("មន្ទីរ ឃុំឃាំង ដែល បាន កត់ត្រា", "Prisons mapped by DC-Cam", "196"),
    ("អង្គជំនុំជម្រះ៖ មន្ទីរ សន្ដិសុខ យ៉ាងតិច", "ECCC: security centres, at least", "200"),
    ("រណ្ដៅ សព ដែល បាន គូរ ផែនទី", "Mass-grave pits mapped by DC-Cam", "19,733")],
    foot="Sources: DC-Cam Mapping Project; ECCC Trial Judgement E465 para 294")
MEMO(["s7"], lambda: T.make_fields("grey", night=True), cam((1200, 800, 1.1), (1200, 760, 1.2)), dark=0.25,
     trans="smoke")
S([], lambda: T.make_altar("morning", lit_at=None), cam((1160, 700, 1.9), (1160, 690, 2.05)), min_d=5.0, pre=0,
  post=0, badge="symbol", note="A candle for those who did not come back", era="present", trans="smoke")

# ================================================================ 8. PURGES WITHIN (10:45 - 11:45)
CH(8, "ការបោសសម្អាត ផ្ទៃក្នុង", "Purges Within", "1976 – 1978", under=lambda: T.make_classroom("bars"),
   music="purge", amb="none", dark=0.1)
Q("q8")
AP("tuol_sleng_facade_barbed_wire_2019.jpg", ["h1"], side="r")
M(["h2"], KH, (104.6, 13.0, 5.5),
  [dict(k="blob", pts=CAMBODIA, at=0.0, fill="#d8cfb0", fa=0.22),
   dict(k="label", lon=104.6, lat=13.25, km="ភូមិភាគឧត្តរ", en="North Zone", at=0.8, size=34),
   mk("kthom", "កំពង់ធំ", "Kampong Thom", 1.2, "r")], badge="map",
  note="Zone names only; boundaries not drawn · modern borders")
M(["h3"], KH, (105.4, 11.9, 5.0),
  [dict(k="blob", pts=CAMBODIA, at=0.0, fill="#d8cfb0", fa=0.22),
   dict(k="label", lon=105.75, lat=11.75, km="ភូមិភាគបូព៌ា", en="East Zone", at=0.6, size=34),
   dict(k="line", pts=[(105.5, 11.7), (104.6, 12.3), (103.5, 12.9)], at=2.0, draw=2.6, color="#1f5cff", lw=6),
   mk("bb", "ភូមិភាគពាយ័ព្យ", "Northwest", 4.0, "r")], badge="map_recon",
  note="Schematic: East Zone people deported to the northwest, 1978 · modern borders")
S(["h4"], lambda: T.make_exodus("grey", city=False, carts=False, people=[grp(0.6, *T.crowd(16, 13, kinds=[
    "blue_m", "blue_w", "child_k", "blue_w", "blue_m"]))]), cam((1150, 1000, 1.3), (1350, 990, 1.36)), badge="recon",
  note="Reconstruction: East Zone deportees, 1978")
AP("heng_samrin_2019.jpg", ["h5"], side="l", note="Photo: Heng Samrin in 2019")

# ================================================================ 9. WAR AND COLLAPSE (11:45 - 13:00)
CH(9, "សង្គ្រាម និង ការដួលរលំ", "War and Collapse", "1975 – 1979", under=lambda: Y.make_border("night", heli=False),
   music="war75", amb="night")
Q("q9")
M(["i1"], (105.0, 11.4, 4.6), (105.4, 11.2, 4.0),
  [dict(k="blob", pts=CAMBODIA, at=0.0, fill="#d8cfb0", fa=0.22),
   dict(k="label", lon=103.9, lat=10.05, km="កោះ ដែល មាន ជម្លោះ", en="Disputed islands", at=0.6, size=26),
   dict(k="line", pts=[(105.9, 11.0), (106.2, 11.4), (106.1, 11.9), (106.4, 12.3)], at=1.6, draw=2.0,
        color="#9a3a2a", lw=6, dash=[4, 6]),
   dict(k="label", lon=106.9, lat=11.6, km="ព្រំដែន", en="Border clashes", at=2.4, size=26)],
  badge="map_recon", note="Schematic: areas of the 1975–78 clashes · who struck first in 1975 is disputed")
S(["i2"], lambda: Y.make_border("night", flashes=True, heli=False), cam((1200, 700, 1.05), (1300, 660, 1.18)),
  badge="recon", note="Reconstruction: fighting far away (schematic)")
AP("december_2_front_memorial_snuol.jpg", ["i3"], side="r", note="Modern photo (2015) of the 2 December monument")
AP("map_vietnamese_invasion_dec1978_jan1979.png", ["i4"], side="c", badge="map", tilt=0.0)
AP("cia_presidential_briefing_kampuchea_16jan1979.jpg", ["i5"], side="l", badge="document", focus=(0.5, 0.2))
MEMO(["s8"], lambda: T.make_exodus("mist", city=False, carts=False, home=True,
                                    people=[grp(0.6, F(900, 1220, 320, "sophal_k", "idle", 60, 31))]),
     cam((1000, 1000, 1.45), (1050, 990, 1.5)))

# ================================================================ 10. AFTER THE DARKNESS (13:00 - 14:15)
CH(10, "ក្រោយ ភាពងងឹត", "After the Darkness", "1979 →", under=lambda: T.make_exodus("mist", home=True, city=True,
                                                                                 carts=False),
   music="after", amb="farm")
Q("q10")
MEMO(["s9"], lambda: T.make_exodus("mist", city=True, carts=False, home=True,
                                    people=[grp(0.6, F(1250, 1150, 300, "sophal_k", "walk_slow", -90, 32, vx=-16),
                                                F(900, 1170, 300, "mom75", "idle", 60, 33),
                                                F(1010, 1176, 200, "vuthy_k", "idle", 60, 34))]),
     cam((1100, 980, 1.55), (1080, 980, 1.62)))
S(["j1"], lambda: T.make_exodus("mist", city=True, carts=False, home=True,
                                people=[grp(0.6, *T.crowd(12, 17, vx=-24, kinds=["worker_m", "worker_w", "child_k",
                                                                                 "worker_w"]))]),
  cam((1250, 980, 1.25), (1150, 980, 1.3)), badge="recon", note="Reconstruction: survivors walking home, 1979")
AP("tuol_sleng_museum_entrance_2013.jpg", ["j2"], side="l", note="Modern photo (2013)")
AP("eccc_main_building_2009.jpg", ["j3", "j4"], side="r")
AP("eccc_case002_01_verdict_7aug2014.jpg", ["j5"], side="l")
NOTE(["j6", "j7"], "តើ មនុស្ស ប៉ុន្មាន នាក់ បាន ស្លាប់?", "How many died? Estimates differ by method", [
    ("ការគូរ ផែនទី រណ្ដៅ សព (DC-Cam)", "Mapping mass graves (DC-Cam): remains counted in graves, mostly the executed",
     "≈ 1.3 million"),
    ("ការសិក្សា ប្រជាសាស្ត្រ", "Population studies (Kiernan; Tabeau & Kheam; Heuveline)", "≈ 1.7–2.2 million"),
    ("អង្គជំនុំជម្រះ ឆ្នាំ ២០១៨", "The tribunal (2018): 'most probable'", "1.5–2 million")],
    foot="About 8 million people lived in Cambodia in 1975. The often-quoted 2.5 million covers 1970–1979; "
         "3.3 million (1983) is judged too high.", min_d=18.0)
S(["j8"], lambda: T.make_memorial("morning", people=[
    grp(0.6, *[F(700 + k * 170, 1150 + (k % 2) * 20, 300, ["mourner_m", "mourner_w", "kh_monk", "mourner_w",
                                                           "mourner_m", "kh_monk", "mourner_w"][k], "pray", 0, 90 + k)
               for k in range(7)])]),
  cam((1250, 880, 1.15), (1250, 880, 1.25)), badge="recon",
  note="Reconstruction: the National Day of Remembrance, 20 May", era="present", trans="smoke", sfx=("monbell",))

# ================================================================ CLOSING (14:15 - 15:00)
CHAPTERS.append(len(SHOTS))
GUIDE("m10", lambda m: T.make_altar("morning", lit_at=1.6, people=[grp(0.85, malis(1500, 1450, 820, "kneel_pray", -30,
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
    return [("កម្ពុជាប្រជាធិបតេយ្យ ១៩៧៥–១៩៧៩ · DEMOCRATIC KAMPUCHEA 1975–1979 · WE REMEMBER",
             ["An educational documentary in pencil-and-charcoal 2D animation, maps and authentic archival images",
              "Narration: Khmer · Subtitles: English and Khmer",
              "Yeay Sophal, Malis and their family are fictional, drawn from many survivors' stories",
              "Dedicated to the victims and to the survivors of Democratic Kampuchea"]),
            ("SOURCES PROVIDED", [
                "Khamboly Dy, ប្រវត្តិសាស្ត្រកម្ពុជាប្រជាធិបតេយ្យ (DC-Cam), via MoEYS Sala Digital",
                "DC-Cam, ប្រវត្តិសាស្ត្រសង្ខេបរបស់ខ្មែរក្រហម (Cambodia Tribunal Monitor)",
                "Khmer Wikipedia: កម្ពុជាប្រជាធិបតេយ្យ · Grade 9 and Grade 12 history lessons (EBC; Meas Phyrun)",
                "Scribd study sheet 'សម័យកម្ពុជាប្រជាធិបតេយ្យ ឬ ប៉ុល ពត' (lead only)"]),
            ("MAIN REFERENCES", [
                "Extraordinary Chambers in the Courts of Cambodia: Case 001 (2010, 2012); Case 002/01 (2014, 2016);",
                "Case 002/02 Trial Judgement (2018) and Supreme Court Chamber Appeal (2022)",
                "Khamboly Dy, A History of Democratic Kampuchea (1975–1979), DC-Cam (2007)",
                "DC-Cam Mapping Project · Tuol Sleng Genocide Museum",
                "Library of Congress, Cambodia: A Country Study (ed. R. Ross, 1987)",
                "P. Heuveline (2001; 2015) · B. Kiernan (2003) · E. Tabeau & They Kheam (2009, via press reports)",
                "F. Ponchaud, Cambodia: Year Zero (1978) · A. Ers (2011)",
                "Sub-Decree No. 19 on the National Day of Remembrance (14 Feb 2018)",
                "Full list with links and access dates: docs/research_brief.md"]),
            ("SURVIVOR TESTIMONY", ["Sim Soth (Koy), quoted in Khamboly Dy, A History of Democratic Kampuchea, p. 16"]),
            ("ARCHIVES FOR FURTHER RESEARCH", [
                "Documentation Center of Cambodia · Tuol Sleng Genocide Museum · Bophana Audiovisual Resource Center",
                "No S-21 prisoner portraits are shown in this film."]),
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


# chapter start targets (s) from the brief: 0:45 2:00 3:30 5:00 6:30 7:45 9:15 10:45 11:45 13:00; closing 14:15
TARGETS = [45, 120, 210, 300, 390, 465, 555, 645, 705, 780, 855]
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
