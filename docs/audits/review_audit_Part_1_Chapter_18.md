# Scholarly Review Audit: Part 1, Chapter 18

**Date:** 2026-10-14 00:20:18 UTC  
**Target:** Munk English Translation - Second Edition (`munk_production_v2.json`)  
**Review Engine:** `gemini-3.8-flash`  

## Summary Metrics

- Total Segments Evaluated: 7
- Unchanged: 0 (0.0%)
- Modified: 7 (100.0%)

### Flags Breakdown

- **`style_modernization`**: 6
- **`citation_standardization`**: 4
- **`ocr_repair`**: 1
- **`untranslated_repair`**: 1

---

## Detailed Modification Audit

### 1. Segment: `root.text.Part 1..17.0`

**Flags:** `ocr_repair`, `style_modernization`, `citation_standardization`  
**Rationale:** Corrected Hebrew OCR typo in Exod. 4:25: ותנע -> ותגע (nun to gimel); standardized citations (Exod. 32:19, ibid., 14:10, ibid., 4:25, Isa. 6:7, Gen. 44:18).

| Layer | Text |
| :--- | :--- |
| **v1 English (Original)** | <i>Karab</i> (<span dir="rtl">קרב</span>), <i>naga’</i> (<span dir="rtl">נגע</span>) and <i>nagasch</i> (<span dir="rtl">נגש</span>). — These three words sometimes have the meaning <i>of approaching</i> (<i>touching</i>), <i>drawing near</i> in space, and sometimes they express the union of knowledge with the thing known, (a union) which is compared, in some way, to one body <i>approaching</i> another body. — As for the primitive meaning of <i>karab</i>, which is that of <i>drawing near</i> in space (here are examples): <i>When he drew near</i> (<span dir="rtl">קרב</span>) <i>to the camp</i> (Exodus, 32, 19); <i>And Pharaoh drew near</i> (<span dir="rtl">הקריב</span>) (<i>Ibid.</i>, 14, 10). <i>Naga</i>’ primitively expresses the bringing into contact of one body with another; for example: <i>She touched</i> (<span dir="rtl">ותנע</span>) <i>his feet</i> (<i>Ibid.</i>, 4, 25); <i>He touched</i> (<span dir="rtl">ויגע</span>) <i>my mouth</i> (Isaiah, 6, 7). The primitive meaning of <i>nagasch</i> is <i>to advance</i> towards a person, <i>to move</i> towards him; for example: <i>And Judah advanced</i> (<span dir="rtl">ויגש</span>) <i>towards him</i> (Genesis, 44, 18). |
| **v2 English (Reviewed)** | **<i>Qārav</i> (<span dir="rtl">קרב</span>), <i>nāga‘</i> (<span dir="rtl">נגע</span>), and <i>nāgaš</i> (<span dir="rtl">נגש</span>). — These three verbs sometimes have the meaning of <i>approaching</i> (or <i>touching</i>), of <i>drawing near</i> in space, and sometimes they express the conjunction of knowledge with the object known—a conjunction which is compared in a certain manner to one body <i>drawing near</i> to another body. — As for the primary meaning of <i>qārav</i>, which is that of <i>drawing near</i> in space, here are examples: <i>When he came near</i> (<span dir="rtl">קרב</span>) <i>to the camp</i> (Exod. 32:19); <i>And Pharaoh drew near</i> (<span dir="rtl">הקריב</span>) (<i>ibid.</i>, 14:10). <i>Nāga‘</i> primarily expresses the bringing into contact of one body with another; e.g.: <i>And she touched</i> (<span dir="rtl">ותגע</span>) <i>his feet</i> (<i>ibid.</i>, 4:25); <i>And he touched</i> (<span dir="rtl">ויגע</span>) <i>my mouth</i> (Isa. 6:7). The primary meaning of <i>nāgaš</i> is <i>to advance</i> toward someone, <i>to move</i> toward him; e.g.: <i>Then Judah came near</i> (<span dir="rtl">ויגש</span>) <i>unto him</i> (Gen. 44:18).** |
| **Munk French** | <i>Karab</i> (<span dir="rtl">קרב</span>), <i>naga’</i> (<span dir="rtl">נגע</span>) et <i>nagasch</i> (<span dir="rtl">נגש</span>). — Ces trois mots ont tantôt le sens <i>d’aborder</i> (<i>toucher</i>), <i>s’approcher</i> dans l’espace, tantôt ils expriment la réunion de la science avec la chose sue, (réunion) que l’on compare en quelque sorte à un corps <i>s’approchant</i> d’un autre corps. — Quant au sens primitif de <i>karab</i>, qui est celui du <i>rapprochement</i> dans l’espace (en voici des exemples): <i>Lorsqu’il s’approcha</i> (<span dir="rtl">קרב</span>) <i>du camp</i> (Exode, 32, 19); <i>Et Pharaon s’approcha</i> (<span dir="rtl">הקריב</span>) (<i>Ibid.</i>, 14, 10). <i>Naga</i>’ exprime primitivement la mise en contact d’un corps avec un autre; p. ex.: <i>Elle en toucha</i> (<span dir="rtl">ותנע</span>) <i>ses pieds</i> (<i>Ibid.</i>, 4, 25); <i>Il en toucha</i> (<span dir="rtl">ויגע</span>) <i>ma bouche</i> (Isaïe, 6, 7). Le sens primitif de <i>nagasch</i> est <i>s’avancer</i> vers une personne, <i>se mouvoir</i> vers elle; p. ex.: <i>Et Juda s’avança</i> (<span dir="rtl">ויגש</span>) <i>vers lui</i> (Genèse, 44, 18). |
| **Judeo-Arabic** | <span dir="rtl">קרב ונגע ונגש. הד'ה אלת'לת'ה אסמא אעני קריבה ונגיעה ונגישה קד תכון למעני אלדנו ואלקרב פי אלמכאן וקד תכון למעני אתצאל אלעלם באלמעלום פכאנה שבה בקרב ג'סם מן ג'סם. אמא מעני קריבה אלאול והו אלקרב פי אלמכאן כאשר קרב אל המחנה ופרעה הקריב. ואלנגיעה מענאהא אלאול דנו ג'סם בג'סם ותגע לרגליו. ויגע על פי. ומעני נגישה אלאול אקדאם שכ'ץ עלי שכ'ץ וחרכתה אליה ויגש אליו יהודה.</span> |

