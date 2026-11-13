# The brief this example was built from

> STORY: Office series Episode 7 «គីមឡុង ស្ដេចញ៉ែ» / "Kimlong, the King of Flirting" (Khmer, asked for ~2 min,
> 15 scenes, Getaway Car look). While David prepares to defend his thesis, Bong Smei's office gets a new member,
> Kimlong (19), the same age as Sopheak, so the two call each other by name and become friends at once. Kimlong is a
> loud, funny videographer and a great gamer who flirts with every girl using sweet lines, and nobody believes
> him. But he has a good heart, and he uses his camera to help "Bong David" rehearse his thesis defence.
>
> NEW CHARACTERS: **Kimlong** (19, chubby, round face, gelled spiky hair, black tee under an open red flannel,
> jeans, camera round his neck). **Channy** (22, Leanghak's company, long straight hair, white blouse, grey pencil
> skirt, red lanyard, calm). **Sreyneang** (21, waitress next door, high bun, dark blue apron, witty). The rest of
> the series cast returns: Smey, Nimith, David, Sopheak, Leanghak, Pisey.
>
> Part 1 (scenes 1–5): Kimlong arrives, flirts with Channy in the hallway, bursts into the office, over-strong
> handshakes, a same-age fist bump with Sopheak, non-stop questions about the girl next door, films the office.
> Part 2 (scenes 6–9): flirts with the waitress at lunch (an ear pinch from Leanghak, a finger wag from Pisey),
> wins every game with Sopheak as the new duo, Channy brings documents and ignores him.
> Part 3 (scenes 10–15): David rehearses alone; Kimlong turns serious, sets up a tripod and a mock panel, films the
> rehearsal and reviews it on a laptop; in the golden hallway Channy smiles at him for the first time; the
> timer group photo.
>
> EDIT NOTES: the title «វគ្គទី ៧៖ គីមឡុង ស្ដេចញ៉ែ»; each flirt (scenes 1, 6, 9) gets a sweet love sting and ✨💕
> round his face, then «ប្លុក!» or a fail sound; name cards for Channy (scene 1), Kimlong (scene 2) and Sreyneang
> (scene 6); «ប៉ុក!» and «🤜🤛 អាយុដូចគ្នា = មិត្តភ្លាម!» on the fist bump; «👑 គូហ្គេមថ្មី៖ សុភ័ក្រ & គីមឡុង!»;
> «ឈ្នះហ្គេម ១០០% 🏆 | ឈ្នះស្នេហា ០% 💔»; scenes 12–13 seen through the camera (REC ●); slow motion with falling 🌻
> when Channy smiles; a freeze-frame photo with «ឆឹក!» on Kimlong's wink; the end line
> «ម្នាក់ៗខុសគ្នា តែរួមគ្នាយើងខ្លាំង!» and «វគ្គក្រោយ៖ ថ្ងៃការពារសារណារបស់ដេវីត...»; Khmer subtitles; 1080p.
> Every dialogue line is in `voices/lines.json` (Khmer + English).

**How it went:**
- The 79 Khmer lines run 3:44, not 2 minutes. The timeline follows the voices, so the length comes from the script;
  tell the user early and offer to cut lines if the length matters.
- Emoji don't render in Koulen, so ✨💕👑🏆💔🌻📷 are drawn icons (`ICON` in `ep6.mjs`, effects in `ep7.mjs`).
- Khmer Whisper flagged 9 lines (names, «អបអរសាទរ», and the punchline «ស្ដេចញ៉ែ» heard as "snack"). Seed 21
  re-rolls won 5 of 9 (`seeds` in lines.json); the other 4 kept their first take.
- Numbers and English words were respelled in the spoken 4th field (Office → អូហ្វីស, ១៩ → ដប់ប្រាំបួន,
  ៣..២..១ → បី... ពីរ... មួយ), and emoji and "!!!" were removed from what VoxCPM reads.

# How it was staged (3:44, 32 shots); see src/shots.mjs and src/ep/

