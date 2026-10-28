"""Strict Apparatus and Quality Validator for Munk Second Edition (v2)."""

import re
from typing import List, Tuple, Optional, Dict, Any

class StrictApparatusValidator:
    """Enforces apparatus integrity, translation completeness, and style constraints."""

    # Prohibited archaic forms
    ARCHAISMS = [
        r'\bthou\b', r'\bthee\b', r'\bthine\b', r'\bhath\b', r'\bdoth\b',
        r'\bwhilst\b', r'\bunto\b', r'\bcanst\b', r'\bshalt\b', r'\bwilt\b',
        r'\bdost\b', r'\bdidst\b', r'\b\w+eth\b', r'\b\w+est\b'
    ]
    # Whitelist words ending in eth or est that are legitimate English
    ARCHAISM_WHITELIST = {
        'method', 'something', 'teeth', 'twentieth', 'thirtieth', 'fiftieth',
        'hundredth', 'thousandth', 'seventh', 'eighth', 'ninth', 'tenth',
        'eleventh', 'twelfth', 'thirteenth', 'fourteenth', 'fifteenth',
        'sixteenth', 'seventeenth', 'eighteenth', 'nineteenth', 'fourth',
        'fifth', 'sixth', 'death', 'breath', 'length', 'strength', 'width',
        'breadth', 'depth', 'wealth', 'health', 'stealth', 'wrath', 'faith',
        'truth', 'youth', 'earth', 'birth', 'worth', 'north', 'south', 'path',
        'beth', 'seth', 'japheth', 'elizabeth', 'nazareth', 'goliath', 'best',
        'rest', 'test', 'west', 'east', 'nest', 'guest', 'chest', 'pest',
        'quest', 'manifest', 'suggest', 'attest', 'request', 'digest', 'invest',
        'divest', 'interest', 'earnest', 'honest', 'modest', 'forest', 'harvest',
        'priest', 'crest', 'contest', 'oldest', 'newest', 'greatest', 'highest',
        'lowest', 'first', 'purest', 'closest', 'brightest', 'finest', 'deepest',
        'noblest', 'vilest', 'lest', 'northwest', 'northeast', 'southwest', 'southeast',
        'darkest', 'clearest', 'subtlest', 'fullest', 'earliest', 'latest', 'richest',
        'simplest', 'grossest', 'weakest', 'strongest', 'wisest', 'rarest', 'densest',
        'hardest', 'softest', 'crudest', 'boldest', 'strangest', 'broadest', 'warmest',
        'farthest', 'furthest', 'nearest', 'northernmost', 'southernmost', 'easternmost', 'westernmost',
        'uppermost', 'lowermost', 'daleth', 'heth', 'yod', 'shin', 'resh', 'teth', 'aleph', 'bet', 'gimel',
        'zayin', 'lamed', 'mem', 'nun', 'samekh', 'pe', 'tsade', 'qof', 'tav', 'almagest'
    }

    # French functional markers
    FRENCH_INDICATORS = [
        r'\bqui\b', r'\bque\b', r'\bqu’[a-z]+', r'\bqu\'[a-z]+', r'\bdans\b',
        r'\bavec\b', r'\bles\b', r'\bdes\b', r'\bparce que\b', r'\bc\'est\b',
        r'\bc’est\b', r'\bsont des\b', r'\best un\b', r'\btouche les\b',
        r'\bfument\b', r'\bmontagnes\b', r'\bl’[a-z]+', r'\bd’[a-z]+',
        r'\bceux qui\b', r'\bcelle qui\b', r'\blequel\b', r'\blaquelle\b',
        r'\blesquels\b', r'\blesquelles\b', r'\bainsi que\b', r'\bmais aussi\b'
    ]

    # Glued-in Latin drafting relics
    GLUED_LATIN = [
        r'[a-z]{3,}(?:stare|cessare|implere|privatio)',
        r'(?:stare|cessare|implere|privatio)[a-z]{3,}'
    ]

    RTL_REGEX = re.compile(r'<span dir=["\']rtl["\']>(.*?)</span>', re.DOTALL | re.IGNORECASE)
    HEBREW_ARABIC_GLYPHS = re.compile(r'[\u0590-\u05FF\u0600-\u06FF]')
    FN_MARKER_REGEX = re.compile(r'\[\[fn:(\d+)\]\]')
    TAG_REGEX = re.compile(r'<(/?)([a-zA-Z0-9]+)(?:\s+[^>]*)?>')

    SUPPORTED_TAGS = {'i', 'b', 'sup', 'sub', 'span', 'small'}

    def validate_segment(
        self,
        segment_id: str,
        original_text: str,
        revised_text: str,
        expected_footnotes: Optional[List[str]] = None
    ) -> Tuple[bool, List[str]]:
        """Validate a single segment against apparatus and style rules."""
        errors: List[str] = []

        # 1. Footnote callout integrity
        if original_text:
            orig_fns = self.FN_MARKER_REGEX.findall(original_text)
            rev_fns = self.FN_MARKER_REGEX.findall(revised_text)
            if orig_fns != rev_fns:
                errors.append(
                    f"footnote_marker_mismatch in {segment_id}: expected {orig_fns}, found {rev_fns}"
                )

        # 2. HTML Tag Closure Check
        tag_errors = self._check_html_tags(revised_text, segment_id)
        errors.extend(tag_errors)

        # 3. RTL Spans check
        rtl_errors = self._check_rtl_spans(revised_text, segment_id)
        errors.extend(rtl_errors)

        # 4. Untranslated French detection
        french_errors = self._check_french(revised_text, segment_id)
        errors.extend(french_errors)

        # 5. Archaism detection
        archaism_errors = self._check_archaisms(revised_text, segment_id)
        errors.extend(archaism_errors)

        # 6. Glued-in Latin detection
        latin_errors = self._check_glued_latin(revised_text, segment_id)
        errors.extend(latin_errors)

        return (len(errors) == 0, errors)

    def validate_footnote(
        self,
        footnote_id: str,
        original_text: str,
        revised_text: str
    ) -> Tuple[bool, List[str]]:
        """Validate a single footnote entry."""
        errors: List[str] = []

        tag_errors = self._check_html_tags(revised_text, footnote_id)
        errors.extend(tag_errors)

        rtl_errors = self._check_rtl_spans(revised_text, footnote_id)
        errors.extend(rtl_errors)

        french_errors = self._check_french(revised_text, footnote_id)
        errors.extend(french_errors)

        archaism_errors = self._check_archaisms(revised_text, footnote_id)
        errors.extend(archaism_errors)

        latin_errors = self._check_glued_latin(revised_text, footnote_id)
        errors.extend(latin_errors)

        return (len(errors) == 0, errors)

    def _check_html_tags(self, text: str, context_id: str) -> List[str]:
        errors = []
        stack = []
        for match in self.TAG_REGEX.finditer(text):
            is_closing = bool(match.group(1))
            tag_name = match.group(2).lower()
            if tag_name not in self.SUPPORTED_TAGS:
                continue
            if not is_closing:
                stack.append(tag_name)
            else:
                if not stack:
                    errors.append(f"unclosed_html_tag in {context_id}: unexpected closing </{tag_name}>")
                else:
                    last_tag = stack.pop()
                    if last_tag != tag_name:
                        errors.append(
                            f"unclosed_html_tag in {context_id}: mismatched closing tag </{tag_name}> for <{last_tag}>"
                        )
        while stack:
            unclosed = stack.pop()
            errors.append(f"unclosed_html_tag in {context_id}: unclosed <{unclosed}>")
        return errors

    def _check_rtl_spans(self, text: str, context_id: str) -> List[str]:
        errors = []
        for match in self.RTL_REGEX.finditer(text):
            inner_content = match.group(1)
            # Must contain at least one Hebrew or Arabic character
            if not self.HEBREW_ARABIC_GLYPHS.search(inner_content):
                errors.append(
                    f"invalid_rtl_content in {context_id}: RTL span '{inner_content}' lacks Hebrew/Arabic characters"
                )
        return errors

    # Foreign-language *citations* (titles of French/German works and journals, and
    # French-capitalised proper-name elisions such as d'Herbelot) are not untranslated
    # French prose: Munk cites them in the original language, and so must we.
    FOREIGN_CITATION_ALLOWLIST = [
        r"dictionnaire\s+des\s+sc(?:iences|\s*\.)\s+philos(?:ophiques|\s*\.)",
        r"dict\s*\.\s+des\s+sc\s*\.\s+philos\s*\.",
        r"notices\s+et\s+extraits(?:\s+des\s+(?:manuscrits|mss\.?))?",
        r"\bdes\s+(?:manuscrits|mss\.?)\b",
        r"journal\s+(?:des\s+savants|asiatique)",
        r"devoirs\s+des\s+c(?:œ|oe)urs",
        r"m[ée]langes\s+de\s+philosophie\s+juive\s+et\s+arabe",
        r"r[ée]flexions\s+sur\s+le\s+culte\s+des\s+anciens\s+h[ée]breux",
        r"histoire\s+des\s+(?:animaux|sectes\s+religieuses\s+et\s+philosophiques|juifs)",
        r"essai\s+sur\s+les\s+[ée]coles\s+philosophiques\s+chez\s+les\s+arabes",
        r"la\s+religion\s+des\s+mahom[ée]tans,?\s+tir[ée]e\s+du\s+latin\s+de\s+reland",
        r"les\s+oiseaux\s+et\s+les\s+fleurs",
        r"s[ée]ances\s+de\s+hariri",
        r"comptes?\s+rendus\s+des\s+s[ée]ances\s+de\s+l[’']acad[ée]mie\s+des\s+sciences",
        r"recueil\s+des\s+historiens\s+des\s+gaules",
        r"m[ée]moires?\s+(?:sur\s+les\s+nabat[ée]ens|sur\s+l[’']?[ée]poque\s+de\s+l[’']?[ée]tablissement\s+des\s+juifs\s+dans\s+l[’']?\w+|de\s+l[’']acad[ée]mie\s+des\s+inscriptions\s+et\s+belles-lettres)",
        r"livre\s+des\s+myst[èe]res\s+de\s+la\s+lune",
        r"ency[ck]lop(?:ä|ae|œ|oe)dische\s+(?:u|ü|ue)bersicht\s+der\s+wissenschaften\s+des\s+orients",
        r"dict\s*\.\s+des\s+sc\s*\.\s+m[ée]d\s*\.",
        r"histoire\s+de\s+l[’']astronomie(?:\s+du\s+moyen\s+[âa]ge)?",
        r"p\.\s+des\s+bosses",
        r"comment\.\s+sur\s+les\s+aphorismes\s+d[’']hippocrate",
        r"abr[ée]g[ée]\s+de\s+l[’']organon",
        r"morale\s+[àa]\s+nicomaque",
        r"trait[ée]\s+de\s+l[’']intellect",
    ]
    # French-capitalised elisions of proper names / titles: d'Herbelot, l'Académie, l'Alliance ...
    FOREIGN_NAME_ELISION = re.compile(r"\b[dDlL][’'][A-ZÀ-Ý]\w*")
    # Words that occur only in Latin or Italian (never French); used to recognise an
    # embedded Latin/Italian quotation so its function words are not mistaken for French.
    LATIN_ITALIAN_MARKERS = {
        'quod', 'autem', 'enim', 'sunt', 'quae', 'quia', 'secundum', 'igitur', 'ergo', 'nisi',
        'ejus', 'eorum', 'quam', 'cujus', 'ipsa', 'ipsum', 'ipsi', 'tunc', 'dicunt',
        'quomodo', 'accidit', 'motus', 'aer', 'continet', 'fluens', 'nobilior',
        'orbis', 'circuli', 'planetarum', 'intelligentia', 'movet', 'sphaeram', 'sphæram',
        'tali', 'casu', 'existit', 'libellus', 'contra', 'eos', 'omnibus', 'animabus',
        'della', 'degli', 'dei', 'sono', 'cioè', 'tengono', 'essere', 'havere', 'eterno', 'principio', 'temporale', 'ancora', 'alcuni', 'quali', 'perche', 'perché',
        'eterna', 'cosa', 'quello', 'questo', 'tutti', 'huomini', 'del', 'nel',
        'quà', 'qua', 'erit', 'apud', 'vel', 'oportet', 'voluerit', 'judicare', 'contradicit',
        'contradicens', 'propositiones', 'discretionis', 'dignior', 'recipiatur', 'sermo', 'noster',
        'fecerimus', 'tune', 'odiens', 'diligentem', 'pacificum', 'bonæ', 'molti', 'mondo', 'materia', 'generate', 'prodotto', 'vero',
    }

    def _strip_foreign_citations(self, raw_text: str) -> str:
        """Remove cited foreign titles/names from tag-stripped text (case preserved)."""
        txt = self.TAG_REGEX.sub(' ', raw_text)
        for pat in self.FOREIGN_CITATION_ALLOWLIST:
            txt = re.sub(pat, ' ', txt, flags=re.IGNORECASE)
        return self.FOREIGN_NAME_ELISION.sub(' ', txt)

    def _in_latin_italian_quotation(self, clean_text: str, start: int, end: int) -> bool:
        """True if the match sits inside an embedded Latin/Italian quotation."""
        window = clean_text[max(0, start - 140): end + 140]
        words = re.findall(r"[a-zæœà-ÿ]+", window)
        return sum(1 for w in words if w in self.LATIN_ITALIAN_MARKERS) >= 3

    def _check_french(self, text: str, context_id: str) -> List[str]:
        errors = []
        # Remove tags and cited foreign titles/names, then check function words
        clean_text = self._strip_foreign_citations(text).lower()
        for pattern in self.FRENCH_INDICATORS:
            for match in re.finditer(pattern, clean_text, re.IGNORECASE):
                if self._in_latin_italian_quotation(clean_text, match.start(), match.end()):
                    continue
                errors.append(f"french_detected in {context_id}: matched '{pattern}'")
                break
            if errors:
                break
        return errors

    def _check_archaisms(self, text: str, context_id: str) -> List[str]:
        errors = []
        clean_text = self.TAG_REGEX.sub(' ', text).lower()
        for pattern in self.ARCHAISMS:
            for match in re.finditer(pattern, clean_text, re.IGNORECASE):
                word = match.group(0).lower()
                if word in self.ARCHAISM_WHITELIST:
                    continue
                # If word ends in est or eth, check if root is in whitelist or superlative
                if word.endswith('est') and (word[:-3] in {'great', 'high', 'low', 'deep', 'broad', 'small', 'strong', 'weak', 'pure', 'close'} or word in self.ARCHAISM_WHITELIST):
                    continue
                if word.endswith('eth') and word in self.ARCHAISM_WHITELIST:
                    continue
                errors.append(f"archaism_detected in {context_id}: found prohibited archaism '{word}'")
                break
            if any("archaism_detected" in e for e in errors):
                break
        return errors

    def _check_glued_latin(self, text: str, context_id: str) -> List[str]:
        errors = []
        for pattern in self.GLUED_LATIN:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                errors.append(f"glued_latin_detected in {context_id}: found '{match.group(0)}'")
                break
        return errors
