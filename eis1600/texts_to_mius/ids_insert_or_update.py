from logging import ERROR, Formatter
from functools import partial
from sys import argv, exit
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from eis1600.helper.CheckFileEndingActions import CheckFileEndingEIS1600OrEIS1600TMPAction
from p_tqdm import p_uimap
from tqdm import tqdm

from eis1600.helper.chunking import split_file
from eis1600.helper.logging import setup_logger
from eis1600.repositories.repo import TEXT_REPO, get_ready_and_double_checked_files
from eis1600.texts_to_mius.subid_methods import add_ids


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to insert UIDs in EIS1600TMP file(s) and thereby converting them to final EIS1600 
            file(s).
-----
Give a single EIS1600 or EIS1600TMP file as input.

Run without input arg to batch process all double-checked and ready files from the OpenITI_EIS1600_Texts directory.
'''
            )
    arg_parser.add_argument('-D', '--debug', action='store_true')
    arg_parser.add_argument(
            'input', type=str, nargs='?',
            help='EIS1600 or EIS1600TMP file to process',
            action=CheckFileEndingEIS1600OrEIS1600TMPAction
            )
    arg_parser.add_argument(
            '--split',
            metavar="MB",
            type=int,
            default=5,
            help='split files larger or equal to indicated megabytes. '
                 'Default 4 MB. A value of -1 means no chunking.'
            )
    args = arg_parser.parse_args()

    infile = args.input
    debug = args.debug

    if infile:
        add_ids(infile)
        split_file(infile, args.split, debug)
    else:
        files_ready, files_double_checked = get_ready_and_double_checked_files(only_complete=True)
        files = files_ready + files_double_checked

        if not files:
            print(
                    'There are no more EIS1600 files to process'
            )
            exit()

        formatter = Formatter('%(message)s\n\n\n')
        logger = setup_logger('sub_ids', TEXT_REPO + 'sub_ids.log', ERROR, formatter)
        res = []
        count = 0
        if debug:
            print('\nAdd IDs')
            for i, infile in tqdm(list(enumerate(files))):
                print(i+1, infile)
                try:
                    add_ids(infile)
                except ValueError as e:
                    logger.error(f'{infile}\n{e}\n\n')
                    count += 1
            print(f'{len(files) - count}/{len(files)} processed')

            if args.split == -1:
                print("Remove splitted parts of files")
            else:
                print("Split files")
            for i, infile in tqdm(list(enumerate(files))):
                try:
                    split_file(infile, args.split, debug)
                except ValueError as e:
                    logger.error(f'{infile}\n{e}\n\n')
                    count += 1
        else:
            print('\nAdd IDs')
            res += p_uimap(add_ids, files)
            if args.split == -1:
                print("Remove splitted parts of files")
            else:
                print("Split files")
            res += p_uimap(partial(split_file, max_size=args.split, debug=debug), files)

    print('Done')

