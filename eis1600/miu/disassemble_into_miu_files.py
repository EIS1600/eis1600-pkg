from logging import ERROR
from sys import argv, exit
from os.path import isfile, splitext
from argparse import ArgumentParser, Action, RawDescriptionHelpFormatter
from functools import partial

from eis1600.helper.logging import setup_logger

from eis1600.markdown.methods import update_uids
from p_tqdm import p_uimap
from tqdm import tqdm

from eis1600.helper.repo import MIU_REPO, get_path_to_other_repo, read_files_from_autoreport, \
    get_files_from_eis1600_dir, \
    write_to_readme, TEXT_REPO
from eis1600.miu.methods import disassemble_text


class CheckFileEndingAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and isfile(input_arg):
            filepath, fileext = splitext(input_arg)
            if fileext != '.EIS1600':
                parser.error('You need to input an EIS1600 file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, None)


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to disassemble EIS1600 file(s) into MIU file(s).
-----
Give a single EIS1600 file as input
or 
Run without input arg to batch process all double-checked EIS1600 files from the AUTOREPORT.
'''
    )
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument(
            'input', type=str, nargs='?',
            help='EIS1600 file to process',
            action=CheckFileEndingAction
    )
    args = arg_parser.parse_args()

    verbose = args.verbose

    if args.input:
        infile = './' + args.input
        out_path = get_path_to_other_repo(infile, 'MIU')
        print(f'Disassemble {infile}')
        disassemble_text(infile, out_path, verbose)
        infiles = [infile.split('/')[-1]]
        path = out_path.split('data')[0]
        write_to_readme(path, infiles, '# Texts disassembled into MIU files\n')
    else:
        input_dir = TEXT_REPO
        out_path = MIU_REPO + 'data/'

        print(f'Disassemble double-checked EIS1600 files from the AUTOREPORT')
        files_list = read_files_from_autoreport(input_dir)

        infiles = get_files_from_eis1600_dir(input_dir, files_list, 'EIS1600')
        if not infiles:
            print('There are no EIS1600 files to process')
            exit()

        if verbose:
            logger = setup_logger('disassemble', 'disassemble.log')
            for i, infile in tqdm(enumerate(infiles)):
                try:
                    print(f'{i} {infile}')
                    disassemble_text(infile, out_path, verbose)
                except ValueError as e:
                    logger.log(ERROR, infile)
        else:
            res = []
            res += p_uimap(partial(disassemble_text, out_path=out_path), infiles)

        path = out_path.split('data')[0]
        write_to_readme(path, infiles, '# Texts disassembled into MIU files\n')

    print('Done')
