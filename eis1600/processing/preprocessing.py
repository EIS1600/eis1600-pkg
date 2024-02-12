from typing import Iterator, List, Optional, TextIO, Tuple, Union

from pandas import DataFrame, options
from camel_tools.tokenizers.word import simple_word_tokenize

from eis1600.markdown.markdown_patterns import MIU_TAG_PATTERN, PARAGRAPH_SIMPLE_SPLITTER_PATTERN, \
    PARAGRAPH_CAT_PATTERN, PARAGRAPH_UID_TAG_PATTERN, PARAGRAPH_SPLITTER_PATTERN, PUNCTUATION_DICT, TAG_PATTERN
from eis1600.yml.YAMLHandler import YAMLHandler
from eis1600.yml.yml_handling import extract_yml_header_and_text

options.mode.chained_assignment = None


def get_tokens_and_tags(tagged_text: str) -> Tuple[List[Union[str, None]], List[Union[str, None]]]:
    """Splits the annotated text into two lists of the same length, one containing the tokens, the other one the tags

    :param str tagged_text: the annotated text as a single str.
    :return List[str], List[str]: two lists, first contains the arabic tokens, the other one the tags.
    """
    tokens = simple_word_tokenize(tagged_text)
    ar_tokens, tags = [], []
    tag = None
    for t in tokens:
        if TAG_PATTERN.match(t):
            tag = t
        else:
            ar_tokens.append(t)
            tags.append(tag)
            tag = None

    return ar_tokens, tags


def tokenize_miu_text(
        text: str,
        simple_mARkdown: Optional[bool] = False,
        keep_automatic_tags: Optional[bool] = False
) -> Iterator[Tuple[Union[str, None], Union[str, None], List[Union[str, None]]]]:
    """Returns the MIU text as zip object of three sparse columns: sections, tokens, lists of tags.

    Takes an MIU text and returns a zip object of three sparse columns: sections, tokens, lists of tags. Elements can
    be None because of sparsity.
    :param str text: MIU text content to process.
    :param bool keep_automatic_tags: Optional, if True keep automatic annotation (Ü-tags), defaults to False.
    :return Iterator: Returns a zip object containing three sparse columns: sections, tokens, lists of tags. Elements
    can be None because of sparsity.
    """
    text_and_heading = MIU_TAG_PATTERN.split(text)
    # The indices are connected to the number of capturing group in MIU_TAG_PATTERN
    heading = text_and_heading[1]

    if simple_mARkdown:
        text_iter = PARAGRAPH_SIMPLE_SPLITTER_PATTERN.split(text_and_heading[4][:-2]).__iter__()
    else:
        text_iter = PARAGRAPH_SPLITTER_PATTERN.split(text_and_heading[4][:-2]).__iter__()
    paragraph = next(text_iter)

    sections, ar_tokens, tags = [heading], [None], [None]
    section = None

    # First item in text_iter is an empty string if there are multiple paragraphs therefore test for None
    while paragraph is not None:
        if PARAGRAPH_UID_TAG_PATTERN.fullmatch(paragraph):
            section = paragraph
        elif simple_mARkdown and PARAGRAPH_CAT_PATTERN.fullmatch(paragraph):
            section = paragraph
        else:
            # Encode \n with NEWLINE as they will be removed by the simple_word_tokenize method
            # NEWLINE is treated like a tag
            text_wo_new_lines = paragraph.replace('\n_ء_', ' NEWLINE ')
            text_wo_new_lines = text_wo_new_lines.replace('\n', ' NEWLINE ')
            # Replace %~% with HEMISTICH since the simple_word_tokenizer would return '%', '~', '%' and it would no
            # longer be recognizable as a tag
            text_wo_new_lines = text_wo_new_lines.replace('%~%', 'HEMISTICH')
            # The same for automated punctuation
            for key, val in PUNCTUATION_DICT.items():
                text_wo_new_lines = text_wo_new_lines.replace(f'_{key}_', val)
            tokens = simple_word_tokenize(text_wo_new_lines)
            tag = None
            for t in tokens:
                if TAG_PATTERN.match(t):
                    if not t.startswith('Ü') or keep_automatic_tags:
                        # Do not add automated tags to the list - they come from the csv anyway
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
            # We need to add this empty token at the end of the paragraph because in some cases we have a tag as last
            # element of the paragraph (EONOM or automated punctuation)
            sections.append(section)
            section = None
            ar_tokens.append('')
            if tag:
                tags.append(tag)
            else:
                tags.append(None)

        paragraph = next(text_iter, None)

    return zip(sections, ar_tokens, tags)


def get_yml_and_miu_df(
        miu_file_object: Union[TextIO, str],
        keep_automatic_tags: Optional[bool] = False
) -> Tuple[YAMLHandler, DataFrame]:
    """Returns YAMLHandler instance and MIU as a DataFrame containing the columns 'SECTIONS', 'TOKENS', 'TAGS_LISTS'.

    :param TextIO miu_file_object: File object of the MIU file.
    :param bool keep_automatic_tags: Optional, if True keep automatic annotation (Ü-tags), defaults to False.
    :return Tuple[YAMLHandler, DataFrame]: YAMLHandler and DataFrame containing the columns 'SECTIONS', 'TOKENS',
    'TAGS_LISTS'.
    """
    if isinstance(miu_file_object, str):
        miu_text_line_iter = iter(miu_file_object.splitlines(keepends=True))
    else:
        miu_text_line_iter = iter(miu_file_object)
    yml_str, text = extract_yml_header_and_text(miu_text_line_iter, False)
    yml_handler = YAMLHandler().from_yml_str(yml_str)
    zipped = tokenize_miu_text(text, simple_mARkdown=False, keep_automatic_tags=keep_automatic_tags)
    df = DataFrame(zipped, columns=['SECTIONS', 'TOKENS', 'TAGS_LISTS'])

    df.mask(df == '', inplace=True)

    return yml_handler, df


def get_yml(path: str) -> Tuple[str, YAMLHandler]:
    with open(path, 'r', encoding='utf-8') as miu_file_object:
        yml_str, text = extract_yml_header_and_text(miu_file_object, False)
    return path, YAMLHandler().from_yml_str(yml_str)
