from typing import Tuple

from eis1600.markdown.markdown_patterns import AGE_PATTERN, LUNAR_PATTERN, YEAR_PATTERN


def get_yrs_tag_value(tag: str) -> Tuple[int, str]:
    """Returns int value encoded in the tag for date and age tags.

    :param str tag: Annotation.
    :return int:  numeric value which was encoded in the tag.
    :raise ValueError: If the tag is not correct a ValueError is raised.
    """
    if YEAR_PATTERN.match(tag):
        m = YEAR_PATTERN.match(tag)
    elif AGE_PATTERN.match(tag):
        m = AGE_PATTERN.match(tag)
    elif LUNAR_PATTERN.match(tag):
        m = LUNAR_PATTERN.match(tag)
        return int(m.group('written')), m.group('cat')
    else:
        raise ValueError

    if m.group('real'):
        return int(m.group('real')), m.group('cat')
    else:
        return int(m.group('written')), m.group('cat')
