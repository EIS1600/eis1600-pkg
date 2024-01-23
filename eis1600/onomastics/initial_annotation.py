from glob import glob
from pathlib import Path

import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from functools import partial

from p_tqdm import p_uimap

from eis1600.onomastics.methods import nasab_annotation
from eis1600.repositories.repo import TRAINING_DATA_REPO


def main():
    arg_parser = ArgumentParser(
            prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to annotate onomastic information in gold-standard MIUs.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')
    arg_parser.add_argument('-T', '--test', action='store_true')

    args = arg_parser.parse_args()
    debug = args.debug
    test = args.test

    if test:
        with open(TRAINING_DATA_REPO + 'gold_standard.txt', 'r', encoding='utf-8') as fh:
            files_txt = fh.read().splitlines()

        infiles = [TRAINING_DATA_REPO + 'gold_standard/' + file for file in files_txt if Path(
                TRAINING_DATA_REPO + 'gold_standard/' + file).exists()]
    else:
        infiles = glob(TRAINING_DATA_REPO + 'training_data_nasab_ML2/*.EIS1600')

    if debug:
        for file in infiles:
            print(file)
            nasab_annotation(file, test)
    else:
        res = []
        res += p_uimap(partial(nasab_annotation, test=test), infiles)

    print('Done')
