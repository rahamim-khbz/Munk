# Munk Second Edition (v2) Master Style Sheet & Emendation Guide

## Purpose & Scope
This document codifies the mandatory editorial standards, translation conventions, and apparatus integrity rules for the second edition (v2) of Salomon Munk’s translation of Moses Maimonides’ *Guide for the Perplexed* (*Dalālat al-Ḥā’irīn* / *Moreh Nevukhim*).

All human editors, translator subagents, verifier subagents, and automated quality gates must strictly adhere to these standards.

---

## 1. Translation Scope and Scholarly Revision

The second edition is a comprehensive scholarly revision of both the main text (1,531 segments) and the entire critical apparatus (4,053 footnotes):

1. **Academic English Prose (1950s Standard):**
   - Translate Salomon Munk’s 19th-century French (*Le Guide des Égarés*, 1856–1866) into fluent, dignified, and precise mid-20th-century academic English.
   - Favor clarity, exact philosophical equivalence, and grammatical elegance over literal word-for-word calques.
   - Avoid modern colloquialisms or anachronistic idioms; preserve the elevated register suitable for a seminal philosophical treatise.

2. **Complete Recovery of Untranslated Passages:**
   - Translate all residual French phrases, clauses, citations, and sentences left untranslated in v1 into English.
   - Translate all Latin drafting relics (e.g., *materia, forma, privatio*, *ex nihilo*, *stare*, *cessare*, *implere*) into standard English philosophical equivalents, providing the Latin/Greek/Arabic technical term only where Munk explicitly analyzes the philology.

3. **Correction of Translation Errors & Severed Syntax:**
   - Repair fractured sentences, dangling modifiers, drafting collisions, and severed clauses inherited from earlier OCR or automated drafts.
   - Cross-check questionable English readings against Munk’s French text (1856 edition) and, where ambiguous, against the Judeo-Arabic original (*Dalālat al-Ḥā’irīn*) and Ibn Tibbon’s Hebrew version.

4. **Preservation of Apparatus & Markup:**
   - Preserve 100% of HTML tags (`<i>`, `<b>`, `<sup>`, `<span dir="rtl">`, `<small>`).
   - All Hebrew, Aramaic, and Arabic script MUST be enclosed within `<span dir="rtl">...</span>`.
   - Never strip, displace, or corrupt footnote callouts (`[[fn:\d+]]`).

---

## 2. Scriptural Citation Standard ('Just Leave It')

When Salomon Munk’s French text provides a specific chapter and verse citation (e.g., citing `Ps. 114, 14` or `Isa. 21, 2`):

1. **Leave Munk's Citation Numbers Intact:**
   - Strictly leave Munk's verse numbers as he gave them in the 1856 French edition.
   - Standardize ONLY the punctuation (e.g., convert comma to colon: `Ps. 114, 14` -> `Ps. 114:14`).
   - **DO NOT** replace Munk's verse numbering with modern Hebrew Bible (Masoretic) versification or Christian Vulgate versification (e.g., do not alter `Ps. 114:14` to `Ps. 102:14`). The pipeline must not second-guess Munk's source text or printings.

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

*Note:* Biblical quotations translated in the text should follow clear, elevated modern English rather than pseudo-Jacobean pastiche.

---

## 4. Mandatory Terminology Lexicon

Align terminology systematically with rabbinic scholarship and José Faur (*Homo Mysticus: A Guide for Maimonides’s Guide for the Perplexed*):

### A. Rabbinic & Literary Terminology
| French / Obsolete Term | Mandatory v2 Rendering | Notes |
| :--- | :--- | :--- |
| *les docteurs* | **the Sages** (or **the Rabbis**) | When referring to Hazal / Talmudic rabbis |
| *les docteurs de la Loi* | **the Sages of the Law** / **the Rabbis** | |
| *homonyme* | **equivocal term** | Default in semantic chapters (or *metaphorical term* / *amphibolous term* per context) |
| *amphibologique* | **amphibolous term** | Having multiple intermediate senses |
| *terme métaphorique* | **metaphorical term** | Figurative extension |
| *l'annexe* (*al-muḍāf*) | **the governing construct noun** | Grammatical construct state (*semikhut* / *iḍāfah*) |
| *aṣīlē bənē yisrā'ēl* | **Nobles of the children of Israel** | Exod. 24:11 (*‘Atzilim*) |
| *les Cabalistes* | **the Kabbalists** | Standard academic spelling |
| *Talmudistes* | **Talmudists** | |

