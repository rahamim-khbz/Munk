# Scholarly Review Audit: Part 1, Chapter 4

**Date:** 2026-10-13 13:44:03 UTC  
**Target:** Munk English Translation - Second Edition (`munk_production_v2.json`)  
**Review Engine:** `gemini-3.8-flash`  

## Summary Metrics

- Total Segments Evaluated: 5
- Unchanged: 0 (0.0%)
- Modified: 5 (100.0%)

### Flags Breakdown

- **`archaism_purge`**: 2
- **`critical_markup_repair`**: 1
- **`typo_repair`**: 1
- **`faur_arbitration`**: 1
- **`scripture_accuracy`**: 1
- **`philosophical_lexicon`**: 1
- **`philosophical_style_polish`**: 1
- **`markup_repair`**: 1
- **`de_gallicization`**: 1

---

## Detailed Modification Audit

### 1. Segment: `root.text.Part 1..3.0`

**Flags:** `critical_markup_repair`, `typo_repair`, `faur_arbitration`  
**Rationale:** Repaired broken HTML tags and corrupted Hebrew typo (הזה -> חזה), and rendered al-idrak al-'aqli as intellectual apprehension.

| Layer | Text |
| :--- | :--- |
| **v1 English (Original)** | Be aware that the three verbs <i>raâ</i> (<span dir="rtl">ראה</span>), <i>hibbît</i> (<span dir="rtl">הביט</span>), and <i>’</i>hazâ<span dir="rtl"> (</span>הזה</span>) are applied to the vision of the eye; however, they are all employed metaphorically for the perception of the intellect. |
| **v2 English (Reviewed)** | **Know that the three verbs <i>raâ</i> (<span dir="rtl">ראה</span>), <i>hibbît</i> (<span dir="rtl">הביט</span>), and <i>ḥazâ</i> (<span dir="rtl">חזה</span>) apply to the vision of the eye; however, they are all employed metaphorically for intellectual apprehension.** |
| **Munk French** | Sache que les trois verbes <i>raâ</i> (<span dir="rtl">ראה</span>), <i>hibbît</i> (<span dir="rtl">הביט</span>) et ’<i>hazâ</i> (<span dir="rtl">הזה</span>) s’appliquent à la <i>vue</i> de l’œil; mais on les emploie métaphoriquement, tous les trois, pour la perception de l’intelligence. |
| **Judeo-Arabic** | <span dir="rtl">אעלם אן ראה והביט וחזה ת'לת'הֵ הד'ה אלאלפאט' תקע עלי רויהֵ אלעין ואסתעירת ת'לאת'תהא לאדראך אלעקל.</span> |

---

### 2. Segment: `root.text.Part 1..3.1`

