from glob import glob
from typing import List, Union

from eis1600.texts_to_mius.subid_methods import pre_clean_text, update_ids

from eis1600.markdown.markdown_patterns import MISSING_DIRECTIONALITY_TAG_PATTERN
from eis1600.nlp.utils import insert_onom_tag, insert_onomastic_tags
from eis1600.processing.postprocessing import write_updated_miu_to_file
from eis1600.processing.preprocessing import get_yml_and_miu_df
from eis1600.yml.yml_handling import extract_yml_header_and_text
from eis1600.yml.YAMLHandler import YAMLHandler


def remove_nasab_tag(tags_list: Union[None, List[str]]):
    if tags_list and 'NASAB' in tags_list:
        tags_list.remove('NASAB')
    return tags_list


def annotation(path: str):
    with open(path, 'r', encoding='utf-8') as miu_file_object:
        # 1. open miu file and disassemble the file to its parts
        yml_handler, df = get_yml_and_miu_df(miu_file_object)

        df['ONOM_TAGS'] = insert_onom_tag(df)
        df['ONOMASTIC_TAGS'] = insert_onomastic_tags(df)
        df['TAGS_LISTS'] = df['TAGS_LISTS'].apply(remove_nasab_tag)

    with open(path.replace('12k/', ''), 'w', encoding='utf-8') as out_file_object:
        write_updated_miu_to_file(
                out_file_object, yml_handler, df[['SECTIONS', 'TOKENS', 'TAGS_LISTS', 'ONOM_TAGS', 'ONOMASTIC_TAGS']],
                forced_re_annotation=True
        )


def fix_formatting(file: str):
    with open(file, 'r', encoding='utf-8') as fh:
        yml_str, text = extract_yml_header_and_text(fh, False)
        yml_handler = YAMLHandler().from_yml_str(yml_str)

    updated_text = text.replace('#', '_ء_#')
    updated_text = pre_clean_text(updated_text)
    updated_text = MISSING_DIRECTIONALITY_TAG_PATTERN.sub('\g<1>_ء_ \g<2>', updated_text)
    updated_text = update_ids(updated_text)

    with open(file, 'w', encoding='utf-8') as fh:
        fh.write(str(yml_handler) + updated_text)


def main():
    infiles = glob('12k/*_dt.EIS1600')

    for file in infiles:
        fix_formatting(file)
        annotation(file)
