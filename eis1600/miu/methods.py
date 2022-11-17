from os.path import splitext, split
from typing import Optional
from pathlib import Path

from eis1600.helper.repo import get_path_to_other_repo
from eis1600.miu.HeadingTracker import HeadingTracker
from eis1600.preprocessing.methods import get_yml_and_MIU_df, write_updated_miu_to_file
from eis1600.nlp.utils import camel2md_as_list, annotate_miu_text
from eis1600.miu.yml_handling import create_yml_header, extract_yml_header_and_text
from eis1600.markdown.re_patterns import HEADER_END_PATTERN, HEADING_PATTERN, MIU_UID_PATTERN, PAGE_TAG_PATTERN, \
    UID_PATTERN


def disassemble_text(infile: str, verbose: Optional[bool] = None) -> None:
    """Disassemble text into MIU files.

    Retrieve MIU files by disassembling the text based on the EIS1600 mARkdown.
    :param str infile: Path to the file which is to be disassembled.
    :param bool verbose: If True outputs a notification of the file which is currently processed, optional.
    """

    heading_tracker = HeadingTracker()
    path, uri = split(infile)
    uri, ext = splitext(uri)
    out_path = get_path_to_other_repo(infile, 'MIU')
    ids_file = out_path + uri + '.IDs'
    yml_file = out_path + uri + '.STATUS.yml'
    miu_dir = Path(out_path + 'MIUs/')
    uid = ''
    miu_text = ''

    if verbose:
        print(f'Disassemble {uri}')

    miu_dir.mkdir(parents=True, exist_ok=True)
    miu_uri = miu_dir.__str__() + '/' + uri + '.'

    with open(infile, 'r', encoding='utf8') as text:
        with open(ids_file, 'w', encoding='utf8') as ids_tree:
            for text_line in iter(text):
                if HEADER_END_PATTERN.match(text_line):
                    uid = 'header'
                    miu_text += text_line
                    with open(miu_uri + uid + '.EIS1600', 'w', encoding='utf8') as miu_file:
                        miu_file.write(miu_text + '\n')
                        ids_tree.write(uid + '\n')
                    miu_text = ''
                    uid = 'preface'
                    next(text)  # Skip empty line after header
                elif MIU_UID_PATTERN.match(text_line):
                    if HEADING_PATTERN.match(text_line):
                        m = HEADING_PATTERN.match(text_line)
                        heading_text = m.group('heading')
                        if PAGE_TAG_PATTERN.search(heading_text):
                            heading_text = PAGE_TAG_PATTERN.sub('', heading_text)
                        heading_tracker.track(len(m.group('level')), heading_text)
                    if miu_text:
                        # Do not create a preface MIU file if there is no preface
                        with open(miu_uri + uid + '.EIS1600', 'w', encoding='utf8') as miu_file:
                            miu_file.write(miu_text + '\n')
                            ids_tree.write(uid + '\n')
                    uid = UID_PATTERN.match(text_line).group('UID')
                    miu_text = create_yml_header(heading_tracker.get_curr_state())
                    miu_text += text_line
                else:
                    miu_text += text_line
            # last MIU needs to be written to file when the for-loop is finished
            with open(miu_uri + uid + '.EIS1600', 'w', encoding='utf8') as miu_file:
                miu_file.write(miu_text + '\n')
                ids_tree.write(uid + '\n')

    with open(yml_file, 'w', encoding='utf8') as status_file:
        status_file.write('STATUS   : DISASSEMBLED')


def reassemble_text(infile, verbose):
    path, uri = split(infile)
    uri, ext = splitext(uri)
    out_path = get_path_to_other_repo(infile, 'TEXT')
    file_path = path + '/'
    ids = []

    if verbose:
        print(f'Reassemble {uri}')

    with open(file_path + uri + '.IDs', 'r', encoding='utf-8') as ids_file:
        ids.extend([line[:-1] for line in ids_file.readlines()])

    with open(out_path + uri + '.EIS1600', 'w', encoding='utf-8') as text_file:
        with open(file_path + uri + '.YAMLDATA.yml', 'w', encoding='utf-8') as yml_data:
            for i, miu_id in enumerate(ids):
                miu_file_path = file_path + 'MIUs/' + uri + '.' + miu_id + '.EIS1600'
                yml_header, text = extract_yml_header_and_text(miu_file_path, i == 0)
                text_file.write(text)
                yml_data.write('#' + miu_id + '\n---\n' + yml_header + '\n\n')


def annotate_miu_file(path: str, tsv_path=None, output_path=None):
    def merge_tagslists(lst1, lst2):
        if lst1 is not None:
            if lst2 != '':
                lst1.append(lst2)
        else:
            if lst2 != '':
                lst1 = [lst2]
        return lst1

    if output_path is None:
        output_path = path
    if tsv_path is None:
        tsv_path = path.replace('.EIS1600', '.tsv')

    # 1. open miu file and diassemble the file to its parts
    yml_header, df = get_yml_and_MIU_df(path)

    # 2. annotate NEs and lemmatize
    df['NER_LABELS'], df['LEMMAS'] = annotate_miu_text(df)

    # 3. convert cameltools labels format to markdown format
    df['NER_TAGS'] = camel2md_as_list(df['NER_LABELS'].tolist())

    # 4. save csv file
    df.to_csv(tsv_path, index=False, sep='\t')

    # 5. merge NER tags with file tags
    df['TAGS_LISTS+NER_TAGS'] = df.apply(lambda x: merge_tagslists(x['TAGS_LISTS'], x['NER_TAGS']), axis=1)

    # 6. reconstruct the text and save it to the output file
    write_updated_miu_to_file(output_path, yml_header, df[['SECTIONS', 'TOKENS', 'TAGS_LISTS+NER_TAGS']])
