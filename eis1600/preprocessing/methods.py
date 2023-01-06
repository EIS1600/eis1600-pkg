from eis1600.miu.YAMLHandler import YAMLHandler

from eis1600.miu.yml_handling import extract_yml_header_and_text
from typing import Iterator, List, TextIO, Tuple, Union

import pandas as pd

pd.options.mode.chained_assignment = None

from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.utils.charsets import UNICODE_PUNCT_CHARSET
from eis1600.markdown.re_patterns import MIU_TAG_PATTERN, SECTION_PATTERN, SECTION_SPLITTER_PATTERN, TAG_PATTERN


def tokenize_miu_text(text: str) -> Iterator[Tuple[Union[str, None], str, Union[List[str], None]]]:
    """Returns the MIU text as zip object of three sparse columns: sections, tokens, lists of tags.

    Takes an MIU text and returns a zip object of three sparse columns: sections, tokens, lists of tags. Elements can
    be None because of sparsity.
    :param text: MIU text content to process.
    :return Iterator: Returns a zip object containing three sparse columns: sections, tokens, lists of tags. Elements
    can be None because of sparsity.
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
            text_wo_new_lines = paragraph.replace('\n_ء_', ' NEWLINE ')
            text_wo_new_lines = text_wo_new_lines.replace('\n', ' NEWLINE ')
            text_wo_new_lines = text_wo_new_lines.replace('%~%', 'HEMISTICH')
            tokens = simple_word_tokenize(text_wo_new_lines)
            tag = None
            for t in tokens:
                if TAG_PATTERN.match(t):
                    if not t.startswith('Ü'):
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
            if tag:
                sections.append(section)
                section = None
                ar_tokens.append('')
                tags.append(tag)

        paragraph = next(text_iter, None)

    return zip(sections, ar_tokens, tags)


def get_yml_and_MIU_df(miu_file_object: TextIO) -> (str, pd.DataFrame):
    """Returns YAMLHandler instance and MIU as a DataFrame containing the columns 'SECTIONS', 'TOKENS', 'TAGS_LISTS'.

    :param TextIO miu_file_object: File object of the MIU file.
    :return pd.DataFrame DataFrame: DataFrame containing the columns 'SECTIONS', 'TOKENS', 'TAGS_LISTS'.
    """
    yml_str, text = extract_yml_header_and_text(miu_file_object, False)
    yml = YAMLHandler().from_yml_str(yml_str)
    zipped = tokenize_miu_text(text)
    df = pd.DataFrame(zipped, columns=['SECTIONS', 'TOKENS', 'TAGS_LISTS'])

    return yml, df


def reconstruct_miu_text_with_tags(
        text_and_tags: Union[Iterator[Tuple[Union[str, None], str, Union[List[str], None]]], pd.DataFrame]
) -> str:
    """Reconstruct the MIU text from a zip object containing three columns: sections, tokens, lists of tags.

    Reconstructs the MIU text with the tags contained in the list of tags. Tags are inserted BEFORE the token.
    Section headers are inserted after an empty line ('\n\n'), followed by the text on the next line.
    :param Iterator[Tuple[Union[str, None], str, Union[List[str], None]]] text_and_tags: zip object containing three
    sparse columns: sections, tokens, lists of tags.
    :return str: The reconstructed MIU text containing all the tags.
    """
    if type(text_and_tags) is pd.DataFrame:
        text_and_tags_iter = text_and_tags.itertuples(index=False)
    else:
        text_and_tags_iter = text_and_tags.__iter__()
    heading, _, _ = next(text_and_tags_iter)
    reconstructed_text = heading
    for section, token, tags in text_and_tags_iter:
        if section:
            reconstructed_text += '\n\n' + section + '\n_ء_'
        if tags:
            reconstructed_text += ' ' + ' '.join(tags)
        if token:
            if token in UNICODE_PUNCT_CHARSET:
                reconstructed_text += token
            else:
                reconstructed_text += ' ' + token

    reconstructed_text += '\n\n'
    reconstructed_text = reconstructed_text.replace(' NEWLINE ', '\n_ء_ ')
    reconstructed_text = reconstructed_text.replace('HEMISTICH', '%~%')
    return reconstructed_text


def merge_tagslists(lst1, lst2):
    if lst1 is not None:
        if lst2 != '':
            lst1.append(lst2)
    else:
        if lst2 != '':
            lst1 = [lst2]
    return lst1


def write_updated_miu_to_file(miu_file_object: TextIO, yml: YAMLHandler, df: pd.DataFrame) -> None:
    """Write MIU file with annotations.

    :param TextIO miu_file_object: Path to the MIU file to write
    :param YAMLHandler yml: The YAMLHandler of the MIU.
    :param pd.DataFrame df: df containing the columns ['SECTIONS', 'TOKENS', 'TAGS_LISTS'] and optional 'ÜTAGS_LISTS'.
    :return None:
    """
    df_subset = None
    if not yml.is_reviewed():
        columns_of_automated_tags = ['NER_TAGS', 'DATE_TAGS']
        df['ÜTAGS'] = df['TAGS_LISTS']
        for col in columns_of_automated_tags:
            if col in df.columns:
                df['ÜTAGS'] = df.apply(lambda x: merge_tagslists(x['ÜTAGS'], x[col]), axis=1)
        df_subset = df[['SECTIONS', 'TOKENS', 'ÜTAGS']]
    else:
        df_subset = df[['SECTIONS', 'TOKENS', 'TAGS_LISTS']]

    updated_text = reconstruct_miu_text_with_tags(df_subset)

    miu_file_object.seek(0)
    miu_file_object.write(str(yml) + updated_text)
    miu_file_object.truncate()
