"""Example episode (bilingual): teaches ENGLISH to Khmer-speaking children.
Characters speak English; the narrator explains in Khmer (K(...) lines);
cards show the English word with its Khmer meaning underneath.
Short 3-scene version: greetings, colors, goodbye. Copy to <project>/script_data.py.
"""
from cartoon_dsl import *  # noqa: F401,F403

language("bilingual")
TITLE = "Milo and Luna Learn English"


def word(en, km, color):
    """Bilingual word card: English on top, Khmer meaning below."""
    return (en + "\n" + km, color)


SCENES = []

SCENES.append({"name": "good_morning", "set": "house", "target": 60, "beats": [
    A(6.0, [("card", "Milo & Luna's\nHappy Adventure", WHITE, 5.5, "title"),
            ("sfx", "birds"), ("cam", "wide", 0.1)]),
    K("narr", "សួស្តីក្មេងៗ! ថ្ងៃនេះ យើងរៀនភាសាអង់គ្លេសជាមួយ មីឡូ លូណា និង បូបូ។", gap=0.4),
    A(3.2, [("prop", "door", "open"), ("sfx", "door"),
            (0.6, "walk", "milo", (-2.3, 1.3), 1.2),
            (1.85, "walk", "milo", (-0.9, 0.2), 1.5),
            (0.2, "walk", "luna", (0.9, 0.2), 2.8),
            (0.8, "cam", "two", 2.4)]),
    L("milo", "Good morning, Luna!", ev=[("act", "milo", "wave", 1.8)]),
    L("luna", "Good morning, Milo!", ev=[("act", "luna", "wave", 1.8)]),
    K("narr", "Good morning មានន័យថា អរុណសួស្តី។",
      ev=[("card", *word("GOOD MORNING", "អរុណសួស្តី", ORANGE), 4.0, "word")]),
    L("narr", "Say: Good morning!", gap=0.3),
    P(3.0),
    L("milo", "How are you today?"),
    L("luna", "I'm great! Thank you.", ev=[("act", "luna", "nod", 1.0)]),
    L("milo", "I'm happy!", card=word("HAPPY", "សប្បាយចិត្ត", YELLOW),
      ev=[("act", "milo", "jump", 0.9), ("sfx", "boing")]),
    K("narr", "Happy មានន័យថា សប្បាយចិត្ត។"),
    *say_it("Happy", prompt="Say: %s!"),
    A(2.4, [("prop", "bobo", "fly_in"), ("sfx", "flutter"), (1.4, "sfx", "tweet"),
            ("cam", "three", 1.8)]),
    L("bobo", "Good morning, friends!", card=word("FRIEND", "មិត្តភក្តិ", PINK),
      ev=[("act", "bobo", "flap", 1.4)]),
    K("narr", "Friend មានន័យថា មិត្តភក្តិ។"),
    laugh(),
    L("narr", "Great job!", ev=[("sfx", "sparkle"), ("prop", "fx", "stars")]),
    A(1.2),
]})

SCENES.append({"name": "colors", "set": "garden", "target": 60, "beats": [
    A(3.0, [("walk", "milo", (-1.0, 0.0), 2.8), ("walk", "luna", (0.0, 0.0), 2.8),
            ("sfx", "birds"), ("cam", "wide", 0.1), (0.5, "cam", "garden", 2.5)]),
    L("luna", "Look! A red flower.", card=word("RED", "ក្រហម", RED),
      ev=[("act", "luna", "point", 2.5), ("prop", "red_flower", "bounce"),
          ("cam", "flower", 1.2)]),
    K("narr", "Red មានន័យថា ពណ៌ក្រហម។"),
    *say_it("Red", prompt="Say: %s!"),
    A(2.2, [("prop", "butterfly", "fly_in"), ("cam", "garden", 1.5)]),
    L("milo", "Look! A blue butterfly.", card=word("BLUE", "ខៀវ", BLUE),
      ev=[("act", "milo", "point", 2.5)]),
    K("narr", "Blue មានន័យថា ពណ៌ខៀវ។"),
    *say_it("Blue", prompt="Say: %s!"),
    L("luna", "Look up! The sun is yellow.", card=word("YELLOW", "លឿង", YELLOW),
      ev=[("act", "luna", "point_up", 2.8), ("cam", "sky", 1.5)]),
    K("narr", "Yellow មានន័យថា ពណ៌លឿង។", ev=[("cam", "garden", 1.5)]),
    A(2.6, [("cam", "flower", 1.2), ("prop", "bobo", "fly_to", "flower"),
            ("sfx", "flutter"), (1.9, "sfx", "boing"), (1.9, "prop", "red_flower", "bounce")]),
    L("bobo", "Wow! So many colors!", ev=[("act", "bobo", "flap", 1.2)]),
    laugh(),
    L("narr", "What color is the sun?", gap=0.2, ev=[("cam", "garden", 1.5)]),
    K("narr", "តើព្រះអាទិត្យពណ៌អ្វី?", gap=0.2),
    P(3.0),
    L("milo", "Yellow!", ev=[("act", "milo", "jump", 0.9), ("sfx", "boing")]),
    L("narr", "Great job!", ev=[("sfx", "sparkle"), ("prop", "fx", "stars")]),
    A(1.2),
]})

SCENES.append({"name": "goodbye", "set": "sunset", "target": 25, "beats": [
    A(1.5, [("sfx", "birds_soft"), ("cam", "wide", 0.1), ("music", "soft"),
            (0.3, "cam", "three", 1.5)]),
    L("milo", "We learned so much today!", ev=[("act", "milo", "clap", 1.2)]),
    L("bobo", "See you next time!", ev=[("act", "bobo", "flap", 1.6)]),
    L("all", "Goodbye!", card=word("GOODBYE", "លាហើយ", PURPLE),
      ev=[("act", w, "wave", 2.5) for w in ALL3]),
    K("narr", "Goodbye មានន័យថា លាហើយ។ ជួបគ្នាលើកក្រោយ!",
      ev=[("act", w, "wave", 3.5) for w in ALL3] + [("cam", "front", 2.5)]),
    A(6.0, [("card", "GREAT JOB!\nពូកែណាស់!", YELLOW, 6.0, "title"),
            ("sfx", "sparkle"), ("prop", "fx", "stars")] +
        [("act", w, "wave", 6.0) for w in ALL3]),
]})
