"""Example episode (English): "Milo & Luna's Happy Adventure" (9 min, 10 scenes).
Copy to <project>/script_data.py to reuse.

Each scene is a list of beats played one after another.
  L(who, text, ...)  - a spoken line (duration comes from the voice audio)
  P(sec)             - a pause so the child can answer ("YOUR TURN!")
  A(sec, ...)        - an action-only beat (walking, dancing, flying ...)

Events (ev=[...]) are tuples. An optional leading number is an offset in
seconds from the start of the beat:
  ("act", who, action, dur, *params)  character animation
  ("face", who, mood, dur)            facial expression
  ("walk", who, (x, y), dur)          walk to a point
  ("card", text, color, dur, style)   on-screen text card
  ("cam", shot, move_dur)             move camera to a named shot
  ("prop", name, action, *params)     scene specific prop animation
  ("sfx", name)                       sound effect
  ("music", mode)                     music mode: normal / dance / soft
"""

from cartoon_dsl import *  # noqa: F401,F403

language("english")
TITLE = "Milo & Luna's Happy Adventure"
NUMS = NUMS_EN

SCENES = []

# ---------------------------------------------------------------- Scene 1
SCENES.append({"name": "good_morning", "target": 62, "beats": [
    A(6.5, [("card", "Milo & Luna's\nHappy Adventure", WHITE, 6.0, "title"),
            ("sfx", "birds"), ("cam", "wide", 0.1)]),
    A(3.2, [("prop", "door", "open"), ("sfx", "door"),
            (0.6, "walk", "milo", (-2.3, 1.3), 1.2),
            (1.85, "walk", "milo", (-0.9, 0.2), 1.5),
            (0.2, "walk", "luna", (0.9, 0.2), 2.8),
            (0.8, "cam", "two", 2.4)]),
    L("milo", "Good morning, Luna!", ev=[("act", "milo", "wave", 1.8)]),
    L("luna", "Good morning, Milo!", ev=[("act", "luna", "wave", 1.8)]),
    L("milo", "How are you today?"),
    L("luna", "I'm great! Thank you. How are you?",
      ev=[("act", "luna", "nod", 1.0)]),
    L("milo", "I'm happy!", ev=[("act", "milo", "jump", 0.9),
                                ("sfx", "boing")]),
    L("luna", "What a sunny day!", ev=[("act", "luna", "point_up", 2.2)]),
    L("milo", "Yes! I love the sun!"),
    A(2.4, [("prop", "bobo", "fly_in"), ("sfx", "flutter"),
            (1.4, "sfx", "tweet"), ("cam", "three", 1.8)]),
    L("bobo", "Good morning!", ev=[("act", "bobo", "flap", 1.4)]),
    laugh(),
    L("narr", "Good morning!", card=("GOOD MORNING", ORANGE)),
    L("milo", "I am happy!", card=("HAPPY", YELLOW),
      ev=[("face", "milo", "excited", 2.0), ("act", "milo", "jump", 0.9)]),
    *say_it("Happy"),
    L("luna", "Milo is my friend!", card=("FRIEND", PINK),
      ev=[("act", "luna", "hug", 2.2), ("act", "milo", "hug", 2.2)]),
    L("milo", "Luna is my friend, too!"),
    *say_it("Friend"),
    L("bobo", "And me! I am your friend!", ev=[("act", "bobo", "flap", 1.5)]),
    L("narr", "Can you say, 'Good morning'?", gap=0.2,
      ev=[("cam", "front", 1.5)]),
    P(3.0),
    L("all", "Good morning!", ev=[("act", "milo", "wave", 1.8),
                                  ("act", "luna", "wave", 1.8),
                                  ("act", "bobo", "flap", 1.8)]),
    L("narr", "Great job!", ev=[("sfx", "sparkle"), ("prop", "fx", "stars")]),
    A(1.4),
]})

