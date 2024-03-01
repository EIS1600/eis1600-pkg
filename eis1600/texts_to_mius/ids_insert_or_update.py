from os import remove
from os.path import splitext, getsize, exists
from logging import ERROR, Formatter
from itertools import groupby
from functools import partial
from typing import List
from sys import argv, exit
from re import search
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from eis1600.helper.CheckFileEndingActions import CheckFileEndingEIS1600OrEIS1600TMPAction
from p_tqdm import p_uimap
from tqdm import tqdm

from eis1600.helper.logging import setup_logger
from eis1600.markdown.markdown_patterns import HEADER_END_PATTERN, MISSING_DIRECTIONALITY_TAG_PATTERN, \
    FIRST_LEVEL_HEADING_PATTERN
from eis1600.repositories.repo import TEXT_REPO, get_ready_and_double_checked_files, SPLITTED_PART_NAME_INFIX, \
    get_part_filepath
from eis1600.texts_to_mius.subid_methods import add_ids, pre_clean_text
from eis1600.texts_to_mius.check_formatting_methods import check_file_split


def resize_chunks(chunks: List[str], n: int = 400_000) -> List[str]:
    """ If there are chunks with size smaller than n, merge them in groups to avoid having too many tiny files.

    :param list chunks: chunks of text.
    :param int n: soft maximum number of characters per chunk.
    :return list: modified chunking.
    """
    new_chunks = []
    aux = ""
    for chunk in chunks:
        if len(aux) > n:
            new_chunks.append(aux)
            aux = ""
        if aux:
            aux += "\n\n"
        aux += chunk
    if aux:
        # if the last piece of text is too small, add it to the last
        if len(aux) < n // 2 and new_chunks:
            new_chunks[-1] += f"\n\n{aux}"
        else:
            new_chunks.append(aux)
    return new_chunks


def split_file(infile: str, max_size: int, debug: bool = False):
    """ Break files larger or equal MB indicated in max_size into parts so that they can be processed separately.
    All chunks will share the same header.


    :param str infile: Path of the file to split.
    :param int max_size: Maximum size of file in megabytes. If file is larger, it is splitted in parts.
        I max_size is -1, do not split.
    :param bool debug: show warnings.
    :return None:
    """
    if SPLITTED_PART_NAME_INFIX in infile:
        return

    file_path, file_ext = splitext(infile)

    # remove previous splitting
    i = 1
    while exists(old_part_file := get_part_filepath(file_path, i, file_ext)):
        remove(old_part_file)
        i += 1

    if max_size == -1:
        return

    if (getsize(infile) >> 20) < max_size:
        return

    with open(infile, 'r', encoding='utf8') as infile_h:
        text = infile_h.read()

        header_and_text = HEADER_END_PATTERN.split(text)
        header = header_and_text[0] + header_and_text[1]
        text = header_and_text[2].lstrip('\n')  # Ignore new lines after #META#Header#End#
        text = pre_clean_text(text)
        text = MISSING_DIRECTIONALITY_TAG_PATTERN.sub('\g<1>_ء_ \g<2>', text)

        paragraphs = text.split('\n\n')

        blocks = [(k, list(gr)) for k, gr in groupby(
            paragraphs,
            lambda s: bool(search(FIRST_LEVEL_HEADING_PATTERN, s))
        )]

        chunks = []

        aux = []
        for is_fst_header, paragraphs in blocks:
            if is_fst_header:
                #if debug and len(paragraphs) > 1:
                #    multiple_headings = "\n\n".join(paragraphs)
                #    print(f"\nfile {infile} has consecutive first level multiple_headings:"
                #          f"\n\n{multiple_headings}")
                if len(aux) > 1:
                    chunks.append("\n\n".join(aux))
                    aux = []
            for paragraph in paragraphs:
                aux.append(paragraph)

        if aux:
            chunks.append("\n\n".join(aux))

        # to avoid having too many small files
        chunks = resize_chunks(chunks)

        # there is only one first level heading in all the file
        if len(chunks) > 1:

            for i, chunk in enumerate(chunks, 1):

                final = header + '\n\n' + chunk
                if final[-1] != '\n':
                    final += '\n'

                outfile_path = get_part_filepath(file_path, i, file_ext)
                with open(outfile_path, 'w', encoding='utf8') as outfp:
                    outfp.write(final)

            check_file_split(infile, debug)


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