---

### 2. Segment: `root.text.Part 1..17.1`

**Flags:** `style_modernization`, `citation_standardization`  
**Rationale:** Standardized citations (Jer. 51:9, Deut. 1:17, Gen. 18:23, Isa. 29:13); modernized prose; preserved [[fn:147]], [[fn:148]].

| Layer | Text |
| :--- | :--- |
| **v1 English (Original)** | — The second meaning of these three words expresses a union through knowledge, a drawing near through perception, and not a local drawing near. <i>Naga’</i> (<span dir="rtl">נגע</span>) was used in the sense of <i>union through knowledge</i> when it was said: <i>For his judgment has touched</i> (<span dir="rtl">נגע</span>) <i>up to heaven</i>[[fn:147]] (Jeremiah, 51, 9). It was said, using <i>karab</i> (<span dir="rtl">קרב</span>): <i>And the cause which will be too difficult for you, you shall present</i> (<span dir="rtl">תקריבון</span>) <i>to me</i>, that is to say, you will make me <i>know</i>; thus (this verb) was used in the sense of: to make <i>known</i> that which must be <i>known</i>. It was said, using <i>nagasch</i> (<span dir="rtl">נגש</span>): <i>And Abraham advanced</i> (<span dir="rtl">ויגש</span>) <i>and said</i> (Genesis, 18, 23); for he was then in a state of prophetic vision and slumber, as will be explained[[fn:148]]. (Elsewhere it is said): <i>Since this people, in approaching</i> (<span dir="rtl">נגש</span>), <i>has honored me with its mouth and lips</i> (Isaiah, 29, 13). |
| **v2 English (Reviewed)** | **— The second meaning of these three words expresses a union through knowledge, an approach through perception, and not a spatial approach. <i>Nāga‘</i> (<span dir="rtl">נגע</span>) has been employed in the sense of <i>union through knowledge</i> in the verse: <i>For her judgment reaches</i> (<span dir="rtl">נגע</span>) <i>unto heaven</i>[[fn:147]] (Jer. 51:9). In employing <i>qārav</i> (<span dir="rtl">קרב</span>), it has been said: <i>And the cause that is too hard for you, you shall bring</i> (<span dir="rtl">תקריבון</span>) <i>unto me</i> (Deut. 1:17), that is to say, you shall make it <i>known</i> to me; this verb has thus been used in the sense of making <i>known</i> that which is to be <i>known</i>. In employing <i>nāgaš</i> (<span dir="rtl">נגש</span>), it has been said: <i>And Abraham drew near</i> (<span dir="rtl">ויגש</span>), <i>and said</i> (Gen. 18:23); for he was then in a state of prophetic vision and trance, as will be explained[[fn:148]]. Elsewhere it is said: <i>Inasmuch as this people draw near</i> (<span dir="rtl">נגש</span>) <i>with their mouth, and with their lips honor Me</i> (Isa. 29:13).** |
| **Munk French** | — Le deuxième sens de ces trois mots exprime une union par la science, un rapprochement par la perception, et non pas un rapprochement local. On a employé <i>naga’</i> (<span dir="rtl">נגע</span>) dans le sens de l’<i>union par la science</i> en disant: <i>Car son jugement a touché</i> (<span dir="rtl">נגע</span>) <i>jusqu’au ciel</i><sup class="footnote-marker">(1)</sup><i class="footnote">C’est-à-dire son jugement est arrivé devant Dieu, qui a eu <i>connaissance</i> des péchés de Babel et a décrété son châtiment.</i> (Jérémie, 51, 9). On a dit, en employant <i>karab</i> (<span dir="rtl">קרב</span>): <i>Et la cause qui sera trop difficile pour vous, vous la présenterez</i> (<span dir="rtl">תקריבון</span>) <i>à moi</i> (Deutér., 1, 17), c’est-à-dire vous me la ferez <i>savoir;</i> on a donc employé (ce verbe) dans le sens de: faire <i>savoir</i> ce qui doit être <i>su</i>. On a dit, en employant <i>nagasch</i> (<span dir="rtl">נגש</span>): <i>Et Abraham s’avança</i> (<span dir="rtl">ויגש</span>) <i>et dit</i> (Genèse, 18, 23); car celui-ci était alors dans un état de vision et d’assoupissement prophétique, comme on l’expliquera<sup class="footnote-marker">(2)</sup><i class="footnote">Voir cette I<sup>re</sup> partie, ch. XXI, et II<sup>e</sup> partie, ch. XLI.</i>. (Ailleurs il est dit): <i>Puisque ce peuple, en m’abordant</i> (<span dir="rtl">נגש</span>), <i>m’a honoré de sa bouche et de ses lèvres</i> (Isaïe, 29, 13). |
| **Judeo-Arabic** | <span dir="rtl">ומעני הד'ה אלת'לת'ה אסמא אלת'אני הו אתצאל עלם ודנו אדראך לא דנו מכאן קאל מן אלנגיעה פי מעני אתצאל אלעלם כי נגע אל השמים משפטה. וקיל מן אלקריבה והדבר אשר יקשה מכם תקריבון אלי כאנה יקול תעלמוני בה פקד אסתעמל פי אעלאם במעלום. וקיל מן אלנגישה ויגש אברהם ויאמר והו כאן פי חאל אלוחי ואלסבאת אלנבוי כמא סיבין יען כי נגש העם הזה בפיו ובשפתיו כבדוני.</span> |