# ---------------------------------------------------------------- Scene 2
SCENES.append({"name": "colors", "target": 75, "beats": [
    A(3.0, [("walk", "milo", (-1.0, 0.0), 2.8), ("walk", "luna", (0.0, 0.0), 2.8),
            ("sfx", "birds"), ("cam", "wide", 0.1), (0.5, "cam", "garden", 2.5)]),
    L("milo", "Wow! Look at the garden!", ev=[("face", "milo", "excited", 2)]),
    L("luna", "Look! A red flower.", card=("RED", RED),
      ev=[("act", "luna", "point", 2.5), ("prop", "red_flower", "bounce"),
          ("cam", "flower", 1.2)]),
    L("milo", "Red!"),
    L("narr", "Red. Say it with me: Red!", gap=0.2),
    P(2.2),
    A(2.2, [("prop", "butterfly", "fly_in"), ("cam", "garden", 1.5)]),
    L("milo", "Look! A blue butterfly.", card=("BLUE", BLUE),
      ev=[("act", "milo", "point", 2.5)]),
    L("luna", "Blue!"),
    *say_it("Blue"),
    L("bobo", "Blue! Like me!", ev=[("prop", "bobo", "fly_to", "hop"),
                                    ("act", "bobo", "flap", 1.5)]),
    laugh("milo"),
    L("luna", "Look up! The sun is yellow.", card=("YELLOW", YELLOW),
      ev=[("act", "luna", "point_up", 2.8), ("cam", "sky", 1.5)]),
    L("milo", "Yellow!"),
    *say_it("Yellow"),
    L("milo", "And the tree is green.", card=("GREEN", GREEN),
      ev=[("act", "milo", "point", 2.5), ("cam", "tree", 1.5)]),
    L("luna", "Green!"),
    *say_it("Green"),
    L("luna", "I see a pink flower, too!", card=("PINK", PINK),
      ev=[("prop", "pink_flower", "bounce"), ("act", "luna", "point", 2.0),
          ("cam", "garden", 1.4)]),
    L("milo", "And a purple flower!", card=("PURPLE", PURPLE),
      ev=[("prop", "purple_flower", "bounce"), ("act", "milo", "point", 2.0)]),
    A(2.6, [("cam", "flower", 1.2), ("prop", "bobo", "fly_to", "flower"),
            ("sfx", "flutter"), (1.9, "sfx", "boing"),
            (1.9, "prop", "red_flower", "bounce")]),
    L("bobo", "Wow! So many colors!", ev=[("act", "bobo", "flap", 1.2)]),
    laugh(),
    L("narr", "Red.", gap=0.3, ev=[("card", "RED", RED, 1.3, "word")]),
    L("narr", "Blue.", gap=0.3, ev=[("card", "BLUE", BLUE, 1.3, "word")]),
    L("narr", "Yellow.", gap=0.3, ev=[("card", "YELLOW", YELLOW, 1.3, "word")]),
    L("narr", "Green.", gap=0.5, ev=[("card", "GREEN", GREEN, 1.4, "word"),
                                     ("cam", "garden", 1.5)]),
    L("narr", "What color is the sun?", gap=0.2),
    P(3.0),
    L("milo", "Yellow!", ev=[("act", "milo", "jump", 0.9), ("sfx", "boing")]),
    L("narr", "Great job!", ev=[("sfx", "sparkle"), ("prop", "fx", "stars")]),
    A(1.4),
]})

