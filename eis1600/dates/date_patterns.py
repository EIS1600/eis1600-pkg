from regex import compile

from openiti.helper.ara import denormalize
from eis1600.helper.ar_normalization import normalize_dict, create_opt_pattern
from eis1600.markdown.markdown_patterns import WORD, OPT_PUNCT_PATTERN

ONES = {
        'واحد': 1, 'الواحد': 1, 'احدى': 1, 'احد': 1,
        'اثنين': 2, 'الاثنين': 2, 'اثنتين': 2, 'الاثنتين': 2, 'اثني': 2, 'اثنتي': 2,
        'ثنين': 2, 'ثنتين': 2, 'ثني': 2, 'ثنتي': 2,
        'أثنا': 2, 'اثنتان': 2,
        'ثلاث': 3, 'ثلث': 3, 'ثلاثة': 3, 'الثلاثة': 3,
        'اربع': 4, 'اربعة': 4, 'الاربعة': 4, 'أربع': 4, 'أربعة': 4, 'الأربعة': 4,
        'خمس': 5, 'خمسة': 5, 'الخمسة': 5, 'نيف': 5, 'بضع': 5,
        'ست': 6, 'ستة': 6, 'الستة': 6,
        'سبع': 7, 'سبعة': 7, 'السبعة': 7,
        'ثماني': 8, 'ثمان': 8, 'ثمانية': 8, 'الثمانية': 8,
        'تسع': 9, 'تسعة': 9, 'التسعة': 9
}
ONES_NOR = normalize_dict(ONES)
ONES_HINDI = {
        '٠': 0, '١': 1, '٢': 2, '٣': 3, '٤': 4, '٥': 5, '٦': 6, '٧': 7, '٨': 8, '٩': 9
}
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
THOUSAND = normalize_dict({'ألف': 1000, 'الف': 1000})
THOUSAND_NOR = normalize_dict(THOUSAND)

DAY_ONES = {
        'واحد': 1, 'حادي': 1, 'ثاني': 2, 'ثالث': 3, 'رابع': 4, 'خامس': 5, 'خميس': 5, 'سادس': 6, 'سابع': 7,
        'ثامن': 8, 'تاسع': 9, 'عاشر': 10
}
DAY_ONES_NOR = normalize_dict(DAY_ONES)
DAY_TEN = {'عشرة': 10, 'عشري': 10, 'عشر': 10, 'عشرين': 20, 'عشرون': 20, 'ثلاثين': 30, 'ثلاثون': 30}
DAY_TEN_NOR = normalize_dict(DAY_TEN)
WEEKDAYS = {
        'يوم الأحد': 1, 'يوم الاثنين': 2, 'يوم الثلاثاء': 3, 'يوم الأربعاء': 4, 'يمو الخميس': 5, 'يوم الجمعة': 6,
        'يوم السبت': 7
}
WEEKDAYS_NOR = normalize_dict(WEEKDAYS)

MONTHS = {
        'محرم': 1, 'شهر الله المحرم': 1, 'صفر': 2, 'صفر الخير': 2, 'ربيع': 3, 'ربيع الاول': 3, 'ربيع الثاني': 4,
        'ربيع الاخر': 4, 'جمادى الاول': 5, 'جمادى الاولى': 5, 'جمادى الاخرة': 6, 'جمادى الاخر': 6, 'جمادى الثانية': 6,
        'رجب': 7, 'رجب الفرد': 7, 'رجب المبارك': 7, 'شعبان': 8, 'شعبان المكرم': 8, 'رمضان': 9,
        'رمضان المعظم': 9, 'شوال': 10, 'ذي القعدة': 11, 'ذي قعدة': 11, 'ذي الحجة': 12, 'ذي حجة': 12, 'ذو القعدة': 11,
        'ذو قعدة': 11, 'ذو الحجة': 12, 'ذو حجة': 12, 'اخر': -1
}
MONTHS_NOR = normalize_dict(MONTHS)
SANA = sorted(['سنة', 'وسنة', 'عام', 'في حدود سنة', 'في حدود'], key=len, reverse=True)

AR_MONTHS = create_opt_pattern(MONTHS.keys())
AR_ONES = create_opt_pattern(ONES.keys())
AR_TEN = create_opt_pattern(TEN.keys())
AR_HUNDRED = create_opt_pattern(HUNDRED.keys())
AR_THOUSAND = create_opt_pattern(THOUSAND.keys())
AR_ONES_DAY = create_opt_pattern(DAY_ONES.keys())
AR_TEN_DAY = create_opt_pattern(DAY_TEN.keys())
AR_WEEKDAY = create_opt_pattern(WEEKDAYS.keys())
AR_SANA = '|'.join([denormalize(s) for s in SANA])
MONTH_IN_CONTEXT = r'\s(?:(?:من\s)?(?:شهر\s)?)?(?P<month>(?:ال)?(?:' + AR_MONTHS + r'))(?:\s(?:من|ف[يى])(?:\sشهور)?)?'

