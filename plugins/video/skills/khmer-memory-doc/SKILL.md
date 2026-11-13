---
name: khmer-memory-doc
description: Khmer "memory drawing" documentary builder for remembrance, survivor and testimony history films, such as the Khmer Rouge / Democratic Kampuchea years, a genocide, a war, a famine, a forced evacuation or other painful history told to students and families. It turns a topic into a finished, narrated 15-minute 2D documentary MP4 in soft pencil and charcoal on aged paper. Memories are drawn in grey; the present day is warm colour (incense smoke, lotus, morning light); colour slowly returns at the end. An elderly survivor tells her grandchild what she lived through at a memorial. Both are fictional composites and are labelled as such. It runs live research first and stops for the user's approval of a research brief, verifying every fact with two independent sources and showing disputed numbers as ranges. It uses symbolic imagery instead of violence (empty shoes, broken spectacles, silent classrooms, a closed temple gate, a candle), and authentic photos as old prints in a family album with checked licences. Victims' photos are used only with permission. It produces Khmer narration in locked VoxCPM2 voices (narrator, elder, grandchild) with Khmer Whisper QC, burned English plus soft Khmer/English subtitles, a sparse score (tro, khim, monastery bell; near-silence for the hardest chapter), and a full script, storyboard, image list and references. Use it whenever the user wants a respectful remembrance documentary, a survivor-and-grandchild framed history, a "we remember" film, a film about the Khmer Rouge, Pol Pot, S-21/Tuol Sleng, the killing fields, the 1975 evacuation or the ECCC trials, or "a doc like the Democratic Kampuchea one", even if they don't name the skill. For paper-cut kingdom and heritage docs use khmer-history-doc; for chibi cartoons use khmer-2d-animation.
---

# Khmer Memory-Drawing Documentary

This skill makes 12–18-minute educational documentaries in Khmer with English subtitles, in a pencil-and-charcoal "memory drawing" style. They are built for subjects where survivors and their descendants will watch.

The worked example is the 15:18 film *Democratic Kampuchea 1975–1979: We Remember* in `examples/democratic_kampuchea/`. It includes the narration, the shot list, the research brief, the fact-check files, the image manifest with licensed images, the storyboard and the script docs.

**Three rules above all:**
1. **Accuracy beats drama.** Every narrated fact needs at least two independent sources. Disputed numbers are given as ranges, and the film explains where each comes from. Anything with only one source stays out of the narration.
2. **Dignity beats impact.** Never depict violence. Use symbols and absence instead. Never animate, colour, crop or alter photographs of victims, and use them only with the holding institution's permission (see `references/sensitivity.md`).
3. **Fiction is labelled.** The elder and the grandchild are fictional composites, and the screen says so. They speak only of experiences the sources describe as common. Legal findings, dates and numbers come from the narrator, never from a fictional witness.

## Layout

```
khmer-memory-doc/
  engine/        film engine (copied into every project; patch it freely there)
                 memory.py  pencil/charcoal look, album photos, memorial frames, pencil chapter cards, smoke transition
                 sets75.py  memorial at dawn, altar + candle, exodus road, still lifes, classroom, fields/dam, dining hall
                 cast.py    elder (sophal_old), grandchild (malis), 1975 family, cadres and workers in black, East Zone blue scarf
  template/      narration.py, script_src.py (sample), make.py, pipeline.py, project.json, build/, locked voices
  examples/democratic_kampuchea/   the full film source, docs, research and licensed archive images
  scripts/new_memory_doc.py        create a project
  references/    workflow.md · research.md · look.md · sensitivity.md · gotchas.md
```

**Environments** come from the **khmer-history-doc** skill. If `~/.claude/skills/khmer-history-doc/.venv` is missing, run its `scripts/setup.sh` once. That provides the render venv (`.venv`), VoxCPM2 and Khmer Whisper (`.venv-vox`), fonts and the map fetcher.

## Workflow (details in references/workflow.md)

1. **Research first, then stop.** Create the project, then run research subagents in parallel: provided sources, a fact check for each half of the chapters, and images and licences. The prompts are in `references/research.md`.
   - Write `docs/research_brief.md`: provided-source summaries, the extra sources, a verified timeline per chapter with status marks (✓✓ / ✓ (1) / ⚖ / ✗), disputed points, exclusions, corrections to the user's brief, the image list, and an "approach for your approval" section with concrete questions.
   - Make an HTML copy (`docs/research_brief.html`) and open it for the user.
   - **Stop and wait for approval.** If the user replies with a short or unclear message, ask one direct yes/no question ("Start the film now with my recommendations?") rather than repeating the questions.
2. **Create the project:**
   `~/.claude/skills/khmer-history-doc/.venv/bin/python ~/.claude/skills/khmer-memory-doc/scripts/new_memory_doc.py ~/animation-2D/<slug> --title-en "…" --title-km "…"`
   Add `--example democratic_kampuchea` to start from the full film. The research files go in `research/`, `source/`, `archive/`.
3. **Narration first** (voices are the slowest step). In `narration.py`, use `L(key, km, en, src=…)` for the narrator, `E(...)` for the elder and `Yo(...)` for the grandchild.
   - About 85 lines and 1,400–1,700 English words make 15 minutes at a calm pace.
   - Use short Khmer clauses separated by spaces, Khmer digits, and one idea per line. Put each year in its own short line.
   - Rename the guides through `VOICES[...]["label_*"]`.
   - The locked voices `nar`, `elder` and `youth` are included. To design new ones, run `make.py voices`, score the candidates with `build/cand_eval.py`, then `make.py lock`.
   - Start synthesis detached: `VOXCPM_MPS_DTYPE=bfloat16 nohup .venv/bin/python make.py narrate > build/narrate.log 2>&1 &`
4. **Shot list (`script_src.py`).** While the voices run, write the shot list. Replace only the SHOTS section.
   - Use the helpers `S`, `AP`, `MF`, `M`, `CH`, `NOTE`, `QUOTE`, `MEMO`, `Q`, `A` and `GUIDE` (see `references/look.md`).
   - Set the chapter start times from the brief in `TARGETS`, and the credits start in `end_target` (project.json).
   - Mark present-day shots `era="present"`.
5. **Preview.** Run `make.py info`, then `WORKERS=3 make.py shotstills`, and look at every `build/shots/sheet_*.jpg`. Fix layout, badges and camera moves before rendering.
6. **Finish unattended** once every line exists:
   `VOXCPM_MPS_DTYPE=bfloat16 WORKERS=5 nohup caffeinate -i .venv/bin/python pipeline.py > build/pipeline.log 2>&1 &`
   This runs ASR on every line, reseeds weak lines once (keeping the better take), mixes the audio, renders, makes the web copy and the docs, and backs everything up to `~/Movies/khmer_history_docs`. Watch it with Monitor.
   - If a long line still scores under about 0.6, stop the job, split the line in `narration.py`, re-narrate and restart.
   - A 15-minute render takes about 40 minutes on 5 workers.
7. **Cover.** Edit the title lines in `build/cover.py`, then run `.venv/bin/python build/cover.py`. It writes `film/cover_<name>.png`, `.jpg` and a 1280×720 jpg, with the present-day guides dissolving into a grey memory scene and the title on an aged notebook page. Copy them to `~/Movies/khmer_history_docs/covers/`.
8. **Report.** Give the runtime, the file paths, the ASR mean and the low lines. Say clearly that a native Khmer speaker should listen, especially to lines with years, and that a historian should review the Khmer text.

## Credits

Credits list sources, scholarship, survivor testimony and every archival image with its licence. **Never add a "VOICES / VoxCPM2" credit.**
