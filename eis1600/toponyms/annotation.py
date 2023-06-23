from glob import glob
from pathlib import Path

from sys import argv
from os.path import isfile, splitext
from argparse import Action, ArgumentParser, RawDescriptionHelpFormatter
from functools import partial

from p_tqdm import p_uimap

from eis1600.helper.repo import TRAINING_DATA_REPO
from eis1600.toponyms.methods import toponym_category_annotation


class CheckFileEndingAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and isfile(input_arg):
            filepath, fileext = splitext(input_arg)
            if fileext != '.EIS1600':
                parser.error('Input must be a single MIU file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, None)


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to annotate onomastic information in gold-standard MIUs.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')
    arg_parser.add_argument('-K', '--keep', action='store_true', help='Keep automatic tags (Ü-tags)')
    arg_parser.add_argument('-T', '--test', action='store_true')
    arg_parser.add_argument(
            'input', type=str, nargs='?',
            help='IDs or MIU file to process',
            action=CheckFileEndingAction
    )

    args = arg_parser.parse_args()
    debug = args.debug
    test = args.test
    keep = args.keep

    if args.input:
        toponym_category_annotation(args.input, test, keep)
    else:
        if test:
            with open(TRAINING_DATA_REPO + 'gold_standard.txt', 'r', encoding='utf-8') as fh:
                files_txt = fh.read().splitlines()

            infiles = [TRAINING_DATA_REPO + 'gold_standard_nasab/' + file for file in files_txt if Path(
                    TRAINING_DATA_REPO + 'gold_standard_nasab/' + file).exists()]
        else:
            infiles = glob(TRAINING_DATA_REPO + 'training_data_nasab_ML2/*.EIS1600')

        if debug:
            for file in infiles[:20]:
                print(file)
                toponym_category_annotation(file, test, keep)
        else:
            res = []
            res += p_uimap(partial(toponym_category_annotation, test=test, keep_automatic_tags=keep), infiles)

    print('Done')
