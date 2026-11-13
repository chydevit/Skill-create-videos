# Story films: dialogue-driven scenes, people, lip-sync

Use this for character stories where people talk: introductions, office/school/family life, lessons, explainers
with a cast, or any brief that's mostly dialogue and narration rather than slapstick. The worked example is
`examples/team-story/` (*Bong Smei, Bong Nimith & Devit*: 8 scenes, ~3 min, Khmer dialogue + narrator).

## Contents
1. The timeline comes from the voices
2. People (`people.mjs`)
3. Lip-sync
4. Staging dialogue scenes
5. Style: pastel vs bold
6. Music and ambience for stories
7. Changing the brief midway
8. A new Office series episode (the `kimlong` example)

## 1. The timeline comes from the voices
In a talky film, shot lengths are set by the lines, so don't hard-code times. Use the running clock:
```js
import { take, beats, talk } from './kit.mjs';
const b = beats([0.6, 's1', 0.35, 's2']);          // numbers = gaps (s), strings = line ids
take(b.end + 1.2, (ctx, lt, t) => { /* draw */ }, [...b.cues, [0, 'room_tone', { dur: b.end + 1.2 }]]);
```
- `beats()` returns `{ cues, end, at: {id: startTime} }`, so you can key actions to lines (`lt > b.at.s2`).
- `lineDur(id)` (vox.mjs) gives the real clip length after pause-tightening, or an estimate (~11 Khmer chars/s)
  until the clip exists. You can stage everything before the voices finish; when they arrive, the whole film
  re-times itself.
- Narration can run across a cut: put the cue in the first shot and size the shots from `lineDur`
  (see the delivery montage in the example).
- Write `docs/shotlist.md` with target lengths per scene, then compare with the printed timeline after
  `npm run audio`. Trim gaps or tails if the film runs long; don't speed up voices.

## 2. People (`people.mjs`)
`person(ctx, who, o)` is a natural-proportion cartoon person (big friendly head, IK arms and legs, clean lines).
`who` is a key in `CAST` or a look object (spread a CAST entry and change colours for extras). A look has
`H` (height px), `sw`/`ww` (shoulder and waist half-width), skin, hair, `hairStyle` (short | neat | messy |
ponytail | part | bob | wavy | receding | long | bun | spiky), `beard`, `glasses`, clothes `style` (polo | shirt |
hoodie | tee | blouse | flannel) and colours, `eyeSize`. Extras on a look:
- women: `skirt` (colour; add `pencil: true` for a fitted pencil skirt), `lashes`, `thinBrows`, `clip` (hair clip
  colour, with `bob`), `tie` (ponytail hair-tie colour), `chainGlasses` (glasses hanging on a chain)
