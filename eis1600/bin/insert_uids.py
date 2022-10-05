#!/usr/bin/env python
from pathlib import Path

import sys
import os
from argparse import ArgumentParser, Action, RawDescriptionHelpFormatter
from glob import glob
from multiprocessing import Pool

from eis1600.markdown.methods import insert_uids


class CheckFileEndingAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if os.path.isfile(input_arg):
            filepath, fileext = os.path.splitext(input_arg)
            if fileext != 'EIS1600_tmp':
                parser.error('You need to input an EIS1600_tmp file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, input_arg)


if __name__ == '__main__':

    arg_parser = ArgumentParser(prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
                                         description='''Script to insert uids in EIS1600_tmp file(s) and thereby converting them to final EIS1600 file(s).
-----
Give a single EIS1600_tmp file as input
or 
Give an input AND an output directory for batch processing.''')
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument('input', type=str,
                            help='EIS1600_tmp file to process or input directory with EIS1600_tmp files to process if an output directory is also given',
                            action=CheckFileEndingAction)
    arg_parser.add_argument('output', type=str, nargs='?',
                            help='Optional, if given batch processes all files from the input directory to the output directory')
    args = arg_parser.parse_args()

    verbose = args.verbose

    if args.input and not args.output:
        infile = args.input
        insert_uids(infile, None, verbose)

    elif args.output:
        input_dir = args.input
        output_dir = args.output

        print(f'Insert UIDS into {input_dir}, save resulting EIS1600 files to {output_dir}')

        infiles = glob(input_dir + '/*.EIS1600_tmp')
        if not infiles:
            print(
                'The input directory does not contain any EIS1600_tmp files to process')
            sys.exit()

        # Check if output directory exists else create that directory
        Path(output_dir).mkdir(exist_ok=True, parents=True)

        params = [(infile, output_dir, verbose) for infile in infiles]

        with Pool() as p:
            p.starmap_async(insert_uids, params).get()
    else:
        print(
            'Pass in a <uri.EIS1600_tmp> file to process a single file or enter an input and output directory to use batch processing')
        sys.exit()

    print('Done')
