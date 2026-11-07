---
name: generate-logo
description: Turn any logo image (PNG, JPG, WebP or SVG) into finished 5-second animated logo reveals in five styles (liquid, neon, bounce, lens, rise). Each comes as a 1080p60 MP4 with synthesised sound effects, a transparent WebM (optional ProRes 4444 .mov) for video editors, and a keyframe sheet. It can add a two-tone wordmark, render square or vertical versions for social media, and build a bespoke style for a particular logo. Use it whenever the user wants a logo animation, animated logo, logo reveal, intro, outro or sting, motion logo, a brand intro for a video, or "make my logo move", or types /generate-logo, even if they only attach a logo and say "animate this".
---

# Generate logo animations

This skill turns a logo image into 5-second animated reveals. Each style is a canvas scene that headless Chrome renders frame by frame. ffmpeg encodes the frames, and the sound is synthesised from events the scene reports (landings, pops, flickers). There are no AI image services, stock footage or samples. The last frames of every style are the logo file's own pixels, so the animation never "redraws" the brand.

Requirements: Node 22+, ffmpeg (libx264, libvpx-vp9, prores_ks) and Chrome or Chromium. If Chrome isn't in a standard location, set `CHROME_PATH`.

## Workflow

### 1. Find and look at the logo
Locate the file the user means: check the working directory, `~/Downloads` and `~/Desktop`, or ask. **Read the image** before rendering. Note whether it has a transparent or flat background, how many separate shapes it has, whether it already includes a wordmark, and its colours. This decides which styles will shine. Keep it in mind when you check the preview.

### 2. Settle the brief, using defaults rather than questions
Defaults are all five styles, 1920×1080 at 60 fps, automatic background, and MP4 plus transparent WebM. Only ask when the answer changes the output and you can't infer it. For example, if the user wants a name added but you don't know the exact spelling or where the colour split goes.

| User wants | Option |
|---|---|
| specific styles | `--styles liquid,neon` |
| Instagram / square, TikTok / Reels / vertical | `--size square`, `--size vertical` (or `--size 1280x720`) |
| a brand name next to the mark | `--text "Pharm\|Kulen"` (the `\|` splits it into two colours taken from the logo), `--font "Arial Rounded MT Bold"`, `--text-colors "#0a3fa8,#ff9a00"` |
| dark or light page | `--bg dark`, `--bg light`, `--bg "#0b1e2d"` (neon is always dark) |
| files for Premiere / Final Cut | `--prores` (adds a large ProRes 4444 .mov with alpha) |

### 3. Preview first (seconds, not minutes)
```bash
<skill>/scripts/animate.sh "<logo>" --preview --out "<out-dir>" [options]
```
This writes `<name>-5s-<style>-preview.png` (10 stills per style), plus `<name>-5s-overview.png` when there are two or more styles, and an `-info.json` per style. Read the overview and check:
- **Cut-out:** a clean edge, and no background colour or specks inside the logo. `keyedBackground` in info.json is set when the background was keyed out (no transparency in the file).
- **Grouping:** `parts` is the number of separate shapes and `textParts` the number of letters it found. Letters must be detected as text for neon flicker, liquid beads and bounce drops to treat them as a word.
- **Framing:** nothing is cropped and the size looks right.

If something is off, see "Fixing analysis problems" below. Show the overview to the user if they want a say before the full render.

### 4. Render
```bash
<skill>/scripts/animate.sh "<logo>" --styles <list> --out "<out-dir>" [options]
```
Each style takes about 60–70 s (the opaque and transparent passes plus encoding). For four or more styles, run it in the background. Outputs per style go in the output folder:
`<name>-5s-<style>.mp4` (with sound), `-alpha.webm`, `-alpha.mov` (with `--prores`), `-sfx.wav`, `-keyframes.png` and `-info.json`.

### 5. Check before you hand it over
- Read each `-keyframes.png`. The last still must be the clean, complete logo.
- Use `ffprobe` to confirm 5.000 s duration and the size. Sound peaks are normalised to −3 dB.
- Send the MP4s and the overview to the user (SendUserFile when available) and list every file as a link. Mention the transparent versions and what each style does in a line each.

### 6. Iterate
Timing lives in each style's `T` object in `scripts/styles/<style>.mjs`. Every other timing hangs off it, and the sound follows automatically, so change it there. For a look the five styles can't give, or a logo whose shapes should do something specific, write a new style. See `references/custom-style.md`.

## The styles
Full details are in `references/styles.md`; read it when choosing for a user or explaining what each does.
- **liquid**: a drop of the logo's main colour falls onto the page and spreads into the biggest shape. The other shapes and letters squeeze out as beads. Best for rounded, organic logos.
- **neon**: on a dark page, glowing tubes trace each shape, the logo lights up with a flash, and letters flicker on like a sign. Very dark shapes become white.
- **bounce**: big shapes tumble down or roll in and bounce like plastic, followed by a confetti pop, then the letters drop in. Playful.
- **lens**: a magnifier glides across an empty page, and the logo shows only through its glass. It then zooms out from the main shape. Suits search, health or insight brands.
- **rise**: a brand-coloured hairline opens into a band and the shapes rise into it. Calm and corporate, and it works on anything.

## Fixing analysis problems
- **Halo or background left around a JPG logo:** the background is keyed by its border colour. If the logo touches the image edge, or sits on a gradient or photo, cut it out first (export a transparent PNG) and rerun.
- **White details disappear** (a white shape on a white background): that's correct keying. Use a transparent PNG if those white parts must show.
- **Letters not detected as text:** they need 3+ separate letters of similar height in one row beside or below the main shape. Joined script or a single-shape wordmark is treated as one part, which still animates fine in rise and lens.
- **Wordmark in the wrong font:** `--font` must be installed on the machine. Check `fc-list`, or look in `/System/Library/Fonts` on macOS.

## Making a bespoke style
When the user wants something specific, such as "the pills should fall into place" or "the magnifier should scan", read `references/custom-style.md`. It covers the style API, the engine helpers, the sound event list, and the techniques that made earlier bespoke logo animations work well. These include rebuilding the mark as vector shapes, checking that rebuild against the PNG, and handing over to the real pixels at the end.
