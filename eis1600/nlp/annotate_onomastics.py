from glob import glob
from re import compile

from eis1600.yml.YAMLHandler import YAMLHandler

from eis1600.yml.yml_handling import extract_yml_header_and_text

from eis1600.processing.postprocessing import write_updated_miu_to_file

from eis1600.nlp.utils import insert_onom_tag, insert_onomastic_tags
from eis1600.processing.preprocessing import get_yml_and_miu_df

missing_directionality_tag_pattern = compile(r'(^|\n)([^\n])')


def annotation(path: str):
    with open(path, 'r', encoding='utf-8') as miu_file_object:
        # 1. open miu file and disassemble the file to its parts
        yml_handler, df = get_yml_and_miu_df(miu_file_object)

        yml_handler.reviewed = 'NOT REVIEWED'
        df['ONOM_TAGS'] = insert_onom_tag(df)
        df['ONOMASTIC_TAGS'] = insert_onomastic_tags(df)

        # print(df['ONOM_TAGS'])
        # print(df['ONOMASTIC_TAGS'])

    with open(path.replace('12k/', ''), 'w', encoding='utf-8') as out_file_object:
        write_updated_miu_to_file(
            out_file_object, yml_handler, df[['SECTIONS', 'TOKENS', 'TAGS_LISTS', 'ONOM_TAGS', 'ONOMASTIC_TAGS']]
        )


def fix_formatting(file: str):
    with open(file, 'r', encoding='utf-8') as fh:
        yml_str, text = extract_yml_header_and_text(fh, False)
        yml_handler = YAMLHandler().from_yml_str(yml_str)

    updated_text = missing_directionality_tag_pattern.sub(r'\g<1>_ء_ \g<2>', text)
    updated_text = updated_text.replace('_ء_ #', '_ء_#')

    print(updated_text)

    with open(file, 'w', encoding='utf-8') as fh:
        fh.write(str(yml_handler) + updated_text)


def main():
    infiles = glob('12k/*_dt.EIS1600')

    for file in infiles:
        fix_formatting(file)
        annotation(file)
