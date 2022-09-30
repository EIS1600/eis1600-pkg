from pathlib import Path

from eis1600.miu_handling.yml_handling import create_yml_header
from eis1600.eis1600_tags import HEADER_END_PATTERN, UID_PATTERN


def disassemble_text(file_path, uri):
    eis_file = file_path + '.EIS1600'
    ids_file = file_path + '.IDs'
    miu_dir = Path(file_path + '/')
    uid = ''
    miu_text = ''

    miu_dir.mkdir(exist_ok=True)
    miu_uri = miu_dir.__str__() + '/' + uri + '.'

    with open(eis_file, 'r', encoding='utf8') as text:
        with open(ids_file, 'w', encoding='utf8') as ids_tree:
            for text_line in iter(text):
                if HEADER_END_PATTERN.match(text_line):
                    uid = 'header'
                    miu_text += text_line
                    with open(miu_uri + uid + '.EIS1600', 'w', encoding='utf8') as miu_file:
                        miu_file.write(miu_text + '\n')
                    miu_text = ''
                    uid = 'preface'
                    next(text)  # Skip empty line after header
                elif UID_PATTERN.match(text_line):
                    with open(miu_uri + uid + '.EIS1600', 'w', encoding='utf8') as miu_file:
                        miu_file.write(miu_text)
                    uid = UID_PATTERN.match(text_line).group('UID')
                    ids_tree.write(uid + '\n')
                    miu_text = create_yml_header()
                    miu_text += text_line
                else:
                    miu_text += text_line
            # last MUI needs to be written to file when the for-loop is finished
            with open(miu_uri + uid + '.EIS1600', 'w', encoding='utf8') as miu_file:
                miu_file.write(miu_text)
