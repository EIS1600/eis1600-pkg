"""Compiled regex patterns for recognizing temporal expressions.

The date pattern is adapted from ``eis1600.dates.date_patterns``. It matches a
date phrase consisting of (all parts optional except the year keyword):

    [context words] [weekday] [day ordinal] [month] <sana> [digits] [spelled-out year]

Two variants are combined: the common order (ones, ten, hundred, thousand) and
the reversed order (hundred first, e.g. 'سنة مائتين وست وأربعين'). The reversed
variant is tried first.

Requires the third-party ``regex`` module because the two variants reuse the
same group names within one alternation, which stdlib ``re`` rejects.
"""
from regex import compile

from .normalization import create_opt_pattern, denormalize
from .vocabulary import (
    DATE_CATEGORIES_DICT,
    DAY_ELAPSED,
    DAY_FIRST,
    DAY_LAST,
    DAY_MID,
    DAY_REMAINING,
    BARE_WEEKDAYS,
    CENTURY_ORDINALS,
    NAMED_YEARS,
    YEAR_ORDINAL_ONES,
    DAY_ONES,
    DAY_TEN,
    HUNDRED,
    MONTHS,
    ONES,
    SANA,
    TEN,
    THOUSAND,
    WEEKDAYS,
)

AR_LETTERS_CHARSET = (
        u'ءآأؤإئا'
        u'بةتثجحخ'
        u'دذرزسشص'
        u'ضطظعغـف'
        u'قكلمنهو'
        u'ىيٱپچڤگ'
)
AR_CHR = '[' + AR_LETTERS_CHARSET + ']'
WORD = r'(?:(?:^|\s)' + AR_CHR + '+)'

# Optional punctuation tokens that may interrupt a date phrase.
_OPT_PUNCT = r'(?:\s[,،:\[\]/]+)??'

# Separator before the *first* token of the expression. Normally a date is
# preceded by a word (and thus a space), but a heading is often the bare date
# itself ('سنة اثنتين'), where the keyword sits at the very start of the string
# with no leading space. ``^`` only matches at offset 0, so downstream tokens
# (which are never at offset 0) still require a real space.
_SEP = r'(?:^|\s)'

AR_MONTHS = create_opt_pattern(MONTHS.keys())
AR_ONES = create_opt_pattern(ONES.keys())
AR_TEN = create_opt_pattern(TEN.keys())
AR_HUNDRED = create_opt_pattern(HUNDRED.keys())
AR_THOUSAND = create_opt_pattern(THOUSAND.keys())
AR_ONES_DAY = create_opt_pattern(DAY_ONES.keys())
AR_TEN_DAY = create_opt_pattern(DAY_TEN.keys())
AR_WEEKDAY = create_opt_pattern(WEEKDAYS.keys())
# Weekdays accepted inside a full date: the prefixed forms plus the bare names
# (الخميس), which are trusted here only because a day/month/year follows.
AR_WEEKDAY_INDATE = create_opt_pattern(list(WEEKDAYS.keys()) + list(BARE_WEEKDAYS.keys()))
AR_CENTURY_ORD = create_opt_pattern(CENTURY_ORDINALS.keys())
AR_SANA = '|'.join(denormalize(s) for s in SANA)
AR_DAY_ELAPSED = create_opt_pattern(DAY_ELAPSED)
AR_DAY_REMAINING = create_opt_pattern(DAY_REMAINING)
AR_DAY_FIRST = create_opt_pattern(DAY_FIRST)
AR_DAY_MID = create_opt_pattern(DAY_MID)
AR_DAY_LAST = create_opt_pattern(DAY_LAST)

# A day-within-month formula, occupying the day slot before the month:
#   * elapsed:   '[لـ]N [ليلة/ليال/يوم/أيام] خلون/خلت' -> day = N (cardinal count)
#   * remaining: '[لـ]N ... بقين/بقيت'                  -> day = length − N + 1
#   * start:     'غرة' / 'مستهل'                        -> day = 1
#   * middle:    'النصف [من]' / 'منتصف' / 'نصف'          -> day = 15
#   * last:      'سلخ'                                   -> day = month length
# The count reuses cardinal ONES (+ an optional DAY_TEN), e.g. 'لخمس عشرة خلت'.
_DAY_COUNT = (
    r'(?:'
    r'(?P<fc_ones>' + AR_ONES + r')(?:\s(?:و\s?)?(?P<fc_ten>' + AR_TEN_DAY + r'))?'
    r'|(?P<fc_ten2>' + AR_TEN_DAY + r')'
    r')'
)
_DAY_FORMULA = (
    r'(?:'
    r'ل?' + _DAY_COUNT +
    r'(?:\s(?:ليلة|ليال|ليله|يوما|يوم|أيام|ايام))?'
    r'\s(?:(?P<elapsed>' + AR_DAY_ELAPSED + r')|(?P<remaining>' + AR_DAY_REMAINING + r'))'
    r'|(?P<day_first>' + AR_DAY_FIRST + r')'
    r'|(?P<day_mid>' + AR_DAY_MID + r')(?:\sمن)?'
    r'|(?P<day_last>' + AR_DAY_LAST + r')'
    r')'
)

