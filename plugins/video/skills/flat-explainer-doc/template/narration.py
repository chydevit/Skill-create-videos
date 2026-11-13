"""Narration: L(key, Khmer, English) for the narrator, T(key, ...) for the on-screen guide (Dara).
Write numbers with Khmer digits; khnum.speak() turns them into words for the voice.
Explainer rhythm: ONE idea per line, 8-20 words, a question or a twist every few lines, a picture change on almost
every line.  Every factual line must trace to docs/fact_sheet.md.

SAMPLE CONTENT (the Human Era) - replace it with your film.  Khmer needs native-speaker review."""

N = {}
WHO = {}

VOICES = {
    "nar": dict(label_en="", label_km="",
                design="A warm, friendly Cambodian man in his thirties, curious science-explainer narrator, clear "
                       "bright voice, lively but unhurried pace, smiling tone",
                sample="ស្រមៃមើល៍ ពិភពលោកកាលពីដប់ពាន់ឆ្នាំមុន។ គ្មានទីក្រុង គ្មានផ្លូវ មានតែភ្លើង និងមនុស្ស។"),
    "dara": dict(label_en="DARA: ", label_km="ដារ៉ា៖ ",
                 design="A bright, curious Cambodian teenage boy about fourteen, clear friendly youthful voice, "
                        "playful",
                 sample="សួស្តី! ខ្ញុំឈ្មោះ ដារ៉ា។ តោះ ទៅមើលអតីតកាលជាមួយគ្នា!"),
}
GUIDE = "dara"


def L(key, km, en, who="nar"):
    N[key] = (km, en)
    WHO[key] = who
    return key


def T(key, km, en):
    return L(key, km, en, GUIDE)


# ---------------------------------------------------------------- COLD OPEN
L("o1", "អស់រយៈពេលដ៏យូរនៃប្រវត្តិសាស្ត្រមនុស្សជាតិ មនុស្សរស់នៅជាក្រុមតូចៗ ជុំវិញភ្លើងបែបនេះ។",
  "For most of human history, people lived in small groups, around fires like this one.")
T("t1", "ប៉ុន្តែ តើយើងរាប់ពេលវេលាដ៏យូរនោះ ដោយរបៀបណា?",
  "But how do we even count all that time?")

# ---------------------------------------------------------------- 1 COUNTING YEARS  [fact sheet §1]
L("a1", "ប្រតិទិនភាគច្រើនសព្វថ្ងៃ រាប់ចាប់ពីឆ្នាំទី ១ ដែលមានប្រហែល ២០០០ ឆ្នាំមុន។",
  "Most calendars today count from Year 1, about two thousand years ago.")
L("a2", "អ្វីៗដែលកើតឡើងមុននោះ ត្រូវរាប់ថយក្រោយ ជាឆ្នាំមុនគ្រិស្តសករាជ។",
  "Everything earlier has to be counted backwards, as years BCE.")
L("a3", "នៅឆ្នាំ ១៩៩៣ អ្នកវិទ្យាសាស្ត្រ ឆេសារ៉េ អេមីលីយ៉ានី បានស្នើដំណោះស្រាយងាយមួយ៖ បូកបន្ថែម ១០០០០ ឆ្នាំ។",
  "In 1993, the scientist Cesare Emiliani suggested a simple fix: add ten thousand years.")
L("a4", "ដូច្នេះ ឆ្នាំ ២០២៦ នេះ ក្លាយជាឆ្នាំ ១២០២៦ នៃសករាជមនុស្សជាតិ។",
  "So this year, 2026, becomes the year 12,026 of the Human Era.")

# ---------------------------------------------------------------- 2 THE FIRST VILLAGES  [fact sheet §2]
L("a5", "ឆ្នាំទី ១ នៃសករាជនេះ ស្ថិតនៅជិតចុងយុគទឹកកកចុងក្រោយ ពេលដែលមនុស្សនៅកន្លែងខ្លះ ចាប់ផ្ដើមសាងសង់ភូមិ និងវិមានដំបូងៗ។",
  "Year 1 of this era falls near the end of the last Ice Age, when people in some places began building the "
  "first villages and monuments.")
L("a6", "កន្លែងដូចជា គោបេគ្លី តេប៉េ នៅប្រទេសទួរគីបច្ចុប្បន្ន មានអាយុជាង ១១០០០ ឆ្នាំ។",
  "Places like Göbekli Tepe, in present-day Türkiye, are more than eleven thousand years old.")
L("a7", "បើរាប់បែបនេះ រឿងរ៉ាវទាំងមូលនៃកសិកម្ម ភូមិ និងទីក្រុង ស្ថិតនៅក្នុងប្រតិទិនតែមួយ។",
  "Counted this way, the whole story of farming, villages and cities fits inside one calendar.")
T("t2", "ដូច្នេះ សូមស្វាគមន៍មកកាន់ឆ្នាំ ១២០២៦!",
  "So, welcome to the year 12,026!")
