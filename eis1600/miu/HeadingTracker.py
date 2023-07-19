from __future__ import annotations
from copy import deepcopy

from typing import Dict, Optional


class HeadingTracker:
    """A class to keep track of the super elements of a MIU.

    This class keeps track of the headings on different levels to keep this information in the MIU YAML header. Some
    headings are empty stings
    :ivar str h1: Level 1 heading, optional.
    :ivar str h2: Level 2 heading, optional.
    :ivar str h3: Level 3 heading, optional.
    :ivar str h4: Level 4 heading, optional.
    """

    def __init__(self, headings_dict: Optional[Dict] = None) -> None:
        """Constructor which sets attributes to empty strings."""

        self.h1 = None
        self.h2 = None
        self.h3 = None
        self.h4 = None
        self.page_tag = None

        if headings_dict and type(headings_dict) == dict:
            for key, val in headings_dict.items():
                self.__setattr__(key, val)

    def __iter__(self):
        """Iterate over headings which are not None. Omits page_tag."""
        for key, val in self.__dict__.items():
            if key.startswith('h') and val is not None:
                yield key, val

    def get_curr_state(self) -> HeadingTracker:
        """Get current state of the tacker as deepcopy.

        Returns a deepcopy of the current state.
        :return HeadingTracker: Deepcopy of the current state of the tracker.
        """

        return deepcopy(self)

    def get_yamlfied(self) -> str:
        """Stringifies HeadingTracker in YAML format, only includes levels which are set.

        :return str: returns the HeadingTracker in YAML format as a string.
        """

        if self.h1 is None:
            return '[]'

        heading_tracker_str = '\n'
        heading_tracker_str += '    - h1    : \'' + self.h1 + '\'\n'
        if self.h2 is not None:
            heading_tracker_str += '    - h2    : \'' + self.h2 + '\'\n'
            if self.h3 is not None:
                heading_tracker_str += '    - h3    : \'' + self.h3 + '\'\n'
                if self.h4 is not None:
                    heading_tracker_str += '    - h4    : \'' + self.h4 + '\'\n'

        if self.page_tag:
            heading_tracker_str += '    - page_tag    : \'' + self.page_tag + '\''
        else:
            heading_tracker_str = heading_tracker_str[:-1]

        return heading_tracker_str

    def to_json(self) -> Dict:
        json_dict = {}
        for key, val in vars(self).items():
            if val is not None:
                json_dict[key] = val
        return json_dict

    def track_headings(self, level: int, heading: str) -> None:
        """Checks which of the levels changed and sets all sub levels to None (some headings are just an empty string).

        :param int level: The level of the heading indicated by the number of leading `|`.
        :param str heading: The new heading text for the given level.
        """

        if level == 1:
            self.h1 = heading
            self.h2 = None
            self.h3 = None
            self.h4 = None
        elif level == 2:
            self.h2 = heading
            self.h3 = None
            self.h4 = None
        elif level == 3:
            self.h3 = heading
            self.h4 = None
        else:
            self.h4 = heading

    def track_pages(self, page_tag: str) -> None:
        self.page_tag = page_tag.strip()

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __str__(self) -> str:
        return self.get_yamlfied()
