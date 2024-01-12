from typing import Optional, List, Set
from copy import copy
from random import randint


class UIDs:
    """Generates a set of UIDs which can be used by all instances of UIDs.

    Generates one large set of UIDs when this class is imported. Each instance reuses that set, but subtracts already
    used UIDs. Saves time as the set only needs to be generated once and is reused and adapted in instances.

    :param List[int] existing_uids: List of UIDs already used in the current text, optional.
    :ivar Set[int] ids: Set of UIDs which does not contain already used UIDs.
    """

    @staticmethod
    def _generate_ids() -> Set[int]:
        """Generates a set of 5000000 UIDs.

        :return Set[int]: A set of 5000000 UIDs.
        """

        ids = []
        for i in range(0, 5000000):
            ids.append(randint(400000000000, 999999999999))
        return set(ids)

    IDS = None

    def __init__(self, existing_uids: Optional[List[int]] = None) -> None:
        """Constructor method, creates an individual set uids per instance.

        Adaptes the pre-generated set of UIDs to the current instance by subtracting already existing UIDs,
        if this list was given to the constructor. Otherwise it uses a copy of the static IDS set.
        :param List[int] existing_uids: List of already used UIDs in the current text.
        """

        if UIDs.IDS is None:
            """Set of 5000000 random UIDs generated once and shared by all instances of this class."""
            UIDs.IDS = UIDs._generate_ids()

        if existing_uids:
            self.ids = UIDs.IDS.difference(existing_uids)
        else:
            self.ids = copy(UIDs.IDS)

        self.iter = self.ids.__iter__()

    def get_uid(self) -> int:
        """Returns an individual UID."""

        return next(self.iter)

