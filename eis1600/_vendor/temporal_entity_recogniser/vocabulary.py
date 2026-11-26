"""Arabic vocabularies for temporal expressions.

Dictionaries map Arabic (spelled-out) number words, month names, weekdays and
date-category trigger words to their numeric values / category codes. The
``*_NOR`` variants have heavily-normalized keys and are used to look up
matched (raw) text after normalizing it.

Taken from ``eis1600.dates.date_patterns`` with two fixes:
- the weekday key for Thursday had a typo ('يمو الخميس'), now 'يوم الخميس'
- the redundant double normalization of THOUSAND was removed
"""
from .normalization import normalize_dict

ONES = {
        'واحد': 1, 'الواحد': 1, 'احدى': 1, 'احد': 1,
        'اثنين': 2, 'الاثنين': 2, 'اثنتين': 2, 'الاثنتين': 2, 'اثني': 2, 'اثنتي': 2,
        'ثنين': 2, 'ثنتين': 2, 'ثني': 2, 'ثنتي': 2,
        'أثنا': 2, 'اثنتان': 2,
        'ثلاث': 3, 'ثلث': 3, 'ثلاثة': 3, 'الثلاثة': 3,
        'اربع': 4, 'اربعة': 4, 'الاربعة': 4, 'أربع': 4, 'أربعة': 4, 'الأربعة': 4,
        'خمس': 5, 'خمسة': 5, 'الخمسة': 5,
        # نيف / بضع ("odd", "a few") are indeterminate approximators, not the value 5:
        # 'نيف وأربعين وثلاثمائة' is "three-hundred-and-forty-odd". Valued 0 so they are
        # consumed (the phrase still parses to its determinate 340) without inventing a 5,
        # and a bare 'سنة نيف' yields no year rather than 5.
        'نيف': 0, 'بضع': 0,
        'ست': 6, 'ستة': 6, 'الستة': 6,
        'سبع': 7, 'سبعة': 7, 'السبعة': 7,
        'ثماني': 8, 'ثمان': 8, 'ثمانية': 8, 'الثمانية': 8,
        'تسع': 9, 'تسعة': 9, 'التسعة': 9
}
ONES_NOR = normalize_dict(ONES)

# Feminine ordinal ones used in ordinal-year headings ('السنة السادسة والأربعون
# وست مئة' = 646). العاشرة = 10th; الحادية / الأولى = 1st; a following 'عشرة' makes a
# teen ('الحادية عشرة' = 11), a following 'والعشرين' a compound ('الحادية والعشرين'
# = 21). The tens/hundreds reuse TEN/HUNDRED.
YEAR_ORDINAL_ONES = {
        'الأولى': 1, 'الاولى': 1, 'الحادية': 1, 'الثانية': 2, 'الثالثة': 3, 'الرابعة': 4,
        'الخامسة': 5, 'السادسة': 6, 'السابعة': 7, 'الثامنة': 8, 'التاسعة': 9, 'العاشرة': 10
}
YEAR_ORDINAL_ONES_NOR = normalize_dict(YEAR_ORDINAL_ONES)

# Named years — years referred to by their event rather than a number. Opt-in
# (the recogniser only matches these when gazetteer mode is on) because a name is
# a weaker signal than a spelled/ digit year. Only well-established post-hijra
# names are listed; pre-hijra ones (عام الفيل، عام الحزن) are omitted since they
# have no positive Hijri year.
NAMED_YEARS = {
        'عام الفتح': 8, 'سنة الفتح': 8,                    # conquest of Mecca
        'عام الوفود': 9, 'سنة الوفود': 9,                  # year of delegations
        'عام حجة الوداع': 10, 'سنة حجة الوداع': 10, 'حجة الوداع': 10,  # farewell pilgrimage
        'عام الرمادة': 18, 'سنة الرمادة': 18,              # famine under Umar
        'عام الجماعة': 41, 'سنة الجماعة': 41               # accession of Muawiya
}
NAMED_YEARS_NOR = normalize_dict(NAMED_YEARS)

