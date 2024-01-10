from typing import Optional

from sys import exit
from os.path import split, splitext

from eis1600.markdown.UIDs import UIDs
from eis1600.helper.markdown_patterns import EMPTY_FIRST_PARAGRAPH_PATTERN, EMPTY_PARAGRAPH_PATTERN, \
    HEADER_END_PATTERN, \
    MISSING_DIRECTION_TAG_PATTERN, NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN, MIU_TAG_AND_TEXT_PATTERN, \
    NORMALIZE_BIO_CHR_MD_PATTERN, ONLY_PAGE_TAG_PATTERN, \
    PAGE_TAG_IN_BETWEEN_PATTERN, \
    PAGE_TAG_PATTERN, \
    PAGE_TAG_SPLITTING_PARAGRAPH_PATTERN, SPACES_CROWD_PATTERN, \
    NEWLINES_CROWD_PATTERN, \
    POETRY_PATTERN, SPACES_AFTER_NEWLINES_PATTERN, PAGE_TAG_ON_NEWLINE_MARKDOWN_PATTERN, \
    PAGE_TAG_ON_NEWLINE_TMP_PATTERN, \
    MIU_UID_TAG_AND_TEXT_SAME_LINE_PATTERN, \
    UID_PATTERN, \
    HEADING_OR_BIO_PATTERN, \
    BIO_CHR_TO_NEWLINE_PATTERN


def normalize_bio_chr_md(paragraph: str) -> str:
    md = NORMALIZE_BIO_CHR_MD_PATTERN.match(paragraph).group(0)
    if md == '$BIO_MAN$':
        return NORMALIZE_BIO_CHR_MD_PATTERN.sub('# $', paragraph)
    elif md == '$BIO_WOM$':
        return NORMALIZE_BIO_CHR_MD_PATTERN.sub('# $$', paragraph)
    elif md == '$BIO_REF$':
        return NORMALIZE_BIO_CHR_MD_PATTERN.sub('# $$$', paragraph)
    elif md == '$CHR_EVE$':
        return NORMALIZE_BIO_CHR_MD_PATTERN.sub('# @', paragraph)
    elif md == '$CHR_RAW$':
        return NORMALIZE_BIO_CHR_MD_PATTERN.sub('# @@@', paragraph)
    elif md == '@ RAW':
        return NORMALIZE_BIO_CHR_MD_PATTERN.sub('# @@@', paragraph)
    else:
        return paragraph


def convert_to_EIS1600TMP(infile: str, output_dir: Optional[str] = None, verbose: bool = False) -> None:
    """Coverts a file to EIS1600TMP for review process.

    Converts mARkdown, inProgress, completed file to light EIS1600TMP for the review process. Creates the file with the
    '.EIS1600TMP' extension.

    :param str infile: Path of the file to convert.
    :param str or None output_dir: Directory to write new file to (discontinued), optional.
    :param bool verbose: If True outputs a notification of the file which is currently processed, defaults to False.
    :return None:
    """
    if output_dir:
        path, uri = split(infile)
        uri, ext = splitext(uri)
        outfile = output_dir + '/' + uri + '.EIS1600TMP'
    else:
        path, ext = splitext(infile)
        outfile = path + '.EIS1600TMP'
        path, uri = split(infile)

    if verbose:
        print(f'Convert {uri} from mARkdown to EIS1600 file')

    with open(infile, 'r', encoding='utf8') as infile_h:
        text = infile_h.read()

    header_and_text = HEADER_END_PATTERN.split(text)
    header = header_and_text[0] + header_and_text[1]
    text = header_and_text[2][1:]  # Ignore second new line after #META#Header#End#

    if text[0:2] == '#\n':
        # Some texts start with a plain #, remove these
        text = text[2:]

    # fix
    text = text.replace('~\n', '\n')
    text = text.replace('\n~~', ' ')
    text = text.replace(' \n', '\n')

    # spaces
    text = SPACES_AFTER_NEWLINES_PATTERN.sub('\n', text)
    text = SPACES_CROWD_PATTERN.sub(' ', text)

    # fix poetry
    text = POETRY_PATTERN.sub(r'\1', text)

    # fix page tag on newlines
    text = PAGE_TAG_SPLITTING_PARAGRAPH_PATTERN.sub(r'\1 \2 \3', text)
    text = PAGE_TAG_ON_NEWLINE_MARKDOWN_PATTERN.sub(r' \1\n', text)
    text = SPACES_CROWD_PATTERN.sub(' ', text)

    # fix new lines
    text = text.replace('\n###', '\n\n###')
    text = text.replace('\n# ', '\n\n')
    text = NEWLINES_CROWD_PATTERN.sub('\n\n', text)

    text = text.split('\n\n')

    text_updated = []

    for paragraph in text:
        if paragraph.startswith('### '):
            paragraph = paragraph.replace('###', '#')
            if NORMALIZE_BIO_CHR_MD_PATTERN.match(paragraph):
                paragraph = normalize_bio_chr_md(paragraph)
            paragraph = BIO_CHR_TO_NEWLINE_PATTERN.sub(r'\1\n\2', paragraph)
        text_updated.append(paragraph)

    # reassemble text
    text = '\n\n'.join(text_updated)
    final = header + '\n\n' + text
    if final[-1] != '\n':
        final += '\n'

    with open(outfile, 'w', encoding='utf8') as outfile_h:
        outfile_h.write(final)


