from eis1600.miu_handling.re_patterns import MIU_HEADER_PATTERN, NEWLINES_PATTERN
from importlib.resources import read_text


yml_template = read_text('eis1600.miu_handling', 'yaml_template.yml')


def create_yml_header():
    yml_header = yml_template
    # TODO: populate template with MIU related information
    return yml_header + '\n'


def extract_yml_header_and_text(miu_file, miu_id, is_header):
    with open(miu_file, 'r', encoding='utf-8') as file:
        text = ''
        miu_yml_header = ''
        for line in iter(file):
            if MIU_HEADER_PATTERN.match(line):
                # Omit the #MIU#Header# line as it is only needed inside the MIU.EIS1600 file, but not in YMLDATA.yml
                next(file)
                line = next(file)
                miu_yml_header = '#' + miu_id + '\n---\n'
                while not MIU_HEADER_PATTERN.match(line):
                    miu_yml_header += line
                    line = next(file)
                # Skip empty line after #MIU#Header#
                next(file)
            else:
                text += line
            # Replace new lines which separate YAML header from text
            if not is_header:
                text, n = NEWLINES_PATTERN.subn('\n\n', text)
        return miu_yml_header, text


def update_yml_header():
    # TODO: update YAML header with MIU related information from automated analyses and manual tags
    pass
