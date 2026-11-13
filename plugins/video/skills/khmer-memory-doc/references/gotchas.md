# Gotchas

## Voices
- **VoxCPM2 on a 16 GB Mac**: always set `VOXCPM_MPS_DTYPE=bfloat16`; float32 thrashes swap. Detach long jobs with `nohup`, because background jobs die when the Claude session restarts. Run only one synthesis worker at a time.
- **Long lines with several years** come out garbled. The Sihanouk line "returned in September 1975 … resigned April 1976 … until January 1979" scored 0.39 twice; split into two lines it scored 0.92 and 0.85. Keep each year in a short line of its own.
- **Whisper mishears spoken years.** It often writes "1979" as "1999". A line can score 0.85 with the year still "wrong" in the transcript. Have a native speaker check year lines by ear.
- **Short questions score low** (a missed word drops the score a lot). Try a seed such as 37 by hand: edit `audio/seeds.json`, then run `make.py narrate`.
- **Proper names** such as Kaing Guek Eav (Duch) score around 0.75 even when they are spoken correctly.
- **Clip names**: clips are keyed by a hash of the spoken text, the seed and the speaker. Editing a line re-synthesises only that line; reordering shots re-synthesises nothing.

## Pipeline and render
- **ASR cache**: the template `pipeline.py` caches scores per clip in `build/asr_scores.jsonl`, so a restart reuses them. The original DK pipeline did not, and wasted 15 minutes re-scoring.
- **Stop and restart cleanly**: run `pkill -f pipeline.py; pkill -f "make.py all"`, then `rm -rf build/chunks`, because any change in timing makes every later chunk wrong.
- **Never add `-shortest`** to the mux: it cuts the credits when subtitle tracks are present.
- **Render speed**: about 0.8 s per frame per process. Five workers render 15 minutes in about 37 minutes.

## Drawing
- **Lip-sync**: `GUIDE` passes `pre` to `mouth_for`, so a guide shot with a long `pre` (for example a candle lit before Malis speaks) stays in sync.
- **Layered sets** are inked before their `over()`. Archive frames (`ink=None`) are never inked, so photos stay unaltered.
- **Cutting out images**: draw a clipped image (the portrait in the altar) with `ctx.save(); ctx.rectangle(...); ctx.clip()`. Do not hide it with a painted patch.
- **Pencil hatching** starts only at darkness above about 0.32, so light skies stay as clean paper. Raising it covers the whole frame with a mechanical screen.
- **Map lines** have no arrowheads: use dashed `line` elements with `draw=` progress.
- **Albums**: `AP` stops the build if the image file is missing. Check `archive/img` first.

## Credits
- Fix ugly attribution lines in the manifest (for example a Commons uploader's note) before rendering. The credits read `attribution_line`.