# A month with its optional surroundings: 'من شهر رمضان المعظم من'. A single
# attached proclitic (و / ب / ف / ل, as in 'وصفر'، 'برجب') is consumed before the
# month; inside a year-anchored date the year keeps this from over-matching.
_MONTH_PROCLITIC = r'(?:[وبفل])?'
_MONTH_CORE = (
    r'(?:(?:من\s)?(?:شهر\s)?)?'
    + _MONTH_PROCLITIC +
    r'(?P<month>(?:ال)?(?:' + AR_MONTHS + r'))'
    r'(?:\s(?:من|ف[يى])(?:\sشهور)?)?'
)

# The weekday may be followed by a connector (في / من) before the day or month,
# as in 'يوم الجمعة في المحرم'. Consuming it inside the weekday group keeps the
# weekday attached to the expression; a bare 'في المحرم' (no weekday) is
# unaffected and leaves 'في' in the context as before.
_DAY_AND_MONTH = (
    r'(?:' + _SEP + r'(?P<weekday>' + AR_WEEKDAY_INDATE + r')(?!' + AR_CHR + r')(?:\s(?:ف[يى]|من))?)?'
    # Day slot: a day-within-month formula, or an ordinal — either 'خامس عشر'
    # (ones, then an optional ten) or a bare ten on its own ('الثلاثين' = 30th).
    r'(?:' + _SEP + r'(?:' + _DAY_FORMULA + r'|'
    r'(?:ال)?(?:'
    r'(?P<day_ones>' + AR_ONES_DAY + r')(?:\s(?:و)?(?:ال)?(?P<day_ten>' + AR_TEN_DAY + r'))?'
    r'|(?P<day_ten_only>' + AR_TEN_DAY + r')'
    r')))?'
    r'(?:' + _SEP + _MONTH_CORE + r')?'
)

# The year keyword followed by an optional digit year like '748', '٧٤٨',
# optionally marked with ه / م / الهجرية.
_SANA_AND_DIGITS = (
    _SEP + r'(?P<sana>' + AR_SANA + r')' + _OPT_PUNCT +
    r'(?:\s(?P<digits_str>(?P<digits>[1-9١٢٣٤٥٦٧٨٩][\d٠١٢٣٤٥٦٧٨٩]{0,3})(?:\s(?:[هم]|الهجري[هة])|ه)?))?' +
    _OPT_PUNCT
)

# A thousand must not be followed by another thousand: 'ألف ألف' is a
# multiplicative amount (thousand-thousand = a million, as in 'ألف ألف درهم'),
# never a year. Appended after every thousand group so such amounts don't match.
_NOT_THOUSAND_NEXT = r'(?!\s+(?:' + AR_THOUSAND + r'))'

# The ones digit must not be the first word of a *spaced* hundred: in 'ثلاث مائة'
# (= 300) the ones group would otherwise grab 'ثلاث' (3) and leave 'مائة' (100),
# yielding 103. This guard makes the ones slot skip it so the hundred group
# matches the whole 'ثلاث مائة'.
_ONES_NOT_HUNDRED = r'(?!\s+(?:مائة|ماية|مئة|مية|ماءة|مائه))'

# Spelled-out year in the common order: ones, ten, hundred, thousand.
# 'خمس أو ست' ("five or six") keeps the first alternative; a footnote marker
# like '( 123 )' may interrupt the phrase.
_YEAR_WORDS = (
    r'(?:\s(?P<ones>' + AR_ONES + r')' + _ONES_NOT_HUNDRED + r')?'
    r'(?:\s(?P<opt_ones>[إأٱآا]و\s+(?:' + AR_ONES + r')))?' + _OPT_PUNCT +
    r'(?:\s(?P<note>\(\s+\d+\s+\)))?'
    r'(?:\s[و]?(?P<ten>' + AR_TEN + r'))?' + _OPT_PUNCT +
    r'(?:\s[و]?(?P<hundred>' + AR_HUNDRED + r'))?' + _OPT_PUNCT +
    # The 'و' before the thousand is captured: a genuine year joins it ('...وألف'),
    # while a bare 'ألف' after a number is a multiplicative amount (خمسمائة ألف).
    r'(?:\s(?P<thousand_conj>و)?(?P<thousand>' + AR_THOUSAND + r')' + _NOT_THOUSAND_NEXT + r')?' + _OPT_PUNCT
)

