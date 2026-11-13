"""Narration and guide dialogue for 'Democratic Kampuchea 1975-1979: We Remember' (កម្ពុជាប្រជាធិបតេយ្យ ១៩៧៥–១៩៧៩).
L(key, Khmer, English, who, src).  who = "nar" (adult narrator), "sophal" (Yeay Sophal, a fictional elderly survivor)
or "malis" (Malis, her fictional teenage granddaughter).
Numbers use Khmer digits; khnum.speak() turns them into words for the voice.
Every factual line carries a source tag that points to docs/research_brief.md (codes such as E313, E465, DCC, LOC).
Sophal's and Malis's lines are fiction: a composite family story built only from experiences the sources describe as
common (evacuation, separation, mobile units, an educated parent taken away, the walk home in 1979).
Approved 2026-10-25: death toll 'about 1.5 to 2 million, one in five' (ECCC E465 para 297); three voices; no S-21
portraits; neutral wording for 7 January 1979.  Single-source details are left out."""

N = {}
WHO = {}
SRC = {}
VOICES = {
    "nar": dict(label_en="", label_km="",
                design="A warm, calm Cambodian man in his forties, documentary narrator, clear deep voice, measured "
                       "unhurried pace",
                sample="នៅឆ្នាំ ១៨៦៣ ទឹកដីកម្ពុជា បានចូលទៅក្រោម អាណាព្យាបាល របស់បារាំង អស់រយៈពេល ៩០ ឆ្នាំ។"),
    "sophal": dict(label_en="YEAY SOPHAL: ", label_km="យាយ សុផល៖ ",
                   design="An elderly Cambodian grandmother in her late sixties, soft warm slightly husky voice, "
                          "gentle and slow, speaking quietly with deep feeling, natural unhurried pace",
                   sample="ចៅ អើយ យាយ នឹង ប្រាប់ ចៅ នូវ រឿង ដែល យាយ មិន ដែល ភ្លេច។ ពេលនោះ យាយ អាយុ ដប់ប្រាំមួយ ឆ្នាំ។"),
    "malis": dict(label_en="MALIS: ", label_km="ម្លិះ៖ ",
                  design="A Cambodian teenage girl of about fifteen, clear bright young female voice, gentle, curious "
                         "and respectful, natural unhurried pace",
                  sample="យាយ! ហេតុអ្វី បាន ជា យើង មក ទីនេះ រៀងរាល់ ឆ្នាំ? ចៅ ចង់ ដឹង រឿង របស់ យាយ។"),
}


def L(key, km, en, who="nar", src=""):
    N[key] = (km, en)
    WHO[key] = who
    SRC[key] = src
    return key


def Y(key, km, en):
    return L(key, km, en, "sophal", "fiction (composite survivor)")


def M(key, km, en):
    return L(key, km, en, "malis", "fiction (guide)")


# ---------------------------------------------------------------- OPENING (0:00 - 0:45)
M("m0", "យាយ ហេតុអ្វី បាន ជា យើង មក ទីនេះ រៀងរាល់ ឆ្នាំ?",
  "Grandma, why do we come here every year?")
Y("s0", "ដើម្បី ចងចាំ ចៅ។ ថ្ងៃនេះ យាយ នឹង ប្រាប់ ចៅ នូវ អ្វី ដែល យាយ បាន ឆ្លងកាត់។",
  "To remember, my child. Today I will tell you what I lived through.")
L("o1", "យាយ សុផល និង ម្លិះ ជា តួអង្គ ប្រឌិត ដែល ផ្សំ ចេញពី រឿងរ៉ាវ របស់ អ្នករស់រានមានជីវិត ជាច្រើន។",
  "Yeay Sophal and Malis are fictional characters, drawn from the stories of many survivors.")
L("o2", "ពីថ្ងៃទី ១៧ ខែមេសា ឆ្នាំ ១៩៧៥ ដល់ ថ្ងៃទី ៦ ខែមករា ឆ្នាំ ១៩៧៩ កម្ពុជា ស្ថិត ក្រោម របប ខ្មែរក្រហម អស់ រយៈពេល ៣ ឆ្នាំ ៨ ខែ ២០ ថ្ងៃ។",
  "From the 17th of April 1975 to the 6th of January 1979, Cambodia lived under the Khmer Rouge: "
  "three years, eight months and twenty days.", src="ECCC-TL; E313 fn 1557; DCC")

# ---------------------------------------------------------------- 1 APRIL 17, 1975 (0:45 - 2:00)
M("q1", "យាយ នៅ ថ្ងៃទី ១៧ មេសា ឆ្នាំ ១៩៧៥ យាយ នៅ ឯណា?",
  "Grandma, where were you on the 17th of April 1975?")
Y("s1", "យាយ អាយុ ១៦ ឆ្នាំ។ យាយ រស់ នៅ ភ្នំពេញ ជាមួយ ឪពុក ដែល ជា គ្រូបង្រៀន ម្ដាយ ដែល លក់ ក្រណាត់ នៅ ផ្សារ និង ប្អូនប្រុស តូច ឈ្មោះ វុទ្ធី។",
  "I was sixteen. I lived in Phnom Penh with my father, a teacher, my mother, who sold cloth at the market, "
  "and my little brother, Vuthy.")
