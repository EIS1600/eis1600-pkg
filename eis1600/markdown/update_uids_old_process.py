from os.path import split, splitext

from eis1600.markdown.UIDs import UIDs
from typing import Optional

import sys
import os
from argparse import ArgumentParser, Action, RawDescriptionHelpFormatter
from multiprocessing import Pool

from eis1600.helper.repo import get_files_from_eis1600_dir, write_to_readme, read_files_from_readme
from eis1600.markdown.re_patterns import BIO_CHR_TO_NEWLINE_PATTERN, HEADER_END_PATTERN, HEADING_OR_BIO_PATTERN, \
    MIU_LIGHT_OR_EIS1600_PATTERN, NEWLINES_CROWD_PATTERN, UID_PATTERN


class CheckFileEndingAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and os.path.isfile(input_arg):
            filepath, fileext = os.path.splitext(input_arg)
            if fileext != '.EIS1600':
                parser.error('You need to input an EIS1600 file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, None)


def xx_update_uids(infile: str, verbose: Optional[bool] = False) -> None:
    """Updates a text with missing UIDs.

    :param str infile: Path of the file to update UIDs in.
    :param bool verbose: If True outputs a notification of the file which is currently processed, defaults to False.
    :return None:
    """

    path, ext = splitext(infile)
    outfile = path + '.EIS1600'
    path, uri = split(infile)

    if verbose:
        print(f'Update UIDs in {uri}')

    with open(infile, 'r', encoding='utf8') as infile_h:
        text = infile_h.read()

    text = BIO_CHR_TO_NEWLINE_PATTERN.sub(r'\1\n\2', text)
    header_and_text = HEADER_END_PATTERN.split(text)
    header = header_and_text[0] + header_and_text[1]
    text = header_and_text[2]
    text = NEWLINES_CROWD_PATTERN.sub('\n\n', text)
    text = text.split('\n\n')
    text_updated = []

    used_ids = []

    for paragraph in text:
        if UID_PATTERN.match(paragraph):
            used_ids.append(int(UID_PATTERN.match(paragraph).group('UID')))

    uids = UIDs(used_ids)

    text_iter = text.__iter__()
    paragraph = next(text_iter, None)
    while paragraph is not None:
        next_p = next(text_iter, None)

        if paragraph:
            # Only do this is paragraph is not empty
            if HEADING_OR_BIO_PATTERN.match(paragraph):
                paragraph = paragraph.replace('#', f'_ء_#={uids.get_uid()}=')
                if next_p and not MIU_LIGHT_OR_EIS1600_PATTERN.match(next_p):
                    heading_and_text = paragraph.split('\n', 1)
                    if len(heading_and_text) > 1:
                        paragraph = heading_and_text[0] + f'\n\n_ء_={uids.get_uid()}= ::UNDEFINED:: ~\n' + \
                                    heading_and_text[1]
            elif not UID_PATTERN.match(paragraph):
                section_header = '' if paragraph.startswith('::') else '::UNDEFINED:: ~\n'
                paragraph = f'_ء_={uids.get_uid()}= {section_header}' + paragraph

            text_updated.append(paragraph)

        paragraph = next_p

    text = '\n\n'.join(text_updated)

    # reassemble text
    final = header + '\n\n' + text

    with open(outfile, 'w', encoding='utf8') as outfile_h:
        outfile_h.write(final)


def main():
    arg_parser = ArgumentParser(
            prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to insert UIDs in updated EIS1600 file(s).
-----
Give a single EIS1600 file as input
or 
Use -e <EIS1600_repo> to batch process all EIS1600 files in the EIS1600 directory which have not been processed yet.
'''
    )
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument(
            '-e', '--eis1600_repo', type=str,
            help='Takes a path to the EIS1600 file repo and batch processes all files which have not been processed yet'
    )
    arg_parser.add_argument(
            'input', type=str, nargs='?',
            help='EIS1600 file to process',
            action=CheckFileEndingAction
    )
    args = arg_parser.parse_args()

    verbose = args.verbose

    if args.input:
        infile = './' + args.input
        xx_update_uids(infile, verbose)
    elif args.eis1600_repo:
        input_dir = args.eis1600_repo
        if not input_dir[-1] == '/':
            input_dir += '/'

        print(
                f'Insert missing UIDs into checked files from the EIS1600 repo (only for EIS1600 files which have not '
                f'been updated yet)'
        )
        files_list = read_files_from_readme(
            input_dir, '# Texts which need to be updated (old process)\n', False
            )
        infiles = get_files_from_eis1600_dir(input_dir, files_list, 'EIS1600')
        if not infiles:
            print(
                    'There are no more files to update'
            )
            sys.exit()

        params = [(infile, verbose) for infile in infiles]

        with Pool() as p:
            p.starmap_async(xx_update_uids, params).get()

        write_to_readme(input_dir, infiles, '# Texts updated with missing UIDs\n')
    else:
        print(
                'Pass in a <uri.EIS1600> file to process a single file or use the -e option for batch processing'
        )
        sys.exit()

    print('Done')
