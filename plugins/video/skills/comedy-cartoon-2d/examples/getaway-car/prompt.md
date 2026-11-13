# The brief this example was built from

> 2D ANIMATION BUILD PROMPT: "GETAWAY CAR"
>
> Create a short comedic 2D animation (60–90 seconds) in a bold cartoon style. Thick black outlines, flat bright colors,
> simple shading, exaggerated squash-and-stretch movement, like a modern TV cartoon short. 16:9 frame, 24fps, snappy
> timing, holds before gags, fast smears during action.
>
> CHARACTERS: Benny (the driver): short, round, nervous, tiny striped beanie, big sweaty eyebrows, white knuckles.
> Marge (the boss): tall and lanky, overconfident smirk, burglar mask, sack of loot with a "$".
> The Getaway Car: beat-up tiny green hatchback, too small for them, dented door, rattling muffler, one flickering
> headlight, expressive bumper "face" that grimaces when stressed. The Cop: slow, bored officer on a bicycle with a bell.
>
> BEATS: 1 Opening (0–10s) bank, alarm, they cram into the car, legs out the window, loot wedged on the roof.
> 2 False start (10–20s) car rattles, launches backward into a trash can, Marge deadpan to camera.
> 3 Chase (20–50s) bike cop keeps catching up; duck family crossing while sirens wail; Benny signals politely at every
> turn; money flies off the roof, Marge grabs bills mid-air; drive-through detour, Benny panics and orders fries.
> 4 Climax (50–70s) bridge, out of gas, cop pedals up, Benny pushes while Marge steers, extreme squash-and-stretch.
> 5 Punchline (70–90s) car rolls downhill, escapes, lands perfectly in a parking spot of the police station. The bike cop
> arrives, rings his bell once. Iris out.
>
> CAMERA: wide establishing, low angles for speed, rapid cuts in the chase, close-up reactions, speed-line background
> loop. AUDIO: upbeat frantic jazzy chase music, boings, honks, skids, slide whistles; minimal dialogue.
> COLOR: warm city tones (orange, teal, yellow), green car pops, red/blue siren flashes.

Later the user asked for the dialogue in **Khmer** with VoxCPM2 voices (https://voxcpm.com/en/).

# How it was staged (90.0 s, 35 shots); see shots.mjs

| time | shots | beat and gags |
|---|---|---|
| 0–10 | S01–S03 | title card over the bank; alarm; doors BAM; Benny dives in the window, Marge squishes in (legs out, striped socks); bag pops out twice, third time lands on the roof (THUD, car grimaces); "បើកទៅ។" |
| 10–20 | S04–S08 | close-up gulp → determined; STOMP insert; car rattles in place (VROOOM); shoots backward into the trash can (CRASH, banana peel on Marge); deadpan stare + crickets; "...wrong gear"; CLUNK, ZOOM |
| 20–33 | S09–S12 | low-angle head-on chase (perspStreet + radial lines + siren wash); bored cop yawns; cop is suddenly right behind them; skid stop; ducks cross (front view, cop approaching in the distance), cut-in facepalm, last duckling stares |
| 33–49 | S13–S15 | top-down route with turn signals (cop rides straight past); "JUST DRIVE" close-up; bills fly off, Marge's arm stretches to snatch them, missed bills land in the cop's basket; drive-through: speaker, panic, "large fries", cop waits in line, peel out |
| 49–70 | S16–S20 | sunset bridge wide; sputter (PUTT ×3, music tape-stops); fuel gauge insert; cop approaches; "PUSH!"; push cycles with heave stings and squash/stretch; crest, Benny pancaked, dives back in as the car rolls |
| 70–90 | S21–S25 | downhill speed lines; head-on into camera; car jumps and lands PERFECT in a parking bay; cheer; pan up reveals POLICE STATION (record scratch); cop rolls in, rings the bell once; iris out on the car's sheepish grimace; THE END |
