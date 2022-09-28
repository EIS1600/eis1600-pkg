ONES = {'واحد': 1, 'إحدى': 1, 'اثنتين': 2, 'اثنتي': 2, 'ثلاث': 3, 'اربع': 4, 'خمس': 5, 'ست': 6, 'سبع': 7, 'ثماني': 8,
        'ثمان': 8, 'تسع': 9}
TEN = {'عشرة': 10, 'عشري': 10, 'عشر': 10, 'عشرين': 20, 'ثلاثين': 30, 'أربعين': 40, 'خمسين': 50, 'ستين': 60, 'سبعين': 70,
       'ثمانين': 80, 'ثماني': 8, 'تسعين': 90}
HUNDRED = {'مائة': 100, 'ماية': 100, 'مية': 100, 'مئة': 100, 'مائتين': 200, 'مايتين': 200, 'ميتين': 200,
           'ثلاثمائة': 300, 'ثلاث مائة': 300, 'أربعمائة': 400, 'أربع مائة': 400, 'خمسمائة': 500, 'خمس مائة': 500,
           'ستمائة': 600, 'ست مائة': 600, 'سبعمائة': 700, 'سبع مائة': 700, 'ثمانمائة': 800, 'ثمان مائة': 800,
           'ثمانيمائة': 800, 'ثماني مائة': 800, 'تسعمائة': 900, 'تسع مائة': 900, 'ثلاثماية': 300, 'ثلاث ماية': 300,
           'أربعماية': 400, 'أربع ماية': 400, 'خمسماية': 500, 'خمس ماية': 500, 'ستماية': 600, 'ست ماية': 600,
           'سبعماية': 700, 'سبع ماية': 700, 'ثمانماية': 800, 'ثمان ماية': 800, 'ثمانيماية': 800, 'ثماني ماية': 800,
           'تسعماية': 900, 'تسع ماية': 900, 'ثلاثمية': 300, 'ثلاث مية': 300, 'أربعمية': 400, 'أربع مية': 400,
           'خمسمية': 500, 'خمس مية': 500, 'ستمية': 600, 'ست مية': 600, 'سبعمية': 700, 'سبع مية': 700, 'ثمانمية': 800,
           'ثمان مية': 800, 'ثمانيمية': 800, 'ثماني مية': 800, 'تسعمية': 900, 'تسع مية': 900, 'ثلاثمئة': 300,
           'ثلاث مئة': 300, 'أربعمئة': 400, 'أربع مئة': 400, 'خمسمئة': 500, 'خمس مئة': 500, 'ستمئة': 600,
           'ست مئة': 600, 'سبعمئة': 700, 'سبع مئة': 700, 'ثمانمئة': 800, 'ثمان مئة': 800, 'ثمانيمئة': 800,
           'ثماني مئة': 800, 'تسعمئة': 900, 'تسع مئة': 900}

DAY_ONES = {'واحد': 1, 'حادي': 1, 'ثاني': 2, 'ثالث': 3, 'رابع': 4, 'خامس': 5, 'خميس': 5, 'سادس': 6, 'سابع': 7,
            'ثامن': 8, 'تاسع': 9, 'عاشر': 10}
DAY_TEN = {'عشرة': 10, 'عشري': 10, 'عشر': 10, 'عشرين': 20, 'عشرون': 20, 'ثلاثين': 30, 'ثلاثون': 30}

WEEKDAYS = {'يوم الأحد': 1, 'يوم الاثنين': 2, 'يوم الثلاثاء': 3, 'يوم الأربعاء': 4, 'يمو الخميس': 5, 'يوم الجمعة': 6,
            'يوم السبت': 7}
MONTHS = {'محرم': 1, 'شهر الله المحرم': 1, 'صفر': 2, 'صفر الخير': 2, 'ربيع': 3, 'ربيع الأول': 3, 'ربيع الثاني': 4,
          'ربيع الآخر': 4, 'جمادى الأول': 5, 'جمادى الأولى': 5, 'جمادى الآخرة': 6, 'جمادى الآخر': 6, 'جمادى الثانية': 6,
          'رجب': 7, 'رجب الفرد': 7, 'رجب المبارك': 7, 'شعبان': 8, 'شعبان المكرم': 8, 'رمضان': 9,
          'رمضان المعظم': 9, 'شوال': 10, 'ذي القعدة': 11, 'ذي قعدة': 11, 'ذو القعدة': 11,
          'ذو قعدة': 11, 'ذي الحجة': 12, 'ذي حجة': 12, 'ذو الحجة': 12, 'ذو حجة': 12, 'أواخر': 'End of', 'آخر': 'End of'}

DATE_CATEGORIES = {'ولد': 'B', 'مولده': 'B', 'مات': 'D', 'موته': 'D', 'توفي': 'D', 'حخ': 'H', 'سمع': 'samia',
                   'قرأ': 'qaraa', 'إستقر': 'istaqara', 'أجاز': 'ajaza', 'إنفصل': 'infasala', 'لقي': 'laqiya'}


def build_hundreds_dict():
    hundred = ['مائة', 'ماية', 'مية', 'مئة']
    one = {'ثلاث': 3, 'أربع': 4, 'خمس': 5, 'ست': 6, 'سبع': 7, 'ثمان': 8, 'ثماني': 8, 'تسع': 9}
    final = {}

    for h in hundred:
        for k, value in one.items():
            key = k + h
            final[key] = value * 100
            key = k + ' ' + h
            final[key] = value * 100
