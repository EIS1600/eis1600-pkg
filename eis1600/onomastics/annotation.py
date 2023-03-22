import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from functools import partial
from glob import glob

from p_tqdm import p_uimap

import pandas as pd

from eis1600.gazetteers.Onomastics import Onomastics
from eis1600.gazetteers.Toponyms import Toponyms
from eis1600.onomastics.methods import nasab_filtering, nasab_annotation


def main():
    arg_parser = ArgumentParser(
            prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to disassemble EIS1600 file(s) into MIU file(s).
    -----
    Give a single EIS1600 file as input
    or 
    Run without input arg to batch process all EIS1600 files in the EIS1600 directory.
    '''
    )
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument('-f', '--filtering', action='store_true')
    args = arg_parser.parse_args()

    verbose = args.verbose

    og = Onomastics.instance()
    tg = Toponyms.instance()
    infiles = glob('OpenITI_EIS1600_MIUs/training_data/*.EIS1600')#[:100]

    if args.filtering:
        res = []
        res += p_uimap(partial(nasab_filtering, og=og, tg=tg), infiles)

        unknown, nasabs, manipulated, cutoff = zip(*res)

        with open('OnomasticonArabicum2020/oa2020/nasabs.txt', 'w', encoding='utf-8') as fh:
            fh.write('\n\n'.join([f'1\n{nsb}\n2\n{co}' for u, nsb, m, co in res]))

        with open('OnomasticonArabicum2020/oa2020/manipulated.txt', 'w', encoding='utf-8') as fh:
            fh.write('\n\n'.join(manipulated))

        unknown_flat = pd.Series([elem for sub in unknown for elem in sub])
        unknown_flat.value_counts().to_csv('OnomasticonArabicum2020/oa2020/unknown.csv')
    else:
        # for file in infiles:
        #     print(file)
        #     nasab_annotation(file, og, tg)
        res = []
        res += p_uimap(partial(nasab_annotation, og=og, tg=tg), infiles)

        with open('OnomasticonArabicum2020/oa2020/tagged.txt', 'w', encoding='utf-8') as fh:
            fh.write('\n\n'.join(res))

    print('Done')
