from sys import argv, exit
from os.path import isfile, splitext
from argparse import ArgumentParser, Action, RawDescriptionHelpFormatter
from functools import partial
from pathlib import Path

from p_tqdm import p_uimap
from tqdm import tqdm

from eis1600.helper.repo import get_files_from_eis1600_dir, read_files_from_readme, MIU_REPO
from eis1600.miu.methods import annotate_miu_file, get_mius


class CheckFileEndingAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and isfile(input_arg):
            filepath, fileext = splitext(input_arg)
            if fileext != '.IDs' and fileext != '.EIS1600':
                parser.error('You need to input an IDs file or a single MIU file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, None)


def main():
    arg_parser = ArgumentParser(
        prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
        description='''Script to NER annotate MIU file(s).
-----
Give an IDs file or a single MIU file as input
otherwise 
all files in the MIU directory are batch processed.
'''
        )
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument('-D', '--debug', action='store_true')
    arg_parser.add_argument('-p', '--parallel', help='parallel processing', action='store_true')
    arg_parser.add_argument('-f', '--force', help='force re-annotation', action='store_true')
    arg_parser.add_argument(
        'input', type=str, nargs='?',
        help='IDs or MIU file to process',
        action=CheckFileEndingAction
        )
    args = arg_parser.parse_args()

    verbose = args.verbose
    force = args.force

    if args.input:
        infile = './' + args.input
        filepath, fileext = splitext(infile)
        if fileext == '.IDs':
            mius = get_mius(infile)[1:]  # First element is path to the OPENITI HEADER
            print(f'NER annotate MIUs of {infile}')
            if args.parallel:
                res = []
                res += p_uimap(partial(annotate_miu_file), mius)
            else:
                for miu in tqdm(mius):
                    try:
                        annotate_miu_file(miu)
                    except Exception as e:
                        print(miu, e)
        else:
            print(f'NER annotate {infile}')
            annotate_miu_file(infile, force_annotation=force)
    else:
        input_dir = MIU_REPO

        if not Path(input_dir).exists():
            print('Your working directory seems to be wrong, make sure it is set to the parent dir of '
                  '`EIS1600_MIUs/`.')
            exit()

        print(f'NER annotate MIU files')
        files_list = read_files_from_readme(input_dir, '# Texts disassembled into MIU files\n')
        infiles = get_files_from_eis1600_dir(input_dir, files_list, 'IDs')
        if not infiles:
            print('There are no IDs files to process')
            exit()

        for infile in infiles:
            if verbose:
                print(f'NER annotate MIUs of {infile}')

            mius = get_mius(infile)[1:]  # First element is path to the OPENITI HEADER
            if args.parallel:
                res = []
                res += p_uimap(partial(annotate_miu_file), mius)
            else:
                for miu in tqdm(mius):
                    try:
                        annotate_miu_file(miu)
                    except Exception as e:
                        print(miu, e)

    print('Done')
