---
name: flat-explainer-doc
description: Flat-animation history and science explainer video builder, like the "We Finally Know More About Humanity's First Civilization" style. It makes narrated 2D MP4s with flat vector scenes (no outlines, a hard light from one side, violet nights lit by one warm fire, isometric dioramas, cutaways), a recurring original guide character (Dara) seen from behind, pop-in banner tags, Human Era / CE timelines, glowing chapter titles, framed maps made from real Natural Earth data with pins, circular "portal" flashback bubbles, multi-panel comparisons, ambient synth music with pops and whooshes, Khmer narration in locked VoxCPM2 voices (Khmer Whisper QC) and English subtitles. Use it whenever the user wants an explainer, an "educational video like Kurzgesagt", an animated history or science video, a video "like this template", a first-civilizations, Human Era, prehistory or archaeology explainer, or a flat-style version of a khmer-history-doc film, even if they don't name the skill. For paper-cut / shadow-puppet documentaries use khmer-history-doc; for chibi cartoon stories use khmer-2d-animation.
---

# Flat Explainer Doc

This skill turns a topic into a 5–20 minute narrated explainer in a flat vector style. Scenes and characters are
hand-written SVG files, so they are crisp, editable and consistent. The picture is assembled by the
**khmer-history-doc engine** (shot timeline, camera, Khmer voices, ASR QC, mix, subtitles, render, mux), which
this skill copies into each project and extends with:

- `engine/svgscene.py`: SVG sets (2400×1350) → parallax layers, animated sprites (`data-anim`) and reusable
  characters (`data-include`, poses, recolours)
- `engine/explainer.py`: the graphic grammar: tags, timelines, chapter titles, map cards, portals, panels, big text
- `engine/depth.py`: 2.5D camera: `cam(..., dolly=(c0, c1), dof=(focus, px) | (f0, f1, px))` pushes the
  camera through the depth planes (near layers rush past and fade) with depth of field and rack focus. Per-object
  `data-depth` and root `data-haze` give crowds and atmospheric perspective.
- `engine/synthscore.py`: ambient synth moods (wonder, ancient, tension, warm, discovery, outro)
- film.py patches: flat post-processing and `iris` / `wipe` transitions. audio.py patches: timed SFX.
  core/make patches: `project.json` `"fps"` (default 60, like the reference) and `"burn_subs"` (default false: the
  reference has no burned subtitles; EN and KM subtitles stay as selectable tracks).

**Originality:** this reproduces techniques studied from the reference video. Never copy its characters, mascots,
logo, end screen or narration text. **Accuracy:** every claim comes from `docs/fact_sheet.md`, with certainty
words in the narration.

## Requirements
- The `khmer-history-doc` skill installed and set up (its engine, plus `.venv-vox` with VoxCPM2 and Khmer Whisper).
- This skill's `.venv` (cairocffi, cairosvg, numpy, scipy, soundfile, pyloudnorm, pyshp, pillow) is already set
  up. To recreate it: `python3.12 -m venv .venv && .venv/bin/pip install cairocffi cairosvg numpy scipy soundfile pyloudnorm pyshp pillow`
- ffmpeg, pango (`pango-view`), the fonts Avenir Next, DIN Condensed, Noto Sans Khmer and Koulen.

## Read first
- `references/style.md`: the visual grammar, measured pacing, colour coding, motion rules and writing rules
- `references/svg-authoring.md`: how to draw sets, characters and maps, and the animation attributes
- khmer-history-doc `references/workflow.md` + `gotchas.md`: voices, ASR and rendering (same engine)

## Production kit for long films (`engine/kit.py`)
A 10–15 minute film needs 30–50 sets and characters in dozens of poses. Write them as Python with `kit`, not as
hand-drawn SVG:
- `Scene(name, light=, rim=, dark=, haze=)` with `.layer(id, *children, depth=)` and `.save()`
- backgrounds: `sky, stars, mesas, hills, ground, pebbles, bush, palm, grass_tuft, halo`
- props: `t_pillar(relief=fox|snake|boar|vulture|arms), round_house, box_house, skull(deco=), bones`
- `person(x, y, h, style, view=, arms=dict(l=(shoulder°, elbow°), r=...), legs=stand|walk|sit|kneel|("walk", phase),
  hold=dict(r=torch|bowl|chisel|spear|bundle|tablet|skull|straw, head=basket), face=calm|happy|open|focus|worry|sad,
  anim="walk|data-dx=200")`. These are parametric reference-style characters (rubber-hose limbs) that get the
  scene's rim light automatically. Styles: guide, woman, man, elder, child, shaman, worker, plus colour overrides.
- See `~/Animation-new/first_civilization/scenes_src/part1.py` / `part2.py` (44 sets) and `maps.py` (8 maps, with
  approximate ice and lake reconstructions added from lon/lat outlines).
- `scenes_src/preview.py name ...` writes contact sheets of sets without building the timeline.
Graphics added for long films: `E.clip("clips/<3d shot>", fps=30, offset=)` plays Blender frames as a timeline
shot, so 2D and 3D share voices, music and subtitles. `E.graph(...)` gives animated line charts, `E.swirls()` the
memory backdrop, and `MAP(..., banner=, routes=)` migration arrows.

## Workflow
1. **Research and fact sheet** (`docs/fact_sheet.md`), with tags and a DO-NOT-SAY list. Run the research in
   parallel with a subagent when the topic is big.
