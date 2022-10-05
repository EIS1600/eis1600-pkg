#!/usr/bin/env python

import sys
import os
from argparse import ArgumentParser, Action, RawDescriptionHelpFormatter
from multiprocessing import Pool

from eis1600.helper.repo import travers_eis1600_dir
from eis1600.miu_handling.reassembling import reassemble_text


class CheckFileEndingAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and os.path.isfile(input_arg):
            filepath, fileext = os.path.splitext(input_arg)
            if fileext != '.EIS1600':
                parser.error('You need to input a EIS1600 file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, None)


if __name__ == '__main__':

    arg_parser = ArgumentParser(prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
                                description='''Script to reassemble EIS1600 file(s) from MIU file(s).
-----
Give a single EIS1600 file as input
or 
Use -e <EIS1600_repo> to batch process all EIS1600 files in the EIS1600 directory.
''')
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument('-e', '--eis1600_repo', type=str,
                            help='Takes a path to the EIS1600 file repo and batch processes all files')
    arg_parser.add_argument('input', type=str, nargs='?',
                            help='EIS1600 file to process',
                            action=CheckFileEndingAction)
    args = arg_parser.parse_args()

    verbose = args.verbose

    if args.input:
        infile = './' + args.input
        reassemble_text(infile, verbose)
    elif args.eis1600_repo:
        input_dir = args.eis1600_repo

        print(f'Reassemble EIS1600 files from the EIS1600 repo')
        infiles = travers_eis1600_dir(input_dir, '*.EIS1600')
        if not infiles:
            print('There are no EIS1600 files to process')
            sys.exit()

        params = [(infile, verbose) for infile in infiles]

        with Pool() as p:
            p.starmap_async(reassemble_text, params).get()
    else:
        print(
            'Pass in a <uri.EIS1600> file to process a single file or use the -e option for batch processing'
        )
        sys.exit()

    print('Done')
