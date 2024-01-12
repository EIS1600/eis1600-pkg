from typing import Dict


def dict_to_yaml(d: Dict, level: int) -> str:
    intend = '    ' * level
    yaml = ''
    for key2, val2 in d.items():
        if isinstance(val2, dict):
            val_str = dict_to_yaml(val2, level + 1)
            yaml += intend + f'- {key2} :\n{val_str}\n'
        else:
            yaml += intend + f'- {key2} : {str(val2)}\n'

    return yaml[:-1]
