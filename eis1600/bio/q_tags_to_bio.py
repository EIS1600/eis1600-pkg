from datetime import date
from functools import partial
from pathlib import Path
from typing import Dict, Optional, Tuple, Union
from sys import argv
from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter
from re import compile
from json import dump

from pandas import Series

from p_tqdm import p_uimap
from tqdm import tqdm

from eis1600.helper.CheckFileEndingActions import CheckIsDirAction
from eis1600.bio.md_to_bio import md_to_bio
from eis1600.processing.preprocessing import get_yml_and_miu_df
from eis1600.repositories.repo import RESEARCH_DATA_REPO

LABEL_DICT = {'B-TOPD': 0, 'I-TOPD': 1, 'O': 2}
CATS = ['N', 'T']
Q_PATTERN = compile(r'Q(?P<num_tokens>\d+)(?P<cat>[' + ''.join(CATS) + ']*)')
stat = {'NOT REVIEWED': 0, 'REVIEWED': 0, 'REVIEWED2': 0, 'EXCLUDED': 0}


def reconstruct_automated_tag(row) -> str:
    return 'Q' + row['num_tokens']


def get_q_true(file: str, bio_main_class: str, keep_automatic_tags: Optional[bool] = False) \
        -> Tuple[str, Union[Dict, None]]:
    """

    :param file: miu to process.
    :param bio_main_class: tag is composed like this: B-<bio_main_class>, defaults to B-Q.
    :param keep_automatic_tags: Keep Ü-tags, defaults to false.
    :return: Tuple of reviewed status and bio-tags dict.
    """
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object, keep_automatic_tags)

    stat[yml_handler.reviewed] = stat[yml_handler.reviewed] + 1
    if yml_handler.reviewed != 'REVIEWED':
        return yml_handler.reviewed, None

    s_notna = df['TAGS_LISTS'].loc[df['TAGS_LISTS'].notna()].apply(lambda tag_list: ','.join(tag_list))
    df_true = s_notna.str.extract(Q_PATTERN).dropna(how='all')
    tops = df_true.apply(reconstruct_automated_tag, axis=1)
    tops.name = 'TRUE'

    if not tops.empty:
        df = df.join(tops)
    else:
        return yml_handler.reviewed, None

    bio_tags = md_to_bio(
            df[['TOKENS', 'TRUE']],
            'TRUE',
            Q_PATTERN,
            bio_main_class,
            LABEL_DICT
    )

    return yml_handler.reviewed, bio_tags


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to extract Q-annotations from MIUs and create BIO-training-data.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')
    arg_parser.add_argument(
            'input', type=Path, nargs=1,
            help='Directory which holds the files to process or individual file to annotate',
            action=CheckIsDirAction
    )
    arg_parser.add_argument(
            'out_file', type=FileType('w'), nargs=1,
            help='''Name for the JSON file containing the training-data (without file ending).
            E.G. Q/q_training_data'''
    )
    arg_parser.add_argument(
            'bio_main_class', type=str, nargs='?', default='Q', action='store',
            help='BIO main class, B-<bio_main_class>, defaults to B-Q',
    )

    args = arg_parser.parse_args()
    debug = args.debug
    bio_main_class = args.bio_main_class
    input_df = args.input
    out_file = args.out_file
    keep = True

    mius = input_df.glob('*.EIS1600')

    res = []
    if debug:
        for idx, miu in tqdm(list(enumerate(mius))):
            try:
                res.append(get_q_true(miu, bio_main_class, keep))
            except Exception as e:
                print(idx, miu)
                print(e)
    else:
        res += p_uimap(partial(get_q_true, bio_main_class=bio_main_class, keep_automatic_tags=keep), mius)

    reviewed, bio_dicts = zip(*res)
    bio_dicts = [r for r in bio_dicts if r is not None]

    with open(
            RESEARCH_DATA_REPO + out_file + '_' + date.today().isoformat() + '.json',
            'w',
            encoding='utf-8'
    ) as fh:
        dump(bio_dicts, fh, indent=4, ensure_ascii=False)

    print(Series(reviewed).value_counts())
    print('Done')
