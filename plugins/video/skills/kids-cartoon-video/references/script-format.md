# Script format and set catalogue

## Contents
1. File skeleton
2. Beats: L, K, P, A and the helpers
3. Events
4. Characters and actions
5. Set catalogue (starting positions, shots, props)
6. Adding a new set

## 1. File skeleton (`<project>/script_data.py`)

```python
from cartoon_dsl import *          # colors RED..WHITE, ALL3, NUMS_EN, NUMS_KM, helpers

language("english")                # "english" | "bilingual" | "khmer"  (call first)
TITLE = "Milo & Luna's Happy Adventure"
UI = {"your_turn": "YOUR TURN!"}   # optional override of the badge text

SCENES = [
  {"name": "good_morning", "set": "house", "target": 60, "beats": [ ... ]},
  ...
]
```

- `name` is used for file and folder names, so keep it snake_case and unique.
- `set` picks the 3D location (see Section 5).
- `target` is only a guide: `build_audio.sh` prints the actual length next to it.

## 2. Beats

Beats play in order. Each beat's length comes from its audio, or from the seconds you give it.

| Helper | Meaning |
|---|---|
| `L(who, text, ev=[], cap=True, gap=0.8, rate=None, card=None, lang=None)` | A spoken line. `who`: `milo luna bobo narr cat dog duck cow`, or a group (`"all"` = the three friends, `"ml"` = Milo + Luna). `gap` is the silence after the line. `card=("WORD", color)` shows a word card as the line starts. `cap=False` hides the caption. `lang` defaults to the episode mode (`"km"` in khmer mode, otherwise `"en"`). |
| `K(who, text, ...)` | The same as `L`, but spoken in Khmer. Use it in bilingual mode for the Khmer narrator. |
| `P(sec)` | A pause for the child to answer. Shows the "your turn" badge. |
| `A(sec, ev)` | A silent beat for actions: walking, flying, dancing. |
| `laugh(who="all")` | "Ha ha ha!", or "ហាហាហា!" in Khmer mode, with laughing animation. |
| `say_it(word, prompt=None)` | The narrator says "Say: X!" (or "និយាយតាម: X!") and then pauses. |
| `count_line(n, who, word, prop="apple")` | Speaks one number, shows the number card, and bounces prop `n`. Use it with `NUMS_EN` or `NUMS_KM`. |

**`rate`** controls speed:
- English: words per minute (the default is about 128, and 118 for the narrator).
- Khmer: a percentage string such as `"-10%"`.

Use a fast `rate` only on purpose, e.g. Bobo counting too fast.

## 3. Events (`ev=[...]`)

A tuple with an optional leading number is an offset in seconds from the start of the beat, e.g. `(1.5, "sfx", "boing")`.

| Event | Notes |
|---|---|
| `("act", who, action, dur)` | See Section 4. |
| `("face", who, mood, dur)` | Moods: `happy sad excited tired surprised`. |
| `("walk", who, (x, y), dur)` | Walks the kid to a ground point. Walks are processed first, so later actions know where the kid stands. |
| `("card", text, color, dur, style)` | Styles: `word` (big, top), `sentence` (top, wraps), `number` (big disc), `title` (centre, translucent, with stars). A new top card replaces the previous one. `\n` makes two lines; bilingual cards are `"RED\nក្រហម"`. |
| `("cam", shot, move_dur)` | Moves the camera to a shot in the current set. Each scene should start with `("cam","wide",0.1)`. |
| `("prop", name, action, *args)` | Set-specific props, plus these, which work in every set: `("prop","fx","stars")` for a star burst, and Bobo's flight: `("prop","bobo","fly_in")`, `("prop","bobo","fly_to",spot)`, `("prop","bobo","loop")`. |
| `("sfx", name)` | `pop boing birds birds_soft tweet flutter door sparkle correct bell claps whoosh yawn`. Footsteps are added automatically for walks. |
| `("music", mode)` | `normal`, `dance` (a stronger beat) or `soft` (the ending). |

Colors: `RED BLUE YELLOW GREEN ORANGE PURPLE PINK TEAL BROWN WHITE`, or any `"#RRGGBB"`.

## 4. Characters and actions

**Kids (`milo`, `luna`):**
- `wave`, `jump`, `jump3`, `clap`
- `point` (the outer arm), `point_up`, `point_self`
- `nod`, `laugh`, `hug` (leans toward the other kid)
- `run` / `walk_in_place` (on the spot), `dance`

**Bobo:** the same names are mapped to bird motions (`clap`/`wave`/`point` = excited flapping). He also has `flap`, `yawn` and `dizzy` (spins).

Listeners automatically turn their heads toward whoever is speaking. Everyone blinks and breathes.

**Animals** (`cat dog duck cow rabbit`):
- They exist only in the `farm` set, and the cat and cow on the `quiz_stage` board.
- They speak with `L("cat", "Meow!")`, or `L("cat", "មៀវ!")` in Khmer.
- Props: `("prop","cat","happy")`; the rabbit also has `("prop","rabbit","hop")`.

