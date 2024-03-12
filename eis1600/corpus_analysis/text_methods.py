from os.path import split, splitext
from typing import List, Tuple

from eis1600.markdown.markdown_patterns import CATEGORY_PATTERN, HEADER_END_PATTERN, HEADING_PATTERN, MIU_TAG_PATTERN, \
    MIU_UID_TAG_PATTERN, PAGE_TAG_PATTERN
from eis1600.miu.HeadingTracker import HeadingTracker
from eis1600.texts_to_mius.check_formatting_methods import check_file_for_mal_formatting
from eis1600.yml.yml_handling import create_yml_header


def get_text_as_list_of_mius(infile: str) -> Tuple[str, List[Tuple[str, str, bool]]]:
    """Disassemble text into list of MIUs.

    Splits the texts into individual MIUs and returns a list of all contained MIUs.
    :param str infile: File which will be disassembled.
    :return List[Tuple[str, str, bool]]: returns the individual MIUs as tuples of (uid, miu_text, analysis_flag).
    """
    heading_tracker = HeadingTracker()
    path, uri = split(infile)
    uri, ext = splitext(uri)
    uid = ''
    miu_text = ''

    with open(infile, 'r', encoding='utf8') as text:
        header_text = text.read().split('#META#Header#End#\n\n')
        meta_data_header = header_text[0] + '#META#Header#End#\n\n'

        try:
            check_file_for_mal_formatting(infile, header_text[1])
        except ValueError:
            raise

        mal_formatted = []
        mius = []

        text.seek(0)
        for text_line in iter(text):
            if HEADER_END_PATTERN.match(text_line):
                miu_text = ''
                uid = uri + '.' + 'preface'
                next(text)  # Skip empty line after header
            elif MIU_UID_TAG_PATTERN.match(text_line):
                if HEADING_PATTERN.match(text_line):
                    m = HEADING_PATTERN.match(text_line)
                    heading_text = m.group('heading')
                    if PAGE_TAG_PATTERN.search(heading_text):
                        heading_text = PAGE_TAG_PATTERN.sub('', heading_text)
                    heading_tracker.track_headings(len(m.group('level')), heading_text)
                if miu_text:
                    # Do not create a preface MIU file if there is no preface
                    mius.append((uid, miu_text + '\n', analyse_flag))
                m = MIU_TAG_PATTERN.match(text_line)
                uid = uri + '.' + m.group('UID')
                category = ''
                try:
                    category = CATEGORY_PATTERN.search(m.group('category')).group(0)
                except AttributeError:
                    mal_formatted.append(f"Category not recognised: {m.group(0)}\n")
                yml_header = create_yml_header(category, heading_tracker.get_curr_state())
                analyse_flag = category not in ['|PARATEXT|', '|EDITOR|']
                miu_text = yml_header
                miu_text += text_line
            else:
                miu_text += text_line

            if PAGE_TAG_PATTERN.search(text_line):
                heading_tracker.track_pages(PAGE_TAG_PATTERN.search(text_line).group(0))

        # last MIU needs to be appended after the for-loop is finished
        mius.append((uid, miu_text + '\n', analyse_flag))

    if mal_formatted:
        print('Something seems to be mal-formatted, check:')
        print(infile)
        for elem in mal_formatted:
            print(elem)

    return meta_data_header, mius