L("a1", "ក្រោយ សង្គ្រាមស៊ីវិល ប្រាំ ឆ្នាំ នៅ ព្រឹក ថ្ងៃទី ១៧ ខែមេសា ឆ្នាំ ១៩៧៥ កងកម្លាំង ខ្មែរក្រហម បាន ចូល ភ្នំពេញ ពី គ្រប់ ទិសទី។",
  "After five years of civil war, on the morning of the 17th of April 1975, Khmer Rouge forces entered Phnom Penh "
  "from every direction.", src="E313 paras 460-463; DCC p.13; PON")
L("a2", "ទាហាន ជាច្រើន នៅ ក្មេង ណាស់ ហើយ ស្លៀកពាក់ ពណ៌ខ្មៅ។ ប្រជាជន នាំគ្នា ចេញ មក គ្រវី ក្រណាត់ស ដោយ គិត ថា សង្គ្រាម បាន បញ្ចប់ ហើយ។ អ្នក ខ្លះ ទៀត លាក់ខ្លួន ក្នុង ផ្ទះ ដោយ ភ័យខ្លាច។",
  "Many of the soldiers were very young, dressed in black. Crowds came out waving white cloths, believing the war "
  "was over. Others hid in their homes, afraid.", src="E313 paras 463-465; DCC p.13")
L("a3", "ប៉ុន្មាន ម៉ោង ក្រោយមក ទាហាន បាន បាញ់ ទៅលើ អាកាស ហើយ បញ្ជា ឲ្យ មនុស្ស គ្រប់គ្នា ចាកចេញ ពី ទីក្រុង។",
  "Within hours, the soldiers fired into the air and ordered everyone to leave the city.",
  src="DCC p.13, p.16; E313 paras 464-466")
L("a4", "គេ ប្រាប់ ថា អាមេរិក នឹង ទម្លាក់ គ្រាប់បែក ហើយ ថា ប្រជាជន អាច ត្រឡប់ មក វិញ ក្នុង រយៈពេល ពីរ ឬ បី ថ្ងៃ។",
  "They said the Americans would bomb the city, and that people could come back in two or three days.",
  src="DCC p.15; E313 paras 465-469")
Y("s2", "ឪពុក មិន ចាក់សោ ទ្វារ ទេ។ គាត់ ថា យើង នឹង ត្រឡប់ មក វិញ ឆាប់ៗ។ គាត់ យក តែ វ៉ែនតា និង សៀវភៅ មួយ ក្បាល ប៉ុណ្ណោះ។",
  "Father didn't lock the door. He said we would be back soon. He took only his glasses and one book.")

# ---------------------------------------------------------------- 2 EMPTYING THE CITIES (2:00 - 3:30)
M("q2", "មនុស្ស ប៉ុន្មាន នាក់ ដែល ត្រូវ ចាកចេញ?",
  "How many people had to leave?")
L("b1", "ក្នុង រយៈពេល ប្រហែល មួយ សប្ដាហ៍ មនុស្ស យ៉ាងតិច ពីរ លាន នាក់ ត្រូវ បាន បណ្ដេញ ចេញ ពី ភ្នំពេញ។",
  "In about one week, at least two million people were driven out of Phnom Penh.",
  src="E313 paras 518-520; DCC p.13")
L("b2", "មន្ទីរពេទ្យ ត្រូវ បាន ជម្លៀស ឲ្យ ទទេ។ អ្នកជំងឺ មនុស្សចាស់ ស្ត្រីមានផ្ទៃពោះ និង ព្រះសង្ឃ គ្មាន ការលើកលែង ឡើយ។",
  "Hospitals were emptied. The sick, the old, pregnant women and monks: there were no exceptions.",
  src="E313 para 476; DCC p.16")
L("b3", "បាត់ដំបង កំពង់ចាម តាកែវ និង ទីក្រុង ផ្សេងទៀត ក៏ ត្រូវ បាន ជម្លៀស ដែរ។",
  "Battambang, Kampong Cham, Takeo and other towns were emptied too.", src="E313 para 170; DCC p.13")
L("b4", "អ្នកធាក់ស៊ីក្លូ ម្នាក់ ឈ្មោះ ស៊ឹម សុត បាន រំឭក ថា៖ «នៅលើ ផ្លូវ ដ៏ ណែនណាន់តាន់តាប់ ខ្ញុំ ឮ សូរសំឡេង មនុស្សម្នា ស្រែក ហៅ រក ឪពុកម្ដាយ និង បងប្អូន និង សម្រែក ក្មេងៗ យំ ទារ រក បាយ»។",
  "A cyclo driver, Sim Soth, remembered: \"On the crowded road, I heard people calling for their parents and "
  "relatives, and hungry children crying for rice.\"", src="Sim Soth, testimony in DCC p.16 (Khmer ed. p.18)")
L("b5", "មនុស្ស រាប់ពាន់ នាក់ បាន ស្លាប់ តាម ផ្លូវ ជាពិសេស កូនក្មេង មនុស្សចាស់ និង អ្នកជំងឺ។ គ្រួសារ ជាច្រើន បាន បែកគ្នា ក្នុង ហ្វូងមនុស្ស។",
  "Thousands died on the roads, above all the very young, the old and the sick. Many families lost each other in "
  "the crowds.", src="E313 paras 467, 521; DCC p.16")
Y("s3", "យើង ដើរ អស់ ជាច្រើន ថ្ងៃ។ ម្ដាយ ចង ដៃ វុទ្ធី ជាប់ នឹង ក្រមា របស់ គាត់ ដើម្បី កុំ ឲ្យ បាត់ គ្នា។",
  "We walked for many days. Mother tied Vuthy's wrist to her krama, so we would not lose each other.")
