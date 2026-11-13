# Provided sources — Democratic Kampuchea (របបកម្ពុជាប្រជាធិបតេយ្យ), 17 Apr 1975 – 7 Jan 1979

Step 1 of the documentary research: the six sources the user supplied, opened, extracted and summarised.
Accessed: 2026-10-25. All downloads are in `source/raw/` (treated as untrusted data; nothing in them was executed or followed).
Extracted texts are in `source/P<n>_*.txt`.

How each text was obtained:

| # | Method | Result |
|---|---|---|
| P1 | curl of the percent-encoded URL; HTML → text; revision data from the MediaWiki API | OK (current revision 338202, 2026-08-03, a bot link fix; last content edits 2024-05-20) |
| P2 | curl of /document/, /doc/, /read/ and /embeds/ URLs all returned Scribd's "Client Challenge" bot page; web.archive.org had no snapshot (404); Wayback API returned 429; WebFetch got the title and uploader only, and the embed's text layer is garbled (Khmer vowels/subscripts stripped) | **Read visually**: opened the `/embeds/695913729/content` page in Chrome and read all 8 rendered pages. `P2_…_notes.txt` is a close English rendering with short Khmer quotes, **not a verbatim transcript** |
| P3 | The sala.moeys.gov.kh page is a catalogue entry; its embedded JSON points to the PDF on api.saladigital.org (9.5 MB, 102 pp.). The PDF uses the legacy **Truth/Limon** Khmer font encoding, so it was converted to Unicode with a port of the khmerconverter (KhmerOS/Debian) Truth mapping table | OK. Converted text is clean apart from occasional stray symbols |
| P4 | curl PDF (91 PowerPoint slides). The embedded text layer is corrupted (broken Khmer glyph mapping), so the slides were rendered at 300 dpi and OCR'd with Tesseract `khm`; key image-only slides were checked by eye | OK. The OCR has errors; several slides are photos or diagrams with no text |
| P5 | curl of the Moodle page (no login needed); HTML → text | OK. 8 small illustrative thumbnails were not described |
| P6 | curl PDF (6 pp.), legacy Truth font → Unicode conversion as for P3 | OK |

---

## 1. Summary table

| # | Source (URL) | What it is | Key facts | Reliability |
|---|---|---|---|---|
| P1 | Khmer Wikipedia, «កម្ពុជាប្រជាធិបតេយ្យ» — https://km.wikipedia.org/wiki/កម្ពុជាប្រជាធិបតេយ្យ | Encyclopedia article, crowd-written, partly translated from English Wikipedia. Created 2009; last content edits 2024-05-20. 36 footnotes (Kiernan, Chandler, Jackson, Vickery, Becker, Etcheson, DC-Cam, Yale CGP, Sharp) | 17 Apr 1975; constitution 5 Jan 1976; Sihanouk resigned 2 Apr 1976 / "mid-April" (it gives both), house arrest until 1979; 8 zones listed as 7 + special regions 505 and 106; ~68,000 KR troops → Revolutionary Army of Kampuchea; Office 870; CPK revealed "March 1977"; ~25,000 monks killed; >1.38 million killed (DC-Cam/Yale grave mapping), up to 2.5 million including disease and starvation, ~25% of the population; S-21 ~17,000 detained, "only 7 escaped"; regime lasted 3 years 8 months 20 days | **Medium–low.** Useful pointers and footnotes, but uneven translation, several factual slips, internal contradictions and a "citation needed" tag. Do not cite it directly; follow its footnotes |
| P2 | Scribd doc 695913729, «សម័យកម្ពុជាប្រជាធិបតេយ្យ ឬ ប៉ុល ពត», uploader "Kim Sor" — https://www.scribd.com/document/695913729/ | Anonymous 8-page Q&A study sheet headed "Lesson 4: Democratic Kampuchea" (matches the Grade 9/12 syllabus). No author, date or references | 8-point policy of 20–25 May 1975; evacuation pretexts; constitution adopted by a ~1,000-member congress on 15–19 Dec 1975, in force 5 Jan 1976, 250 seats (150/50/50); state and CPK posts; Four-Year Plan "1977–1981"; cooperatives in 3 stages; base vs new people; "nearly 200" security centres; 1978 East Zone purge; Front founded 2 Dec 1978 at Snuol, Kratie, led by Heng Samrin; 7 Jan 1979 framed as "liberation from the genocidal regime"; why the leaders were tried | **Low as evidence** (unsourced student/teacher notes), but a useful picture of what Cambodian students are taught. Several errors: "6 chapters" (should be 16), plan "1977–1981" (should be 1977–1980), "24 hours a day", Hu Nim "rose against Pol Pot in Jan 1976" |
| P3 | sala.moeys.gov.kh library 00006014 (MoEYS "Sala Digital") → PDF of **ឌី ខាំបូលី, «ប្រវត្តិសាស្ត្រកម្ពុជាប្រជាធិបតេយ្យ (១៩៧៥-១៩៧៩)»**, DC-Cam — https://sala.moeys.gov.kh/kh/library/00006014 | Khmer edition of Khamboly Dy, *A History of Democratic Kampuchea (1975–1979)*, Documentation Center of Cambodia, 2007 (this copy is the 2nd printing, 2011: 300,000 + 200,000 copies). Reviewed by David Chandler and Wynne Cougill; Khmer translation by Pheng Pong-Rasy. The English edition was approved by a Government commission (3 Jan 2007) as supplementary teaching material. This PDF is a post-2015 revised reprint | ~2 million evacuated from Phnom Penh, "thousands" died; constitution approved 14 Dec 1975, promulgated 5 Jan 1976; 250-seat assembly met once (Apr 1976); only election 20 Mar 1976; Sihanouk's retirement accepted by the Standing Committee 11 Mar 1976 and by the Assembly in Apr 1976; 6 zones, 32 sectors; Four-Year Plan 1977–1980, 3 t/ha; "nearly 200" prisons; ~500,000 executed; Cham dead 87,000 (Kiernan) to 400–500,000 (Ysa Osman); East Zone 1978 ~100,000 dead; S-21 ~14,000 prisoners, ~23 survived, 179 released; Choeung Ek 13 km SW; Front 2 Dec 1978 at Snuol; invasion 25 Dec 1978; 7 Jan 1979; ~2 million dead (range 740,000–3.3 million in the notes); DC-Cam mapping 388 sites / 19,733 pits / 196 prisons | **High.** Cambodia's standard school text on DK, written from DC-Cam archives and reviewed by leading scholars. Simplified for students; some figures are now dated |
| P4 | digital-library.cloudnet.com.kh PDF — https://digital-library.cloudnet.com.kh/storage/media_files/c3Fg5lx9CmAMqnRe0iCpAToCnX5R62ilrYpQhgEx.pdf | 91-slide lesson deck, "Smart 1000 video, Grade 12 History, Chapter 2 Lesson 4: Democratic Kampuchea (1975–1979)", teacher **Meas Phyrun (មាស ភិរុណ), Preah Sisowath High School**; made 2 Feb 2022. Based on the MoEYS Grade 12 summary booklet (2018) and the textbook pp. 103–172 | Pol Pot ordered the attack on Phnom Penh without consulting Vietnam; 17 Apr 1975; evacuation pretexts; 8-point policy, 20–25 May 1975; 1975–76 GRUNK government; constitution 15–19 Dec 1975 / 5 Jan 1976, **16 chapters, 21 articles**; 6 zones and 32 sectors in 1976 (with codes), Central Zone created 1977; Four-Year Plan **1977–1980**; slogan «កម្ទេចខុស ជៀសជាងលែងខុស»; enemies of Angkar diagram; S-21 units (hot, cold and "chewing" interrogation groups); Front founded 2 Dec 1978, attack 25 Dec 1978, victory 7 Jan 1979; ECCC law 10 Aug 2001, Cases 001/002, 002/02 verdict | **Medium.** A teacher's deck closely following the official curriculum and DC-Cam material; illustrated with DC-Cam and press photos. No death-toll figure. OCR-derived text |
| P5 | EBC eLearning — https://elearning.ebc.edu.kh/mod/page/view.php?id=265102 | Moodle lesson page "His G9: (Ch.2) Lesson 4 (summary): Democratic Kampuchea (1975–1979)", a Grade 9 history Q&A summary. Last modified Thu 23 Oct 2025 | Glossary (អង្គការ, high-level cooperative = sleep, eat and work together); 17 Apr 1975 "liberated"; evacuation pretexts; 8 principles (a different list); "6 zones and 32 sectors" with codes and zone secretaries; state and CPK posts 1976–78; congress 15–19 Dec 1975 with 1,000 people; constitution in use "**15** Jan 1976" (contradicts its own "5 Jan 1976"); 250 seats; anthem «១៧ មេសា មហាជោគជ័យ» "composed by Pol Pot"; cooperatives in 2 stages; 12–15 h work; mass weddings; Front 2 Dec 1978 under Heng Samrin; 7 Jan 1979 | **Low–medium.** Unsourced exam-prep summary with typos and some clear errors (15 Jan; "300–400 villages"; Koy Thuon "killed 1976"). Useful for the official curriculum framing |
| P6 | cambodiatribunal.org court-filings — https://www.cambodiatribunal.org/assets/pdf/court-filings/historical_overview_of_the_krouge_kh.pdf | DC-Cam, «ប្រវត្តិសាស្ត្រសង្ខេបរបស់ខ្មែរក្រហម» (Historical Overview of the Khmer Rouge), Khmer, 6 pp., translated by Kry Suyheang, edited by Nhean Sochetra; PDF dated 21 Sep 2010. States it is excerpted from Dy's *History of DK* (= P3). Posted on the Cambodia Tribunal Monitor site; despite the folder name it is not itself a court filing | CPK took power 17 Apr 1975, existence secret until 1977, leaders called themselves «អង្គការបដិវត្តន៍»; Pol Pot party secretary 1963; Jan–Aug 1973 bombing "over half a million tons", "over 300,000" dead; KR held ~85% of territory in early 1973; >2 million evacuated from Phnom Penh, thousands died; S-21 ~14,000 prisoners, **12 survived**; 3 t/ha quota; >12 h work; border war from late 1977; Vietnamese invasion Dec 1978, Phnom Penh taken 7 Jan 1979; UN seat 1979–1990; 1982 coalition; KR finished 1999; **nearly 2 million** dead | **High** for the DK-period core (it is a condensation of P3). The pre-1975 bombing sentence is garbled in translation and its figures are contested (see Conflicts) |

