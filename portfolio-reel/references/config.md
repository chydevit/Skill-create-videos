# promo.json keys

Paths are relative to the folder that holds `promo.json`. Everything except `name` has a default, but a reel needs at least an `avatar`, a few `sections` and the user's own texts.

```json
{
  "name": "alex-reel",
  "lang": "en",
  "avatar": {"file": "me.jpg", "crop": [420, 80, 900]},
  "avatarStyle": "photo",
  "logo": "logo.png",
  "text": {
    "hook": ["Looking for a", "Video editor?"],
    "badge": "Ideas, made visual",
    "hello": "Hello, I'm Alex",
    "roles": ["Video editor", "Motion designer", "Creative"],
    "button": "Here's my work",
    "cta": ["Let's turn that idea into visuals", "DM me, let's talk :)"]
  },
  "sections": [
    {"title": "Short Form Edits", "clips": [{"file": "reel1.mp4", "at": 3}, "reel2.mp4", "reel3.mp4"]},
    {"title": "Motion Graphics", "clips": ["logo-anim.mp4", "explainer.mp4"]},
    {"title": "Personal Work", "clips": ["short.mp4", "poster.jpg"]}
  ],
  "profile": {"handle": "@alex", "name": "Alex Doe", "stats": [["Posts", 41], ["Followers", 150], ["Following", 67]],
              "buttons": ["Follow", "Message"], "clicked": "Following", "back": "alex.studio"},
  "colors": {"bg": ["#f3e83d", "#d4c81f", "#4b4607"], "title": ["#8b8611", "#bdb423"], "button": "#4c46f0"},
  "music": "track.mp3", "musicStart": 0, "musicLevel": 0, "sfxLevel": 0,
  "sfxDir": "~/Sounds/SFX"
}
```

| Key | Default | What it does |
|---|---|---|
| `name` | `portfolio-reel` | output file names: `out/<name>-1080p60.mp4`, `-contact.png`, `-preview.png` |
| `lang` | `en` | `en` uses the system UI font (SF Pro on a Mac). `km` sets every text in Kantumruy Pro (bundled) |
| `avatar` | none (a plain yellow disc) | a photo or a video still (`{"file", "at"}`), cropped square by `crop: [x, y, size]` px, or else the centre square, a bit above the middle |
| `avatarStyle` | `photo` | `photo`: the picture in a thin yellow ring. `duotone`: a grey multiply over the yellow disc (best for light backgrounds) |
| `logo` | the avatar | the picture inside the profile card's white circle |
| `text.hook` | `["Looking for a", "Video editor?"]` | the small line (word by word), then the big question |
| `text.badge` | `Ideas, made visual` | the outlined pill with a star above the greeting |
| `text.hello` | `Hello, I'm Alex` | the big greeting, word by word |
| `text.roles` | 3 roles | short roles, split by thin vertical bars |
| `text.button` | `Here's my work` | the black pill's label |
| `text.cta` | two lines | the closing lines on yellow. The second is optional |
| `sections` | none | 1-4 `{title, clips}`. `clips` holds 1-3 images or videos, `{"file", "at", "seconds"}` (5.5 s from 25 % in by default) |
| `profile.handle` / `name` | placeholders | the card's handle (big) and name |
| `profile.stats` | 3 pairs | up to 3 `[label, value]`. Numbers count up from 0, strings appear as they are. Use real numbers only |
| `profile.buttons` / `clicked` | `Follow`, `Message` / `Following` | the two buttons and the first one's label after the click |
| `profile.back` | the handle | the text on the back of the card after the flip |
| `colors.bg` | mustard yellow, 3 stops | the gradient: centre, middle, edge |
| `colors.title` | olive | the section titles' gradient: bottom, top |
| `colors.button` | `#4c46f0` | the card's buttons |
| `music` | none | the user's own track instead of the synthesised lo-fi beat, from `musicStart` s |
| `musicLevel` / `sfxLevel` | `0` | dB added to the music or to every sound effect |
| `sfxDir` | none | a folder of sound files. The names in `audio.py` `SFX` are tried first, and missing ones are synthesised |
