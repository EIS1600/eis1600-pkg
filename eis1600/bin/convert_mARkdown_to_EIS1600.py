#!/usr/bin/env python
from pathlib import Path

import sys
import os
from argparse import ArgumentParser, Action, RawDescriptionHelpFormatter
from glob import glob
from multiprocessing import Pool

from eis1600.helper.repo import travers_eis1600_dir, get_files_from_eis1600_dir, read_files_from_readme
from eis1600.markdown.methods import convert_to_eis1600


class CheckFileEndingAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and os.path.isfile(input_arg):
            filepath, fileext = os.path.splitext(input_arg)
            if fileext not in ['.mARkdown', '.inProgess', '.completed']:
                parser.error('You need to input a mARkdown file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, None)


if __name__ == '__main__':

    arg_parser = ArgumentParser(prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
                                description='''Script to convert mARkdown file(s) to EIS1600TMP file(s).
-----
Give a single mARkdown file as input
or 
Give an input AND an output directory for batch processing.

Use -e <EIS1600_repo> to batch process all mARkdown files in the EIS1600 directory which have not been processed yet.
''')
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument('-e', '--eis1600_repo', type=str,
                            help='Takes a path to the EIS1600 file repo and batch processes all files which have not been processed yet')
    arg_parser.add_argument('input', type=str, nargs='?',
                            help='MARkdown file to process or input directory with mARkdown files to process if an output directory is also given',
                            action=CheckFileEndingAction)
    arg_parser.add_argument('output', type=str, nargs='?',
                            help='Optional, if given batch processes all files from the input directory to the output directory')
    args = arg_parser.parse_args()

    verbose = args.verbose

    if args.input and not args.output:
        infile = './' + args.input
        convert_to_eis1600(infile, None, verbose)

    elif args.output:
        input_dir = args.input
        output_dir = args.output
        if not input_dir[-1] == '/':
            input_dir += '/'

        print(f'Convert mARkdown files from {input_dir}, save resulting EIS1600TMP files to {output_dir}')

        infiles = glob(input_dir + '*.mARkdown')
        if not infiles:
            print(
                'The input directory does not contain any mARkdown files to process')
            sys.exit()

        # Check if output directory exists else create that directory
        Path(output_dir).mkdir(exist_ok=True, parents=True)

        params = [(infile, output_dir, verbose) for infile in infiles]

        with Pool() as p:
            p.starmap_async(convert_to_eis1600, params).get()
    elif args.eis1600_repo:
        input_dir = args.eis1600_repo
        if not input_dir[-1] == '/':
            input_dir += '/'

        print(f'Convert mARkdown files from the EIS1600 repo (only if there is not an EIS1600TMP file yet)')
        files_list = read_files_from_readme(input_dir, '# Texts with fixed poetry\n')
        infiles = get_files_from_eis1600_dir(input_dir, files_list, ['*.mARkdown', '*.inProcress', '*.completed'],
                                             '*.EIS1600*')
        if not infiles:
            print(
                'There are no more mARkdown files to process')
            sys.exit()

        params = [(infile, None, verbose) for infile in infiles]

        with Pool() as p:
            p.starmap_async(convert_to_eis1600, params).get()
    else:
        print(
            'Pass in a <uri.mARkdown> file to process a single file or use the -e option for batch processing'
        )
        sys.exit()

    print('Done')