TEN = {
        'عشرة': 10, 'العشرة': 10, 'عشري': 10, 'عشر': 10,
        'عشرين': 20, 'عشرون': 20, 'العشرين': 20, 'العشرون': 20,
        'ثلاثين': 30, 'ثلاثون': 30, 'الثلاثين': 30, 'الثلاثون': 30,
        'اربعين': 40, 'اربعون': 40, 'الاربعين': 40, 'الاربعون': 40,
        'أربعين': 40, 'أربعون': 40, 'الأربعين': 40, 'الأربعون': 40,
        'خمسين': 50, 'خمسون': 50, 'الخمسين': 50, 'الخمسون': 50,
        'ستين': 60, 'ستون': 60, 'الستين': 60, 'الستون': 60,
        'سبعين': 70, 'سبعون': 70, 'السبعين': 70, 'السبعون': 70,
        'ثمانين': 80, 'ثمانون': 80, 'الثمانين': 80, 'الثمانون': 80,
        'تسعين': 90, 'تسعون': 90, 'التسعين': 90, 'التسعون': 90
}
TEN_NOR = normalize_dict(TEN)

HUNDRED = {
        'مائة': 100, 'ماية': 100, 'مية': 100, 'مئة': 100, 'ماءة': 100,
        'المائة': 100, 'الماية': 100, 'المية': 100, 'المئة': 100,
        'مائتين': 200, 'مئتين': 200, 'مايتين': 200, 'ميتين': 200, 'المائتين': 200,
        'ثلاثمائة': 300, 'ثلاث مائة': 300, 'ثلثمائة': 300, 'ثلث مائة': 300, 'ثلاثماية': 300, 'ثلاث ماية': 300,
        'ثلثماية': 300, 'ثلث ماية': 300, 'ثلاثمية': 300, 'ثلاث مية': 300, 'ثلثمية': 300, 'ثلث مية': 300,
        'ثلاثمئة': 300, 'ثلاث مئة': 300, 'ثلثمئة': 300, 'ثلث مئة': 300,
        'اربعمائة': 400, 'اربع مائة': 400, 'اربعماية': 400, 'اربع ماية': 400, 'اربعمية': 400, 'اربع مية': 400,
        'اربعمئة': 400, 'اربع مئة': 400,
        'خمسمائة': 500, 'خمس مائة': 500, 'خمسماية': 500, 'خمس ماية': 500, 'خمسمية': 500, 'خمس مية': 500, 'خمسمئة': 500,
        'خمس مئة': 500,
        'ستمائة': 600, 'ست مائة': 600, 'ستماية': 600, 'ست ماية': 600, 'ستمية': 600, 'ست مية': 600, 'ستمئة': 600,
        'ست مئة': 600,
        'سبعمائة': 700, 'سبع مائة': 700, 'سبعماية': 700, 'سبع ماية': 700, 'سبعمية': 700, 'سبع مية': 700, 'سبعمئة': 700,
        'سبع مئة': 700,
        'ثمانمائة': 800, 'ثمان مائة': 800, 'ثمانيمائة': 800, 'ثماني مائة': 800, 'ثمانماية': 800, 'ثمان ماية': 800,
        'ثمانيماية': 800, 'ثماني ماية': 800, 'ثمانمية': 800, 'ثمان مية': 800, 'ثمانيمية': 800, 'ثماني مية': 800,
        'ثمانمئة': 800, 'ثمان مئة': 800, 'ثمانيمئة': 800, 'ثماني مئة': 800,
        'تسعمائة': 900, 'تسع مائة': 900, 'تسعماية': 900, 'تسع ماية': 900, 'تسعمية': 900, 'تسع مية': 900, 'تسعمئة': 900,
        'تسع مئة': 900
}
HUNDRED_NOR = normalize_dict(HUNDRED)

THOUSAND = {'ألف': 1000, 'الف': 1000}
THOUSAND_NOR = normalize_dict(THOUSAND)