## 5. Set catalogue

Coordinates are in metres. x runs to the right of the camera, y goes into the scene, and kids stand about 1.6 m tall. "Start" is where the kids stand when the scene begins. If a start is off-screen, **walk them in** with a first `A(...)` beat that moves them to the suggested positions.

### `house`
A yellow house with a door, a fence, trees and flowers.
- **Start:** Milo `(-2.3, 2.6)` is *inside the house*; Luna `(5.0, 0.6)` is off-screen right.
- **Walk in:** open the door (`("prop","door","open")` + `("sfx","door")`). Walk Milo to `(-2.3, 1.3)` over 1.2 s, then on to `(-0.9, 0.2)` over 1.5 s. Walk Luna to `(0.9, 0.2)` over 2.8 s.
- **Bobo:** hidden until `("prop","bobo","fly_in")`. Without that event he never appears.
- **Shots:** `wide two three front`.

### `house_talk`
The same house, with the kids already standing and facing each other.
- **Start:** Milo `(-0.8, 0.2)`, Luna `(0.8, 0.2)`.
- **Bobo:** hidden until `fly_in`.
- **Shots:** `wide two three front`.

### `garden`
A flower garden with a giant red flower, a butterfly, a smiling sun and a tree.
- **Start:** Milo `(-4.8, 0.3)`, Luna `(-4.0, 0.6)`, both off-screen left. Walk them to `(-1.0, 0.0)` and `(0.0, 0.0)` over about 2.8 s.
- **Props:** `red_flower|pink_flower|purple_flower bounce`, `butterfly fly_in`.
- **Bobo spot:** `flower` (he perches inside the red flower).
- **Shots:** `wide garden flower sky tree front`.

### `apple_tree`
A big apple tree with 10 apples in a row.
- **Start:** Milo `(-4.8, 1.0)`, Luna `(4.8, 1.0)`. Walk them to `(-1.3, 0.8)` and `(1.3, 0.8)`.
- **Props:** `("prop","apple","count",n)` bounces apple *n* and shows a 3D number above it; `("prop","apple","reset")` hides the numbers.
- **Shots:** `wide apples apples_close front`.

### `farm`
A red barn, a fence, and a cat, dog, duck, cow and rabbit in an arc on the right.
- **Start:** Milo `(-5.8, 0.4)`, Luna `(-5.0, 0.2)`. Walk them to `(-2.4, 0.2)` and `(-1.5, 0.0)`.
- **Shots:** `wide cat dog duck cow rabbit`. Each animal shot frames that animal low in the picture, so word cards don't cover it.

### `picnic`
A checked blanket with an apple, banana, bread, milk and water, plus a basket.
- **Start:** Milo `(-1.5, 1.0)`, Luna `(1.5, 1.0)`.
- **Props:** `apple|banana|bread|milk|water bounce`.
- **Shots:** `wide food picnic front`.

### `playground`
Swings, a slide and a sandbox, good for action words.
- **Start:** Milo `(-1.1, 0)`, Luna `(0.15, 0)`; Bobo hovers on the right.
- **Shots:** `wide play dance front`.

### `meadow`
Flowers and trees, good for feelings and general talk.
- **Start:** Milo `(-1.1, 0)`, Luna `(0.15, 0)`.
- **Props:** `("prop","emoji","show",kind)`, where kind is `happy sad excited tired surprised` or `none`. It shows a big emoji face on the right side of the screen.
- **Shots:** `wide c_milo c_luna c_bobo two bobo three front` (the `c_*` shots are close-ups).

### `quiz_stage`
A purple game-show stage with a quiz board.
- **Start:** the kids stand stage-left.
- **Props:**
  - `("prop","quiz","show",item)`, where item is `red blue cat cow apples happy`
  - `("prop","qapple","count",1..3)`
  - `("prop","cat"/"cow","happy")`
- **Shots:** `wide front`.

### `sunset`
The meadow and house at sunset.
- **Start:** Milo `(-0.9, 0.2)`, Luna `(0.9, 0.2)`.
- **Shots:** `wide three front`. Use it with `("music","soft")` for goodbyes.

## 6. Adding a new set

Only do this when no existing set fits, e.g. a beach, a classroom or a kitchen. In `scripts/bl_scenes.py`, subclass `Scene`:
1. Set `kids = {"milo": ((x, y), facing_rz), "luna": (...)}`, `bobo_home = (x, y, z)`, and `shots = {"wide": (cam_loc, look_at), ...}`.
2. In `build()`, call `self.daylight()` (sky, sun, ground, hills, clouds), then add props with the helpers in `bl_env.py`: `tree`, `bush`, `flower`, `flower_field`, `fence`, `house`, `cloud`, and the `sphere`/`cyl`/`box` primitives from `bl_util`.
3. If the set has animated props, implement `prop(self, name, action, t, args)`. Write the animation arrays with `pulse(self.A, obj, t, ...)` or `self.A.set(obj, path, index, values)`.
4. Register it in `SCENE_CLASSES`, then check it with `stills.sh` before using it in a script.
