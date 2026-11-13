---
name: brand-promo
description: Make a ~50-second dark, kinetic studio showreel / promo video from a brand's own videos, its logo animation and a few lines of text. It has a typed intro, a ring of 3D cards, a glitchy title drop, and 3-5 spotlights (each work on a tilted card or a phone, playing its own sound). Then "Your story… next.", a 3D rush of clips, and the liquid logo reveal with the name, chips and website. It comes with an original synthesised score, narration (VoxCPM2, English or Khmer) and sound effects, as a 1080p60 MP4. Use it whenever the user wants a showreel, studio reel, portfolio video, agency or brand promo, "demo video" of their work, a promo like a template video, or a Khmer version of one, or types /brand-promo, even if they only hand over a few videos and a logo.
---

# Brand promo (studio showreel)

This skill makes one finished promo video from a single config file, `promo.json`. A canvas scene draws every frame in headless Chrome, so the video is pure motion design with no templates or stock footage:
- **Picture:** the brand's own clips, its logo animation, its texts.
- **Score:** an original synth track made in code (128 bpm). Every cut, drop and hit sits on its bars.
- **Narration:** VoxCPM2, run locally.
- **Sound:** each work's own audio plays in its spotlight.

The structure is fixed and works at any brand scale. Only the content changes.

| Time | Section |
|---|---|
| 0-3.4 s | `{ Every story }` typed in, then "deserves to **move.**" |
| 3.2-7.6 s | a ring of 3D cards (stills from all the works): "Here are five of **ours.**" |
| 7.6 s (bar 4) | the drop: eyebrow, the brand name in a glitching accent box, a subline |
| 9.5 s + 5.6 s each | one spotlight per work: title block plus the work on a tilted card (16:9) or a phone (9:16), "Full video · m:ss" chip, its own sound with live level bars |
| break | "Your story" then a big "**next.**" on the last word of the narration line |
| rush | every clip flies past in 3D, with three words (Written · Voiced · Animated) on the narrator's phrases |
| end | the liquid logo lands on the final hit, slides left, the name wipes in, then the chips and the URL |

The length is 51.5 s with 5 works, 45.9 s with 4 and 40.2 s with 3.

Requirements:
- ffmpeg, Node 22+ and Google Chrome or Chromium (`CHROME_PATH`).
- A Python with numpy and scipy (`PROMO_PY`).
- For narration, VoxCPM2 (`VOX_PY`, see `scripts/voices.py`). Without it the promo has no narrator, or you can drop your own recordings in `build/vox/<id>.wav`.

## Workflow

### 1. Gather what the promo needs
- **3-5 works:** finished videos of the brand's work, at any length. A vertical video plays on a phone, a landscape one on a card. Watch for:
  - A good **sound moment** in each, such as a sentence start or a punchline: 4 s of it play in the spotlight. Give its start time as `sound`, or leave it out and the start of a quiet gap near 35 % of the video is used.
  - Set `"mute": true` for a work whose sound shouldn't play.
- **The logo animation**, with transparency. The best source is `/generate-logo` with the liquid style:

  ```bash
  generate-logo/scripts/animate.sh logo.png --styles liquid --prores
  ```

  This gives `<name>-5s-liquid-alpha.mov` plus its `-sfx.wav`. A transparent `-alpha.webm` or a transparent PNG also works.
- **Brand facts:**
  - The name, split into two colour parts (`["KumNit", " Studio"]`).
  - The colours: two gradients for the name, an accent, a second accent and a warm accent. Read the logo for them.
  - The website.
  - What the brand makes: the four chips.
- **Language:** `"lang": "en"` or `"km"`. For Khmer, write every text and narration line in natural Khmer. Kantumruy Pro and Koulen are bundled.

### 2. Write the project
Make a folder for the project and copy `examples/kumnit-showreel.json` into it as `promo.json`, then edit it. Every key is described in `references/config.md`. Keep the texts short: titles of one to three words, lines of up to six words. Long lines shrink to fit, but they read worse.

Write the narration in `voice.lines` as one short sentence per moment:
- `next` should end on the word shown big. For example, "Your story could be **next**."
- `rush` needs three phrases separated by commas, one per rush word ("We write it, voice it, and animate every frame.").

### 3. Preview (about 30 s)
```bash
<skill>/scripts/promo.sh <project>/promo.json --preview
```
This cuts the assets, plans the timings and renders 12 stills to `out/<name>-preview.png`. **Read it** and check:
- The cards show the right moments.
- No title is crammed.
- The logo is framed (its mark should fill about 60 % of its box).
- The spotlights alternate sides.

To fix a picture, change the `sound` start of that work. Then delete `assets/clips/p<k>`, `assets/bites/p<k>.wav` and `assets/manifest.json`, and run the preview again.

### 4. Render (about 10 minutes the first time)
```bash
<skill>/scripts/promo.sh <project>/promo.json        # run in the background
```
The stages run in this order: assets, voices, plan, music, mix, render, encode.
- **Voices:** the first run loads the model (about 2 min), then takes 10-60 s per line. Lines that already exist are kept, so delete a `build/vox/<id>.wav` to redo it.
- **Rendering:** about 4 min with 2 Chrome processes.
- **Resuming:** `--from mix` (or `render`, or `encode`) reruns from that stage only.

Output: `out/<name>-1080p60.mp4` and `out/<name>-contact.png` (one frame per second).

### 5. Check before handing it over
- Read the contact sheet.
- `ffprobe` should show the expected length (51.5 s with 5 works).
- The mix is normalised to -14 LUFS.
- You can't hear the result, so tell the user what you checked (timings, levels, frames) and ask them to listen. Pay most attention to the narrator over each work's own sound.

## Tuning
- **Sound effects:** set `sfxDir` to a folder of the user's own sound effects and the file names in `scripts/audio.py` (`SFX`) are tried first. Anything missing is synthesised, so the skill also works with no library.
- **Timings:** these are measured from the narration in `scripts/plan.py`. Each work's sound starts after its narration line and stops before the next spotlight. To change the rules, edit `plan.py`, not the scene.
- **Look:** colours come from `brand`, all motion is in `scripts/scene.mjs`, and the score is in `scripts/music.py`, whose bar layout is documented at its top.