L("b6", "នៅ តាម ភូមិ អ្នក ជម្លៀស ត្រូវ បាន គេ ហៅ ថា «ប្រជាជនថ្មី» ឬ «ប្រជាជន ១៧ មេសា»។ អ្នក ដែល រស់ នៅ ក្រោម ខ្មែរក្រហម ពីមុន ជា «ប្រជាជនមូលដ្ឋាន»។ ប្រជាជនថ្មី ត្រូវ បាន គេ ប្រព្រឹត្ត យ៉ាង ធ្ងន់ធ្ងរ ជាង។",
  "In the villages, the evacuees were called \"new people\" or \"17 April people\". Those who had lived under the "
  "Khmer Rouge before were \"base people\". The new people were treated far more harshly.",
  src="DCC pp.29-30; LOC 29; E313 para 169")
L("b7", "ចាប់ពី ចុង ឆ្នាំ ១៩៧៥ មនុស្ស ជាច្រើន ត្រូវ បាន ផ្លាស់ទី ម្ដង ទៀត ភាគច្រើន ទៅ ភូមិភាគពាយ័ព្យ។",
  "From late 1975, many were moved again, mostly to the northwest.", src="E313 paras 575-580; DCC p.34")

# ---------------------------------------------------------------- 3 "YEAR ZERO" (3:30 - 5:00)
M("q3", "ពួកគេ ចង់ បាន អ្វី?", "What did they want?")
L("c1", "មេដឹកនាំ ថ្មី ចង់ កសាង សង្គម កសិករ មួយ ដែល គ្មាន វណ្ណៈ ដោយ ចាប់ផ្ដើម ពី សូន្យ ឡើងវិញ។ ក្រោយមក គេ ហៅ បដិវត្តន៍ នេះ ថា «ឆ្នាំសូន្យ»។",
  "The new rulers wanted a society of peasants without classes, starting again from nothing. "
  "Their revolution was later called \"Year Zero\".", src="DCC p.15; LOC 27; ERS p.8; PON (title)")
L("c2", "លុយ ត្រូវ បាន លុបចោល។ ក្រដាសប្រាក់ ហោះ ពេញ ផ្លូវ ដែល ស្ងាត់ ទទេ។ ផ្សារ ត្រូវ បាន បិទ។",
  "Money was abolished. Banknotes blew through the empty streets. Markets were closed.",
  src="DCC p.2; LOC 29, 61; E313 para 494")
L("c3", "សាលារៀន និង សាកលវិទ្យាល័យ ត្រូវ បាន បិទ។ សៀវភៅ ត្រូវ បាន គេ បោះបង់ចោល។",
  "Schools and universities were shut, and books were left behind.", src="DCC pp.2, 35; LOC 29")
L("c4", "វត្ត វិហារ ឥស្លាម និង ព្រះវិហារ គ្រិស្ត ត្រូវ បាន បិទ ឬ ប្រើ ជា ឃ្លាំង និង កន្លែង ឃុំឃាំង។ ព្រះសង្ឃ ត្រូវ បាន បង្ខំ ឲ្យ សឹក។",
  "Pagodas, mosques and churches were closed, or used as storehouses and prisons. Monks were forced to leave the "
  "monkhood.", src="DCC p.2; LOC 29; E465 summary paras 15, 35-36")
L("c5", "កម្មសិទ្ធិ ឯកជន ត្រូវ បាន លុបចោល។ ដី ឧបករណ៍ គោក្របី សូម្បីតែ ឆ្នាំង បាយ ក៏ ក្លាយ ជា របស់ សមូហភាព។",
  "Private property was abolished. Land, tools, cattle, even cooking pots, belonged to the collective.",
  src="DCC pp.2, 25; LOC 29")
L("c6", "អ្វីៗ ទាំងអស់ ស្ថិត ក្រោម «អង្គការ» ដែល ជា ថ្នាក់ដឹកនាំ សម្ងាត់ របស់ បក្សកុម្មុយនិស្តកម្ពុជា។ បក្ស មិន បាន បង្ហាញ ខ្លួន ជា សាធារណៈ រហូត ដល់ ខែកញ្ញា ឆ្នាំ ១៩៧៧។",
  "Everything was ruled by \"Angkar\", the Organisation: the hidden leadership of the Communist Party of Kampuchea. "
  "The party did not reveal itself in public until September 1977.", src="DCC pp.2, 17, 22; E313 paras 221-222; LOC 32")
Y("s4", "គេ ប្រាប់ យើង ថា អង្គការ ជា ឪពុកម្ដាយ របស់ យើង។ ហើយ គេ និយាយ ថា ទុក ក៏ មិន ចំណេញ ដកចេញ ក៏ មិន ខាត។",
  "They told us Angkar was our mother and father. And they said: to keep you is no gain, to lose you is no loss.")

