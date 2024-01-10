from re import compile
from typing import Optional

from eis1600.markdown.SubIDs import SubIDs
from eis1600.markdown.UIDs import UIDs

from eis1600.helper.markdown_patterns import BIO_CHR_TO_NEWLINE_PATTERN, EMPTY_FIRST_PARAGRAPH_PATTERN, \
    EMPTY_PARAGRAPH_PATTERN, HEADER_END_PATTERN, \
    HEADING_OR_BIO_PATTERN, MISSING_DIRECTION_TAG_PATTERN, MIU_TAG_AND_TEXT_PATTERN, NEWLINES_CROWD_PATTERN, \
    NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN, ONLY_PAGE_TAG_PATTERN, PAGE_TAG_IN_BETWEEN_PATTERN, \
    PAGE_TAG_ON_NEWLINE_TMP_PATTERN, PAGE_TAG_PATTERN, \
    PAGE_TAG_SPLITTING_PARAGRAPH_PATTERN, UID_PATTERN, MIU_UID_TAG_AND_TEXT_SAME_LINE_PATTERN

MIU_UID_PATTERN = compile(r'_ء_#=(?P<uid>\d{12})= ')
PARAGRAPH_UID_REPLACE = compile(r'_ء_=\d{12}= (::[A-Z_]+::) ~')


def pre_clean_text(text: str) -> str:
    text = NEWLINES_CROWD_PATTERN.sub('\n\n', text)
    text = NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN.sub('\n\n', text)
    text = text.replace(' \n', '\n')
    text = text.replace('\n ', '\n')
    text = PAGE_TAG_ON_NEWLINE_TMP_PATTERN.sub(r' \1', text)
    text = MISSING_DIRECTION_TAG_PATTERN.sub('\g<1>_ء_ \g<2>', text)

    return text


def insert_ids(text: str) -> str:
    # disassemble text into paragraphs
    text = text.split('\n\n')
    text_updated = []

    uids = UIDs()

    text_iter = text.__iter__()
    paragraph = next(text_iter)
    prev_p = ''

    subids = None

    # Insert UIDs and EIS1600 tags into the text
    while paragraph is not None:
        next_p = next(text_iter, None)

        if paragraph:
            # Only do this if paragraph is not empty
            if paragraph.startswith('#'):
                uid = uids.get_uid()
                subids = SubIDs(uid)
                # Move content to an individual line
                paragraph = BIO_CHR_TO_NEWLINE_PATTERN.sub(r'\1\n\2', paragraph)
                paragraph = paragraph.replace('#', f'_ء_#={uid}=')
                # Insert a paragraph tag
                heading_and_text = paragraph.splitlines()
                if len(heading_and_text) == 2:
                    paragraph = heading_and_text[0] + f'\n\n_ء_={subids.get_id()}= ::UNDEFINED:: ~\n_ء_ ' + \
                                heading_and_text[1]
                elif len(heading_and_text) > 2:
                    raise ValueError(
                            f'There is a single new line in this paragraph:\n{paragraph}'
                    )
                text_updated.append(paragraph)
            elif '%~%' in paragraph:
                paragraph = f'_ء_={subids.get_id()}= ::POETRY:: ~\n_ء_ ' + '\n_ء_ '.join(paragraph.splitlines())
                text_updated.append(paragraph)
            elif PAGE_TAG_PATTERN.fullmatch(paragraph):
                page_tag = PAGE_TAG_PATTERN.match(paragraph).group('page_tag')
                if PAGE_TAG_SPLITTING_PARAGRAPH_PATTERN.search('\n\n'.join([prev_p, paragraph, next_p])):
                    if text_updated:
                        if text_updated[-1][-1] == ' ':
                            text_updated[-1] += page_tag + ' ' + next_p
                        else:
                            text_updated[-1] += ' ' + page_tag + ' ' + next_p
                        paragraph = next_p
                        next_p = next(text_iter, None)
                elif text_updated:
                    text_updated[-1] += ' ' + page_tag
            elif paragraph.startswith('::'):
                p_pieces = paragraph.splitlines()
                section_header = p_pieces[0]

                if '%' in paragraph:
                    paragraph = '\n_ء_ '.join(p_pieces[1:])
                elif len(p_pieces) > 2:
                    raise ValueError(
                            f'There is a single new line in this paragraph:\n{paragraph}'
                    )
                elif len(p_pieces) == 2:
                    paragraph = p_pieces[1]
                else:
                    raise ValueError(
                            'There is an empty paragraph, check with\n'
                            '::\\n[^هسءگؤقأذپيمجثاڤوضآرتنكزفبعٱشىصلدطغإـئظحةچخ_]'
                    )

                paragraph = f'_ء_={subids.get_id()}= {section_header} ~\n_ء_ ' + paragraph
                text_updated.append(paragraph)
            else:
                paragraph = f'_ء_={subids.get_id()}= ::UNDEFINED:: ~\n_ء_ ' + paragraph
                text_updated.append(paragraph)

        prev_p = paragraph
        paragraph = next_p

    # reassemble text
    text = '\n\n'.join(text_updated)

    return text


def add_ids(infile: str, ids_update: Optional[bool] = False) -> None:
    """Insert UIDs and EIS1600 tags into EIS1600TMP file and thereby convert it to EIS1600 format.


    :param str infile: Path of the file to convert.
    :return None:
    """

    with open(infile, 'r+', encoding='utf8') as infile_h:
        text = infile_h.read()

        header_and_text = HEADER_END_PATTERN.split(text)
        header = header_and_text[0] + header_and_text[1]
        text = header_and_text[2].lstrip('\n')  # Ignore new lines after #META#Header#End#
        text = pre_clean_text(text)

        if ids_update:
            try:
                text = text
            except ValueError as e:
                print(f'{infile}\n{e}')
        else:
            text = MIU_UID_PATTERN.sub(r'# ', text)
            text = PARAGRAPH_UID_REPLACE.sub(r'\g<1>', text)
            try:
                text = insert_ids(text)
            except ValueError as e:
                print(f'{infile}\n{e}')

        final = header + '\n\n' + text
        if final[-1] != '\n':
            final += '\n'

        infile_h.seek(0)
        infile_h.write(final)
        infile_h.truncate()
