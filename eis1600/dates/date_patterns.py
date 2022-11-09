import re

from openiti.helper.ara import denormalize

from eis1600.helper.ar_normalization import normalize_set
from eis1600.markdown.re_patterns import AR_STR, WORD


ONES = {'واحد': 1, 'احدى': 1, 'احد': 1, 'اثنين': 2, 'اثنتين': 2, 'اثنتي': 2, 'ثلاث': 3, 'اربع': 4, 'خمس': 5, 'ست': 6,
        'سبع': 7, 'ثماني': 8, 'ثمان': 8, 'تسع': 9}
ONES_NOR = normalize_set(ONES)
TEN = {'عشرة': 10, 'عشري': 10, 'عشر': 10, 'عشرين': 20, 'ثلاثين': 30, 'اربعين': 40, 'خمسين': 50, 'ستين': 60, 'سبعين': 70,
       'ثمانين': 80, 'تسعين': 90}
TEN_NOR = normalize_set(TEN)
HUNDRED = {'مائة': 100, 'ماية': 100, 'مية': 100, 'مئة': 100, 'مائتين': 200, 'مايتين': 200, 'ميتين': 200,
           'ثلاثمائة': 300, 'ثلاث مائة': 300, 'اربعمائة': 400, 'اربع مائة': 400, 'خمسمائة': 500, 'خمس مائة': 500,
           'ستمائة': 600, 'ست مائة': 600, 'سبعمائة': 700, 'سبع مائة': 700, 'ثمانمائة': 800, 'ثمان مائة': 800,
           'ثمانيمائة': 800, 'ثماني مائة': 800, 'تسعمائة': 900, 'تسع مائة': 900, 'ثلاثماية': 300, 'ثلاث ماية': 300,
           'اربعماية': 400, 'اربع ماية': 400, 'خمسماية': 500, 'خمس ماية': 500, 'ستماية': 600, 'ست ماية': 600,
           'سبعماية': 700, 'سبع ماية': 700, 'ثمانماية': 800, 'ثمان ماية': 800, 'ثمانيماية': 800, 'ثماني ماية': 800,
           'تسعماية': 900, 'تسع ماية': 900, 'ثلاثمية': 300, 'ثلاث مية': 300, 'اربعمية': 400, 'اربع مية': 400,
           'خمسمية': 500, 'خمس مية': 500, 'ستمية': 600, 'ست مية': 600, 'سبعمية': 700, 'سبع مية': 700, 'ثمانمية': 800,
           'ثمان مية': 800, 'ثمانيمية': 800, 'ثماني مية': 800, 'تسعمية': 900, 'تسع مية': 900, 'ثلاثمئة': 300,
           'ثلاث مئة': 300, 'اربعمئة': 400, 'اربع مئة': 400, 'خمسمئة': 500, 'خمس مئة': 500, 'ستمئة': 600, 'ست مئة': 600,
           'سبعمئة': 700, 'سبع مئة': 700, 'ثمانمئة': 800, 'ثمان مئة': 800, 'ثمانيمئة': 800, 'ثماني مئة': 800,
           'تسعمئة': 900, 'تسع مئة': 900}
HUNDRED_NOR = normalize_set(HUNDRED)

DAY_ONES = {'واحد': 1, 'حادي': 1, 'ثاني': 2, 'ثالث': 3, 'رابع': 4, 'خامس': 5, 'خميس': 5, 'سادس': 6, 'سابع': 7,
            'ثامن': 8, 'تاسع': 9, 'عاشر': 10}
DAY_ONES_NOR = normalize_set(DAY_ONES)
DAY_TEN = {'عشرة': 10, 'عشري': 10, 'عشر': 10, 'عشرين': 20, 'عشرون': 20, 'ثلاثين': 30, 'ثلاثون': 30}
DAY_TEN_NOR = normalize_set(DAY_TEN)
WEEKDAYS = {'يوم الأحد': 1, 'يوم الاثنين': 2, 'يوم الثلاثاء': 3, 'يوم الأربعاء': 4, 'يمو الخميس': 5, 'يوم الجمعة': 6,
            'يوم السبت': 7}
