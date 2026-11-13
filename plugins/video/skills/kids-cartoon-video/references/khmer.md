# Khmer (ភាសាខ្មែរ) guide

## Contents
1. How Khmer is handled
2. Voices
3. Glossary for children's content
4. Useful sentences
5. Bilingual patterns
6. Checks before publishing

## 1. How Khmer is handled

- **Speech:** a line is spoken in Khmer when `lang="km"`. That's the default in `khmer` mode; in `bilingual` mode, mark Khmer lines with `K(...)`. These lines use edge-tts neural voices, which need internet. Results are cached in `build/vo/`, so a rebuild doesn't call the service again.
- **Text:**
  - Blender can't lay out Khmer correctly: subscript consonants (ជើង) and stacked vowels come out broken.
  - So any card, caption or badge containing Khmer characters is drawn by `scripts/render_text`, which uses macOS CoreText with the *Khmer MN Bold* font. It's saved as a PNG and shown on a plane.
  - Mixed text such as `"RED\nក្រហម"` works.
  - If Khmer appears as boxes or broken stacks, re-run `setup.sh` to recompile the renderer.
- **Line wrapping:** Khmer normally has no spaces between words, so CoreText wraps it by itself (captions and sentence cards pass a maximum width). A space in Khmer marks a phrase break, which is a good place to wrap.
- **Size:** Khmer glyphs are drawn at 0.74× so they sit well next to English text (`KHMER_SCALE` in `bl_hud.py`).

## 2. Voices (`VOICES_KM` in `scripts/audio_build.py`)

| Role | Voice | Speed | Pitch factor | Result |
|---|---|---|---|---|
| Narrator | km-KH-SreymomNeural (female) | -12% | 1.00 | warm teacher |
| Luna | km-KH-SreymomNeural | -8% | 1.20 | young girl |
| Milo | km-KH-PisethNeural (male) | -8% | 1.32 | young boy |
| Bobo | km-KH-SreymomNeural | +0% | 1.55 | small cartoon bird |
| Animals | Sreymom / Piseth | | 0.72–1.5 | cat, dog, duck, cow sounds |

Only these two Khmer neural voices exist. The characters are told apart by pitch.

## 3. Glossary for children's content

Use simple, warm, everyday Khmer.

