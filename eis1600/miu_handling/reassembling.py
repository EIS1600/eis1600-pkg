from os.path import split, splitext

from eis1600.miu_handling.yml_handling import extract_yml_header_and_text


def reassemble_text(infile, verbose):
    path, uri = split(infile)
    uri, ext = splitext(uri)
    file_path = path + '/' + uri
    ids = ['header', 'preface']

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
