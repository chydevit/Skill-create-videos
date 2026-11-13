# Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Frames take 15+ minutes each; both queues stall at the same moments | The Mac idle-sleeps or throttles the GPU. `render_all.sh` wraps the queues in `caffeinate -ims`. If you start Blender by hand, wrap it the same way. |
| The render stopped part-way (session ended, laptop closed) | Run `render_all.sh P` again. Frames that already exist are skipped (`use_overwrite=False`) and each scene's segment is re-encoded. |
| Transparent panels look grainy | Materials with alpha must use `surface_render_method = "BLENDED"`. The helpers `flat(..., alpha)` and `mat(..., alpha)` already set it. |
| Text looks speckled or flickers | The outline and fill layers are too close together (z-fighting). Keep about 0.004 units between the HUD layers. |
| Khmer appears as boxes or broken stacks | The text went through Blender's own text engine. Check that `needs_shaping()` sees it (Khmer range U+1780–U+17FF) and that `scripts/render_text` exists; re-run `setup.sh` if not. |
| `edge-tts` fails or hangs | It needs internet and retries 4 times. Run it again; lines that already succeeded are cached in `build/vo/`. |
| A character pokes through a wall or door | The walk path cuts a corner. Split it into two walks (straight out of the door first, as in the `house` set). |
| A word card covers a face or an animal | Aim the camera shot slightly above the subject so it sits low in the frame, or use a wider shot. |
| Bobo never appears | The `house` and `house_talk` sets hide Bobo until `("prop","bobo","fly_in")`. |
| The episode is too short | Add `say_it()` repeats, `P()` pauses, and quiz questions. Don't slow the voices below about 118–128 wpm (English) or –12% (Khmer). |
| Music drowns out speech | In `audio_build.py`, the final mix is `voice*0.9 + fx*0.7 + music*0.36`, and the music ducks by 50% under speech. Lower the music factor. |
| `unknown set` error | The scene's `"set"` must be a key of `SCENE_CLASSES` in `bl_scenes.py`. |
