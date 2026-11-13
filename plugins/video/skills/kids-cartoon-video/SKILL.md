---
name: kids-cartoon-video
description: Make a finished 3D animated kids' learning cartoon (MP4 + subtitles) starring Milo, Luna and Bobo the blue bird. Renders it locally with Blender and text-to-speech. Supports English, bilingual English-with-Khmer-help, and full Khmer (ភាសាខ្មែរ). Use this skill whenever the user asks for a kids' cartoon or educational video episode for young children (vocabulary, colors, numbers, animals, greetings, feelings, ABCs and so on). Also use it for a Khmer or Cambodian version of such a video, for "another Milo & Luna episode", or for turning a cartoon script or storyboard into an actual rendered video, even if they don't say "Blender" or "skill".
---

# Kids cartoon video (English / Bilingual / Khmer)

This skill turns an episode idea into a rendered 1080p cartoon. The same code draws Milo, Luna and Bobo in every scene, so they always look identical. You write one Python file, `script_data.py`, which holds the episode's lines, pauses and events. The pipeline then:

1. voices every line: macOS `say` for English, edge-tts neural voices for Khmer
2. times the episode from the real audio length
3. animates everything in Blender: lip movement follows each speaker's voice loudness, plus walking, gestures and on-screen cards
4. mixes generated music and sound effects
5. joins the scenes with cartoon transitions

## Choose the language mode

Ask which mode the user wants if it isn't clear. It changes the whole script.

| Mode | Who it's for | What changes |
|---|---|---|
| `english` | Kids learning English | Everything is in English (see `assets/example_english.py`) |
| `bilingual` | Khmer-speaking kids learning English | Characters speak English. The narrator explains in Khmer with `K(...)` lines. Cards show `"RED\nក្រហម"` (see `assets/example_bilingual.py`) |
| `khmer` | Kids learning or watching in Khmer | Every line, card, caption and badge is in Khmer (see `assets/example_khmer.py`) |

For Khmer text, read `references/khmer.md` first. It has a checked glossary, the tone and politeness conventions for children's content, and the voice setup. Khmer translations should be reviewed by a native speaker before anything is published. Tell the user this; don't claim the Khmer is perfect.

## Workflow

The skill lives at `~/.claude/skills/kids-cartoon-video`. The scripts are in `scripts/`. The project folder (`P`) is wherever the user wants the episode.

1. **Setup (once):** `~/.claude/skills/kids-cartoon-video/scripts/setup.sh`. It checks Blender, ffmpeg, the Khmer font, edge-tts (needs internet) and the Swift text renderer. Fix anything it reports as missing before continuing.
2. **Write the script.**
   - Create `P/script_data.py`. Start from the example that matches the mode.
   - Read `references/script-format.md` for the helpers (`L`, `K`, `P`, `A`), the event types, and the 10 reusable **sets**, with their camera shots, props and where the kids start.
   - Plan roughly 10 scenes. Give each one a `"set"` and a `"target"` length in seconds.
   - Reuse existing sets; each one fits many topics. Only write a new set class in `bl_scenes.py` when no set fits.
3. **Build the audio:** `scripts/build_audio.sh P`. It prints each scene's length against its target and the total length.
   - If the total is short, add content: "say it with me" repeats (`say_it`), `P()` pauses after questions, extra quiz questions.
   - Don't slow the voices further.
   - Kids need a 2–4 s pause after every question. That's what the "your turn" badge is for.
4. **Check stills before rendering.** A full render takes hours; stills take seconds.
   - Run `scripts/stills.sh P <scene> <t1> <t2> …` for 3–4 moments per scene: card moments, pauses, the start of walks.
   - View the PNGs in `P/build/tests/`, and combine them into a grid with ffmpeg `xstack` to save looking at each one.
   - Look for: cards covering faces, characters off-screen, Bobo hidden behind a card, text cut off, and Khmer rendered as boxes (which means the renderer failed).
   - Fix, rebuild the audio if the script changed, and re-check.
5. **Render:** `scripts/render_all.sh P`. Run it in the background.
   - It renders two queues in parallel, resumes if interrupted, and uses `caffeinate` so the Mac doesn't idle-sleep. (Idle sleep once made each frame take 15 minutes instead of 1–2 seconds.)
   - Expect about 1–2 s per frame per queue on an M1 Pro. A 9-minute episode is about 13,000 frames, or 2–4 hours.
   - Watch `P/build/logs/queue*.log` with a Monitor for `done scene|ERROR|Traceback`.
6. **Assemble:** `scripts/assemble.sh P`. It writes `P/<Title>[_bilingual|_khmer].mp4` (loudness-normalised to –16 LUFS) and a matching `.srt`.
   - If the user wants to watch before everything is done, build a preview from the finished `build/segments/segNN.mp4` files with the same xfade chain and a trimmed audio track.

Run the scripts directly. Don't re-implement them. Blender's own Python (found by `build_audio.sh`) provides numpy.

## Writing good episodes for 4–8 year olds

These choices worked in the first episode:
- Keep sentences short and repeat new words 3+ times: character says it, narrator repeats it, the child repeats it.
- Put a card on screen the moment a new word is spoken (`card=("RED", RED)`). In bilingual mode, add the Khmer meaning underneath.
- Every question to the viewer gets `P(2.5–4)`.
- Give Bobo the funny mistakes (counting too fast, falling into a flower). It keeps kids watching, and Luna gently corrects him.
- End scenes with praise: `("sfx","sparkle")` plus `("prop","fx","stars")`.
- Move the camera gently, cutting between named shots with 1–2.5 s moves. No fast motion.
- Only scripted `"all"` or `"ml"` lines should be spoken together; everything else is one speaker at a time.
- Target about 60–75 s per scene and about 9.5–10.5 min in total, unless the user asks otherwise.
- Keep everything child-safe: no scary, violent or unsafe content.

## Limitations to tell the user about

- The voices are text-to-speech. Khmer uses Microsoft neural voices through edge-tts, which needs internet. To swap in human voice actors, replace the files in `P/build/vo/` (keep the lengths similar) and re-run `build_audio.sh`, which picks up cached files.
- Lip sync follows the voice loudness, not exact mouth shapes.
- The look is a clean, rounded 3D toy style, not studio-quality animation.

## Files

- `scripts/`: the pipeline (`audio_build.py`, `bl_*.py`, `assemble.py`, `make_srt.py`), the shell wrappers, and `render_text` (CoreText renderer for Khmer).
- `assets/example_*.py`: complete example scripts for each mode.
- `references/script-format.md`: the helpers, the events and the set catalogue. Read it before writing a script.
- `references/khmer.md`: the Khmer glossary, voices, fonts and bilingual patterns.
- `references/troubleshooting.md`: known problems and fixes.