---

## 2. Detailed notes per source

### P1 — Khmer Wikipedia «កម្ពុជាប្រជាធិបតេយ្យ»
File: `source/P1_kmwiki_democratic_kampuchea.txt`. Page id 10259, length 74,932 bytes, created 2009-05-21 by user Rotna; current revision 338202 (2026-08-03, a link-rescue edit by InternetArchiveBot). Section names below follow the article.

**Infobox**
- Names: «កម្ពុជា» (1975–76), then «កម្ពុជាប្រជាធិបតេយ្យ» (1976–82). Regime 1975–1979; the state existed 1975–1982 (it kept the UN seat).
- Anthem «ដប់ប្រាំពីរមេសាជោគជ័យ» ("Glorious/Victorious Seventeenth of April"). State religion «អទេវនិយមរដ្ឋ» (state atheism) [fn 1, Britannica]. Currency: "none (money was abolished)".
- Party general secretary: Pol Pot (given as 1976–79). Head of state: Norodom Sihanouk 1975–76, then Khieu Samphan 1976–79. Prime minister: Penn Nouth 1975–76, Khieu Samphan 1976 (an acting role, unlabelled), Pol Pot 1976–79. Legislature: Kampuchean People's Representative Assembly.
- Key dates: KR took Phnom Penh 17 Apr 1975; constitution proclaimed 5 Jan 1976; "Vietnamese troops entered Phnom Penh" 7 Jan 1979. Area 181,035 km².

**Lead and History**
- DK is the name for the KR dictatorship of 1975–1979, also called «របបប្រល័យពូជសាសន៍» ("the genocidal regime"). The KR were responsible for "millions" of deaths. After 1979 DK became a China-backed rump state; in June 1982 it formed the Coalition Government of DK with two non-communist groups and kept international recognition [fn 5].
- Background: the 1970 coup by Lon Nol; Sihanouk allied with the KR; Vietnamese communist presence and US carpet-bombing helped the KR's rise; strong rural support. Some speculative, unsourced analysis says KR violence was learned during the war and meant to "toughen" people against Vietnam.
- Sihanouk was kept as nominal head of state until **2 April 1976**, "the day he decided to resign"; a later paragraph says he resigned in "mid-April 1976" (internal inconsistency). He returned from China in **September 1975** and was confined in the palace with royal family members until the 1979 war, when he went to the UN Security Council to argue DK's case, then to China.

**Organisation (§2)**
- January 1976: the CPK put the DK constitution into use. The People's Representative Assembly (ស.ត.ប.ក.) met **only once, in April 1976**. Its 250 members were never really elected; all were appointed from above.
- DK was an atheist state; Islam, Christianity and especially Buddhism were banned. "Nearly **25,000 monks** were killed" [fn 12, a 1992 NYT article, journalistic].
- All power lay with the Standing Committee (Pol Pot, Nuon Chea and seven others), known to most people as "Angkar", working from **Office 870** in Phnom Penh. Pol Pot revealed the CPK's existence in a speech in "**March 1977**", when it became known that Pol Pot and Saloth Sar were the same person. (Mainstream: the public revelation was Pol Pot's speech of 27 Sep 1977.)
- §2.1 Administration: says "8 zones" but lists 7 (Northwest, North, Northeast, East, Southwest, West, Central) plus 2 special regions: **Kratie 505** and, before mid-1977, **Siem Reap 106** [Martin 1994]. Villages were split into groups of 15–20 families under a group chief.
- §2.2 Justice: no courts, judges, laws or trials. The "people's courts" of constitution Art. 9 were never set up. They were replaced by "education", interrogation and security centres [Becker].
- §2.3 Foreign relations: close ties with China and North Korea. It says "**Kim Jong Il**" sent praise in 1977, on the CPK's 17th anniversary; this is likely an error for Kim Il Sung, the leader in 1977. Diplomatic relations only with China, North Korea, Egypt, Albania, Cuba, Laos, Vietnam (until Dec 1977), Romania and Yugoslavia.
- §2.4 Army: ~**68,000** KR fighters renamed the Revolutionary Army of Kampuchea (ក.ប.ក.) after 17 Apr 1975, under Son Sen (commander and defence minister): 230 battalions, 30–40 regiments, 12–14 brigades. The first tasks were executing Khmer Republic officials and their families without trial. Zone secretaries were "like warlords", and troops were moved between zones to purge.

**Ideology (§3)**
- Influences: Maoism, the French Communist Party, Marx and Lenin, and Khmer racial-superiority ideas. Paris-educated leaders (Pol Pot, Khieu Samphan, Kaing Guek Eav alias Duch) are named. Vickery and Rithy Panh (on Duch) are cited.
- Collectivisation split families; DK claimed to have "liberated" women (Karkaria). "In reality not equal" carries a «[ត្រូវការអំណះអំណាង]» ("citation needed") tag.
- Cities became ghost towns; religion, private property, money and markets were abolished. The killing reached about **25%** of the population. Victims listed: capitalists, professionals, intellectuals, police, civil servants (incl. Lon Nol leaders), and ethnic **Chinese, Vietnamese, Lao and Cham**.
- Duration "3 years 8 months 20 days". Mass-grave analysis by **DC-Cam's mapping programme and Yale** gives **>1.38 million** killed [fn 34–35]; with disease and starvation the toll "rises to **2.5 million**", including minorities [fn 36, Bruce Sharp]. Vietnamese in Cambodia were killed "almost to the last one".
- **S-21** (now the Tuol Sleng Genocide Museum) "detained and killed about **17,000**; only **7** people escaped".