def insert_uids(infile: str, output_dir: Optional[str] = None, verbose: Optional[bool] = False) -> None:
    """Insert UIDs and EIS1600 tags into EIS1600TMP file and thereby convert it to EIS1600 format.


    :param str infile: Path of the file to convert.
    :param str or None output_dir: Directory to write new file to (discontinued), optional.
    :param bool verbose: If True outputs a notification of the file which is currently processed, defaults to False.
    :return None:
    """

    if output_dir:
        path, uri = split(infile)
        uri, ext = splitext(uri)
        outfile = output_dir + '/' + uri + '.EIS1600'
    else:
        path, ext = splitext(infile)
        outfile = path + '.EIS1600'
        path, uri = split(infile)

    if verbose:
        print(f'Insert UIDs into {uri} and convert to final EIS1600 file')

    with open(infile, 'r', encoding='utf8') as infile_h:
        text = infile_h.read()

    # disassemble text into paragraphs
    header_and_text = HEADER_END_PATTERN.split(text)
    header = header_and_text[0] + header_and_text[1]
    text = header_and_text[2].lstrip('\n')  # Ignore new lines after #META#Header#End#
    text = NEWLINES_CROWD_PATTERN.sub('\n\n', text)
    text = NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN.sub('\n\n', text)
    text = text.replace(' \n', '\n')
    text = text.replace('\n ', '\n')
    text = PAGE_TAG_ON_NEWLINE_TMP_PATTERN.sub(r' \1', text)
    text = text.split('\n\n')
    text_updated = []

    uids = UIDs()

    text_iter = text.__iter__()
    paragraph = next(text_iter)
    prev_p = ''

    # Insert UIDs and EIS1600 tags into the text
    while paragraph is not None:
        next_p = next(text_iter, None)

        if paragraph:
            # Only do this if paragraph is not empty
            if paragraph.startswith('#'):
                # Move content to an individual line
                paragraph = BIO_CHR_TO_NEWLINE_PATTERN.sub(r'\1\n\2', paragraph)
                paragraph = paragraph.replace('#', f'_ء_#={uids.get_uid()}=')
                # Insert a paragraph tag
                heading_and_text = paragraph.splitlines()
                if len(heading_and_text) == 2:
                    paragraph = heading_and_text[0] + f'\n\n_ء_={uids.get_uid()}= ::UNDEFINED:: ~\n_ء_ ' + \
                                heading_and_text[1]
                elif len(heading_and_text) > 2:
                    raise ValueError(
                            infile + '\n'
                            f'There is a single new line in this paragraph:\n{paragraph}'
                    )
                text_updated.append(paragraph)
            elif '%~%' in paragraph:
                paragraph = f'_ء_={uids.get_uid()}= ::POETRY:: ~\n_ء_ ' + '\n_ء_ '.join(paragraph.splitlines())
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
                # else:
                # Remove PageV00P000 at the beginning in an individual paragraph
                # text_updated.append(paragraph)
                # pass
            elif paragraph.startswith('::'):
                p_pieces = paragraph.splitlines()
                section_header = p_pieces[0]

                if '%' in paragraph:
                    paragraph = '\n_ء_ '.join(p_pieces[1:])
                elif len(p_pieces) > 2:
                    raise ValueError(
                            infile + '\n'
                            f'There is a single new line in this paragraph:\n{paragraph}'
                    )
                elif len(p_pieces) == 2:
                    paragraph = p_pieces[1]
                else:
                    print(
                        'There is an empty paragraph, check with\n'
                        '::\\n[^هسءگؤقأذپيمجثاڤوضآرتنكزفبعٱشىصلدطغإـئظحةچخ_]'
                        )
                    exit()

                paragraph = f'_ء_={uids.get_uid()}= {section_header} ~\n_ء_ ' + paragraph
                text_updated.append(paragraph)
            else:
                paragraph = f'_ء_={uids.get_uid()}= ::UNDEFINED:: ~\n_ء_ ' + paragraph
                text_updated.append(paragraph)

        prev_p = paragraph
        paragraph = next_p

    # reassemble text
    text = '\n\n'.join(text_updated)
    final = header + '\n\n' + text
    if final[-1] != '\n':
        final += '\n'

    with open(outfile, 'w', encoding='utf8') as outfile_h:
        outfile_h.write(final)


