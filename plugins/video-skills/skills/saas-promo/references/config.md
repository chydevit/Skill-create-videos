# promo.json keys

Paths are relative to the folder that holds `promo.json`. Only `name` is really needed: everything else has a default. With no `cards`, every card is a built-in UI card.

```json
{
  "name": "acme-launch",
  "lang": "en",
  "cards": ["shots/*.png", {"file": "demo.mp4", "at": 12.5}],
  "logo": "logo.png",
  "hero": "hero.jpg",
  "backdrop": "field.jpg",
  "text": { "typed": "Acme.", "bento": ["Build", "Ask the AI", "a prototype"],
            "headline": "Ship Your Product Faster", "sub": "…", "from": "From a sketch", "to": "To a Launch Film",
            "glyphs": "#<@!?*", "labels": ["Ask anything…", "Approvals", "Dashboard"], "url": "acme.com" },
  "colors": { "neon": ["#b62bff", "#c8ff1f"], "orb": ["#16e0c4", "#c4f53b", "#a54dff", "#6b3cff"],
              "sky": ["#0d5fc8", "#3f8fe0", "#e9a96a", "#f2861e"], "symbols": ["#ff6a00", "#2f8bff"], "accent": "#4f7cff" },
  "music": "track.mp3", "musicLevel": 0, "sfxLevel": -4,
  "sfxDir": "~/Sounds/SFX",
  "chapters": [
    { "tag": "app", "typed": "Acme App.", "wall": "dark", "bento": ["Inbox", "Ask the assistant", "in one tap"],
      "headline": "Your Inbox, Sorted by AI", "sub": "…", "orb": ["#22d3ee", "#6366f1", "#a855f7"] }
  ]
}
```

A card can be `{"file": "shot.png", "tag": "app"}`: the chapter with that `tag` shows it first.

| Key | Default | What it does |
|---|---|---|
| `name` | `saas-promo` | output file names: `out/<name>-1080p60.mp4`, `-contact.png`, `-preview.png` |
| `lang` | `en` | `en` uses the system UI font (SF Pro on a Mac). `km` sets every text in Kantumruy Pro (bundled) |
| `cards` | none | images and videos, globs allowed, up to 40. `{"file", "at"}` takes the still of a video at `at` s (default 30 % in). The first cards closest to each slot's shape fill the bento wall. All of them, mixed with a few UI cards, make the 3D swirl. The big hero card takes the first landscape picture in the list. `{"file", "wall": false}` keeps a picture out of the wall (swirl only) |
| `logo` | none | shown under `text.to` at the end. An opaque image (no transparency) is drawn as a rounded app icon |
| `hero` | none | the finale picture instead of the code-drawn flower (cover-cropped, slow push in). Symbols, rain and texts still play over it |
| `backdrop` | none | the bento-wall background instead of the painted meadow |
| `text.typed` | `SaaS.` | scene 2: the word typed in with a cursor. Keep it to one word or name (it shrinks to fit 900 px) |
| `text.glyphs` | `#<@!?*` | scene 1: the big symbols flashed in the centre, one every 0.08 s |
| `text.bento` | `Build`, `Ask an AI agent`, `a prototype` | scene 3: typed on the hero card, vertically on the tall glass card, and on the white card the camera zooms into |
| `text.headline` | (generic) | scene 4: revealed word by word next to the orb. Split on spaces |
| `text.sub` | (generic) | scene 4: one line under the headline, wiped in left to right |
| `text.from` / `text.to` | (generic) | scene 5: "From …" blurs in and out, then "To …" lands on the boom |
| `text.url` | none | a website line under the last text (and under the logo), for example `acme.com`. It adds 0.45 s to the end so it can be read |
| `text.labels` | UI words | the texts on built-in UI cards (search placeholder, form title, chart label…) |
| `colors.neon` | purple, lime | scene 1 neon shapes and the glitch blocks |
| `colors.orb` | teal, lime, purple, violet | the conic gradient of the orb (any number of colours) |
| `colors.sky` | 4 colours | the finale sky from top to bottom |
| `colors.symbols` | orange, blue | the flying symbols (alternating) |
| `colors.accent` | `#4f7cff` | the typing cursors on cards |
| `music` | none | the user's own track instead of the synth bed. `assets.py` measures its tempo and drop, and the video starts so that the first cut lands on the drop. It fades out with the picture |
| `musicStart` | auto | the song second the video starts at (overrides the drop alignment) |
| `bpm` / `musicDrop` | auto | the song's tempo and drop (song seconds), when the measurement prints wrong values |
| `sfxLevel` | `0` | dB added to every sound effect (for example `-4` under a song) |
| `wall` | `meadow` | the look of the intro wall: `meadow`, `dusk` or `dark` |
| `chapters` | none | turns on the ~50 s long cut. Each chapter is `{tag, typed, bento, headline, sub, wall, orb, colors, labels}`. Without `typed` it has no swirl opener. Its beats are 1.5 bars each (bars from the song's tempo, or 2.2 s without music) |
| `musicLevel` | `0` | dB added to the bed or track (for example `-3` makes the effects stand out more) |
| `sfxDir` | none | a folder of sound files. The names in `audio.py` `SFX` are tried first, and missing ones are synthesised |
