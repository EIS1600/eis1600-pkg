"""Rule-based recogniser for temporal expressions in classical Arabic texts.

Recognizes Hijri year phrases (spelled out and/or in digits) and Islamic month
names, converts them to numeric values and classifies year statements by the
trigger word in the preceding context (birth, death, pilgrimage, ...).

Logic adapted from ``eis1600.dates.date_methods`` / ``month_methods``, but
instead of splicing inline tags into the text it returns a list of
:class:`~temporal_entity_recogniser.entities.TemporalEntity` objects carrying
the matched text and character offsets.
"""
import logging
from typing import Dict, List, Optional, Tuple

from regex import Match

from .entities import TemporalEntity
from .normalization import normalize_ara_heavy, normalize_input
from .patterns import (
    CENTURY_PATTERN,
    DATE_CATEGORY_PATTERN,
    DATE_PATTERN,
    DAY_FORMULA_BEFORE_MONTH,
    NAMED_YEAR_PATTERN,
    ORDINAL_YEAR_PATTERN,
    STANDALONE_MONTH_CUE,
    STANDALONE_MONTH_PATTERN,
    STANDALONE_WEEKDAY_PATTERN,
)
from .vocabulary import (
    CENTURY_ORDINALS_NOR,
    DATE_CATEGORIES_NOR,
    DAY_ONES_NOR,
    DAY_TEN_NOR,
    HUNDRED_NOR,
    MONTH_STANDARD_LENGTH,
    MONTHS_NOR,
    NAMED_YEARS_NOR,
    ONES_NOR,
    TEN_NOR,
    THOUSAND_NOR,
    WEEKDAYS_ALL_NOR,
    WEEKDAYS_NOR,
    YEAR_ORDINAL_ONES_NOR,
)

try:
    from convertdate import islamic as _islamic
except ImportError:  # pragma: no cover - fallback when convertdate is absent
    _islamic = None

logger = logging.getLogger(__name__)

# Separate logger for date-consistency warnings (e.g. a day beyond its month's
# length) so callers can route or silence them independently of the noisier
# per-record recognition warnings on ``logger``.
validation_logger = logging.getLogger('temporal_entity_recogniser.validation')

# Trailing characters trimmed off the recognized expression.
_TRAILING_JUNK = ' \t\n,،:/][.'

# Sentinel for a day that a formula ('لسبع بقين', 'سلخ') refers to but whose exact
# value cannot be computed because the month length is unknown — i.e. Dhū
# al-Ḥijja (29 or 30, depending on the leap year) with no year to disambiguate.
UNKNOWN_DAY = -1


def _month_length(year: Optional[int], month: int) -> Optional[int]:
    """The exact length of *month* in days, or ``None`` if it is unknowable.

    With a year, convertdate gives the tabular length (handling Dhū al-Ḥijja's
    29/30 leap variation). Without a year, months 1–11 have a fixed tabular
    length; Dhū al-Ḥijja (12) is genuinely ambiguous, so ``None`` is returned.
    """
    if year is not None and _islamic is not None:
        try:
            return _islamic.month_length(year, month)
        except (ValueError, IndexError, OverflowError):
            pass
    if month == 12:
        return None
    return MONTH_STANDARD_LENGTH.get(month)


def _month_max_days(year: Optional[int], month: int) -> Optional[int]:
    """Largest valid day for *month* (used for the advisory over-length check).

    Like :func:`_month_length` but never ``None``: an unknown Dhū al-Ḥijja falls
    back to its maximum (30) so legitimate leap-year dates are not flagged."""
    length = _month_length(year, month)
    return length if length is not None else MONTH_STANDARD_LENGTH.get(month)


def _warn_if_day_exceeds_month(year: Optional[int], month: Optional[int],
                               day: Optional[int], context: str) -> None:
    """Warn (advisory) if *day* is beyond the length of *month*."""
    if month is None or day is None or day <= 0:  # <=0 includes the UNKNOWN_DAY sentinel
        return
    max_days = _month_max_days(year, month)
    if max_days is not None and day > max_days:
        validation_logger.warning(
            'Day %d exceeds the length of month %d (%d days) in %r',
            day, month, max_days, context.strip()
        )


