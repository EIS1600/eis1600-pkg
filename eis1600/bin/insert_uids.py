#!/usr/bin/env python
from pathlib import Path

import sys
import os
from argparse import ArgumentParser, Action, RawDescriptionHelpFormatter
from glob import glob
from multiprocessing import Pool

from eis1600.helper.repo import travers_eis1600_dir, get_files_from_eis1600_dir, write_to_readme, read_files_from_readme
from eis1600.markdown.methods import insert_uids


class CheckFileEndingAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and os.path.isfile(input_arg):
            filepath, fileext = os.path.splitext(input_arg)
            if fileext != '.EIS1600TMP':
                parser.error('You need to input an EIS1600TMP file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, None)


if __name__ == '__main__':

    arg_parser = ArgumentParser(prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
                                description='''Script to insert UIDs in EIS1600TMP file(s) and thereby converting them to final EIS1600 file(s).
-----
Give a single EIS1600TMP file as input
or 
Give an input AND an output directory for batch processing.

Use -e <EIS1600_repo> to batch process all EIS1600TMP files in the EIS1600 directory which have not been processed yet.
''')
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument('-e', '--eis1600_repo', type=str,
                            help='Takes a path to the EIS1600 file repo and batch processes all files which have not been processed yet')
    arg_parser.add_argument('input', type=str, nargs='?',
                            help='EIS1600TMP file to process or input directory with EIS1600TMP files to process if an output directory is also given',
                            action=CheckFileEndingAction)
    arg_parser.add_argument('output', type=str, nargs='?',
                            help='Optional, if given batch processes all files from the input directory to the output directory')
    args = arg_parser.parse_args()

    verbose = args.verbose

    if args.input and not args.output:
        infile = './' + args.input
        insert_uids(infile, None, verbose)

    elif args.output:
        input_dir = args.input
        output_dir = args.output

        print(f'Insert UIDs into {input_dir}, save resulting EIS1600 files to {output_dir}')

        infiles = glob(input_dir + '/*.EIS1600TMP')
        if not infiles:
            print(
                'The input directory does not contain any EIS1600TMP files to process')
            sys.exit()

        # Check if output directory exists else create that directory
        Path(output_dir).mkdir(exist_ok=True, parents=True)

        params = [(infile, output_dir, verbose) for infile in infiles]

        with Pool() as p:
            p.starmap_async(insert_uids, params).get()
    elif args.eis1600_repo:
        input_dir = args.eis1600_repo
        if not input_dir[-1] == '/':
            input_dir += '/'

        print(f'Insert UIDs into files from the EIS1600 repo (only if there is not an EIS1600 file yet)')
        files_list = read_files_from_readme(input_dir, '# Texts with fixed poetry\n')
        infiles = get_files_from_eis1600_dir(input_dir, files_list, '*.EIS1600TMP', '*.EIS1600')
        if not infiles:
            print(
                'There are no more EIS1600TMP files to process')
            sys.exit()

        params = [(infile, None, verbose) for infile in infiles]

        with Pool() as p:
            p.starmap_async(insert_uids, params).get()

        write_to_readme(input_dir, infiles, '# Texts converted into `.EIS1600`\n')
    else:
        print(
            'Pass in a <uri.EIS1600TMP> file to process a single file or use the -e option for batch processing'
        )
        sys.exit()

    print('Done')
