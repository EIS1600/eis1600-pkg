from pathlib import Path
from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from pandas import DataFrame

from eis1600.corpus_analysis.text_methods import get_text_as_list_of_mius
from eis1600.helper.CheckFileEndingActions import CheckFileEndingEIS1600OrEIS1600TMPAction
from eis1600.paragraphs.paragraph_methods import redefine_paragraphs
from eis1600.repositories.repo import NEW_PARAGRAPHS_REPO, POETRY_TEST_RES_REPO, TEXT_REPO


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description=''
    )
    arg_parser.add_argument(
            'input', type=str, nargs='1',
            help='EIS1600 or EIS1600TMP file to process',
            action=CheckFileEndingEIS1600OrEIS1600TMPAction
    )

    args = arg_parser.parse_args()

    # TODO ATM it only works with a single file so you can test how the output will look like. When this routine is
    #  ready for use, it should be part of the incorporate new files or ids_insert_or_update routine
    infile = args.input

    meta_data_header, mius_list = get_text_as_list_of_mius(infile)
    data = []
    mius = []
    x = 0
    for i, tup in enumerate(mius_list[x:]):
        uid, miu_as_text, analyse_flag = tup
        print(i + x, uid)
        poetry_tests_list, miu = redefine_paragraphs(uid, miu_as_text)
        mius.append(miu)
        data += [(uid, dict_per_paragraph['text'], dict_per_paragraph['label'], dict_per_paragraph['score']) for
               dict_per_paragraph in poetry_tests_list]

    outfile = infile.replace(TEXT_REPO, NEW_PARAGRAPHS_REPO)
    path_parts = outfile.split('/')
    Path('/'.join(path_parts[:-1])).mkdir(exist_ok=True, parents=True)
    with open(outfile, 'w', encoding='utf-8') as fh:
        fh.write(meta_data_header + ''.join(mius))
    poetry_test_res_path = infile.replace(TEXT_REPO, POETRY_TEST_RES_REPO).replace('EIS1600', 'csv')
    path_parts = poetry_test_res_path.split('/')
    Path('/'.join(path_parts[:-1])).mkdir(exist_ok=True, parents=True)
    DataFrame(data, columns=['uid', 'text', 'meter', 'score']).to_csv(poetry_test_res_path)
