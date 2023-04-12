from eis1600.helper.markdown_patterns import AGE_PATTERN, YEAR_PATTERN


def get_yrs_tag_value(tag: str) -> int:
    """Returns int value encoded in the tag for date and age tags.

    :param str tag: Annotation.
    :return int:  numeric value which was encoded in the tag.
    :raise ValueError: If the tag is not correct a ValueError is raised.
    """
    if YEAR_PATTERN.match(tag):
        m = YEAR_PATTERN.match(tag)
    elif AGE_PATTERN.match(tag):
        m = AGE_PATTERN.match(tag)
    else:
        raise ValueError

    if m.group('real'):
        return int(m.group('real'))
    else:
        return int(m.group('written'))