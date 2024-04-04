from typing import Iterator, List, Optional, TextIO, Tuple, Union

from os import path
from pandas import DataFrame, notna

from eis1600.markdown.markdown_patterns import ENTITY_TAGS_PATTERN, PUNCTUATION_DICT
from eis1600.yml.YAMLHandler import YAMLHandler
from eis1600.yml.yml_handling import add_annotated_entities_to_yml


def get_text_with_annotation_only(
        text_and_tags: Union[Iterator[Tuple[Union[str, None], str, Union[List[str], None]]], DataFrame]
) -> str:
    """Returns the MIU text only with annotation tags, not page tags and section tags.

    Returns the MIU text only with annotation tags contained in the list of tags. Tags are inserted BEFORE the token.
    Section headers and other tags - like page tags - are ignored.
    :param Iterator[Tuple[Union[str, None], str, Union[List[str], None]]] text_and_tags: zip object containing three
    sparse columns: sections, tokens, lists of tags.
    :return str: The MIU text with annotation only.
    """
    if type(text_and_tags) is DataFrame:
        text_and_tags_iter = text_and_tags.itertuples(index=False)
    else:
        text_and_tags_iter = text_and_tags.__iter__()
    next(text_and_tags_iter)
    text_with_annotation_only = ''
    for section, token, tags in text_and_tags_iter:
        if isinstance(tags, list):
            entity_tags = [tag for tag in tags if ENTITY_TAGS_PATTERN.fullmatch(tag)]
            text_with_annotation_only += ' ' + ' '.join(entity_tags)
        if notna(token):
            text_with_annotation_only += ' ' + token

    return text_with_annotation_only


def reconstruct_miu_text_with_tags(
        text_and_tags: Union[Iterator[Tuple[Union[str, None], str, Union[List[str], None]]], DataFrame]
) -> str:
    """Reconstruct the MIU text from a zip object containing three columns: sections, tokens, lists of tags.

    Reconstructs the MIU text with the tags contained in the list of tags. Tags are inserted BEFORE the token.
    Section headers are inserted after an empty line ('\n\n'), followed by the text on the next line.
    :param Iterator[Tuple[Union[str, None], str, Union[List[str], None]]] text_and_tags: zip object containing three
    sparse columns: sections, tokens, lists of tags.
    :return str: The reconstructed MIU text containing all the tags.
    """
    if type(text_and_tags) is DataFrame:
        text_and_tags_iter = text_and_tags.itertuples(index=False)
    else:
        text_and_tags_iter = text_and_tags.__iter__()
    heading, _, _ = next(text_and_tags_iter)
    reconstructed_text = heading
    for section, token, tags in text_and_tags_iter:
        if notna(section):
            if token and notna(token):
                reconstructed_text += '\n\n' + section + '\n_ء_'
            else:
                reconstructed_text += '\n\n' + section

        if isinstance(tags, list):
            reconstructed_text += ' ' + ' '.join(tags)
        elif tags is not None:
            print("df['TAGS_LISTS'] must be list but is " + type(tags))
            print(tags)
            raise TypeError
        if notna(token):
            reconstructed_text += ' ' + token

    reconstructed_text += '\n\n'

    # Replace tag replacements with their actual EIS1600 tags (we use PERIOD, ARCOMMA and COLON while processing
    # because the simple_word_tokenizer would return 3 tokens '_', '.', '_' and the tags are no longer recognized.
    reconstructed_text = reconstructed_text.replace(' NEWLINE ', '\n_ء_ ')
    reconstructed_text = reconstructed_text.replace('HEMISTICH', '%~%')
    for key, val in PUNCTUATION_DICT.items():
        reconstructed_text = reconstructed_text.replace(val, '_' + key + '_')
    return reconstructed_text


def merge_tagslists(row, key):
    if isinstance(row['TAGS_LISTS'], list) and row[key] and notna(row[key]):
        row['TAGS_LISTS'].append(row[key])
    elif row[key] and notna(row[key]):
        row['TAGS_LISTS'] = [row[key]]
    return row['TAGS_LISTS']


def merge_tagslists_without_duplicates(row, key):
    if isinstance(row['TAGS_LISTS'], list) and row[key] and notna(row[key]):
        row['TAGS_LISTS'].extend(row[key])
        return list(set(row['TAGS_LISTS']))
    elif row[key] and notna(row[key]):
        return row[key]
    else:
        return None


def write_updated_miu_to_file(
        miu_file_object: TextIO,
        yml_handler: YAMLHandler,
        df: DataFrame,
        target_columns: tuple[str],
        forced_re_annotation: Optional[bool] = False,
        add_annotations_to_yml: Optional[bool] = True
) -> None:
    """Write MIU file with annotations and populated YAML header.

    :param TextIO miu_file_object: Path to the MIU file to write
    :param YAMLHandler yml_handler: The YAMLHandler of the MIU.
    :param DataFrame df: df containing the columns ['SECTIONS', 'TOKENS', 'TAGS_LISTS'].
    :param tuple target_columns: columns to include in reconstructed text.
    :param bool forced_re_annotation: some annotation was added to already existing annotation, therefore merge new
    annotation into TAGS_LISTS.
    :param bool add_annotations_to_yml: add all annotations to yml header.
    :return None:
    """
    if not yml_handler.is_reviewed() or forced_re_annotation:
        for col in target_columns:
            if col in df.columns:
                df['TAGS_LISTS'] = df.apply(merge_tagslists, key=col, axis=1)
        df_subset = df[['SECTIONS', 'TOKENS', 'TAGS_LISTS']]
    else:
        df_subset = df[['SECTIONS', 'TOKENS', 'TAGS_LISTS']]

    if add_annotations_to_yml:
        add_annotated_entities_to_yml(df_subset, yml_handler, path.realpath(miu_file_object.name), df_subset)
    updated_text = reconstruct_miu_text_with_tags(df_subset)

    miu_file_object.seek(0)
    miu_file_object.write(str(yml_handler) + updated_text)
    miu_file_object.truncate()