# Thousand-first order for years >= 1000: 'ألف ومائتين وخمسة وأربعين' = 1245. Here
# the thousand legitimately leads (no preceding number), so it is NOT a money
# amount; the reject in parse_year uses the components' positions to tell them apart.
_YEAR_WORDS_THOUSAND_FIRST = (
    r'\s(?P<thousand>' + AR_THOUSAND + r')' + _NOT_THOUSAND_NEXT + r'' + _OPT_PUNCT +
    r'(?:\s[و]?(?P<hundred>' + AR_HUNDRED + r'))?' + _OPT_PUNCT +
    r'(?:\s[و]?(?P<ones>' + AR_ONES + r'))?'
    r'(?:\s(?P<opt_ones>[إأٱآا]و\s+(?:' + AR_ONES + r')))?' + _OPT_PUNCT +
    r'(?:\s[و]?(?P<ten>' + AR_TEN + r'))?' + _OPT_PUNCT
)

# Reversed order with the hundred first: 'سنة مائتين وست وأربعين'.
_YEAR_WORDS_REVERSED = (
    r'\s(?P<hundred>' + AR_HUNDRED + r')' + _OPT_PUNCT +
    r'\s[و]?(?P<ones>' + AR_ONES + r')'
    r'(?:\s(?P<opt_ones>[إأٱآا]و\s+(?:' + AR_ONES + r')))?' + _OPT_PUNCT +
    r'\s[و]?(?P<ten>' + AR_TEN + r')' + _OPT_PUNCT +
    r'(?:\s(?P<thousand_conj>و)?(?P<thousand>' + AR_THOUSAND + r')' + _NOT_THOUSAND_NEXT + r')?' + _OPT_PUNCT
)

# The expression must end at a word boundary: either a following Arabic word,
# end of string, or a punctuation mark. The class includes Arabic punctuation
# (، ؛ ؟) and closing brackets/parens so a date glued to punctuation without a
# preceding space (e.g. 'سنة أربعين،') still terminates cleanly instead of
# failing to match (or worse, matching a truncated year).
_LOOKAHEAD = r'(?=' + WORD + r'|[\s.,،؛؟:)\]}]|$)'


def _date_pattern(year_words: str) -> str:
    # No leading context group: the category trigger is found separately by a
    # bounded look-back window in ``recognise_dates``. Anchoring the regex on the
    # expression (the sana keyword onward) avoids catastrophic backtracking that a
    # lazy multi-word context prefix caused — a ~20x speed-up on the date pass.
    return (
        r'(?P<expression>' + _DAY_AND_MONTH +
        r'(?P<year>' + _SANA_AND_DIGITS + year_words + r')'
        r')' + _LOOKAHEAD
    )


# Order matters: try the reversed (hundred-first) and thousand-first orders before
# the plain forward order, so 'سنة ألف ومائتين' matches fully as 1200 instead of the
# forward branch stopping at the leading 'ألف' (1000).
DATE_PATTERN = compile(
    _date_pattern(_YEAR_WORDS_REVERSED) + '|'
    + _date_pattern(_YEAR_WORDS_THOUSAND_FIRST) + '|'
    + _date_pattern(_YEAR_WORDS)
)

# A month name on its own (not necessarily part of a full date phrase),
# delimited so it is not matched inside a longer word. An attached proclitic
# (و / ب / ف / ل, as in 'وصفر') may precede it and is captured separately.
STANDALONE_MONTH_PATTERN = compile(
    r'(?<!\S)(?P<proclitic>[وبفل])?(?P<month>(?:ال)?(?:' + AR_MONTHS + r'))(?!' + AR_CHR + r')'
)

# Cue that must immediately precede a *bare* single-word month for it to be
# trusted as a date rather than a personal name (رجب، ربيع، شعبان) or a common
# word (صفر). Compound/qualified months (ربيع الأول، ذي القعدة) are trusted on
# their own and bypass this check. The cue may carry a conjunction prefix, as in
# 'وفي رمضان'.
STANDALONE_MONTH_CUE = compile(r'(?:شهر|ف[يى]|من)\s$')

