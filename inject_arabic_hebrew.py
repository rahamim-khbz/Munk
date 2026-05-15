import json

# Fix French
with open("preface_resegmented.json", "r", encoding="utf-8") as f:
    fr_paras = json.load(f)

# Fix paragraph 15
fr_15 = fr_paras[15]
fr_15 = fr_15.replace("càph ponctué (îp) au khà (^)", "câph ponctué (כּ) au khâ (خ)")
fr_15 = fr_15.replace("guimel sans point (3) au ghaïn (p) (i)", "guimel sans point (ג) au ghaïn (غ) (1)")

# Extract and move footnote 1 from the middle of the sentence
footnote_1 = " (1) Dans quelques manuscrits, le غ est rendu par ג̇ ou ג̄, et le ج par ג."
fr_15 = fr_15.replace("et (1) Dans quelques manuscrits, le ^ est rendu par i ou Xi ^^ 1^ t par :;. notamment les désinences,", "et notamment les désinences,")
# Add footnote 1 to the end of para 15 if not already there
if footnote_1 not in fr_15:
    fr_15 += footnote_1

fr_15 = fr_15.replace("terminaison ^?\" de Taccusatif", "terminaison א\" de l'accusatif")
fr_15 = fr_15.replace("])îé (^) pour ••y-IÛ, I^DO pour \"^I^DD", "מֻדַע (مُدَع) pour מדעא, מסאִ pour מסאי")
fr_15 = fr_15.replace("pnni\"' pour iirni\"» (fol. 17 6), ^vin^ pour pinS^ (fol. 97 6) (i)", "יִגְזָאוּן pour יִגְזוּן (fol. 17 b), יִלְגָאוּן pour יִלְגוּן (fol. 97 b) (1)")

fr_paras[15] = fr_15

# Fix paragraph 16
fr_16 = fr_paras[16]
fr_16 = fr_16.replace("\"•ît^, i<:x, quoique l'orthographe plus correcte soit '^iîi^ (^') <i3t< (^L')• L'impératif n^< (pour j ou Tij)", "אַנִי, אַנָא, quoique l'orthographe plus correcte soit אַנְנִי (أنني), אַנְנָא (أننا). L'impératif אֲרֵי (pour رَ ou رَة)")

fr_paras[16] = fr_16

with open("preface_resegmented.json", "w", encoding="utf-8") as f:
    json.dump(fr_paras, f, ensure_ascii=False, indent=2)

# Fix English
with open("preface_english_final.json", "r", encoding="utf-8") as f:
    en_paras = json.load(f)

en_15 = en_paras[15]
en_15 = en_15.replace("punctuated kaph (כּ) for the kha (כ) and the gimel without a point (ג) for the ghayn (ג̇) (1)", "punctuated kaph (כּ) for the kha (خ) and the gimel without a point (ג) for the ghayn (غ) (1)")
en_15 = en_15.replace("writing, for instance, (1) for (2), (3) for (4)", "writing, for instance, מֻדַע (مُدَع) for מדעא, מסאִ for מסאי")
en_15 = en_15.replace("I have written, for example, (5) for (6), (7) for (8).", "I have written, for example, יִגְזָאוּן for יִגְזוּן (fol. 17 b), יִלְגָאוּן for יִלְגוּן (fol. 97 b).")

# Add the footnote text to the end of the English paragraph 15
en_footnote_1 = " (1) In some manuscripts, the غ is rendered by ג̇ or ג̄, and the ج by ג."
if en_footnote_1 not in en_15:
    en_15 += en_footnote_1

en_paras[15] = en_15

en_16 = en_paras[16]
en_16 = en_16.replace("thus, I have always written (9), (10), although the more correct orthography is (11), (12). The imperative (13) (for (14))", "thus, I have always written אַנִי, אַנָא, although the more correct orthography is אַנְנִי (أنني), אַנְנָא (أننا). The imperative אֲרֵי (for رَ or رَة)")

en_paras[16] = en_16

with open("preface_english_final.json", "w", encoding="utf-8") as f:
    json.dump(en_paras, f, ensure_ascii=False, indent=2)

print("Hebrew and Arabic characters successfully injected.")