DATE1 = r'(?P<context>' + WORD + r'{0,10}?' + r'(?:\s(?:ف[يى]|تقريبا))?' + WORD + r'{0,9}?)' + \
       r'(?:\s(?P<weekday>' + AR_WEEKDAY + r'))?' + \
       r'(?:\s(?:ال)?(?P<day_ones>' + AR_ONES_DAY + r'))?(?:\s(?:و)?(?:ال)?(?P<day_ten>' + AR_TEN_DAY + r'))?' + \
       r'(?:' + MONTH_IN_CONTEXT + r')?' +\
       r'(?P<year>' + \
              r'\s(?P<sana>' + AR_SANA + ')' + \
              r'(?:\s(?P<punct1>' + OPT_PUNCT_PATTERN + '))??' + \
              r'(?:\s(?P<digits_str>(?P<digits>[1-9١٢٣٤٥٦٧٨٩][\d٠١٢٣٤٥٦٧٨٩]{0,3})(?:\s(?:[هم]|الهجري[هة])|ه)?))?' + \
              r'(?:\s(?P<punct2>' + OPT_PUNCT_PATTERN + '))??' + \
              r'(?:\s(?P<ones>' + AR_ONES + r'))?' + \
              r'(?:\s(?P<opt_ones>[إأٱآا]و\s+(?:' + AR_ONES + r')))?' + \
              r'(?:\s(?P<punct3>' + OPT_PUNCT_PATTERN + '))??' + \
              r'(?:\s(?P<note>\(\s+\d+\s+\)))?' + \
              r'(?:\s[و]?(?P<ten>' + AR_TEN + r'))?' + \
              r'(?:\s(?P<punct4>' + OPT_PUNCT_PATTERN + '))??' + \
              r'(?:\s[و]?(?P<hundred>' + AR_HUNDRED + \
              r'))?' + r'(?:\s(?P<punct5>' + OPT_PUNCT_PATTERN + '))??' + \
              r'(?:\s[و]?(?P<thousand>' + AR_THOUSAND + r'))?' + \
              r'(?:\s(?P<punct6>' + OPT_PUNCT_PATTERN + '))??' + \
       r')' + \
        r'(?=(?:' + WORD + r'|[\s.,]|$))'

# only for reversed cases such as سنة مائتين وست وأ ربعين
DATE2 = r'(?P<context>' + WORD + r'{0,10}?' + r'(?:\s(?:ف[يى]|تقريبا))?' + WORD + r'{0,9}?)' + \
       r'(?:\s(?P<weekday>' + AR_WEEKDAY + r'))?' + \
       r'(?:\s(?:ال)?(?P<day_ones>' + AR_ONES_DAY + r'))?(?:\s(?:و)?(?:ال)?(?P<day_ten>' + AR_TEN_DAY + r'))?' + \
       r'(?:' + MONTH_IN_CONTEXT + r')?' +\
       r'(?P<year>' + \
              r'\s(?P<sana>' + AR_SANA + ')' + \
              r'(?:\s(?P<punct1>' + OPT_PUNCT_PATTERN + '))??' + \
              r'(?:\s(?P<digits_str>(?P<digits>[1-9١٢٣٤٥٦٧٨٩][\d٠١٢٣٤٥٦٧٨٩]{0,3})(?:\s(?:[هم]|الهجري[هة])|ه)?))?' + \
              r'(?:\s(?P<punct2>' + OPT_PUNCT_PATTERN + '))??' + \
              r'\s(?P<hundred>' + AR_HUNDRED + r')' + \
              r'(?:\s(?P<punct3>' + OPT_PUNCT_PATTERN + '))??' + \
              r'\s[و]?(?P<ones>' + AR_ONES + r')' + \
              r'(?:\s(?P<opt_ones>[إأٱآا]و\s+(?:' + AR_ONES + r')))?' + \
              r'(?:\s(?P<punct4>' + OPT_PUNCT_PATTERN + '))??' + \
              r'\s[و]?(?P<ten>' + AR_TEN + r')' + \
              r'(?:\s(?P<punct5>' + OPT_PUNCT_PATTERN + '))??' + \
              r'(?:\s[و]?(?P<thousand>' + AR_THOUSAND + r'))?' + \
              r'(?:\s(?P<punct6>' + OPT_PUNCT_PATTERN + '))??' + \
       r')' + \
        r'(?=(?:' + WORD + r'|[\s.,]|$))'

DATE_PATTERN = compile(fr'{DATE2}|{DATE1}')

MONTH_PATTERN = compile(AR_MONTHS)
MONTH_IN_CONTEXT_PATTERN = compile(MONTH_IN_CONTEXT)
SANA_PATTERN = compile(r'\s' + r'|'.join([denormalize(s) for s in SANA]))

DATE_CATEGORIES_DICT = {
       'ولد': 'B', 'مولد': 'B',
       'مات': 'D', 'موت': 'D', 'توفي': 'D', 'وفاة': 'D',
       'حج': 'P',
       'سمع': 'K', 'روى': 'K', 'روا': 'K', 'قرا': 'K', 'اجاز': 'K', 'حدث': 'K',
       'استقر': 'O', 'انفصل': 'O', 'ولي': 'O', 'قاضي': 'O', 'نائب': 'O', 'صاحب': 'O', 'أعمال': 'O'
}
DATE_CATEGORIES_NOR = normalize_dict(DATE_CATEGORIES_DICT)

AR_DATE_CATEGORIES = '|'.join([denormalize(key) for key in DATE_CATEGORIES_DICT.keys()])
DATE_CATEGORY_PATTERN = compile(r'\s[وف]?(?P<date_category>' + AR_DATE_CATEGORIES + r')')

DATE_CATEGORIES = list(set(DATE_CATEGORIES_DICT.values())) + ["X"]

DATE_LABEL_DICT = {
       'B-YYB': 0,
       'I-YYB': 1,
       'B-YYD': 2,
       'I-YYD': 3,
       'B-YYK': 4,
       'I-YYK': 5,
       'B-YYO': 6,
       'I-YYO': 7,
       'B-YYP': 8,
       'I-YYP': 9,
       'B-YYX': 10,
       'I-YYX': 11,
       'O': 12
}

DATE_CATEGORIES_REPLACEMENTS = {
        'M': 'X',
        'R': 'X'
}