# ---------------------------------------------------------------- 4 LIFE IN THE COOPERATIVES (5:00 - 6:30)
M("q4", "ជីវិត ប្រចាំថ្ងៃ យ៉ាង ម៉េច ដែរ យាយ?", "What was daily life like, Grandma?")
L("d1", "ប្រទេស ទាំងមូល ត្រូវ បាន រៀបចំ ជា សហករណ៍។ មនុស្ស ធ្វើការ ដប់ពីរ ម៉ោង ក្នុង មួយ ថ្ងៃ ឬ ច្រើន ជាង នេះ ពេលខ្លះ ដល់ យប់ នៅ វាលស្រែ ប្រឡាយ និង ទំនប់។",
  "The whole country was organised into cooperatives. People worked twelve hours a day or more, sometimes into the "
  "night, in rice fields, on canals and on dams.", src="DCC pp.29, 37-38; E465 summary paras 14-19; LOC 29")
L("d2", "ផែនការ បួន ឆ្នាំ ១៩៧៧ ដល់ ១៩៨០ ទាមទារ ស្រូវ បី តោន ក្នុង មួយ ហិកតា ខណៈ ដែល អង្ករ នៅតែ ត្រូវ បាន នាំចេញ ទៅ ក្រៅប្រទេស។",
  "The Four-Year Plan for 1977 to 1980 demanded three tonnes of rice per hectare, while rice was still sent abroad.",
  src="DCC p.25; E465 para 1008; E313 para 604; LOC 61")
L("d3", "មនុស្ស ហូប បាយ រួម គ្នា នៅ រោងបាយ សហករណ៍។ របប ផ្លូវការ គឺ អង្ករ ប្រហែល ពីរ កំប៉ុង ក្នុង មួយ ថ្ងៃ ប៉ុន្តែ មនុស្ស ភាគច្រើន ទទួល បាន តិច ជាង នេះ ឆ្ងាយ ជាញឹកញាប់ គ្រាន់តែ បបរ រាវ។",
  "Meals were eaten together in communal halls. The official ration was about two tins of rice a day, but most "
  "people got far less, often only thin, watery porridge.", src="E465 paras 940-941, 1008-1009; DCC p.27; LOC 61")
L("d4", "ការអត់ឃ្លាន ជំងឺ និង ការហត់នឿយ បាន ឆក់ យក ជីវិត មនុស្ស ជាច្រើន។ អ្នក ដែល រក អាហារ ដោយ ខ្លួនឯង ត្រូវ បាន ដាក់ ទោស។",
  "Hunger, disease and exhaustion took many lives. Those caught searching for food were punished.",
  src="DCC pp.26-27, 38; E465 summary paras 15-17")
L("d5", "គ្រួសារ ត្រូវ បាន បំបែក តាម អាយុ និង ភេទ។ កុមារ ត្រូវ បាន គេ បង្រៀន ថា អង្គការ ជា ឪពុកម្ដាយ របស់ ពួកគេ ហើយ ខ្លះ ត្រូវ បាន ប្រើ ឲ្យ ឃ្លាំមើល មនុស្សចាស់ សូម្បីតែ គ្រួសារ របស់ ខ្លួន។",
  "Families were split by age and sex. Children were taught that Angkar was their parent, and some were made to "
  "watch the adults, even their own families.", src="DCC pp.25, 35, 38; LOC 29")
L("d6", "គូស្វាមីភរិយា ត្រូវ បាន រៀបការ ជា ក្រុម ដោយ កម្មាភិបាល ជា អ្នក ជ្រើសរើស។ ក្រោយមក តុលាការ បាន រក ឃើញ ថា ការបង្ខំ ឲ្យ រៀបការ នេះ ជា ឧក្រិដ្ឋកម្ម ប្រឆាំង មនុស្សជាតិ។",
  "Couples were married in group ceremonies, chosen by the cadres. The tribunal later found these forced marriages "
  "to be a crime against humanity.", src="E465 summary paras 39-41; DCC pp.31-34")
Y("s5", "យាយ ត្រូវ គេ បញ្ជូន ទៅ កងចល័ត ដើម្បី ជីក ប្រឡាយ។ វុទ្ធី នៅ ក្នុង កងកុមារ។ យាយ ឃើញ ប្អូន ម្ដង ក្នុង មួយ ខែ ឬ តិច ជាង នេះ។",
  "I was sent to a mobile work unit to dig canals. Vuthy was put in a children's unit. I saw him once a month, "
  "or less.")

# ---------------------------------------------------------------- 5 THE LEADERS AND THE STATE (6:30 - 7:45)
M("q5", "តើ នរណា ជា អ្នក ដឹកនាំ?", "Who was in charge?")
L("e1", "នៅ ថ្ងៃទី ៥ ខែមករា ឆ្នាំ ១៩៧៦ រដ្ឋធម្មនុញ្ញ ថ្មី បាន ដាក់ ឈ្មោះ ប្រទេស ថា កម្ពុជាប្រជាធិបតេយ្យ។ វា មិន បាន និយាយ ពី បក្ស ដែល កាន់ អំណាច ទាល់តែ សោះ។",
  "On the 5th of January 1976, a new constitution renamed the country Democratic Kampuchea. It never mentioned "
  "the party that ruled it.", src="DCC pp.19-20; LOC 31; E313 para 233")
L("e2a", "សម្ដេច នរោត្តម សីហនុ បាន យាង ត្រឡប់ មក វិញ នៅ ខែកញ្ញា ឆ្នាំ ១៩៧៥ ជា ប្រមុខរដ្ឋ ប៉ុន្តែ គ្មាន អំណាច ទេ។",
  "Prince Norodom Sihanouk had returned in September 1975 as head of state, but without power.",
  src="E313 paras 231, 758; DCC p.18")
