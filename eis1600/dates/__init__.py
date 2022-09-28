import re
from eis1600.ara_re_pattern import WORD
from eis1600.dates.date_dicts import ONES, TEN, HUNDRED, DAY_ONES, DAY_TEN, MONTHS, WEEKDAYS, DATE_CATEGORIES
from eis1600.dates.Date import Date

AR_MONTHS = '|'.join(['(?:' + r'\s'.join(key.split()) + ')' for key in MONTHS.keys()])
AR_ONES = '|'.join(ONES.keys())
AR_TEN = '|'.join(TEN.keys())
AR_HUNDRED = '|'.join(['(?:' + r'\s'.join(key.split()) + ')' for key in HUNDRED.keys()])
AR_ONES_DAY = '|'.join(DAY_ONES.keys())
AR_TEN_DAY = '|'.join(DAY_TEN.keys())
AR_WEEKDAY = '|'.join(['(?:' + r'\s'.join(key.split()) + ')' for key in WEEKDAYS.keys()])
DATE = r'(?P<context>' + WORD + r'{0,10}?' + r'(?:\s(?:في|تقريبا))?' + WORD + r'{0,9}?)' + \
       r'(?:\s(?P<weekday>' + AR_WEEKDAY + r'))?' + \
       r'(?:\s(:?ال)?(?P<day_ones>' + AR_ONES_DAY + r'))?(?:\s(:?و)?(:?ال)?(?P<day_ten>' + AR_TEN_DAY + r'))?' + \
       r'(?:\s(?:(?:من\s)?(?:شهر\s)?)?(?:ال)?(?P<month>' + AR_MONTHS + r')(?:\s(?:من|في)(?:\sشهور)?)?)?' + \
       r'\s(?P<sana>سنة|عام)(?:\s(?P<ones>' + AR_ONES + r'))?' + \
       r'(?:\s[و]?(?P<ten>' + AR_TEN + r'))?' + \
       r'(?:\s[و]?(?P<hundred>' + AR_HUNDRED + r'))?(?=(?:' + WORD + r'|[\s\.,]|$))'

AR_DATE_CATEGORIES = '|'.join(DATE_CATEGORIES.keys())
DATE_CATEGORY_PATTERN = re.compile(r'\s[وف]?(?P<date_category>' + AR_DATE_CATEGORIES + r')[تا]?')
DATE_PATTERN = re.compile(DATE)
MONTH_PATTERN = re.compile(AR_MONTHS)


def tag_dates(text):
    for m in DATE_PATTERN.finditer(text):
        month = None
        year = 0
        day = 0
        weekday = None

        if DATE_CATEGORY_PATTERN.search(m.group('context')):
            last = DATE_CATEGORY_PATTERN.findall(m.group('context'))[-1]
            date_category_str = last
        else:
            date_category_str = False
        date_category = DATE_CATEGORIES.get(date_category_str) if date_category_str else None

        if m.group('weekday'):
            weekday = WEEKDAYS.get(m.group('weekday'))
        if m.group('day_ones'):
            day += DAY_ONES.get(m.group('day_ones'))
        if m.group('day_ten'):
            day += DAY_TEN.get(m.group('day_ten'))
        if m.group('month'):
            month_str = m.group('month')
            month = MONTHS.get(month_str)
        # else:
        #     mm = MONTH_PATTERN.search(m[0])
        #     if mm:
        #         month_str = mm[0]
        #         month = MONTHS.get(month_str)
        if m.group('ones'):
            year += ONES.get(m.group('ones'))
        if m.group('ten'):
            year += TEN.get(m.group('ten'))
        if m.group('hundred'):
            year += HUNDRED.get(m.group('hundred'))

        if day == 0:
            day = None
        if year == 0:
            year = None

        date = Date(year, month, day, weekday, date_category)
        pos = m.start('sana')
        text = text[:pos] + date.get_tag() + text[pos:]

    return text