**Memory (§4)**: Tuol Sleng was a high school turned into the S-21 interrogation and torture centre; **Choeung Ek** was a mass burial and execution site outside Phnom Penh, now a memorial. The article says the government did little else to commemorate, because former KR cadres stayed influential, and that teaching was "neglectful" until international pressure. Survivor memoirs (Haing Ngor, Pin Yathay, Laurence Picq, Ponchaud, Chanrithy Him, Loung Ung, Oni Vitandham, Ung Kilong), Rithy Panh films, and *Year Zero* (Pilger and Munro, 1979; "raised £42 million").

### P2 — Scribd «សម័យកម្ពុជាប្រជាធិបតេយ្យ ឬ ប៉ុល ពត» (uploader Kim Sor)
File: `source/P2_scribd_kim_sor_lesson4_notes.txt` (full English rendering, question by question). Page refs are the document's own page numbers 1–8.
- **Q1 (p.1)**: KR took Phnom Penh 17 Apr 1975. On **20–25 May 1975** a big meeting announced an **8-point policy**: (1) evacuate all towns, especially Phnom Penh; (2) abolish markets; (3) abolish currency; (4) defrock all monks and send them to farm; (5) execute Lon Nol regime leaders; (6) high-level cooperatives nationwide; (7) expel all ethnic Vietnamese; (8) send troops to the borders, especially the Vietnamese border.
- **Q2 (p.1)**: evacuation reasons: purge enemies and spy networks; make a nation of peasants; collective rice farming; the pretext of US bombing («ប្រើលេសថាខ្លាចអាមេរិកទម្លាក់គ្រាប់បែក»); claimed lack of transport for food; "purity". No numbers.
- **Q3 (p.1)**: National Congress at the **Olympic Stadium, 15–19 Dec 1975**, ~**1,000** members, adopted the constitution. In use from **5 Jan 1976**, "**6** chapters, 21 articles" (P4 says 16). Country renamed DK. Assembly of **250** seats = **150 peasants + 50 workers/labourers + 50 Revolutionary Army**. Anthem «17 មេសាមហាជោគជ័យ».
- **Q4 (pp.1–2)**: state: **Khieu Samphan** president of the State Presidium; **Nuon Chea** president of the Assembly; **Pol Pot** prime minister; **Ieng Sary** DPM, foreign affairs; **Vorn Vet** DPM, economy; **Son Sen** DPM, defence. CPK: Pol Pot secretary, Nuon Chea deputy. Central Committee: So Phim, Ieng Sary, Son Sen, "ឈិនជឿន" (sic; = Chhit Choeun alias Ta Mok), Vorn Vet, Ke Pauk, Khieu Samphan, Nhim Ros. No Ieng Thirith.
- **Q5 (p.2)**: Four-Year Plan "**1977–1981**" [sic]: security plus the "Great Leap"; labour divided by age, sex and class; modern agriculture in 10–15 years and industry in 15–20; **3 t/ha** on ordinary land, **6–7 t/ha** on double-cropped land; rice split 4 ways (food, seed, reserve, export for machinery and weapons); self-reliance «ម្ចាស់ការ ខ្លួនទីពឹងខ្លួន».
- **Q6 (pp.2–3)**: cooperatives: 1970–75 mutual-aid groups of 10–30 families; after 1975 low-level cooperatives of hundreds of families; **1977** high-level cooperatives of 3–4 villages or a whole commune. **Base people** «ប្រជាជនចាស់» vs **new / "17 April" people** «ប្រជាជនថ្មី (ប្រជាជន 17 មេសា)». Saying: «ទុកក៏មិនចំណេញ ដកចេញក៏មិនខាត» ("to keep you is no gain, to lose you is no loss"). Mass weddings of 3–10 and of 30–50 up to 100+ couples. Schools became prisons; children were raised as "Angkar's children" to spy on parents.
- **Q7 (p.3)**: work over **12 h/day, 7 days/week**. Hunt for «ខ្មាំងបង្កប់ស៊ីផ្ទៃក្នុង» ("hidden enemies burrowing from within"); killings of alleged CIA, KGB and Vietnamese agents. **1978**: the most brutal purge, of the **East Zone** «ភូមិភាគបូព៌ា». "**Nearly 200**" «មន្ទីរសន្តិសុខ» (security offices). Most victims were innocent people accused of being former Lon Nol soldiers or officials.
- **Q8 (p.3)**: fall: popular hatred; purges of senior cadres from mid-1976; border war (clashes from 1975; attacks on Chau Doc and Ha Tien in 1977); the **Kampuchean United Front for National Salvation** «រណសិរ្សសាមគ្គីសង្គ្រោះជាតិកម្ពុជា», founded **2 Dec 1978 in Snuol district, Kratie**, led by **Heng Samrin**, took Phnom Penh with the Vietnamese army on **7 Jan 1979**.
- **Q9 (p.4)**: meaning of 7 January in official terms ("rebirth", national unity, the darkest chapter closed).
- **Q10–16 (pp.4–6)**: why the killing escalated (secrecy, false reporting, young semi-literate cadres, mutual denunciation); «គុកឥតជញ្ជាំង» ("prison without walls"); black clothes; forced marriage; the «មហាលោតផ្លោះមហាអស្ចារ្យ» ("super great leap"); purging for "pure" revolutionaries «វិសុទ្ធកម្ម». Consequences include "hundreds of thousands" who fled abroad. **No death-toll figure anywhere.**
- **Q17 (p.7)** (uprisings): **Hu Nim** "came out against Pol Pot", Jan 1976; risings in Siem Reap (Chi Kraeng?) Mar 1976, the North and Battambang Jan 1977, and Kampong Thom, Kampong Chhnang, Mondulkiri Mar–Apr 1977; **Hun Sen** fled to Vietnam in 1977; 2 Dec 1978 Front; "within two weeks" the whole country was freed. Several items are unsourced and not mainstream (see Conflicts).
- **Q18 (pp.7–8)**: crimes named: war crimes, crimes against humanity, genocide. The government asked the UN for a hybrid court, «តុលាការកូនកាត់» / «សាលាក្តីខ្មែរក្រហម» ("Khmer Rouge Tribunal"). No ECCC dates or verdicts.
- **Q19 (p.8)**: base people split into «ប្រជាជនពេញសិទ្ធិ» (full-rights) and «ប្រជាជនត្រៀម» (candidates).

### P3 — Khamboly Dy, «ប្រវត្តិសាស្ត្រកម្ពុជាប្រជាធិបតេយ្យ (១៩៧៥-១៩៧៩)», DC-Cam (via MoEYS Sala Digital)
File: `source/P3_dccam_dy_history_dk_km.txt` (102 PDF pages; **book page = PDF page − 10**).
Catalogue page (sala.moeys.gov.kh): title «របបកម្ពុជាប្រជាធិបតេយ្យ (១៩៧៥-១៩៧៩)», author ឌី ខាំបូលី, publisher មជ្ឈមណ្ឌលឯកសារកម្ពុជា (DC-Cam), year 2007, keyword ខ្មែរក្រហម; 8,520 views and 56 downloads on 2026-10-25.
Imprint (PDF p.3): authors (1) Dy Khamboly, (2) David Chandler, (3) Wynne Cougill; Khmer translation by Pheng Pong-Rasy; funded by OSI and NED; © DC-Cam 2007; 1st printing 2007 (300,000 copies), 2nd printing 2011 (200,000 copies). The English edition states that on 3 Jan 2007 the Government commission approved the text as supplementary material for teachers and a basis for high-school lessons.

**Edition caveat:** the colophon says the 2nd printing was 2011. But the biographies mention events "up to the end of 2015" (Nuon Chea, Khieu Samphan) and Ieng Thirith's death in 2015, so this PDF (file date Jan 2016) is a revised reprint. This copy does not carry the government-approval sentence found in the English edition.
Page refs below are **book p. / PDF p.** Facts were extracted by reading the whole text; key figures were spot-checked in the Khmer (S-21 14,000/23/179, the 388/19,733/196 mapping, 14 Dec 1975, 20 Mar 1976, 500,000, bombing tonnage).

