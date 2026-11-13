"""Helpers for writing an episode script (the project's script_data.py).

    from cartoon_dsl import *
    language("bilingual")          # "english" | "bilingual" | "khmer"
    TITLE = "Milo & Luna's Happy Adventure"
    SCENES = [ {"name": ..., "set": ..., "target": 60, "beats": [ L(...), P(...), A(...) ]} ]

Beats run one after another:
  L(who, text, ...)  spoken line; its length comes from the generated voice
  P(sec)             pause for the child to answer (shows the "your turn" badge)
  A(sec, ev)         action-only beat (walking, dancing, flying ...)

Events (ev=[...]) are tuples; an optional leading number is an offset in seconds
from the start of the beat:
  ("act", who, action, dur)          wave jump jump3 clap point point_up point_self nod
                                     laugh hug run walk_in_place dance flap yawn dizzy
  ("face", who, mood, dur)           happy sad excited tired surprised
  ("walk", who, (x, y), dur)         walk to a point on the ground
  ("card", text, color, dur, style)  style: word | sentence | number | title
  ("cam", shot, move_dur)            move camera to a named shot of the set
  ("prop", name, action, *args)      set-specific prop animation (see references)
  ("sfx", name)                      pop boing birds birds_soft tweet flutter door sparkle
                                     correct bell claps whoosh yawn
  ("music", mode)                    normal | dance | soft
"""

RED, BLUE, YELLOW, GREEN = "#E53935", "#1E88E5", "#FDD835", "#43A047"
ORANGE, PURPLE, PINK, TEAL = "#FB8C00", "#8E24AA", "#EC407A", "#00ACC1"
BROWN, WHITE = "#8D6E63", "#FFFFFF"
ALL3 = ["milo", "luna", "bobo"]

_STATE = {"language": "english"}

# text shown in the "your turn" badge, per language
UI_DEFAULTS = {
    "english": {"your_turn": "YOUR TURN!"},
    "bilingual": {"your_turn": "YOUR TURN! ដល់វេនប្អូន"},
    "khmer": {"your_turn": "ដល់វេនប្អូន!"},
}


def language(mode):
    """Set the episode language: english, bilingual or khmer."""
    assert mode in ("english", "bilingual", "khmer"), mode
    _STATE["language"] = mode


def current_language():
    return _STATE["language"]


def _default_lang():
    return "km" if _STATE["language"] == "khmer" else "en"


def L(who, text, ev=(), cap=True, gap=0.8, rate=None, card=None, lang=None):
    """A spoken line. lang="km" makes it Khmer speech (edge-tts neural voice)."""
    ev = list(ev)
    if card:
        word, color = card
        ev.insert(0, (0.1, "card", word, color, 3.6, "word"))
    return {"kind": "line", "who": who, "text": text, "ev": ev, "cap": cap,
            "gap": gap, "rate": rate, "lang": lang or _default_lang()}


def K(who, text, **kw):
    """Shortcut for a Khmer line (used in bilingual episodes)."""
    kw["lang"] = "km"
    return L(who, text, **kw)


def P(sec=3.0, ev=(), turn=True):
    return {"kind": "pause", "dur": sec, "ev": list(ev), "turn": turn}


def A(sec, ev=()):
    return {"kind": "action", "dur": sec, "ev": list(ev)}


def laugh(who="all", text=None):
    if text is None:
        text = "ហាហាហា!" if _default_lang() == "km" else "Ha ha ha!"
    return L(who, text, cap=False, gap=0.3,
             ev=[("act", w, "laugh", 1.6) for w in (ALL3 if who == "all" else [who])])


def say_it(word, gap=0.3, pause=2.3, prompt=None):
    """Narrator asks the child to repeat a word, then pauses."""
    if prompt is None:
        prompt = ("និយាយតាម: %s!" if _default_lang() == "km"
                  else "Say: %s!")
    return [L("narr", prompt % word, gap=gap), P(pause)]


COUNT_COLORS = ["#E53935", "#FB8C00", "#FDD835", "#43A047", "#00ACC1", "#1E88E5",
                "#8E24AA", "#EC407A", "#E53935", "#FB8C00"]


def count_line(n, who, word, gap=0.9, rate=None, prop="apple", lang=None):
    """One number of a count: speaks the word, pops the number card, bounces prop n."""
    return L(who, word, cap=False, gap=gap, rate=rate, lang=lang,
             ev=[("card", str(n), COUNT_COLORS[(n - 1) % 10], 1.2, "number"),
                 ("prop", prop, "count", n), ("sfx", "pop")])


NUMS_EN = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten"]
NUMS_KM = ["មួយ", "ពីរ", "បី", "បួន",
           "ប្រាំ", "ប្រាំមួយ",
           "ប្រាំពីរ", "ប្រាំបី",
           "ប្រាំបួន", "ដប់"]