def _lookup(table: Dict[str, int], raw: str) -> int:
    value = table.get(normalize_ara_heavy(raw))
    if value is None:
        # Should not happen: the regex only matches words derived from the
        # same vocabulary. Be defensive rather than crash on a whole corpus.
        logger.warning('Unmapped word %r in temporal expression', raw)
        return 0
    return value


def parse_year(m: Match) -> Optional[int]:
    """Convert the year components of a date match to an integer Hijri year.

    Sums the spelled-out components (ones, ten, hundred, thousand). If the
    phrase also (or only) contains a digit year, the two are reconciled: normally
    the spelled-out value wins, but when it is a lone single component (exactly
    one of ones/ten/hundred/thousand, e.g. a stray 'خمس' / 'تسعمائة' / 'ألف'
    dangling after a full digit year as in 'سنة 981 خمس') the digit is trusted
    instead. Either way a mismatch is logged.

    Returns ``None`` if the match contains no year value at all (usually an
    age phrase like 'ثمانون سنة').
    """
    year = 0
    n_components = 0
    for group, table in (
            ('ones', ONES_NOR),
            ('ten', TEN_NOR),
            ('hundred', HUNDRED_NOR),
            ('thousand', THOUSAND_NOR),
    ):
        raw = m.group(group)
        if raw:
            year += _lookup(table, raw)
            n_components += 1

    # Reject multiplicative money amounts misread as years: a thousand ('ألف')
    # right after a number with no connecting 'و' means "N thousand" (خمسمائة ألف
    # = 500,000, أربعين ألف = 40,000), not a year. A genuine year >1000 either joins
    # the thousand with 'و' ('...وألف') or leads with it ('ألف ومائتين'); a bare
    # 'ألف' (=1000) has no preceding component. So reject only when a number
    # component sits *before* the thousand with no 'و' directly on it. This catches
    # amounts the future-year guard misses because they fall in range (أربعين ألف).
    if m.group('thousand') and m.group('thousand_conj') is None:
        th_start = m.start('thousand')
        if any(m.group(g) and m.start(g) < th_start for g in ('hundred', 'ten', 'ones')):
            return None

    digits = m.group('digits')
    if digits:
        # int() accepts Arabic-Indic digits (٧٤٨) as well as ASCII ones.
        year_digits = int(digits)
        if year == 0:
            year = year_digits
        elif year != year_digits:
            # A single spelled component is almost always a fragment stranded
            # after the (fuller) digit year, so trust the digit there; a compound
            # spelled value is the genuine year (the digit is usually a truncation
            # like 94 for 944), so keep it.
            if n_components == 1:
                logger.warning(
                    'Date recognition: spelled-out year (%d) is a lone fragment != '
                    'digit year (%d) in %r; keeping the digit value',
                    year, year_digits, m.group(0).strip()
                )
                year = year_digits
            else:
                logger.warning(
                    'Date recognition: spelled-out year (%d) != digit year (%d) in %r; '
                    'keeping the spelled-out value', year, year_digits, m.group(0).strip()
                )

    # The definite 'السنة' is a weak year cue — it also heads "per year" rates
    # ('في السنة خمسة دنانير') and reign years — so trust it only with a digit year
    # or a hundreds/thousands component ('السنة 329', 'السنة خمس وعشرين وثلاثمائة'),
    # not a bare ones/ten which is usually a rate.
    sana = m.group('sana')
    if (sana and normalize_ara_heavy(sana).startswith('ال')
            and not (digits or m.group('hundred') or m.group('thousand'))):
        return None

    return year if year else None