# Day-of-month ordinals: 'خامس عشر' = 5 + 10 = 15. ('خميس' is NOT included: it is
# the weekday الخميس (Thursday), not the ordinal "fifth" (خامس) — including it made
# 'الخميس الثلاثين' parse as 5 + 30 = 35.)
DAY_ONES = {
        'واحد': 1, 'حادي': 1, 'ثاني': 2, 'ثالث': 3, 'رابع': 4, 'خامس': 5, 'سادس': 6, 'سابع': 7,
        'ثامن': 8, 'تاسع': 9, 'عاشر': 10
}
DAY_ONES_NOR = normalize_dict(DAY_ONES)

DAY_TEN = {'عشرة': 10, 'عشري': 10, 'عشر': 10, 'عشرين': 20, 'عشرون': 20, 'ثلاثين': 30, 'ثلاثون': 30}
DAY_TEN_NOR = normalize_dict(DAY_TEN)

# Day-within-month formulas (exact-day forms only):
# * "elapsed" — 'لثلاث خلون من رجب' = "three (nights) elapsed of Rajab" => day 3.
#   The count uses cardinal ONES (+ a DAY_TEN), e.g. 'لخمس عشرة خلت' = 15.
# * "start" — 'غرة رمضان' / 'مستهل رمضان' => day 1.
# * "middle" — 'النصف من شعبان' / 'منتصف شعبان' => day 15.
# * "remaining" — 'لسبع بقين من رجب' = "seven (nights) remaining of Rajab" => the
#   day is (month length − count + 1), using the month's length (exact for the
#   year via convertdate, else the standard tabular length).
# * "last" — 'سلخ رمضان' = the last day of the month => its length.
# When the length is genuinely unknown (Dhū al-Ḥijja with no year: 29 or 30), the
# day is set to the sentinel -1 (see ``UNKNOWN_DAY`` in ``recogniser``).
DAY_ELAPSED = ('خلون', 'خلت', 'مضت', 'مضين', 'خلوت', 'خلا')
DAY_FIRST = ('غرة', 'مستهل')
DAY_MID = ('النصف', 'منتصف', 'نصف')
DAY_REMAINING = ('بقين', 'بقيت', 'بقيتا')
DAY_LAST = ('سلخ',)

# 1 = Sunday ... 7 = Saturday. Both 'يوم <day>' (day of) and 'ليلة <day>' (eve
# of) are recognized; classical texts date events to the night preceding a day,
# and 'ليلة الأربعاء' is conventionally associated with that weekday (Wednesday).
WEEKDAYS = {
        'يوم الأحد': 1, 'يوم الاثنين': 2, 'يوم الثلاثاء': 3, 'يوم الأربعاء': 4, 'يوم الخميس': 5, 'يوم الجمعة': 6,
        'يوم السبت': 7,
        'ليلة الأحد': 1, 'ليلة الاثنين': 2, 'ليلة الثلاثاء': 3, 'ليلة الأربعاء': 4, 'ليلة الخميس': 5,
        'ليلة الجمعة': 6, 'ليلة السبت': 7
}
WEEKDAYS_NOR = normalize_dict(WEEKDAYS)

# Bare weekday names (no يوم/ليلة prefix). These are trusted only *inside* a full
# year-anchored date phrase, right before the day/month (الخميس الثلاثين من رمضان),
# never on their own — a lone الجمعة is usually the Friday prayer, not a date. The
# ordinal day words (الحادي، الثاني، ...) differ from these, so they do not collide.
BARE_WEEKDAYS = {
        'الأحد': 1, 'الاثنين': 2, 'الثلاثاء': 3, 'الأربعاء': 4, 'الخميس': 5, 'الجمعة': 6, 'السبت': 7
}
BARE_WEEKDAYS_NOR = normalize_dict(BARE_WEEKDAYS)
# Lookup used by the year-anchored date parser, which may match either form.
WEEKDAYS_ALL_NOR = {**WEEKDAYS_NOR, **BARE_WEEKDAYS_NOR}

# Century ordinals: 'القرن الثامن' = the 8th century. Masculine ordinal forms with
# the article; compound teens through the 15th (the current Hijri century).
CENTURY_ORDINALS = {
        'الأول': 1, 'الثاني': 2, 'الثالث': 3, 'الرابع': 4, 'الخامس': 5, 'السادس': 6, 'السابع': 7,
        'الثامن': 8, 'التاسع': 9, 'العاشر': 10, 'الحادي عشر': 11, 'الثاني عشر': 12, 'الثالث عشر': 13,
        'الرابع عشر': 14, 'الخامس عشر': 15
}
CENTURY_ORDINALS_NOR = normalize_dict(CENTURY_ORDINALS)