# ---------------------------------------------------------------- Scene 3
count1 = [count_line(i + 1, "ml", w) for i, w in enumerate(NUMS)]
count2 = [count_line(i + 1, "all", w, gap=1.25) for i, w in enumerate(NUMS)]
SCENES.append({"name": "counting", "target": 75, "beats": [
    A(2.6, [("walk", "milo", (-1.3, 0.8), 2.4), ("walk", "luna", (1.3, 0.8), 2.4),
            ("sfx", "birds"), ("cam", "wide", 0.1), (0.6, "cam", "apples", 2.0)]),
    L("luna", "Look! Apples!", ev=[("act", "luna", "point", 2.0),
                                   ("face", "luna", "surprised", 1.5)]),
    L("milo", "Let's count the apples!", ev=[("act", "milo", "clap", 1.2)]),
    L("luna", "Yes! Let's count slowly.", ev=[("act", "luna", "nod", 1.0)]),
    *count1,
    L("milo", "Ten apples!", ev=[("act", "milo", "jump", 0.9),
                                 ("sfx", "boing")]),
    L("bobo", "My turn! One, two, three... TEN!", rate=235,
      ev=[("act", "bobo", "flap", 2.0), (1.5, "act", "bobo", "dizzy", 2.0),
          (1.6, "sfx", "boing")]),
    laugh("luna"),
    L("luna", "Slowly, Bobo!", ev=[("act", "luna", "nod", 1.0)]),
    L("bobo", "Oops!", ev=[("face", "bobo", "surprised", 1.2)]),
    L("narr", "Let's count together. Count with us!",
      ev=[("prop", "apple", "reset"), ("cam", "apples_close", 1.5)]),
    *count2,
    L("narr", "Ten apples! Great counting!",
      ev=[("sfx", "sparkle"), ("prop", "fx", "stars"),
          ("act", "milo", "jump", 0.9), ("act", "luna", "jump", 0.9)]),
    L("narr", "How many apples?", gap=0.2),
    P(2.8),
    L("all", "Ten!", card=("TEN", GREEN), ev=[("sfx", "correct")]),
    L("bobo", "Ten! Ten apples!", ev=[("act", "bobo", "flap", 1.5)]),
    L("luna", "Apples are yummy!", ev=[("face", "luna", "happy", 2.0)]),
    A(1.4),
]})

# ---------------------------------------------------------------- Scene 4
def animal(asker, answer, name, sound_who, sound, color, shot, extra=()):
    return [
        L(asker, "What is this?", ev=[("cam", shot, 1.3)]),
        L(answer, "It's a %s!" % name, card=(name.upper(), color),
          ev=[("act", answer, "point", 2.0)]),
        L(sound_who, sound, ev=[("prop", name, "happy")]) if sound else
        A(1.8, [("prop", name, "hop"), ("sfx", "boing")]),
        *extra,
        L("narr", "%s." % name.capitalize(), gap=0.4),
        P(2.2),
    ]


SCENES.append({"name": "animals", "target": 75, "beats": [
    A(2.4, [("walk", "milo", (-2.4, 0.2), 2.4), ("walk", "luna", (-1.5, 0.0), 2.4),
            ("sfx", "birds"), ("cam", "wide", 0.1)]),
    L("milo", "Look! A farm!", ev=[("act", "milo", "point", 2.0)]),
    L("luna", "Let's see the animals!", ev=[("act", "luna", "clap", 1.2)]),
    *animal("luna", "milo", "cat", "cat", "Meow!", ORANGE, "cat"),
    *animal("milo", "luna", "dog", "dog", "Woof! Woof!", BROWN, "dog"),
    *animal("luna", "bobo", "duck", "duck", "Quack! Quack!", YELLOW, "duck"),
    *animal("milo", "luna", "cow", "cow", "Moo!", "#6D4C41", "cow"),
    *animal("luna", "milo", "rabbit", None, None, PINK, "rabbit",
            extra=[L("luna", "Hop, hop, hop!",
                     ev=[("act", "luna", "jump", 0.8), ("prop", "rabbit", "hop")])]),
    L("bobo", "What animal says 'woof woof'?", gap=0.2,
      ev=[("cam", "wide", 1.5), ("act", "bobo", "flap", 1.2)]),
    P(3.0),
    L("dog", "Woof! Woof!", ev=[("prop", "dog", "happy"), ("cam", "dog", 1.0)]),
    L("milo", "A dog!", ev=[("act", "milo", "jump", 0.9), ("sfx", "boing")]),
    L("narr", "Yes! A dog! Great job!",
      ev=[("sfx", "sparkle"), ("prop", "fx", "stars"), ("cam", "wide", 1.5)]),
    L("milo", "I love animals!", ev=[("face", "milo", "happy", 2.0)]),
    L("luna", "Me too! Bye bye, animals!", ev=[("act", "luna", "wave", 2.0),
                                              ("act", "milo", "wave", 2.0)]),
    A(1.4),
]})

