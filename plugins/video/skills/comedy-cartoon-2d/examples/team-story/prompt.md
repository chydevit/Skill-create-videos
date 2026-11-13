# The brief this example was built from

> STORY: "Bong Smei, Bong Nimith & Devit": 2D animation (Khmer), about 2.5–3 minutes, 8 scenes.
>
> STYLE: 2D flat cartoon animation, clean line art, warm lighting, modern Cambodian tech office in Phnom Penh, 16:9,
> smooth character animation, expressive faces, consistent character design across all shots.
>
> **Bong Smei** (Mentor): Cambodian man, mid-40s, short hair with gray at the temples, neat short beard, dark green
> polo shirt, holds a cup of tea, calm, wise, kind smile.
> **Bong Nimith** (Software Engineer): Cambodian man, early 30s, short neat black hair, round glasses, light blue
> button-up shirt, calm and thoughtful, often holding a marker or notebook.
> **Devit** (Junior Software Developer): young Cambodian man, early 20s, messy short black hair, orange hoodie,
> headphones around his neck, energetic and playful, always holding iced coffee. Visibly younger than Nimith.
>
> 1 Introduction: Phnom Penh skyline at sunset, Independence Monument, camera pushes into an office window (narrator).
> 2 Meet Devit: typing fast, colourful code flying, spins in chair, grins, thumbs up.
> 3 Meet Bong Nimith: whiteboard architecture diagram, turns, adjusts glasses, Devit waves from his desk (+ narrator).
> 4 Meet Bong Smei: walks in with tea, nods at both, gentle smile to camera, golden light.
> 5 The Big Project: meeting room, slide "Food Delivery App, 1 Month"; Devit jumps up, Nimith raises his hand, Smei smiles.
> 6 Launch Day Crash: confetti, phone floods with orders, ERROR 500, servers smoke, Devit panics, Smei's hand on his shoulder.
> 7 Teamwork: Nimith's notebook with the backup plan; split screen: servers + load balancer / Devit optimising code;
>   Smei nods proudly; progress bars fill; the clock spins.
> 8 Success and Lesson: "All Systems Online", motorbike deliveries across Phnom Penh, high five, rooftop at night with
>   Smei in the middle, camera pulls back to the sky.
>
> VOXCPM VOICE NOTES: Smei deepest and calmest; Nimith steady, medium-low; Devit most energetic, slightly higher;
> narrator a normal voice. Every dialogue line is in `voices/lines.json` (Khmer + English).

**Revisions during the build (and how they were handled):**
1. Nimith changed from a woman to a man (and the narrator's នាង to គាត់). The voice job was stopped, and only
   Nimith's look, Nimith's and Devit's voices, and the changed narrator line were regenerated. The Smei and
   narrator clips were kept.
2. "Use the Getaway Car look": `film.json` `"style": "bold"` (thick black ink), plus a saturated palette in
   `sets.mjs` `S` and `people.mjs` `CAST`. Originally it was soft pastel.
3. Two lines (d6, s5) were re-rolled after a Khmer Whisper check (`voices/asr_check.py`).

# How it was staged (~2:39, 27 shots); see src/shots.mjs

Lengths come from the voice clips (`take` + `beats`); the times below are from the final build.

| time | scene | shots and beats |
|---|---|---|
| 0–11 | 1 Intro | sunset skyline + monument; Khmer title card; narrator; exponential push into the lit office window, where the cast are tiny |
| 11–22 | 2 Devit | desk shot: typing, code glyphs fly off the monitor, chair spin (back view + motion arcs), thumbs up, two lines, wink |
| 22–39 | 3 Nimith | back view drawing the diagram stroke by stroke, turn with a squash, glasses glint, two lines; two-shot: Devit waves, "បងនិមិត្ត!" bubble on the narrator's line |
| 39–53 | 4 Smei | door opens, walk-in with tea, nods to each, golden light; medium single, two lines, sip |
| 53–78 | 5 Project | wide meeting (slide, Smei presenting, both seated), then singles: Devit's jump (anticipation, launch, arms up), Nimith's raised hand and question, Smei's quiet smile |
| 78–97 | 6 Crash | launch party (banner, confetti, horn); phone CU with orders flooding and accelerating pings, ERROR 500 (music tape-stop); smoking server racks with red wash; Devit panic CU; Smei's hand on his shoulder while the red fades to warm |
| 97–113 | 7 Teamwork | notebook opens to Plan B; slanted split screen (dashboard + LB / Devit with code); wide: both at laptops, Smei nodding, clock spinning, bars filling |
| 113–159 | 8 Success | dashboard turns green (chime); delivery scooter on a shophouse street (narration across the cut); customer + kid receive the bag; high five; rooftop back view; front shots with lip-synced lesson lines; pull back to the stars; "ចប់" card |
