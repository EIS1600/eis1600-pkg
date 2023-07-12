from re import compile

from openiti.helper.ara import denormalize

from eis1600.helper.ar_normalization import normalize_dict


# TODO Annotate hajja -> Mekka
# TODO Annotate jāwara -> Medina

TOPONYM_CATEGORIES_DICT = {
        'ولد': 'B', 'مولد': 'B',
        'مات': 'D', 'موت': 'D', 'توفي': 'D', 'وفاة': 'D',
        'دفن': 'G',
        'سمع': 'K', 'روى': 'K', 'روا': 'K', 'قرا': 'K', 'اجاز': 'K', 'حدث': 'K',
        'استقر': 'R', 'انفصل': 'R', 'ولي': 'R', 'قاضي': 'R', 'نائب': 'R', 'صاحب': 'R', 'أعمال': 'R',
        # 'حج': 'V',
        'سكن': 'R', 'نزل': 'R', 'نزيل': 'R', 'من اهل': 'R', 'استوطن': 'R', 'كان من': 'R', 'نشأ': 'R'
}
TOPONYM_CATEGORIES = list(set(TOPONYM_CATEGORIES_DICT.values())) + ['X']
TOPONYM_CATEGORIES_NOR = normalize_dict(TOPONYM_CATEGORIES_DICT)

AR_TOPONYM_CATEGORIES = '|'.join([denormalize(key) for key in TOPONYM_CATEGORIES_DICT.keys()])
TOPONYM_CATEGORY_PATTERN = compile(r'\s[وف]?(?P<topo_category>' + AR_TOPONYM_CATEGORIES + r')')