# ---------------------------------------------------------------- Scene 5
def food(word, color, prop):
    return [L("narr", "%s." % word, card=(word.upper(), color), gap=0.4,
              ev=[("prop", prop, "bounce"), ("sfx", "pop")]),
            P(2.2)]


SCENES.append({"name": "picnic", "target": 75, "beats": [
    A(2.0, [("sfx", "birds"), ("cam", "wide", 0.1)]),
    L("luna", "Picnic time!", ev=[("act", "luna", "clap", 1.2)]),
    L("milo", "Yay!", ev=[("act", "milo", "jump", 0.9), ("sfx", "boing")]),
    L("narr", "Let's learn some food and drinks.", ev=[("cam", "food", 1.5)]),
    *food("Apple", RED, "apple"),
    *food("Banana", YELLOW, "banana"),
    *food("Bread", BROWN, "bread"),
    *food("Milk", TEAL, "milk"),
    *food("Water", BLUE, "water"),
    L("milo", "I like apples.", ev=[("cam", "picnic", 1.4),
                                    ("prop", "apple", "bounce"),
                                    ("act", "milo", "point", 1.8)]),
    L("luna", "I like bananas.", ev=[("prop", "banana", "bounce"),
                                     ("act", "luna", "point", 1.8)]),
    L("bobo", "I like everything!", ev=[("act", "bobo", "flap", 1.6)]),
    laugh(),
    L("luna", "Let's eat! Mmm, yummy!", ev=[("face", "luna", "happy", 2.5),
                                            ("prop", "banana", "bounce")]),
    L("narr", "What do you like?", ev=[("card", "What do you like?", PURPLE,
                                        3.0, "sentence")]),
    L("milo", "Luna, what do you like?",
      ev=[("card", "What do you like?", PURPLE, 3.0, "sentence")]),
    L("luna", "I like bananas.",
      ev=[("card", "I like bananas.", ORANGE, 3.0, "sentence"),
          ("prop", "banana", "bounce")]),
    L("luna", "Milo, what do you like?"),
    L("milo", "I like apples and milk!",
      ev=[("card", "I like apples and milk!", RED, 3.0, "sentence"),
          ("prop", "milk", "bounce")]),
    L("bobo", "I like water! Yummy!", ev=[("prop", "water", "bounce")]),
    L("milo", "Can I have some milk, please?",
      ev=[("card", "Can I have some milk, please?", TEAL, 3.5, "sentence")]),
    L("luna", "Here you are!", ev=[("prop", "milk", "give"),
                                   ("card", "Here you are!", PURPLE, 2.5,
                                    "sentence")]),
    L("milo", "Thank you!", ev=[("card", "Thank you!", ORANGE, 2.5, "sentence"),
                                ("act", "milo", "nod", 1.0)]),
    L("narr", "What do YOU like?", gap=0.2, ev=[("cam", "front", 1.5)]),
    P(4.0),
    L("narr", "Yummy! Great job!", ev=[("sfx", "sparkle"),
                                      ("prop", "fx", "stars")]),
    A(1.4),
]})

# ---------------------------------------------------------------- Scene 6
def move(word, color, acts, dur=3.2, cam=None):
    ev = [("card", word.upper(), color, dur + 0.6, "word")]
    ev += [("act", w, a, dur) for w, a in acts]
    if cam:
        ev.append(("cam", cam, 1.2))
    return [L("narr", word + "!", gap=0.1, ev=ev), A(dur)]