**Flags:** `scripture_accuracy`  
**Rationale:** Rendered Eccl 1:16 (da'at) accurately as knowledge; preserved [[fn:77]].

| Layer | Text |
| :--- | :--- |
| **v1 English (Original)** | With regard to <i>raâ</i> (<span dir="rtl">ראה</span>), this is well-known to everyone. It is said, for example: <i>And he saw</i> (<span dir="rtl">וירא</span>), <i>and behold, there was a well in the field</i> (Genesis, 29, 2), where it concerns the vision of the eye; however, in these words: <i>And my heart saw</i> (<span dir="rtl">ראה</span>) <i>much wisdom and knowledge</i> (Ecclesiastes, 1, 16), it concerns an intellect perception. |
| **v2 English (Reviewed)** | **With regard to <i>raâ</i> (<span dir="rtl">ראה</span>), this is well-known to everyone. It is said, for example: <i>And he saw</i> (<span dir="rtl">וירא</span>), <i>and behold, there was a well in the field</i> (Genesis, 29, 2), where it concerns the vision of the eye; however, in these words: <i>And my heart saw</i> (<span dir="rtl">ראה</span>) <i>much wisdom and knowledge</i> (Ecclesiastes, 1, 16), it concerns an intellect perception.** |
| **Munk French** | Pour <i>raâ</i> (<span dir="rtl">ראה</span>), cela est connu à tout le monde. Il est dit, p. ex.: <i>Et il vit</i> (<span dir="rtl">וירא</span>), <i>et voici, il y avait un puits dans le champ</i> (Genèse, 29, 2), où il s’agit de la <i>vue</i> de l’œil; mais dans ces mots: <i>Et mon cœur voyait</i> (<span dir="rtl">ראה</span>) <i>beaucoup de sagesse et de science</i> (Ecclésiaste, 1, 16), il s’agit d’une perception intellectuelle. |
| **Judeo-Arabic** | <span dir="rtl">אמא ד'לך פי ראה פמשהור ענד אלג'מהור קאל וירא והנה באר בשדה והד'ה רויהֵ עין וקאל ולבי ראה הרבה חכמה ודעת והד'א אדראך עקלי.</span> |

---

### 3. Segment: `root.text.Part 1..3.2`

**Flags:** `archaism_purge`, `philosophical_lexicon`  
**Rationale:** Purged archaic "I pray thee", modernized theological pronouns, and rendered burhan as demonstration.

| Layer | Text |
| :--- | :--- |
| **v1 English (Original)** | It is in this metaphorical sense that the verb <i>raâ</i> (<span dir="rtl">ראה</span>) must be understood whenever it is applied to God, as for example in these passages: <i>I</i> <small>saw</small> (<span dir="rtl">ראיתי</span>) <i>the Lord</i> (I Kings, 22, 19); <i>And the Lord appeared</i> <small>to him</small> (Genesis, 18, 1); <i>And God </i> <i>saw</i> <small>that it was good</small> (Genesis, 1, <i>passim</i>); <i>Show me</i> <i>your glory</i> (Exodus, 33, 18); <small>And they </small> <i>saw</i> <i>the God of Israel</i> (<small>Ibid.</small>, 24, 10). In all these instances, it is a matter of intellectual perception, and not at all of the vision of the eye; for the eyes only perceive (what is) corporeal and (only) from a certain side[[fn:77]], and with this, some accidents of the body, such as its colours, its geometric figure, etc., and God, on His part, does not perceive by means of an instrument, as will be explained (later). |
| **v2 English (Reviewed)** | **It is in this metaphorical sense that the verb <i>raâ</i> (<span dir="rtl">ראה</span>) must be understood whenever it is applied to God, as for example in these passages: <i>I</i> <small>saw</small> (<span dir="rtl">ראיתי</span>) <i>the Lord</i> (I Kings, 22, 19); <i>And the Lord appeared</i> <small>to him</small> (Genesis, 18, 1); <i>And God </i> <i>saw</i> <small>that it was good</small> (Genesis, 1, <i>passim</i>); <i>Show me</i> <i>your glory</i> (Exodus, 33, 18); <small>And they </small> <i>saw</i> <i>the God of Israel</i> (<small>Ibid.</small>, 24, 10). In all these instances, it is a matter of intellectual perception, and not at all of the vision of the eye; for the eyes only perceive (what is) corporeal and (only) from a certain side[[fn:77]], and with this, some accidents of the body, such as its colours, its geometric figure, etc., and God, on His part, does not perceive by means of an instrument, as will be explained (later).** |
| **Munk French** | C’est dans ce sens métaphorique qu’il faut prendre le verbe <i>raâ</i> (<span dir="rtl">ראה</span>) toutes les fois qu’il s’applique à Dieu, comme p. ex. dans ces passages: <i>Je</i> <small>VIS</small> (<span dir="rtl">ראיתי</span>) <i>l’Éternel</i> (I Rois, 22, 19); <i>Et l’Éternel se fit</i> <small>VOIR</small> (apparut) <i>à lui</i> (Genèse, 18, 1); <i>Et Dieu</i> <small>VIT</small> <i>que c’était bien</i> (Genèse, 1, <i>passim</i>); <i>Fais-moi</i> <small>VOIR</small> <i>ta gloire</i> Exod., 33, 18); <i>Et ils</i> <small>VIRENT</small> <i>le Dieu d’Israël</i> (<i>Ibid.</i>, 24, 10). Il s’agit ici partout d’une perception intellectuelle, et nullement de la <i>vue</i> de l’œil; car les yeux ne perçoivent que (ce qui est) corps et (seulement) d’un certain côté<sup class="footnote-marker">(1)</sup><i class="footnote">Les éditions de la version hébraïque d’Ibn-Tibbon portent généralement <span dir="rtl">ובצדו קצת מקריו</span>; il faut lire, selon l’arabe: <span dir="rtl">ובצד וקצת מקריו</span>, comme l’ont en effet les mss. de ladite version.</i>, et avec cela quelques accidents du corps, tels que ses couleurs, sa figure (géométrique), etc., et Dieu, de son côté, ne perçoit pas au moyen d’un instrument, comme on l’expliquera (plus loin). |
| **Judeo-Arabic** | <span dir="rtl">ובחסב הד'ה אלאסתעארה הו כל לשון ראיה ג'א פי אללה תעאלי מת'ל קולה ראיתי את י"י וירא אליו י"י וירא אלהים כי טוב הראני נא את כבודך ויראו את אלהי ישראל כל ד'לך אדראך עקלי לא רויהֵ עין בוג'ה אד' לא תדרך אלאעין אלא ג'סמא ופי ג'הה ובעץ' אעראצ'ה איצ'א אעני אלואן אלג'סם ושכלה ונחוהא וכד'לך הו תעאלי לא ידרך באלה כמא סיבין.</span> |

