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
        'priest', 'crest', 'crest', 'oldest', 'newest', 'greatest', 'highest',
        'lowest', 'first', 'purest', 'closest', 'brightest', 'finest', 'deepest'
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

    def _check_french(self, text: str, context_id: str) -> List[str]:
        errors = []
        # Remove tags for word checking
        clean_text = self.TAG_REGEX.sub(' ', text).lower()
        for pattern in self.FRENCH_INDICATORS:
            if re.search(pattern, clean_text, re.IGNORECASE):
                errors.append(f"french_detected in {context_id}: matched '{pattern}'")
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
