class HeadingTracker:
    """A class to keep track of the super elements of a MIU.

    This class keeps track of the headings on different levels to keep this information in the MIU YAML header. Some
    headings are empty stings
    :ivar str level1: Level 1 heading, optional.
    :ivar str level2: Level 2 heading, optional.
    :ivar str level3: Level 3 heading, optional.
    :ivar str level4: Level 4 heading, optional.
    """

    def __init__(self) -> None:
        """Constructor which sets attributes to empty strings."""

        self.level1 = None
        self.level2 = None
        self.level3 = None
        self.level4 = None

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __str__(self) -> str:
        return str(self.__dict__)

    def get_curr_state(self) -> dict:
        """Get current state of the tacker as dict.

        Returns a dictionary of the current state, but only with attributes whose value is not an empty string.
        :return dict: Dict of the current state of the tracker.
        """

        if self.level1 is None:
            return None

        headings_dict = {}
        for key, val in self.__dict__.items():
            if val is not None:
                headings_dict[key] = val

        return headings_dict

    def get_yamlfied(self) -> str:
        """Stringifies HeadingTracker in YAML format, only includes levels which are set.

        :return str: returns the HeadingTracker in YAML format as a string.
        """

        if self.level1 is None:
            return None

        heading_tracker_str = 'Heading_1    : ' + self.level1 + '\n'
        if self.level2 is not None:
            heading_tracker_str += 'Heading_2    : ' + self.level2 + '\n'
            if self.level3 is not None:
                heading_tracker_str += 'Heading_3    : ' + self.level3 + '\n'
                if self.level4 is not None:
                    heading_tracker_str += 'Heading_4    : ' + self.level4 + '\n'

        return heading_tracker_str

    def track(self, level: int, heading: str) -> None:
        """Checks which of the levels changed and sets all sub levels to None (some headings are just an empty string).

        :param int level: The level of the heading indicated by the number of leading `|`.
        :param str heading: The new heading text for the given level.
        """

        if level == 1:
            self.level1 = heading
            self.level2 = None
            self.level3 = None
            self.level4 = None
        elif level == 2:
            self.level2 = heading
            self.level3 = None
            self.level4 = None
        elif level == 3:
            self.level3 = heading
            self.level4 = None
        else:
            self.level4 = heading