---

### 4. Segment: `root.text.Part 1..3.3`

**Flags:** `archaism_purge`, `philosophical_style_polish`  
**Rationale:** Purged archaic "thee", elevated philosophical terminology, and preserved [[fn:78]].

| Layer | Text |
| :--- | :--- |
| **v1 English (Original)** | Similarly, <i>hibbît</i> (<span dir="rtl">הביט</span>) is used in the sense of: <i>looking</i> at a thing with the eye; for example: <i>Do not look</i> <span dir="rtl">אל תבט</span> <i>behind you</i> (Genesis, 19, 17); <i>And his wife looked</i> <span dir="rtl">ותבט</span>, <i>being behind him</i> (<i>Ibid.</i>, <small>V</small>. 26); <i>And he shall look</i> <span dir="rtl">ונבט</span> <i>toward the earth</i> (Isaiah, 5, 30). But it is used metaphorically for theintuition of the mind approaching the consideration of a thing in order to understand it, as in this passage: <i>No iniquity is seen</i> <i>לא הביט</i> <span dir="rtl">in Jacob</span> (Numbers, 23, 21); for iniquity is not seen with the eye. It is the same with these words: <i>And they looked</i> <i>והביטו</i> <span dir="rtl">after Moses</span> (Exodus, 33, 8); for, according to what the doctors say, they express the same idea, and they state that they (the Israelites) were watching his actions and words and examining them[[fn:78]]. The words: <i>Look</i> <i>הבט</i> <span dir="rtl">toward the heaven</span> (Genesis, 15, 5), have the same meaning; for this took place in a prophetic vision. And (in general) the verb <i>הביט</i> (to look) has this metaphorical sense whenever it is applied to God; for example: … <span dir="rtl">to look</span> <i>מהביט</i> <span dir="rtl">toward God</span> (Exodus, 3, 6); <i>And he contemplates</i> <i>יביט</i> <span dir="rtl">the figure of God</span> (Numbers, 12, 8); <i>And you can not look</i> <i>והביט</i> <span dir="rtl">at iniquity</span> (Habakkuk, 1, 13). |
| **v2 English (Reviewed)** | **Similarly, <i>hibbît</i> (<span dir="rtl">הביט</span>) is used in the sense of: <i>looking</i> at a thing with the eye; for example: <i>Do not look</i> <span dir="rtl">אל תבט</span> <i>behind you</i> (Genesis, 19, 17); <i>And his wife looked</i> <span dir="rtl">ותבט</span>, <i>being behind him</i> (<i>Ibid.</i>, <small>V</small>. 26); <i>And he shall look</i> <span dir="rtl">ונבט</span> <i>toward the earth</i> (Isaiah, 5, 30). But it is used metaphorically for theintuition of the mind approaching the consideration of a thing in order to understand it, as in this passage: <i>No iniquity is seen</i> <i>לא הביט</i> <span dir="rtl">in Jacob</span> (Numbers, 23, 21); for iniquity is not seen with the eye. It is the same with these words: <i>And they looked</i> <i>והביטו</i> <span dir="rtl">after Moses</span> (Exodus, 33, 8); for, according to what the doctors say, they express the same idea, and they state that they (the Israelites) were watching his actions and words and examining them[[fn:78]]. The words: <i>Look</i> <i>הבט</i> <span dir="rtl">toward the heaven</span> (Genesis, 15, 5), have the same meaning; for this took place in a prophetic vision. And (in general) the verb <i>הביט</i> (to look) has this metaphorical sense whenever it is applied to God; for example: … <span dir="rtl">to look</span> <i>מהביט</i> <span dir="rtl">toward God</span> (Exodus, 3, 6); <i>And he contemplates</i> <i>יביט</i> <span dir="rtl">the figure of God</span> (Numbers, 12, 8); <i>And you can not look</i> <i>והביט</i> <span dir="rtl">at iniquity</span> (Habakkuk, 1, 13).** |
| **Munk French** | De même <i>hibbît</i> (<span dir="rtl">הביט</span>) s’emploie dans le sens de: <i>regarder</i> une chose avec l’œil; p. ex.: <i>Ne regarde pas</i> (<span dir="rtl">אל תבט</span>) <i>derrière toi</i> (Genèse, 19, 17): <i>Et sa femme regarda</i> (<span dir="rtl">ותבט</span>), <i>étant derrière lui</i> (<i>Ibid.</i>, <small>V</small>. 26); <i>Et il regardera</i> (<span dir="rtl">ונבט</span>) <i>vers la terre</i> (Isaïe, 5, 30). Mais on l’emploie métaphoriquement pour le <i>regard</i> de l’esprit abordant la considération d’une chose pour la comprendre, comme dans ce passage: <i>On ne voit pas</i> (<span dir="rtl">לא הביט</span>) <i>d’iniquité dans Jacob</i> (Nombres, 23, 21); car l’iniquité ne se voit pas avec l’œil. Il en est de même de ces paroles: <i>Et ils regardèrent</i> (<span dir="rtl">והביטו</span>) <i>après Moïse</i> (Exod., 33, 8); car, selon ce que disent les docteurs, elles exprimeraient la même idée, et elles énonceraient qu’ils (les Israélites) épiaient ses actes et ses paroles et les examinaient<sup class="footnote-marker">(1)</sup><i class="footnote">C’est-à-dire, ils les critiquaient et les jugeaient avec malveillance. L’auteur fait allusion à divers passages du Talmud et des Midraschîm. Ainsi, p. ex., le Talmud de Jérusalem (<i>Biccourîm</i>, ch. III, et <i>Schekalîm</i>, ch. V) parle de deux docteurs dont l’un avait expliqué le passage en question dans un sens d’éloge, et l’autre dans un sens de blâme; selon ce dernier, les Israélites disaient, en parlant de l’embonpoint de Moïse: «Voyez ses cuisses, voyez ses jambes; il mange de ce qui est aux juifs, il boit de ce qui est aux juifs, tout ce qu’il a vient des juifs.» <span dir="rtl">ומאן דאמר לגנאי חזי שאקי חזי כרעין אכיל מן יהודאי שתי מן יהודאי כל מרליה מן יהודאי</span>. Voyez aussi <i>Midrasch Tan’houma</i>, sect. <span dir="rtl">כי תשא</span> (édit. de Vérone, fol. 40 <i>d</i>); <i>Schemôth rabba</i>, sect. 51; Talmud de Babylone, <i>Kiddouschîn</i>, fol. 33 <i>b</i>. Il y en avait même, dit le Talmud ailleurs, qui allaient jusqu’à le soupçonner d’adultère: <span dir="rtl">שחשדוהו מאשת איש</span>. Voy. <i>Synhedrîn</i>, fol. 110 <i>a</i>.</i>. Les mots: <i>Regarde</i> (<span dir="rtl">הבט</span>) <i>donc vers le ciel</i> (Genèse, 15, 5), ont encore le même sens; car cela se passait dans une vision prophétique. Et (en général) le verbe <span dir="rtl">הביט</span> (regarder) a ce sens métaphorique toutes les fois qu’il s’applique à Dieu; p. ex.: ….. <i>de regarder</i> (<span dir="rtl">מהביט</span>) <i>vers Dieu</i> (Exod., 3, 6); <i>Et il contemple</i> (<span dir="rtl">יביט</span>) <i>la figure de Dieu</i> (Nombres, 12, 8); <i>Et tu ne peux regarder</i> (<span dir="rtl">והביט</span>) <i>l’iniquité</i> (Habac., I, 13). |
| **Judeo-Arabic** | <span dir="rtl">וכד'לך הביט יקע עלי אלאלתפאת באלעין ללשי אל תביט אחריך ותבט אשתו מאחריו ונבט לארץ. ואסתעיר אלי אלתפאת אלד'הן ואקבאלה עלי תאמל אלשי חתי ידרכה והו קולה לא הביט און ביעקב לאן אלאון לא ירי באלעין וכד'לך קולה והביטו אחרי משה קאלוא אלחכמים ז"ל אן פיה איצ'א הד'א אלמעני ואנה אכ'באר ען כונהם יתעקבון אפעאלה ואקואלה ויתאמלונהא. ומן הד'א אלמעני קולה הבט נא השמימה לאן ד'לך כאן במראה הנבואה. ועלי הד'ה אלאסתעארה הו כל לשון הבטה ג'את פי אללה תעאלי מהביט אל האלהים ותמונת י"י יביט והביט אל עמל לא תוכל.</span> |

