# Authoring SVG sets, characters and maps

## Sets: `scenes/<name>.svg`, viewBox `0 0 2400 1350`
- Use top-level layer groups in back-to-front order: `bg far mid near char front fx`. Any other id needs
  `data-depth`. Depth controls parallax: 0 barely moves, 1 moves with the camera.
- The camera shows 1920 px of the set at zoom 1.0, so keep important things inside x 240–2160 and y 135–1215,
  or plan your moves.
- Use only flat fills. Gradients only for skies, halos and lit ground. **No `<filter>`** (cairosvg ignores it),
  and no CSS.
- Shade each shape with a second path in the shade tone on the side away from the light. Never use outlines.
- Glow = a radial-gradient circle (stop-opacity 0.85 → 0) behind the source.
- Draw night variants with `swap={"#day": "#night", ...}` instead of a second file (see NIGHT in script_src.py).
- Keep scenes rich: 3+ depth planes, 5+ figures in crowd scenes, idle animation on 2–4 sprites.

## Animation attributes (svgscene.py docstring has the full list)
`data-anim="bob|sway|pulse|flicker|spin|drift|walk|appear|fadein|fadeout"`, combinable ("flicker pulse").
Parameters: `data-amp data-period data-deg data-dx data-dy data-at data-speed data-phase data-pivot="x,y"`.
Each animated element becomes its own cached sprite drawn **on top of** its layer's static art, so animate
whole objects (a person, a flame, a bird flock), not tiny pieces deep inside a layered drawing.

## Look effects (what makes it match the reference)
| attribute | where | effect |
|---|---|---|
| `data-light="x,y"` | root `<svg>` | key light position (fire, torch, sun) used by every rim |
| `data-rim-chars="#ffb347"` | root `<svg>` | every included character gets a warm rim on the edge facing the light. **Always set this.** |
| `data-rim="#hex" data-rim-w="6"` | any element | rim on a prop or rock (silhouette edge toward the light) |
| `data-blur="18"` | any element or layer | soft edge: light pools, glows, cast shadows, distant haze |
| `data-blend="add\|screen\|multiply\|overlay"` | any element or layer | glows = add/screen, shade plates = multiply |
| `data-dark="#12051a 0.82 1250"` | root `<svg>` | night look: a dark veil with a soft hole around the key light (radius in set px) |
| `data-dark-lights="570,520,760@1.45"` | root `<svg>` | more light holes (torch, lamp), each switching on at t seconds |
| `data-dark-reveal="1.8"` | root `<svg>` | cold-open reveal: total darkness opening from the light |
| `data-poses="back@0 torch@1.4"` | an include | cut-out animation: the character changes pose over the shot (0.12 s cross-fades) |
| `data-anim="emit"` | small element | particle emitter (sparks, dust): `data-n data-life data-vy data-spread`; add `window` + `data-t0` to start late |
Recipes from the reference:
- **Cold open** (the reference's first shot): `data-dark` + `data-dark-reveal`, the guide turning (`data-poses`),
  the torch lighting (`window` on the flame, glow and `emit` sparks, plus a `data-dark-lights` hole), and a camera
  pulling back from the guide to the whole set.
- **Fire / torch**: a flame sprite (`flicker pulse`), a glow circle (`data-blur="30" data-blend="add"`, radial
  gradient), and a light-pool layer of 4 concentric ellipses (dark red → orange) with `data-blur="18"`, between
  the ground and the characters.
- **Shade plates**: a big diagonal polygon in a dark violet at opacity 0.15–0.25 across buildings and rocks.
- **Pebble texture**: small rounded dashes (`rx` = half height) one tone lighter or darker, scattered on ground
  and walls.
- **Striped hills**: rounded hill ellipses with 2–3 horizontal rounded bars in teal or deep blue.
- **Bushes**: 8–9 pointed leaves fanned around 2 ellipses, sometimes with yellow berries.
- A generator script is fine for repetitive detail (stars, pebbles, leaves). See how `scenes/fire_night.svg` and
  `village_day.svg` are built.

## Characters: `chars/<name>.svg`
- Any viewBox. The feet sit at the bottom centre. Alternative poses are top-level groups `id="pose-<name>"`, and
  expressions are `id="face-<name>"`.
- Place them with `<g data-include="chars/guide.svg" data-x data-y data-h data-pose data-flip data-swap>`, where
  (x, y) is the feet position in the set and h is the height in set px. Guide 450–760 px, adults in mid-ground
  250–330 px.
- Write the palette in a comment at the top of the file, so `data-swap` recolouring (clothes, skin) stays
  intentional.
- The reference character language: **rubber-hose limbs** (thick `stroke-linecap="round"` strokes, which are easy
  to re-pose), tapered torsos, mitten hands (circles), small heads with big hair masses (purple and indigo), eyebrow
  bars, sleepy oval eyes or small whites with dots, red lips, gold earrings, and spotted clothes. No outlines; the
  rim comes from the scene.
- Bundled originals: `guide.svg`, which is Dara (poses stand, point, back, torch); `villager.svg`, a woman (stand,
  carry, sit, offer); and `man.svg`, a bearded man (stand, work, sit, cheer). Add poses by copying a pose group and
  re-routing the limb strokes.

## Maps
```bash
.venv/bin/python ~/.claude/skills/flat-explainer-doc/scripts/make_map_svg.py --view LON LAT WIDTH_DEG \
    --style ochre|green|ice [--borders] [--rivers 6] [--desert LAT] [--no-terrain] --out scenes/map_<x>.svg
```
The output already looks like the reference: teal sea with a grid and "^" marks, an orange coastline over a dark
drop shadow, elevation zones, and mountain clusters from real terrain tiles.
Use `MAP(..., banner="Spread of Farming", routes=[dict(pts=[(lon, lat), ...], at=1.0)])` for the banner title and
the animated dashed arrows.
- `data-view` on the root lets `MAP(..., pins=[dict(lon=, lat=, label=)])` place pins by coordinates.
- The file ends with a comment giving the lon/lat → px formula, for adding hand-drawn mountains, trees or sites.
- Ancient coastlines and glaciers (Lake Agassiz, Doggerland, the Ice Age shoreline): draw them as extra paths on a
  copy of the map, label them as reconstructions, and cite the source in the fact sheet.

## Check before rendering
`make.py shotstills` renders one still per shot and writes contact sheets (`build/shots/sheet_*.jpg`). Look at
them for layout, tags off-screen, characters floating above the ground, and text overlapping art.
Delete `build/cache/svg` after editing an SVG **only if** the stills don't update. Keys are content hashes, so
edits normally re-render on their own.
