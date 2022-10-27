class HeadingTracker:
    """A class to keep track of the super elements of a MIU.

    This class keeps track of the headings on different levels to keep this information in the MIU YAML header.
    :ivar str level1: Level 1 heading.
    :ivar str level2: Level 2 heading.
    :ivar str level3: Level 3 heading.
    :ivar str level4: Level 4 heading.
    """

    def __init__(self) -> None:
        """Constructor which sets attributes to empty strings."""

        self.level1 = ''
        self.level2 = ''
        self.level3 = ''
        self.level4 = ''

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __str__(self) -> str:
        return str(self.__dict__)

    def get_curr_state(self) -> dict:
        """Get current state of the tacker as dict.

        Returns a dictionary of the current state, but only with attributes whose value is not an empty string.
        :return dict: Dict of the current state of the tracker.
        """

        if not self.level1:
            return None

        headings_dict = {}
        for key, val in self.__dict__.items():
            if val:
                headings_dict[key] = val

        return headings_dict

    def get_yamlfied(self) -> str:
        """Stringifies HeadingTracker in YAML format, only includes levels which are set.

        :return str: returns the HeadingTracker in YAML format as a string.
        """

        if not self.level1:
            return ''

        heading_tracker_str = 'Heading_1    : ' + self.level1 + '\n'
        if self.level2:
            heading_tracker_str += 'Heading_2    : ' + self.level2 + '\n'
            if self.level3:
                heading_tracker_str += 'Heading_3    : ' + self.level3 + '\n'
                if self.level4:
                    heading_tracker_str += 'Heading_4    : ' + self.level4 + '\n'

        return heading_tracker_str

    def track(self, level: int, heading: str) -> None:
        """Checks which of the levels changed and sets all sub levels to an empty string.

        :param int level: The level of the heading indicated by the number of leading `|`.
        :param str heading: The new heading text for the given level.
        """

        if level == 1:
            self.level1 = heading
            self.level2 = ''
            self.level3 = ''
            self.level4 = ''
        elif level == 2:
            self.level2 = heading
            self.level3 = ''
            self.level4 = ''
        elif level == 3:
            self.level3 = heading
            self.level4 = ''
        else:
            self.level4 = heading
