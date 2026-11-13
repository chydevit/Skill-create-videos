# Dialogue and voices (VoxCPM2, Khmer or English)

## lines.json
```json
{
  "lang": "km", "translation": "en",
  "voices": {
    "benny":   { "seed": 2101, "design": "A nervous, jittery Cambodian man in his thirties, ... speaks fast and anxiously",
                 "sample": "ខ្ញុំ... ខ្ញុំខ្លាចណាស់បង។ ប៉ូលិសមកហើយ! យើងត្រូវរត់ឥឡូវនេះ!", "gain": 0.95, "pan": 0 },
    "speaker": { "seed": 2303, "design": "A bored young Cambodian fast-food worker talking through a drive-thru intercom...",
                 "sample": "...", "fx": "intercom", "gain": 0.75, "pan": 0.35 }
  },
  "lines": { "v_benny_yelp": ["benny", "ម៉ែអើយ!", "Oh, mother!"] },
  "seeds": { "v_benny_yelp": 11 }
}
```
- `lang` is the spoken language (subtitle track 1); `translation` is the second subtitle track (third field of each line).
- `fx`: `intercom` (drive-thru speaker), `radio`, `phone`. `gain`/`pan` per voice. One line can take an effect too:
  top-level `"fx": {"<line id>": "thought"}` (inner voice with a soft echo, for a thought bubble) or `"phone"`.
- `seeds.<line>` re-rolls a single line that came out garbled.
- Optional 4th field = the text actually spoken, when it must differ from the subtitle: `["smei", "ខ្ញុំជាគ្រូណែនាំ (Mentor)។",
  "I'm the mentor.", "ខ្ញុំជាគ្រូណែនាំ Mentor។"]`. VoxCPM treats `(...)` as a voice instruction, so remove brackets
  from spoken text. Also use it for respellings.
- A narrator is just another voice (`"narrator": {design, sample, seed}`) whose lines move no mouth.
- English film: `"lang": "en"`, write English lines, drop `translation` (or translate to `km`). VoxCPM2 speaks English
  too. For quick drafts without VoxCPM a voice may carry `"say": {"voice": "Samantha", "rate": 175, "pitch": 0.93}`
  (macOS TTS, English only, robotic); it is used only when the VoxCPM clip is missing.

## Making the clips
`npm run voices` → `voices/run.sh`: writes `build/vox/jobs.json`, then runs the VoxCPM2 worker (`voices/tts_vox.py`) with
the first Python found among `$VOX_PY`, the khmer-2d-animation skill's `.venv-vox`, and `~/voxcpm-env`. If none
exists, install it once: `python3.12 -m venv ~/voxcpm-env && ~/voxcpm-env/bin/pip install voxcpm soundfile`
(the ~5 GB model downloads on first use). The worker:
1. **Locks one voice per character**: designs `voices/<who>.wav` from `(design)sample` once.
2. **Clones every line** from that clip into `build/vox/<id>.wav` so a character never changes voice.
Existing files are skipped. Delete a line's wav to regenerate it; delete `voices/<who>.wav` **and** that character's
lines to redesign a voice (only when the user asks: voices are part of the character).

Timing on Apple Silicon: model load 1–2.5 min, voice design 30–100 s, each line 10–60 s. **Run in the background**
(`run_in_background`) and tell the user the ETA; it is the slowest step of the whole build.
On a 16 GB Mac the model needs ~12 GB: with other heavy apps open it spills into swap and lines slow to 2–7 min
each (79 lines took about 2.5 h). Re-estimate the ETA from the clip timestamps in `build/vox/` when asked, name the
apps eating CPU or memory (`ps -Ao pcpu,comm -r | head`), and suggest closing them. If memory runs critically low the
job can be killed; rerunning `npm run voices` resumes, since finished clips are skipped.

## Writing Khmer dialogue
- Natural spoken Khmer, short punchy lines (cartoon timing): `បើកទៅ។` beats a full sentence. Interjections work well:
  `ម៉ែអើយ!`, `អូយម៉ែ!`, `អឺ... អឺ...`, `ហ៊ូរ៉េ!`, `យេ៎!`.
- Names and loanwords in Khmer script (បេននី, ប៊ឺហ្គឺបាន); numbers as words. Register: friends/crew use ឯង/ខ្ញុំ, bong (បង) to
  strangers; elders, monks and royalty need the proper forms (see khmer-2d-animation's guidance).
- On-screen lettering that echoes a line should be Khmer too (`fx.sfxText('បើកទៅចុះ!', ...)`: Koulen is automatic).
  Pure sound words (BAM!, CRASH!) can stay as English onomatopoeia unless the user wants Khmer.
- Always tell the user the Khmer needs a native speaker's check and that VoxCPM can mispronounce words.

## Fitting lines to the picture
VoxCPM leaves long pauses at `!`/`។`/`...`; the mixer automatically shrinks pauses >0.22 s to 0.15 s and drops a stray
breath after the last word. Khmer lines usually run **longer than English**. After `npm run audio`, read the printed
timeline: if a line overlaps the next one or runs past its gag, move the next cue later, speed the exchange, or lengthen
the shot with `setShift()` and trim time elsewhere (see craft.md). Match mouth/reaction timing in the shot (e.g. a
speaker's talk light on for the line's real length).

## Checking clips without ears: Khmer Whisper
`npm run asr` transcribes every clip with `seanghay/whisper-small-khmer-v2` (the khmer-history-doc / VoxCPM venv) and
scores it against the script (character similarity, ignoring spaces, punctuation and Latin letters). Scores of
0.9–1.0 are clean. English tech words inside Khmer lines (Server, load balancer) drop to ~0.75–0.85 because
Whisper spells them in Khmer; that's expected. A Khmer-only line under ~0.85 deserves a re-roll, and so does any line where Whisper hears a name or the
punchline wrong (Episode 7's last line, «ស្ដេចញ៉ែ», came back as "snack ញ៉ាយ" and scored 0.80). Whisper writes
spoken numbers as digits (ដប់ប្រាំបួន → ១៩), so a correct line with numbers can score ~0.4–0.7: read the words,
not just the score. Re-roll every flagged line in one go (one model load):
1. Save the current takes: `cp build/vox/<id>.wav build/vox_keep/<id>.s7.wav` (7 is the default seed).
2. Set `"seeds": {"<id>": 21, ...}` in lines.json and delete `build/vox/<id>.wav`.
3. Run `npm run voices`, then save the new takes as `build/vox_keep/<id>.s21.wav`.
4. `npm run asr -- <id> <id> ...` scores every saved take side by side.
5. Keep the better take: copy it to `build/vox/<id>.wav`. If the old take wins, remove its seed from lines.json
   so the file matches the clip, then run `npm run durations`.

Expect about half the re-rolls to win. If both takes score the same, the word is probably hard for Whisper
rather than mispronounced; keep it and mention it in the report.

The model downloads on first use if it isn't cached.