ALL3 = ["milo", "luna", "bobo"]
SCENES.append({"name": "actions", "target": 75, "beats": [
    A(2.0, [("sfx", "kids"), ("cam", "wide", 0.1)]),
    L("milo", "Let's play at the playground!",
      ev=[("act", "milo", "wave", 1.6)]),
    L("luna", "Let's run!", ev=[("act", "luna", "clap", 1.0)]),
    *move("Run", RED, [("milo", "run"), ("luna", "run")], cam="wide"),
    L("milo", "Now let's walk."),
    *move("Walk", GREEN, [("milo", "walk_in_place"), ("luna", "walk_in_place")]),
    L("milo", "Let's jump!", ev=[("cam", "play", 1.3)]),
    L("all", "Jump! Jump! Jump!", card=("JUMP", ORANGE),
      ev=[("act", w, "jump3", 3.0) for w in ALL3] +
         [(0.0, "sfx", "boing"), (1.0, "sfx", "boing"), (2.0, "sfx", "boing")]),
    L("luna", "Now clap your hands!", card=("CLAP", PURPLE)),
    A(2.6, [("act", w, "clap", 2.6) for w in ALL3] + [("sfx", "claps")]),
    L("bobo", "Now dance!", card=("DANCE", PINK),
      ev=[("music", "dance")]),
    A(5.5, [("act", w, "dance", 5.5) for w in ALL3] +
        [("cam", "dance", 2.5)]),
    L("narr", "Stand up and do it with us!", gap=0.2,
      ev=[("music", "normal"), ("cam", "front", 1.5)]),
    *move("Walk", GREEN, [(w, "walk_in_place") for w in ALL3]),
    *move("Jump", ORANGE, [(w, "jump3") for w in ALL3]),
    *move("Run", RED, [(w, "run") for w in ALL3]),
    *move("Clap", PURPLE, [(w, "clap") for w in ALL3]),
    L("narr", "Dance!", gap=0.1, card=("DANCE", PINK),
      ev=[("music", "dance")]),
    A(4.0, [("act", w, "dance", 4.0) for w in ALL3]),
    L("narr", "Wonderful! Great job!",
      ev=[("music", "normal"), ("sfx", "sparkle"), ("prop", "fx", "stars")]),
    L("all", "That was fun!", ev=[("act", w, "jump", 0.9) for w in ALL3]),
    L("bobo", "Look at me! I can fly!", ev=[("prop", "bobo", "loop"),
                                            ("sfx", "flutter")]),
    A(2.0),
    laugh(),
    A(1.4),
]})

# ---------------------------------------------------------------- Scene 7
def feel(word, color, emoji, who, mood):
    return [L("narr", word + ".", card=(word.upper(), color), gap=0.4,
              ev=[("prop", "emoji", "show", emoji), ("face", who, mood, 6.5),
                  ("cam", "c_" + who, 1.2),
                  ("act", who, "jump", 0.9) if mood in ("happy", "excited")
                  else ("act", who, "nod", 1.0)]),
            L(who, "I am %s." % word.lower(), gap=0.4),
            P(2.0)]