---

### 3. Segment: `root.text.Part 1..17.2`

**Flags:** `style_modernization`  
**Rationale:** Polished philosophical vocabulary; clarified syntax.

| Layer | Text |
| :--- | :--- |
| **v1 English (Original)** | Every time one encounters in prophetic books the expression of <i>karab</i> or of <i>nagasch</i> (applying to a relation) between God and any creature whatsoever, it is always in the latter sense; for God is not a body, as will be demonstrated in this treatise, and therefore the Most High does not approach anything, nor does He draw near to anything, and nothing draws near to Him nor does He approach anything; for, by excluding corporeality, one excludes space, and it is not a question of proximity, access, distance, union, separation, contact, or succession. |
| **v2 English (Reviewed)** | **Whenever one encounters in the prophetic books the expression <i>qārav</i> or <i>nāgaš</i> applying to a relationship between God and any creature whatsoever, it is always in this latter sense; for God is not a body, as will be demonstrated in this treatise, and consequently He, the Most High, approaches nothing and draws near to nothing, nor does anything draw near to Him or approach Him. For by excluding corporeality, one excludes space; and there can be no question of proximity, approach, distance, union, separation, contact, or succession.** |
| **Munk French** | Toutes les fois qu’on rencontre dans les livres prophétiques l’expression de <i>karab</i> ou de <i>nagasch</i> (s’appliquant à un rapport) entre Dieu et une créature quelconque, c’est toujours dans ce dernier sens; car Dieu n’est pas un corps, ainsi qu’on te le démontrera dans ce traité, et par conséquent lui, le Très-Haut, n’aborde rien, ni ne s’approche de rien, et aucune chose ne s’approche de lui ni ne l’aborde; car, en écartant la corporéité, on écarte l’espace, et il ne peut être question de rapprochement, d’accès, d’éloignement, de réunion, de séparation, de contact ou de succession. |
| **Judeo-Arabic** | <span dir="rtl">פכל לשון קריבה או נגישה תג'דהא ג'את פי כתב אלנבוה בין אללה תעאלי ובין מכ'לוק מן אלמכ'לוקאת פהי כלהא מן הד'א אלמעני אלאכ'יר לאן אללה תעאלי ליס הו ג'סמא כמא סיתברהן לך פי הד'ה אלמקאלה פלא הו תעאלי ידנו ולא יקרב מן שי ולא שי מן אלאשיא יקרב מנה או ידנו בה תעאלי אד' בארתפאע אלג'סמאניה ירתפע אלמכאן ויבטל כל קרב ודנו או בעד או אתצאל או אנפצאל או תמאס או תתאלי</span> |

