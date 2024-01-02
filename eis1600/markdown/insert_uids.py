from tqdm import tqdm
from p_tqdm import p_uimap
from pathlib import Path

from sys import argv, exit
from os.path import isfile, splitext
from argparse import ArgumentParser, Action, RawDescriptionHelpFormatter
from glob import glob
from multiprocessing import Pool

from eis1600.helper.repo import get_files_from_eis1600_dir, read_files_from_readme
from eis1600.markdown.methods import insert_uids


class CheckFileEndingAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and isfile(input_arg):
            filepath, fileext = splitext(input_arg)
            if fileext != '.EIS1600TMP':
                parser.error('You need to input an EIS1600TMP file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, None)


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to insert UIDs in EIS1600TMP file(s) and thereby converting them to final EIS1600 
            file(s).
-----
Give a single EIS1600TMP file as input
or 
Give an input AND an output directory for batch processing.

Run without input arg to batch process all EIS1600TMP files in the EIS1600 directory which have not been processed yet.
'''
            )
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument(
            'input', type=str, nargs='?',
            help='EIS1600TMP file to process, you need to run this command from inside text repo',
            action=CheckFileEndingAction
            )
    arg_parser.add_argument(
            'output', type=str, nargs='?',
            help='Optional, if given batch processes all files from the input directory to the output directory'
            )
    args = arg_parser.parse_args()

    verbose = args.verbose

    # If this script is run with a single file as input
    if args.input and not args.output:
        infile = './' + args.input
        if 'data' in infile:
            path = infile.split('data')[0]
        else:
            depth = len(infile.split('/'))
            if depth == 2:
                path = '../../../'
            elif depth == 3:
                path = '../../'
            else:
                path = '../'
        print(f'Insert UIDs into {infile}')
        insert_uids(infile, None, verbose)
        infiles = [infile.split('/')[-1]]

    # If this script is run with input and output directory (old, not used any more)
    elif args.output:
        input_dir = args.input
        output_dir = args.output

        print(f'Insert UIDs into {input_dir}, save resulting EIS1600 files to {output_dir}')

        infiles = glob(input_dir + '/*.EIS1600TMP')
        if not infiles:
            print(
                    'The input directory does not contain any EIS1600TMP files to process'
                    )
            exit()

        # Check if output directory exists else create that directory
        Path(output_dir).mkdir(exist_ok=True, parents=True)

        params = [(infile, output_dir, verbose) for infile in infiles]

        with Pool() as p:
            p.starmap_async(insert_uids, params).get()

    # If this script is run with -e option on the EIS1600 text repo
    else:
        input_dir = './'

        # Get EIS1600TMP files which are marked as ready to process in the README and have not yet been converted to
        # EIS1600
        print(f'Insert UIDs into files from the EIS1600 repo (only if there is not an EIS1600 file yet)')
        # TODO there is no longer a readme file
        files_list = read_files_from_readme(input_dir, '# Texts converted into `.EIS1600TMP`\n')
        infiles = get_files_from_eis1600_dir(input_dir, files_list, 'EIS1600TMP', 'EIS1600')
        if not infiles:
            print(
                    'There are no more EIS1600TMP files to process'
                    )
            exit()

        # Insert UIDs in the selected files, runs in parallel
        if verbose:
            for infile in tqdm(infiles):
                try:
                    insert_uids(infile, None, verbose)
                except Exception as e:
                    print(infile, e)
        else:
            res = []
            res += p_uimap(insert_uids, infiles)

    print('Done')
