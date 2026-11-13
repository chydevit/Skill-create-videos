---
name: saas-promo
description: Make a kinetic SaaS / startup / product / developer promo video (1080p60 MP4) in one fixed, fast motion-design style: an ~11-second teaser, or a ~50-second version with chapters (one per product or project) cut on the beat of the user's own song. It opens with glyph flashes and purple/lime neon shapes, then types a word with a cursor while a 3D swirl of your screenshots orbits it. Cards slide onto a painted meadow and build a bento wall with words typing inside them, and the camera zooms into a card. A glowing gradient orb then reveals the headline word by word, and a glitch drops into a long-exposure flower on a blue-to-orange sky with flying symbols and "From … / To …". Every frame is drawn in code, with typing, whoosh, riser and impact sound effects and a synthesised ambient bed or your own song (its tempo and drop are measured, so every cut lands on the beat), mixed to -14 LUFS. English or Khmer. Use it whenever the user wants a SaaS promo, product or app teaser, a developer or portfolio promo, a longer 30-60 s promo set to a song, startup launch video, website / UI showcase, agency teaser, a short promo "like this template" or like "skill 1", a Khmer version of one, or types /saas-promo, even if they only hand over a few screenshots and a headline.
---

# SaaS promo (template: "skill 1")

This skill makes one finished promo from one config file, `promo.json`: the classic ~11 s cut, or a ~50 s long cut when `promo.json` has `chapters`. A canvas scene draws every frame in headless Chrome. There is no stock footage, AI video or template service:
- **Picture:** the user's own screenshots, app UI, designs or video stills. Built-in UI cards fill any gaps.
- **Words:** the user's own texts.
- **Sound:** an effect on every cue, plus an original synth bed or the user's own track.

The structure is fixed and copies the pacing of the reference reel `skill 1 .MP4` (a TikTok SaaS-agency reel). Only the techniques are copied, never its footage, words, branding or watermark.

| Time | Scene |
|---|---|
| 0-0.5 s | big glyphs (`# < @ ! ?`) flash in the centre; purple and lime neon bars and 4-point sparkles strobe on a dim dot-matrix glyph field |
| 0.5-3.3 s | `text.typed` types in with a cursor; 26 cards fly in from far away and orbit the word as a 3D ring (halftone dots first, then the real picture); the ring speeds up, rushes past the camera and blurs out |
| 3.3-6.45 s | a painted meadow with clouds, birds and butterflies, pastel-washed and then saturating; three cards slide in on the right, then the rest fly into a 12-card bento wall. `bento[0]` types on the hero card, `bento[1]` types vertically on a tall glass card, two cards swap pictures, and `bento[2]` types on a white card. The camera then zooms into that card |
| 6.45-~8.8 s | dark dot-wave field; a glowing gradient orb pops in and slides left; `headline` appears word by word (blur to sharp), then `sub` wipes in; everything defocuses |
| ~8.8-11.1 s | glitch (hue-shifted, sliced) into the hero: a long-exposure blue/white flower on a blue-to-orange sky, flying `! @ # $ % *` symbols and digital rain. `from` blurs in and out, then `to` lands with a boom and the optional logo appears under it. It ends with a fade to black |

The length is about 11.1 s. It grows slightly with a long headline, because the subline always gets about 0.85 s on screen.

### Long cut (~50 s): `chapters`
Add `"chapters"` (one per product, project or theme) and the same four scenes repeat as **beats** of 1.5 bars each, with the finale taking 2 bars:

| Beats | What plays |
|---|---|
| intro | open (`typed` + swirl of everything) → wall (all pictures, `bento`) → orb (`headline` / `sub`) |
| each chapter | open (the chapter's `typed`, its pictures in the swirl; skipped without `typed`) → wall (its pictures first, its `bento`, its `wall` look) → orb (its `headline` / `sub` / `orb` colours) |
| end | finale (`from` / `to` / `url` / logo), 2 bars |

Four chapters with three typed openers give 23 bars, which is ~50 s at 109 BPM.
- **Pictures:** tag each with `"tag"` to file it under its chapter.
- **Wall looks:** `"meadow"` (day), `"dusk"` (sunset) or `"dark"` (the dot-wave field with glows in the chapter's orb colours). Alternating them keeps the chapters apart.
- **Music sync:**
  - With `music`, `assets.py` measures the song's tempo and its drop (the biggest lift in energy, snapped to a kick drum). The video starts so that the first cut, after the intro swirl, lands on the drop, and every later cut sits on the bar grid.
  - Check the printed `music: … bpm, drop at … s` line. If it's wrong, give `bpm` and `musicDrop` (song seconds) yourself.
  - Use `sfxLevel` (for example -4) to sit the effects under the song.
- **Copyright:** a commercial song can get the video muted or claimed when posted. Mention this, and suggest the platform's own sound library for public posts.

Requirements: ffmpeg, Node 22+, Google Chrome or Chromium (`CHROME_PATH`), and a Python with numpy and scipy (`PROMO_PY`; `promo.sh` finds one by itself).

## Workflow

### 1. Gather what the promo needs
- **Cards (8-20 pictures):** screenshots of the product, website, app or dashboard; design work; or stills from the user's videos. Images and videos both work. A video gives one still, at `"at"` seconds or at 30 % of its length. Landscape pictures go to the wide slots and portrait ones to the tall slots. With fewer than 8, built-in UI cards fill the rest (search bar, form, chart, gradient orb, pill and so on, labelled with `text.labels`). Look at the pictures first and drop ones that are mostly empty.
- **Texts:** keep them short, because the scene types and reveals them at fixed speeds.
  - `typed`: one word or name with punctuation, about 4-8 letters ("SaaS.", "KumNit.").
  - `bento`: three short phrases (1, 2-4 and 2-3 words).
  - `headline`: 5-8 words. `sub`: one line of up to about 90 characters.
  - `from` / `to`: the closing "From … / To …" pair.
  - For Khmer (`"lang": "km"`), write natural Khmer. Put a space between the chunks of `headline`, `from` and `to` that should appear one at a time. Kantumruy Pro is bundled.
- **Optional:**
  - `logo`: shown under the last line. An opaque logo becomes a rounded app icon.
  - `text.url`: a website line on the end card.
  - `hero`: the user's own finale image instead of the flower.
  - `backdrop`: an image instead of the painted meadow.
  - `music`: their own track. In the long cut its drop lands on the first cut; set `musicStart` to override.
  - `chapters`: the ~50 s long cut, with each chapter's `tag`, `typed`, `bento`, `headline`, `sub`, `wall` and `orb`.
  - `sfxDir`: a folder of their own sound effects.
  - `colors`: brand colours for the neon, orb, sky and symbols.

### 2. Write the project
Make a project folder and copy `examples/kumnit-saas.json` (or `-km.json`) into it as `promo.json`, then edit it. Every key is described in `references/config.md`. Paths are relative to the project folder.

### 3. Preview (about 10 s)
```bash
<skill>/scripts/promo.sh <project>/promo.json --preview
```
This prepares the pictures (and measures the music) and renders 12 stills (one per beat in the long cut) to `out/<name>-preview.png`. **Read it** and check:
- The typed word is clear of the cards.
- No text is crammed: long texts shrink to fit, but they read worse.
- The hero card (big, left) shows a good picture: it takes the first landscape picture in `cards`.
- The finale text is readable over the flower or hero.

### 4. Render (under a minute; about 4 minutes for the long cut, so run that one in the background)
```bash
<skill>/scripts/promo.sh <project>/promo.json
```
The stages run in this order: assets, plan (timeline and sound cues from the scene), render (3 Chrome renderers, `--jobs N`), mix, encode.
- `--from mix` re-mixes the sound and re-encodes without rendering the frames again.
- `--from render` redraws the picture.

Output: `out/<name>-1080p60.mp4` and `out/<name>-contact.png` (about 30 frames across the video).

### 5. Check before handing it over
- Read the contact sheet.
- `ffprobe` should show about 11.1 s (classic) or the beats' total (long; `build/cues.json` lists every beat). The mix is normalised to -14 LUFS / -1 dBTP: measure it with `ffmpeg -i out.mp4 -af ebur128 -f null -`.
- The mix stage prints how many effects came from `sfxDir` and how many were synthesised.
- You can't hear the result, so tell the user what you checked and ask them to listen. The intro clicks and the meadow impact are the loudest moments.

## Tuning
- **Timing:**
  - `plan()` at the top of `scripts/scene.mjs` holds the classic scene times.
  - `beatSpecs()` lays out the beats: `mapT()` moves and stretches those times into each beat.
  - The sound cues in `cuesFor()` follow automatically, because `audio.py` reads them from `build/cues.json`.
- **Look:**
  - Colours come from `colors`.
  - The bento layout is the `SLOTS` table in `scene.mjs`.
  - The meadow, flower and orb are drawn in `buildMeadow`, `drawFlower` and `drawOrb`.
- **Sound:** the file names tried in `sfxDir` are the `SFX` table in `scripts/audio.py`, with variants picked per cue. The bed's chords and sections are in `make_bed()`.
- **Size:** 1920×1080 only, as in the template. A vertical 9:16 version would need its own layouts.