L("e2b", "នៅ ខែមេសា ឆ្នាំ ១៩៧៦ ទ្រង់ បាន លាលែង ពី តំណែង។ ទ្រង់ ត្រូវ បាន ឃុំ ក្នុង ព្រះបរមរាជវាំង រហូត ដល់ ខែមករា ឆ្នាំ ១៩៧៩។",
  "In April 1976 he resigned, and was kept under guard in the palace until January 1979.",
  src="E313 para 761; DCC pp.18, 21; LOC 31")
L("e3", "អំណាច ពិត ស្ថិត នៅ ក្នុង គណៈកម្មាធិការ អចិន្ត្រៃយ៍ របស់ បក្ស។ ប៉ុល ពត លេខាធិការ បក្ស ក្លាយ ជា នាយករដ្ឋមន្ត្រី។ នួន ជា អនុលេខាធិការ ត្រូវ បាន គេ ស្គាល់ ថា «បងធំទីពីរ»។",
  "Real power lay with the party's Standing Committee. Pol Pot, the party Secretary, became Prime Minister. "
  "Nuon Chea, his deputy, was known as \"Brother Number Two\".", src="E313 paras 203, 228, 235, 312; DCC pp.17-22")
L("e4", "ខៀវ សំផន ក្លាយ ជា ប្រមុខរដ្ឋ។ អៀង សារី ទទួល បន្ទុក ការបរទេស សុន សេន ទទួល បន្ទុក ការពារជាតិ ហើយ តាម៉ុក ជា លេខា ភូមិភាគនិរតី។",
  "Khieu Samphan became head of state. Ieng Sary ran foreign affairs, Son Sen defence, and Ta Mok led the Southwest "
  "Zone.", src="E313 paras 235-236; DCC p.22 & note 14; LOC 31")
L("e5", "ប្រទេស ចិន ជា សម្ព័ន្ធមិត្ត ដ៏ សំខាន់ ជាងគេ របស់ របប នេះ ដោយ ផ្ដល់ អាវុធ និង ទីប្រឹក្សា។",
  "China was the regime's main ally, sending weapons and advisers.", src="DCC pp.56-57; LOC 32, 61")

# ---------------------------------------------------------------- 6 TARGETED GROUPS (7:45 - 9:15)
M("q6", "ហេតុអ្វី បាន ជា ឪពុក យាយ ភ័យខ្លាច?", "Why was your father afraid?")
Y("s6", "ឪពុក ធ្លាប់ ជា គ្រូ។ គាត់ បោះ វ៉ែនតា ចោល ហើយ ប្រាប់ គេ ថា គាត់ ជា អ្នកធាក់ស៊ីក្លូ។",
  "Father had been a teacher. He threw away his glasses and told them he was a cyclo driver.")
L("f1", "របប នេះ ឃើញ សត្រូវ គ្រប់ ទីកន្លែង។ អតីត ទាហាន និង មន្ត្រី សាធារណរដ្ឋ ត្រូវ បាន តាមចាប់ ហើយ ជាច្រើន ត្រូវ បាន សម្លាប់។ គ្រូ វេជ្ជបណ្ឌិត និង អ្នក មាន ចំណេះ ស្ថិត ក្នុង គ្រោះថ្នាក់ ធំ។",
  "The regime saw enemies everywhere. Former soldiers and officials of the Republic were hunted, and many were "
  "killed. Teachers, doctors and educated people were in great danger.",
  src="E465 summary paras 37-38; DCC ch.8; E188 para 141")
L("f2", "មុន សង្គ្រាម កម្ពុជា មាន ព្រះសង្ឃ ប្រហែល ៦០,០០០ អង្គ។ ព្រះពុទ្ធសាសនា ត្រូវ បាន ហាមឃាត់ ហើយ វត្ត អារាម បាន នៅ ស្ងាត់។",
  "Before the war, Cambodia had about sixty thousand monks. Buddhism was banned, and the pagodas fell silent.",
  src="E465 para 263 (Harris); Cultural Survival; E465 summary paras 35-36; F76/1")
L("f3", "ជនជាតិ ចាម មូស្លីម ត្រូវ បាន ហាម មិន ឲ្យ ធ្វើ ពិធី បួងសួង និង និយាយ ភាសា របស់ ខ្លួន។ ក្រោយ ការបះបោរ នៅ ឆ្នាំ ១៩៧៥ សហគមន៍ របស់ ពួកគេ ត្រូវ បាន បំបែក ហើយ ជម្លៀស ឲ្យ នៅ ខ្ចាត់ខ្ចាយ។",
  "The Cham Muslims were forbidden to pray or to speak their language. After uprisings in 1975, their communities "
  "were broken up and scattered.", src="E465 summary paras 27-28; DCC ch.8")
L("f4", "ជនជាតិ វៀតណាម ប្រហែល ១៥០,០០០ នាក់ ត្រូវ បាន បណ្ដេញ ចេញ នៅ ឆ្នាំ ១៩៧៥។ អ្នក ដែល នៅ សល់ ក្រោយមក ត្រូវ បាន តាមចាប់ សម្លាប់។",
  "About one hundred and fifty thousand ethnic Vietnamese were expelled in 1975. Those who stayed were later hunted "
  "down.", src="E465 summary paras 31-32; KIE03; HEU01")
