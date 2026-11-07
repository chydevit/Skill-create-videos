# The five styles

Every style is 5 s long. The logo is complete by about 2.0–3.0 s, then a gloss sweep and a chime play, and the hold has a slow 1.8 % push-in. Timings adapt to the number of shapes and letters (`times` in `-info.json` lists the final values). The engine sorts the logo into:
- **main**: the biggest shape.
- **parts**: every separate shape (8-connected), sorted by size. Tiny specks are merged into the nearest shape.
- **text**: 3+ smaller shapes of similar height on one row, beside or below the main shape.

| Style | Page | Feel | Good for | Watch out for |
|---|---|---|---|---|
| liquid | light (auto) | organic, satisfying | rounded or blobby marks, gradients, apps | very thin line-art: beads are tiny |
| neon | always dark | night, tech, premium | bold marks, wordmarks, events | dark logos are recoloured white on dark |
| bounce | light (auto) | playful, friendly | consumer brands, kids, food, health | very wide single shapes look heavy when tumbling |
| lens | light (auto) | discovery, search | search, health, data, research | logos with one tiny shape: the zoom is short |
| rise | light (auto) | calm, corporate | anything; formal brands, lower thirds | none really; the safe choice |

## liquid
- **0.12–0.5 s:** a drop of the main shape's dominant colour falls toward the page, large, blurred and fading in. It lands with a plop and two ripple rings.
- **0.54–1.42 s:** a signed-distance morph turns the circle into the main shape with a small wobble. The colours flow from the solid drop into the logo's own, and the shape ends on its exact pixels with a jelly settle.
- **From 1.3 s:** each other shape grows from a bead at the edge point nearest the main shape and travels to its own centre. It morphs, then stretches and settles. Marks go first, nearest first, then letters left to right.
- **Sound:** fall whoosh, plop and thump, spread swell, a bloop per arrival (rising in pitch across letters), gloss, chime, warm pad.

## neon
- **0.15–1.3 s:** glowing tubes in each shape's own colour (white for dark shapes) trace each non-text shape with a radial sweep. Letters wait as faint unlit tubes.
- **1.45 s:** ignition flash, a dust boost and a glow bloom. The fills fade in and the tubes fade out.
- **From 1.85 s:** letters flicker on left to right with seeded neon stutters. With no letters, the lit mark stutters once.
- **Sound:** transformer hum, crackle while drawing, a zap and sub at ignition, a zap per flicker, gloss, chime, dark pad.

## bounce
- Big shapes (≥ 20 % of the main shape's area) alternate between two entrances. Most tumble down from above the frame with a bounce-out and squash. Every second one rolls in from the right, spinning, with a back-ease overshoot.
- When the last big shape lands, confetti in the logo's colours bursts from the main shape.
- Smaller shapes and letters then drop in one by one with a little rotation and squash.
- **Sound:** a slide-whistle fall, plastic tocks per bounce, a rattle every half-turn while rolling, a pop with sparkles for the confetti, a pitched tick per letter, gloss, chime, bright pad.

## lens
- **0.15–2.0 s:** a magnifier glides along a curve across the logo's area. It uses the darkest saturated logo colour (white-ish on dark pages). The page is empty; the logo shows only through the glass, magnified 1.45×.
- **1.65–2.05 s:** it settles on the main shape's deepest point and magnifies to 2.4×.
- **2.08–2.95 s:** the view opens out from the lens while the camera zooms out to 1×. The magnifier shrinks and fades, a ping ring plays, and the last frames are the exact logo.
- **Sound:** a travel whoosh panning with the lens, glassy tones over the logo, a focus glide, a ping (click, tone, sub), the zoom-out whoosh, gloss, chime, calm pad.

## rise
- **0.25–0.95 s:** a hairline in the logo's first two colours draws outward from the centre.
- **0.95–1.85 s:** it splits into two lines that open a band. Shapes rise into the band left to right from 14 % below, with blur and fade (no blur with more than 14 shapes).
- **Sound:** a soft glide for the line, a click and thump as it opens, a whoosh, light ticks per shape, gloss, chime, warm pad.
