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

TOPONYM_CATEGORIES_REPLACEMENTS = {
        'O': 'R',
        'A': 'X',
        'V': 'X'
}

TOPONYM_CATEGORIES = list(set(TOPONYM_CATEGORIES_DICT.values())) + ['X']
TOPONYM_CATEGORIES_NOR = normalize_dict(TOPONYM_CATEGORIES_DICT)

TOPONYM_LABEL_DICT = {
        'B-TOB': 0,
        'I-TOB': 1,
        'B-TOD': 2,
        'I-TOD': 3,
        'B-TOG': 4,
        'I-TOG': 5,
        'B-TOK': 6,
        'I-TOK': 7,
        'B-TOR': 8,
        'I-TOR': 9,
        'B-TOX': 10,
        'I-TOX': 11,
        'O': 12
}

TOPONYM_LESS_LABEL_DICT = {
        'B-TOB': 0,
        'I-TOB': 1,
        'B-TOD': 2,
        'I-TOD': 3,
        'B-TOR': 4,
        'I-TOR': 5,
        'B-TOX': 6,
        'I-TOX': 7,
        'O': 8
}

AR_TOPONYM_CATEGORIES = '|'.join([denormalize(key) for key in TOPONYM_CATEGORIES_DICT.keys()])
TOPONYM_CATEGORY_PATTERN = compile(r'\s[وف]?(?P<topo_category>' + AR_TOPONYM_CATEGORIES + r')')
