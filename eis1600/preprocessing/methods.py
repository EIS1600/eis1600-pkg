from typing import Iterator, List, Tuple, Union

from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.utils.charsets import UNICODE_PUNCT_CHARSET
from eis1600.markdown.re_patterns import MIU_TAG_PATTERN, SECTION_PATTERN, SECTION_SPLITTER_PATTERN, TAG_PATTERN


def preprocess(text: str) -> Iterator[Tuple[Union[str, None], str, Union[List[str], None]]]:
    """

    :param text: MIU text content to process.
    :return Iterator: Returns a zip object containing three columns: sections, tokens, lists of tags. Elements can be
    None.
    """
    text_and_heading = MIU_TAG_PATTERN.split(text)
    heading = text_and_heading[1]
    text_iter = SECTION_SPLITTER_PATTERN.split(text_and_heading[3][:-2]).__iter__()
    paragraph = next(text_iter)

    sections, ar_tokens, tags = [heading], [None], [None]
    section = None

    # First item in text_iter is an empty string if there are multiple paragraphs therefore test for None
    while paragraph is not None:
        if SECTION_PATTERN.fullmatch(paragraph):
            section = paragraph
        else:
            # Encode \n with NEWLINE as they will be removed by the simple_word_tokenize method
            # NEWLINE is treated like a tag
            text_wo_new_lines = paragraph.replace('\n', ' NEWLINE ')
            tokens = simple_word_tokenize(text_wo_new_lines)
            tag = None
            for t in tokens:
                if TAG_PATTERN.match(t):
                    # There might be multiple tags in front of a token - Page, NEWLINE, NER tag, ...
                    if tag:
                        tag.append(t)
                    else:
                        tag = [t]
                else:
                    sections.append(section)
                    section = None
                    ar_tokens.append(t)
                    tags.append(tag)
                    tag = None
            if tag:
                sections.append(section)
                section = None
                ar_tokens.append('')
                tags.append(tag)

        paragraph = next(text_iter, None)

    return zip(sections, ar_tokens, tags)


def reconstruct_text_with_tags(text_and_tags: Iterator[Tuple[Union[str, None], str, Union[List[str], None]]]) -> str:
    """
    
    :param text_and_tags:
    :return:
    """
    text_and_tags_iter = text_and_tags.__iter__()
    heading, _, _ = next(text_and_tags_iter)
    reconstructed_text = heading
    for section, token, tags in text_and_tags_iter:
        if section:
            reconstructed_text += '\n\n' + section + '\n'
        if tags:
            reconstructed_text += ' ' + ' '.join(tags)
        if token:
            if token in UNICODE_PUNCT_CHARSET:
                reconstructed_text += token
            else:
                reconstructed_text += ' ' + token

    reconstructed_text += '\n\n'
    reconstructed_text = reconstructed_text.replace(' NEWLINE ', '\n')
    return reconstructed_text
