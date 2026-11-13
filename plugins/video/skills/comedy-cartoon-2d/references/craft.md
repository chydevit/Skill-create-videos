# Craft: style, comedy timing, staging, QC lessons

## Style bible (keep consistent across a film)
- **Line**: ink `#1d1520`, 7 px at 1080p on characters/props, 4–6 px on details, 0–5 px on far backgrounds (far layers
  have no outline and are lighter: atmospheric depth).
- **Colour**: flat fills + one cel-shade tone (light from upper left). Warm city palette (orange, teal, yellow,
  brick, plum); reserve one saturated hue for the hero object (the green car) so it pops; red/blue for siren washes.
  No gradients except sky/sea.
- **Motion**: characters on twos (`onTwos(lt)` for cycles/poses), camera and fast moves on ones. Anticipation before
  every big action (compress `sq` +, lean back), then a smear (3–4 ghost copies at 0.16 alpha + speed streaks +
  stretch `sq` −) and an overshoot/settle (`wobble`). Squash on impact. Holds before and after gags.
- **Faces sell the joke**: change expression on the beat, sweat drops for panic, stress marks for anger, half-lidded
  eyes for boredom/deadpan.

## Comedy timing patterns that worked
- **Setup, hold, payoff.** Hold 0.3–0.6 s before the punchline frame; after it, hold the reaction 1–2 s.
- **Deadpan to camera** (character turns pupils to the viewer, blinks once, says nothing, crickets): 2–3 s.
- **Rule of three** with escalation (the bag pops out twice, the third time it flies onto the roof).
- **Contrast**: a frantic chase vs a polite, slow obstacle (ducks, turn signals); a slow bored pursuer who somehow
  keeps up (cut away, cut back: he is right there).
- **Silence/needle-scratch before a reveal**, then a slow camera pan to the reveal (the police station sign), faces fall.
- **Button**: one small sound on the last beat (a single bell ding, a meep), then iris out on a face.

## Staging and camera
- Open wide (establish geography + title card), then go closer. Low angles (`perspStreet`, low `vpy`) for speed and
  power; close-ups for reactions; top-down for route/turning gags; inserts (foot on pedal, fuel gauge) for punctuation.
- Chase sections: rapid cuts of 0.8–2.5 s. Gags and reactions: 1.5–4 s. Keep screen direction consistent
  (the chase goes left to right).
- Keep important action inside the centre ~80 % of frame; check that text/lettering doesn't get cropped by zoom
  (put lettering in screen space or check stills).
- `cam()` zoom 1.0 = full set; 1.5–2.5 medium; 3–4.5 close-up on a window/face.

## Shot list first
Before coding, write a beat sheet → shot table (`docs/shotlist.md`): id, start–end, framing, action, gag, cues.
Hit the brief's beat timings (e.g. opening 0–10 s, chase 20–50 s) and total length. Then implement shot by shot,
checking stills as you go.

## Retiming
Shots use absolute times. When a beat must grow (usually because dialogue came out longer), change that shot's end,
call `setShift(+x)` right after it so every later shot moves, and win the time back by shortening a long shot or the
end card (adjust any `lt/duration` ratios inside it). Music and SFX follow automatically because cues are shot-relative.
Never leave gaps: render prints a total; `SHOTS` must tile 0..DURATION.

## QC checklist (problems actually hit while building the example)
- **Clipping occupants**: the car's `crew` clip must include both windows in one path (`frontWin(ctx, false)`, i.e. no
  new beginPath); otherwise characters vanish.
- **Readability**: dark legs against dark interiors read as tufts; add a stripe/sock/shoe highlight.
- **Effects that draw at life 0**: pass `seg(...)` lives and make effects skip `life <= 0` (fx.dust does).
- **Overlaps**: a character hidden behind a set piece; a crushed prop covered by the hero: move one so both read.
- **Text collisions**: two sfx words at once; lettering overlapping signs; Khmer stacks are taller (allow headroom).
- **Mirrored text** on flipped props: draw text un-flipped.
- **Background holes**: when the camera zooms out, fill every region (sky to horizon, city behind the hero building).
- **Muxing**: never use `-shortest` with subtitle tracks (it cuts at the last subtitle); build.mjs uses `-t DURATION`.
- **Font paths** with spaces: use `fileURLToPath`, not `URL.pathname`.
- Look at `film/qc/contact_sheet.png` (every 4 s) and 3–6 full-res stills of key gags before calling it done.