SCENES.append({"name": "feelings", "target": 65, "beats": [
    A(2.0, [("sfx", "birds"), ("cam", "wide", 0.1)]),
    L("milo", "Let's play a feelings game!", ev=[("act", "milo", "clap", 1.2)]),
    L("luna", "Let's make faces! How do we feel?",
      ev=[("act", "luna", "wave", 1.6)]),
    *feel("Happy", YELLOW, "happy", "milo", "happy"),
    *feel("Sad", BLUE, "sad", "luna", "sad"),
    *feel("Excited", ORANGE, "excited", "milo", "excited"),
    *feel("Tired", PURPLE, "tired", "bobo", "tired"),
    *feel("Surprised", PINK, "surprised", "luna", "surprised"),
    L("milo", "I am happy!", ev=[("face", "milo", "happy", 2.0),
                                 ("act", "milo", "jump", 0.9),
                                 ("prop", "emoji", "show", "happy"),
                                 ("cam", "two", 1.2)]),
    L("luna", "I am excited!", ev=[("face", "luna", "excited", 2.0),
                                   ("act", "luna", "jump", 0.9),
                                   ("prop", "emoji", "show", "excited")]),
    A(2.2, [("act", "bobo", "yawn", 2.2), ("sfx", "yawn"),
            ("face", "bobo", "tired", 4.5), ("cam", "bobo", 1.2)]),
    L("bobo", "I am tired.", ev=[("prop", "emoji", "show", "tired")]),
    L("luna", "Oh, Bobo! Wake up!", ev=[("act", "luna", "clap", 1.0),
                                        ("cam", "three", 1.2)]),
    A(1.2, [("act", "bobo", "jump", 0.9), ("sfx", "boing"),
            ("face", "bobo", "surprised", 1.2)]),
    L("bobo", "I am awake! I am happy!", ev=[("face", "bobo", "happy", 2.5),
                                             ("act", "bobo", "flap", 1.5)]),
    laugh("milo"),
    L("narr", "How are you today?", gap=0.2,
      ev=[("cam", "front", 1.5), ("prop", "emoji", "show", "none")]),
    P(3.0),
    L("luna", "You can say, 'I am happy!'",
      ev=[("card", "I am happy!", YELLOW, 3.0, "sentence"),
          ("face", "luna", "happy", 3.0), ("act", "luna", "wave", 1.6)]),
    A(1.4),
]})

# ---------------------------------------------------------------- Scene 8
def talk(who, text, color, ev=()):
    return L(who, text, gap=1.0,
             ev=[("card", text, color, 99, "sentence")] + list(ev))


SCENES.append({"name": "conversation", "target": 55, "beats": [
    A(2.0, [("sfx", "birds"), ("cam", "wide", 0.1), (0.5, "cam", "two", 1.5)]),
    talk("milo", "Hello!", ORANGE, [("act", "milo", "wave", 1.6)]),
    talk("luna", "Hello!", PURPLE, [("act", "luna", "wave", 1.6)]),
    talk("milo", "What is your name?", ORANGE),
    talk("luna", "My name is Luna. What is your name?", PURPLE,
         [("act", "luna", "nod", 1.0)]),
    talk("milo", "My name is Milo.", ORANGE, [("act", "milo", "point_self", 1.8)]),
    talk("luna", "How are you?", PURPLE),
    talk("milo", "I'm great, thank you!", ORANGE, [("act", "milo", "jump", 0.9)]),
    A(1.8, [("prop", "bobo", "fly_in"), ("sfx", "flutter"),
            ("cam", "three", 1.4)]),
    talk("bobo", "And my name is Bobo!", BLUE, [("act", "bobo", "flap", 1.6)]),
    talk("all", "Hello, Bobo!", GREEN,
         [("act", "milo", "wave", 1.6), ("act", "luna", "wave", 1.6)]),
    talk("bobo", "Nice to meet you!", BLUE, [("act", "bobo", "flap", 1.4)]),
    talk("ml", "Nice to meet you, too!", GREEN),
    laugh(),
    L("narr", "Now you try! Say: My name is...", gap=0.2,
      ev=[("card", "My name is ...", TEAL, 5.5, "sentence"),
          ("cam", "front", 1.5)]),
    P(3.2),
    L("narr", "Wonderful!", ev=[("sfx", "sparkle"), ("prop", "fx", "stars")]),
    L("narr", "How are you?", gap=0.2,
      ev=[("card", "How are you?", PURPLE, 3.0, "sentence")]),
    P(2.8),
    L("milo", "I'm great, thank you!",
      ev=[("card", "I'm great, thank you!", ORANGE, 3.0, "sentence"),
          ("act", "milo", "wave", 1.6)]),
    A(1.2),
]})