def _parse_month(raw: Optional[str]) -> Optional[int]:
    if not raw:
        return None
    if raw.startswith('ال'):
        raw = raw[2:]
    month = MONTHS_NOR.get(normalize_ara_heavy(raw))
    if month == -1:
        # 'اخر' ("end of ...") is consumed by the pattern but is not a month.
        return None
    return month


def _formula_count(m: Match) -> int:
    """The cardinal night-count of an elapsed/remaining formula (0 if absent)."""
    count = 0
    if m.group('fc_ones'):
        count += _lookup(ONES_NOR, m.group('fc_ones'))
    if m.group('fc_ten'):
        count += _lookup(DAY_TEN_NOR, m.group('fc_ten'))
    if m.group('fc_ten2'):
        count += _lookup(DAY_TEN_NOR, m.group('fc_ten2'))
    return count


def _parse_day_formula(m: Match, year: Optional[int] = None,
                       month: Optional[int] = None) -> Optional[int]:
    """Day from a within-month formula (غرة / النصف / خلون / بقين / سلخ), or None.

    'بقين' (remaining) and 'سلخ' (last) need the month's length: it is taken from
    *year*+*month* (exact) or *month* alone (tabular); when the length is unknown
    (Dhū al-Ḥijja with no year) the day is the ``UNKNOWN_DAY`` sentinel (-1).
    Works on both the full date pattern and the ``DAY_FORMULA_BEFORE_MONTH`` tail.
    """
    if m.group('day_first'):        # غرة / مستهل
        return 1
    if m.group('day_mid'):          # النصف من / منتصف / نصف
        return 15
    if m.group('day_last'):         # سلخ -> the last day = the month's length
        length = _month_length(year, month) if month else None
        return length if length is not None else UNKNOWN_DAY
    if m.group('elapsed'):          # 'لثلاث خلون من ...' -> the cardinal count
        return _formula_count(m) or None
    if m.group('remaining'):        # 'لسبع بقين من ...' -> length − count + 1
        count = _formula_count(m)
        if not count:
            return None
        length = _month_length(year, month) if month else None
        return (length - count + 1) if length is not None else UNKNOWN_DAY
    return None


def _parse_day(m: Match, year: Optional[int] = None,
               month: Optional[int] = None) -> Optional[int]:
    # Day-within-month formulas take precedence over the plain 'خامس عشر' ordinal.
    formula_day = _parse_day_formula(m, year, month)
    if formula_day is not None:
        return formula_day

    day = 0
    if m.group('day_ones'):
        day += _lookup(DAY_ONES_NOR, m.group('day_ones'))
    if m.group('day_ten'):
        day += _lookup(DAY_TEN_NOR, m.group('day_ten'))
    if m.group('day_ten_only'):     # a ten-ordinal on its own, e.g. 'الثلاثين'
        day += _lookup(DAY_TEN_NOR, m.group('day_ten_only'))
    return day if day else None


def _classify(context: str) -> Tuple[str, Optional[Match]]:
    """Return the date category based on the last trigger word in *context*,
    together with the trigger match ('X' and None if there is no trigger)."""
    matches = list(DATE_CATEGORY_PATTERN.finditer(context))
    if not matches:
        return 'X', None
    last = matches[-1]
    category = DATE_CATEGORIES_NOR.get(normalize_ara_heavy(last.group('trigger')), 'X')
    return category, last


# How far back (characters) to look for the category trigger before a date/century
# /ordinal, matching the old ~20-word context window. The search stops at the last
# sentence-ending full stop so a trigger does not bleed across a sentence boundary.
_CLASSIFY_WINDOW = 160


def _classify_before(text: str, pos: int) -> Tuple[str, Optional[str], Optional[int]]:
    """Classify the phrase at *pos* from the last trigger in the preceding window.

    Looks back up to :data:`_CLASSIFY_WINDOW` characters but not across the last
    full stop. Returns ``(category, trigger, trigger_start)``; the trigger and its
    start are ``None`` when none is found. Replaces the former in-regex context
    group, which caused catastrophic backtracking in ``DATE_PATTERN``.
    """
    start = max(0, pos - _CLASSIFY_WINDOW)
    context = text[start:pos]
    cut = context.rfind('.')
    if cut != -1:
        start += cut + 1
        context = context[cut + 1:]
    category, trigger_m = _classify(context)
    if trigger_m is None:
        return 'X', None, None
    return category, trigger_m.group('trigger'), start + trigger_m.start('trigger')