L("f5", "នៅ ឆ្នាំ ២០១៨ តុលាការ បាន រក ឃើញ ថា អំពើប្រល័យពូជសាសន៍ ត្រូវ បាន ប្រព្រឹត្ត ទៅលើ ជនជាតិ វៀតណាម និង ជនជាតិ ចាម។ សាលក្រម ចំពោះ ជនជាតិ វៀតណាម ត្រូវ បាន តម្កល់ ក្នុង សាលឧទ្ធរណ៍ នៅ ឆ្នាំ ២០២២។",
  "In 2018 the tribunal found that genocide was committed against the Vietnamese and the Cham. The finding on the "
  "Vietnamese was upheld on appeal in 2022.", src="E465 summary paras 30, 34, 71-72; F76/1")

# ---------------------------------------------------------------- 7 S-21 AND THE SECURITY SYSTEM (9:15 - 10:45)
M("q7", "យាយ អគារ នេះ ធ្លាប់ ជា សាលារៀន មែន ទេ?", "Grandma, this building was a school?")
L("g1", "មែន។ វិទ្យាល័យ ពញាយ៉ាត នៅ ភ្នំពេញ ត្រូវ បាន ប្ដូរ ទៅ ជា មន្ទីរសន្ដិសុខ ស-២១។",
  "Yes. Ponhea Yat High School in Phnom Penh became Security Office 21: S-21.",
  src="TSL; DCC ch.9; E188 para 135")
L("g2", "ប្រធាន មន្ទីរ នេះ គឺ កាំង ហ្កេកអ៊ាវ ហៅ ឌុច។",
  "Its chief was Kaing Guek Eav, known as Duch.", src="E188 para 112; DC-001")
L("g3", "មនុស្ស យ៉ាងតិច ១២,០០០ នាក់ ត្រូវ បាន ឃុំ នៅ ទីនេះ ប្រហែល ជា ច្រើន ជាង នេះ ទៅ ទៀត។ ភាគច្រើន ជា កម្មាភិបាល និង ទាហាន ខ្មែរក្រហម ដែល ត្រូវ គេ ចោទ ថា ក្បត់។ បុរស ស្ត្រី និង សូម្បី តែ កុមារ។",
  "At least twelve thousand people were held here, probably many more. Most were Khmer Rouge cadres and soldiers "
  "accused of betrayal. Men, women, and even children.", src="E188 paras 141, 340; TSL; DCC ch.9")
L("g4", "អ្នកទោស ត្រូវ បាន ថតរូប សួរចម្លើយ និង បង្ខំ ឲ្យ សារភាព។ ស្ទើរតែ គ្មាន នរណា ម្នាក់ រួចជីវិត ឡើយ។",
  "Prisoners were photographed, interrogated and forced to confess. Almost no one survived.",
  src="E188; DCC ch.9; TSL")
L("g5", "ជាច្រើន ត្រូវ បាន នាំ ទៅ ជើងឯក ចម្ងាយ ប្រហែល ១៥ គីឡូម៉ែត្រ ពី ទីក្រុង ហើយ ត្រូវ បាន សម្លាប់ នៅ ទីនោះ។",
  "Many were taken to Choeung Ek, about fifteen kilometres from the city, and killed there.",
  src="E188 paras 184-186; DCC ch.9")
L("g6", "មាន តែ មនុស្ស មួយ ក្ដាប់ តូច ប៉ុណ្ណោះ ដែល នៅ រស់ ក្នុង នោះ មាន វិចិត្រករ វ៉ាន់ ណាត ជាងម៉ាស៊ីន ជុំ ម៉ី វិចិត្រករ ប៊ូ ម៉េង និង កុមារ ពីរ បី នាក់ រួម ទាំង នង ចាន់ផល។",
  "Only a handful survived, among them the painter Vann Nath, the mechanic Chum Mey, the painter Bou Meng, and a "
  "few children, including Norng Chan Phal.", src="TSL; DCC ch.9; DC-001; RFA; E188")
L("g7", "នៅ ទូទាំង ប្រទេស មាន មន្ទីរ ឃុំឃាំង បែប នេះ ជិត ២០០ កន្លែង។",
  "Across the country there were nearly two hundred such prisons.", src="DC-MAP (196); E465 para 294 (at least 200)")
Y("s7", "នៅ យប់ មួយ គេ បាន ហៅ ឪពុក យាយ ទៅ «រៀនសូត្រ»។ គាត់ មិន ដែល ត្រឡប់ មក វិញ ទេ។",
  "One night, they called my father away \"to study\". He never came back.")

# ---------------------------------------------------------------- 8 PURGES WITHIN (10:45 - 11:45)
M("q8", "ពួកគេ ក៏ សម្លាប់ គ្នា ឯង ដែរ ឬ?", "They killed their own people too?")
L("h1", "មែន។ ចាប់ពី ឆ្នាំ ១៩៧៦ ថ្នាក់ដឹកនាំ បាន ស្វែងរក «ខ្មាំង ស៊ី ផ្ទៃក្នុង»។ រដ្ឋមន្ត្រី លេខា ភូមិភាគ និង កម្មាភិបាល រាប់ពាន់ នាក់ ត្រូវ បាន ចាប់ ខ្លួន ហើយ បញ្ជូន ទៅ ស-២១។",
  "Yes. From 1976 the leadership hunted for \"enemies burrowing from within\". Ministers, zone leaders and "
  "thousands of cadres were arrested and sent to S-21.", src="E465 paras 2068-2069; DCC ch.7; E188 para 141")
