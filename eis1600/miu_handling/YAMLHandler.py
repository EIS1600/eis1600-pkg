from typing import Iterable

from eis1600.miu_handling.re_patterns import MIU_HEADER


class YAMLHandler:
    """A class to take care of the MIU YAML Headers

    :param bool reviewed: Indicating if this record has been manually reviewed. If True, the record will not be
    changed by automated analysis.
    """

    def __init__(self) -> None:
        self.reviewed = False

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __str__(self) -> str:
        return str(self.__dict__)

    def set_headings(self, headings: dict):
        for key, val in headings.items():
            self.__setattr__(key, val)

    def get_yamlfied(self) -> str:
        yaml_str = MIU_HEADER + '\n\n'
        for key, val in vars(self).items():
            yaml_str += key + '    : ' + str(val) + '\n'
        yaml_str += '\n' + MIU_HEADER + '\n\n'

        return yaml_str
