
import json
import os

filepath = "French_Arabic_Enriched.json"
with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

def find_and_fix(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                if "Ficelles_The_VTo" in v:
                    print(f"Found corruption in key {k}. Fixing...")
                    # We only fix the specific part that is corrupted.
                    # The corruption starts with 'أنA de#' and ends with 'The statement is **false**.'
                    # Actually, the grep showed it's even longer.
                    # Let's just restore the clean text.
                    clean_text = "La nature de cette chose fait que celui qui a reçu cet <i>épanchement</i> surabondant prêche nécessairement aux hommes, n’importe qu’il soit écouté ou non, dût-il même exposer sa personne<sup class=\"footnote-marker\">(5)</sup><i class=\"footnote\">Littéralement: <i>dût-il être endommagé dans son corps</i>. La version d’Ibn-Tibbon a <span dir=\"rtl\">\u05d1\u05e2\u05e6\u05de\u05d5</span>, pour <span dir=\"rtl\">\u05db\u05d2\u05d5\u05e4\u05d5</span>.</i>; de sorte que nous trouvons des prophètes qui prêchèrent aux hommes jusqu’à se faire tuer, stimulés par cette inspiration divine qui ne leur laissait ni tranquill té ni repos<sup class=\"footnote-marker\">(1)</sup><i class=\"footnote\">Tous les mss. ont <span dir=\"rtl\">\u05d9\u05e7\u05e8\u05d0</span>  et <span dir=\"rtl\">\u05d9\u05dd\u05db\u05e0\u05d5\u05d0</span> au mode subjonctif; il faut sous-entendre la conjonction <span dir=\"rtl\">\u0623\u0646</span> . Voy. Silv. de Sacy, <i>grammaire arabe</i>, (2<sup>e</sup> édition), t. II, n° 64.</i>, lors même qu’ils étaient frappés de grands malheurs. C’est pourquoi tu vois Jérémie déclarer<sup class=\"footnote-marker\">(2)</sup><i class=\"footnote\">Les deux traducteurs hébreux ont omis de traduire le verbe <span dir=\"rtl\">\u05e6\u05e8\u05d7</span> , qui manque aussi dans le ms. de Leyde, n° 18.</i>, qu’à cause du mépris qu’il essuyait de la part de ces hommes rebelles et incrédules qui existaient de son temps, il voulait cacher<sup class=\"footnote-marker\">(3)</sup><i class=\"footnote\">Ibn-Tibbon, qui a <span dir=\"rtl\">\u05dc\u05dd\u05ea\u05d5\u05dd</span>, paraît avoir lu <span dir=\"rtl\">\u05d9\u05db\u05c4\u05ea\u05dd</span> <span dir=\"rtl\">(\u064a\u062e\u062a\u0645)</span> , avec un <span dir=\"rtl\">\u05db\u05c4</span> ponctué; d’après lui, il faudrait traduire: <i>il voulait clore sa mission prophétique</i>.</i> sa mission prophétique et ne plus les appeler à la vérité qu’ils avaient rejetée, mais que cela lui était impossible: <i>Car la parole de l’Éternel</i>, dit-il, <i>est devenue pour moi une cause d’opprobre et de dérision tout le jour. Je me disais: Je ne ferai plus mention de lui, et je ne parlerai plus en son nom; mais il y avait dans mon cœur comme un feu ardent, renfermé dans mes os; j’étais las de le supporter, je ne le pouvais plus</i> (Jérémie, 20, 8, 9). C’est dans le même sens qu’un autre prophète a dit: <i>Le Seigneur, l’Éternel, a parlé; qui ne prophétiserait pas</i> (Amos, 3, 8)? — Il faut te pénétrer de cela."
                    obj[k] = clean_text
                    return True
            if find_and_fix(v): return True
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str):
                if "Ficelles_The_VTo" in v:
                    print(f"Found corruption in list at index {i}. Fixing...")
                    clean_text = "La nature de cette chose fait que celui qui a reçu cet <i>épanchement</i> surabondant prêche nécessairement aux hommes, n’importe qu’il soit écouté ou non, dût-il même exposer sa personne<sup class=\"footnote-marker\">(5)</sup><i class=\"footnote\">Littéralement: <i>dût-il être endommagé dans son corps</i>. La version d’Ibn-Tibbon a <span dir=\"rtl\">\u05d1\u05e2\u05e6\u05de\u05d5</span>, pour <span dir=\"rtl\">\u05db\u05d2\u05d5\u05e4\u05d5</span>.</i>; de sorte que nous trouvons des prophètes qui prêchèrent aux hommes jusqu’à se faire tuer, stimulés par cette inspiration divine qui ne leur laissait ni tranquill té ni repos<sup class=\"footnote-marker\">(1)</sup><i class=\"footnote\">Tous les mss. ont <span dir=\"rtl\">\u05d9\u05e7\u05e8\u05d0</span>  et <span dir=\"rtl\">\u05d9\u05dd\u05db\u05e0\u05d5\u05d0</span> au mode subjonctif; il faut sous-entendre la conjonction <span dir=\"rtl\">\u0623\u0646</span> . Voy. Silv. de Sacy, <i>grammaire arabe</i>, (2<sup>e</sup> édition), t. II, n° 64.</i>, lors même qu’ils étaient frappés de grands malheurs. C’est pourquoi tu vois Jérémie déclarer<sup class=\"footnote-marker\">(2)</sup><i class=\"footnote\">Les deux traducteurs hébreux ont omis de traduire le verbe <span dir=\"rtl\">\u05e6\u05e8\u05d7</span> , qui manque aussi dans le ms. de Leyde, n° 18.</i>, qu’à cause du mépris qu’il essuyait de la part de ces hommes rebelles et incrédules qui existaient de son temps, il voulait cacher<sup class=\"footnote-marker\">(3)</sup><i class=\"footnote\">Ibn-Tibbon, qui a <span dir=\"rtl\">\u05dc\u05dd\u05ea\u05d5\u05dd</span>, paraît avoir lu <span dir=\"rtl\">\u05d9\u05db\u05c4\u05ea\u05dd</span> <span dir=\"rtl\">(\u064a\u062e\u062a\u0645)</span> , avec un <span dir=\"rtl\">\u05db\u05c4</span> ponctué; d’après lui, il faudrait traduire: <i>il voulait clore sa mission prophétique</i>.</i> sa mission prophétique et ne plus les appeler à la vérité qu’ils avaient rejetée, mais que cela lui était impossible: <i>Car la parole de l’Éternel</i>, dit-il, <i>est devenue pour moi une cause d’opprobre et de dérision tout le jour. Je me disais: Je ne ferai plus mention de lui, et je ne parlerai plus en son nom; mais il y avait dans mon cœur comme un feu ardent, renfermé dans mes os; j’étais las de le supporter, je ne le pouvais plus</i> (Jérémie, 20, 8, 9). C’est dans le même sens qu’un autre prophète a dit: <i>Le Seigneur, l’Éternel, a parlé; qui ne prophétiserait pas</i> (Amos, 3, 8)? — Il faut te pénétrer de cela."
                    obj[i] = clean_text
                    return True
            if find_and_fix(v): return True
    return False

if find_and_fix(data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Fixed and saved.")
else:
    print("Could not find corruption.")
