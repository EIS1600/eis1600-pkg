from eis1600.markdown.markdown_patterns import MISSING_DIRECTIONALITY_TAG_PATTERN
from eis1600.texts_to_mius.subid_methods import pre_clean_text, update_ids
from eis1600.yml.yml_handling import extract_yml_header_and_text
from eis1600.yml.YAMLHandler import YAMLHandler


def fix_formatting(file: str):
    with open(file, 'r+', encoding='utf-8') as fh:
        yml_str, text = extract_yml_header_and_text(fh, False)
        yml_handler = YAMLHandler().from_yml_str(yml_str)

        updated_text = text.replace('#', '_ء_#')
        updated_text = pre_clean_text(updated_text)
        updated_text = MISSING_DIRECTIONALITY_TAG_PATTERN.sub('\g<1>_ء_ \g<2>', updated_text)
        updated_text = update_ids(updated_text)

        fh.seek(0)
        fh.write(str(yml_handler) + updated_text)
        fh.truncate()
