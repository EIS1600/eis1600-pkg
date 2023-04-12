from pathlib import Path

import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from functools import partial

from eis1600.helper.logging import setup_logger
from p_tqdm import p_uimap

from eis1600.onomastics.methods import nasab_annotation


def main():
    arg_parser = ArgumentParser(
            prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to annotate onomastic information in gold-standard MIUs.'''
    )

    with open('OpenITI_EIS1600_MIUs/gold_standard.txt', 'r', encoding='utf-8') as fh:
        files_txt = fh.read().splitlines()
    infiles = ['OpenITI_EIS1600_MIUs/training_data/' + file for file in files_txt if Path(
            'OpenITI_EIS1600_MIUs/training_data/' + file).exists()]

    logger_nasab = setup_logger('nasab_unknown', 'OpenITI_EIS1600_MIUs/logs/nasab_unknown.log')
    res = []
    res += p_uimap(partial(nasab_annotation, logger_nasab=logger_nasab), infiles)

    # for file in infiles:
    #     print(file)
    #     res.append(nasab_annotation(file, logger_nasab))

    with open('gazetteers/tagged.txt', 'w', encoding='utf-8') as fh:
        fh.write('\n\n'.join(res))

    print('Done')
