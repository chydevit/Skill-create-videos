# Engine reference

All drawing is Canvas 2D (`@napi-rs/canvas`) at **1920×1080, 24 fps**. Every module is plain ESM in `src/`.
Coordinates are pixels, y down. Characters' origin is **feet / ground centre, facing right**; `flip: true` mirrors.

## Contents
1. core.mjs: palette, timing, drawing primitives
2. kit.mjs: shots, camera, title card, perspective street
3. chars.mjs: the example cast (rig options)
4. bg.mjs: sets and props
5. fx.mjs: effects
6. render.mjs / build.mjs: commands and speed
7. Writing a new character

## 1. core.mjs
- `W, H, FPS, INK, LW`: ink colour and outline width follow `film.json` `"style"` (`bold`: `#1d1520`, 7 px; `pastel`:
  `#3b2d3b`, 5 px), palette `C.*` (teal/orange/yellow city tones, `green*` reserved for
  the hero prop so it pops, `red`/`blue` for sirens, skin tones, `navy`, `black`, `money`, `copBlue`, `sea`…).
- Timing: `seg(t, a, b)` → 0..1 clamped; `lerp`, `clamp`; `ease.{in,out,inOut,in3,out3,back,elastic,bounce}`;
  `onTwos(t)` (holds every 2nd frame for character animation); `wobble(t, freq, damp)` (damped settle, 0 at t=0);
  `hash(n)`, `jit(t, seed, amp)` (jitter on twos), `rng(seed)`.
