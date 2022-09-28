import re
from camel_tools.tokenizers.word import simple_word_tokenize
from eis1600.eis1600_tags import TAG_PATTERN


SLASH_PATTERN = re.compile(r'[/\\()[\]{}|]')
NEWLINE_PATTERN = re.compile(r'\n')


def preprocess(text):
    text_wo_new_lines, n = NEWLINE_PATTERN.subn(' NEWLINE ', text)
    tokens = simple_word_tokenize(text_wo_new_lines)
    ar_tokens, tags = [], []
    tag = None
    for t in tokens:
        if TAG_PATTERN.match(t):
            if tag:
                tag = ' '.join([tag, t])
            else:
                tag = t
        else:
            ar_tokens.append(t)
            tags.append(tag)
            tag = None
    if tag:
        ar_tokens.append('')
        tags.append(tag)

    return zip(ar_tokens, tags)
