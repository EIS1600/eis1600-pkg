#!/usr/bin/env python

import sys
import os
from argparse import ArgumentParser, Action, RawDescriptionHelpFormatter
from multiprocessing import Pool

from eis1600.helper.repo import get_files_from_eis1600_dir, write_to_readme, read_files_from_readme
from eis1600.markdown.methods import update_uids


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


if __name__ == '__main__':

    arg_parser = ArgumentParser(prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
                                description='''Script to insert UIDs in updated EIS1600 file(s).
-----
Give a single EIS1600 file as input
or 
Use -e <EIS1600_repo> to batch process all EIS1600 files in the EIS1600 directory which have not been processed yet.
''')
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument('-e', '--eis1600_repo', type=str,
                            help='Takes a path to the EIS1600 file repo and batch processes all files which have not been processed yet')
    arg_parser.add_argument('input', type=str, nargs='?',
                            help='EIS1600 file to process',
                            action=CheckFileEndingAction)
    args = arg_parser.parse_args()

    verbose = args.verbose

    if args.input:
        infile = './' + args.input
        update_uids(infile, verbose)
    elif args.eis1600_repo:
        input_dir = args.eis1600_repo
        if not input_dir[-1] == '/':
            input_dir += '/'

        print(
            f'Insert missing UIDs into checked files from the EIS1600 repo (only for EIS1600 files which have not been updated yet)')
        files_list = [file for file, checked in read_files_from_readme(input_dir, '# Texts converted into `.EIS1600`\n')
                      if checked]
        files_list_done = read_files_from_readme(input_dir, '# Texts updated with missing UIDs\n')
        files_list = [file for file in files_list if file not in files_list_done]
        infiles = get_files_from_eis1600_dir(input_dir, files_list, '*.EIS1600')
        if not infiles:
            print(
                'There are no more files to update')
            sys.exit()

        params = [(infile, verbose) for infile in infiles]

        with Pool() as p:
            p.starmap_async(update_uids, params).get()

        write_to_readme(input_dir, infiles, '# Texts updated with missing UIDs\n')
    else:
        print(
            'Pass in a <uri.EIS1600> file to process a single file or use the -e option for batch processing'
        )
        sys.exit()

    print('Done')
