# Writing a bespoke style

The five built-in styles work on any logo because they only know "shapes" and "letters". A logo with meaning in its parts can do much better with a style written for it: for example, a pharmacy cross built from two capsules with a magnifier, or a letter K whose orange drop is "squeezed out". Write a new file `scripts/styles/<name>.mjs` and run it with `animate.sh <logo> --styles <name>`.

## The style API
```js
import * as E from '../engine.mjs';
export async function setup(ctx) {        // ctx: the frame's 2D context (E.W × E.H)
  const L = E.L;                          // the analysed logo, below
  const T = { /* your timeline, seconds */ hold: 3.4 };
  function render(t, transparent) { /* draw frame t; when transparent, draw no background or shadow */ }
  const events = [ /* sound events, below */ ];
  return { render, events, times: { ...T, fadeFrom: 4.5 } };
}
```
`render` must be deterministic in `t` (frames render out of order for previews), so draw everything from `t`. Use seeded randomness (`E.mulberry32`), never `Math.random()`.

## What the engine gives you (`E.*`)
- **`E.L` (the logo):** `canvas` is the cut-out RGBA logo in "logo px". `w`/`h`, `palette` (dominant colours, most common first) and `S` (logo px → frame px). `toFrame(x,y)`, `box` (frame rect), `main` (biggest part), `parts`, `reading` (marks first, then letters in reading order) and `res` (logo px per design unit, for scale-free sizes).
- **A part:** bbox `x0..y1`, `area`, `cx/cy` (centroid), `text` (bool) and `lum`. `sprite` is its own pixels in a canvas whose (0,0) is at logo px (`rx`,`ry`). `A`/`F` hold alpha and straight colour.
- **`E.field(p)`:** adds `p.sdf` (signed distance, negative inside), `p.C` (colours filled outward), and `p.deep` (the point furthest inside, plus its distance).
- **`E.morphPart(p, cx, cy, r, m, wob, t, exact, tint, tk)`:** a circle morphing into the part, returned as a canvas placed at (`p.rx`, `p.ry`) in logo space.
- **Drawing:** `E.logoSpace(g)` (maps logo px to the frame), `E.applyPush(g, E.pushIn(t, T.hold))`, `E.paintBg(ctx, t, theme)`, `E.gloss(g, t, [a,b])`, `E.shadowPass(ctx, layer, alpha)` and `E.ripple(...)`.
- **Maths:** `E.bezier(...)`, `easeInOut`, `easeOut`, `back`, `spring(t,t0,amp,freq,decay)`, `bounceOut` with `BOUNCE_HITS`, `prog(t,[a,b])`, `smooth`, `lerp`, `mix`, `rgb`, `rgba`, `lum`, and `panOf(frameX)`.
- **Config:** `E.CFG` holds `theme`, `text`, `width`/`height`, and any key you add to the config.

## Sound events
Each event is `{type, ...}`. Times are in seconds and `pan` runs from −1 to 1 (`E.panOf(x)`):
- **whoosh:** `t0, tp, t1, gain, fa, fb, fc, p0, p1, q, body`. Air noise whose centre frequency goes fa→fb→fc.
- **plop:** `t, gain, f0, f1, rise, tau, pan`. A water drop or pop; the pitch springs from f0 to f1.
- **sub:** `t, gain, f0, f1, tau`. A low thump.
- **click:** `t, gain, fc, bodyHz, decay, bodyGain`. A tick.
- **tock:** `t, gain, bodyHz`. A plastic hit.
- **glide:** `t0, t1, f0, f1, gain`. A sliding sine.
- **tone:** `t, f, gain, tau`. A bell.
- **zap:** `t, gain, dur, fc`. An electric zap.
- **hum:** `t0, t1, level, boostAt`. Neon hum.
- **crackle:** `t0, t1`. Sparse ticks.
- **shimmer:** `t`. A four-note arpeggio.
- **sparkle:** `t, n`. Bright ticks.
- **ping:** `t`. Click, tone and sub.
- **chime:** `t`. Two bell tones and a sub.
- **pad:** `t0, mood` (warm, bright, dark or calm). A background chord.

## Techniques that work
1. **Rebuild a structured mark as vector shapes for the motion.** Use `roundRect` capsules, arcs and polygons in the logo's own unit space, so pieces can move, spin and overlap with real geometry. For example, two capsules where the overlap is drawn by clipping one with the other. Then **check the rebuild against the PNG**. Draw both at 1:1 into canvases and compare pixels (mean channel difference under about 0.5, with differences only along edges). Measure details you can't read from a source file: fit circles to the edge points of a ring, and sample cross-sections of a line for its width and angle.
2. **Hand over to the real pixels when the motion ends.** Crossfade the vector drawing into the PNG over about 0.2 s while nothing moves. The final frames are then exactly the brand file, and the handover is invisible.
3. **Don't blend coverage between two different shapes.** Mixing the alpha of a morph that hasn't arrived yet with the real alpha leaves a translucent rim. Let the morph reach the target first (m = 1), then blend.
4. **Never let letters appear where a moving shape still is.** Start a wordmark once the mark has cleared the space, or hide letters under the mark and slide them out from behind it, clipped at the mark's centre.
5. **Keep the frame balanced while a mark builds on one side.** Show unlit or ghost letters, roll a piece in across the empty area, or build at the centre and slide into the lockup.
6. **Make a transition carry the brand idea.** A magnifier that locks onto the logo's own ring, then zooms out with it, reads better than a lens that shrinks to a dot.
7. **Use a solid-colour stand-in for multi-colour logos.** A drop or circle that samples a multi-colour logo looks like a random cut-out. Draw it in the dominant colour and blend to the real colours as it forms.
8. **Make neon readable.** Turn shapes that are too dark for the dark page white (like the brand's white-text variant), and keep coloured ones.

## Checking your work
Render stills without encoding video:
```bash
node scripts/render.mjs --config cfg.json --logo logo.png --out stills --times 0.5,1,1.5,2,3,4.98 --info info.json
ffmpeg -pattern_type glob -i 'stills/t_*.png' -vf "scale=480:-1,tile=6x1:padding=6:color=white" -frames:v 1 sheet.png
```
`cfg.json` looks like `{"style":"<name>","theme":"auto","width":1920,"height":1080,"logoFile":"logo.png"}`. Read the sheet, fix what's off, and repeat. Then run `animate.sh` for the real thing. Also look at one transparent frame (`--transparent`) composited over grey, to make sure nothing depends on the background.