- **Talking to the viewer:** the narrator calls children **ប្អូន** ("little one"), e.g. **តើប្អូនអាច… បានទេ?**
- **Between the kids:** Milo and Luna use **ឯង**/**ខ្ញុំ** with each other, the normal way friends of the same age talk.
- **Character names:** Milo = **មីឡូ**, Luna = **លូណា**, Bobo = **បូបូ**.

| English | Khmer |
|---|---|
| Good morning | អរុណសួស្តី |
| Hello | សួស្តី |
| Goodbye | លាហើយ |
| See you next time | ជួបគ្នាលើកក្រោយ |
| Thank you | អរគុណ |
| Friend | មិត្តភក្តិ |
| Great job! / Well done! | ពូកែណាស់! |
| Your turn | ដល់វេនប្អូន |
| Say (after me): … | និយាយតាម: … |
| Let's count! | តោះរាប់! |
| Red / Blue / Yellow / Green | ក្រហម / ខៀវ / លឿង / បៃតង |
| Pink / Purple / Orange / White / Black | ផ្កាឈូក / ស្វាយ / ទឹកក្រូច / ស / ខ្មៅ |
| color | ពណ៌ (e.g. ពណ៌ក្រហម "red color") |
| 1–10 | មួយ ពីរ បី បួន ប្រាំ ប្រាំមួយ ប្រាំពីរ ប្រាំបី ប្រាំបួន ដប់ (digits: ១ ២ ៣ ៤ ៥ ៦ ៧ ៨ ៩ ១០) |
| cat / dog / duck / cow / rabbit | ឆ្មា / ឆ្កែ / ទា / គោ / ទន្សាយ |
| bird / fish / chicken / elephant | បក្សី (សត្វស្លាប) / ត្រី / មាន់ / ដំរី |
| apple / banana / bread / milk / water | ផ្លែប៉ោម / ចេក / នំប៉័ង / ទឹកដោះគោ / ទឹក |
| rice / mango / orange (fruit) | បាយ / ស្វាយ / ក្រូច |
| run / walk / jump / clap / dance | រត់ / ដើរ / លោត / ទះដៃ / រាំ |
| stand up / sit down | ក្រោកឈរ / អង្គុយចុះ |
| happy / sad / excited / tired / surprised | សប្បាយចិត្ត / ពិបាកចិត្ត / រំភើប / អស់កម្លាំង / ភ្ញាក់ផ្អើល |
| sun / tree / flower / butterfly | ព្រះអាទិត្យ / ដើមឈើ / ផ្កា / មេអំបៅ |
| house / farm / picnic / playground | ផ្ទះ / កសិដ្ឋាន / ពិកនិក / សួនកុមារ |
| Animal sounds | ឆ្មា: មៀវ! · ឆ្កែ: វូវ! វូវ! · ទា: ក្វាក់! ក្វាក់! · គោ: ម៉ូ! |

## 4. Useful sentences

| English | Khmer |
|---|---|
| What is this? | តើនេះជាអ្វី? |
| It's a cat! | នេះជាឆ្មា! |
| What color is this? | តើនេះពណ៌អ្វី? |
| It's red. | វាពណ៌ក្រហម។ |
| How many apples? | តើមានផ្លែប៉ោមប៉ុន្មាន? |
| What is your name? | តើឯងឈ្មោះអ្វី? (narrator to viewer: តើប្អូនឈ្មោះអ្វី?) |
| My name is Luna. | ខ្ញុំឈ្មោះលូណា។ |
| How are you? | តើឯងសុខសប្បាយទេ? (to the viewer: តើប្អូនសុខសប្បាយទេ?) |
| I'm fine, thank you. | ខ្ញុំសុខសប្បាយ អរគុណ។ |
| I like apples. | ខ្ញុំចូលចិត្តផ្លែប៉ោម។ |
| What do you like? | តើឯងចូលចិត្តអ្វី? |
| I am happy. | ខ្ញុំសប្បាយចិត្ត។ |
| Can you say "…"? | តើប្អូនអាចនិយាយថា "…" បានទេ? |
| Keep practicing every day. | ហាត់រៀនរាល់ថ្ងៃណា។ |

## 5. Bilingual patterns (teaching English to Khmer speakers)

The characters speak English so children hear native-like models. The Khmer narrator only bridges meaning. Keep the Khmer short, so it doesn't crowd out the English practice.

```python
L("luna", "Look! A red flower.", card=("RED\nក្រហម", RED)),
K("narr", "Red មានន័យថា ពណ៌ក្រហម។"),        # "Red means the color red."
*say_it("Red", prompt="Say: %s!"),           # the repeat prompt stays in English
L("narr", "What color is the sun?"),
K("narr", "តើព្រះអាទិត្យពណ៌អ្វី?"),           # the same question in Khmer
P(3.0),
```

- Put the **English word first** on cards, with the Khmer meaning on the second line.
- Captions show exactly what was said, so English and Khmer captions mix naturally.
- Explain each new word in Khmer once. After that, practise in English only.
- The badge text is `"YOUR TURN! ដល់វេនប្អូន"`. Override it with `UI = {...}` if needed.

## 6. Checks before publishing

- Have a native Khmer speaker read every Khmer line and card. Check spelling (especially subscripts), naturalness and politeness level.
- Listen to the Khmer voices at normal speed. If one sounds rushed, lower its speed in `VOICES_KM` or give that line a `rate` override.
- Watch for English words inside Khmer lines, like "Red មានន័យថា…". The Khmer voice pronounces them with an accent. That's acceptable, but you can instead let the English character say the word and have the narrator give only the Khmer meaning.
