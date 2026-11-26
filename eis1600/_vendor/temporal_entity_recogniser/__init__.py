"""Rule-based temporal entity recogniser for classical Arabic texts.

Recognizes Hijri year phrases and Islamic month names, converts them to
numeric values and classifies year statements (birth, death, pilgrimage,
knowledge transmission, office).

    >>> from temporal_entity_recogniser import recognise
    >>> recognise('توفي سنة ثمان وأربعين وسبعمائة')
    [TemporalEntity(text='توفي سنة ثمان وأربعين وسبعمائة', ..., year_hijri=748, year_ce=1347, category='D', ...)]
"""
from .entities import TemporalEntity
from .logging_setup import configure_logging
from .markup import annotate
from .normalization import clean_text, normalize_input
from .recogniser import (
    UNKNOWN_DAY,
    recognise,
    recognise_centuries,
    recognise_dates,
    recognise_months,
    recognise_named_years,
    recognise_ordinal_years,
    recognise_weekdays,
)
from .vocabulary import DATE_CATEGORIES

__version__ = '0.1.0'

__all__ = [
    'TemporalEntity',
    'annotate',
    'clean_text',
    'configure_logging',
    'normalize_input',
    'recognise',
    'recognise_centuries',
    'recognise_dates',
    'recognise_months',
    'recognise_named_years',
    'recognise_ordinal_years',
    'recognise_weekdays',
    'UNKNOWN_DAY',
    'DATE_CATEGORIES',
    '__version__',
]
