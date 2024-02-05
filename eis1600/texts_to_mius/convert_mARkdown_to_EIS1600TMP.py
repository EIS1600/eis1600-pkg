from sys import argv, exit
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
from glob import glob
from functools import partial

from tqdm import tqdm
from p_tqdm import p_uimap

from eis1600.helper.CheckFileEndingActions import CheckFileEndingMARKdownAction
from eis1600.repositories.repo import get_files_from_eis1600_dir, read_files_from_readme, \
    update_texts_fixed_poetry_readme
from eis1600.texts_to_mius.convert_mARkdown_methods import convert_to_EIS1600TMP


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to convert mARkdown file(s) to EIS1600TMP file(s).
-----
Give a single mARkdown file as input
or 
Give an input AND an output directory for batch processing.

Run without input arg to batch process all mARkdown files in the EIS1600 directory which have not been processed yet.
'''
    )
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument(
            'input', type=str, nargs='?',
            help='MARkdown file to process or input directory with mARkdown files to process if an output directory is '
                 'also given',
            action=CheckFileEndingMARKdownAction
    )
    arg_parser.add_argument(
            'output', type=str, nargs='?',
            help='Optional, if given batch processes all files from the input directory to the output directory'
    )
    args = arg_parser.parse_args()

    verbose = args.verbose

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
        print(f'Convert mARkdown file {infile} to EIS1600TMP file')
        convert_to_EIS1600TMP(infile, None, verbose)
        infiles = [infile.split('/')[-1]]

    elif args.output:
        input_dir = args.input
        output_dir = args.output
        if not input_dir[-1] == '/':
            input_dir += '/'

        print(f'Convert mARkdown files from {input_dir}, save resulting EIS1600TMP files to {output_dir}')

        infiles = glob(input_dir + '*.mARkdown')
        if not infiles:
            print(
                    'The input directory does not contain any mARkdown files to process'
            )
            exit()

        # Check if output directory exists else create that directory
        Path(output_dir).mkdir(exist_ok=True, parents=True)

        if verbose:
            for infile in tqdm(infiles):
                try:
                    convert_to_EIS1600TMP(infile, output_dir, verbose)
                except Exception as e:
                    print(infile, e)
        else:
            res = []
            res += p_uimap(partial(convert_to_EIS1600TMP, output_dir=output_dir), infiles)

    else:
        input_dir = './'

        print(f'Update list of texts with automatically fixed poetry in the README')
        update_texts_fixed_poetry_readme(input_dir, '# Texts with fixed poetry\n')
        print(f'List of texts with automatically fixed poetry was successfully updated in the README')

        print(f'Convert mARkdown files from the EIS1600 repo (only if there is not an EIS1600TMP file yet)')
        files_list = read_files_from_readme(input_dir, '# Texts with fixed poetry\n')
        infiles = get_files_from_eis1600_dir(
                input_dir, files_list, ['mARkdown', 'inProcress', 'completed'], 'EIS1600*'
        )
        if not infiles:
            print(
                    'There are no more mARkdown files to process'
            )
            exit()

        if verbose:
            for infile in tqdm(infiles):
                try:
                    convert_to_EIS1600TMP(infile, None, verbose)
                except Exception as e:
                    print(infile, e)
        else:
            res = []
            res += p_uimap(convert_to_EIS1600TMP, infiles)

    print('Done')
