from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from eis1600.repositories.repo import TEXT_REPO

from eis1600.corpus_analysis.text_methods import get_text_as_list_of_mius
from eis1600.helper.CheckFileEndingActions import CheckFileEndingEIS1600OrEIS1600TMPAction
from eis1600.paragraphs.paragraph_methods import redefine_paragraphs

# split_mius_into_paragraphs OpenITI_EIS1600_Texts/data/0346Mascudi/0346Mascudi.TanbihWaIshraf/0346Mascudi.TanbihWaIshraf.Shamela0023718-ara1.EIS1600



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

    x = 0
    for i, tup in enumerate(mius_list[x:]):
        uid, miu_as_text, analyse_flag = tup
        print(i + x, uid)
        redefine_paragraphs(uid, miu_as_text)