2. **Create the project:**
   `~/.claude/skills/flat-explainer-doc/.venv/bin/python ~/.claude/skills/flat-explainer-doc/scripts/new_explainer.py ~/Animation-new/<slug> --title-en "…" --title-km "…"`
   It contains the sample film (the Human Era, about 70 s) as a working reference.
3. **Script** (`narration.py`): a hook in the first 20 s, one idea per line, chapters that end on a turn.
   Use `L()` for the narrator and `T()` for Dara.
4. **Art:** draw the sets in `scenes/` (reuse each set across several shots with different camera moves and
   `swap` variants), add poses to `chars/`, and make the maps with `scripts/make_map_svg.py`.
5. **Shots** (`script_src.py`): `SV` for scene shots, `CH` for chapters, `MAP`, `E.timeline`, `E.portal`,
   `E.panels`, `E.big_text`. Change the picture every 3–6 s. Every element that pops in gets a `("pop", t)`.
6. **Check:** `make.py info` → `make.py shotstills` → look at `build/shots/sheet_*.jpg` and fix. Use
   `make.py stills 12.5 30` for exact moments, for example mid-animation.
7. **Voices:** `make.py voices` → listen → `make.py lock nar <seed>` / `lock dara <seed>` → `make.py narrate`
   → `make.py asr` (reseed bad lines).
8. **Render:** `make.py all` → `film/<name>.mp4`, then `make.py web` and `make.py docs`.
9. **Report:** give the runtime, the paths, the ASR mean, a contact sheet image, and the note that Khmer text
   needs a native-speaker review.

## Gotchas
- Render speed: about 3 minutes of compute per minute of film at 60 fps on 8 cores (half that at `"fps": 30`). SVG layers are
  rasterised once and cached in `build/cache/svg`, so the first render of a new set is slower.
- If a frame raises (for example, a bad overlay), the render now stops with `frame N (t=…s) failed`. Reproduce it
  with `make.py stills <t>`.
- Depth of field is the slow part: a rack focus (`dof=(f0, f1, px)`) is about 4× slower than a plain move,
  because each blur level is computed per layer. Use it on hero shots; a fixed `dof=(focus, px)` is cheap after
  the first frames.
- Animated sprites draw above their layer's static art. To have something pass *behind* an object, put that
  object in a nearer layer (`front`).
- `E.portal` and `E.panels` render whole scenes per frame inside the clip, so they are about 2× slower. Keep
  portal shots short.
- `data-swap` replaces hex strings in order, so avoid chains where one replacement creates a later key.
- English narration also works with VoxCPM2, but `make.py asr` is Khmer-only. Check English lines by ear.

## Full 3D mode (Blender): `blender3d/`
Use this when a shot needs real 3D camera moves: orbiting a site, turning a diorama, or craning over a crowd.
It keeps the same flat look:
- `toon3d.py` has the banded toon shader. Received light is quantized into flat bands (deep / shade / lit / hot),
  there is a warm rim only on lit silhouettes, view transform is Standard, and colours are exact hex. Point lights
  paint the reference's concentric light rings and crisp cast shadows. It also has `Char`, which builds the
  characters from primitives: tube limbs with posable `pose_arm()` (down, up, point, forward, lap, head, cheer),
  sphere heads, hair masses, dot eyes and bar brows, with styles guide, woman and man.
- `render3d.py` builds scenes procedurally (`fire_night`: a T-pillar enclosure, fire circle and torch moment;
  `village_day`: round mud-brick village, hills and bushes) with keyframed cameras (crane, orbit) and depth of field.
  ```bash
  cd ~/.claude/skills/flat-explainer-doc/blender3d
  blender -b --factory-startup --python render3d.py -- --scene fire_night --dur 4.8 --out P/frames/fire_night [--still 1 2 3] [--preview]
  ```
  This takes about 0.6 s per 1080p frame on an M1 Pro, so a 10 s clip at 60 fps takes about 7 minutes. Use
  `--still` and `--preview` while iterating.
- `compose3d.py` assembles the shots with bloom, vignette and grain, blob transitions, 2D overlays (tags, portal
  bubbles fed by another shot's frames) and the narration, music and subtitle tracks of a 2D project:
  ```bash
  .venv/bin/python blender3d/compose3d.py --project <2d project> --frames P/frames --out P/film.mp4 \
      --shot fire_night 0 4.8 --shot village_day 4.0 5.9 --tag 1 "First Villages" 960 300 0.9 --portal 1 0 330 250 160 0.4
  ```
3D gotchas:
- Emissive meshes must not cast shadows (`toon3d.no_shadow`, automatic for `glow()`), or flames block their own
  light.
- Build colour ramps with `set_ramp()`; assigning positions to existing elements re-sorts them.
- Rim-less toon materials disable the facing test; otherwise grazing surfaces (far ground) turn black.
- Bevel widths are applied after scale (`transform_apply`), so `bevel=` is in world units.
- Props held in hands go on `char.grips[side]` (unscaled), not on the hand spheres.
- Memory: VoxCPM2 (about 5 GB) slows to a crawl under swap pressure. Close browsers before `make.py narrate`. If
  a line takes more than 2 minutes, kill the worker and rerun `narrate` (finished lines are kept). Render 3D at
  `nice -n 10` while narration runs.
- Keep the camera path clear of tall props, and leave a corridor in rings of pillars.
