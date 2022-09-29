from textwrap import wrap
from random import randint
from os.path import split, splitext

from eis1600.miu_handling.re_patterns import HEADER_END_PATTERN, SPACES_PATTERN, NEWLINES_PATTERN, POETRY_PATTERN, \
    BELONGS_TO_PREV_PARAGRAPH_PATTERN, SPACES_AFTER_NEWLINES_PATTERN


def generate12ids(iterations):
    ids = []
    for i in range(0, iterations):
        ids.append('$%s$' % str(randint(400000000000, 999999999999)))
        # input(ids)
    ids = list(set(ids))
    # print('ids: {:,}'.format(len(ids)))
    return ids


def wrap_paragraph(paragraph, len_symb):
    wrapped = '\n'.join(wrap(paragraph, len_symb))
    return wrapped


def convert_to_eis1600(infile, output_dir, verbose):
    path, uri = split(infile)
    uri, ext = splitext(uri)
    if output_dir:
        outfile = output_dir + '/' + uri + '.EIS1600'
    else:
        outfile = '.' + path + '/' + uri + '.EIS1600'
    if verbose:
        print(f'Convert {uri} from mARkdown to EIS1600 file')


    with open(infile, 'r', encoding='utf8') as infileh:
        text = infileh.read()

    header_and_text = HEADER_END_PATTERN.split(text)
    header = header_and_text[0] + header_and_text[1]
    text = header_and_text[2]

    ids = generate12ids(3000000)

    # fix
    text = text.replace('~\n', '\n')
    text = text.replace('\n~~', ' ')

    # text = re.sub(r'(#~:\w+: *)', r'\n\1\n\n', text)

    text = SPACES_PATTERN.sub(' ', text)

    text = text.replace('\n###', '\n\n###')
    text = text.replace('\n# ', '\n\n')

    text = NEWLINES_PATTERN.sub('\n\n', text)

    # fix poetry
    text = POETRY_PATTERN.sub(r'\1\2', text)
    text = POETRY_PATTERN.sub(r'\1\2', text)
    text = POETRY_PATTERN.sub(r'\1\2', text)

    text = text.split('\n\n')

    text_updated = []

    counter = 0
    for m in text:
        counter += 1
        if m.startswith('### '):
            m = m.replace('### ', '#%s ' % ids[counter])
            text_updated.append(m)
        elif '%~%' in m:
            m = '%s ::POETRY:: ~\n' % ids[counter] + m
            text_updated.append(m)
        else:
            m = wrap_paragraph(m, 60)
            m = '%s ::UNDEFINED:: ~\n' % ids[counter] + m
            text_updated.append(m)

    text = '\n\n'.join(text_updated)
    text, n = BELONGS_TO_PREV_PARAGRAPH_PATTERN.subn(r' \1\n', text)

    # spaces
    text, n = SPACES_AFTER_NEWLINES_PATTERN.subn('\n', text)

    # reassemble text
    final = header + '\n\n' + text

    with open(outfile, 'w', encoding='utf8') as outfileh:
        outfileh.write(final)