### B. Philosophical & Theological Terminology (Faur / Classical Aristotelianism)
| Original / French Term | Mandatory v2 Rendering | Semantic Context |
| :--- | :--- | :--- |
| *al-‘aql* / *l'intellect* | **intellect** | The intellectual faculty or substance |
| *al-ma‘qūl* / *l'intelligible* | **intelligible** | Object of intellection |
| *al-‘āqil* / *l'intellectuel* | **intelligent subject** / **intellecting agent** | The knowing mind |
| *ha-sekhel ha-po‘el* / *al-‘aql al-fa‘‘āl* | **Active Intellect** | Capitalized when denoting the Tenth Separate Intellect |
| *al-khayāl* / *l'imagination* | **imagination** | The imaginative faculty |
| *al-mashhūrāt* | **conventional opinions** | Generally accepted/probable premises (*endoxa*) |
| *al-awwaliyyāt* | **primary intelligibles** | Self-evident first principles |
| *fayd* / *l'émanation* | **divine overflow** (or **emanation**) | Overflow of intellect and being |
| *takhṣīṣ* | **particularization** (or **determination**) | Kalām argument for divine choice in creation |
| *kalam* / *mutakallimūn* | **Kalām** / **Mutakallimūn** | Capitalized proper nouns |
| *materia, forma, privatio* | **matter, form, privation** | Aristotelian triad (*hylē*, *morphē*, *sterēsis*) |
| *creatio ex nihilo* | **creation ex nihilo** (or **creation from nothing**) | |

---

## 5. Transliteration Standards

Transliteration of Hebrew, Aramaic, and Judeo-Arabic terms must follow standard academic conventions:

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

### B. Vowels
- Long vowels use standard macrons: `ā`, `ī`, `ū`.
- Vocal shewa: `e` or `ə`.
- Proper names commonly known in English may use standard academic forms: *Maimonides*, *Averroes*, *Avicenna*, *Alfarabi*, *Saadia*, *Onkelos*, *Ibn Tibbon*, *Harizi*, *Pococke*.

---

## 6. Footnote Formatting Rules

### A. Footnote Callout Syntax
- Every footnote callout in the body text MUST strictly follow the format: `[[fn:\d+]]` (e.g. `[[fn:12]]`).
- No marker may be omitted, re-ordered, or created without matching an apparatus entry.

### B. Citation Punctuation and Abbreviations
In footnote text, cite biblical books, rabbinic treatises, and classical sources with standard academic abbreviations and colon notation:

- **Torah / Pentateuch:** `Gen. 1:1`, `Exod. 20:2`, `Lev. 19:18`, `Num. 6:24`, `Deut. 6:4`.
- **Historical Books:** `Josh. 1:1`, `Judg. 5:2`, `I Sam. 15:22`, `II Sam. 7:1`, `I Kings 8:27`, `II Kings 2:11`.
- **Prophets:** `Isa. 6:1`, `Jer. 1:5`, `Ezek. 1:1`, `Hos. 2:1`, `Amos 3:7`, `Mic. 6:8`, `Hab. 3:2`, `Mal. 3:1`.
- **Writings:** `Ps. 104:1`, `Prov. 3:5`, `Job 1:1`, `Song of Sol. 1:1`, `Eccles. 1:2`, `Dan. 7:9`.
- **Internal Cross-References:** `Part I, chap. XX`, `Part II, chap. VII`, `ibid., v. 5`, `supra, p. 45`, `infra, chap. XXX`.
- **Rabbinic Citations:** `B. Berakhot 31b`, `Mishnah Sanhedrin 10:1`, `Midrash Rabbah, Gen. § 8`.

### C. Critical Apparatus Integrity
- Footnotes in Munk's edition contain invaluable textual variants from Judeo-Arabic manuscripts (Oxford, Paris, Pococke), Ibn Tibbon’s Hebrew translation, and Judah al-Harizi’s translation.
- Translate Munk’s French discussions accurately into English while maintaining his precise textual citations and manuscript sigla.
- Ensure that quotations in Hebrew or Arabic within the footnotes are encased in `<span dir="rtl">...</span>`.

---

## 7. Quality Assurance Checklist

Before any shard or chapter review is submitted or merged:

- [ ] Does the text contain any prohibited archaisms (`thou`, `hath`, `whilst`, etc.)?
- [ ] Are all scriptural citation numbers preserved as Munk gave them ("Just Leave It")?
- [ ] Have all French and Latin drafting relics been fully translated into English?
- [ ] Are all `[[fn:\d+]]` callouts intact and identical to the original sequence?
- [ ] Are all HTML tags correctly paired and closed?
- [ ] Are all Hebrew/Arabic words wrapped in `<span dir="rtl">` tags?
- [ ] Does the terminology match the Mandatory Terminology Lexicon?