# Islamic (Hijri) months, including common honorific variants.
# 'اخر' ("end [of]") is not a month; it is kept with the sentinel value -1 so
# the date regex still consumes it, but it is never emitted as a month value.
MONTHS = {
        'محرم': 1, 'شهر الله المحرم': 1, 'صفر': 2, 'صفر الخير': 2, 'ربيع': 3, 'ربيع الاول': 3, 'ربيع الثاني': 4,
        'ربيع الاخر': 4, 'جمادى الاول': 5, 'جمادى الاولى': 5, 'جمادى الاخرة': 6, 'جمادى الاخر': 6, 'جمادى الثانية': 6,
        'رجب': 7, 'رجب الفرد': 7, 'رجب المبارك': 7, 'شعبان': 8, 'شعبان المكرم': 8, 'رمضان': 9,
        'رمضان المعظم': 9, 'شوال': 10, 'ذي القعدة': 11, 'ذي قعدة': 11, 'ذي الحجة': 12, 'ذي حجة': 12, 'ذو القعدة': 11,
        'ذو قعدة': 11, 'ذو الحجة': 12, 'ذو حجة': 12, 'اخر': -1
}
MONTHS_NOR = normalize_dict(MONTHS)

# Standard (tabular) length of each Hijri month, used only as a fallback for the
# day-in-month sanity check when no year is known (with a year, the exact length
# is taken from ``convertdate``). Odd months have 30 days, even months 29; ذو
# الحجة is 29 or 30 (leap), so its maximum, 30, is used to avoid false warnings.
MONTH_STANDARD_LENGTH = {
        1: 30, 2: 29, 3: 30, 4: 29, 5: 30, 6: 29,
        7: 30, 8: 29, 9: 30, 10: 29, 11: 30, 12: 30,
}

# Words introducing a year statement ("in the year ..."), including the common
# proclitics و/ل/ب/ف on سنة/عام ('لسنة خمس' = "for the year 5", 'بعام'). The
# definite 'السنة' is included but treated as a weak cue in ``parse_year`` (it also
# heads "per year" rates and reign years), so it is trusted only with a digit year
# or a hundreds/thousands component.
SANA = sorted([
    'سنة', 'وسنة', 'لسنة', 'بسنة', 'فسنة', 'السنة',
    'عام', 'وعام', 'لعام', 'بعام', 'فعام',
    'في حدود سنة', 'في حدود',
], key=len, reverse=True)

# Trigger words in the context preceding a date, mapped to the date class:
# B = birth, D = death, P = pilgrimage (hajj), K = knowledge transmission
# (heard/narrated/read/licensed), O = office/appointment. X = unclassified.
DATE_CATEGORIES_DICT = {
       # Birth. 'ولاد'/'ميلاد' are stems that also match ولادته / ميلاده.
       'ولد': 'B', 'مولد': 'B', 'ولاد': 'B', 'ميلاد': 'B',
       # Death. 'وفات' matches the suffixed noun وفاته / وفاتها; 'متوفى' the
       # participle المتوفى (the ال is consumed by DATE_CATEGORY_PATTERN).
       'مات': 'D', 'موت': 'D', 'توفي': 'D', 'وفاة': 'D', 'وفات': 'D', 'متوفى': 'D',
       'حج': 'P',
       'سمع': 'K', 'روى': 'K', 'روا': 'K', 'قرا': 'K', 'قرئ': 'K', 'قراء': 'K', 'اجاز': 'K', 'حدث': 'K',
       'استقر': 'O', 'انفصل': 'O', 'ولي': 'O', 'قاضي': 'O', 'نائب': 'O', 'صاحب': 'O', 'أعمال': 'O'
}
DATE_CATEGORIES_NOR = normalize_dict(DATE_CATEGORIES_DICT)

DATE_CATEGORIES = sorted(set(DATE_CATEGORIES_DICT.values())) + ['X']