**Chapters**: 1 Summary (1) · 2 Who were the KR (6) · 3 Taking power (16) · 4 Government (22) · 5 Administrative geography (28) · 6 Four-Year Plan 1977–1980 (32) · 7 Daily life (36) · 8 Security system (50) · 9 S-21 (59) · 10 Foreign relations (69) · 11 Fall (72) · Conclusion (79) · Appendix: S-21 guard rules (80) · Bibliography (82) · Endnotes (85).

**Takeover and evacuation**
- 17 Apr 1975: the rebels, in black and khaki, entered from all sides. Some crowds cheered with white cloth; many stayed hidden. Radio said they had not come to negotiate and would execute only senior officials and commanders (16/26). Note 13 lists the 7 pre-victory "super-traitors" «មហាជនក្បត់»: Lon Nol, Sirik Matak, Long Boret, Cheng Heng, In Tam, Sosthène Fernandez, Son Ngoc Thanh (86/96).
- Long Boret, Sirik Matak and Lon Non were executed, along with hundreds of officers and officials. About 610 foreigners sheltered at the French embassy and were trucked to Thailand after two weeks (17/27).
- Evacuation began 2–3 hours after entry: **~2 million** Phnom Penh residents, **incl. >1 million war refugees**, were moved out within about a week. Hospitals were emptied; "**thousands**" died on the road (18–19/28–29; 2/12).
- Reasons given: US bombing and "back in 2–3 days" (at the time); lack of food transport (Ieng Sary, later); breaking enemy spy networks (Pol Pot in Beijing, Oct 1977). Historians add that the KR saw city people as "impure" «មិនស្អាតស្អំ» (20–21/30–31).
- Phnom Penh became a ghost city of ~**40,000** (cadres, soldiers, workers) (21/31). Witness accounts: Sim Sot, So Ry (18–20).

