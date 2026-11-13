"""Narration and guide dialogue (TEMPLATE: replace every sample line after the research brief is approved).
L(key, Khmer, English, who, src).  who = "nar" (adult narrator), "elder" (the fictional elderly survivor / witness)
or "youth" (the fictional grandchild who asks).  Numbers use Khmer digits; khnum.speak() turns them into words.
Every factual narrator line carries src= with codes from docs/research_brief.md.  The elder's and youth's lines are
fiction: a composite family story built only from experiences the sources describe as common.
Keep each line to one idea and under ~170 Khmer characters; split lines that contain several years (see
references/gotchas.md)."""

N = {}
WHO = {}
SRC = {}
VOICES = {
    "nar": dict(label_en="", label_km="",
                design="A warm, calm Cambodian man in his forties, documentary narrator, clear deep voice, measured "
                       "unhurried pace",
                sample="នៅឆ្នាំ ១៨៦៣ ទឹកដីកម្ពុជា បានចូលទៅក្រោម អាណាព្យាបាល របស់បារាំង អស់រយៈពេល ៩០ ឆ្នាំ។"),
    "elder": dict(label_en="YEAY SOPHAL: ", label_km="យាយ សុផល៖ ",
                  design="An elderly Cambodian grandmother in her late sixties, soft warm slightly husky voice, "
                         "gentle and slow, speaking quietly with deep feeling, natural unhurried pace",
                  sample="ចៅ អើយ យាយ នឹង ប្រាប់ ចៅ នូវ រឿង ដែល យាយ មិន ដែល ភ្លេច។ ពេលនោះ យាយ អាយុ ដប់ប្រាំមួយ ឆ្នាំ។"),
    "youth": dict(label_en="MALIS: ", label_km="ម្លិះ៖ ",
                  design="A Cambodian teenage girl of about fifteen, clear bright young female voice, gentle, curious "
                         "and respectful, natural unhurried pace",
                  sample="យាយ! ហេតុអ្វី បាន ជា យើង មក ទីនេះ រៀងរាល់ ឆ្នាំ? ចៅ ចង់ ដឹង រឿង របស់ យាយ។"),
}


def L(key, km, en, who="nar", src=""):
    N[key] = (km, en)
    WHO[key] = who
    SRC[key] = src
    return key


def E(key, km, en):
    return L(key, km, en, "elder", "fiction (composite survivor)")


def Yo(key, km, en):
    return L(key, km, en, "youth", "fiction (guide)")


# ---------------------------------------------------------------- OPENING (sample)
Yo("m0", "យាយ ហេតុអ្វី បាន ជា យើង មក ទីនេះ រៀងរាល់ ឆ្នាំ?",
   "Grandma, why do we come here every year?")
E("s0", "ដើម្បី ចងចាំ ចៅ។ ថ្ងៃនេះ យាយ នឹង ប្រាប់ ចៅ នូវ អ្វី ដែល យាយ បាន ឆ្លងកាត់។",
  "To remember, my child. Today I will tell you what I lived through.")
L("o1", "យាយ សុផល និង ម្លិះ ជា តួអង្គ ប្រឌិត ដែល ផ្សំ ចេញពី រឿងរ៉ាវ របស់ អ្នករស់រានមានជីវិត ជាច្រើន។",
  "Yeay Sophal and Malis are fictional characters, drawn from the stories of many survivors.")

# ---------------------------------------------------------------- CHAPTER 1 (sample: replace with researched lines)
Yo("q1", "យាយ រឿង នេះ ចាប់ផ្ដើម យ៉ាង ដូចម្ដេច?", "Grandma, how did it begin?")
L("a1", "នេះ ជា ឃ្លា គំរូ។ ជំនួស វា ដោយ ការពិត ដែល មាន ប្រភព ពីរ បញ្ជាក់ ក្នុង សេចក្ដីសង្ខេប ស្រាវជ្រាវ។",
  "This is a sample line. Replace it with a fact confirmed by two sources in the research brief.", src="TODO")
E("s1", "យាយ នៅ ចាំ ផ្លូវ ដែល ពោរពេញ ដោយ មនុស្ស។ ម្ដាយ កាន់ ដៃ ប្អូន យាយ ជាប់។",
  "I still remember the road full of people. Mother held my brother's hand tight.")

# ---------------------------------------------------------------- CLOSING (sample)
Yo("m10", "ចៅ នឹង ចងចាំ យាយ។", "I will remember, Grandma.")
E("s10", "ចងចាំ ចៅ ដើម្បី កុំ ឲ្យ រឿង នេះ កើត ឡើង ម្ដង ទៀត។", "Remember, my child, so that it never happens again.")
L("z1", "ខ្សែភាពយន្ត នេះ សូម ឧទ្ទិស ដល់ អ្នក ដែល បាន បាត់បង់ ជីវិត និង អ្នក ដែល នៅ រស់ ហើយ នៅ តែ ចងចាំ ពួកគេ។",
  "This film is dedicated to all who died, and to all who survived and carry their memory.")