WEEKDAYS_NOR = normalize_set(WEEKDAYS)

MONTHS = {'محرم': 1, 'شهر الله المحرم': 1, 'صفر': 2, 'صفر الخير': 2, 'ربيع': 3, 'ربيع الاول': 3, 'ربيع الثاني': 4,
          'ربيع الاخر': 4, 'جمادى الاول': 5, 'جمادى الاولى': 5, 'جمادى الاخرة': 6, 'جمادى الاخر': 6, 'جمادى الثانية': 6,
          'رجب': 7, 'رجب الفرد': 7, 'رجب المبارك': 7, 'شعبان': 8, 'شعبان المكرم': 8, 'رمضان': 9,
          'رمضان المعظم': 9, 'شوال': 10, 'ذي القعدة': 11, 'ذي قعدة': 11, 'ذي الحجة': 12, 'ذي حجة': 12, 'ذو القعدة': 11,
          'ذو قعدة': 11, 'ذو الحجة': 12, 'ذو حجة': 12, 'اخر': -1}
MONTHS_NOR = normalize_set(MONTHS)

AR_MONTHS = '|'.join(['(?:' + r'\s'.join(denormalize(key.split())) + ')' for key in MONTHS.keys()])
AR_ONES = '|'.join(denormalize(ONES.keys()))
AR_TEN = '|'.join(denormalize(TEN.keys()))
AR_HUNDRED = '|'.join(['(?:' + r'\s'.join(denormalize(key.split())) + ')' for key in HUNDRED.keys()])
AR_ONES_DAY = '|'.join(denormalize(DAY_ONES.keys()))
AR_TEN_DAY = '|'.join(denormalize(DAY_TEN.keys()))
AR_WEEKDAY = '|'.join(['(?:' + r'\s'.join(key.split()) + ')' for key in WEEKDAYS.keys()])
DATE = r'(?P<context>' + WORD + r'{0,10}?' + r'(?:\s(?:ف[يى]|تقريبا))?' + WORD + r'{0,9}?)' + \
       r'(?:\s(?P<weekday>' + AR_WEEKDAY + r'))?' + \
       r'(?:\s(:?ال)?(?P<day_ones>' + AR_ONES_DAY + r'))?(?:\s(:?و)?(:?ال)?(?P<day_ten>' + AR_TEN_DAY + r'))?' + \
       r'(?:\s(?:(?:من\s)?(?:شهر\s)?)?(?:ال)?(?P<month>' + AR_MONTHS + r')(?:\s(?:من|ف[يى])(?:\sشهور)?)?)?' + \
       r'\s(?P<sana>سن[ةه]|عام)(?:\s(?P<ones>' + AR_ONES + r'))?' + \
       r'(?:\s[و]?(?P<ten>' + AR_TEN + r'))?' + \
       r'(?:\s[و]?(?P<hundred>' + AR_HUNDRED + r'))?(?=(?:' + WORD + r'|[\s\.,]|$))'

DATE_PATTERN = re.compile(DATE)
MONTH_PATTERN = re.compile(AR_MONTHS)

DATE_CATEGORIES = {'ولد': 'B', 'مولده': 'B', 'مات': 'D', 'موته': 'D', 'توفي': 'D', 'وفاته': 'D', 'حخ': 'H',
                   'سمع': 'K', 'قرا': 'K', 'استقر': 'P', 'اجاز': 'K', 'انفصل': 'P', 'لقي': 'M'}

AR_DATE_CATEGORIES = '|'.join(denormalize(DATE_CATEGORIES.keys()))
DATE_CATEGORY_PATTERN = re.compile(r'\s[وف]?(?P<date_category>' + AR_DATE_CATEGORIES + r')[تا]?')
