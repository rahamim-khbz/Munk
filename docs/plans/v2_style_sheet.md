# Munk Second Edition (v2) Master Style Sheet & Emendation Guide

## Purpose & Scope
This document codifies the mandatory editorial standards, translation conventions, apparatus integrity rules, and scholarly emendation protocols for the second edition (`munk_production_v2.json`) of Salomon Munk’s translation of Moses Maimonides’ *Guide for the Perplexed* (*Dalālat al-Ḥā’irīn* / *Moreh Nevukhim*).

The definitive source of truth for text and apparatus is Salomon Munk’s 1856 French edition (*Le Guide des Égarés: Traité de Théologie et de Philosophie par Moïse ben Maimoun*, Paris: A. Franck, 1856–1866; `French_Healed_Enriched.json` and `French_Arabic_Enriched.json`). The second edition preserves Munk's distinct scholarly voice and philological precision while executing systematic, user-approved mechanical modernizations and lexical realignments.

All human editors, translator subagents, verifier subagents, and automated quality gates (`StrictApparatusValidator`) must strictly adhere to these standards.

**Scope of the Apparatus:**
- **Main Text Segments:** Exactly **1,531** segments across all 6 sections (Prefatory Remarks: 28; Munk's Introduction: 11; Letter to R. Joseph: 5; Part 1: 561; Part 2: 432; Part 3: 494).
- **Critical Footnotes:** Exactly **3,999** canonical footnotes (`fn.0` through `fn.3998`). Note: the raw uncurated baseline (`v1`) contained legacy uncurated baseline entries (over 4,050 raw notes, including 51 split sub-notes like `fn.1061.sub_0` and 3 anomalous keys `f1`, `f2`, `f3`), which have been curated and consolidated into the 3,999 canonical entries in `v2`.
- **In-Text Callout Markers:** Exactly **3,997** callout markers `[[fn:\d+]]` appear in the text segments, preserving 100% sequential parity with `munk_production_v1.json`. Exactly 2 canonical footnotes (`fn.2525` and `fn.2642`) are uncalled editorial apparatus notes present in Munk's 1856 French publication and preserved in `"footnotes"`.

**Absolute Ban on Unauthorized External Translations:**
The text must remain strictly and exclusively faithful to Salomon Munk’s 1856 French translation and apparatus, cross-checked against Maimonides' Judeo-Arabic original (`1856 Judeo-Arabic [jrb]`) and the medieval Hebrew translations (Samuel ibn Tibbon, Judah al-Harizi, and modern editions such as Rabbi Yosef Qafih and Makbili 2024). Under no circumstances may editors or subagents introduce phrases, readings, or summaries from unauthorized external English translations (such as the 1903 English translation). Any intrusion of unauthorized external versions into the text or apparatus is strictly prohibited.

---

## 1. Translation Scope and Scholarly Revision

The second edition is a comprehensive scholarly revision of both the main text (1,531 segments) and the entire critical apparatus (3,999 canonical footnotes):

### A. Academic English Prose & Register
1. Translate Salomon Munk’s 19th-century French into fluent, dignified, and precise mid-20th-century academic English.
2. Favor clarity, exact philosophical equivalence, and grammatical elegance while strictly adhering to Munk's literal French argument and structure.
3. Avoid modern colloquialisms, trendy academic jargon, or anachronistic idioms; preserve the elevated register suitable for a seminal philosophical treatise.
4. Maintain the authorial voice of Salomon Munk: his erudite 19th-century footnotes, bibliographical annotations, Arabic and Hebrew etymologies, and manuscript collations must be rendered in full, scholarly English.

### B. Anti-Truncation & Content Completeness Policy
1. **The 80% Word Retention Threshold:**
   Every segment and footnote with $\ge 30$ words in the literal baseline (`v1`) must retain $\ge 80\%$ of its `v1` word count in `v2`, unless `v1` contained duplicated OCR corruption or drafting repetitions. Any reduction below 80% constitutes presumptive truncation and must be flagged as a quality violation.
2. **Category C Restorations:**
   All 33 segments and 107 footnotes identified in Category C of `tripartite_redline_analysis.json` as having suffered from unfaithful rewrites, paraphrasing, or severe truncation must be restored from the faithful `v1` literal translation of Munk's French and then cleaned using the 5-pillar mechanical modernization framework.
3. **Mandatory Highlighted Segments (Restored & Modernized):**
   The following 8 heavily truncated or rewritten segments must be restored with 100% fidelity to Munk's 1856 French:
   - `root.text.Part 1..33.3`: Restore Maimonides' genuine discussion of preparatory studies; purge the fabricated parable regarding baking bread from wheat.
   - `root.text.Part 2..18.12`: Restore the full philosophical argument on creation and time.
   - `root.text.Part 2..46.4`: Restore the complete exposition of prophetic imagery and vision.
   - `root.text.Part 3..17.4`: Restore the detailed analysis of the five theories of divine providence.
   - `root.text.Part 3..22.0`: Restore the complete introductory exposition of the Book of Job.
   - `root.text.Part 3..22.1.sub_0`: Restore the full sentence-by-sentence analysis of the Satan narrative in Job.
   - `root.text.Part 3..31.1`: Restore the comprehensive discussion on the utility and rationale of the biblical commandments (*ta'amei ha-mitzvot*).
   - `root.text.Part 3..34.1`: Restore the full treatment of universal law versus individual circumstances.
4. **Mandatory Highlighted Footnotes (Restored & Modernized):**
   The following 7 heavily truncated or abridged footnotes must be restored with 100% fidelity to Munk's apparatus:
   - `fn.1784`: Restore the full apparatus detailing Judeo-Arabic manuscripts, variant readings, and medieval Hebrew translations.
   - `fn.1847`: Restore the comprehensive 300+ word philological and philosophical commentary, which was erroneously abridged to 14 words in prior drafts.
   - `fn.1377`: Restore Munk's extensive philosophical excursus and textual citations.
   - `fn.3010`: Restore the complete critical apparatus on the text of Job and rabbinic commentary.
   - `fn.3011`: Restore Munk's textual comparisons between Ibn Tibbon and Judah al-Harizi.
   - `fn.3356`: Restore the detailed Talmudic and Midrashic cross-references.
   - `fn.3411`: Restore Munk's extensive halakhic and philosophical analysis.

### C. Protection of Genuine English Completions
In 42+ specific segments and footnotes across the corpus, `v1` left French phrases, clauses, or entire footnote glosses untranslated (e.g. leaving *c'est le culte du cœur*, *volonté*, *allégorie*, or French glosses in notes). In `v2`, these have been genuinely and accurately translated into English.
- These 42+ genuine English completions (including `root.text.Part 3..50.9.sub_0`, `fn.1756`, `fn.2606`, `fn.3009`, etc.) MUST be protected and retained.
- Under no circumstances may an automated restoration revert these completions back to the raw French text of `v1`, which would introduce `french_detected` validation failures.

### D. The 5-Pillar Mechanical Modernization Framework
Whenever text is restored from `v1`, it must be cleaned and modernized according to 5 mechanical pillars:
1. **Archaism Removal:** Systematic elimination of Victorian and King James grammatical archaisms (`thou`, `thee`, `hath`, `doth`, `whilst`, `unto`, `-eth`, `-est`) per Section 3.
2. **OCR & Drafting Typo Correction:** Repair of scanned character errors and transcription slips inherited from raw drafts (e.g. `ses` -> `sees`, `denots` -> `denotes`, `constituts` -> `constitutes`, `compriss` -> `comprises`, `rids` -> `rides`, `SSEVENTH` -> `SEVENTH`).
3. **HTML Tag Balancing:** Strict FIFO nesting and closure for all supported formatting tags (`<i>`, `<b>`, `<sup>`, `<sub>`, `<span>`, `<small>`).
4. **RTL Semitic Span Validation:** Every Semitic quotation (Hebrew, Aramaic, Arabic) must be enclosed in `<span dir="rtl">...</span>` and contain valid Unicode characters in the Hebrew (`U+0590`–`U+05FF`) or Arabic (`U+0600`–`U+06FF`) code blocks. No English or Latin text may be trapped inside an RTL span.
5. **Transliteration Standardization:** Modernization of 19th-century French Orientalist transliterations into academic standards (`Motécallemîn` -> `Mutakallimūn`, `Al-'Harîzi` -> `Al-Ḥarīzī`, `Cabôd` -> `Kavod`, `Cabalistes` -> `Kabbalists`) per Section 5.

---

## 2. Scriptural Citation Standard ('Just Leave It')

When Salomon Munk’s French text provides a specific chapter and verse citation (e.g., citing `Ps. 114, 14` or `Isa. 21, 2`):

1. **Leave Munk's Citation Numbers Intact:**
   - Strictly leave Munk's verse numbers and chapter digits exactly as he gave them in the 1856 French edition.
   - Standardize ONLY the punctuation (e.g., convert comma to colon: `Ps. 114, 14` -> `Ps. 114:14`).
   - **DO NOT** replace Munk's verse numbering with modern Hebrew Bible (Masoretic) versification or Christian Vulgate versification (e.g., do not alter `Ps. 114:14` to `Ps. 102:14`). The pipeline must never second-guess Munk's source text or printings.

2. **Scope of the Rule:**
   - This "Just Leave It" policy applies **strictly to verse numbering and chapter digits**.
   - It does **NOT** restrict translation corrections, vocabulary improvements, or scholarly revision in the surrounding text or notes.

---

## 3. Archaism Ban List

Victorian, King James, and pseudo-biblical archaisms are strictly prohibited in both body text and footnotes. Replace them systematically:

| Prohibited Archaism | Mandatory Replacement |
| :--- | :--- |
| `thou` / `thee` / `thine` | `you` / `your` / `yours` |
| `hath` / `doth` | `has` / `does` |
| `whilst` | `while` |
| `unto` | `to` |
| `canst` / `shalt` / `wilt` | `can` / `shall` / `will` |
| `dost` / `didst` | `do` / `did` |
| `art` (verb) | `are` |
| Verb suffixes `-eth`, `-est` | Modern 3rd/2nd person (`knows`, `speaks`, `leads`) |
| `wherefore` (archaic usage) | `therefore`, `why`, `for which reason` |
| `thence` / `whence` | `from there` / `from where` |
| `nay` | `no`, `rather`, `on the contrary` |
| `amongst` | `among` |
| `amidst` | `amid` |
| `spake` | `spoke` |

*Archaism Whitelist:*
Words with legitimate non-archaic endings (`-eth`, `-est`) are explicitly permitted:
- Ordinal numbers: `fourth` through `nineteenth`, `twentieth`, `thirtieth`, `hundredth`, `thousandth`.
- Standard nouns and adjectives: `method`, `something`, `teeth`, `death`, `breath`, `length`, `strength`, `width`, `breadth`, `depth`, `wealth`, `health`, `stealth`, `wrath`, `faith`, `truth`, `youth`, `earth`, `birth`, `worth`, `north`, `south`, `path`, `best`, `rest`, `test`, `west`, `east`, `nest`, `guest`, `chest`, `pest`, `quest`, `manifest`, `suggest`, `attest`, `request`, `digest`, `invest`, `divest`, `interest`, `earnest`, `honest`, `modest`, `forest`, `harvest`, `priest`, `crest`, `contest`, `almagest`.
- Superlative adjectives: `greatest`, `highest`, `lowest`, `purest`, `closest`, `brightest`, `finest`, `deepest`, `noblest`, `vilest`, `earliest`, `latest`, `richest`, `simplest`, `grossest`, `weakest`, `strongest`, `wisest`, `rarest`, `densest`, `hardest`, `softest`, `crudest`, `boldest`, `strangest`, `broadest`, `warmest`, `farthest`, `furthest`, `nearest`, `northernmost`, `southernmost`, `easternmost`, `westernmost`, `uppermost`, `lowermost`.
- Hebrew letter names and biblical proper names: `aleph`, `beth`, `daleth`, `heth`, `teth`, `seth`, `japheth`, `elizabeth`, `nazareth`, `goliath`.

---

## 4. Mandatory Terminology Lexicon

Terminology must be strictly aligned with Salomon Munk's deliberate 1856 French philosophical choices, honoring classical Aristotelian vocabulary while incorporating user-approved modernizations.

### A. Category A Reversions (Mandatory Return to Munk's 1856 French Terms)
The following 6 terms were altered by anachronistic replacements in prior revisions. They MUST be restored to Munk’s deliberate terminology:

| Munk 1856 French Term | Mandatory `v2` Rendering | Prohibited Substitutions | Rationale & Philological Context |
| :--- | :--- | :--- | :--- |
| *homonyme(s) / homonymie*<br>(Ar. משתרך, Heb. משותף) | **homonym(s) / homonymous / homonymy** | `equivocal / equivocation / equivocal expression(s)` | Munk deliberately translated Aristotle's ὁμώνυμα as *homonyme / homonymie*. While later English translators used "equivocal", replacing Munk's terms erases his specific translation philosophy. |
| *émanation / épanchement*<br>(Ar. פיץ, Heb. שפע) | **emanation** | `divine outpouring / overflow / (Pines: overflow)` | Munk explicitly renders *fayd / shefa'* as *émanation* throughout the Guide. Substituting "overflow" or "divine outpouring" anachronistically imports modern terminology against Munk's French text. |
| *quiddité*<br>(Ar. מאהיה, Heb. מהות) | **quiddity** | `essence` | Munk carefully distinguishes *quiddité* (*māhiyya* / *mahut*, the "what-it-is") from *essence* (*dhāt* / *'etzem*). Collapsing *quiddité* into "essence" destroys an essential Avicennian and Maimonidean metaphysical distinction. |
| *l'Éternel*<br>(Heb. יהוה) | **the Eternal** (or **the Eternal One**) | `the Lord` | In the French Jewish Bible translation tradition (Munk, Zadoc Kahn), the Tetragrammaton is consistently rendered *l'Éternel*. Furthermore, Munk analyzes *l'Éternel* philosophically in Part 1. Restoring "the Eternal" preserves Munk's Franco-Jewish idiom. |
| *ce qui naît et périt / naît / naissent / naissance*<br>(Ar. כון, Heb. הויה) | **is born and perishes / born / birth** | `generated / generation / comes into being` | Munk deliberately translates *kawn wa-fasād* in plain French as *ce qui naît et périt* (explaining the technical Greek genesis/phthora in his notes). English translations must reflect Munk's literal French voice rather than substituting Aristotelian jargon. |
| *l'intelligence / les intelligences (séparées)* vs. *l'intellect*<br>(Ar. עקל, Heb. שכל) | **intelligence(s) / separate intelligences** (for *intelligence[s]*);<br>**intellect** (for *intellect*) | Collapsing *intelligence(s)* into `intellect(s)` | Munk rigorously maintains a lexical distinction in French between *l'intellect* (the human cognitive faculty or the Active Intellect) and *les intelligences séparées* (the separate cosmic/angelic substances). The distinction must be strictly preserved. |

### B. Category A Retentions (User-Approved Lexical Modernizations)
The following 9 modernizations are explicitly approved and must be consistently maintained:

| Munk French / Obsolete `v1` | Mandatory `v2` Rendering | Deprecated / Prohibited Form | Context & Application |
| :--- | :--- | :--- | :--- |
| *les docteurs / docteur*<br>(Chazal / Talmudic rabbis) | **Sages / Sage** (or **the Rabbis**) | `doctors / doctor` | Standard rabbinic scholarship in English; eliminates misleading medical connotations. |
| *en puissance / virtualité* | **in potentiality / potentiality** | `in potency` | Standardizes scholastic philosophical usage across the entire corpus. |
| *en acte* | **in actuality / actuality** | `in act` | Modern philosophical English for Aristotelian *energeia / entelecheia*. |
| *le vulgaire / la foule* | **common people / multitude** | `the vulgar` | Eliminates the modern English pejorative moral sense of "vulgar". |
| *intelligences séparées / choses séparées* | **separate** (e.g. *separate intelligences*) | `separated` | Idiomatic philosophical English for actual separate substances (rather than participial past action). |
| *moteur / premier moteur* | **mover(s) / Prime Mover** | `motor(s) / First Motor` | Standard Aristotelian English; avoids modern mechanical engine connotations. |
| *les tables (de la Loi)* | **Tablets (of the Law)** | `Tables (of the Law)` | Standard modern English for the Decalogue tablets (*luḥot*). |
| *corporéité* | **corporeality** | `corporeity` | Standard modern philosophical form. |
| *mouvement(s)* | **motion(s)** in physics/astronomy;<br>**movement(s)** in general prose | Indiscriminate usage | Use "motion" when discussing cosmology, mechanics, and spheres (e.g. *motion of the sphere*, *laws of motion*); preserve "movement" in general prose. |

### C. Category B Cognate Pairs (Table 2: Direct French Cognate Restorations)
In accordance with user approval, all 25 cognate departures where `v2` substituted non-cognate synonyms or stylistic variations must be reverted to Munk's direct English cognates from `v1`:

| # | Munk 1856 French | Mandatory `v2` Cognate (`v1`) | Prohibited Substitution | Example Target Segments / Footnotes |
| :---: | :--- | :--- | :--- | :--- |
| 1 | *portent / porte (les mss. portent)* | **bear / bears** (*the MSS. bear*) | `read / reads / have` | `root.text.Part 1..40.0`, `fn.180`, `fn.194`, `fn.200` |
| 2 | *sens (dans le sens de)* | **sense(s)** | `meaning(s)` | `root.text.Part 1..19.4`, `root.text.Part 1..26.0`, `root.text.Part 1..34.3` |
| 3 | *commencement / commencer* | **commencement / commence(s/d)** | `beginning / begin(s) / began` | `root.text.Part 1.Introduction.14`, `root.text.Part 1..32.0`, `root.text.Part 1..33.8` |
| 4 | *idée(s)* | **idea(s)** | `concept(s) / notion(s)` | `root.text.Part 1..35.6`, `root.text.Part 1..56.1`, `root.text.Part 1..59.4` |
| 5 | *exposé / exposer / exposerons* | **set forth / expound(ed)** | `explain(ed)` | `root.text.Part 1..30.6`, `root.text.Part 1..33.8`, `root.text.Part 1..38.6` |
| 6 | *signification(s) / signifie(nt)* | **signification(s) / signif(y/ies/ied)**| `meaning(s) / mean(s/t)` | `root.text.Part 1..23.3`, `root.text.Part 1..24.0`, `root.text.Part 1..27.6` |
| 7 | *science(s) (la science de Dieu)* | **science(s)** (e.g. *my science*) | `knowledge / learning` | `root.text.Prefatory Remarks.2`, `root.text.Part 1..33.1`, `root.text.Part 1..33.9` |
| 8 | *employer / employé(e)* | **employ(s/ed/ing)** | `use(s/d) / using` | `root.text.Part 1..21.0`, `root.text.Part 1..22.1`, `root.text.Part 1..23.0` |
| 9 | *manifeste / manifester* | **manifest(ed)** | `clear / evident / reveal(ed)` | `root.text.Part 1.Introduction.6`, `root.text.Part 1..36.2`, `root.text.Part 1..53.4` |
| 10 | *primitif / primitivement* | **primitive / primarily** | `original / originally / primary` | `root.text.Part 1..8.0`, `root.text.Part 1..10.0`, `root.text.Part 1..17.0` |
| 11 | *comprendre / comprend* | **comprehend(s/ed/ing)** | `understand(s/ing) / understood`| `root.text.Part 1..52.1`, `root.text.Part 1..54.1`, `root.text.Part 1..55.2` |
| 12 | *phrase(s) (cette phrase)* | **phrase(s)** | `sentence(s) / clause(s)` | `fn.657`, `fn.678`, `fn.724`, `fn.1356` |
| 13 | *mot à mot* | **word for word** | `literally` | `fn.2212`, `fn.2936`, `fn.2940`, `fn.2979` |
| 14 | *langue (dans notre langue)* | **tongue(s)** | `language(s)` | `root.text.Part 1..20.5`, `root.text.Part 1..21.0`, `root.text.Part 1..29.0` |
| 15 | *contestation / contester* | **contest(ation)** | `dispute / controversy` | `root.text.Part 1..30.2`, `root.text.Part 1..70.14`, `root.text.Part 1..73.5` |
| 16 | *histoire (l'histoire d'Adam/Job)* | **history** | `story / account` | `root.text.Part 2..31.4`, `root.text.Part 3..21.0`, `root.text.Part 3..22.0` |
| 17 | *relation (relation de la création)* | **relation** | `account` | `root.text.Part 1..26.2`, `root.text.Part 1..70.17`, `fn.209` |
| 18 | *mouvement local / locomotion* | **local (movement/motion)** | `spatial / locomotion` | `root.text.Part 1..17.1`, `root.text.Part 1..17.3`, `root.text.Part 1..19.3` |
| 19 | *repos* | **repose** | `rest` | `root.text.Part 1..25.2`, `root.text.Part 1..66.0`, `fn.779`, `fn.996` |
| 20 | *convenable* | **convenient** | `suitable / fitting / appropriate` | `root.text.Part 1..45.8`, `root.text.Part 2.Introduction.35` |
| 21 | *exercé (dans les sciences)* | **exercised** | `trained` | `root.text.Part 1..33.1`, `root.text.Part 1..33.6`, `root.text.Part 2..31.3` |
| 22 | *peine et fatigue* | **pain and fatigue** | `toil and weariness` | `root.text.Part 1.Introduction.14` |
| 23 | *sacerdotale (bénédiction)* | **sacerdotal** | `priestly` | `root.text.Part 1..60.0.sub_1`, `root.text.Part 1..61.1` |
| 24 | *abstenu (s'est abstenu)* | **abstained** | `refrained` | `root.text.Part 1..33.7`, `root.text.Part 1..40.1` |
| 25 | *fermées (les portes...)* | **closed** | `locked` | `root.text.Part 1.Introduction.14` |

### D. Rabbinic & Literary Terminology
| French / Source Term | Mandatory `v2` Rendering | Notes |
| :--- | :--- | :--- |
| *les docteurs de la Loi* | **the Sages of the Law** / **the Rabbis** | In halakhic/rabbinic contexts |
| *amphibologique* | **amphibolous term** | Term possessing multiple intermediate senses |
| *terme métaphorique* | **metaphorical term** | Figurative extension |
| *l'annexe (al-muḍāf)* | **the governing construct noun** | Grammatical construct state (*semikhut* / *iḍāfah*) |
| *aṣīlē bənē yisrā'ēl* | **Nobles of the children of Israel** | Exod. 24:11 (*‘Atzilim*) |
| *les Cabalistes* | **the Kabbalists** | Standard academic spelling |
| *Talmudistes* | **Talmudists** | |

### E. Philosophical & Theological Terminology
| Original / French Term | Mandatory `v2` Rendering | Semantic Context |
| :--- | :--- | :--- |
| *al-ma‘qūl / l'intelligible* | **intelligible** | Object of intellection |
| *al-‘āqil / l'intellectuel* | **intelligent subject / intellecting agent** | The knowing mind |
| *ha-sekhel ha-po‘el / al-‘aql al-fa‘‘āl* | **Active Intellect** | Capitalized when denoting the Tenth Separate Intellect |
| *al-khayāl / l'imagination* | **imagination** | The imaginative faculty |
| *al-mashhūrāt* | **conventional opinions** | Generally accepted/probable premises (*endoxa*) |
| *al-awwaliyyāt* | **primary intelligibles** | Self-evident first principles |
| *takhṣīṣ* | **particularization** (or **determination**) | Kalām argument for divine choice in creation |
| *kalam / mutakallimūn* | **Kalām / Mutakallimūn** | Capitalized proper nouns |
| *materia, forma, privatio* | **matter, form, privation** | Aristotelian triad (*hylē, morphē, sterēsis*) |
| *creatio ex nihilo* | **creation ex nihilo** (or **creation from nothing**) | |

---

## 5. Transliteration Standards

Transliteration of Hebrew, Aramaic, and Judeo-Arabic terms must follow standard modern academic conventions, replacing 19th-century French Orientalist transliterations:

### A. Consonants
- **Aleph / Hamza:** `’` (right curved apostrophe / modifier letter `U+02BC` or `’`).
- **Ayin:** `‘` (left curved apostrophe / modifier letter `U+02BB` or `‘`).
- **Shin:** `š` (or `sh` in common anglicized terms like *Shem*, *Shabbat*).
- **Sin:** `ś`.
- **Teth:** `ṭ`.
- **Tsade / Sad:** `ṣ`.
- **Ḥeth / Ḥa:** `ḥ`.
- **Khaf / Kha:** `kh` (or `ḫ`).
- **Dhal:** `ḏ`.
- **Ghain:** `ġ`.
- **Zha:** `ẓ`.

### B. Vowels & Macrons
- Long vowels use standard macrons: `ā`, `ī`, `ū`.
- Vocal shewa: `e` or `ə`.
- Proper names commonly known in English use standard academic forms: *Maimonides*, *Averroes*, *Avicenna*, *Alfarabi*, *Saadia*, *Onkelos*, *Ibn Tibbon*, *Al-Ḥarīzī*, *Pococke*.

---

## 6. Footnote Formatting Rules

### A. Apparatus Universe and Numbering
- The critical apparatus contains exactly **3,999 canonical footnotes** keyed strictly from `fn.0` through `fn.3998`.
- No sub-keys (such as `.sub_0`, `.sub_1`) or anomalous keys (such as `f1`, `f2`, `f3`) are permitted in `munk_production_v2.json`. All 54 legacy non-canonical keys from `v1` have been curated and merged into the canonical 3,999 apparatus entries.
- Exactly 3,997 footnote callouts appear in the text segments.
- Exactly two canonical footnotes (`fn.2525` and `fn.2642`) are uncalled editorial apparatus notes present in Munk's 1856 French edition and must be preserved in `"footnotes"`.

### B. Footnote Callout Syntax
- Every footnote callout in the body text MUST strictly follow the format: `[[fn:\d+]]` (e.g. `[[fn:12]]`).
- No marker may be omitted, re-ordered, or created. Footnote callouts must match the sequence of `munk_production_v1.json` 100%.

### C. Citation Punctuation and Abbreviations
In footnote text, cite biblical books, rabbinic treatises, and classical sources with standard academic abbreviations and colon notation:
- **Torah / Pentateuch:** `Gen. 1:1`, `Exod. 20:2`, `Lev. 19:18`, `Num. 6:24`, `Deut. 6:4`.
- **Historical Books:** `Josh. 1:1`, `Judg. 5:2`, `I Sam. 15:22`, `II Sam. 7:1`, `I Kings 8:27`, `II Kings 2:11`.
- **Prophets:** `Isa. 6:1`, `Jer. 1:5`, `Ezek. 1:1`, `Hos. 2:1`, `Amos 3:7`, `Mic. 6:8`, `Hab. 3:2`, `Mal. 3:1`.
- **Writings:** `Ps. 104:1`, `Prov. 3:5`, `Job 1:1`, `Song of Sol. 1:1`, `Eccles. 1:2`, `Dan. 7:9`.
- **Internal Cross-References:** `Part I, chap. XX`, `Part II, chap. VII`, `ibid., v. 5`, `supra, p. 45`, `infra, chap. XXX`.
- **Rabbinic Citations:** `B. Berakhot 31b`, `Mishnah Sanhedrin 10:1`, `Midrash Rabbah, Gen. § 8`.

### D. Critical Apparatus Integrity
- Footnotes in Munk's edition contain invaluable textual variants from Judeo-Arabic manuscripts (Oxford, Paris, Pococke), Ibn Tibbon’s Hebrew translation, and Judah al-Harizi’s translation.
- Translate Munk’s French discussions accurately into English while maintaining his precise textual citations and manuscript sigla (*les mss. portent* -> `the MSS. bear`).
- Ensure that quotations in Hebrew or Arabic within the footnotes are encased in `<span dir="rtl">...</span>`.

---

## Quality Assurance Checklist

Before any segment, chapter, or footnote revision is submitted, validated, or merged:

- [ ] **Apparatus Scope:** Does the corpus contain exactly 1,531 text segments and 3,999 canonical footnotes (`fn.0`..`fn.3998`)?
- [ ] **Anti-Truncation:** Do all segments and footnotes $\ge 30$ words retain $\ge 80\%$ of their `v1` word count? Are all 8 highlighted segments and 7 highlighted footnotes fully restored from Munk's French?
- [ ] **Completions Protection:** Are all 42+ genuine English completions (`Part 3..50.9.sub_0`, `fn.1756`, `fn.2606`, `fn.3009`, etc.) preserved without reverting to French?
- [ ] **Category A Reversions:** Are `homonym(s)/homonymous/homonymy`, `emanation`, `quiddity`, `the Eternal`, `is born and perishes/born/birth`, and the distinction between `intelligence(s)` and `intellect` strictly enforced?
- [ ] **Category A Retentions:** Are `Sages/Sage`, `in potentiality`, `in actuality`, `common people/multitude`, `separate`, `mover(s)/Prime Mover`, `Tablets (of the Law)`, `corporeality`, and `motion(s)` in physics correctly applied?
- [ ] **Category B Cognates:** Are all 25 rows of Table 2 cognate pairs (`the MSS. bear`, `sense(s)`, `commence`, `idea(s)`, `set forth`, `signification(s)`, `science(s)`, etc.) restored?
- [ ] **Archaism Ban:** Does the text contain zero prohibited archaisms (`thou`, `thee`, `hath`, `doth`, `whilst`, `unto`, `-eth`, `-est`, etc.)?
- [ ] **Scriptural Citations:** Are all citation numbers preserved exactly as Munk gave them ("Just Leave It"), with colon punctuation?
- [ ] **Tag Nesting & Balance:** Are all HTML tags (`<i>`, `<b>`, `<sup>`, `<sub>`, `<span>`, `<small>`) properly nested and closed in FIFO order?
- [ ] **RTL Semitic Spans:** Are all Hebrew and Arabic characters enclosed in `<span dir="rtl">` tags, with zero Latin characters trapped inside?
- [ ] **Fidelity & Zero External Contamination:** Does the text contain ZERO readings from unauthorized external translations (such as the 1903 edition), and ZERO occurrences of the prohibited name?
- [ ] **Validator Passing:** Does `StrictApparatusValidator` report exactly 0 errors?
