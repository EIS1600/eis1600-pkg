from typing import Optional, Type

from eis1600.miu.HeadingTracker import HeadingTracker
from eis1600.miu.YAMLHandler import YAMLHandler

from eis1600.markdown.re_patterns import MIU_HEADER_PATTERN, NEWLINES_CROWD_PATTERN


def create_yml_header(headings: Type[HeadingTracker]) -> str:
    """Creates a YAML header for the current MIU file and returns it as yamlfied string.

    :param Type[HeadingsTracker] headings: HeadingTracker with the super elements of the current MIU.
    :return str: YAML header for the current MIU.
    """

    yml_header = YAMLHandler()
    if headings:
        yml_header.set_headings(headings)

    return yml_header.get_yamlfied()


def extract_yml_header_and_text(miu_file: str, is_header: Optional[bool] = False) -> (str, str):
    """ Returns the YAML header and the text as a tuple.

    Splits the MIU file into a tuple of YAML header and text.
    :param str miu_file: Path to the MIU file from which to extract YAML header and text.
    :param bool is_header: Indicates if the current MIU is the YAML header of the whole work and if so skips
    removing
    blank lines, defaults to False.
    :return (str, str): Tuple of the extracted YAML header and text.
    """

    with open(miu_file, 'r', encoding='utf-8') as file:
        text = ''
        miu_yml_header = ''
        for line in iter(file):
            if MIU_HEADER_PATTERN.match(line):
                # Omit the #MIU#Header# line as it is only needed inside the MIU.EIS1600 file, but not in YMLDATA.yml
                next(file)
                line = next(file)
                miu_yml_header = ''
                while not MIU_HEADER_PATTERN.match(line):
                    miu_yml_header += line
                    line = next(file)
                # Omit the empty line between the header content and the #MIU#Header# line
                miu_yml_header = miu_yml_header[:-2]
                # Skip empty line after #MIU#Header#
                next(file)
            else:
                text += line
            # Replace new lines which separate YAML header from text
            if not is_header:
                text = NEWLINES_CROWD_PATTERN.sub('\n\n', text)

        return miu_yml_header, text


def update_yml_header():
    # TODO: update YAML header with MIU related information from automated analyses and manual tags
    pass
