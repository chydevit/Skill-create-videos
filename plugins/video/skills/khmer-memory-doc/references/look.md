# Look and engine API

## The look (engine/memory.py)
`memory.inkify(surface, mode, dark, accent, color)` runs on every drawn shot:
- **color = 0 (memory)**: graphite greys on warm paper, a light graphite wash, and tonal pencil hatching (three directions that build up with darkness). It adds a sketchy doubled outline, charcoal strokes, rubbed smudges, age stains and foxing, and darkened page edges.
- **color = 1 (present)**: soft coloured pencil over the same paper, with lighter lines and lighter hatching.
- **Accents survive in memory**: paint props `GOLD_PAINT` (#ff9a2a) and they become a candle-flame orange; paint `BLUE_PAINT` (#1f5cff) and it becomes a faded blue. In the DK film the blue was used only for the 1978 East Zone scarves.
- `LOOK(t)` in script_src returns `color` for memory shots: 0 for most of the film, rising to 0.4 through the last chapter and to 1.0 as the candle is lit. Present shots (`era="present"`) are always full colour. `dark=` on a shot (0–0.3) deepens the tone, for example in the S-21 chapter.

## Shot helpers (script_src.py)
| Helper | What it makes |
|---|---|
| `S(lines, vis, cam, badge, note, era, dark, trans, music, amb, sfx, pre, post, min_d)` | any shot |
| `AP(file, lines, side="r"/"l"/"c", badge="photo"/"document"/"map", focus, z, note)` | authentic image as an old print in a family album: photo corners, pencil caption (Khmer, English, date, credit). Unaltered. |
| `MF(file, lines)` | framed photo on a memorial table, a candle beside it (survivors) |
| `M(lines, view_a, view_b, elements, badge="map"/"map_recon", note)` | relief map; elements are `blob`, `line` (`color=ROUTE` stays orange), `label`, `marker` (`mk(key, km, en)`), `note` |
| `CH(n, km, en, years, under=lambda: scene)` | hand-written pencil chapter card on a ruled notebook page, the chapter's sketch showing through a window |
| `NOTE(lines, title_km, title_en, rows=[(km, en, value)], foot)` | notebook table: "what the sources say", estimates, legal findings |
| `QUOTE(lines, km, en, who)` | a survivor's words hand-copied onto a notebook page, with the source |
| `Q(key)` / `A(key)` | the grandchild asks / the elder answers at the memorial (lip-synced, `era="present"`) |
| `GUIDE(key, scene_fn, cam)` | any lip-synced guide shot; the scene must take `mouth_fn` |
| `MEMO(lines, fn, cam)` | the elder's voice over a grey memory scene (`badge="memory"`) |

Badges: `recon`, `memory`, `symbol`, `photo`, `document`, `map`, `map_recon`, `text`, `guide`.

Transitions (`trans=`): `smoke` (incense smoke drifts across; use it between present and memory), `page` (album/notebook page turn; used for photos and notes), `redraw` (pencil lines fade and redraw), and the default soft dissolve.

## Sets (engine/sets75.py; all reconstructions)
- `make_memorial(tod="morning", people, mouth_fn, incense=True)`: stupa, frangipani, lotus pond, incense smoke. Ground about y 1250 at depth 0.9.
- `make_altar(lit_at=None)`: drawn portrait of the elder's father (cast `dad75`), lotus, incense, and a candle lit at `lit_at` seconds.
- `make_exodus(tod="grey"/"mist", people, city, carts, home=False)`: the road out of the city. `home=True` gives the same road empty and overgrown, for 1979. People at depth 0.6, y 1130–1300; use `T.crowd(n, seed, vx, kinds=[...])`.
- `make_still(kind)`: `shoes`, `glasses`, `bowl`, `notes` (blowing banknotes), `books`, `gate` (chained pagoda gate), `krama` (blue scarf on a fence).
- `make_classroom("books" | "bars")`: an abandoned classroom, or a barred empty room with one chair (a symbol only).
- `make_fields(dam=False, night=False)`: square-dug paddies, or an earthen dam. Use `T.workers(n, seed, y0, y1, h0, h1, pose)` with poses `harvest`, `carry_shoulder` (pole and baskets), `sit`, `carry_bundle`.
- `make_hall()`: communal dining hall, tables and tin bowls (people sit at depth 0.6, y about 960–1000).
- Older sets still available: `Z.make_newsstand("grey")` (Phnom Penh street), `Z.make_empty`, `Z.make_pagoda`, `Y.make_village`, `Y.make_palace60`, `Y.make_assembly`, `Y.make_border("night")`, `Y.make_road`.
- New `tod` palettes: `morning` (present) and `mist` (1979 return).

## Cast additions (engine/cast.py)
- Present day: `sophal_old` (elder), `malis` (grandchild), `mourner_m`, `mourner_w`.
- 1975 family: `sophal_y`, `mom75`, `dad75`, `vuthy`.
- In black: `sophal_k`, `vuthy_k`, `kr_soldier`, `kr_soldier_f`, `worker_m`, `worker_w`, `child_k`.
- East Zone (blue scarf): `blue_m`, `blue_w`.
- Older cast still available: `pp_man`, `pp_woman`, `student_m`, `kh_monk`, `kh_elder`, `refugee_*`.
- Never put a weapon pointed at a person. The soldiers in the DK film carry nothing.

## Music (engine/music70.py MOODS)
`remember`, `april`, `exodus`, `zero`, `coop`, `state`, `targets`, `silence` (no score), `purge`, `war75`, `after`, `hope`, `credits75`.

SFX names for `sfx=(...)`: `monbell` (distant monastery bell), `match` (match plus flame), and the older ones. Ambience: `delta` (dawn birds), `town`, `farm`, `night`, `none`.
