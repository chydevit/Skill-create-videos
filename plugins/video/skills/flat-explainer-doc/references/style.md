# Visual grammar of the flat explainer (studied from "We Finally Know More About Humanity's First Civilization")

We reproduce **techniques only**. The guide, characters, scenes and music are original. Never copy the studio's
characters (the duck or bird mascot, their explorer), logo, branded end screen, or text.

## Measured numbers (reference video, 17:30, 1080p60)
- About 107 hard cuts. The median shot is about 6 s, but many "shots" are long continuous moves (pans across a
  diorama, push-ins), so the picture changes every 3–5 s.
- One narrator, voice-over almost the whole time. The guide character is mostly seen from behind, reacting and
  pointing, and rarely speaks.
- Music is ambient synth (pads, arpeggios), always under the voice. Pops and whooshes accompany every element
  that appears.

## Look
- **Flat vector, no outlines.** Shapes are separated by value and hue, not by lines. Each material has 2 tones
  (lit and shade). The light comes from one side and the shade is a clean hard-edged plate.
- **Characters**: bean bodies, round heads, big hair shapes, dot eyes, tiny mouths, minimal hands. Skin tones are
  warm browns. Crowds come from re-coloured copies of a few base figures (`data-swap`).
- **Lighting by colour**: night scenes are violet/indigo with ONE warm source (fire, torch). The ground under the
  source becomes concentric warm ellipses, and figures near it get a warm rim plate. Day scenes use a mint→cream
  sky, a pale sun disc with a halo, and ochre and green land.
- **Depth**: far layers are low-contrast and desaturated, and the foreground framing is the darkest element.
  Parallax comes from the camera moving across layers (svgscene depths).
- **Recurring set types** (draw these as SVGs):
  1. *Isometric diorama*: a town or site seen at 30°. Use it for "how it was laid out" and pan across it.
  2. *Cutaway*: a building sliced open on a dark background, with people inside doing things.
  3. *Fire circle / crowd from above*: lit centre and dark periphery.
  4. *Landscape panorama*: wide, layered hills, tiny figures, a big sun.
  5. *Close-up object*: one prop (skull, tablet, figurine, seed) big on a flat background.
  6. *Guide from behind*: the guide in the foreground looking into a scene, a doorway or a glowing portal.
  7. *Symbol / glow*: a single glowing pictogram on a dark field (writing, ideas).

## Graphic grammar (explainer.py)
| element | when | call |
|---|---|---|
| banner tag (hexagon pill) | naming a place or thing in the scene | `E.tag("Göbekli Tepe", x, y, C["magenta"], at=1.0, space="set", depth=0.5)` |
| box tag with pointer | years and data points | `E.tag("Year 0", x, y, C["teal"], style="box")` |
| title banner | top-centre title of a diagram | `E.title_tag("Timeline")` |
| timeline | any "when" question; repeat it as the film progresses | `E.timeline(...)` |
| chapter title | each chapter: small italic line plus a big condensed glowing title plus an era bar | `CH(small, big, bar, labels)` |
| framed map | the first time each place is mentioned | `MAP(lines, svg, title, pins)` |
| portal / memory bubble | flashback, comparison, "imagine…" | `E.portal(inner_scene_fn, cx, cy, r)` |
| panels | 2–4 parallel examples ("in many places…") | `E.panels([fn, fn, fn])` |
| big text / number | one striking number or a quote | `E.big_text([...])` / `E.caption(...)` |

Colour coding for tags: magenta = places, teal = years and dates, green = present day, orange = empires and
power, violet = ideas and religion.

## 2.5D depth (dolly + focus)
The reference stays flat in its drawing, but its camera moves through stacked planes. Do the same:
- Spread every set over 5–8 depth planes (`bg 0, far 0.25, far2 0.4, mid ~0.5, crowd 0.6–0.78 per person,
  front 0.92, lens 0.985`). A "lens" plane of dark grass or rocks sliding past the camera sells the depth.
- `dolly=(0, 0.6)` push-ins for openings and discoveries; `dolly=(0.55, 0)` pull-backs for reveals.
- `dof=(0.95, 0.7, 20)` racks focus from the guide in the foreground to the subject; `dof=(0.66, 14)` keeps
  focus on a crowd.
- `data-haze` (day: a pale blue-grey; night: a deep violet) lightens and tints the far planes.

## Motion rules
- Everything that appears **pops** (back-out overshoot, 0.45 s) and gets a `pop` SFX.
- The camera never sits still. Default push 1.0→1.06. Use slow pans across dioramas, and a push-in on the guide
  when they speak.
- Idle life: fire `flicker`, plants `sway`, birds `drift`, people `bob` (amp 3–5) or `walk`.
- Transitions: `blob` (liquid ink iris with a wobbling edge; the reference's signature), `iris` into a new topic, `wipe` between diagrams, `cut` within a scene, `fade` for time passing.

## Writing
- Hook in the first 20 s: a question or a paradox. Short sentences, second person ("imagine you…").
- Narrate claims with honest certainty words: "we think", "probably", "the evidence suggests", following the
  fact sheet tags.
- End each chapter with a turn that pulls into the next one.