---

### 4. Segment: `root.text.Part 1..17.3`

**Flags:** `style_modernization`, `citation_standardization`  
**Rationale:** Purged pseudo-biblical 'unto'; modernized prose; standardized citations (Ps. 145:18, Isa. 58:2, Ps. 73:28, Deut. 4:7, ibid., 5:27, Exod. 24:2).

| Layer | Text |
| :--- | :--- |
| **v1 English (Original)** | I do not think you have any doubt (in this regard), and there shall be nothing obscure to you in these passages: <i>The Lord is near to all who call upon Him</i> (Ps. 145, 18); <i>They desire to draw near to God</i> (Isaiah, 58, 2); <i>To draw near to God is my happiness</i> (Ps. 73, 28); for in all these passages it is a matter of drawing near through knowledge, that is to say, through scientific perception, and not through local approach. It is the same in these passages: (<i>God</i>) <i>near to Him</i> (Deuteronomy, 4, 7); <i>Draw near and hearken</i> (<i>Ibid.</i>, 5, 27); <i>And Moses shall approach alone unto the Lord, but they shall not approach</i> (Exodus, 24, 2). |
| **v2 English (Reviewed)** | **I do not think you have any doubt in this regard, and there will be nothing obscure to you in these passages: <i>The Lord is near to all who call upon Him</i> (Ps. 145:18); <i>They delight to draw near to God</i> (Isa. 58:2); <i>Drawing near to God is my good</i> (Ps. 73:28); for in all these passages it is a question of drawing near through knowledge—that is to say, through intellectual perception, and not through spatial approach. It is the same in these passages: <i>God so near to him</i> (Deut. 4:7); <i>Draw near and hear</i> (<i>ibid.</i>, 5:27); <i>And Moses alone shall draw near to the Lord, but they shall not draw near</i> (Exod. 24:2).** |
| **Munk French** | Je ne pense pas que tu aies un doute (à cet égard), et il n’y aura rien d’obscur pour toi dans ces passages: <i>L’Éternel est près de tous ceux qui l’invoquent</i> (Ps. 145, 18); <i>Ils désirent s’approcher de Dieu</i> (Isaïe, 58, 2); <i>M’approcher de Dieu, c’est mon bonheur</i> (Ps. 73, 28); car dans tous ces passages il s’agit d’un rapprochement par la science, je veux dire d’une perception scientifique, et non d’un rapprochement local. Il en est de même dans ces passages: (<i>Dieu</i>) <i>près de lui</i> (Deutéron., 4, 7); <i>Approche-toi et écoute</i> (<i>Ibid.</i>, 5, 27); <i>Et Moïse s’avancera seul vers l’Éternel, mais eux ne s’avanceront pas</i> (Exode, 24, 2). |
| **Judeo-Arabic** | <span dir="rtl">ומא אראך תשך ולא ילבס עליך קולה קרוב י"י לכל קוראיו קרבת אלהים יחפצון קרבת אלהים לי טוב אן הד'ה כלהא קרב עלם אעני אדראך עלמי לא קרב מכאן. וכד'לך קולה קרובים אליו קרב אתה ושמע ונגש משה לבדו אל י"י והם לא יגשו</span> |

