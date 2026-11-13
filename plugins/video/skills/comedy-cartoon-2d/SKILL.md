---
name: comedy-cartoon-2d
description: >-
  2D cartoon builder for comedy shorts and character stories: turns a cartoon brief, build prompt, story script,
  beat sheet or gag idea into a finished 1–4 minute MP4 (plus a cover thumbnail) in a bold modern TV-cartoon
  style or a softer pastel style. It uses thick black outlines, flat bright colours with one-tone shading, squash-and-stretch, smears, holds before gags and characters animated on twos, all drawn in code
  (Node + canvas, 1920×1080, 24 fps). It ships with a synthesized frantic jazz chase score (walking bass, swing
  drums, brass stabs, stings, tape-stops) and 80+ cartoon sound effects (boings, honks, skids, slide whistles,
  sirens, bike bells, quacks, sad trombone). Dialogue can be in Khmer (default when the user writes Khmer or asks
  for it) or English, spoken by locked VoxCPM2 voices, with Khmer lettering in Koulen and soft Khmer/English
  subtitles. Story films get a natural-proportion person rig, lip-sync from the voice clips, a narrator voice,
  a timeline that follows the real dialogue, and gentle music (warm, upbeat, build, triumph, tender, love, game).
  It carries the Office series cast (Smey, Nimith, David, Sopheak, Leanghak, Pisey, Kimlong, Channy, Sreyneang)
  with their locked voices and sets. Use it
  whenever the user wants a funny animated short, slapstick, chase or heist cartoon, a gag cartoon "like a TV
  cartoon short", a story video with characters who talk (workplace, team, lesson, introduction or heartfelt
  story) with scenes and dialogue lines, a 2D animation build prompt with characters, beats and timings, a video
  "like Getaway Car", a new episode with Benny, Marge, the bike cop, Bong Smei, Bong Nimith, Devit/David, Sopheak,
  Leanghak, Pisey or Kimlong (វគ្គថ្មី), or a cartoon
  re-voiced in Khmer, even if they don't name the skill. Prefer khmer-2d-animation for chibi Khmer folk tales,
  kids-cartoon-video for 3D kids learning videos and flat-explainer-doc for narrated explainers.
---

# Comedy & Story Cartoon 2D

Build an original cartoon from a brief, entirely in code: characters, sets, animation, camera, music, sound
effects, dialogue, lip-sync, subtitles. Three worked examples show the kinds of film. Read the closest one's
`src/shots.mjs` before writing a new film, and watch its sample MP4 (or contact sheet) if you need the target look:
- **Getaway Car** (`examples/getaway-car/`): a 90 s slapstick heist chase. Gags, smears, chase music,
  hard-coded shot times.
- **Bong Smei, Bong Nimith & Devit** (`examples/team-story/`): a 2.5 min, 8-scene Khmer story about a Phnom Penh
  tech team. Three talking characters plus a narrator, lip-sync, a timeline built from the voices, inserts and
  a split screen. For dialogue-driven films also read `references/story.md`.
- **Kimlong, the King of Flirting** (`examples/kimlong/`): Office series Episode 7, a 3:44, 15-scene Khmer story
  with nine series characters and 79 lines. Scenes are split into files (`src/ep/q1–q3.mjs`); it adds name cards,
  a camera viewfinder (REC ●), slow motion with falling sunflowers, a freeze-frame group photo, chorus lines and the
  `love` music sting. Start a new episode of the series from it (story.md §8).

`SK` = this skill's folder (`~/.claude/skills/comedy-cartoon-2d`).