- work: `lanyard` (colour; an ID badge, hide with `badge: false`), `necktie`, `apron` (waiter's bib apron),
  `camera: true` (a camera round the neck; hidden with `camera: false` or while holding one)
- `flannel` takes `tee` (the T-shirt under the open shirt) and `plaid` (check colour); `browCol` sets brow colour
- headphones: `headphones: true` (small cups at the neck) or `phones: 'on' | 'one' | 'neck' | 'off'` (big over-ear
  cans; `'one'` pushes one cup up, `phonesLift` picks the side, `phonesCol` the colour). Override per shot with `o.phones`.
- `bag` (backpack colour, drawn when `o.backpack`)

**Cartoon proportions (use them; natural proportions look stiff next to Getaway Car):** each look can set `legs` and
`torso` (fractions of H), `headS` (head scale, 1.4–1.8), `hx`/`hy` (head stretch), `belly` (0–0.7), `arm` (segment
length), `nose` (`bulb`, `point` or `button`) and `neck`. `CAST` holds the Office series cast, each with a
silhouette hook: **smey** (early 30s, light blue shirt), **nimith** (late 20s, tall and lanky, glasses, white tee),
**david** (about 20, short and round, giant head, grey hoodie), **sopheak** (19, slim, side part, headphones round
the neck), **leanghak** (mid 30s, bob with a clip, cream blouse, navy skirt, lanyard), **pisey** (mid 40s, wavy hair, glasses on
a chain), **kimlong** (19, chubby, spiky hair, open red flannel, camera), **channy** (22, long straight hair, white
blouse, pencil skirt), **sreyneang** (21, high bun, navy apron), plus **boss**, **coworker** and **professor**.
Use them for a new episode, or spread one (`{ ...CAST.channy, shirt: '#…' }`) for extras. The team-story example
registers its own first-film looks (smei, nimith, devit) in `src/cast.mjs`; a film that needs different looks
does the same with `Object.assign(CAST, {...})` and imports that module from every entry file (shots, sheet, cover).

Limbs are rubber hoses, eyes are big whites with small pupils, brows are thick and outlined, and every figure has a
breathing bounce on twos plus a squash on each syllable.

**Contact between characters:** use `anchors(who, o)` to get world positions (`shL`, `shR`, `handL`, `handR`,
`head`, `chest`) and `toLocal(who, o, point)` for reach targets. A hand on a shoulder or a high five then lands
correctly whatever the body shapes. The cover uses `anchors().head` to put every face at the same height.

Options: `x, y, s, facing` (-1..1: 3/4 left to front to 3/4 right), `back` (seen from behind), `mirror` (flip
the figure to use the other hand), `pose`, `t`, `expr`, `mouth` (lip-sync 0..1), `look:[x,y]`, `hold:[left,
right]` (tea | coffee | marker | phone | notebook | camera), `nod`, `tilt`, `sq`, `sit`, `tears` (0..1, eyes welling
up then a drop), `headOnly` (redraw just the head, e.g. over a pillow or a desk drawn on top of the body), `rec`
(the held camera shows a red REC light).
- **Poses:** stand, walk (`ph`), sitTalk, type, thumbs, wave, draw, glasses, present, presentL, sip, jump (`hop`),
  raise, cheer, clap, panic, rub (hand rubbing the forehead), scratch (embarrassed head scratch), point (index finger
  out), wag (finger wagging "no no"), phone (phone in the left hand; with `reach` the right hand taps it), call (phone
  at the ear), reach / reachL (`reach:[x,y]` in local px; add `point: true` for an index finger that follows the
  forearm), reach2 (both hands to `reach` and `reachL`, e.g. a bear hug), notebook, highfive, hold, sitBack,
  sampeah (palms together, the Khmer greeting), facepalm, cover (hands over the face), chin (thinking), chest
  (hand on the heart, other arm flung out), heart (hand heart), belly (clutching the stomach laughing), shout
  (hands cupped round the mouth), ears (hands on the headphone cups), bump (fist bump), wave2 (two-hand wave),
  stretch, hug, clip (fixing a hair clip), fixHair (both hands smoothing the hair), leanWall (one hand on a wall,
  legs crossed), film (camera held up in both hands; `rec`), slump (asleep on the desk; `headDrop` lowers the head).
- **Expressions:** smile, calm, grin, laugh, proud (eyes closed), surprised, worried, panic, thinking,
  determined, tired (heavy lids, eye bags), focus (tongue out, concentrating), sleep (eyes shut), wink (screen-right
  eye a ^ curve; no blink), love (beating heart eyes). Blinks are automatic.
- **Props and furniture:** `chair`, `chairBack`, `teaCup`, `icedCoffee`, `marker`, `notebook(open, drawFn)`, `phone`,
  `camera(ctx, x, y, s, rot, rec, t)` (a mirrorless camera, lens to the viewer).
- **Elbows:** the IK always picks the outward/downward elbow, so raised hands don't cross the face.
- **Hands on top of props:** `handShape(ctx, x, y, side, 'point', rot, skin)` is exported, so a shot can draw a
  big cartoon phone at `anchors().handL` (`phoneUI` from screens.mjs) and then redraw the tapping fingertip over
  its screen: draw the person, then the phone, then `handShape(...'point'...)` at `anchors().handR`.

Render a model sheet (`npm run sheet`) of every pose you plan to use before animating. Check age reads
(beard and gray temples for older, rounder face and bigger eyes for younger), that each character has a
silhouette hook, and gender and clothing exactly as the brief says.

## 3. Lip-sync
`talk(who, t)` returns mouth openness from the speaking clip's loudness (held on twos); pass it as
`mouth` (the example's `pp()` wrapper does this for every character). Mouths only move during that character's
own line cues. Narrator lines move no mouth. Small head bob comes with it. Before clips exist it flaps
procedurally, so early stills still show who's talking.

## 4. Staging dialogue scenes
- **Keep it a cartoon, not just people talking.** Give every action Getaway Car treatment:
  - smear ghosts on fast moves (chair spin, turn)
  - squash on landings
  - sound-effect words: TAP TAP TAP!, WHOOSH!, TING!, BOING!, KABOOM!, POW!, ZOOM!, YUM!
  - impact stars on hits and reveals
  - sweat drops and stress marks for panic
  - sparkle stars for good ideas
  - a camera shake on crashes

  Leave the heartfelt ending quiet.
- Shot pattern per scene: establishing wide → medium single on the speaker (cam zoom 1.5–2.1) → reaction or
  two-shot → back to wide for the button. "Cut between all three" = a single on each speaker.
- Give each speaker an action: turn to camera, adjust glasses, sip tea, thumbs up. Put it in the gap
  before or after the line, not on top of it.
- Background characters keep doing something (typing, waving).
- Hand contact (hand on shoulder, high five): compute the target from the other character's position in world
  space and convert to local (`(wx - o.x) / o.s`). Stand them close enough that the arm doesn't stretch
  rubber-style.
- Insert shots carry story beats without dialogue: phone screen with orders and an error, server rack smoking,
  dashboard going green, notebook with the plan, wall clock spinning (time passes).
- Split screen: two `clip()` polygons with a slanted divider, each with its own staging.
- Ending: a back view of the cast looking at the city, then the camera pulls back to the sky and a title card.

## 5. Style: pastel vs bold
`core.mjs` reads `film.json` `"style"`: `"bold"` (default: ink `#1d1520`, 7 px, saturated TV-cartoon colours) or
`"pastel"` (ink `#3b2d3b`, 5 px, softer). The team-story example started pastel and was switched to bold at the
user's request ("make it look like Getaway Car"). That took one `film.json` flag plus a bolder colour set in
`sets.mjs` `S` and `people.mjs` `CAST`. For pastel, use lighter, less saturated tokens (soft peach, mint,
lavender, baby blue). Both styles use a warm light wash over interiors (`warmLight`).

## 6. Music and ambience for stories
Music sections `warm` (e-piano + roneat-style xylophone), `upbeat` (marimba), `build` (driving ostinato for
work montages), `triumph` (brass celebration), `tender` (pads + piano for heartfelt endings), and `tension` for
problems. Set `film.json` `"mix": {"music": 0.95, "duck": 0.4}`: music plays full between lines and ducks under
dialogue automatically. Use `npm run qc` levels to confirm no window sits more than ~10 dB below the dialogue
windows unless it's meant to be quiet. Ambience per shot: `room_tone`, `city_amb`, `night_amb`
(each `{dur}`). SFX for offices: `typing`, `ping`, `error_buzz`, `alarm_beep`, `server_hum`, `party_pop`,
`party_horn`, `chime_success`, `highfive`, `swivel`, `marker`, `footsteps`, `sip`, `page_flip`, `clock_fast`,
`motorbike`, `sparkle`, `nod`, `whoosh {f0, f1, dur}`.

## 7. Changing the brief midway
Users revise briefs, for example changing a character's gender or a line. Stop the voice job if it's running.
Then change only what the revision touches:
- the look in `CAST`
- that character's voice: delete `voices/<who>.wav` and the clips
- the edited lines: delete just those clips

Re-run `npm run voices`. Everything else, including other characters' finished clips, is kept.

## 8. A new Office series episode (the `kimlong` example)
`new_project.sh <dir> --example kimlong` scaffolds Episode 7 «គីមឡុង ស្ដេចញ៉ែ» (3:44, 15 scenes, 32 shots), the
latest episode with the full series cast. Copy it and replace the scenes for the next episode:
- `src/shots.mjs` only imports the scene files (`ep/q1.mjs`, `q2`, `q3`, about five scenes each). Each scene is a
  `// ===== SCENE n — ...` header followed by `take()` calls. Keep one header per brief scene so a shot list can
  be generated from the source.
- `ep/common.mjs` holds the series helpers: cast keys (`SM, NM, DV, KP, LH, PS, KL, CN, SN`), `D` (line length),
  `pp(ctx, who, t, o)` (person + lip-sync), `seat(who, x, o)` (seated at a desk), `atHead(who, o, headY)` (place a
  person so the head lands at a height), `headOf`, `room` (the office), `deskFront`, `monitor`, `backRow`,
  `thoughtBubble`, `titleKh` (the episode title card), `banner`, `heartPop`, `sweat`, `stars`, `blush`, `zzz`,
  `warmLight` / `goldHour` / `nightTint` (light washes), `wallClock`.
- `places.mjs` has the series sets: `home`, `street` (+ `tuktuk`), `hallway` (the two office doors, `openB`, `gold`),
  `deskRow`, `lotusOffice`, `restaurant` + `lunchTable`, `bench`, `mySlide`; `sets.mjs` the original office,
  meeting room, skyline and rooftop.
- `ep6.mjs`: `ICON` (small drawn icons used in place of emoji) and `tag(ctx, x, y, text, k, {icon, col, ink, size,
  rot})` (pop-in label), `victory`, `timeChip`, the phone game (`gameScreen`, `gamePhone`), group chat
  (`chatPhone`), university sets (`campus`, `classroom`, `uniHall`), `moto`, `laptop`, `polaroid`.
- `ep7.mjs`: `flirtFx` (✨💕 round a face), `plok` (the «ប្លុក!» rejection), `nameCard` (lower-third name tag),
  `tripod` / `tripodSide`, `viewfinder` (REC ●, timecode, battery: "seen through the camera"), `meetingRoom`,
  `slide`, `sunflowers` (falling 🌻), `dreamGlow`, `scoreCard`, `photoFrame` (freeze-frame photo border).

Emoji in a brief («🤜🤛», «👑», «🏆», «💔», «😎») don't render in Koulen: draw them with `ICON` or a small prop
next to the Khmer text. Slow motion: draw the shot with a scaled clock (`st = t * 0.3`) and add a slower music
section under it. Freeze frame: hold one `t` for the drawing, flash white with a `shutter` cue, and add a photo
border with a slow pull-back.