L("h2", "នៅ ឆ្នាំ ១៩៧៧ ការបោសសម្អាត បាន វាយ ប្រហារ ភូមិភាគឧត្តរ។ រដ្ឋមន្ត្រី ហ៊ូ នឹម ស្ថិត ក្នុង ចំណោម អ្នក ដែល ត្រូវ បាន សម្លាប់។",
  "In 1977 the purge swept through the North Zone. Minister Hu Nim was among those killed.",
  src="E465 paras 358, 2068-2069, 2300; DCC ch.7")
L("h3", "នៅ ឆ្នាំ ១៩៧៨ វា បាន ឈាន ដល់ ភូមិភាគបូព៌ា។ មេដឹកនាំ ភូមិភាគ គឺ សោ ភឹម បាន ធ្វើ អត្តឃាត។ ប្រជាជន ភូមិភាគបូព៌ា រាប់ម៉ឺន នាក់ បាន ស្លាប់ ហើយ ជាច្រើន ត្រូវ បាន ជម្លៀស ទៅ ភូមិភាគពាយ័ព្យ។",
  "In 1978 it reached the East Zone. Its leader, So Phim, took his own life. Tens of thousands of easterners died, "
  "and many were deported to the northwest.", src="E465 paras 2053, 2071-2072; DCC ch.7, ch.11")
L("h4", "អ្នក នៅ រស់ ចងចាំ ពួកគេ ថា ជា «អ្នក ពាក់ ក្រមា ខៀវ»។",
  "Survivors remember them as \"the blue scarf people\".", src="DC-EAST (2013); Kiernan via Uni Bonn")
L("h5", "មេបញ្ជាការ ភូមិភាគបូព៌ា មួយ ចំនួន បាន រត់ ភៀសខ្លួន ទៅ ប្រទេស វៀតណាម ក្នុង នោះ មាន ហេង សំរិន និង ហ៊ុន សែន។",
  "Some East Zone commanders fled to Vietnam, among them Heng Samrin and Hun Sen.",
  src="E465 para 1988 & fn to 292; DCC ch.11; Cambodia Daily")

# ---------------------------------------------------------------- 9 WAR AND COLLAPSE (11:45 - 13:00)
M("q9", "របប នេះ បាន បញ្ចប់ យ៉ាង ដូចម្ដេច?", "How did it end?")
L("i1", "ប៉ុន្មាន សប្ដាហ៍ ក្រោយ ឡើង កាន់ អំណាច របប នេះ បាន ប៉ះទង្គិច ជាមួយ វៀតណាម ពី រឿង កោះ។ នៅ ឆ្នាំ ១៩៧៧ កងទ័ព ខ្មែរក្រហម បាន វាយ ប្រហារ ភូមិ នានា ឆ្លង ព្រំដែន ហើយ វៀតណាម បាន វាយ តប វិញ។",
  "Within weeks of taking power, the regime clashed with Vietnam over disputed islands. In 1977 Khmer Rouge forces "
  "attacked villages across the border, and Vietnam struck back.", src="E465 paras 281-290; DCC ch.11; LOC 33")
L("i2", "នៅ ថ្ងៃទី ៣១ ខែធ្នូ ឆ្នាំ ១៩៧៧ កម្ពុជាប្រជាធិបតេយ្យ បាន ផ្ដាច់ ទំនាក់ទំនង ការទូត ជាមួយ វៀតណាម។",
  "On the 31st of December 1977, Democratic Kampuchea broke off relations with Vietnam.",
  src="E465 para 289; DCC ch.10")
L("i3", "នៅ ថ្ងៃទី ២ ខែធ្នូ ឆ្នាំ ១៩៧៨ ជនភៀសខ្លួន ខ្មែរ ដឹកនាំ ដោយ ហេង សំរិន បាន ប្រកាស បង្កើត រណសិរ្សសាមគ្គីសង្គ្រោះជាតិកម្ពុជា។",
  "On the 2nd of December 1978, Cambodian exiles led by Heng Samrin announced the Kampuchean United Front for "
  "National Salvation.", src="DCC fn 25; E465 para 293; LOC 75")
L("i4", "នៅ ចុង ខែធ្នូ កងទ័ព វៀតណាម និង កងកម្លាំង របស់ រណសិរ្ស បាន ចូល មក កម្ពុជា។ នៅ ថ្ងៃទី ៧ ខែមករា ឆ្នាំ ១៩៧៩ ពួកគេ បាន មក ដល់ ភ្នំពេញ។ របប នេះ បាន ដួលរលំ។",
  "In late December, Vietnamese forces and the Front's fighters crossed into Cambodia. On the 7th of January 1979, "
  "they reached Phnom Penh. The regime fell.", src="DCC ch.11; LOC 33; E465 para 293")
L("i5", "មេដឹកនាំ ខ្មែរក្រហម បាន ដកថយ ទៅ ព្រំដែន ថៃ ហើយ បន្ត ការប្រយុទ្ធ អស់ ជាច្រើន ឆ្នាំ។",
  "The Khmer Rouge leaders retreated to the Thai border, and fought on for years.", src="DCC ch.1, ch.11; P6")
Y("s8", "ពេល យាយ ឮ ថា ពួកគេ បាន រត់ ចោល យាយ មិន ដឹង ថា ត្រូវ សើច ឬ យំ ទេ។",
  "When I heard they had fled, I didn't know whether to laugh or cry.")