# The date regex can only match around a year keyword (سنة / عام / في حدود); every
# such keyword contains one of these substrings, so a text without them cannot
# contain a date and the (still non-trivial) scan is skipped.
_YEAR_KEYWORD_HINTS = ('سن', 'عام', 'حدود')


def recognise_dates(text: str) -> List[TemporalEntity]:
    """Recognize year-anchored date phrases in *text*.

    Matches that contain a year keyword but no actual year value (typically
    age phrases such as 'وعمره ثمانون سنة') are skipped.
    """
    if not any(hint in text for hint in _YEAR_KEYWORD_HINTS):
        return []
    entities = []
    for m in DATE_PATTERN.finditer(text):
        year = parse_year(m)
        if year is None:
            continue

        expression = m.group('expression')
        expr_start = m.start('expression') + (len(expression) - len(expression.lstrip()))
        expression = expression.strip().rstrip(_TRAILING_JUNK)
        expr_end = expr_start + len(expression)

        category, trigger, trigger_start = _classify_before(text, m.start('expression'))
        if trigger_start is not None:
            start = trigger_start
        else:
            start = expr_start

        month = _parse_month(m.group('month'))
        entities.append(TemporalEntity(
            text=text[start:expr_end],
            expression=expression,
            start=start,
            end=expr_end,
            entity_type='year',
            year_hijri=year,
            year_ce=TemporalEntity.hijri2CE(year),
            month=month,
            day=_parse_day(m, year, month),
            weekday=WEEKDAYS_ALL_NOR.get(normalize_ara_heavy(m.group('weekday') or '')),
            category=category,
            trigger=trigger,
            length=len(text[m.start('sana'):expr_end].split()),
        ))
    return entities


def _standalone_month_trusted(text: str, m: Match) -> bool:
    """Whether a standalone month match is a date rather than a name/word.

    Many month names double as personal names (رجب، ربيع، شعبان) or words
    (صفر). A bare single-word month is trusted only when introduced by a cue
    (شهر / في / من); a compound or qualified month (ربيع الأول، ذي القعدة,
    رمضان المعظم — anything with more than one token) is trusted on its own.

    A bare proclitic (وصفر، برجب) is *not* enough on its own — 'ب' especially is
    ambiguous ('بصفر اليدين' = "empty-handed") — so a proclitic month still needs
    a cue or to be compound; the cue is looked for before the proclitic.
    """
    if len(m.group('month').split()) > 1:
        return True
    boundary = m.start('proclitic') if m.group('proclitic') else m.start('month')
    return STANDALONE_MONTH_CUE.search(text[:boundary]) is not None


def recognise_months(text: str) -> List[TemporalEntity]:
    """Recognize standalone Islamic month names in *text*.

    A day-within-month formula immediately before the month (e.g. 'غرة رمضان',
    'لثلاث خلون من رجب') is attached as the ``day`` and folded into the span.
    """
    entities = []
    for m in STANDALONE_MONTH_PATTERN.finditer(text):
        raw = m.group('month')
        month = _parse_month(raw)
        if month is None:
            continue

        start = m.start('month')
        # A day-within-month formula right before the month is itself a strong
        # date cue, so it trusts an otherwise-bare month (غرة رمضان); otherwise
        # the usual cue guard applies.
        tail = DAY_FORMULA_BEFORE_MONTH.search(text[:start])
        if tail is None and not _standalone_month_trusted(text, m):
            continue

        day = None
        if tail is not None:
            # No year in a standalone month, so بقين/سلخ use the tabular length.
            day = _parse_day_formula(tail, year=None, month=month)
            start = tail.start('formula')

        span = text[start:m.end('month')]
        entities.append(TemporalEntity(
            text=span,
            expression=span,
            start=start,
            end=m.end('month'),
            entity_type='month',
            month=month,
            day=day,
            length=len(span.split()),
        ))
    return entities