---

### 5. Segment: `root.text.Part 1..17.4`

**Flags:** `style_modernization`  
**Rationale:** Modernized philosophical syntax; preserved [[fn:149]], [[fn:150]], [[fn:151]].

| Layer | Text |
| :--- | :--- |
| **v1 English (Original)** | However, if you desire to understand by the word <span dir="rtl">ונגש</span>, <i>shall approach</i>, applied to Moses, that he could approach that place on the mountain where the light descended, that is to say, <i>the glory of the Lord</i>, you are at liberty to do so; only you must adhere to this principle, that no matter whether the individual be in the centre of the earth or at the summit of the ninth sphere[[fn:149]], — if this were possible, — he is not thereby farther from God, and there he is not nearer to Him; but one is near to God in perceiving Him, and he who ignores Him is far from Him. There is, in this regard, a great variety of gradations[[fn:150]] in approach and withdrawal; in one of the chapters of this treatise[[fn:151]] I shall explain what this relative superiority is in the perception (of the divinity). |
| **v2 English (Reviewed)** | **However, if you wish to understand by the word <span dir="rtl">ונגש</span>, <i>shall draw near</i>, applied to Moses, that he could approach that place on the mountain where the light descended—that is to say, <i>the glory of the Lord</i>—you are at liberty to do so; only you must hold fast to this principle: whether an individual be at the center of the earth or at the summit of the ninth sphere[[fn:149]]—were that possible—he is not in the former case farther from God, nor in the latter nearer to Him; but one is near to God by perceiving Him, and whoever is ignorant of Him is far from Him. There is in this regard a great variety of gradations[[fn:150]] in drawing near and in withdrawing; and in one of the chapters of this treatise[[fn:151]] I shall explain what this relative superiority consists of in the perception of the Divinity.** |
| **Munk French** | Cependant, si tu veux entendre par le mot <span dir="rtl">ונגש</span>, <i>s’avancera</i>, appliqué à Moïse, qu’il pouvait s’approcher de cet endroit de la montagne où descendait la lumière, je veux dire <i>la gloire de l’Éternel</i>, tu en es libre; seulement il faut t’en tenir à ce principe que, n’importe que l’individu soit dans le centre de la terre ou au sommet de la neuvième sphère<sup class="footnote-marker">(1)</sup><i class="footnote">C’est-à-dire de la sphère la plus élevée. Sur le nombre des sphères, voy. le ch. IV de la II<sup>e</sup> partie de cet ouvrage.</i>, — si cela était possible, — il n’est pas ici plus éloigné de Dieu, et là il n’en est pas plus rapproché; mais on est près de Dieu en le percevant, et celui qui l’ignore est loin de lui. Il y a à cet égard dans le approchement et dans l’éloignement une grande variété de gradations<sup class="footnote-marker">(2)</sup><i class="footnote">Littéralement: <i>une très grande lutte réciproque de supériorité</i>.</i>; dans l’un des chapitres de ce traité<sup class="footnote-marker">(3)</sup><i class="footnote">Voy. ce que l’auteur dit au sujet des attributs négatifs au chap. LX de cette I<sup>re</sup> partie.</i> j’expliquerai quelle est cette supériorité relative dans la perception (de la divinité). |
| **Judeo-Arabic** | <span dir="rtl">אלא אן תריד אן תג'על מא קיל פי משה ונגש אנה יקרב מן אלמוצ'ע מן אלג'בל אלד'י חל פיה אלנור אעני כבוד י"י פלך ד'לך לכן תמסך באלאצל אן לא פרק בין כון אלשכ'ץ פי מרכז אלארץ' או פי אעלי אלפלך אלתאסע לו אמכן ד'לך פאנה לם יבעד מן אללה הנא ולא קרב מנה הנאך בל אלקרב מנה תעאלי באדראכה ואלבעד ענה למן ג'הלה ויתפאצ'ל אלקרב ואלבעד מן הד'ה אלג'הה תפאצ'לא כת'ירא ג'דא וסאבין פי פצל מן פצול הד'ה אלמקאלה כיף הו אלתפאצ'ל פי אלאדראך</span> |

