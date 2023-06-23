from re import compile

from openiti.helper.ara import denormalize

from eis1600.helper.ar_normalization import normalize_dict


# TODO Annotate hajja -> Mekka
# TODO Annotate jāwara -> Medina

TOPONYM_CATEGORIES = {
        'ولد': 'B', 'مولد': 'B',
        'مات': 'D', 'موت': 'D', 'توفي': 'D', 'وفاة': 'D',
        'دفن': 'G',
        'سمع': 'K', 'روى': 'K', 'روا': 'K', 'قرا': 'K', 'اجاز': 'K', 'حدث': 'K',
        'استقر': 'O', 'انفصل': 'O', 'ولي': 'O', 'قاضي': 'O', 'نائب': 'O', 'صاحب': 'O', 'أعمال': 'O',
        'حج': 'V',
        'سكن': 'R', 'نزل': 'R', 'نزيل': 'R', 'من اهل': 'R', 'استوطن': 'R', 'كان من': 'R', 'نشأ': 'R'
}
TOPONYM_CATEGORIES_NOR = normalize_dict(TOPONYM_CATEGORIES)

AR_TOPONYM_CATEGORIES = '|'.join([denormalize(key) for key in TOPONYM_CATEGORIES.keys()])
TOPONYM_CATEGORY_PATTERN = compile(r'\s[وف]?(?P<topo_category>' + AR_TOPONYM_CATEGORIES + r')')
