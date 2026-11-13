---
name: portfolio-reel
description: Make a ~30-second creator / freelancer / developer portfolio intro reel (1080p60 MP4) in one fixed, friendly motion-design style (template "skill 2"). A mustard-yellow gradient asks a hook question ("Looking for a … Video editor?"), a white circle wipes to a profile hero (round avatar, badge pill, "Hello, I'm …", roles split by bars, a black "Here's my work ↑" button). The page then scrolls through 1-4 work sections on light grey with window-light shadows, each a title plus 1-3 rounded cards playing the user's own clips or showing their pictures. A yellow light wipe brings two closing lines, then a black social profile card pops up with counting stats, a cursor clicks Follow (it turns into Following) and the card flips in 3D to its back. Every frame is drawn in code, with typing, pop, whoosh and click sounds over a synthesised lo-fi beat (or your own track), mixed to -14 LUFS. English or Khmer. Use it whenever the user wants a portfolio reel, "about me" or intro video, a video CV or showreel for a creator, freelancer, editor, designer or developer, a "hire me" or "here's my work" video, a reel like "skill 2" or "like this template" with a profile card, or types /portfolio-reel, even if they only hand over a photo, a few clips and their name.
---

# Portfolio reel (template: "skill 2")

This skill makes one finished ~30 s intro reel from one config file, `promo.json`. A canvas scene draws every frame in headless Chrome and plays the user's clips inside the cards. There is no stock footage, AI video or template service. The structure copies the pacing of the reference reel `skill2.MP4` (a TikTok creator intro). Only the techniques are copied, never its footage, words, names, handles or watermark.

| Time (3 sections) | Scene |
|---|---|
| 0-2.3 s | mustard gradient, two big soft circles slide in; `hook[0]` types word by word, then `hook[1]` pops up big and bold |
| 2.3-2.9 s | a white circle wipes up from the bottom; the avatar pops in as a small yellow disc |
| 2.9-6.4 s | profile hero on white: the avatar grows into a big circle (with a yellow ring, or a yellow duotone), then the outlined `badge` pill with a star, `hello` word by word, `roles` split by thin bars, and a black `button` pill with ↑ in a white circle. The arrow shoots up and the page scrolls |
| 6.4-20.5 s | one page per section (4.6 s each) on light grey with soft window-light shadows: a gradient title, then 1-3 rounded cards trailing the scroll and floating. Videos play, pictures slowly zoom. Portrait cards stand tall, landscape cards go wide, mixed rows stagger |
| 20.5-24.4 s | a yellow light blooms from the bottom-left back to the gradient; `cta[0]`, then `cta[1]`, word by word |
| 24.4-30.3 s | a black profile card pops from a dot (avatar or `logo`, `handle`, `name`, up to 3 counting `stats`, two buttons). A cursor clicks the first button, which turns grey and shows `clicked`, then the card flips in 3D to its `back` |

The length is about 30 s with 3 sections, 4.6 s more or less per section, and a little longer with long texts.

Requirements: ffmpeg, Node 22+, Google Chrome or Chromium (`CHROME_PATH`), and a Python with numpy and scipy (`PROMO_PY`; `promo.sh` finds one by itself).

## Workflow

### 1. Gather what the reel needs
- **Avatar:** a portrait photo, face and shoulders. Give `crop: [x, y, size]` (pixels) so the face sits in the circle, and check the preview. With a busy or light background, `"avatarStyle": "duotone"` makes a dark figure on yellow, as in the template.
- **Sections (1-4):** a short title each (2-4 words) and 1-3 clips: videos (`{"file", "at"}`, 5.5 s from `at` play in the card) or pictures. Use the user's best work, and mix portrait and landscape for variety.
- **Texts:** keep them short.
  - `hook`: a small line and a big 1-2 word question.
  - `badge`: a slogan of up to about 50 characters.
  - `hello`: "Hello, I'm …".
  - `roles`: 2-4 short roles.
  - `button`: the button label.
  - `cta`: two closing lines.
- **Profile card:** `handle`, `name`, up to 3 `stats`, `buttons`, `clicked` and `back`. **Only use real numbers** (from the user, their site or their profile). A string value (like `"2023"`) is shown as is, without counting.
- **Language:** for Khmer, set `"lang": "km"` and write natural Khmer. Kantumruy Pro is bundled.
- **Optional:** `logo` (inside the card's circle), `colors`, `music` (+ `musicStart`), `sfxDir`.

### 2. Write the project
Make a project folder and copy `examples/creator-reel.json` into it as `promo.json`, then edit it. Every key is described in `references/config.md`. Paths are relative to the project folder.

### 3. Preview (about 10 s)
```bash
<skill>/scripts/promo.sh <project>/promo.json --preview
```
This cuts the clips and renders about 13 stills to `out/<name>-preview.png`. **Read it** and check:
- the avatar crop;
- that no line is crammed (long texts shrink);
- that each section's cards show good frames: change `at`;
- the profile card's numbers.

### 4. Render (about 2 minutes; run it in the background)
```bash
<skill>/scripts/promo.sh <project>/promo.json --jobs 4
```
The stages run in this order: assets, plan, render, mix, encode. `--from mix` re-mixes the sound without rendering the frames again.

Output: `out/<name>-1080p60.mp4` and `out/<name>-contact.png`.

### 5. Check before handing it over
- Read the contact sheet.
- `ffprobe` should show the length that `build/cues.json` gives. The mix is normalised to -14 LUFS / -1 dBTP.
- You can't hear the result, so tell the user what you checked and ask them to listen.

## Tuning
- **Timing:** `plan()` in `scripts/scene.mjs`. `SEC` is the length of a section and `SCROLL` the length of a page scroll. The cues in `buildCues()` follow automatically.
- **Look:**
  - Colours come from `colors`.
  - The card layout is `layout()`.
  - The window shadows are `buildShade()`.
  - The flip is `drawFlip()`, strips with perspective.
- **Sound:** `SFX` in `scripts/audio.py` lists the file names tried in `sfxDir`. `make_bed()` is the lo-fi beat.