---

### 6. Segment: `root.text.Part 1..17.5`

**Flags:** `untranslated_repair`, `citation_standardization`  
**Rationale:** CRITICAL REPAIR: Translated two biblical verses that were completely left in French in v1 ('Touche les montagnes, et qu’elles fument' -> 'Touch the mountains, and they shall smoke'; 'Et touche sa personne' -> 'Touch his bone and his flesh'); standardized Ps. 144:5 and Job 2:5.

| Layer | Text |
| :--- | :--- |
| **v1 English (Original)** | — As for these words: <i>Touche les montagnes, et qu’elles fument</i> (Ps. 144, 5), one intends to convey thereby; Cause your command to reach them (which, in turn, is to be understood) metaphorically; likewise the words: <i>Et touche sa personne</i> (Job, 2, 5) signify: Cause your affliction to descend upon him. |
| **v2 English (Reviewed)** | **— As for these words: <i>Touch the mountains, and they shall smoke</i> (Ps. 144:5), the meaning intended is: Cause Your decree to reach them—which, in turn, is to be understood metaphorically. Likewise the words: <i>Touch his bone and his flesh</i> (Job 2:5) signify: Cause Your affliction to descend upon him.** |
| **Munk French** | — Quant à ces paroles: <i>Touche les montagnes, et qu’elles fument</i> (Ps. 144, 5), on veut dire par là; Fais-leur parvenir ton ordre (ce qui, à son tour, doit s’entendre) métaphoriquement; de même les mots: <i>Et touche sa personne</i> (Job, 2, 5) signifient: Fais descendre ton fléau sur lui. |
| **Judeo-Arabic** | <span dir="rtl">אמא קולה גע בהרים ויעשנו יעני בה אוצל אמרך להא עלי ג'ההֵ אלמת'ל כמא קאל וגע אל עצמו יעני אחל אפתך בה.</span> |

---

### 7. Segment: `root.text.Part 1..17.6`

**Flags:** `style_modernization`  
**Rationale:** Modernized academic style.

| Layer | Text |
| :--- | :--- |
| **v1 English (Original)** | Thus, in each passage, you must consider the verb <span dir="rtl">נגע</span> (to touch), as well as its derived forms, in accordance with the entirety: one expresses by this verb, at times, the contact of one body with another, and, at times, the union through the science and perception of something; for he who perceives the thing he had not previously perceived, as it were, approaches a thing that was distant from him. This must be well understood. |
| **v2 English (Reviewed)** | **Thus in each passage you must consider the verb <span dir="rtl">נגע</span> (to touch), as well as its derived forms, in conformity with the context as a whole: one expresses by this verb at times the contact of one body with another, and at times union through knowledge and the perception of something; for he who perceives a thing which he had not previously perceived draws near, as it were, to a thing that was distant from him. This must be well understood.** |
| **Munk French** | C’est ainsi que, dans chaque passage, tu dois considérer le verbe <span dir="rtl">נגע</span> (toucher), ainsi que ses formes dérivées, conformément à l’ensemble: on exprime par ce verbe tantôt le contact d’un corps avec un autre, tantôt l’union par la science et la perception de quelque chose; car celui qui perçoit la chose qu’il n’avait pas perçue auparavant s’approche, pour ainsi dire, d’une chose qui était loin de lui. Il faut bien comprendre cela. |
| **Judeo-Arabic** | <span dir="rtl">וכד'לך אלנגיעה ומא יתצרף מנהא תעתברהא פי כל מכאן בחסבה פתארה יראד בהא דנו ג'סם בג'סם ותארה אתצאל עלם ואדראך אמר מא פכאן מדרך אלאמר אלד'י לם יכן ידרכה קבל קד קרב מן שי כאן בעידא ענה פאפהם הד'א:</span> |

---

## Unchanged Segments

Count: 0 segments verified and preserved byte-for-byte.
