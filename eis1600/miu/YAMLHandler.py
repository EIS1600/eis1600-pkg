from __future__ import annotations

from typing import Any, Dict, Optional, Type

from eis1600.markdown.re_patterns import AR_STR_AND_TAGS, MIU_HEADER
from eis1600.miu.HeadingTracker import HeadingTracker


class YAMLHandler:
    """A class to take care of the MIU YAML Headers

    :param Dict yml: the YAML header as a dict, optional.
    :ivar Literal['NOT REVIEWED', 'REVIEWED'] reviewed: Indicates if the file has manually been reviewed, defaults to
    'NOT REVIEWED'.
    :ivar str reviewer: Initials of the reviewer if the file was already manually reviewed, defaults to None.
    :ivar HeadingTracker headings: HeadingTracker returned by the get_curr_state method of the HeaderTracker.
    :iver List[str] dates: List of dates contained in headings and text
    """

    @staticmethod
    def __parse_yml_val(val: str) -> Any:
        if val.startswith('"\''):
            return val.strip('"\'')
        elif val.isdigit():
            return int(val)
        elif val == 'True':
            return True
        elif val == 'False':
            return False
        elif val == 'None':
            return None
        elif val.startswith('["'):
            val_list = val.strip('[]')
            val_list = val_list.replace('"', '')
            return val_list.split(',')
        else:
            return val

    @staticmethod
    def __parse_yml(yml_str: str) -> Dict:
        yml = {}
        level = []
        dict_elem = {}
        # print(yml_str)
        for line in yml_str.splitlines():
            if not line.startswith('#'):
                intend = (len(line) - len(line.lstrip())) / 4
                key_val = line.split(':')
                key = key_val[0].strip(' -')
                val = ':'.join(key_val[1:]).strip()

                if intend < len(level):
                    yml[level[0]] = dict_elem
                    dict_elem = {}
                    level.pop()
                    yml[key] = YAMLHandler.__parse_yml_val(val)
                elif intend and intend == len(level):
                    dict_elem[key] = YAMLHandler.__parse_yml_val(val)
                elif val == '':
                    dict_elem = {}
                    level.append(key)
                else:
                    yml[key] = YAMLHandler.__parse_yml_val(val)

        if len(level):
            yml[level[0]] = dict_elem

        return yml

    def __init__(self, yml: Optional[Dict] = None) -> None:
        self.reviewed = 'NOT REVIEWED'
        self.reviewer = None
        self.headings = None
        self.dates = None

        if yml:
            for key, val in yml.items():
                if key == 'headings':
                    val = HeadingTracker(val)
                self.__setattr__(key, val)

    @classmethod
    def from_yml_str(cls, yml_str: str) -> Type[YAMLHandler]:
        """Return instance with attr set from the yml_str."""
        return cls(YAMLHandler.__parse_yml(yml_str))

    def set_headings(self, headings: Type[HeadingTracker]):
        self.headings = headings

    def get_yamlfied(self) -> str:
        yaml_str = MIU_HEADER + 'Begin#\n\n'
        for key, val in vars(self).items():
            if key == 'dates' and val is not None:
                yaml_str += key + '    : ['
                for date in val:
                    yaml_str += '"' + date + '",'
                yaml_str = yaml_str[:-1]
                yaml_str += ']\n'
            else:
                yaml_str += key + '    : ' + str(val) + '\n'
        yaml_str += '\n' + MIU_HEADER + 'End#\n\n'

        return yaml_str

    def is_reviewed(self) -> bool:
        return self.reviewed == 'REVIEWED'

    def add_date(self, date_tag: str):
        if self.dates:
            self.dates.append(date_tag)
        else:
            self.dates = [date_tag]

    def __setitem__(self, key: str, value: Any) -> None:
        super().__setattr__(key, value)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __str__(self) -> str:
        return self.get_yamlfied()
