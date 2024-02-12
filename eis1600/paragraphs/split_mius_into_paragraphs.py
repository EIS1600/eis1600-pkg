from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from pandas import DataFrame, concat

from eis1600.corpus_analysis.text_methods import get_text_as_list_of_mius
from eis1600.helper.CheckFileEndingActions import CheckFileEndingEIS1600OrEIS1600TMPAction
from eis1600.paragraphs.paragraph_methods import redefine_paragraphs
from eis1600.repositories.repo import TEXT_REPO


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description=''
    )
    arg_parser.add_argument(
            'input', type=str, nargs='?',
            help='EIS1600 or EIS1600TMP file to process',
            action=CheckFileEndingEIS1600OrEIS1600TMPAction
    )

    args = arg_parser.parse_args()

    infile = args.input
    infile = TEXT_REPO + 'Footnotes_noise example.EIS1600'

    mius_list = get_text_as_list_of_mius(infile)
    columns = ['uid', 'text', 'meter', 'score']
    poetry_test_res = DataFrame(None, columns=columns)
    x = 0
    for i, tup in enumerate(mius_list[x:]):
        uid, miu_as_text, analyse_flag = tup
        print(i + x, uid)
        poetry_tests_list = redefine_paragraphs(uid, miu_as_text)
        data = [(uid, dict_per_paragraph['text'], dict_per_paragraph['label'], dict_per_paragraph['score']) for
               dict_per_paragraph in poetry_tests_list]
        tmp = DataFrame(data, columns=columns)
        if poetry_test_res.empty:
            poetry_test_res = tmp
        else:
            poetry_test_res = concat([poetry_test_res, tmp])

    poetry_test_res.to_csv(TEXT_REPO + 'Footnotes_noise example_poetry_test_res.csv')
