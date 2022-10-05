from textwrap import wrap
from random import randint
from os.path import split, splitext

from eis1600.miu_handling.re_patterns import HEADER_END_PATTERN, SPACES_PATTERN, NEWLINES_PATTERN, POETRY_PATTERN, \
    BELONGS_TO_PREV_PARAGRAPH_PATTERN, SPACES_AFTER_NEWLINES_PATTERN, PAGE_TAG_ON_NEWLINE_PATTERN, PARAGRAPH_PATTERN


def generate12ids_iterator(iterations):
    ids = []
    for i in range(0, iterations):
        ids.append(randint(400000000000, 999999999999))
    ids = set(ids).__iter__()
    return ids


def wrap_paragraph(paragraph, len_symb):
    wrapped = '\n'.join(wrap(paragraph, len_symb))
    return wrapped


def convert_to_eis1600(infile, output_dir, verbose):
    if output_dir:
        path, uri = split(infile)
        uri, ext = splitext(uri)
        outfile = output_dir + '/' + uri + '.EIS1600_tmp'
    else:
        path, ext = splitext(infile)
        outfile = path + '.EIS1600_tmp'
        path, uri = split(infile)

    if verbose:
        print(f'Convert {uri} from mARkdown to EIS1600 file')

    with open(infile, 'r', encoding='utf8') as infileh:
        text = infileh.read()

    header_and_text = HEADER_END_PATTERN.split(text)
    header = header_and_text[0] + header_and_text[1]
    text = header_and_text[2]

    # fix
    text = text.replace('~\n', '\n')
    text = text.replace('\n~~', ' ')

    # text = re.sub(r'(#~:\w+: *)', r'\n\1\n\n', text)

    text = SPACES_PATTERN.sub(' ', text)

    # fix poetry
    text, n = POETRY_PATTERN.subn(r'\1', text)

    # fix page tag on newlines
    text, n = PAGE_TAG_ON_NEWLINE_PATTERN.subn(r' \1', text)

    text = text.replace('\n###', '\n\n###')
    text = text.replace('\n# ', '\n\n')

    text = NEWLINES_PATTERN.sub('\n\n', text)

    text = text.split('\n\n')

    text_updated = []

    for paragraph in text:
        if paragraph.startswith('### '):
            text_updated.append(paragraph)
        elif '%~%' in paragraph:
            paragraph = '::POETRY:: ~\n' + paragraph
            text_updated.append(paragraph)
        else:
            #paragraph = wrap_paragraph(paragraph, 60) # Not wrapping paragraphs for EIS1600 Kate/Gedit
            paragraph = '::UNDEFINED:: ~\n' + paragraph
            text_updated.append(paragraph)

    text = '\n\n'.join(text_updated)
    text, n = BELONGS_TO_PREV_PARAGRAPH_PATTERN.subn(r' \1\n', text)

    # spaces
    text, n = SPACES_AFTER_NEWLINES_PATTERN.subn('\n', text)

    # reassemble text
    final = header + '\n\n' + text

    with open(outfile, 'w', encoding='utf8') as outfileh:
        outfileh.write(final)


def insert_uids(infile, output_dir, verbose):
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

    with open(infile, 'r', encoding='utf8') as infileh:
        text = infileh.read()

    header_and_text = HEADER_END_PATTERN.split(text)
    header = header_and_text[0] + header_and_text[1]
    text = header_and_text[2]

    ids_iter = generate12ids_iterator(3000000)
    text = text.split('\n\n')
    text_updated = []

    for paragraph in text:
        if paragraph.startswith('### '):
            paragraph = paragraph.replace('###', f'#${next(ids_iter)}$')
            text_updated.append(paragraph)
        elif PARAGRAPH_PATTERN.match(paragraph):
            paragraph = f'${next(ids_iter)}$ ' + paragraph
            text_updated.append(paragraph)

    text = '\n\n'.join(text_updated)

    # reassemble text
    final = header + '\n\n' + text

    with open(outfile, 'w', encoding='utf8') as outfileh:
        outfileh.write(final)
