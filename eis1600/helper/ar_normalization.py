from typing import List

from openiti.helper.ara import normalize_ara_heavy


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
        tmp.append('ا' + elem[1:])
    if elem.endswith(('يء', 'ىء', 'ؤ', 'ئ')):
        # hamzas
        tmp.append([var[:-1] + 'ء' for var in tmp])
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