**Abolitions and Angkar**
- Abolished: money, markets, education, private property, foreign fashion, religious practice, and Khmer and minority traditions. Schools, pagodas, **mosques, churches** and universities were closed or turned into prisons, stables, re-education camps and granaries. Black clothes for all; no transport, no leisure. "Three people chatting could be accused as enemies" (2/12).
- Leaders called themselves «អង្គការបដិវត្តន៍» (revolutionary organisation); the party was secret until **1977**; Angkar claimed to be everyone's «ឪពុកម្តាយ» (parents) (1–2/11–12). Angkar = CPK members led secretly by Pol Pot (22/32).
- Office 870 directive of 11 Jul 1977 on the use of "Angkar" (note 15, 86/96). Pol Pot publicly revealed the CPK and his role in **Sept 1977**, before visiting China (27/37).
- March 1976: the party's founding date was changed from **1951 to 1960**, to deny Vietnamese parentage (27/37).
- Slogans: «លាក់ការណ៍ជាកត្តាជ័យជម្នះ…» (secrecy is the key to victory); «អង្គការ ថាម៉េច ត្រូវធ្វើយ៉ាងហ្នឹង!» (whatever Angkar says, do it!); «អង្គការគ្មានទេសញ្ញាប័ត្រ មានតែសញ្ញាឃើញ» (Angkar has no diplomas, only visible results); «មិនដឹង មិនឮ មិនឃើញ» (don't know, didn't hear, didn't see).

**Sihanouk and the constitution**
- GRUNK name kept until late 1975. Sihanouk returned in **early Sept 1975** with Penn Nouth, Khieu Samphan and Ieng Thirith. Three weeks later he went to the UN (23–25/33–35). About 20 royals died under DK, at least 7 at Tuol Sleng (25/35).
- Constitution approved by the **3rd National Congress on 14 Dec 1975** and **promulgated 5 Jan 1976**. Country named «កម្ពុជាប្រជាធិបតេយ្យ». People's Representative Assembly of **250** (150 peasants, 50 workers and labourers, 50 army). It never mentions the CPK. The Assembly met only once, **11–13 Apr 1976** (note 20) (25/35, 87/97).
- Only election: **20 Mar 1976**; full-rights base people only; names never published (37/47).
- Flag: Art.16. Anthem «១៧មេសា មហាជោគជ័យ», attributed to Pol Pot, lyrics printed (24/34). The number of chapters and articles is not given.
- Resignation: the Standing Committee accepted his request on **11 Mar 1976**, with conditions (no travel, statements or diplomats). In **April 1976** the Assembly accepted it unanimously, with an $8,000 pension never paid. Held in the Palace until Jan 1979 (26/36). He flew to China on 6 Jan 1979 (note 19).

**Leaders**
- Central Committee, Sept 1975: Pol Pot, Nuon Chea, So Phim, Ieng Sary, Son Sen, Ta Mok, Vorn Vet. Added in 1977: Nhim Ros, Khieu Samphan, Ke Pauk (22/32). The Standing Committee alone decided policy (26/36).
- Government (note 20, 87/97):
  - Assembly: Nuon Chea chair.
  - State Presidium: Khieu Samphan; vice-chairs So Phim and Nhim Ros.
  - Ministers: Pol Pot PM; Ieng Sary DPM, Foreign Affairs; Vorn Vet DPM, Economy; Son Sen DPM, Defence; Hu Nim, Information; Thiounn Thioeun, Health; **Ieng Thirith, Social Affairs**; Toch Phoeun, Public Works; **Yun Yat, Culture and Education**.
  - Committees: Koy Thuon commerce, Cheng An industry.
- Biographies:
  - **Pol Pot** (Saloth Sar): b.1925; party secretary Feb 1963; died 15 Apr 1998.
  - **Nuon Chea**: b.1926; "Brother No.2", key in security; ECCC arrest 19 Sep 2007.
  - **Khieu Samphan**: b.1931; President of the State Presidium.
  - **Son Sen**: S-21's direct supervisor; killed on Pol Pot's order 10 Jun 1997.
  - **Ieng Sary**: defected 1996; died 14 Mar 2013.
  - **Ta Mok** (Chhit Choeun): Southwest secretary; died 21 Jul 2006.
  - **Ieng Thirith**: "died 22 Mar 2015" (mainstream: 22 Aug 2015).

**Zones** (28–31/38–41): 1976: **6 zones, 32 sectors**:
- **East 203** (So Phim; sectors 20–24)
- **Southwest 405** (Ta Mok)
- **North 303** (Koy Thuon until early 1976, then Ke Pauk; Kang Chap from 1977)
- **Northwest 560** (Nhim Ros)
- **West 401** (Chou Chet)
- **Northeast 108** (Ney Sarann alias Ya, killed 1976)
- Autonomous sectors: Siem Reap–Oddar Meanchey **106** and Preah Vihear **103**; Kampong Som separate. In **1977** the Central Zone was formed from the old North; 505 (Kratie) and 105 (Mondulkiri) became autonomous.

**Four-Year Plan 1977–1980** (32–34/42–44): drafted hastily in 1976; collectivisation the top priority after security. **3 t/ha** average, 6–7 t/ha on "No.1" land. Rice in four shares, with a theoretical ration of 312 kg paddy a year per person. In practice rice went to the army, workers and exports, mainly to China. Real diet: gruel with less than half a condensed-milk can of rice a day (34/44).

**Daily life**
- Cooperatives (36/46): 1970–75 mutual-aid teams of **10–30 families**; low-level cooperatives of **300–400 people** or a village (from 1973, mostly after 1975); by **1977** high-level cooperatives of **~1,000 families** or a commune. Communal eating, work and tools.
- Work over **12 h/day, 7 days/week**, sometimes until midnight by moonlight or torchlight (46/56).
- Classes (37–38/47–48): base people (full-rights «ពេញសិទ្ធិ» / candidates «ត្រៀម») and new / "17 April" people. The new people were called «ជនបញ្ញើក្អែក» (parasites), "war losers and prisoners of war"; slogan «ទុកក៏មិនចំណេញ ដកចេញក៏មិនខាត». Conditions varied by region (East milder than Northwest).
- Weddings (40–42/50–52): «ពិធីបើកវគ្គ», 3–10 couples or 30–100+ (one of 160 couples in 1978); partners chosen by Angkar; some women forced to marry disabled soldiers.
- Children (42–45/52–55): no real schools; children's mobile units; taught that Angkar is their parent; spied on families; thousands killed at the front in 1977–78.

**Security system** (50–58/60–68)
- "**Nearly 200**" prisons called «មន្ទីរសន្តិសុខ». Pol Pot to Belgian visitors, 5 Aug 1978: "we have no prisons".
- Levels: commune, district, sector, zone, and the centre (S-21).
- Arrests peaked in late 1976–early 1977. People were summoned with «អង្គការអញ្ជើញសមមិត្តទៅរៀនសូត្រ» ("Angkar invites comrade to go and study"). Slogans «សុខចិត្តចាប់ខុស១០ មិនឲ្យលែងខុស១» (better to arrest ten wrongly than free one wrongly) and «ជីកស្មៅត្រូវជីកទាំងឫស» (when digging up grass, take the roots).
- Enemies: new people, former regime staff, non-Khmers; thousands of Khmer Republic soldiers and officials killed in 1975.
- **Cham** (53/63): Islam and the Cham language banned, religious leaders killed, forced to eat pork, "tens of thousands" died. Note 24: **Ysa Osman 400–500,000** Cham dead vs **Kiernan ~87,000**.
- **Vietnamese**: expelled in 1975; those who stayed were massacred 1977–78.
- **Chinese**: treated harshly "but not singled out for killing" (debated; see conflicts).
- **Intellectuals** (glasses, foreign languages). Hill minorities at first trusted.
- **Monks**: only via the ban on religion. **Thai**: not mentioned.
- External enemies: the USA and its allies (e.g. Thailand), Vietnam, USSR. «ខ្មាំងបង្កប់ស៊ីរូងផ្ទៃក្នុង» = alleged CIA/KGB/Vietnamese agents (55/65).
- "**About 500,000**" executed (57/67). Methods: blows to the neck at pits, mass shootings, suffocation with bags, wells, burial alive.

**S-21 / Tuol Sleng** (59–68/69–78)
- Location: former Ponhea Yat high school and Tuol Sleng primary school, Tuol Svay Prey.
- Prisoners: "of **about 14,000** prisoners, **about 23** survived" (kept for skills such as painting). About **179** were released 1975–78 (DC-Cam report, note 28). ~400 foreigners, mostly Vietnamese. Mass arrests of cadres from Oct 1976.
- 10-point «វិន័យសន្តិបាល» (security regulations) printed (61/71).
- Staff ~1,000. Documentation, defence and interrogation units; "hot" «កងកាច», "cold" «កងស្លូត» and "chewing" «អង្កៀម» groups.
- Chain of command: under Son Sen. **Duch** chief; Khim Vat alias Hor and Mam Nai deputies. Duch: b.1942; arrested 1999; ECCC verdict "26 Jul 2010 … life" (mainstream: 35 years in 2010, life on appeal 3 Feb 2012) (66/76).
- Killing word «កម្ទេចចោល» ("smash"). From late 1976 prisoners were trucked to **Choeung Ek**, 13 km southwest of the city. The PRK opened both sites as museums in 1979 (68/78).

**Purges** (47–48/57–58; 73–74/83–84)
- From mid-1976; the **North Zone 1977** purge took Koy Thuon, **Hu Nim**, Tiv Ol and others.
- After Vietnam's incursion in late 1977, the East was accused of collaboration. **1978**: East Zone rebellion and Southwest troops sent in; "**about 100,000**" East Zone people died. East Zone people were branded «ក្បាលយួន ខ្លួនខ្មែរ» ("Vietnamese heads, Khmer bodies").
- **So Phim** suicide "May 1978" in the text but "3 June 1978" in a caption (internal conflict).

**Foreign relations and war** (69–75/79–85)
- Diplomatic relations with China, North Korea, Vietnam, Laos, Cuba, Romania, Yugoslavia, Albania, Egypt.
- Clashes from late 1975 (Koh Tral). DK attacks on Vietnamese villages in 1977. Dec 1977: large Vietnamese offensive; DK broke relations "in December 1977" (no day given). On 3 Apr 1978 Radio Hanoi called for an uprising.
- Heavy Chinese military aid but no troops.

**Fall** (72–77/82–87)
- Three causes: exhaustion and starvation (false 3 t/ha reports), the purges, and the war with Vietnam ("the biggest").
- Front «រណសិរ្សសាមគ្គីសង្គ្រោះជាតិកម្ពុជា» founded **2 Dec 1978 in Snuol, Kratie** (note 34): 200 delegates, 14-member committee; **Heng Samrin** chair, Chea Sim vice-chair, Ros Samay secretary-general; announced by Radio Hanoi on 3 Dec.
- Invasion led by Gen. **Van Tien Dung**, **25 Dec 1978**. Phnom Penh taken **7 Jan 1979**; People's Revolutionary Council under Heng Samrin, then the PRK. The book says Vietnamese troops withdrew "in 1990" (mainstream: Sept 1989).
- The KR regrouped in Thailand with Chinese and Thai aid. The UN seat stayed with DK; 1982 tripartite coalition (Sihanouk, Khieu Samphan, Son Sann); 1991 Paris Agreements; defections 1996–98; Ta Mok arrested 1999; the KR ended in 1999.

**Death toll** (4/14; 79/89; note 2, 85/95)
- Main text: "**about two million**" died of disease, starvation, killing and overwork.
- Note 2 gives the range: PRK survey >3.3 million; Kiernan 1.5 million, later ~1.7 million; CIA (1980) ~1.4 million; Vickery ~740,000.
- **DC-Cam mapping**: **388** killing sites with **19,733** pits, **196** prisons, **81** memorials (5/15).
- Pre-1975 bombing: main text "Jan–Aug 1973, ~half a million tons, ~300,000 dead" (14/24; it attributes the bombing to the Khmer Republic, armed by the US). Note 11 (Owen and Kiernan): **2,756,941 t** dropped 1965–73; older estimates of **50,000–150,000** deaths.

**ECCC**: Nuon Chea and Khieu Samphan arrested 2007 and sentenced to life; Ieng Sary died 2013 before judgment; Duch (see above). The 2018 genocide judgment is not covered.

**Conclusion** (79/89): one of the 20th century's worst tragedies; "about two million" dead; extremist, inexperienced leaders copied Chinese, Soviet and Vietnamese models while claiming independence; the country became "a vast prison".

**Main sources** (82–84): DC-Cam archives (biographies, S-21 confessions, Standing Committee minutes, *Tung Padevat*), Chandler, Kiernan, Becker, Chanda, Vickery, Locard, Vann Nath, Pin Yathay, Ysa Osman, Heder and Tittemore, and PRK-era works including Hun Sen (1989, 1991).

### P4 — Grade 12 slide deck, Meas Phyrun (Preah Sisowath HS), "Smart 1000 video"
File: `source/P4_grade12_slides_meas_phyrun_ocr.txt` (OCR; slide = PDF page).
- **S1–2**: Grade 12 History, Ch.2 Lesson 4; teacher «លោកគ្រូ មាស ភិរុណ», «វិទ្យាល័យព្រះស៊ីសុវត្ថិ». Based on the MoEYS booklet «សេចក្តីសង្ខេបមេរៀនប្រវត្តិសាស្ត្រខ្មែរ … ថ្នាក់ទី១២» (2018) and textbook pp. 103–172.
- **S4**: Saloth Sar (Pol Pot) ordered the attack on Phnom Penh "without needing to consult the Vietnamese allies". KR entered Phnom Penh on **17 Apr 1975**. S5: photo of KR troops entering (credit Roland Neveu / LightRocket via Getty).
- **S6**: forced evacuation under pretexts: fear of US bombing, Angkar "sweeping out enemies", lack of transport for food. No numbers.
- **S7–8**: **20–25 May 1975**, a CPK meeting at "Borei Keila" (OCR «បុរីកិឡា», needs checking) announced the **8-point policy** (S8 heading only; the list is not visible in the PDF). S9: DK banknotes (not stated that they were never issued).
- **S10**: 1975–76 government = Royal Government of National Union «រដ្ឋាភិបាលរណសិរ្សរួបរួមជាតិកម្ពុជា»: head of state → PM → three deputy PMs (commander-in-chief, foreign affairs, defence). The names are not printed; the photos appear to be Sihanouk, Penn Nouth, Khieu Samphan, Ieng Sary and Son Sen.
- **S12**: the word «អង្គការ». **S13**: congress adopted the constitution **15–19 Dec 1975**; promulgated **5 Jan 1976**, "**16 chapters, 21 articles**". **S14**: assembly of peasant, worker and army representatives.
- **S15**: CPK leadership 1976–78: Pol Pot → Nuon Chea → eight members (photos; last labelled Nhim Ros). **S16**: state 1976–79: assembly president, State Presidium president, PM, DPMs for foreign affairs, economy and defence.
- **S17–18**: **1976: 6 zones, 32 sectors**: North (303), Northeast (108), East (203), Southwest (405), West (401), Northwest (560); **1977: Central Zone** created (simplified map).
- **S19–20**: "**Super Great Leap Forward**" «មហាលោតផ្លោះមហាអស្ចារ្យ»; **Four-Year Plan 1977–1980**; policy = national security (hunt hidden enemies, troops to the border) + collectivisation; rice target "3 to 7 t/ha", 4 shares; modern agriculture and industry in 15–20 years; self-reliance.
- **S21–23**: cooperatives (live, work and eat together; no private property), 3 stages: 1970–75 mutual-aid teams «ក្រុមប្រវាស់ដៃ», 1975–77 low-level, **1977** high-level. Classes: base people (full-rights / candidates) vs new people.
- **S24–25**: weddings only arranged by Angkar. Schools closed and turned into prisons; the teaching corps was dissolved; pupils, students and intellectuals were killed. Children were "Angkar's children", trained to report on parents. Captioned DK propaganda photos of child labour.
- **S26**: work over 12 h/day; cooperative chiefs controlled everything; anyone who erred or protested was an "enemy" to be "smashed" «កម្ទេច».
- **S27**: purification policy; hunting hidden enemies as foreign agents (CIA, KGB). Cadres suspected from bottom to top; slogan «កម្ទេចខុស ជៀសជាងលែងខុស» ("better to smash by mistake than to release by mistake"). **S28**: **1978** brutal purge of people and cadres in the **East Zone**.
- **S29**: security system in 5 levels: commune, district, sector, zone, top level. **S30**: «ខ្មាំងអង្គការ» (Angkar's enemies): internal = new people, Lon Nol officials, **ethnic minorities**, accused people; external = USA, USSR, Thailand and Vietnam, "burrowing enemies".
- **S31–33**: photos: labour, saluting the party flag, S-21, a dam site, S-21 cadres with families (DC-Cam), empty Phnom Penh Central Market, S-21 interiors and victims' bodies found in 1979, **Choeung Ek** captioned «មន្ទីរជើងឯក». **S32**: S-21 = top-level security office; units for documentation, defence and interrogation, the last split into the "hot", "cold" and "chewing" groups «ក្រុមរងក្តៅ / ក្រុមរងត្រជាក់ / ក្រុមអង្កៀម». A photo of Duch is unlabelled. No prisoner numbers.
- **S34–39**: causes of the fall: hatred of the regime (over 12 h/day, 7 days a week; no food, shelter or medicine; no freedom of religion or movement; parents had no rights over children; slogan «ទុកក៏មិនចំណេញ ដកចេញក៏មិនខាត»); purges split the party; war with Vietnam fought without weighing its strength.
- **S40–41**: Front founded **2 Dec 1978** to free the country from the "genocidal regime". With Vietnamese army support it attacked on **25 Dec 1978** and won on **7 Jan 1979**.
- **S42–49**: ECCC: Cambodia–UN law on the Extraordinary Chambers "in force **10 Aug 2001**"; court began work "**Feb 2006**". Jurisdiction: senior leaders and those most responsible for crimes of **17 Apr 1975 – 6 Jan 1979**. **Case 001**: Kaing Guek Eav alias Duch, charged with crimes against humanity and grave breaches of the 1949 Geneva Conventions; the Supreme Court Chamber gave a **life sentence**. **Case 002**: Khieu Samphan, Nuon Chea, Ieng Sary, Ieng Thirith, charged with war crimes, genocide, crimes against humanity, grave breaches and destruction of cultural property. A press clipping: in **Case 002/02** the Trial Chamber sentenced Nuon Chea and Khieu Samphan to **life imprisonment** for genocide, crimes against humanity and grave breaches; the trial ran **17 Oct 2014 – 11 Jan 2017, 283 hearing days**.
- **S51–91**: multiple-choice quiz (answers not visible), essay questions, and homework: "Would you want the country led like DK? Why?"
- **Not in P4**: death toll, S-21 numbers, Cham, Chinese, Thai, Sihanouk's resignation.

### P5 — EBC eLearning, Grade 9 History, Ch.2 Lesson 4 summary
File: `source/P5_ebc_grade9_lesson4.txt` (lesson body near lines 1040–1290). Moodle page; "last modified Thursday 23 October 2025, 4:12 PM". Same course has video parts 1–2, assessment and homework pages (not opened).
- **Glossary**: «អង្គការ»: the word the Pol Pot group used to cover the Communist Party, the state assembly and the legislature, down to grassroots level. «សហករណ៍កម្រិតខ្ពស់» (high-level cooperative): "sleeping together, eating together and working together".
- "The KR army **liberated** («វាយរំដោះ») Phnom Penh on **17 Apr 1975**." Evacuation methods: Angkar wanted to "clean" the city; fear of US bombs; Angkar had no means to transport food.
- **8 principles** (a different list from P2): evacuate towns; abolish markets **and** currency; destroy pagodas and defrock monks; close all schools; execute intellectuals, old-regime officials **and innocent people**; high-level cooperatives (communal eating, sleeping, work); expel Vietnamese and make war on Vietnam; sever husband–wife, parent–child and family feeling.
- "3rd National Congress" officially declared **5 Jan 1976** (role of workers and peasants, sacrifice for nation and party).
- **Zones**: "6 zones and 32 sectors": **East (203)**, secretary **So Phim** ("killed 1978"; Svay Rieng, Prey Veng, part of Kampong Cham and Kratie; sectors 21–24). **Southwest (405)**, **Chhit Choeun alias Ta Mok** (d. 2006; Kandal (5 districts), Takeo, Kampot, part of Kampong Speu; sectors 13, 25, 33, 35). **West (401)**, **Chou Chet** (part of Kampong Speu, Kampong Chhnang, Kampong Som, Koh Kong; sectors 11, 15, 31, 32, 37). **Northwest (560)**, **Nhim Ros** ("killed 1978"; Pursat, Battambang; sectors 1–7). **North (303)**, **Koy Thuon alias Thuch** ("killed 1976"), then **Ke Pauk** (1977), then **Kang Chap** (1977) (Kampong Thom, Siem Reap, Oddar Meanchey; sectors 41–43). **Northeast (108)**, **Ney Saran alias Ya** ("killed 1976"; Ratanakiri, Mondulkiri, parts of Stung Treng and Kratie; sectors 101, 10[2?], 104, 105, 107 and 505).
- State 1976–78: Khieu Samphan president of the Presidium / head of state; Pol Pot PM; Nuon Chea president of the Assembly; Ieng Sary DPM, foreign affairs; Vorn Vet DPM, economy; Son Sen DPM, defence; **Cheng An** minister of industry. CPK: Pol Pot secretary, Nuon Chea deputy; members So Phim, Ieng Sary, Son Sen, Chhit Choeun (Ta Mok), Vorn Vet, Ke Pauk, Nhim Ros, Khieu Samphan.
- Constitution: the congress met only once, **15–19 Dec 1975**, with **1,000** people. Constitution "put into use **15 Jan 1976**" (contradicts its own 5 Jan statement above and all other sources). Name «កម្ពុជាប្រជាធិបតេយ្យ». **250** seats = 150 peasants, 50 labourers/workers, 50 Revolutionary Army.
- Anthem «១៧ មេសា មហាជោគជ័យ», "**composed by Pol Pot**" (unsourced). Flag red with a yellow three-towered temple. Emblem: rice fields and canals, a factory, sheaves of rice.
- Cooperatives in **2 stages**: 1970–75 low-level / mutual-aid groups of 10–30 families; 1975–79 high-level cooperatives of "**300 to 400 villages** or a whole commune" (sic; probably an error). Purpose: abolish private property and capitalism, strengthen workers and peasants.
- Work **12–15 h/day**; food was thin rice gruel mixed with morning glory, water-lily stems, banana and papaya trunks.
- Classes: base people (in the struggle before 17 Apr 1975) and new people ("17 April people").
- Weddings: "special" ceremonies of 3–10 couples (cadres or unit chiefs); normal ones of 30–50 or 100 couples, men and women in two lines pledging before Angkar and the party flag.
- Fall: hatred of the Pol Pot regime; «វិសុទ្ធកម្ម» purges "from ordinary people up to the Central Committee"; war with a stronger Vietnam. **Front 2 Dec 1978, president Heng Samrin**. The Vietnamese army with the Front "liberated Phnom Penh" on **7 Jan 1979**.
- **Not in P5**: death toll, S-21, Choeung Ek, Sihanouk, minorities, ECCC.

### P6 — DC-Cam, «ប្រវត្តិសាស្ត្រសង្ខេបរបស់ខ្មែរក្រហម» (Historical Overview of the Khmer Rouge, Khmer)
File: `source/P6_dccam_historical_overview_km.txt` (6 pp.). DC-Cam letterhead ("Searching for the Truth: Memory & Justice"). Translated by «គ្រី ស៊ុយហៀង» (Kry Suyheang), edited by «ញាណ សុជាតិ» (Nhean Sochetra). It states that it is drawn from Dy's *History of DK 1975–1979* (= P3).
- **p.1**: the CPK, known as the KR, took power **17 Apr 1975**, created DK in **1976** and ruled until **Jan 1979**. The party's existence stayed secret until **1977**; leaders called themselves «អង្គការបដិវត្តន៍» ("the revolutionary organisation"). The country became "a huge detention centre" and then the grave of "**nearly two million**" people, including KR cadres and senior leaders.
- **pp.1–2**: communist movement born in the 1940s anti-French struggle, influenced by Vietnam. Lon Nol's coup of **March 1970**. **Pol Pot** (born Saloth Sar), CPK secretary and leader from **1963**, studied in France, joined the French Communist Party, and returned in **1953**. Vietnam pulled its troops out at the end of **1972**.
- **p.2 (garbled sentence)**: "Jan–Aug **1973** the Khmer Republic government, with the US as arms supplier, dropped **over half a million tons** of bombs on Cambodia, killing **over 300,000**". Angry survivors joined the KR. By early 1973 about **85%** of the territory was under the KR.
- **p.3**: 17 Apr 1975 = the end of 5 years of foreign intervention, bombing and civil war. Within days the KR forced **over 2 million** people in Phnom Penh, and those in other towns, to the countryside; **thousands died** during the evacuation. The KR abolished currency, free markets, education, private property, foreign clothing styles, religious practice and Khmer traditions. Schools, pagodas, mosques, churches, universities, shops and government buildings were closed or turned into prisons, stables, re-education camps and granaries. No private or public transport. Black clothing required, even for leaders.
- **p.4**: no movement outside the cooperative; no gatherings ("if three people talked together they could be accused as enemies and arrested or killed"); no showing love, joy or pity; Angkar was the people's "mother and father". **Thousands** of Khmer Republic soldiers, commanders and officials were killed right after the takeover. Over the next 3+ years "**hundreds of thousands**" of intellectuals, city people and minorities (**Cham, Vietnamese, Chinese**) were killed, plus many of their own soldiers and party members accused of treason. **S-21**: ~**14,000** prisoners, **only 12 survived**. Four-Year Plan quota of **3 t/ha** meant year-round farming; work over 12 h/day without rest or enough food.
- **p.5**: border clashes with Vietnam from **late 1977**; tens of thousands sent to the front, thousands killed. **Dec 1978** Vietnamese invasion; Phnom Penh taken **7 Jan 1979**. KR leaders fled west and rebuilt in Thailand with Chinese and Thai help. The UN recognised DK as Cambodia's sole legitimate representative **1979–1990**. **1982** tripartite coalition with Sihanouk and Son Sann. Vietnam set up the **People's Republic of Kampuchea** under Heng Samrin. The KR survived until **1999**.
- **p.6**: "**nearly two million**" died of disease (no medicine or health care), starvation, execution or overwork. Tens of thousands of widows and orphans; **hundreds of thousands** fled as refugees; millions of landmines.
- **Not in P6**: dates of the constitution or Sihanouk's resignation, zones, names other than Pol Pot and Heng Samrin, Choeung Ek, ECCC (despite the site).

---

## 3. Conflicts and problems

### 3a. Between the provided sources

| Topic | What the sources say | Comment |
|---|---|---|
| **Death toll** | P1: >1.38 million killed (DC-Cam/Yale grave mapping), up to 2.5 million including disease and starvation, ~25% of the population. P3: "about 2 million" (notes range 740,000 to 3.3 million), ~500,000 executed. P6: "nearly 2 million". P2, P4, P5: no figure | Consistent order of magnitude. P1's "2.5 million" (Bruce Sharp's upper bound) is higher than DC-Cam's. Use a sourced range (≈1.5–2.2 million; see later research) rather than one number |
| **S-21 prisoners and survivors** | P1: ~17,000 detained, "only 7 escaped". P3: ~14,000, ~23 survived, ~179 released earlier. P6 (condensed from P3): ~14,000, **12** survived | P3 and its own condensation P6 disagree (23 vs 12). The "7 survivors" figure usually means the adults found alive in Jan 1979. The ECCC Case 001 judgment's count of identified victims should be the anchor (step 2) |
| **Constitution** | Adopted: P3 14 Dec 1975 (3rd Congress); P2, P4, P5 "15–19 Dec 1975" (~1,000 delegates; P2 adds the Olympic Stadium). Promulgated: 5 Jan 1976 (P1, P2, P3, P4, P5), but P5 also says **15 Jan 1976**. Structure: P4 16 chapters, 21 articles; P2 "6 chapters" | 5 Jan 1976 is solid; P5's 15 Jan is a typo. 16 chapters / 21 articles is the usual description; P2's "6" is an error |
| **Sihanouk's resignation** | P1: "2 April 1976" and also "mid-April 1976". P3: Standing Committee accepted 11 Mar 1976, Assembly accepted Apr 1976. Not in P2, P4, P5 | Mainstream: resignation announced on 4 Apr 1976 (letter dated 2 Apr). Phrase it as "early April 1976" unless step 2 confirms the day |
| **CPK revealed** | P1: "March 1977". P3 and P6: 1977 / Sept 1977 (before the China visit) | P1 is wrong: Pol Pot's speech was 27 Sep 1977 |
| **Prime minister 1976** | P1 lists Khieu Samphan as PM in 1976 (unlabelled). P2, P3, P5: Khieu Samphan was head of state, Pol Pot PM | Khieu Samphan was at most a brief caretaker in April 1976. Treat him as President of the State Presidium |
| **"8-point policy" of May 1975** | P2: evacuate towns, abolish markets, abolish currency, defrock monks, execute Lon Nol leaders, high-level cooperatives, expel Vietnamese, troops to borders. P4: meeting 20–25 May 1975 ("Borei Keila"?), list not visible. P5: a different list (adds closing schools, killing intellectuals "and innocent people", severing family ties). P3: not given as a list in the extracted points | P2's list matches the version usually attributed to the May 1975 meeting (e.g. Kiernan, from cadre testimony). P5 mixes policy with outcomes. Verify the meeting place and dates in step 2 |
| **Four-Year Plan years** | P3 and P4: 1977–1980. P2: "1977–1981" | P2 is wrong |
| **Rice targets** | P3: 3 t/ha average, 6–7 t/ha on No.1 land. P2: 3 and 6–7. P4: "3 to 7 t/ha". P6: 3 t/ha | Consistent; P4 merges the two land classes |
| **Cooperative stages and size** | P3: mutual-aid 10–30 families → low-level 300–400 people / a village → 1977 high-level ~1,000 families / commune. P2: 3 stages, high-level = 3–4 villages / commune. P4: 3 stages (1970–75, 1975–77, 1977). P5: 2 stages, high-level = "300–400 **villages**" | P5 misplaces P3's "300–400 people" and garbles the stages |
| **Zones** | P3, P4, P5: 1976 = 6 zones, 32 sectors (203, 405, 401, 560, 303, 108), Central Zone 1977. P1: "8 zones" but lists 7, plus special regions 505 (Kratie) and 106 (Siem Reap) | P1 mixes the 1977 layout and miscounts. P5 puts 505 inside the Northeast, P3 says it became autonomous in 1977 |
| **Zone leaders' fates** | P5: Koy Thuon "killed 1976", Ney Sarann "killed 1976", So Phim "killed 1978". P3: Koy Thuon moved early 1976, arrested and killed 1977; So Phim **suicide** (May or 3 June 1978: P3 contradicts itself) | So Phim's suicide is standard (early June 1978). Koy Thuon was arrested in 1977 |
| **Working hours** | P3, P4, P6: over 12 h/day, 7 days; P5: 12–15 h; P2: also ">12 h", but Q18 says "24 hours a day" | P2's 24 h is hyperbole |
| **National anthem** | P1: «ដប់ប្រាំពីរមេសាជោគជ័យ»; P2, P3, P5: «១៧ មេសា មហាជោគជ័យ»; P3 and P5: written by Pol Pot | Same anthem, two renderings. Authorship rests only on P3/P5 assertion; flag as "attributed" |
| **Ethnic Chinese** | P1, P6: Chinese among the minorities killed (P6: "hundreds of thousands" of intellectuals, city people, Cham, Vietnamese and Chinese). P3: Chinese suffered "but were not singled out for killing" | Scholarly debate. Kiernan estimates ~50% of ethnic Chinese died, mostly from starvation and disease as "new people". Say "persecuted as city people; very high death rate", not "targeted for extermination" |
| **Cham** | P3 note: 87,000 (Kiernan) vs 400–500,000 (Ysa Osman). P1, P6: Cham among victims. P2, P4, P5: Cham not mentioned (P4 only "ethnic minorities") | A wide, sourced range; present both or a range. The ECCC 002/02 genocide finding (2018) covers Cham and Vietnamese |
| **1973 US bombing** | P3 and P6: "Jan–Aug 1973 ~half a million tons, ~300,000 dead", attributed in the Khmer text to the Khmer Republic, armed by the US. P3 note 11: 2.76 million tons 1965–73 (Owen and Kiernan), 50,000–150,000 deaths. P1: US carpet bombing | The main-text figure contradicts the book's own note; the agent of the bombing (the US Air Force) is mistranslated. Use the note's figures |
| **The Front** | All agree: KUFNS «រណសិរ្សសាមគ្គីសង្គ្រោះជាតិកម្ពុជា», **2 Dec 1978**, Heng Samrin (P2 and P3: at Snuol, Kratie; P3: Radio Hanoi announced it 3 Dec). P3: Heng Samrin "fled to Vietnam in late 1978" | Mainstream: Heng Samrin fled in 1978 after the May East Zone revolt. Minor |
| **Invasion and 7 Jan 1979: framing** | P3, P4: Vietnamese attack 25 Dec 1978. P1, P6: Vietnamese forces "captured/entered" Phnom Penh. P2, P4, P5: Front + Vietnamese army "**liberated**" («រំដោះ») Phnom Penh. P2 adds that the Front "freed the whole country within two weeks" | Dates agree; the wording is politically loaded. For survivors and families, describe both: the regime's overthrow, the Vietnamese-led invasion and occupation, and the KR continuing as an armed movement |
| **Uprisings** | P2: Hu Nim "came out against Pol Pot" Jan 1976; risings in Siem Reap, the North, Battambang, Kampong Thom, Kampong Chhnang, Mondulkiri 1976–77. P3: the 1977 North purge arrested Hu Nim; "3–4 coup plots" and Cham rebellions | P2's Hu Nim claim is unsupported (he was purged as an alleged traitor, i.e. a KR accusation). Don't use P2's list without corroboration |
| **ECCC details** | P4: ECCC law in force 10 Aug 2001; court working Feb 2006; Duch life (Supreme Court); 002/02 life for Nuon Chea and Khieu Samphan. P3: Duch "sentenced to life on 26 Jul 2010" | P3 conflates the 2010 trial judgment (35 years) with the 2012 appeal (life). P4's Supreme Court framing is correct. Check the ECCC dates in step 2 (the law was promulgated 10 Aug 2001 and amended 2004) |
| **UN seat** | P3 and P6: DK recognised by the UN 1979–1990. P1: DK state existed to 1982, then the coalition | DK, then the CGDK, kept the seat through the 1980s. Phrase carefully |
| **Vietnamese withdrawal** | P3: "1990" | Mainstream: Sept 1989 |
| **North Korea message** | P1: "Kim Jong Il" praised DK in 1977 | Probably Kim Il Sung (head of state then). Don't use |
| **Monks** | P1: "nearly 25,000 monks killed" (NYT 1992). Others: monks defrocked and religion banned, no number | Journalistic figure; check against scholarship (step 2) |

### 3b. Unsourced, propagandistic or tone issues
- **P2 and P5** (and partly **P4**) follow the official Cambodian curriculum framing: 17 April as "liberation" in P5, and 7 January as liberation and "rebirth"; «របបប្រល័យពូជសាសន៍» ("genocidal regime") as the standard name. P2 Q9 ("meaning of 7 January") reads as a civic catechism. P2's Hun Sen and Hu Nim uprising list is unsourced.
- **P1** has unsourced speculation (KR violence meant to "toughen" people against Vietnam; a "citation needed" tag) and a political claim that the government neglected commemoration.
- **P3** is careful in tone, but its main text gives round numbers (2 million; 500,000 executed; 100,000 East Zone) whose sources appear only in the endnotes. It relies partly on PRK-era sources (Hun Sen's books) for the 1978–79 events.
- **P4** shows victim photos (bodies at S-21, 1979) and DK propaganda photos of children without context. For a family audience these must not be reused uncritically.
- **No source** discusses the **Thai** minority, gives a figure for **monks** besides P1's 25,000, names **In Lorn (Nat)** fully, or covers the ECCC Case 002/02 genocide findings in detail (only P4's clipping).

### 3c. Items to verify in step 2 (from conflicts above)
1. S-21 numbers (identified victims per the ECCC Case 001 judgment; survivor count definitions).
2. The exact date of Sihanouk's resignation.
3. The 8-point policy: meeting dates and place.
4. Death-toll range and methods (DC-Cam mapping, Heuveline, Kiernan, Yale CGP).
5. Cham, Vietnamese and Chinese death estimates; the ECCC genocide findings of 16 Nov 2018.
6. ECCC milestones (law 2001/2004; Case 001 2010/2012; 002/01 2014/2016; 002/02 2018/2022).
7. US bombing tonnage and deaths.
8. So Phim's death date.
9. The exact date of the Dec 1977 break in relations.
