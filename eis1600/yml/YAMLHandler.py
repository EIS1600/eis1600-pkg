from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, Optional

from ast import literal_eval

from eis1600.markdown.markdown_patterns import MIU_HEADER
from eis1600.miu.HeadingTracker import HeadingTracker
from eis1600.yml.yml_methods import dict_to_yaml


class YAMLHandler:
    """A class to take care of the MIU YAML Headers

    :param Dict yml: the YAML header as a dict, optional.
    :ivar Literal['NOT REVIEWED', 'REVIEWED'] reviewed: Indicates if the file has manually been reviewed, defaults to
    'NOT REVIEWED'.
    :ivar str reviewer: Initials of the reviewer if the file was already manually reviewed, defaults to None.
    :ivar HeadingTracker headings: HeadingTracker returned by the get_curr_state method of the HeaderTracker.
    :ivar List[str] dates_headings: List of dates tags contained in headings.
    :ivar List[int] dates: List of dates contained in the text.
    :ivar Dict onomstics: contains onomastic elements by category.
    :ivar str category: String categorising the type of the entry, bio, chr, dict, etc.
    """
    # Only attributes named in the following list are allowed to be added to the YAMLHeader - add any new attribute
    # to that list
    __attr_from_annotation = ['dates', 'min_date', 'max_date', 'ages', 'onomastics', 'ambiguous_toponyms', 'persons',
                              'toponyms', 'settlements', 'provinces', 'edges_settlements', 'edges_provinces',
                              'books', 'miscs']

    @staticmethod
    def __parse_yml_val(val: str) -> Any:
        if val.isdigit():
            return int(val)
        if len(val.split('.')) == 2 and val.split('.')[0].isdigit() and val.split('.')[1].isdigit():
            return float(val)
        elif val == 'True':
            return True
        elif val == 'False':
            return False
        elif val == 'None' or val == '':
            return None
        elif val.startswith(('\'', '"')):
            return val.strip('\'"')
        elif val.startswith('['):
            # List - no comma allowed in strings, it is used as the separator!
            raw_val_list = val[1:-1]  # strip '[]' but without stripping multiple in case we have nested lists
            if raw_val_list.startswith('(') and raw_val_list.endswith(')'):
                # List of tuples
                val_list = raw_val_list.strip('()').split('), (')
                values = []
                for v in val_list:
                    t = v.split(', ')
                    values.append((YAMLHandler.__parse_yml_val(t[0]), YAMLHandler.__parse_yml_val(t[1])))
            elif raw_val_list.startswith('[') or raw_val_list.startswith('{'):
                # Nested lists
                values = literal_eval(val)
            elif raw_val_list == '':
                return None
            else:
                # List of other values
                val_list = raw_val_list.split(', ')
                values = [YAMLHandler.__parse_yml_val(v) for v in val_list]
            return values
        else:
            return val

    @staticmethod
    def __parse_yml(yml_str: str) -> Dict:
        yml = {}
        level = []
        for line in yml_str.splitlines():
            if not line.startswith('#'):
                intend = (len(line) - len(line.lstrip())) / 4
                key_val = line.split(':')
                key = key_val[0].strip(' -')
                val = ':'.join(key_val[1:]).strip()

                while intend < len(level):
                    # Go as many levels up as necessary, for each level: add key, dict to the parent level and pop child
                    dict_key = level[-1][0]
                    dict_val = level[-1][1]
                    if len(level) > 1:
                        level[-2][1][dict_key] = dict_val
                    else:
                        yml[dict_key] = dict_val
                    level.pop()

                if intend and intend == len(level) and val != '':
                    # Stay on level and add key, val to the respective dict
                    curr_dict = level[-1][1]
                    curr_dict[key] = YAMLHandler.__parse_yml_val(val)
                elif val == '':
                    # Go one level deeper, add key and empty dict for that new level
                    level.append((key, {}))
                else:
                    # Add key, val to the top level
                    yml[key] = YAMLHandler.__parse_yml_val(val)

        while len(level) > 0:
            dict_key = level[-1][0]
            dict_val = level[-1][1]
            if len(level) > 1:
                level[-2][1][dict_key] = dict_val
            else:
                yml[dict_key] = dict_val
            level.pop()

        # This is fix for old files, nas should be part of onomastics
        if hasattr(yml, 'nas'):
            delattr(yml, 'nas')

        return yml

    def __init__(self, yml: Optional[Dict] = None) -> None:
        self.reviewed = 'NOT REVIEWED'
        self.reviewer = 'RESEARCHER'
        self.category = None
        self.headings = None
        self.dates_headings = None
        self.number_of_tokens = None

        for key in YAMLHandler.__attr_from_annotation:
            if key == 'ambiguous_toponyms':
                self.__setattr__(key, False)
            else:
                self.__setattr__(key, None)

        if yml:
            for key, val in yml.items():
                if key == 'headings':
                    val = HeadingTracker(val)
                if key == 'ambigious':
                    # Fix typo
                    key = 'ambiguous'
                self.__setattr__(key, val)

    @classmethod
    def from_yml_str(cls, yml_str: str) -> YAMLHandler:
        """Return instance with attr set from the yml_str."""
        return cls(YAMLHandler.__parse_yml(yml_str))

    def set_category(self, category: str) -> None:
        self.category = category

    def set_number_of_tokens(self, number_of_tokens: int) -> None:
        self.number_of_tokens = number_of_tokens

    def set_ambiguous_toponyms(self) -> None:
        self.ambiguous_toponyms = True

    def set_headings(self, headings: HeadingTracker) -> None:
        self.headings = headings

    def set_reviewed(self, reviewer) -> None:
        self.reviewed = 'REVIEWED'
        self.reviewer = reviewer

    def unset_reviewed(self) -> None:
        self.reviewed = 'NOT REVIEWED'
        self.reviewer = None

    def set_error_while_collecting_annotated_entities(self, tag: str) -> None:
        self.error_while_collecting_annotated_entities = True
        if hasattr(self, 'erroneous_tags'):
            self.erroneous_tags.append(tag)
        else:
            self.erroneous_tags = [tag]

    def get_yamlfied(self) -> str:
        yaml_str = MIU_HEADER + 'Begin#\n\n'
        for key, val in vars(self).items():
            if val:
                if key == 'category':
                    yaml_str += key + '    : \'' + val + '\'\n'
                elif hasattr(val, 'get_yamlfied'):
                    yaml_str += f'{key}    : {val.get_yamlfied()}\n'
                elif isinstance(val, dict):
                    yaml_str += f'{key}    :\n{dict_to_yaml(val, 1)}\n'
                else:
                    yaml_str += key + '    : ' + str(val) + '\n'
        yaml_str += '\n' + MIU_HEADER + 'End#\n\n'

        return yaml_str

    def to_json(self, init) -> Dict:
        json_dict = init
        for key, val in vars(self).items():
            if val:
                if hasattr(val, 'to_json'):
                    json_dict[key] = val.to_json()
                else:
                    json_dict[key] = val
                    if isinstance(val, Decimal):
                        raise TypeError(
                            f'{val} is of type {type(val)} which is not pickable - make sure to use int '
                            f'or float'
                            )
        return json_dict

    def is_bio(self) -> bool:
        return self.category == '$' or self.category == '$$'

    def is_reviewed(self) -> bool:
        return self.reviewed.startswith('REVIEWED')

    def add_date_headings(self, date: int) -> None:
        if self.dates_headings:
            if date not in self.dates_headings:
                self.dates_headings.append(date)
        else:
            self.dates_headings = [date]

    def add_number_of_tokens(self, number_of_tokens: int) -> None:
        self.number_of_tokens = number_of_tokens

    def add_tagged_entities(self, entities_dict: dict) -> None:
        for key in YAMLHandler.__attr_from_annotation:
            # Clear old entities
            if key != 'ambiguous_toponyms':
                self.__setattr__(key, None)
            elif hasattr(self, 'ambiguous_toponyms'):
                self.__delattr__('ambiguous_toponyms')
        for key in YAMLHandler.__attr_from_annotation:
            # Set new entities in same order
            if key in entities_dict.keys():
                self.__setattr__(key, entities_dict.get(key))

    def __setitem__(self, key: str, value: Any) -> None:
        super().__setattr__(key, value)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __str__(self) -> str:
        return self.get_yamlfied()
