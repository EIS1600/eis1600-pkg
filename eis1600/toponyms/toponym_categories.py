from re import compile

from openiti.helper.ara import denormalize

from eis1600.helper.ar_normalization import normalize_dict


TOPONYM_CATEGORIES = {
        'ولد': 'B', 'مولد': 'B',
        'مات': 'D', 'موت': 'D', 'توفي': 'D', 'وفاة': 'D',
        'حج': 'P',
        'سمع': 'K', 'قرا': 'K', 'اجاز': 'K',
        'استقر': 'O', 'انفصل': 'O', 'ولي': 'O', 'قاضي': 'O',
        'لقي': 'M',
        'سكن': 'L', 'نزل': 'L', 'نريل': 'L', 'من اهل': 'L', 'استوطن': 'L'
}
TOPONYM_CATEGORIES_NOR = normalize_dict(TOPONYM_CATEGORIES)

AR_TOPONYM_CATEGORIES = '|'.join([denormalize(key) for key in TOPONYM_CATEGORIES.keys()])
TOPONYM_CATEGORY_PATTERN = compile(r'\s[وف]?(?P<topo_category>' + AR_TOPONYM_CATEGORIES + r')')
