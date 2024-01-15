from typing import Optional

from os.path import split, splitext

from eis1600.markdown.markdown_patterns import HEADER_END_PATTERN, NORMALIZE_BIO_CHR_MD_PATTERN, \
    PAGE_TAG_SPLITTING_PARAGRAPH_PATTERN, SPACES_CROWD_PATTERN, NEWLINES_CROWD_PATTERN, POETRY_PATTERN, \
    SPACES_AFTER_NEWLINES_PATTERN, PAGE_TAG_ON_NEWLINE_MARKDOWN_PATTERN, BIO_CHR_TO_NEWLINE_PATTERN


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
