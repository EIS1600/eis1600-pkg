from os.path import splitext, split
from typing import Optional

from pathlib import Path

from eis1600.miu.HeadingTracker import HeadingTracker
from eis1600.miu.yml_handling import create_yml_header, extract_yml_header_and_text
from eis1600.markdown.re_patterns import HEADER_END_PATTERN, HEADING_PATTERN, MIU_UID_PATTERN, UID_PATTERN


def disassemble_text(infile: str, verbose: Optional[bool] = None) -> None:
    """Disassemble text into MIU files.

    Retrieve MIU files by disassembling the text based on the EIS1600 mARkdown.
    :param str infile: Path to the file which is to be disassembled.
    :param bool verbose: If True outputs a notification of the file which is currently processed, optional.
    """

    heading_tracker = HeadingTracker()
    path, uri = split(infile)
    uri, ext = splitext(uri)
    ids_file = path + '/' + uri + '.IDs'
    miu_dir = Path(path + '/' + uri + '/')
    uid = ''
    miu_text = ''

    if verbose:
        print(f'Disassemble {uri}')

    miu_dir.mkdir(exist_ok=True)
    miu_uri = miu_dir.__str__() + '/' + uri + '.'

    with open(infile, 'r', encoding='utf8') as text:
        with open(ids_file, 'w', encoding='utf8') as ids_tree:
            for text_line in iter(text):
                if HEADER_END_PATTERN.match(text_line):
                    uid = 'header'
                    ids_tree.write(uid + '\n')
                    miu_text += text_line
                    with open(miu_uri + uid + '.EIS1600', 'w', encoding='utf8') as miu_file:
                        miu_file.write(miu_text + '\n')
                    miu_text = ''
                    uid = 'preface'
                    next(text)  # Skip empty line after header
                elif MIU_UID_PATTERN.match(text_line):
                    if HEADING_PATTERN.match(text_line):
                        m = HEADING_PATTERN.match(text_line)
                        heading_tracker.track(len(m.group('level')), m.group('heading'))
                    with open(miu_uri + uid + '.EIS1600', 'w', encoding='utf8') as miu_file:
                        miu_file.write(miu_text)
                    uid = UID_PATTERN.match(text_line).group('UID')
                    ids_tree.write(uid + '\n')
                    miu_text = create_yml_header(heading_tracker.get_curr_state())
                    miu_text += text_line
                else:
                    miu_text += text_line
            # last MIU needs to be written to file when the for-loop is finished
            with open(miu_uri + uid + '.EIS1600', 'w', encoding='utf8') as miu_file:
                miu_file.write(miu_text)


def reassemble_text(infile, verbose):
    path, uri = split(infile)
    uri, ext = splitext(uri)
    file_path = path + '/' + uri
    ids = []

    if verbose:
        print(f'Reassemble {uri}')

    with open(file_path + '.IDs', 'r', encoding='utf-8') as ids_file:
        ids.extend([line[:-1] for line in ids_file.readlines()])

    with open(file_path + '.EIS1600', 'w', encoding='utf-8') as text_file:
        with open(file_path + '.YMLDATA.yml', 'w', encoding='utf-8') as yml_data:
            for i, miu_id in enumerate(ids):
                miu_file_path = file_path + '/' + uri + '.' + miu_id + '.EIS1600'
                yml_header, text = extract_yml_header_and_text(miu_file_path, miu_id, i == 0)
                text_file.write(text)
                yml_data.write(yml_header)
