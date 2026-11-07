# logo-gp

**generate-logo** is a skill for [Claude Code](https://claude.com/claude-code) that turns any logo image into finished 5-second animated logo reveals. Each one is a 1080p60 MP4 with synthesised sound, plus transparent WebM/ProRes versions for video editors.

Five built-in styles work on any logo:

| Style | What happens |
|---|---|
| **liquid** | A drop of the logo's main colour lands and spreads into the shape; other shapes and letters squeeze out as beads. |
| **neon** | On a dark page, glowing tubes trace the logo, it lights up, and the letters flicker on like a neon sign. |
| **bounce** | Shapes tumble or roll in and bounce, a confetti pop, then the letters drop in. |
| **lens** | A magnifier glides over an empty page showing the logo through its glass, then zooms out to reveal it. |
| **rise** | A brand-coloured hairline opens into a band and the shapes rise into it. |

Everything is drawn in code on an HTML canvas, rendered by headless Chrome and encoded with ffmpeg. The sound effects are synthesised, with no samples or AI services. The final frames are always the logo file's own pixels.

## Install

```bash
git clone https://github.com/chydevit/logo-gp.git
mkdir -p ~/.claude/skills
ln -s "$PWD/logo-gp/generate-logo" ~/.claude/skills/generate-logo
```

Requirements: Node 22+, ffmpeg (with libx264, libvpx-vp9, prores_ks) and Google Chrome or Chromium. If Chrome isn't in a standard location, set `CHROME_PATH`.

## Use

In Claude Code:

```
/generate-logo animate logo.png
/generate-logo make neon and lens versions of brand/logo.png, square for Instagram
/generate-logo animate mark.png and add the name "Pharm|Kulen" next to it
```

Or run the script directly:

```bash
generate-logo/scripts/animate.sh logo.png                          # all five styles
generate-logo/scripts/animate.sh logo.png --styles neon,lens --size square
generate-logo/scripts/animate.sh logo.png --text "Pharm|Kulen" --font "Arial Rounded MT Bold" --prores
generate-logo/scripts/animate.sh logo.png --preview                # quick stills only
```

Each style writes `<name>-5s-<style>.mp4`, `-alpha.webm`, `-sfx.wav`, `-keyframes.png` and `-info.json` to `./<name>-animations/` (and `-alpha.mov` with `--prores`).

| Option | |
|---|---|
| `--styles a,b` | liquid, neon, bounce, lens, rise, or `all` (default) |
| `--size` | `1920x1080` (default), `square`, `vertical`, or any `WxH` |
| `--bg` | `auto` (default), `light`, `dark`, or `#rrggbb` |
| `--text "A\|B"` | add a wordmark; `\|` splits it into two colours taken from the logo |
| `--font`, `--text-colors` | wordmark font and colours |
| `--fps` | default 60 |
| `--prores` | also write ProRes 4444 with alpha |
| `--no-alpha` | skip the transparent WebM |
| `--preview` | only render a keyframe sheet per style |

Logos with a transparent background work best. Logos on a flat background (JPG/PNG) are cut out automatically.

## Writing your own style

See [`generate-logo/references/custom-style.md`](generate-logo/references/custom-style.md) for the style API, the engine helpers, sound events and the techniques that make a bespoke logo animation look right.
