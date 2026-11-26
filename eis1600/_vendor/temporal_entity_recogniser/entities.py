"""The structured result type returned by the recogniser."""
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

try:
    from convertdate import islamic as _islamic
except ImportError:  # pragma: no cover - exercised only when convertdate is absent
    _islamic = None


@dataclass
class TemporalEntity:
    """A temporal expression recognized in an Arabic text.

    :param text: the full captured text: from the category trigger word (if
        one was found) through the end of the temporal expression.
    :param expression: the temporal expression proper (weekday, day, month and
        year phrase). Always a suffix of ``text``.
    :param start: character offset of ``text`` in the input.
    :param end: character offset of the end of ``text`` in the input.
    :param entity_type: ``'year'`` for a full date phrase anchored on a year
        keyword, ``'month'`` for a standalone month name, ``'weekday'`` for a
        trigger-anchored weekday, ``'century'`` for a century phrase
        (``القرن الثامن``).
    :param year_hijri: the Hijri year converted to an integer, if a year was given.
    :param year_ce: the Gregorian (CE) year, derived from ``year_hijri`` via
        :meth:`hijri2CE`, if a year was given.
    :param month: the month number (1-12), if a month was recognized.
    :param day: the day of the month (1-30), if given. A "remaining"/"last"
        formula (``لسبع بقين``، ``سلخ``) whose exact day cannot be computed —
        Dhū al-Ḥijja with no year (29 or 30) — yields the sentinel **-1**
        (``recogniser.UNKNOWN_DAY``): the day is known to be the month's last
        day(s) but its number is ambiguous.
    :param century: the Hijri century number (e.g. 8 for ``القرن الثامن``), set
        only on a ``'century'`` entity.
    :param weekday: the day of the week (1 = Sunday ... 7 = Saturday), if given.
    :param category: date class - B (birth), D (death), P (pilgrimage),
        K (knowledge transmission), O (office), X (unclassified).
    :param trigger: the context word that determined ``category``, if any.
    :param length: Legacy EIS1600 tag width: the number of whitespace-delimited
        tokens represented by the tag, **not** a character length, a source-span
        length, or a duration. :meth:`to_tag` embeds this number immediately
        after the entity-kind letter (for example, ``ÜY4D0748Y`` means a
        year tag with width 4). For year entities it is counted from the
        ``سنة`` (year) keyword to the end of the expression, excluding a
        preceding trigger and any earlier day/month/weekday material. For a
        standalone month it is the recognized month span, including an attached
        day formula when present. Weekday and century entities count their
        respective expression spans. It is retained solely to reproduce
        EIS1600's inline-tag format; use ``start``, ``end``, and
        ``expression`` to locate an entity in contemporary consumers.
    """
    text: str
    expression: str
    start: int
    end: int
    entity_type: str
    year_hijri: Optional[int] = None
    year_ce: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    century: Optional[int] = None
    weekday: Optional[int] = None
    category: str = 'X'
    trigger: Optional[str] = None
    length: int = 0

    @property
    def expression_start(self) -> int:
        """Character offset of ``expression`` in the input."""
        return self.end - len(self.expression)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def hijri2CE(year: int) -> int:
        """Convert a Hijri year to a Gregorian (CE) year.

        Uses the tabular Islamic calendar via :mod:`convertdate` when it is
        installed, taking the Gregorian year in which 1 Muḥarram of *year*
        falls. Falls back to a linear approximation (``year * 0.97023 + 622``)
        when convertdate is not available.
        """
        if _islamic is not None:
            gregorian_year, _month, _day = _islamic.to_gregorian(year, 1, 1)
            return gregorian_year
        return int(year * 0.97023 + 622)

    def to_tag(self) -> str:
        """Render the EIS1600 inline tag for this entity: ``ÜY4D0748Y`` for a
        year, ``ÜL2X09L`` for a month, ``ÜW1D6W`` for a weekday, ``ÜC2X08C`` for a
        century. The digit after the entity-kind letter is the legacy token
        width stored in :attr:`length`."""
        if self.entity_type == 'year':
            return f'ÜY{self.length}{self.category}{self.year_hijri:04d}Y'
        if self.entity_type == 'century':
            return f'ÜC{self.length}{self.category}{self.century:02d}C'
        if self.entity_type == 'weekday':
            return f'ÜW{self.length}{self.category}{self.weekday}W'
        return f'ÜL{self.length}X{self.month:02d}L'
