from typing import List

from openiti.helper.ara import normalize_ara_heavy

ALIF_VARIATIONS = ['ا', 'أ', 'ٱ', 'آ', 'إ']

def normalize_dict(o_set: dict) -> dict:
    n_set = {}

    for key, val in o_set.items():
        n_set[normalize_ara_heavy(key)] = val

    return n_set


def denormalize_list(elem: str) -> List[str]:
    # TODO evaluate if this is enough
    n_list = []
    tmp = [elem]
    if elem.startswith(('أ', 'ٱ', 'آ', 'إ')):
        # alifs
        tmp.extend([alif_variation + elem[1:] for alif_variation in ALIF_VARIATIONS])
    if elem.startswith(('الأ', 'الٱ', 'الآ', 'الإ')):
        #  al + alifs
        tmp.extend(['ال' + alif_variation + elem[3:] for alif_variation in ALIF_VARIATIONS])
    if elem.endswith(('يء', 'ىء', 'ؤ', 'ئ')):
        # hamzas
        tmp.extend([var[:-1] + 'ء' for var in tmp])
    if elem.endswith('ى'):
        # alif maqsura
        tmp.extend([var[:-1] + 'ي' for var in tmp])
    if elem.endswith('ي'):
        # alif maqsura
        tmp.extend([var[:-1] + 'ى' for var in tmp])
    if elem.endswith('ة'):
        # ta marbuta
        tmp.extend([var[:-1] + 'ه' for var in tmp])

    n_list.extend(tmp)

    return n_list