def update_uids(infile: str, verbose: Optional[bool] = False) -> None:
    """Updates a text with missing UIDs and EIS1600 tags.

    :param str infile: Path of the file to update UIDs in.
    :param bool verbose: If True outputs a notification of the file which is currently processed, defaults to False.
    :return None:
    """

    path, ext = splitext(infile)
    outfile = path + '.EIS1600'
    path, uri = split(infile)

    if verbose:
        print(f'Update UIDs in {uri}')

    with open(infile, 'r', encoding='utf8') as infile_h:
        text = infile_h.read()

    # disassemble text into paragraphs
    header_and_text = HEADER_END_PATTERN.split(text)
    header = header_and_text[0] + header_and_text[1]
    text = header_and_text[2].lstrip('\n')  # Ignore new lines after #META#Header#End#
    text = NEWLINES_CROWD_PATTERN.sub('\n\n', text)
    text = NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN.sub('\n\n', text)
    text = MISSING_DIRECTION_TAG_PATTERN.sub('\g<1>_ء_ \g<2>', text)
    text = text.split('\n\n')
    text_updated = []

    used_ids = []

    # Collect existing UIDs
    for idx, paragraph in enumerate(text):
        if UID_PATTERN.match(paragraph):
            uid = int(UID_PATTERN.match(paragraph).group('UID'))
            if uid not in used_ids:
                used_ids.append(uid)
            else:
                # If in the review process an UID was accidentally inserted twice, just remove the second occurrence
                # - this element will get a new UID in the next steps.
                if UID_PATTERN.match(paragraph).group(1):
                    # Python returns None for empty capturing groups which messes up the string
                    text[idx] = UID_PATTERN.sub('\1', paragraph)
                else:
                    text[idx] = UID_PATTERN.sub('', paragraph)

    uids = UIDs(used_ids)

    text_iter = text.__iter__()
    paragraph = next(text_iter)
    prev_p = None

    if EMPTY_FIRST_PARAGRAPH_PATTERN.fullmatch(paragraph):
        # Some OpenITI texts start with a single # which causes a plain UID tag as first element - ignore those
        paragraph = next(text_iter)

    # Insert missing UIDs and EIS1600 tags into the text
    while paragraph is not None:
        next_p = next(text_iter, None)

        if paragraph:
            # Only do this if paragraph is not empty
            if HEADING_OR_BIO_PATTERN.match(paragraph):
                # Move content to an individual line
                paragraph = BIO_CHR_TO_NEWLINE_PATTERN.sub(r'\1\n\2', paragraph)
                paragraph = paragraph.replace('#', f'_ء_#={uids.get_uid()}=')
                # Insert a paragraph tag
                heading_and_text = paragraph.splitlines()
                if len(heading_and_text) == 2:
                    paragraph = heading_and_text[0] + f'\n\n_ء_={uids.get_uid()}= ::UNDEFINED:: ~\n\n_ء_ ' \
                                                      f'{heading_and_text[1]}'
                elif len(heading_and_text) > 2:
                    raise ValueError(
                            infile + '\n'
                            f'There is a single new line in this paragraph:\n{paragraph}'
                    )
            elif not UID_PATTERN.match(paragraph):
                if paragraph.startswith('::'):
                    p_pieces = paragraph.splitlines()
                    section_header = p_pieces[0] + ' ~'
                    if '%' in paragraph:
                        paragraph = '\n_ء_ '.join(p_pieces[1:])
                    elif len(p_pieces) > 2:
                        raise ValueError(
                                infile + '\n'
                                f'There is a single new line in this paragraph:\n{paragraph}'
                        )
                    elif len(p_pieces) == 2:
                        paragraph = p_pieces[1]
                    else:
                        print('There is an empty paragraph, check with\n'
                              '::\\n[^هسءگؤقأذپيمجثاڤوضآرتنكزفبعٱشىصلدطغإـئظحةچخ_]'
                              )
                        exit()

                    if paragraph[0] != '_':
                        paragraph = '_ء_ ' + paragraph
                else:
                    cat = 'POETRY' if '%' in paragraph else 'UNDEFINED'
                    if paragraph[0] != '_':
                        paragraph = '_ء_ ' + paragraph
                    section_header = f'::{cat}:: ~'
                paragraph = f'_ء_={uids.get_uid()}= {section_header}\n' + paragraph
            elif MIU_UID_TAG_AND_TEXT_SAME_LINE_PATTERN.match(paragraph):
                paragraph = MIU_UID_TAG_AND_TEXT_SAME_LINE_PATTERN.sub(r'\1\2\n\3', paragraph)
                # Insert a paragraph tag
                heading_and_text = paragraph.splitlines()
                if '%' in '\n'.join(heading_and_text[1:]):
                    paragraph = heading_and_text[0] + f'\n\n_ء_={uids.get_uid()}= ::POETRY:: ~\n\n_ء_' + '\n_ء_ '.join(
                            heading_and_text[1:]
                    )
                elif len(heading_and_text) > 2:
                    raise ValueError(
                            infile + '\n'
                            f'There is a single new line in this paragraph:\n{paragraph}'
                    )
                else:
                    paragraph = heading_and_text[0] + f'\n\n_ء_={uids.get_uid()}= ::UNDEFINED:: ~\n_ء_ ' + \
                                heading_and_text[1]
            elif MIU_TAG_AND_TEXT_PATTERN.match(paragraph):
                # Insert a paragraph tag
                heading_and_text = paragraph.splitlines()
                if '%' in '\n'.join(heading_and_text[1:]):
                    paragraph = heading_and_text[0] + f'\n\n_ء_={uids.get_uid()}= ::POETRY:: ~\n_ء_ ' + '\n_ء_ '.join(
                            heading_and_text[1:]
                    )
                elif len(heading_and_text) > 2:
                    raise ValueError(
                            infile + '\n'
                                     f'There is a single new line in this paragraph:\n{paragraph}'
                    )
                else:
                    paragraph = heading_and_text[0] + f'\n\n_ء_={uids.get_uid()}= ::UNDEFINED:: ~\n_ء_ ' + \
                                heading_and_text[1]
            if ONLY_PAGE_TAG_PATTERN.fullmatch(paragraph):
                # Add page tags to previous paragraph if there is no other information contained in the current
                # paragraph
                page_tag = ONLY_PAGE_TAG_PATTERN.match(paragraph).group('page_tag')
                if PAGE_TAG_IN_BETWEEN_PATTERN.search('\n\n'.join([prev_p, paragraph, next_p])):
                    if text_updated:
                        next_p_text = next_p.split('::UNDEFINED:: ~\n_ء_ ')[1]
                        if text_updated[-1][-1] == ' ':
                            text_updated[-1] += page_tag + ' ' + next_p_text
                        else:
                            text_updated[-1] += ' ' + page_tag + ' ' + next_p_text
                        paragraph = next_p
                        next_p = next(text_iter, None)
                elif text_updated:
                    text_updated[-1] += ' ' + page_tag
                # else:
                # Remove PageV00P000 at the beginning in an individual paragraph
                # text_updated.append(paragraph)
                # pass
            elif not EMPTY_PARAGRAPH_PATTERN.fullmatch(paragraph):
                # Do not add empty paragraphs to the updated text
                text_updated.append(paragraph)
        prev_p = paragraph
        paragraph = next_p

    # reassemble text
    text = '\n\n'.join(text_updated)
    final = header + '\n\n' + text
    if final[-1] != '\n':
        final += '\n'

    with open(outfile, 'w', encoding='utf8') as outfile_h:
        outfile_h.write(final)