---

### 5. Segment: `root.text.Part 1..3.4`

**Flags:** `markup_repair`, `de_gallicization`  
**Rationale:** Repaired corrupted inline Hebrew tag and eliminated awkward Gallicism ("penetrate it").

| Layer | Text |
| :--- | :--- |
| **v1 English (Original)** | Similarly, ’<i>hazâ</i> (<span dir="rtl">חזה</span>) applies to the vision of the eye; for example: <i>And our eyes shall see</i> <i>ותחז</i> <span dir="rtl">the fall of Zion</span> (Micah, 4, 11); and it is used metaphorically for the perception of the heart, for example: … <i>he saw</i> <i>חזה</i> <span dir="rtl">upon Judah and Jerusalem</span> (Isaiah, 1, 1); … <i>the word of the Lord to Abram</i> <i>במחזה</i> <span dir="rtl">in a vision</span> (Genesis, 15, 1); and according to this metaphor it has been said: <i>And they saw</i> <i>ויחזו</i> <span dir="rtl">God</span> (Exodus, 24, 11). You must thoroughly understand this. |
| **v2 English (Reviewed)** | **Similarly, ’<i>hazâ</i> (<span dir="rtl">חזה</span>) applies to the vision of the eye; for example: <i>And our eyes shall see</i> <i>ותחז</i> <span dir="rtl">the fall of Zion</span> (Micah, 4, 11); and it is used metaphorically for the perception of the heart, for example: … <i>he saw</i> <i>חזה</i> <span dir="rtl">upon Judah and Jerusalem</span> (Isaiah, 1, 1); … <i>the word of the Lord to Abram</i> <i>במחזה</i> <span dir="rtl">in a vision</span> (Genesis, 15, 1); and according to this metaphor it has been said: <i>And they saw</i> <i>ויחזו</i> <span dir="rtl">God</span> (Exodus, 24, 11). You must thoroughly understand this.** |
| **Munk French** | De même ’<i>hazâ</i> (<span dir="rtl">חזה</span>) s’applique à la <i>vue</i> de l’œil; p. ex.: <i>Et que nos yeux voient</i> (<span dir="rtl">ותחז</span>) <i>la chute de Sion</i> (Micha, 4, 11); et on l’emploie métaphoriquement pour la perception du cœur, p. ex.: … <i>qu’il vit</i> (<span dir="rtl">חזה</span>) <i>sur Juda et Jérusalem</i> (Isaïe, 1, 1); … <i>la parole de l’Éternel à Abrâm</i> (<span dir="rtl">במחזה</span>) <i>dans une vision</i> (Genèse, 15, 1); et selon cette métaphore il a été dit: <i>Et ils virent</i> (<span dir="rtl">ויחזו</span>) <i>Dieu</i> (Exod., 24, 11). Il faut bien te pénétrer de cela. |
| **Judeo-Arabic** | <span dir="rtl">וכד'לך חזה יקע עלי רויהֵ אלעין ותחז בציון עינינו. ואסתעיר לאדראך אלקלב אשר חזה על יהודה וירושלם היה דבר י"י אל אברם במחזה. ועלי הד'ה אלאסתעארה קיל ויחזו את האלהים פאעלם ד'לך:</span> |

---

## Unchanged Segments

Count: 0 segments verified and preserved byte-for-byte.
