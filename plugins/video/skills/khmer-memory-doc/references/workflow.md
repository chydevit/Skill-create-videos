# Workflow checklist (as used for *Democratic Kampuchea 1975–1979: We Remember*, 2026-10-25)

Timings on a 16 GB Mac: research about 60 min (4 subagents in parallel) · narration of about 85 lines about 75 min · new sets and shot list about 2 h (overlapping the voices) · ASR and reseed about 20 min · render about 40 min · web copy about 8 min.

## 0. Brief
- Topic, period, length (default 15:00), audience (students and families, including survivors and descendants).
- Chapter plan with start times, which go in `TARGETS`. The closing also counts: `CHAPTERS.append(len(SHOTS))` before the closing shots.
- Guides: an elder who lived through it and a grandchild who asks. Both are fictional composites.

## 1. Research (before writing anything)
1. `mkdir -p <project>/{docs,source/raw,research,archive/img}`, or run `new_memory_doc.py` first.
2. Launch 4 subagents in one message (prompts in `research.md`):
   - **provided sources**: open every link the user gave and save the text.
   - **fact check, first half of the chapters** and **fact check, second half plus the death toll**: at least two independent sources per claim.
   - **images**: free licences only, with permission-only items listed and not downloaded.
3. While they run, draft `docs/research_brief.md` from the finished files. Use `examples/democratic_kampuchea/docs/research_brief.md` as the model. Its sections:
   - STEP 1: a table of the provided sources plus their conflicts.
   - STEP 2: the sources used, with short codes (E313, DCC, LOC…), plus the sources that could not be opened.
   - STEP 3: a verified timeline per chapter (date | event | status | sources).
   - A table of the death toll or key numbers, with method and origin.
   - Disputed points, unverified items to exclude, and corrections to the user's brief.
   - STEP 4: images (key usable items, permission-required items, gaps, wrong captions caught).
   - An approach for approval: voices, victims' photos, wording of disputed numbers, framing of contested events.
4. Convert it to HTML (python `markdown` with tables, plus the contact sheet) and `open` it.
5. **Stop. Wait for approval.**

## 2. Narration
- The order is: the opening Q&A, then a narrator line stating that the guides are fictional, then the date range, then the title.
- Each chapter: the grandchild asks, the narrator answers in 4–7 short lines, and the elder gives one or two memory lines (a personal, non-graphic detail).
- Read a survivor's real words with credit, using `QUOTE` (an on-screen notebook page) plus a narrator line naming the person and the source.
- Present every death toll as a range with a method card (`NOTE`).
- Speech rate is about 0.069 s per Khmer character. The elder voice is slower.

## 3. Voices
- The template includes three voices: `nar` (male narrator, also used in the Khmer Republic film), `elder` (VoxCPM seed 23, f0 about 180 Hz) and `youth` (seed 78, f0 about 318 Hz).
- New voices: run `make.py voices` (8 seeds per unlocked speaker), then `.venv/bin/python build/cand_eval.py <who>` (ASR plus median f0). Choose the highest ASR score with a plausible pitch: an elderly woman at 170–200 Hz, a teenage girl at 280–340 Hz. Then `make.py lock <who> <seed>`.
- Test 4 lines in bf16 and ASR them before the full run.

## 4. Shots
See `look.md`. Most chapters run: a pencil chapter card, then a question, then evidence (album photos, maps, notebook pages) mixed with grey reconstructions and symbols, then a memory shot.

## 5. Preview loop
`make.py info` → `make.py shotstills` → look → fix → repeat. `make.py stills 300 612` renders single moments.

## 6. Finish
Run `pipeline.py`, detached, as described in SKILL.md. Check the output with ffprobe (duration and streams: h264, aac, 2× mov_text), then pull out 12 frames across the film and look at them.

## 7. Hand-off
Give the runtime, the paths to the film, web copy, srt files and docs, the ASR mean and low lines, and the lines with years to check by ear. Point out any departure from the brief, such as word count or runtime. Save a project memory.
