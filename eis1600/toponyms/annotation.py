# Annotate hajja -> Mekka
# Annotate jāwara -> Medina
# Tag category of toponyms
from glob import glob
from pathlib import Path

from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from functools import partial

from p_tqdm import p_uimap

from eis1600.helper.repo import TRAINING_DATA_REPO
from eis1600.toponyms.methods import toponym_category_annotation


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
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

        infiles = [TRAINING_DATA_REPO + 'gold_standard_nasab/' + file for file in files_txt if Path(
                TRAINING_DATA_REPO + 'gold_standard_nasab/' + file).exists()]
    else:
        infiles = glob(TRAINING_DATA_REPO + 'training_data_nasab_ML2/*.EIS1600')

    if debug:
        for file in infiles[:20]:
            print(file)
            toponym_category_annotation(file, test)
    else:
        res = []
        res += p_uimap(partial(toponym_category_annotation, test=test), infiles)

    print('Done')
