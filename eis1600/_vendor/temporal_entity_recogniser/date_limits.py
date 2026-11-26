"""Helpers for conservative Hijri-year range checks."""
from __future__ import annotations

from datetime import date

try:
    from convertdate import islamic as _islamic
except ImportError:  # pragma: no cover - fallback when convertdate is absent
    _islamic = None

REFERENCE_TODAY = date(2026, 7, 31)


def current_hijri_year(today: date | None = None) -> int:
    """Current Hijri year for *today*.

    Uses ``convertdate`` when available. Falls back to a close linear estimate
    so callers can still block obviously-future years in lightweight setups.
    """
    today = today or REFERENCE_TODAY
    if _islamic is not None:
        year, _month, _day = _islamic.from_gregorian(today.year, today.month, today.day)
        return int(year)
    return round((today.year - 622) / 0.97023)


def is_future_hijri_year(year: int, max_hijri_year: int | None = None) -> bool:
    """Whether *year* is beyond the allowed Hijri cutoff."""
    return year > (current_hijri_year() if max_hijri_year is None else max_hijri_year)
