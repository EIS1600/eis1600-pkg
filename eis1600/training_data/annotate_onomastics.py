from glob import glob
from typing import List, Union

from tqdm import tqdm

from eis1600.nlp.utils import insert_onom_tag, insert_onomastic_tags
from eis1600.processing.postprocessing import write_updated_miu_to_file
from eis1600.processing.preprocessing import get_yml_and_miu_df
from eis1600.training_data.online_editor_files import fix_formatting


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

    with open(path.replace('12k/', '12k_copy/'), 'w', encoding='utf-8') as out_file_object:
        write_updated_miu_to_file(
                out_file_object, yml_handler, df[['SECTIONS', 'TOKENS', 'TAGS_LISTS', 'ONOM_TAGS', 'ONOMASTIC_TAGS']],
                forced_re_annotation=True
        )


def main():
    infiles = glob('12k/*.EIS1600')

    x = 869
    for idx, file in tqdm(list(enumerate(infiles[x:]))):
        try:
            fix_formatting(file)
        except ValueError:
            print(idx + x, file)
        except Exception as e:
            print(idx + x, file)
            print(e)

        annotation(file)
