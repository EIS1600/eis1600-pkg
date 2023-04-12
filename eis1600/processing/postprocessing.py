from typing import Iterator, List, TextIO, Tuple, Union

import pandas as pd
from camel_tools.utils.charsets import UNICODE_PUNCT_CHARSET

from eis1600.helper.markdown_patterns import ENTITY_TAGS_PATTERN
from eis1600.miu.YAMLHandler import YAMLHandler
from eis1600.miu.yml_handling import add_annotated_entities_to_yml


def get_text_with_annotation_only(
        text_and_tags: Union[Iterator[Tuple[Union[str, None], str, Union[List[str], None]]], pd.DataFrame]
) -> str:
    """Returns the MIU text only with annotation tags, not page tags and section tags.

    Returns the MIU text only with annotation tags contained in the list of tags. Tags are inserted BEFORE the token.
    Section headers and other tags - like page tags - are ignored.
    :param Iterator[Tuple[Union[str, None], str, Union[List[str], None]]] text_and_tags: zip object containing three
    sparse columns: sections, tokens, lists of tags.
    :return str: The MIU text with annotation only.
    """
    if type(text_and_tags) is pd.DataFrame:
        text_and_tags_iter = text_and_tags.itertuples(index=False)
    else:
        text_and_tags_iter = text_and_tags.__iter__()
    next(text_and_tags_iter)
    text_with_annotation_only = ''
    for section, token, tags in text_and_tags_iter:
        if isinstance(tags, list):
            entity_tags = [tag for tag in tags if ENTITY_TAGS_PATTERN.fullmatch(tag)]
            text_with_annotation_only += ' ' + ' '.join(entity_tags)
        if pd.notna(token):
            text_with_annotation_only += ' ' + token

    return text_with_annotation_only


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
    # TODO NASAB tag after token
    for section, token, tags in text_and_tags_iter:
        if pd.notna(section):
            reconstructed_text += '\n\n' + section + '\n_ء_'
        if isinstance(tags, list):
            reconstructed_text += ' ' + ' '.join(tags)
        if pd.notna(token):
            if token in UNICODE_PUNCT_CHARSET:
                reconstructed_text += token
            else:
                reconstructed_text += ' ' + token

    reconstructed_text += '\n\n'
    reconstructed_text = reconstructed_text.replace(' NEWLINE ', '\n_ء_ ')
    reconstructed_text = reconstructed_text.replace('HEMISTICH', '%~%')
    return reconstructed_text


def merge_tagslists(lst1, lst2):
    if isinstance(lst1, list):
        if pd.notna(lst2):
            lst1.append(lst2)
    else:
        if pd.notna(lst2):
            lst1 = [lst2]
    return lst1


def write_updated_miu_to_file(miu_file_object: TextIO, yml_handler: YAMLHandler, df: pd.DataFrame) -> None:
    """Write MIU file with annotations and populated YAML header.

    :param TextIO miu_file_object: Path to the MIU file to write
    :param YAMLHandler yml_handler: The YAMLHandler of the MIU.
    :param pd.DataFrame df: df containing the columns ['SECTIONS', 'TOKENS', 'TAGS_LISTS'] and optional 'ÜTAGS_LISTS'.
    :return None:
    """
    if not yml_handler.is_reviewed():
        columns_of_automated_tags = ['NER_TAGS', 'DATE_TAGS', 'NASAB_TAGS']
        df['ÜTAGS'] = df['TAGS_LISTS']
        for col in columns_of_automated_tags:
            if col in df.columns:
                df['ÜTAGS'] = df.apply(lambda x: merge_tagslists(x['ÜTAGS'], x[col]), axis=1)
        df_subset = df[['SECTIONS', 'TOKENS', 'ÜTAGS']]
    else:
        df_subset = df[['SECTIONS', 'TOKENS', 'TAGS_LISTS']]

    add_annotated_entities_to_yml(df_subset, yml_handler, miu_file_object.name)
    updated_text = reconstruct_miu_text_with_tags(df_subset)

    miu_file_object.seek(0)
    miu_file_object.write(str(yml_handler) + updated_text)
    miu_file_object.truncate()
