from sys import argv, exit
from os.path import isfile, splitext
from argparse import ArgumentParser, Action, RawDescriptionHelpFormatter

from p_tqdm import p_uimap
from tqdm import tqdm

from eis1600.helper.repo import TEXT_REPO, get_files_from_eis1600_dir, read_files_from_autoreport
from eis1600.markdown.methods import update_uids


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
            description='''Script to insert UIDs in updated EIS1600 file(s).
-----
Give a single EIS1600 file as input
or 
Run without input arg to batch process all EIS1600 files in the EIS1600 directory which have not been processed yet.
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
        print(f'Update UIDs in {infile}')
        update_uids(infile, verbose)
        infiles = [infile.split('/')[-1]]
    else:
        input_dir = TEXT_REPO

        print(
                f'Insert missing UIDs into checked files from the EIS1600 repo'
        )

        files_list = read_files_from_autoreport(input_dir)
        infiles = get_files_from_eis1600_dir(input_dir, files_list, 'EIS1600')
        if not infiles:
            print(
                    'There are no more files to update'
            )
            exit()

        if verbose:
            for i, infile in tqdm(list(enumerate(infiles))):
                try:
                    print(f'{i} {infile}')
                    update_uids(infile, verbose)
                except Exception as e:
                    print(infile, e)
        else:
            res = []
            res += p_uimap(update_uids, infiles)

    print('Done')
