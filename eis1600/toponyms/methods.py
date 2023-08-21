from typing import List, Literal, Optional, Union
from pandas import Series
from openiti.helper.ara import normalize_ara_heavy

from eis1600.processing.preprocessing import get_yml_and_miu_df
from eis1600.processing.postprocessing import write_updated_miu_to_file
from eis1600.toponyms.toponym_categories import TOPONYM_CATEGORIES_NOR, TOPONYM_CATEGORY_PATTERN


def add_category_to_tag(
        tag_or_tag_list: Union[str, List[str]],
        category: Literal['B', 'D', 'K', 'M', 'O', 'P', 'R', 'X'],
) -> Union[str, List[str]]:
    if isinstance(tag_or_tag_list, list):
        return [t if not t.startswith('T') else 'Ü' + t + category for t in tag_or_tag_list]
    else:
        return tag_or_tag_list + category


def toponym_category_annotate_miu(s_tokens: Series, s_tags: Series) -> Series:
    """Categorize toponyms based on their context and add category to their tag.

    :param Series s_tokens: Series of tokens, needed for context analysis of the toponym.
    :param Series s_tags: Series of NER tags or TAGS_LISTS, containing the toponyms tags which shall be altered.
    :return Series: Series of altered tags.
    """

    s_notna = None
    s_new_tags = s_tags.copy()
    if s_tags.name == 'TAGS_LISTS':
        s_notna = s_tags.loc[s_tags.notna()].apply(lambda tag_list: ','.join(tag_list))
    else:
        s_notna = s_tags.loc[s_tags.notna()]

    if s_notna.empty:
        return s_tags

    toponym_idcs = s_notna.loc[s_notna.str.contains(r'T\d')].index

    for idx in toponym_idcs:
        # Get context
        min_idx = idx - 10 if idx - 10 > 0 else 0
        tokens = s_tokens.loc[min_idx:idx]
        context = ' '.join([t for t in tokens if isinstance(t, str)])

        if TOPONYM_CATEGORY_PATTERN.search(context):
            # Assign category based on last match in context
            last = TOPONYM_CATEGORY_PATTERN.findall(context)[-1]
            toponym_category = TOPONYM_CATEGORIES_NOR.get(normalize_ara_heavy(last))
        else:
            toponym_category = 'X'

        # Update tag
        s_new_tags.loc[idx] = add_category_to_tag(s_tags.loc[idx], category=toponym_category)

    return s_new_tags


def toponym_category_annotation(file: str, test: Optional[bool] = False, keep_automatic_tags: Optional[bool] = False):
    """Helper to run toponyms category annotation standalone as cmdline script.

    :param str file: Path of the miu file to annotate.
    :param bool test: Optional, indicating if the script is run with test data, defaults to false.
    :param bool keep_automatic_tags: Optional, if True keep automatic annotation (Ü-tags), defaults to False.
    """
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object, keep_automatic_tags)

    df['TAGS_LISTS'] = toponym_category_annotate_miu(df['TOKENS'], df['TAGS_LISTS'])

    if test:
        output_path = str(file).replace('gold_standard_nasab', 'gold_standard_topo')
    else:
        output_path = str(file)

    with open(output_path, 'w', encoding='utf-8') as out_file_object:
        write_updated_miu_to_file(
                out_file_object, yml_handler, df[['SECTIONS', 'TOKENS', 'TAGS_LISTS']]
        )
