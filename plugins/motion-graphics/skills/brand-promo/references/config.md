# promo.json reference

All paths can be absolute or start with `~`. The project folder is the folder that holds `promo.json`; `assets/`, `build/` and `out/` are created next to it.

```jsonc
{
  "name": "kumnit-showreel",          // output prefix: out/<name>-1080p60.mp4
  "lang": "en",                        // "en" or "km" (Khmer fonts, Khmer-aware typing)
  "brand": {
    "name": ["KumNit", " Studio"],     // the wordmark in two colour parts (the second may be "")
    "colors": ["#1f6bff", "#2fb4ff", "#fe8a05", "#ffb21a"],   // part 1 gradient from/to, part 2 gradient from/to
    "accent": "#0a84ff",               // title box, glows, numbers, the big "next."
    "accent2": "#01d4f7",              // floor glow core, level bars, landing ring
    "warm": "#fe9a01",                 // glitch ghost, chip dot
    "font": "Arial Rounded MT Bold",   // optional: the wordmark font (must be installed)
    "logoAnimation": "~/logo/brand-5s-liquid-alpha.mov",      // alpha .mov / .webm, or a transparent PNG
    "logoSfx": "~/logo/brand-5s-liquid-sfx.wav",              // optional: found automatically next to the animation
    "url": "kumnitstudio.com"          // optional: shown under the chips
  },
  "text": {                            // every on-screen word; missing keys fall back to English defaults
    "typed": "Every story",            // typed inside { }
    "line": ["deserves to ", "move."], // muted + accent
    "ring": ["Here are five of ", "ours."],
    "eyebrow": "SHOWREEL",             // above the title box
    "subline": "Animation and AI video, made in Khmer",
    "soundOn": "Sound on", "fullVideo": "Full video · ",
    "next": ["Your story", "next."],   // the break: first word(s), then the big accent word
    "rush": ["Written", "Voiced", "Animated"],                // exactly three, the last in the accent colour
    "rushLine": "all by our own team",
    "chips": ["Folk tales", "Explainers", "Legends", "AI video"]   // up to 5, under the logo
  },
  "works": [                           // 3 to 5; each gets a spotlight in this order
    {
      "video": "~/work/folk-tale.mp4", // vertical videos play on a phone, landscape ones on a card
      "sound": 79.71,                  // optional: start (s) of the 4 s it plays; the picture starts 2 s earlier
      "mute": false,                   // optional: true = no sound for this work
      "label": "FOLK TALE · 9:16",     // eyebrow, numbered [01]...
      "title": "Folk tales",           // big title (1-3 words)
      "line": "for the phone in your hand.",
      "length": "5:53"                 // optional: the "Full video" chip (default: the video's length; "" hides it)
    }
  ],
  "voice": {                           // optional: leave out for no narration
    "design": "A warm, confident young woman ... natural American English, upbeat ...",   // VoxCPM2 voice design (English description, even for Khmer)
    "sample": "Every great story starts with a simple idea, ...",                          // a sample sentence in the narration language
    "ref": "~/voices/narrator.wav", "refText": "...",   // optional: clone this recording instead of designing a voice
    "seed": 4242,
    "lines": {
      "intro": "Every story deserves to move.",          // 0.5 s
      "ring": "Here are five of ours.",                  // 3.7 s
      "title": "This is Kumnit Studio.",                 // on the title drop (write brand names as they sound)
      "works": ["Folk tales, for your phone.", "..."],   // one per work, as its spotlight opens; keep them under ~2 s
      "next": "Your story could be next.",               // the big word lands on this line's LAST word
      "rush": "We write it, voice it, and animate every frame.",   // three phrases split by commas -> the three rush words
      "end": "Kumnit Studio. Let's make your story move."          // as the name appears
    }
  },
  "sfxDir": "~/Sound Effects/MIX"      // optional: your effects library (file names in scripts/audio.py SFX), else synthesised
}
```

## Files the pipeline writes
| Path | What |
|---|---|
| `assets/clips/p<k>/` | 6.4 s of each work at 30 fps (2 s before its sound + 4 s sound + 0.4 s) |
| `assets/clips/r<k>a`, `r<k>b` | two extra silent clips per work for the rush |
| `assets/bites/p<k>.wav`, `levels.json` | each work's 4 s sound bite and its 30 fps loudness (drives the level bars) |
| `assets/stills/` | three stills per work (the card ring) |
| `assets/logo/` | the logo animation as 1000x1000 frames, `mark.json` = the mark's size inside them |
| `build/vox/` | the narrator voice and lines |
| `build/tm.json` | the timings measured from the narration (sound bites, "next", rush words) |
| `build/music.wav`, `build/mix.wav`, `build/stem_*.wav` | score, final mix, stems (voice, source, music, fx) |
| `build/frames/` | the rendered PNG frames (safe to delete after encoding) |
| `out/` | the MP4, the contact sheet, the preview sheet |

To redo a work's clip after changing its `sound`, delete `assets/clips/p<k>`, `assets/bites/p<k>.wav` and `assets/manifest.json`.