def recognise_weekdays(text: str) -> List[TemporalEntity]:
    """Recognize a weekday ('يوم الجمعة' / 'ليلة الأحد') that has no month or year.

    A bare weekday is overwhelmingly a non-date reference (Friday prayer, ...),
    so one is emitted only when a category trigger (توفي، ولد، ...) sits close
    before it — e.g. 'توفي يوم الجمعة'.
    """
    entities = []
    for m in STANDALONE_WEEKDAY_PATTERN.finditer(text):
        weekday = WEEKDAYS_NOR.get(normalize_ara_heavy(m.group('weekday')))
        if weekday is None:
            continue
        # Require a trigger within a short window before the weekday.
        window_start = max(0, m.start('weekday') - 120)
        category, trigger_m = _classify(text[window_start:m.start('weekday')])
        if trigger_m is None:
            continue
        start = window_start + trigger_m.start('trigger')
        entities.append(TemporalEntity(
            text=text[start:m.end('weekday')],
            expression=m.group('weekday'),
            start=start,
            end=m.end('weekday'),
            entity_type='weekday',
            weekday=weekday,
            category=category,
            trigger=trigger_m.group('trigger'),
            length=len(m.group('weekday').split()),
        ))
    return entities


def recognise_centuries(text: str) -> List[TemporalEntity]:
    """Recognize century phrases ('القرن الثامن' = the 8th century) in *text*.

    Emits a ``'century'`` entity carrying the century number; there is no single
    Hijri year, so ``year_hijri`` stays ``None``. The preceding context is
    classified for a category trigger just like a year date (توفي → death).
    """
    entities = []
    for m in CENTURY_PATTERN.finditer(text):
        century = CENTURY_ORDINALS_NOR.get(normalize_ara_heavy(m.group('century_ord')))
        if century is None:
            continue
        expr_start, expr_end = m.start('expression'), m.end('expression')
        window_start = max(0, expr_start - 120)
        category, trigger_m = _classify(text[window_start:expr_start])
        if trigger_m is not None:
            trigger = trigger_m.group('trigger')
            start = window_start + trigger_m.start('trigger')
        else:
            trigger = None
            start = expr_start
        entities.append(TemporalEntity(
            text=text[start:expr_end],
            expression=text[expr_start:expr_end],
            start=start,
            end=expr_end,
            entity_type='century',
            century=century,
            category=category,
            trigger=trigger,
            length=len(m.group('expression').split()),
        ))
    return entities


def recognise_ordinal_years(text: str) -> List[TemporalEntity]:
    """Recognize ordinal-year forms ('السنة السادسة والأربعون وست مئة' = 646) used
    in chronicle section headings.

    A lone single ordinal with no tens/teen/hundred and no hijra marker
    ('السنة السادسة') is skipped — it is usually a reign year, not a Hijri date.
    Classified from the preceding context like a cardinal date.
    """
    entities = []
    for m in ORDINAL_YEAR_PATTERN.finditer(text):
        has_more = any(m.group(g) for g in ('ord_teen', 'ten', 'hundred', 'thousand'))
        if not has_more and not m.group('hijra'):
            continue
        year = _lookup(YEAR_ORDINAL_ONES_NOR, m.group('ord_ones'))
        if m.group('ord_teen'):
            year += 10
        if m.group('ten'):
            year += _lookup(TEN_NOR, m.group('ten'))
        if m.group('hundred'):
            year += _lookup(HUNDRED_NOR, m.group('hundred'))
        if m.group('thousand'):
            year += _lookup(THOUSAND_NOR, m.group('thousand'))

        expr_start, expr_end = m.start('expression'), m.end('expression')
        window_start = max(0, expr_start - 120)
        category, trigger_m = _classify(text[window_start:expr_start])
        if trigger_m is not None:
            trigger = trigger_m.group('trigger')
            start = window_start + trigger_m.start('trigger')
        else:
            trigger = None
            start = expr_start
        entities.append(TemporalEntity(
            text=text[start:expr_end],
            expression=text[expr_start:expr_end],
            start=start,
            end=expr_end,
            entity_type='year',
            year_hijri=year,
            year_ce=TemporalEntity.hijri2CE(year),
            category=category,
            trigger=trigger,
            length=len(text[expr_start:expr_end].split()),
        ))
    return entities


