from datetime import date
from functools import partial
from glob import glob
from os.path import isdir
from typing import Dict, Optional, Tuple, Union
from sys import argv
from argparse import Action, ArgumentParser, RawDescriptionHelpFormatter
from re import compile
from json import dump

from pandas import Series

from p_tqdm import p_uimap
from tqdm import tqdm

from eis1600.helper.repo import RESEARCH_DATA_REPO
from eis1600.markdown.md_to_bio import md_to_bio
from eis1600.processing.preprocessing import get_yml_and_miu_df

LABEL_DICT = {'B-TOPD': 0, 'I-TOPD': 1, 'O': 2}
CATS = ['N', 'T']
Q_PATTERN = compile(r'Q(?P<num_tokens>\d+)(?P<cat>[' + ''.join(CATS) + ']*)')
stat = {'NOT REVIEWED': 0, 'REVIEWED': 0, 'REVIEWED2': 0, 'EXCLUDED': 0}


class CheckFileEndingAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and isdir(input_arg):
            setattr(namespace, self.dest, input_arg)
        else:
            print('You need to specify a valid path to the directory holding the files which have been annotated')
            raise IOError


def reconstruct_automated_tag(row) -> str:
    return 'Q' + row['num_tokens']


def get_q_true(file: str, keep_automatic_tags: Optional[bool] = False) -> Tuple[str, Union[Dict, None]]:
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object, keep_automatic_tags)

    stat[yml_handler.reviewed] = stat[yml_handler.reviewed] + 1
    if yml_handler.reviewed != 'REVIEWED2':
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
            'TOPD',
            LABEL_DICT
    )

    return yml_handler.reviewed, bio_tags


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to annotate onomastic information in gold-standard MIUs.'''
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
    keep = True

    mius = glob(input_df + '*.EIS1600')

    res = []
    if debug:
        for idx, miu in tqdm(list(enumerate(mius))):
            try:
                res.append(get_q_true(miu, keep))
            except Exception as e:
                print(idx, miu)
                print(e)
    else:
        res += p_uimap(partial(get_q_true, keep_automatic_tags=keep), mius)

    reviewed, bio_dicts = zip(*res)
    bio_dicts = [r for r in bio_dicts if r is not None]

    with open(
            RESEARCH_DATA_REPO + 'TOPONYM_DESCRIPTION_DETECTION/toponym_description_training_data_' + date.today(

            ).isoformat() +
            '.json',
            'w',
            encoding='utf-8'
    ) as fh:
        dump(bio_dicts, fh, indent=4, ensure_ascii=False)

    print(Series(reviewed).value_counts())
    print('Done')
