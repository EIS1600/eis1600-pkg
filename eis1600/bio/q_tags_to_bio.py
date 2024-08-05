from datetime import date
from functools import partial
from pathlib import Path
from typing import Dict, Optional, Tuple, Union, Pattern
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
from eis1600.training_data.online_editor_files import fix_formatting


stat = {'NOT REVIEWED': 0, 'REVIEWED': 0, 'REVIEWED2': 0, 'EXCLUDED': 0}

TOPO_LABEL_DICT = {'B-TOPD': 0, 'I-TOPD': 1, 'O': 2}
TOPO_CATS = ['N', 'T']
TOPO_CLASS = "TOPD"
TOPO_PREFIX = "Q"
TOPO_PATTERN = compile(r'Q(?P<num_tokens>\d+)(?P<cat>[' + ''.join(TOPO_CATS) + ']*)')


PER_LABEL_DICT = {'B-PER': 0, 'I-PER': 1, 'O': 2}
PER_CATS = ['B', 'T', 'S', 'F', 'I', 'O']
PER_CLASS = "PER"
PER_PREFIX = "P"
PER_PATTERN = compile(r'P(?P<num_tokens>\d+)(?P<cat>[' + ''.join(PER_CATS) + ']*)')


#FIXME
NASAB_LABEL_DICT = {'B-NASAB': 0, 'I-NASAB': 1, 'O': 2}
NASAB_CLASS = "BONOM"  #"EONOM"
NASAB_PATTERN = compile(r'Q(?P<num_tokens>\d+)(?P<cat>[' + ''.join(TOPO_CATS) + ']*)') #FIXME
NASAB_PREFIX = "N"
# BONOM ISM2 عبد الله بن NAS1 محمد بن NAS2 عبد الله بن NAS1 يونس ، KUN2 أبو الحسين NSB1 السمناني EONOM .


NER_LABEL_DICT = {'B-LOC': 0, 'B-MISC': 1, 'B-ORG': 2, 'B-PERS': 3,
                  'I-LOC': 4, 'I-MISC': 5, 'I-ORG': 6, 'I-PERS': 7, '0': 8}
# https://docs.google.com/document/d/1y-zYzU47E1_DfNT6dwISV0Z7rxsOUpU2vTxxIf_O10o/edit#heading=h.u6stya7t55a8
NER_CATS = ['N', 'T',
            'B', 'S', 'F', 'I', 'O', 'C', 'X',]
NER_CLASS = "TOPD"
NER_PREFIX = "Q"
NER_PATTERN = compile(r'[QAMPTY](?P<num_tokens>\d+)(?P<cat>[' + ''.join(NER_CATS) + ']*)')
#FIXME
#     Converter method for BIO labels to EIS100 tags. BI labels must follow this pattern: [BI]-[AMPTY].* with
#     * [A]ge
#     * [M]ISC
#     * [P]erson
#     * [Q]
#     * [T]oponym
#     * [Y]ear
#     Usually, EIS1600 BIO labels have a three letter code: [YY][BDKP] with YY for year and [BDKP] for the sub-class.


def reconstruct_automated_tag(row, prefix) -> str:
    return prefix + row['num_tokens']


def get_q_true(file: str, pattern: Pattern, class_: str, label_dict: dict, prefix: str,
               keep_automatic_tags: Optional[bool] = False) -> Tuple[str, Union[Dict, None]]:
    """
    :param file: miu to process.
    :param pattern: pattern describing the tag.
    :param class_: tag to use in output.
    :param label_dict: labels associated to integer classes.
    :param prefix: .
    :param keep_automatic_tags: Keep Ü-tags, defaults to false.
    :return: Tuple of reviewed status and bio-tags dict.
    """
    fix_formatting(file, update_ids_flag=False)

    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object, keep_automatic_tags, skip_subsections=True)

    stat[yml_handler.reviewed] = stat[yml_handler.reviewed] + 1
    if not yml_handler.reviewed.startswith('REVIEWED'):
        return yml_handler.reviewed, None

    s_notna = df['TAGS_LISTS'].loc[df['TAGS_LISTS'].notna()].apply(lambda tag_list: ','.join(tag_list))
    df_true = s_notna.str.extract(pattern).dropna(how='all')
    tops = df_true.apply(partial(reconstruct_automated_tag, prefix=prefix), axis=1)
    tops.name = 'TRUE'

    if not tops.empty:
        df = df.join(tops)
    else:
        return yml_handler.reviewed, None

    bio_tags = md_to_bio(
            df[['TOKENS', 'TRUE']],
            'TRUE',
            pattern,
            class_,
            label_dict
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
            'out_file',
            help='''Name for the JSON file containing the training-data (without file ending).
            E.G. Q/q_training_data'''
    )
    arg_parser.add_argument(
            'tag_class', type=str, choices=["TOPO", "PER", "NASAB", "NER"], help='class to extract',
    )

    args = arg_parser.parse_args()

    mius = list(args.input.glob('*.EIS1600'))

    pattern, class_, label_dict, prefix = "", "", "", ""

    if args.tag_class == "TOPO":
        class_ = TOPO_CLASS
        label_dict = TOPO_LABEL_DICT
        pattern = TOPO_PATTERN
        prefix = TOPO_PREFIX
    elif args.tag_class == "PER":
        class_ = PER_CLASS
        label_dict = PER_LABEL_DICT
        pattern = PER_PATTERN
        prefix = PER_PREFIX
    elif args.tag_class == "NASAB":
        class_ = NASAB_CLASS
        label_dict = NASAB_LABEL_DICT
        pattern = NASAB_PATTERN
        prefix = NASAB_PREFIX

    res = []
    if args.debug:
        for idx, miu in tqdm(list(enumerate(mius))):
            try:
                res.append(get_q_true(miu, pattern=pattern, class_=class_, label_dict=label_dict,
                                      prefix=prefix, keep_automatic_tags=True))
            except Exception as e:
                print(idx, miu)
                print(e)
    else:
        res += p_uimap(
            partial(get_q_true, pattern=pattern, class_=class_, label_dict=label_dict, prefix=prefix,
                    keep_automatic_tags=True),
            mius,
            total=len(mius)
        )

    reviewed, bio_dicts = zip(*res)
    bio_dicts = [r for r in bio_dicts if r is not None]

    out_file_path = RESEARCH_DATA_REPO + args.out_file + '_' + date.today().isoformat() + '.json'

    with open(out_file_path, 'w', encoding='utf-8') as fh:
        dump(bio_dicts, fh, indent=4, ensure_ascii=False)

    print(f'Output saved in file {out_file_path}')

    print(Series(reviewed).value_counts())
    print('Done')
