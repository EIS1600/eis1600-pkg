#!/usr/bin/env python

import sys
import os
from argparse import ArgumentParser, Action, RawDescriptionHelpFormatter
from glob import iglob
from multiprocessing import Pool

from eis1600.markdown.methods import convert_to_eis1600


class CheckFileEndingAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if os.path.isfile(input_arg):
            filepath, fileext = os.path.splitext(input_arg)
            if fileext != 'mARkdown':
                parser.error('You need to input a mARkdown file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, input_arg)


if __name__ == '__main__':

    arg_parser = ArgumentParser(prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
                                         description='''Script to convert mARkdown file(s) to EIS1600 file(s).
-----
Give a single mARkdown file as input
or 
Give an input AND an output directory for batch processing.''')
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument('input', type=str,
                            help='MARkdown file to process or input directory with mARkdown files to process if an output directory if also given',
                            action=CheckFileEndingAction)
    arg_parser.add_argument('output', type=str, nargs='?',
                            help='Optional, if given batch processes all files from the input directory to the output directory')
    args = arg_parser.parse_args()

    verbose = args.verbose

    if args.input and not args.output:
        infile = args.input
        convert_to_eis1600(infile, None, verbose)

    elif args.output:
        input_dir = args.input
        output_dir = args.output
        print(f'Convert mARkdown files from {input_dir}, save results to {output_dir}')

        infiles = iglob(input_dir + '/*.mARkdown')
        params = [(infile, output_dir, verbose) for infile in infiles]

        with Pool() as p:
            p.starmap_async(convert_to_eis1600, params).get()
    else:
        print(
            'Pass in a <uri.mARkdown> file to process a single file or enter an input and output directory to use batch processing')
        sys.exit()

    print('Done')