Runtime 3:44.0 (224.0 s), 32 shots, 15 brief scenes, 1920×1080 @ 24 fps. Times are from the real voice clips.

| # | scene | start – end | len | what happens | dialogue | cues |
|---|---|---|---|---|---|---|
| 1 | 1 | 0:00.0 – 0:09.9 | 9.9 | the hallway: a new face, and a girl with a folder | n1a (narrator), n1b (narrator) | room_tone, sting_title, music, footsteps, creak |
| 2 | 1 | 0:09.9 – 0:24.7 | 14.8 | the hallway: a new face, and a girl with a folder | g1a (kimlong), g1b (kimlong), c1a (channy), g1c (kimlong), c1b (channy) | zip_up, sparkle, music, footsteps, record_scratch, pop, slide_down_short, sad_trombone |
| 3 | 2 | 0:24.7 – 0:34.9 | 10.2 | the door bursts open: "HELLO!!!" | g2a (kimlong), g2b (kimlong), m2 (nimith), s2 (smey) | room_tone, door_bam, boing, music, pop, applause |
| 4 | 3 | 0:34.9 – 0:42.1 | 7.3 | sampeah, then handshakes that are far too strong; a same-age fist bump | g3a (kimlong), g3b (kimlong), d3 (david) | squeak_rubber, lid_wobble |
| 5 | 3 | 0:42.1 – 0:52.6 | 10.5 | sampeah, then handshakes that are far too strong; a same-age fist bump | g3c (kimlong), k3a (sopheak), g3d (kimlong), k3b (sopheak) | zip_up, boing, highfive, bonk, ta_da_small |
| 6 | 4 | 0:52.6 – 0:58.9 | 6.2 | non-stop questions about the girl next door; two facepalms | g4a (kimlong), g4b (kimlong), g4c (kimlong) | music, whoosh, pop |
| 7 | 4 | 0:58.9 – 1:01.6 | 2.7 | non-stop questions about the girl next door; two facepalms | s4 (smey) | facepalm_slap |
| 8 | 4 | 1:01.6 – 1:05.1 | 3.5 | non-stop questions about the girl next door; two facepalms | d4 (david) | slide_down_short, register_ding, sparkle |
| 9 | 5 | 1:05.1 – 1:10.5 | 5.4 | the desk next door, and the 30-second office film | k5a (sopheak), k5b (sopheak), g5a (kimlong) | music, room_tone, pop |
| 10 | 5 | 1:10.5 – 1:13.3 | 2.8 | the desk next door, and the 30-second office film |  | ping, whoosh, shutter |
| 11 | 5 | 1:13.3 – 1:21.1 | 7.8 | the desk next door, and the 30-second office film | g5b (kimlong), m5 (nimith) | sparkle, applause |
| 12 | 6 | 1:21.1 – 1:24.1 | 3.0 | "Just looking at your face fills me up!" | g6a (kimlong) | city_amb, music, footsteps, pop |
| 13 | 6 | 1:24.1 – 1:36.3 | 12.2 | "Just looking at your face fills me up!" | g6b (kimlong), y6a (sreyneang), y6b (sreyneang), g6c (kimlong) | music, record_scratch, bonk, pop, footsteps, sting_panic |
| 14 | 6 | 1:36.3 – 1:39.2 | 2.9 | "Just looking at your face fills me up!" | k6 (sopheak) | applause, heh |
| 15 | 7 | 1:39.2 – 1:51.1 | 11.9 | an ear pinch and a finger wag | l7 (leanghak), p7 (pisey), g7a (kimlong), g7b (kimlong) | squeak_rubber, heh, applause, city_amb |
| 16 | 8 | 1:51.1 – 1:56.8 | 5.7 | the new duo: «👑 គូហ្គេមថ្មី៖ សុភ័ក្រ & គីមឡុង!» | g8a (kimlong), k8 (sopheak) | music, title_whoosh, ta_da_small |
| 17 | 8 | 1:56.8 – 1:59.4 | 2.7 | the new duo: «👑 គូហ្គេមថ្មី៖ សុភ័ក្រ & គីមឡុង!» | g8b (kimlong) | zap, ta_da, party_pop |
| 18 | 8 | 1:59.4 – 2:02.3 | 2.8 | the new duo: «👑 គូហ្គេមថ្មី៖ សុភ័ក្រ & គីមឡុង!» | l8a (leanghak), l8b (leanghak) | sting_shock |
| 19 | 8 | 2:02.3 – 2:05.1 | 2.8 | the new duo: «👑 គូហ្គេមថ្មី៖ សុភ័ក្រ & គីមឡុង!» | d8 (david) | highfive, applause |
| 20 | 9 | 2:05.1 – 2:20.8 | 15.6 | Channy brings documents; «ឈ្នះហ្គេម ១០០% 🏆 / ឈ្នះស្នេហា ០% 💔» | c9 (channy), g9a (kimlong), g9b (kimlong), k9 (sopheak), m9 (nimith) | knock, creak, clunk, zip_up, music, door_bam, pop, flop, sad_trombone, heh |
| 21 | 10 | 2:20.8 – 2:26.8 | 6.0 | David rehearses alone, whispering; Kimlong's face changes | d10a (david), d10b (david) | music, room_tone, page_flip |
| 22 | 10 | 2:26.8 – 2:31.8 | 5.0 | David rehearses alone, whispering; Kimlong's face changes | g10 (kimlong) | clunk, sting_tiny |
| 23 | 11 | 2:31.8 – 2:42.6 | 10.8 | tripod, chairs in a row, "you three are the professors!" | g11a (kimlong), g11b (kimlong), s11 (smey) | music, whoosh_by, roll_stop, pop, clunk, creak, footsteps |
| 24 | 12 | 2:42.6 – 2:47.1 | 4.4 | the rehearsal: through the viewfinder, the mock professor, Channy at the door | d12a (david), d12b (david) | ping, room_tone |
| 25 | 12 | 2:47.1 – 2:49.5 | 2.4 | the rehearsal: through the viewfinder, the mock professor, Channy at the door | m12 (nimith) | sparkle |
| 26 | 12 | 2:49.5 – 2:54.2 | 4.7 | the rehearsal: through the viewfinder, the mock professor, Channy at the door | c12 (channy) | music |
| 27 | 13 | 2:54.2 – 2:59.6 | 5.4 | watching the recording: "look at the audience, and smile" | g13a (kimlong), g13b (kimlong) | click, pop, music |
| 28 | 13 | 2:59.6 – 3:10.6 | 11.0 | watching the recording: "look at the audience, and smile" | g13c (kimlong), d13 (david), k13 (sopheak), g13d (kimlong) | sparkle, heh, pop |
| 29 | 14 | 3:10.6 – 3:15.0 | 4.4 | golden hallway: a bear hug; Channy smiles (slow motion, sunflowers) | g14a (kimlong) | music, squish, heh, footsteps |
| 30 | 14 | 3:15.0 – 3:23.0 | 8.1 | golden hallway: a bear hug; Channy smiles (slow motion, sunflowers) | c14a (channy), c14b (channy) | footsteps, whoosh_rev, music, heartbeat |
| 31 | 14 | 3:23.0 – 3:28.5 | 5.5 | golden hallway: a bear hug; Channy smiles (slow motion, sunflowers) | g14b (kimlong), k14 (sopheak) | boing, music |
| 32 | 15 | 3:28.5 – 3:44.0 | 15.4 | the timer photo: «ម្នាក់ៗខុសគ្នា តែរួមគ្នាយើងខ្លាំង!» ... «ឆឹក!» | g15a (kimlong), a15g (kimlong), a15k (sopheak), a15d (david), a15s (smey), a15m (nimith), a15l (leanghak), a15p (pisey), g15b (kimlong) | music, alarm_beep, whoosh_by, footsteps, tick, shutter, title_whoosh, pop |