## Requirements
macOS (Apple Silicon is best), Node 18+, ffmpeg. Dialogue uses VoxCPM2 from `$VOX_PY`, the khmer-2d-animation
skill's venv or `~/voxcpm-env`. If none exists, `npm run voices` prints the one-line install
(`python3.12 -m venv ~/voxcpm-env && ~/voxcpm-env/bin/pip install voxcpm soundfile`). The Khmer Whisper check
(`npm run asr`) also needs `transformers` in that venv (khmer-2d-animation's venv has it). The Koulen Khmer font
is bundled. Characters must be **original designs**; never recreate existing cartoon characters,
even renamed.

## Workflow

Show the user the plan and early stills before the expensive steps. Voices take minutes and you can't listen to
audio, so catch problems in pictures and timelines.

### 1. Understand the brief → shot list
Read the whole brief. Pull out the characters (look, personality, silhouette hook), the beats with their target times,
each gag, the camera language, the audio wishes and the length. Write `docs/shotlist.md` in the project: a table
of shot id, start–end, framing (wide/medium/CU/insert/low angle/top-down), action, the gag and the cues. Hit the
brief's beat timings. Comedy needs room: 1.5–4 s for a gag or reaction, 0.8–2.5 s cuts in chases, and holds before
punchlines. See `references/craft.md` for timing patterns and staging.

If the brief is thin, invent gags in its spirit (rule of three, contrast, deadpan to camera, the reveal pan, a
one-sound button) rather than asking many questions. Ask only about real forks, such as the dialogue language
when it's unclear.

### 2. Scaffold
```
SK/scripts/new_project.sh <project-dir>                         # starter film (3 shots) to replace
SK/scripts/new_project.sh <project-dir> --example getaway-car   # the full comedy example (builds offline)
SK/scripts/new_project.sh <project-dir> --example team-story    # the full story example (builds offline)
SK/scripts/new_project.sh <project-dir> --example kimlong       # Office series Ep 7 with the series cast (builds offline)
```
The project gets `src/` (engine plus your film), `voices/`, `film.json` (title and `"style": "bold"` or
`"pastel"`), `package.json` scripts and `node_modules`. Use `bold` (the *Getaway Car* look: thick black ink,
saturated city colours) unless the brief asks for soft or pastel; if the user points at Getaway Car, use bold. The starter `src/shots.mjs` shows every pattern in about 70 lines. `npm run build` on it should work
straight away; use that as a smoke test.

### 3. Cast → model sheet
For cartoony comedy characters use `src/chars.mjs`. Its example cast (round nervous guy, tall lanky boss, bored
cop on a bike, a car with a bumper face, ducks, loot) is a set of rig templates: reuse them when they fit, or
copy the closest rig and change it. For natural-proportion people who talk (adults, office workers, families)
use `src/people.mjs`: `person(ctx, look, o)` with a `CAST` look per character, about 25 poses, expressions,
props and a `mouth` input for lip-sync (story.md §2). Every rig takes `x, y, s, flip, rot, sq` (squash/stretch), `t`, `pose`, `expr` and `look`
(`references/engine.md` lists them all). Edit `src/sheet.mjs` and run `npm run sheet`, then **look at**
`build/stills/sheet.png`. Check that silhouettes differ, faces read at small size, and limbs read against dark
shapes (add socks, cuffs or highlights). Fix problems now; they get expensive later.

### 4. Sets
Build locations in `src/bg.mjs` from the existing pieces (sky, parallax city rows, shop row, street, speed-line
loop, bank, drive-through, bridge, police station, top-down city) or new ones in the same flat style. Fill every
region the camera can see, since zoomed-out shots expose holes.

### 5. Shots: animate, then look
Write `src/shots.mjs` shot by shot: `shot(start, end, (ctx, lt, t) => {...}, cues)`, or for dialogue films
`take(len, draw, cues)` with lengths from `beats(['line', gap, 'line'])` so the timeline follows the real
voices (story.md §1). Pass `mouth: talk(who, t)` to people so they lip-sync. Use `cam()` for framing,
`onTwos(lt)` for character cycles, anticipation → smear (ghost copies plus streaks) → squash → `wobble` settle for
actions, and `fx.sfxText` for sound words. After every few shots run
`npm run stills -- <times>` and **Read the contact sheet**. Look for the problems in `references/craft.md`
"QC checklist": hidden or overlapped characters, clipped text, wrong window clipping, effects drawing too early,
background holes. Fix them before moving on. Rendering is cheap (about 25 s for 90 s), so iterate.

### 6. Dialogue (VoxCPM2)
Write `voices/lines.json`: one voice per character (English *design* description, sample sentence, seed) and
short punchy lines with a translation (`references/voices.md`). For Khmer, write natural colloquial Khmer, names
in Khmer script, and Khmer lettering for any on-screen words that echo a line. Then:
```
npm run voices      # run_in_background: ~1–2.5 min model load + 10–60 s per line
```
Tell the user the ETA. It locks `voices/<who>.wav` once and clones every line from it, so voices stay consistent.
Add each line's id as a cue at the moment it should be spoken. Start the voices as early as possible: you can
stage the whole film on estimated timings while they generate. Split long speeches at sentence breaks into
separate lines. A narrator is just another voice. If the brief changes a character or a line while voices are
running, stop the job and regenerate only what changed (story.md §7).

When the clips are done, run `npm run asr` (Khmer Whisper) and re-roll the weak lines with a new seed, keeping the
better take of each (`npm run asr -- <ids>` compares them; voices.md "Checking clips without ears").

### 7. Sound
Add cues to every shot: SFX on contact frames, a whoosh under every smear, stings on reactions, music sections as
`music`/`music_end` pairs (comedy: chase, sneak, muzak, tension, vamp; story: warm, upbeat, build, triumph,
tender, tech, love, game; `cut`/`fade`/`tapestop` endings), ambience (`room_tone`, `city_amb`, `night_amb`), and silence
before reveals. The full catalogue is in `references/audio.md`. Then run `npm run audio`. It prints the real
dialogue timeline and warns about **overlapping lines** and **unknown cues**. Khmer lines often run longer than
planned; fix that by moving cues or growing the shot with `setShift()` and trimming elsewhere (craft.md
"Retiming").

### 8. Build and QC
```
npm run build       # video + audio + mux (soft subtitles) + qc
```
This writes `film/<title>.mp4`, `film/<title>.<lang>.srt`, and in `film/qc/` a contact sheet, a spectrogram and
levels. Read the contact sheet and spectrogram, check levels (no dead or clipped windows), and extract 3–6
full-res frames of key gags with ffmpeg and look at them. You can't hear the result: say that you verified
timing, levels and spectrogram, and ask the user to listen.

### 8b. Cover
Make a cover (thumbnail) with `src/cover.mjs`. Start from `examples/team-story/src/cover.mjs`:
- the cast big in front, with heads in the lower half
- a bold title banner (Khmer title in Koulen plus an English line)
- role or hook tags placed over each character
- the film's key location behind them, with a light burst

`npm run cover` writes `film/cover.png` (1920×1080) and `film/cover_1280.jpg`. The next `npm run mux` (and
`npm run build`) embeds the cover as the MP4's thumbnail. Look at the cover before delivering. Faces should read
as the intended emotion at thumbnail size: a mustache drawn as an arch reads as a frown.

### 9. Deliver
Copy or point to the MP4, SRTs and cover, and give the runtime, the beats/shots summary, the cast and voices, and any
caveats:
- VoxCPM may mispronounce words.
- Khmer should get a native speaker's review.
- Which sound words stayed English.

Offer specific next tweaks.

## Making changes later
- Retime a beat: edit its shot's end, `setShift()`, then rebuild. Cues follow automatically.
- Change a line: edit `voices/lines.json`, delete `build/vox/<id>.wav`, run `npm run voices`, then
  `npm run audio && npm run mux`.
- Redesign a voice only when asked: delete `voices/<who>.wav` and that character's clips.
- Visual-only edits: run `npm run video && npm run mux`.

## Files
| path | purpose |
|---|---|
| `scripts/new_project.sh` | scaffold a project (starter or example) |
| `template/src/core.mjs` | palette, easing, `paint/cel/hose/smooth/text` primitives, `onTwos`, `wobble`, Khmer font switch |
| `template/src/kit.mjs` | `shot/setShift`, `take/beats/talk` (voice-driven timing + lip-sync), `cam/shk/toScreen`, `titleCard`, `perspStreet`, `radialLines`, `drawFrame/allCues` |
| `template/src/people.mjs` | natural-proportion person rig (poses, expressions, props, lip-sync, back view, mirror) and the Office series `CAST` |
| `template/src/screens.mjs` | phones, laptops, security icons (optional) |
| `template/src/vox.mjs` | dialogue clips: pause-tightening, real durations, lip-sync envelopes (`npm run durations`) |
| `template/src/chars.mjs` | example cast rigs (templates for new characters) |
| `template/src/bg.mjs`, `fx.mjs` | sets and props; effects (dust, impact, lettering, siren wash, iris, smear streaks) |
| `template/src/render.mjs` | `stills` contact sheets and parallel `video` render |
| `template/src/audio.mjs` | cue-driven score, SFX synths, VoxCPM dialogue, mix, subtitles, warnings |
| `template/src/build.mjs` | `mux` (MP4 + soft subtitle tracks) and `qc` |
| `template/voices/` | `lines.json`, `make_jobs.py`, `run.sh`, `tts_vox.py` (VoxCPM2 worker), `asr_check.py` (Khmer Whisper check, take comparison) |
| `examples/getaway-car/` | 90 s comedy: `src/shots.mjs`, `prompt.md` (brief + staging table), voices, clips, contact sheet, `Getaway Car.mp4` |
| `examples/team-story/` | ~3 min Khmer story: `src/` (shots, sets, its own `cast.mjs`, cast sheet), `prompt.md`, voices, clips, contact sheet, sample MP4 |
| `examples/kimlong/` | Office series Ep 7 (3:44 Khmer story): `src/` (`ep/` scene files and series helpers, `places.mjs`, `ep6.mjs`/`ep7.mjs` props and effects, cover, cast sheet), `prompt.md`, 11 locked voices, 79 clips, contact sheet, cover |
| `references/engine.md` | every drawing/rig/set/fx API |
| `references/audio.md` | cue catalogue, music sections, mix, checking audio without ears |
| `references/voices.md` | lines.json, VoxCPM2 flow, writing Khmer, fitting lines to picture |
| `references/craft.md` | style bible, comedy timing, staging, retiming, QC checklist |
| `references/story.md` | dialogue-driven films: voice-driven timeline, people rig, lip-sync, staging, revising briefs, series episodes |
