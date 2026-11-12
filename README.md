# logo-gp: brand motion skills for Claude Code

Three [Claude Code](https://claude.com/claude-code) skills that turn a brand's logo and its own work into finished videos, ready to post. Everything is drawn in code and rendered on your own machine. There is no stock footage, no template service and no AI video generator.

| Type this | You get |
|---|---|
| **`/generate-logo`** | 5-second animated **logo reveals** in 5 styles from any logo image, with sound and transparent versions |
| **`/brand-promo`** | a ~50-second dark, kinetic **studio showreel** of your work, with an original score, narration (English or Khmer) and each work's own sound |
| **`/brand-loop`** | a seamless 4K 60 fps **looping background** of glossy liquid blobs in your brand colours |

## Examples

### `/generate-logo`: logo reveals
| liquid style (the KumNit K) | a bespoke style set made for one logo (PharmKulen) |
|---|---|
| ![liquid logo reveal](docs/generate-logo-liquid.gif) | ![four styles](docs/generate-logo-styles.gif) |

### `/brand-promo`: studio showreel
![brand-promo: title drop and spotlights](docs/brand-promo.gif)

![brand-promo: one frame per second](docs/brand-promo-contact.jpg)

### `/brand-loop`: seamless liquid background
![brand-loop](docs/brand-loop.gif)

## Install

This repo is private, so your GitHub account needs access.

```bash
gh repo clone chydevit/logo-gp        # or: git clone https://github.com/chydevit/logo-gp.git
cd logo-gp
./install.sh
```

`install.sh` links every skill folder into `~/.claude/skills/`. **Start a new Claude Code session**, type `/`, and `generate-logo`, `brand-promo` and `brand-loop` appear in the list. Because they're links, `git pull` updates them in place.

| Command | What it does |
|---|---|
| `./install.sh` | install (link) |
| `./install.sh --copy` | install a copy instead of links |
| `./install.sh --remove` | uninstall |

## Use: just type `/` and the skill name

```
/generate-logo animate logo.png
/generate-logo make neon and lens versions of brand/logo.png, square for Instagram
/generate-logo animate mark.png and add the name "Pharm|Kulen" next to it

/brand-promo make a showreel from ex1.mp4 to ex5.mp4 with my logo animation
/brand-promo the same showreel in Khmer, with a Khmer narrator

/brand-loop make a 10 second looping background in the colours of logo.png
/brand-loop 1080p loop, teal and coral, for our website hero
```

You don't have to type the slash. Asking in plain words ("make a showreel of our work", "animate this logo", "a looping background in our colours") picks the right skill too. Claude looks at your files first, shows you a quick preview, then renders the full video.

## What each skill does

### `/generate-logo`
- **Styles:** liquid, neon, bounce, lens and rise. Every one ends on your logo file's own pixels.
- **Files:** each style comes as a 1080p60 MP4 with synthesised sound, a transparent WebM (and ProRes 4444 with `--prores`) and a keyframe sheet.
- **Extras:** square and vertical sizes, a two-tone wordmark (`--text "Pharm|Kulen"`), and bespoke styles for a particular logo.
- **Docs:** [generate-logo/SKILL.md](generate-logo/SKILL.md).

### `/brand-promo`
One `promo.json` file describes the whole video:
- 3-5 of your videos (vertical ones play on a phone).
- Your logo animation (made with `/generate-logo` liquid).
- Your name, colours, texts and narration lines.

The video runs in this order:
1. A typed intro, then a ring of 3D cards.
2. A glitchy title drop.
3. A spotlight for each work, playing its own sound with live level bars.
4. "Your story… next.", then a 3D rush of clips.
5. The liquid logo reveal, with chips and your website.

The score is synthesised, every cut sits on its beat, and the mix is set to −14 LUFS. Timings are measured from the narration automatically.
- **Docs:** [brand-promo/SKILL.md](brand-promo/SKILL.md) and [all config keys](brand-promo/references/config.md).
- **Example config:** [brand-promo/examples/kumnit-showreel.json](brand-promo/examples/kumnit-showreel.json).

### `/brand-loop`
- **The look:** two colour families of metaball blobs that merge and pinch off like mercury, on a warm off-white studio backdrop with ripple rings, soft shadows and shallow depth of field.
- **Render:** Blender EEVEE at 4K60.
- **Loop:** every motion is periodic, so the last frame flows into the first.
- **Colours:** they can come straight from a logo (`--logo logo.png`).
- **Docs:** [brand-loop/SKILL.md](brand-loop/SKILL.md).

## Run the scripts yourself (without Claude)

```bash
generate-logo/scripts/animate.sh logo.png --styles liquid,neon --size square
brand-promo/scripts/promo.sh my-promo/promo.json --preview     # 12 stills in ~30 s
brand-promo/scripts/promo.sh my-promo/promo.json               # the full video, ~10 min
brand-loop/scripts/loop.sh --name acme --logo logo.png --preview
brand-loop/scripts/loop.sh --name acme --logo logo.png --res 1920x1080
```

## Requirements

| Skill | Needs |
|---|---|
| all | macOS or Linux, [ffmpeg](https://ffmpeg.org) (libx264; libx265 for brand-loop), Node 22+, Google Chrome or Chromium (`CHROME_PATH` if it is elsewhere) |
| `/brand-promo` | Python with `numpy` and `scipy` (`PROMO_PY`). For narration, [VoxCPM2](https://github.com/OpenBMB/VoxCPM) (`pip install voxcpm soundfile`, `VOX_PY`). Without it, the promo is made without a narrator |
| `/brand-loop` | [Blender](https://www.blender.org) 4.2 or newer with EEVEE on a GPU (tested on 5.2, Apple Silicon) |

The Khmer fonts Kantumruy Pro and Koulen are included under the SIL Open Font License ([brand-promo/fonts](brand-promo/fonts)).