- Drawing: `paint(ctx, fill, lw=LW, stroke=INK)` fills + outlines the current path. Shapes start a new path:
  `circle, oval, rrect, poly(pts), smooth(pts, closed, tension, newPath)`.
  `hose(ctx, pts, width, color)` = rubber-hose limb (2–4 points). `cel(ctx, pathFn, base, shade, dx, dy)` = flat fill with
  a one-tone shade crescent (shade shows where the shape shifted by dx,dy doesn't cover). `clipTo(ctx, pathFn, drawFn)`.
  `text(ctx, str, x, y, {size, font, fill, lw, align, rot})`: outlined lettering; **Khmer strings switch to Koulen
  automatically** (`isKhmer`). `ik(ax, ay, bx, by, l1, l2, bend)` → knee/elbow point.
- Squash & stretch: most rigs take `sq` (>0 = squashed wide/flat, <0 = stretched tall/thin; volume-preserving).

## 2. kit.mjs
- `shot(start, end, draw(ctx, lt, t), cues)`; `setShift(s)` (later shots move s seconds; see craft.md "Retiming");
  `duration()`; `drawFrame`, `allCues` (re-export these from shots.mjs, see the starter).
- `cam(ctx, cx, cy, zoom, rot)`: world point to frame centre. Wrap in `ctx.save()/restore()`.
  `toScreen(x, y, cx, cy, z)` maps world to screen (iris targets). `shk(t, amp)` gives camera shake offsets.
- `P(a, b, k)` lerp points; `arc(a, b, k, h)` hop/jump arc.
- `titleCard(ctx, lt, 'TITLE', {inAt, outAt, y, size})`: ribbon banner pop-in/out.
- `perspStreet(ctx, t, {vpx, vpy, spd, h, z0, extra(pr)})`: head-on street with buildings racing past (low angle when `vpy`
  is low and `h` ~1). `pr(X, Y, Z)` projects a street point (road half-width 7, buildings at ±11) for placing things.
- `radialLines(ctx, t, cx, cy)`: speed lines bursting from a point.

## 2b. Dialogue timing + lip-sync (kit.mjs + vox.mjs)
`take(len, draw, cues)` appends a shot at a running clock. `beats([0.5, 'id1', 0.3, 'id2'], start)` →
`{cues, end, at}` lays lines out back to back using `lineDur(id)`: the real clip length after pause-tightening, or
a text estimate until the clip exists. `talk(who, t)` gives mouth openness 0..1 during that character's lines.
`node src/vox.mjs` (`npm run durations`) caches durations and lip envelopes; `npm run build` runs it first.
See story.md.

## 2c. people.mjs: natural-proportion people
`person(ctx, lookOrKey, {x, y, s, facing, back, mirror, pose, expr, mouth, look, hold, nod, tilt, sq, sit, t})`.
`CAST` is the Office series cast. Its looks, poses, expressions and props are listed in story.md §2. `chair`,
`chairBack`, `teaCup`, `icedCoffee`, `marker`, `notebook`, `phone`, `camera`. `anchors(who, o)` and
`toLocal(who, o, point)` give contact points. The outline width follows the film style.

## 2d. screens.mjs: phones, laptops, security icons (optional module)
`phoneUI(ctx, cx, cy, h, t, {mode, ...})` draws a big cartoon phone centred on (cx, cy). Modes: `home`, `msg` (scam
prize message; `k` pop-in, `flash` link, `alert` red PHISHING overlay), `code` (2FA code notification), `update`
(`press`, `prog`, `done` → shield), `call` (`answered`, `timer`, `press`), `blocked`, `quiz` (`reveal1/2` circle
the misspelled link / password box), `safe`, `tutorial` (a video lesson playing; `k` progress), `text` (a message from `from` with `lines`; `k` pop-in).
`phonePoint(cx, cy, h, PHONE.link)` gives a world point on the screen
(for a finger to aim at). `laptopUI(ctx, x, y, w, h, t, {mode, base})` draws a laptop whose screen is (x, y, w, h):
`links` (real vs fake URL, `hl`, `mag` magnifier, `stamp`, `stranger`), `2fa` (`typed`, `lock`, `deny`, `code`),
`password` (`weak`, `crack`, `strong`, `ok`, `accounts`), `profile` (`blur:[a,b,c]`, `priv`), `slides` (a wall of
text that flies off line by line as `clean` goes 0→1). Icons: `padlock`,
`shield`, `check`, `cross`, `warnTri`, `wifi`, `gift`, `stamp(word, x, y, k)` (rubber stamp slam), and
`thief(ctx, x, y, s, t, {pose: sneak|type|grab|bonk|laugh|sit, flip, reach})`, a hooded cartoon burglar.
`richLine()`/`pieceX()` draw a line of text in coloured pieces (to highlight one letter of a URL).

## 3. chars.mjs: example cast (adapt or copy-modify for new characters)
| function | options |
|---|---|
| `benny(ctx, o)` short round nervous guy, striped beanie | `x,y,s,flip,rot,sq,t,ph` (cycle phase), `look:[x,y]`, `sweat 0..1`, `blush`; **pose** stand, run, drive (`wheel:[x,y]`), grip (`hands:[[x,y],[x,y]]`), push, armsUp, signal, eat (`holding:'fries'`); **expr** worried, panic, shock, gulp, determined, strain, sheepish, happy |
| `marge(ctx, o)` tall lanky boss, mask, red bun | pose stand, run, reach (`reach:[x,y]`), facepalm, steer, cheer; expr smirk, deadpan, blink, yell, angry, strain, shock, grin; `headRot`, `bagHeld` |
| `copBike(ctx, o)` bored cop on a bicycle | `pedal` (turns), `wheel` (angle), expr bored/yawn/look, `bell 0..1` (thumb press), `light` (pass t for siren flashing), `sirenOn` |
| `car(ctx, o)` tiny hatchback with a face (side view, faces right) | `face` neutral/grimace/worried/sad/scared/shock/happy/strain/squint/dizzy/sleepy, `look`, `light` (0 = dead headlight), `sq, bounce, tilt, shake, wheel`, `bag:{x,y,s,rot,sq,open,strap}`, `crew(ctx)` draws occupants **clipped to the windows**, `outside(ctx)` draws things poking out (legs, arms) |
| `carFront(ctx, o)` head-on view | `face`, `bennyExpr`, `margeExpr`, `light`, `look`, `bounce`, `shake`, `bag:false` |
| props | `bag(ctx,x,y,s,rot,sq,open)`, `bill(ctx,x,y,s,rot,flipX)` (animate flipX = cos for flutter), `fries`, `hand(ctx,x,y,r,grip)`, `drop` (sweat), `duck(ctx,x,y,s,ph,baby,flip,look)`, `bikeWheel`, `carWheel` |

Car geometry at s=1: wheels at x ±115, y -36; rear window x -154..-22, front window x -6..104, y -230..-164; headlight
(eye) at (168,-122); roof top ≈ -245. The example film's `crew()` helper shows how to seat characters and stick legs
out of the window.

## 4. bg.mjs: sets and props
`sky({horizon, cloudX, sun})`, `cloud`, parallax rows `farCity(scroll, baseY)`, `midCity`, `shopRow` (awnings, shop
windows), `street(scroll, y0)` (sidewalk, curb, road, lane dashes), `speedBG(t, {speed, horizon, groundY})` (the
classic speed-line loop for driving shots), props `lamp, hydrant, mailbox, trashCan({crush, lid}), trashLid, bananaPeel,
fishBone, tinCan`, buildings `bank({doors, alarm, t})`, `driveThru`, `menuBoard({talk})`, `policeStation`, `squadCar`,
bridge pieces `sea, deckY, bridgeTower, skyline`, top-down `topCity({blocks}), carTop, bikeTop`.
Parallax: scroll far layers at ~0.15×, mid 0.4×, shop row 0.9×, street 1×.

## 5. fx.mjs
`dust(ctx, x, y, life, {n, spread, r, dir, seed})` (life 0..1 → pass `seg(lt, a, b)`), `puff`, `exhaust(x, y, t,
{rate, dark})`, `impact(x, y, r, life, {word})` (spiky burst), `sfxText(word, x, y, life, {size, fill, rot, wob})`
(pop-in lettering; Khmer works), `speedStreaks(x, y, len, h, t, {dir})`, `sirenWash(t, amt)` (red/blue edges, draw
after camera restore), `iris(cx, cy, r)`, `wash(col, a)` (flash frame), `stressMarks`, `zzz`, `musicNote`, `grain`
(applied to every frame by drawFrame).

## 6. Commands and speed
- `npm run stills -- 1.5 4.2 9` → `build/stills/t_*.png` + `sheet_N.png` (3×3 contact sheets). **Use this constantly.**
- `npm run sheet`: model sheet of the cast (`src/sheet.mjs`, edit it for your cast).
- `npm run video`: parallel segments to `build/video.mp4` (~25 s for 90 s on 8 cores; one frame ≈ 8–30 ms).
- `npm run build`: video + audio + mux + qc. `npm run audio` / `npm run mux` / `npm run qc` individually.
- A harmless ffmpeg warning "Truncating packet of size 8294400 to 65536" can appear; frame counts are still exact.

## 7. Writing a new character
Copy the closest example rig and change proportions, palette and features. Keep the pattern:
1. `ctx.save(); translate(x,y); rotate(rot); scale(s*(flip?-1:1)*(1+sq), s/(1+sq))`.
2. Compute a rig per pose (hip, shoulders, hand and foot targets), then draw back limbs → body (`cel`) → front limbs →
   head (expression switch) → front arm.
3. Faces carry the comedy: big readable eyes (white + small pupil, `look` offsets), thick brows whose angle
   sells the emotion, simple mouth shapes per expression. Give each character one silhouette hook
   (Benny's tiny beanie, Marge's height and bun, the cop's cap and moustache, striped socks so legs read
   against dark shapes).
4. Render a model sheet (`npm run sheet`) and look at it before animating.
