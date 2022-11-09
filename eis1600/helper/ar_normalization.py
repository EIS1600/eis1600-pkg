from openiti.helper.ara import normalize_ara_heavy


def normalize_set(o_set):
    n_set = {}

    for key, val in o_set.items():
        n_set[normalize_ara_heavy(key)] = val

    return n_set