# A day-within-month formula ending immediately before a month, used to attach a
# day to a *standalone* month that has no year (e.g. 'غرة رمضان', 'لثلاث خلون من
# رجب'). Matched against the text preceding the month; `formula` is its span.
DAY_FORMULA_BEFORE_MONTH = compile(
    r'(?<!\S)(?P<formula>'
    r'ل?' + _DAY_COUNT + r'(?:\s(?:ليلة|ليال|ليله|يوما|يوم|أيام|ايام))?'
    r'\s(?:(?P<elapsed>' + AR_DAY_ELAPSED + r')|(?P<remaining>' + AR_DAY_REMAINING + r'))\s(?:من\s)?'
    r'|(?P<day_first>' + AR_DAY_FIRST + r')\s'
    r'|(?P<day_mid>' + AR_DAY_MID + r')(?:\sمن)?\s'
    r'|(?P<day_last>' + AR_DAY_LAST + r')\s'
    r')$'
)

# A weekday name on its own ('يوم الجمعة' / 'ليلة الأربعاء'), delimited so it is
# not matched inside a longer word. Trusted as a date only with a nearby trigger.
STANDALONE_WEEKDAY_PATTERN = compile(
    r'(?<!\S)(?P<weekday>' + AR_WEEKDAY + r')(?!' + AR_CHR + r')'
)

# Ordinal-year form used in chronicle section headings: 'السنة السادسة والأربعون
# وست مئة' = 646, 'السنة الحادية والعشرين ومائة' = 121, 'السنة الخامسة من الهجرة' = 5.
# Structure: (ال)سنة + fem-ordinal-ones (+ 'عشرة' teen | + و<ten>) (+ و<hundred>)
# (+ و<thousand>), optionally closed by a hijra marker. A lone single ordinal with
# no ten/teen/hundred/hijra is rejected in the parser (it is usually a reign year,
# 'السنة السادسة من ولايته'). The tens/hundreds/thousands reuse the cardinal vocab.
AR_YEAR_ORDINAL_ONES = create_opt_pattern(YEAR_ORDINAL_ONES.keys())
_HIJRA = r'(?:من\s+)?(?:لل|ال)?هجر(?:ي?[ةه])'
ORDINAL_YEAR_PATTERN = compile(
    _SEP + r'(?P<expression>ال?سنة\s'
    r'(?P<ord_ones>' + AR_YEAR_ORDINAL_ONES + r')'
    r'(?:\s(?P<ord_teen>عشر[ةه]?))?'
    r'(?:\s[و]?(?P<ten>' + AR_TEN + r'))?'
    r'(?:\s[و]?(?P<hundred>' + AR_HUNDRED + r'))?'
    r'(?:\s[و]?(?P<thousand>' + AR_THOUSAND + r'))?'
    r')(?:\s(?P<hijra>' + _HIJRA + r'))?'
    + _LOOKAHEAD
)

# Named years ('عام الفتح' = the Year of the Conquest = 8 AH), matched only in
# gazetteer mode. Delimited so it is not caught inside a longer word.
AR_NAMED_YEAR = create_opt_pattern(NAMED_YEARS.keys())
NAMED_YEAR_PATTERN = compile(
    _SEP + r'(?P<expression>(?P<named_year>' + AR_NAMED_YEAR + r'))(?!' + AR_CHR + r')'
)

# A century phrase ('القرن الثامن' = the 8th century), optionally introduced by a
# cue (في / حدود) and a conjunction. ``expression`` spans just 'القرن <ordinal>'.
CENTURY_PATTERN = compile(
    _SEP + r'[وف]?(?:(?:ف[يى]|حدود)\s)*'
    r'(?P<expression>القرن\s(?P<century_ord>' + AR_CENTURY_ORD + r'))'
    r'(?!' + AR_CHR + r')'
)

# A trigger stem may be followed only by a valid inflectional suffix (pronoun /
# past-tense marker / تاء marbūṭa), then a word boundary. This keeps genuine
# forms (مولده، وفاته، حدثنا، ولدت، توفيت) while rejecting look-alikes where the
# stem is merely the start of a different word (سمعان، وليد، حجاج، توفيق، قرآن).
_TRIGGER_SUFFIX = (
    r'(?:'
    r'تهما|تها|تهم|تهن|تكما|تكم|تكن|تنا|تما|'  # تاء-linked noun + pronoun
    r'هما|كما|ها|هم|هن|نا|كم|كن|ني|تم|تن|تا|تي|تك|ته|وا|ات|'
    r'ه|ة|ت|ي|ك'
    r')'
)
# Category trigger, optionally prefixed with the conjunctions و / ف and/or the
# article ال (so الوفاة، المتوفى، المولد are classified like their bare stems).
AR_DATE_CATEGORIES = create_opt_pattern(DATE_CATEGORIES_DICT.keys())
DATE_CATEGORY_PATTERN = compile(
    r'(?:^|\s)[وف]?(?:ال)?(?P<trigger>' + AR_DATE_CATEGORIES + r')'
    + _TRIGGER_SUFFIX + r'?(?!' + AR_CHR + r')'
)
