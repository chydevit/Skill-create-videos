"""Example episode (Khmer only), short 3-scene version: greetings, colors, goodbye.
Everything is spoken and shown in Khmer. Copy to <project>/script_data.py.
Names: Milo = មីឡូ, Luna = លូណា, Bobo = បូបូ.
"""
from cartoon_dsl import *  # noqa: F401,F403

language("khmer")
TITLE = "Milo and Luna Khmer"          # used for the output file name only

SCENES = []

SCENES.append({"name": "good_morning", "set": "house", "target": 50, "beats": [
    A(6.0, [("card", "ដំណើរផ្សងព្រេងដ៏រីករាយ\nរបស់ មីឡូ និង លូណា", WHITE, 5.5, "title"),
            ("sfx", "birds"), ("cam", "wide", 0.1)]),
    A(3.2, [("prop", "door", "open"), ("sfx", "door"),
            (0.6, "walk", "milo", (-2.3, 1.3), 1.2),
            (1.85, "walk", "milo", (-0.9, 0.2), 1.5),
            (0.2, "walk", "luna", (0.9, 0.2), 2.8),
            (0.8, "cam", "two", 2.4)]),
    L("milo", "អរុណសួស្តី លូណា!", ev=[("act", "milo", "wave", 1.8)]),
    L("luna", "អរុណសួស្តី មីឡូ!", ev=[("act", "luna", "wave", 1.8)]),
    L("milo", "តើឯងសុខសប្បាយទេ?"),
    L("luna", "ខ្ញុំសុខសប្បាយ! អរគុណ។ ចុះឯងវិញ?", ev=[("act", "luna", "nod", 1.0)]),
    L("milo", "ខ្ញុំសប្បាយចិត្តណាស់!", ev=[("act", "milo", "jump", 0.9), ("sfx", "boing")]),
    A(2.4, [("prop", "bobo", "fly_in"), ("sfx", "flutter"), (1.4, "sfx", "tweet"),
            ("cam", "three", 1.8)]),
    L("bobo", "អរុណសួស្តី!", ev=[("act", "bobo", "flap", 1.4)]),
    laugh(),
    L("narr", "អរុណសួស្តី!", card=("អរុណសួស្តី", ORANGE)),
    L("milo", "ខ្ញុំសប្បាយចិត្ត!", card=("សប្បាយចិត្ត", YELLOW),
      ev=[("face", "milo", "excited", 2.0), ("act", "milo", "jump", 0.9)]),
    *say_it("សប្បាយចិត្ត"),
    L("luna", "មីឡូ ជាមិត្តភក្តិរបស់ខ្ញុំ!", card=("មិត្តភក្តិ", PINK),
      ev=[("act", "luna", "hug", 2.2), ("act", "milo", "hug", 2.2)]),
    L("narr", "តើប្អូនអាចនិយាយថា អរុណសួស្តី បានទេ?", gap=0.2, ev=[("cam", "front", 1.5)]),
    P(3.0),
    L("all", "អរុណសួស្តី!", ev=[("act", w, "wave", 1.8) for w in ALL3]),
    L("narr", "ពូកែណាស់!", ev=[("sfx", "sparkle"), ("prop", "fx", "stars")]),
    A(1.2),
]})

SCENES.append({"name": "colors", "set": "garden", "target": 50, "beats": [
    A(3.0, [("walk", "milo", (-1.0, 0.0), 2.8), ("walk", "luna", (0.0, 0.0), 2.8),
            ("sfx", "birds"), ("cam", "wide", 0.1), (0.5, "cam", "garden", 2.5)]),
    L("luna", "មើល! ផ្កាពណ៌ក្រហម។", card=("ក្រហម", RED),
      ev=[("act", "luna", "point", 2.5), ("prop", "red_flower", "bounce"),
          ("cam", "flower", 1.2)]),
    L("milo", "ក្រហម!"),
    *say_it("ក្រហម"),
    A(2.2, [("prop", "butterfly", "fly_in"), ("cam", "garden", 1.5)]),
    L("milo", "មើល! មេអំបៅពណ៌ខៀវ។", card=("ខៀវ", BLUE), ev=[("act", "milo", "point", 2.5)]),
    L("bobo", "ខៀវ! ដូចខ្ញុំ!", ev=[("act", "bobo", "flap", 1.5)]),
    L("luna", "មើលទៅលើ! ព្រះអាទិត្យពណ៌លឿង។", card=("លឿង", YELLOW),
      ev=[("act", "luna", "point_up", 2.8), ("cam", "sky", 1.5)]),
    L("milo", "ហើយដើមឈើពណ៌បៃតង។", card=("បៃតង", GREEN),
      ev=[("act", "milo", "point", 2.5), ("cam", "tree", 1.5)]),
    A(2.6, [("cam", "flower", 1.2), ("prop", "bobo", "fly_to", "flower"),
            ("sfx", "flutter"), (1.9, "sfx", "boing"), (1.9, "prop", "red_flower", "bounce")]),
    L("bobo", "វ៉ាវ! ពណ៌ច្រើនណាស់!", ev=[("act", "bobo", "flap", 1.2)]),
    laugh(),
    L("narr", "តើព្រះអាទិត្យពណ៌អ្វី?", gap=0.2, ev=[("cam", "garden", 1.5)]),
    P(3.0),
    L("milo", "ពណ៌លឿង!", ev=[("act", "milo", "jump", 0.9), ("sfx", "boing")]),
    L("narr", "ពូកែណាស់!", ev=[("sfx", "sparkle"), ("prop", "fx", "stars")]),
    A(1.2),
]})

SCENES.append({"name": "goodbye", "set": "sunset", "target": 25, "beats": [
    A(1.5, [("sfx", "birds_soft"), ("cam", "wide", 0.1), ("music", "soft"),
            (0.3, "cam", "three", 1.5)]),
    L("milo", "ថ្ងៃនេះយើងរៀនបានច្រើនណាស់!", ev=[("act", "milo", "clap", 1.2)]),
    L("luna", "ពូកែណាស់!", ev=[("act", "luna", "jump", 0.9)]),
    L("bobo", "ជួបគ្នាលើកក្រោយ!", ev=[("act", "bobo", "flap", 1.6)]),
    L("all", "លាហើយ!", ev=[("act", w, "wave", 2.5) for w in ALL3]),
    L("narr", "ហាត់រៀនរាល់ថ្ងៃណា។ លាហើយ មិត្តតូចៗ!",
      ev=[("act", w, "wave", 3.5) for w in ALL3] + [("cam", "front", 2.5)]),
    A(6.0, [("card", "ពូកែណាស់!\nជួបគ្នាលើកក្រោយ!", YELLOW, 6.0, "title"),
            ("sfx", "sparkle"), ("prop", "fx", "stars")] +
        [("act", w, "wave", 6.0) for w in ALL3]),
]})
