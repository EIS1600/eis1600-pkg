import sys
import logging
from tqdm import tqdm
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from eis1600.helper.CheckFileEndingActions import CheckFileEndingEIS1600OrEIS1600TMPAction
from eis1600.helper.logging import setup_logger
from eis1600.repositories.repo import TEXT_REPO, get_ready_and_double_checked_files
from eis1600.texts_to_mius.check_formatting_methods import check_formatting


def main():
    arg_parser = ArgumentParser(
            prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
            description=''
    )
    arg_parser.add_argument(
            'input', type=str, nargs='?',
            help='EIS1600 or EIS1600TMP file to process',
            action=CheckFileEndingEIS1600OrEIS1600TMPAction
    )
    arg_parser.add_argument(
            '--parts', action='store_true',
            help='check part files instead of original in case file is splitted',
    )

    args = arg_parser.parse_args()

    infile = args.input

    if infile:
        check_formatting(infile)
    else:
        files_ready, files_double_checked = get_ready_and_double_checked_files(only_complete=not args.parts)
        files = files_ready + files_double_checked

        formatter = logging.Formatter('%(message)s\n\n\n')
        logger = setup_logger(
            name='mal_formatted_texts',
            log_file=TEXT_REPO + 'mal_formatted_texts.log',
            level=logging.INFO,
            formatter=formatter,
            add_stderr=True
        )
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
