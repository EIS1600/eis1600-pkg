"""Self-contained Arabic normalization helpers.

Vendored and adapted from ``openiti.helper.ara`` and
``eis1600.helper.ar_normalization`` so this package has no dependency on
either project.
"""
import re
from typing import Dict, Iterable

# Character replacements applied by heavy normalization: unify alif variants,
# alif maqsura, remove hamzas, unify ta marbuta.
_NORMALIZE_REPLACEMENTS = [
    ('أ', 'ا'), ('ٱ', 'ا'), ('آ', 'ا'), ('إ', 'ا'),  # alifs
    ('ى', 'ي'),                                      # alif maqsura
    ('ؤ', ''), ('ئ', ''), ('ء', ''),                 # hamzas
    ('ة', 'ه'),                                      # ta marbuta
]

# Arabic combining diacritics (signs, harakat, tanwīn, shadda, sukūn, superscript
# alif, Quranic annotation marks) and the tatweel/kashida — all removed. Built
# from explicit codepoint ranges so the Arabic-Indic digits (U+0660–0669),
# punctuation and letters between 0660–066F are NOT swept up.
_DIACRITIC_RANGES = [
    (0x0610, 0x061A), (0x0640, 0x0640), (0x064B, 0x065F), (0x0670, 0x0670),
    (0x06D6, 0x06DC), (0x06DF, 0x06E4), (0x06E7, 0x06E8), (0x06EA, 0x06ED),
]
_DIACRITICS_RE = re.compile(
    '[' + ''.join(f'{chr(a)}-{chr(b)}' if a != b else chr(a)
                  for a, b in _DIACRITIC_RANGES) + ']'
)
# Character-level input canonicalization (letters/digits are mapped 1:1 to their
# Arabic form; invisible marks are removed; unusual spaces become a plain space).
_INPUT_MAP = {
    # Persian/Urdu & presentation look-alikes -> Arabic
    'ی': 'ي', 'ﯼ': 'ي', 'ﯽ': 'ي',            # yeh
    'ک': 'ك', 'ﮎ': 'ك', 'ﮏ': 'ك', 'ﻙ': 'ك',   # kaf
    'ۀ': 'ة', 'ہ': 'ه', 'ﻫ': 'ه', 'ﻩ': 'ه',   # heh variants
    # Persian digits -> Arabic-Indic
    '۰': '٠', '۱': '١', '۲': '٢', '۳': '٣', '۴': '٤',
    '۵': '٥', '۶': '٦', '۷': '٧', '۸': '٨', '۹': '٩',
}
# Bidi/formatting controls, BOM and soft hyphen -> removed (they never separate
# tokens, so deleting them must not merge words).
for _cp in (0x00AD, 0x200E, 0x200F,
            0x202A, 0x202B, 0x202C, 0x202D, 0x202E,
            0x2066, 0x2067, 0x2068, 0x2069, 0xFEFF):
    _INPUT_MAP[chr(_cp)] = None
# Zero-width spaces/joiners and non-breaking/unusual spaces -> a plain space, so a
# token boundary marked by them is preserved (e.g. 'ثمان<ZWNJ>وأربعين').
for _cp in (0x200B, 0x200C, 0x200D,
            0x00A0, 0x2007, 0x2009, 0x200A, 0x202F, 0x205F, 0x3000):
    _INPUT_MAP[chr(_cp)] = ' '
_INPUT_TRANSLATE = str.maketrans(_INPUT_MAP)


def normalize_input(text: str) -> str:
    """Canonicalize raw text before recognition.

    Strips Arabic diacritics and the tatweel; removes zero-width/bidi controls;
    normalizes non-breaking and other unusual spaces to a plain space; and maps
    non-Arabic look-alikes (Persian/Urdu yeh, kaf, heh; Persian digits) to their
    Arabic equivalents. Only removals change length; on already-clean,
    undiacritized text the mapping is 1:1, so character offsets are preserved.
    """
    return _DIACRITICS_RE.sub('', text).translate(_INPUT_TRANSLATE)


# Inline markers that break spelled-out numbers but carry no date meaning.
#  * Latin-script tokens — EIS1600 milestone markers (``ms027``), source ids
#    (``JK000412``, ``ara1``), page markers: a run with a letter is dropped
#    (``ست ms027 وسبعين`` would read as 6 instead of 76), a pure-digit run
#    (``748``) is kept.
#  * Editorial brackets/braces ``[ ]`` and ``{ }`` — critical editions wrap an
#    editor-supplied part of a date in them: ``سنة أربع عشرة [وثلاثمائة]`` would read
#    as 14 instead of 314, and ``سنة ست و { ثمانين ومائة }`` as 6, because the number
#    connector does not span the bracket.
_LATIN_TOKEN_RE = re.compile(r'[0-9A-Za-z]+')
_EDITORIAL_BRACKETS_RE = re.compile(r'[\[\]{}]')
_WHITESPACE_RE = re.compile(r'\s+')


def clean_text(text: str) -> str:
    """Strip inline markers that break number recognition, then collapse spaces.

    Removes Latin-script tokens (milestone/source/page markers, keeping pure-digit
    runs) and editorial square brackets, collapses whitespace and trims the ends.

    Unlike :func:`normalize_input`, this **changes the text length**, so character
    offsets no longer line up with the original text; use it only when offsets into
    the original are not needed (e.g. the batch tool, which keeps none).
    """
    cleaned = _LATIN_TOKEN_RE.sub(
        lambda m: m.group(0) if m.group(0).isdigit() else ' ', text)
    cleaned = _EDITORIAL_BRACKETS_RE.sub(' ', cleaned)
    return _WHITESPACE_RE.sub(' ', cleaned).strip()


_ALIFS_REG = '[إأٱآا]'
# Includes the bare hamza 'ء' in the character class so that a denormalized
# pattern still matches its own source string (e.g. 'ماءة'). The openiti
# original used '(?:[ؤئ]|[وي]ء)', which required a carrier letter and thus
# failed on bare medial hamza.
_HAMZAS_REG = '(?:[ؤئء]|[وي]ء)'


def normalize_ara_heavy(text: str) -> str:
    """Normalize Arabic text by simplifying alifs, alif maqsura, hamzas and
    ta marbuta, e.g. ``normalize_ara_heavy('قهوة') == 'قهوه'``."""
    for old, new in _NORMALIZE_REPLACEMENTS:
        text = text.replace(old, new)
    return text


def denormalize(text: str) -> str:
    """Replace normalizable characters with a regex snippet covering all
    spelling variants, e.g. ``denormalize('يحيى') == 'يحي[يى]'``."""
    text = re.sub(_ALIFS_REG, _ALIFS_REG, text)
    text = re.sub(r'[يى]\b', '[يى]', text)
    text = re.sub(r'[هة]\b', '[هة]', text)
    text = re.sub('[ؤئء]', _HAMZAS_REG, text)
    return text


def normalize_dict(vocabulary: Dict[str, int]) -> Dict[str, int]:
    """Return a copy of *vocabulary* with heavily-normalized keys.

    Entries are inserted in descending order of value so that when two keys
    collapse onto the same normalized form, the smaller value wins (same
    behaviour as the original eis1600 implementation).
    """
    normalized = {}
    for key, val in sorted(vocabulary.items(), key=lambda item: item[1], reverse=True):
        normalized[normalize_ara_heavy(key)] = val
    return normalized


def create_opt_pattern(values: Iterable[str]) -> str:
    """Build a regex alternation of denormalized variants, longest first."""
    return '|'.join(sorted((denormalize(value) for value in values), key=len, reverse=True))
