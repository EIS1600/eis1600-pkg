from typing import Optional

from os.path import split, splitext

from eis1600.markdown.UIDs import UIDs
from eis1600.markdown.re_patterns import HEADER_END_SPLIT_PATTERN, MIU_LIGHT_OR_EIS1600_PATTERN, SPACES_PATTERN, \
    NEWLINES_PATTERN, POETRY_PATTERN, SPACES_AFTER_NEWLINES_PATTERN, PAGE_TAG_ON_NEWLINE_PATTERN, UID_PATTERN, \
    HEADING_OR_BIO_PATTERN, POETRY_TO_PARAGRAPH, BIO_CHR_TO_NEWLINE_PATTERN


def convert_to_eis1600_light(infile: str, output_dir: Optional[str] = None, verbose: bool = False) -> None:
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

    header_and_text = HEADER_END_SPLIT_PATTERN.split(text)
    header = header_and_text[0] + header_and_text[1]
    text = header_and_text[2]

    # fix
    text = text.replace('~\n', '\n')
    text = text.replace('\n~~', ' ')

    # spaces
    text = SPACES_AFTER_NEWLINES_PATTERN.sub('\n', text)
    text = SPACES_PATTERN.sub(' ', text)

    # fix poetry
    text = POETRY_PATTERN.sub(r'\1', text)
    text = POETRY_TO_PARAGRAPH.sub(r'\1\n\n\2', text)

    # fix page tag on newlines
    text = PAGE_TAG_ON_NEWLINE_PATTERN.sub(r' \1', text)

    text = text.replace('\n###', '\n\n###')
    text = text.replace('\n# ', '\n\n')

    text = NEWLINES_PATTERN.sub('\n\n', text)

    text = text.split('\n\n')

    text_updated = []

    for paragraph in text:
        if paragraph.startswith('### '):
            paragraph = paragraph.replace('###', '#')
            paragraph = BIO_CHR_TO_NEWLINE_PATTERN.sub(r'\1\n\2', paragraph)
        text_updated.append(paragraph)

    text = '\n\n'.join(text_updated)

    # reassemble text
    final = header + '\n\n' + text

    with open(outfile, 'w', encoding='utf8') as outfile_h:
        outfile_h.write(final)


def insert_uids(infile: str, output_dir: Optional[str] = None, verbose: Optional[bool] = False) -> None:
    """Insert UIDs into EIS1600TMP file and thereby convert it to EIS1600.


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

    header_and_text = HEADER_END_SPLIT_PATTERN.split(text)
    header = header_and_text[0] + header_and_text[1]
    text = header_and_text[2]
    text = NEWLINES_PATTERN.sub('\n\n', text)
    text = text.split('\n\n')
    text_updated = []

    uids = UIDs()

    text_iter = text.__iter__()
    paragraph = next(text_iter)
    while paragraph is not None:
        next_p = next(text_iter, None)

        if paragraph:
            # Only do this is paragraph is not empty
            if paragraph.startswith('#'):
                paragraph = paragraph.replace('#', f'_ء_#={uids.get_uid()}=')
                if next_p and not next_p.startswith('#'):
                    heading_and_text = paragraph.split('\n', 1)
                    if len(heading_and_text) > 1:
                        paragraph = heading_and_text[0] + f'\n\n_ء_={uids.get_uid()}= ::UNDEFINED:: ~\n' + \
                                    heading_and_text[1]
            elif '%~%' in paragraph:
                paragraph = f'_ء_={uids.get_uid()}= ::POETRY:: ~\n' + paragraph
            else:
                paragraph = f'_ء_={uids.get_uid()}= ::UNDEFINED:: ~\n' + paragraph

            text_updated.append(paragraph)

        paragraph = next_p

    text = '\n\n'.join(text_updated)

    # reassemble text
    final = header + '\n\n' + text

    with open(outfile, 'w', encoding='utf8') as outfile_h:
        outfile_h.write(final)


def update_uids(infile: str, verbose: Optional[bool] = False) -> None:
    """Updates a text with missing UIDs.

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

    header_and_text = HEADER_END_SPLIT_PATTERN.split(text)
    header = header_and_text[0] + header_and_text[1]
    text = header_and_text[2]
    text = text.split('\n\n')
    text_updated = []

    used_ids = []

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
    while paragraph is not None:
        next_p = next(text_iter, None)

        if paragraph:
            # Only do this is paragraph is not empty
            if HEADING_OR_BIO_PATTERN.match(paragraph):
                paragraph = paragraph.replace('#', f'_ء_#={uids.get_uid()}=')
                if next_p and not MIU_LIGHT_OR_EIS1600_PATTERN.match(next_p):
                    heading_and_text = paragraph.split('\n', 1)
                    if len(heading_and_text) > 1:
                        paragraph = heading_and_text[0] + f'\n\n_ء_={uids.get_uid()}= ::UNDEFINED:: ~\n' + \
                                    heading_and_text[1]
            elif not UID_PATTERN.match(paragraph):
                section_header = '' if paragraph.startswith('::') else '::UNDEFINED:: ~\n'
                paragraph = f'_ء_={uids.get_uid()}= {section_header}' + paragraph

            text_updated.append(paragraph)
        paragraph = next_p

    text = '\n\n'.join(text_updated)

    # reassemble text
    final = header + '\n\n' + text

    with open(outfile, 'w', encoding='utf8') as outfile_h:
        outfile_h.write(final)
