from typing import List, Literal

from eis1600.processing.postprocessing import write_updated_miu_to_file
from openiti.helper.ara import normalize_ara_heavy

from eis1600.toponyms.toponym_categories import TOPONYM_CATEGORIES_NOR, TOPONYM_CATEGORY_PATTERN
from eis1600.processing.preprocessing import get_yml_and_miu_df


def add_category_to_tag(tag_list: List[str], category: Literal['B', 'D', 'K', 'M', 'O', 'P', 'X']) -> List[str]:
    return [t if not t.startswith('T') else t + category for t in tag_list]


def toponym_category_annotation(file: str, test: bool) -> str:
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object)

    s_notna = df['TAGS_LISTS'].loc[df['TAGS_LISTS'].notna()].apply(lambda tag_list: ','.join(tag_list))
    toponym_idcs = s_notna.loc[s_notna.str.contains(r'T\d')].index

    for idx in toponym_idcs:
        min_idx = idx - 10 if idx - 10 > 0 else 0
        tokens = df['TOKENS'].loc[min_idx:idx]
        context = ' '.join([t for t in tokens if isinstance(t, str)])

        if TOPONYM_CATEGORY_PATTERN.search(context):
            last = TOPONYM_CATEGORY_PATTERN.findall(context)[-1]
            toponym_category = TOPONYM_CATEGORIES_NOR.get(normalize_ara_heavy(last))
        else:
            toponym_category = 'X'

        df['TAGS_LISTS'].loc[idx] = add_category_to_tag(df['TAGS_LISTS'].loc[idx], category=toponym_category)

    if test:
        output_path = str(file).replace('gold_standard_nasab', 'gold_standard_topo')
    else:
        output_path = str(file)

    with open(output_path, 'w', encoding='utf-8') as out_file_object:
        write_updated_miu_to_file(
                out_file_object, yml_handler, df[['SECTIONS', 'TOKENS', 'TAGS_LISTS']]
        )
