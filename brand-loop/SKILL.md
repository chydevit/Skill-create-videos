---
name: brand-loop
description: Make a seamless looping background video of glossy 3D liquid blobs in a brand's colours. Two colour families float slowly in zero gravity, each merging and pinching off like mercury, on a soft off-white studio backdrop with a warm gradient, faint ripple rings, soft drop shadows and shallow depth of field. It renders in Blender EEVEE at 4K 60 fps as H.264, HEVC 10-bit and 1080p, and the last frame flows into the first. Use it whenever the user wants a looping background, brand backdrop, abstract 3D or liquid loop, motion background for a website, stream, event screen or presentation, a "seamless loop", or a background for their logo or text, or types /brand-loop.
---

# Brand loop (seamless liquid background)

`scripts/scene.py` builds the whole studio in Blender and renders it:
- **Blobs:** metaballs in two families that merge only with themselves. They're glossy and liquid-like, with a two-tone colour that follows each blob's squash.
- **Backdrop:** a warm off-white wall with ripple rings expanding from the centre, two per loop.
- **Lighting:** an elliptical key light with soft shadows, plus reflection-only softboxes for the liquid sheen.
- **Camera:** a 50 mm lens at f/2, giving shallow depth of field.

Every motion is a sine of whole cycles per loop, so frame N equals frame 0 exactly. The centre of the frame stays open for a logo or title on top. The video has no text and no sound.

Requirements: Blender 4.2+ with EEVEE (tested on 5.2, Apple Silicon GPU), and ffmpeg with libx264 and libx265.

## Workflow

### 1. Colours
The cool family uses 5 shades, dark to light, for the big blobs. The warm family uses 3 shades for the accent blobs. You can get them two ways:
- **From a logo:** `python3 scripts/palette.py logo.png` prints its main colours and a suggested `--cool`/`--warm` pair. You can also pass `--logo logo.png` to `loop.sh` directly.
- **From brand hex values:** fewer shades are fine, because they're interpolated.

Keep the two families clearly different, such as blue and orange or teal and coral. Mixed colours would turn grey where blobs merge, so they're kept apart. `--paper "#fcfbf8,#f2eae0"` sets the backdrop's centre and corner colours.

### 2. Preview (about 1 minute)
```bash
<skill>/scripts/loop.sh --name acme --cool "#0b3d91,#1565c0,#1e88e5,#42a5f5,#80d8ff" --warm "#ff6f00,#ffa000,#ffca28" --preview
```
**Read** `<name>/<name>-preview.png`, which shows six moments across the loop, and check:
- The colours read as the brand's.
- The backdrop isn't grey.
- The two families never cut into each other.

### 3. Render (long: run it in the background)
```bash
<skill>/scripts/loop.sh --name acme --cool ... --warm ...            # 4K 60 fps, 10 s
<skill>/scripts/loop.sh --name acme --res 1920x1080 ...              # 1080p, about 4x faster
```
On an M1 Pro, a 10 s 4K60 loop takes about 95 minutes (600 frames, about 9.5 s each with 2 Blender processes), and 1080p about 25 minutes. The render resumes where it stopped if it's interrupted. Frames are deleted after encoding unless you pass `--keep-frames`.

Output in `<name>/`:
- `<name>-4k60-loop.mp4`: H.264, plays everywhere.
- `-loop-hevc10.mp4`: 10-bit, smoothest gradients, for editors.
- `-1080p60-loop.mp4`: for the web.
- `-still.png` and `-keyframes.png`.

### 4. Check
- The script prints a **seam check**. The PSNR of the last-to-first step must be close to the PSNR of a normal step; if it's much lower, something isn't periodic.
- Read `-keyframes.png`.
- Tell the user it loops with no visible seam, and remind them to turn on looping in their player or editor.

## Knobs
Pass any of these straight through to `scene.py`, either by editing `loop.sh`'s `LOOK` array or by running Blender yourself:
- `--key`, `--fill` and `--wash`: light levels.
- `--emit` and `--world`: backdrop brightness.
- `--ringamt` and `--ringbump`: how strong the ripples are.
- `--fstop`: blur (lower is blurrier).
- `--glow`: blob vividness.
- `--dur`: loop length; motion stays periodic at any length.

Layout, sizes and paths of the blobs are the `BLOBS` list in `scene.py`. Positions are in metres, and the frame at the focus plane is 0.864 × 0.486 m. After moving blobs, check that the two families never come closer than the sum of their sizes.
