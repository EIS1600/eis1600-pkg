from argparse import Action, ArgumentParser, RawDescriptionHelpFormatter
from glob import glob
from os.path import isdir, isfile
from sys import argv
from time import process_time, time

from p_tqdm import p_uimap

from eis1600.miu.methods import annotate_miu_file
from torch import cuda
from tqdm import tqdm


class CheckFileEndingAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and (isdir(input_arg) or isfile(input_arg)):
            setattr(namespace, self.dest, input_arg)
        else:
            print('You need to specify a valid path to the directory holding the files which shall be (re-)annotated')
            raise IOError


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to annotated directory holding gold-standard MIUs.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')
    arg_parser.add_argument(
            'input', type=str, nargs='?',
            help='Directory which holds the files to process or individual file to annotate',
            action=CheckFileEndingAction
    )

    args = arg_parser.parse_args()
    debug = args.debug
    input_df = args.input

    print(f'GPU available: {cuda.is_available()}')

    if isfile(input_df):
        annotate_miu_file(input_df)
    else:
        st = time()
        stp = process_time()

        mius = glob(input_df + '*.EIS1600')

        if debug:
            for idx, miu in tqdm(list(enumerate(mius))):
                try:
                    annotate_miu_file(miu)
                except Exception as e:
                    print(idx, miu)
                    print(e)
        else:
            res = []
            res += p_uimap(annotate_miu_file, mius)

        et = time()
        etp = process_time()

        print(f'Processing time: {etp-stp} seconds')
        print(f'Execution time: {et-st} seconds')

    print('Done')