# ---------------------------------------------------------------- 10 AFTER THE DARKNESS (13:00 - 14:15)
M("q10", "យាយ បាន ជួប ម្ដាយ វិញ ទេ?", "Did you find your mother again?")
Y("s9", "យាយ ដើរ ត្រឡប់ ទៅ ភ្នំពេញ អស់ ជាច្រើន សប្ដាហ៍។ យាយ បាន ជួប ម្ដាយ និង វុទ្ធី វិញ។ ចំណែក ឪពុក យើង មិន ដែល រក ឃើញ ទេ។",
  "I walked for weeks to get back to Phnom Penh. I found my mother, and Vuthy. My father, we never found.")
L("j1", "នៅ ឆ្នាំ ១៩៧៩ អ្នក នៅ រស់ បាន ដើរ ឆ្លង កាត់ ប្រទេស ដើម្បី ស្វែងរក ផ្ទះ និង គ្រួសារ របស់ ខ្លួន។ ច្រើន នាក់ មិន ដែល រក ឃើញ ឡើយ។",
  "In 1979, survivors walked across the country, searching for their homes and families. Many never found them.",
  src="DCC ch.11; TSL")
L("j2", "ស-២១ ក្លាយ ជា សារមន្ទីរ ឧក្រិដ្ឋកម្ម ប្រល័យពូជសាសន៍ ទួលស្លែង ដែល បាន បើក ជូន សាធារណជន នៅ ឆ្នាំ ១៩៨០។",
  "S-21 became the Tuol Sleng Genocide Museum, which opened to the public in 1980.",
  src="TSL; DCC ch.9; DC-Cam classroom flyer")
L("j3", "ប៉ុល ពត បាន ស្លាប់ នៅ ឆ្នាំ ១៩៩៨ ដោយ មិន ដែល ត្រូវ បាន កាត់ទោស។",
  "Pol Pot died in 1998, never brought to trial.", src="Britannica; DC-Cam")
L("j4", "នៅ ឆ្នាំ ២០០៦ អង្គជំនុំជម្រះវិសាមញ្ញ ក្នុង តុលាការ កម្ពុជា ដែល ទទួល ការគាំទ្រ ពី អង្គការសហប្រជាជាតិ បាន ចាប់ផ្ដើម ការងារ។",
  "In 2006 a court backed by Cambodia and the United Nations, the Extraordinary Chambers in the Courts of Cambodia, "
  "began its work.", src="UN Treaty Series 2329; ECCC at a Glance")
L("j5", "តុលាការ នេះ បាន ផ្ដន្ទាទោស មនុស្ស បី នាក់ គឺ ឌុច នួន ជា និង ខៀវ សំផន ឲ្យ ជាប់ ពន្ធនាគារ អស់ មួយ ជីវិត។",
  "It convicted three people, Duch, Nuon Chea and Khieu Samphan, and sentenced each of them to life in prison.",
  src="F28; E313; SCC16; E465; F76/1; ECCC-CR")
L("j6", "អ្នក ស្រាវជ្រាវ ប៉ាន់ស្មាន ថា មនុស្ស ប្រហែល មួយ លាន កន្លះ ទៅ ពីរ លាន នាក់ គឺ ប្រហែល មួយ ភាគ ប្រាំ នៃ ប្រជាជន កម្ពុជា បាន ស្លាប់ ក្រោម របប នេះ ដោយ ការប្រហារជីវិត ការអត់ឃ្លាន ការងារ ហួសកម្លាំង និង ជំងឺ។",
  "Researchers estimate that about one and a half to two million people, roughly one in every five Cambodians, "
  "died under the regime: executed, or killed by hunger, overwork and disease.",
  src="E465 para 297; KIE03; HEU15; TK09")
L("j7", "តួលេខ ទាំងនេះ មក ពី វិធីសាស្ត្រ ផ្សេងៗ គ្នា៖ ការគូរ ផែនទី រណ្ដៅ សព ការសិក្សា ប្រជាសាស្ត្រ និង ការងារ របស់ តុលាការ។ វា នៅតែ ជា ការប៉ាន់ស្មាន។",
  "These numbers come from different methods: mapping mass graves, studying the population, and the work of the "
  "tribunal. They remain estimates.", src="DC-MAP; HEU01; HEU15; TK09; E465 para 297")
L("j8", "រៀងរាល់ ឆ្នាំ នៅ ថ្ងៃទី ២០ ខែឧសភា ប្រជាជន កម្ពុជា ជួបជុំ គ្នា ក្នុង ទិវាជាតិ នៃ ការចងចាំ។",
  "Every year on the 20th of May, Cambodians gather for the National Day of Remembrance.",
  src="SD19 (14 Feb 2018); VOA20")

# ---------------------------------------------------------------- CLOSING (14:15 - 15:00)
M("m10", "ចៅ នឹង ចងចាំ យាយ។", "I will remember, Grandma.")
Y("s10", "ចងចាំ ចៅ ដើម្បី កុំ ឲ្យ រឿង នេះ កើត ឡើង ម្ដង ទៀត។",
  "Remember, my child, so that it never happens again.")
L("z1", "ខ្សែភាពយន្ត នេះ សូម ឧទ្ទិស ដល់ អ្នក ដែល បាន បាត់បង់ ជីវិត និង អ្នក ដែល នៅ រស់ ហើយ នៅ តែ ចងចាំ ពួកគេ។",
  "This film is dedicated to all who died, and to all who survived and carry their memory.")
