from eis1600.helper.entity_tags import get_entity_tags_df
from eis1600.helper.markdown_methods import get_yrs_tag_value
from eis1600.miu.YAMLHandler import YAMLHandler

from eis1600.miu.yml_handling import extract_yml_header_and_text
from typing import Dict, Iterator, List, Optional, TextIO, Tuple, Union

import pandas as pd

from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.utils.charsets import UNICODE_PUNCT_CHARSET
from eis1600.helper.markdown_patterns import ENTITY_TAGS_PATTERN, MIU_TAG_PATTERN, SECTION_PATTERN, \
    SECTION_SPLITTER_PATTERN, TAG_PATTERN


pd.options.mode.chained_assignment = None


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


def tokenize_miu_text(text: str) -> Iterator[Tuple[Union[str, None], Union[str, None], List[Union[str, None]]]]:
    """Returns the MIU text as zip object of three sparse columns: sections, tokens, lists of tags.

    Takes an MIU text and returns a zip object of three sparse columns: sections, tokens, lists of tags. Elements can
    be None because of sparsity.
    :param text: MIU text content to process.
    :return Iterator: Returns a zip object containing three sparse columns: sections, tokens, lists of tags. Elements
    can be None because of sparsity.
    """
    text_and_heading = MIU_TAG_PATTERN.split(text)
    # The indices are connected to the number of capturing group in MIU_TAG_PATTERN
    heading = text_and_heading[1]
    text_iter = SECTION_SPLITTER_PATTERN.split(text_and_heading[4][:-2]).__iter__()
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


def get_yml_and_miu_df(miu_file_object: TextIO) -> (str, pd.DataFrame):
    """Returns YAMLHandler instance and MIU as a DataFrame containing the columns 'SECTIONS', 'TOKENS', 'TAGS_LISTS'.

    :param TextIO miu_file_object: File object of the MIU file.
    :return DataFrame: DataFrame containing the columns 'SECTIONS', 'TOKENS', 'TAGS_LISTS'.
    """
    yml_str, text = extract_yml_header_and_text(miu_file_object, False)
    yml_handler = YAMLHandler().from_yml_str(yml_str)
    zipped = tokenize_miu_text(text)
    df = pd.DataFrame(zipped, columns=['SECTIONS', 'TOKENS', 'TAGS_LISTS'])

    df.mask(df == '', inplace=True)

    return yml_handler, df


def add_to_entities_dict(entities_dict: Dict, cat: str, entity: Union[str, int], tag: Optional[str]) -> None:
    """Add a tagged entity to the respective list in the entities_dict.

    :param Dict entities_dict: Dict containing previous tagged entities.
    :param str cat: Category of the entity.
    :param Union[str|int] entity: Entity - might be int if entity is a date, otherwise str.
    :param str tag: Onomastic classification, used to differentiate between onomastic elements.
    """
    cat = cat.lower()
    if tag:
        tag = tag.lower()
    if cat in entities_dict.keys():
        if cat == 'onomastics' and tag:
            if tag in entities_dict[cat].keys():
                entities_dict[cat][tag].append(entity)
            else:
                entities_dict[cat][tag] = [entity]
        else:
            entities_dict[cat].append(entity)
    else:
        if cat == 'onomastics' and tag:
            entities_dict[cat] = {}
            entities_dict[cat][tag] = [entity]
        else:
            entities_dict[cat] = [entity]


def add_annotated_entities_to_yml(df: pd.DataFrame, yml_handler: YAMLHandler, filename: str) -> None:
    """Populates YAMLHeader with annotated entities.

    :param DataFrame df: DataFrame of the MIU.
    :param YAMLHandler yml_handler: YAMLHandler of the MIU.
    :param str filename: Filename of the current MIU (used in error msg.)
    """
    text_with_tags = get_text_with_annotation_only(df)
    entity_tags_df = get_entity_tags_df()
    entities_dict = {}

    m = ENTITY_TAGS_PATTERN.search(text_with_tags)
    while m:
        tag = m.group('entity')
        length = int(m.group('length'))
        entity = text_with_tags[m.end():].split(maxsplit=length)[:length]

        cat = entity_tags_df.loc[entity_tags_df['TAG'].str.fullmatch(tag), 'CATEGORY'].iloc[0]
        if cat == 'DATES' or cat == 'AGE':
            try:
                entity = get_yrs_tag_value(m.group(0))
            except ValueError:
                print(f'Tag is neither year nor age: {m.group(0)}\nCheck: {filename}')
                return

            add_to_entities_dict(entities_dict, cat, entity, tag)
        else:
            add_to_entities_dict(entities_dict, cat, ' '.join(entity), tag)

        m = ENTITY_TAGS_PATTERN.search(text_with_tags, m.end())

    yml_handler.add_tagged_entities(entities_dict)


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
            if token in UNICODE_PUNCT_CHARSET:
                text_with_annotation_only += token
            else:
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