# ---------------------------------------------------------------- Scene 9
SCENES.append({"name": "quiz", "target": 34, "beats": [
    A(1.2, [("sfx", "bell"), ("cam", "wide", 0.1),
            ("card", "QUIZ TIME!", ORANGE, 1.6, "word")]),
    L("narr", "What color is this?", gap=0.1,
      ev=[("prop", "quiz", "show", "red")]),
    P(2.8),
    L("all", "Red!", card=("RED", RED),
      ev=[("sfx", "correct"), ("prop", "fx", "stars")]),
    L("narr", "What animal says meow?", gap=0.1,
      ev=[("prop", "quiz", "show", "cat")]),
    P(2.8),
    L("all", "Cat!", card=("CAT", ORANGE),
      ev=[("sfx", "correct"), ("prop", "fx", "stars"), ("prop", "cat", "happy")]),
    L("narr", "What color is this?", gap=0.1,
      ev=[("prop", "quiz", "show", "blue")]),
    P(2.6),
    L("all", "Blue!", card=("BLUE", BLUE),
      ev=[("sfx", "correct"), ("prop", "fx", "stars")]),
    L("narr", "What animal says moo?", gap=0.1,
      ev=[("prop", "quiz", "show", "cow")]),
    P(2.6),
    L("all", "Cow!", card=("COW", "#6D4C41"),
      ev=[("sfx", "correct"), ("prop", "fx", "stars")]),
    L("narr", "Count three apples!", gap=0.2,
      ev=[("prop", "quiz", "show", "apples")]),
    L("all", "One,", cap=False, gap=0.3, ev=[("prop", "qapple", "count", 1),
                                             ("card", "1", RED, 0.9, "number")]),
    L("all", "two,", cap=False, gap=0.3, ev=[("prop", "qapple", "count", 2),
                                             ("card", "2", ORANGE, 0.9, "number")]),
    L("all", "three!", cap=False, gap=0.4,
      ev=[("prop", "qapple", "count", 3), ("card", "3", GREEN, 1.2, "number"),
          ("sfx", "correct"), ("prop", "fx", "stars")]),
    L("narr", "Show me HAPPY!", gap=0.1,
      ev=[("prop", "quiz", "show", "happy")] +
         [("face", w, "happy", 3.0) for w in ALL3]),
    L("all", "Happy!", card=("HAPPY", YELLOW),
      ev=[("sfx", "correct"), ("prop", "fx", "stars")] +
         [("act", w, "jump", 0.9) for w in ALL3]),
    A(1.0),
]})

# ---------------------------------------------------------------- Scene 10
SCENES.append({"name": "goodbye", "target": 24, "beats": [
    A(1.5, [("sfx", "birds_soft"), ("cam", "wide", 0.1), ("music", "soft"),
            (0.3, "cam", "three", 1.5)]),
    L("milo", "We learned so much today!", ev=[("act", "milo", "clap", 1.2)]),
    L("luna", "Great job!", ev=[("act", "luna", "jump", 0.9)]),
    L("bobo", "See you next time!", ev=[("act", "bobo", "flap", 1.6)]),
    L("all", "Goodbye!", ev=[("act", w, "wave", 2.5) for w in ALL3]),
    L("narr", "Keep practicing English every day. Goodbye, friends!",
      ev=[("act", w, "wave", 3.5) for w in ALL3] +
         [("cam", "front", 2.5)]),
    A(6.5, [("card", "GREAT JOB!\nSEE YOU NEXT TIME!", YELLOW, 6.5,
             "title"), ("sfx", "sparkle"), ("prop", "fx", "stars")] +
        [("act", w, "wave", 6.5) for w in ALL3]),
]})
