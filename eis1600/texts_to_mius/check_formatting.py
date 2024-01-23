from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from logging import Formatter, INFO

from tqdm import tqdm

from eis1600.helper.CheckFileEndingActions import CheckFileEndingEIS1600OrEIS1600TMPAction
from eis1600.helper.logging import setup_logger
from eis1600.repositories.repo import TEXT_REPO, get_ready_and_double_checked_files
from eis1600.texts_to_mius.check_formatting_methods import check_formatting


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

    if infile:
        check_formatting(infile)
    else:
        files_ready, files_double_checked = get_ready_and_double_checked_files()
        files = files_ready + files_double_checked

        formatter = Formatter('%(message)s\n\n\n')
        logger = setup_logger('mal_formatted_texts', TEXT_REPO + 'mal_formatted_texts.log', INFO, formatter)
        print('Check formatting for double-checked and ready texts')

        count = 0
        for text in tqdm(files):
            try:
                check_formatting(text)
            except ValueError as e:
                count += 1
                logger.error(e)
            except FileNotFoundError:
                print(f'Missing: {text}')

        logger.info(f'\n\n\n{count}/{len(files)} files need fixing')

    print('Done')