def recognise_named_years(text: str) -> List[TemporalEntity]:
    """Recognize named years ('عام الفتح' = Year of the Conquest = 8 AH).

    Only the small :data:`NAMED_YEARS` gazetteer is matched; a name is a weaker
    signal than a spelled/digit year, so this runs only in gazetteer mode.
    Classified from the preceding context like a cardinal date.
    """
    entities = []
    for m in NAMED_YEAR_PATTERN.finditer(text):
        year = NAMED_YEARS_NOR.get(normalize_ara_heavy(m.group('named_year')))
        if year is None:
            continue
        expr_start, expr_end = m.start('expression'), m.end('expression')
        window_start = max(0, expr_start - 120)
        category, trigger_m = _classify(text[window_start:expr_start])
        if trigger_m is not None:
            trigger = trigger_m.group('trigger')
            start = window_start + trigger_m.start('trigger')
        else:
            trigger = None
            start = expr_start
        entities.append(TemporalEntity(
            text=text[start:expr_end],
            expression=text[expr_start:expr_end],
            start=start,
            end=expr_end,
            entity_type='year',
            year_hijri=year,
            year_ce=TemporalEntity.hijri2CE(year),
            category=category,
            trigger=trigger,
            length=len(text[expr_start:expr_end].split()),
        ))
    return entities


def _overlaps(entity: TemporalEntity, others: List[TemporalEntity]) -> bool:
    """Whether *entity*'s temporal span overlaps any of *others*' spans."""
    return any(
        entity.expression_start < other.end and other.expression_start < entity.end
        for other in others
    )


def recognise(text: str, gazetteer: bool = False) -> List[TemporalEntity]:
    """Recognize all temporal expressions in *text*, sorted by position.

    Standalone month and weekday entities already covered by a fuller phrase are
    suppressed (a date's month/weekday is available in its own attributes).

    When *gazetteer* is true, named years ('عام الفتح' = 8 AH) from the
    :data:`~temporal_entity_recogniser.vocabulary.NAMED_YEARS` gazetteer are also
    matched; it is off by default because a name is a weaker signal than a
    spelled/digit year.

    The text is first canonicalized (diacritics stripped, Persian look-alikes
    mapped) via :func:`normalize_input`, so entity offsets index that normalized
    text; on already-undiacritized input the mapping is 1:1 and offsets are
    unchanged.
    """
    text = normalize_input(text)
    dates = recognise_dates(text)
    ordinals = [o for o in recognise_ordinal_years(text) if not _overlaps(o, dates)]
    dates = dates + ordinals
    if gazetteer:
        named = [n for n in recognise_named_years(text) if not _overlaps(n, dates)]
        dates = dates + named
    months = [m for m in recognise_months(text) if not _overlaps(m, dates)]
    covered = dates + months
    weekdays = [w for w in recognise_weekdays(text) if not _overlaps(w, covered)]
    covered = covered + weekdays
    centuries = [c for c in recognise_centuries(text) if not _overlaps(c, covered)]
    result = sorted(dates + months + weekdays + centuries,
                    key=lambda entity: (entity.start, entity.end))
    # Advisory day-in-month sanity check on the final (deduplicated) entities.
    for entity in result:
        _warn_if_day_exceeds_month(entity.year_hijri, entity.month, entity.day, entity.expression)
    return result
