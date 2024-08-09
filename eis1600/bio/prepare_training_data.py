import pandas as pd

from datetime import date
from functools import partial
from pathlib import Path
from typing import Dict, Optional, Tuple, Union, Pattern
from collections.abc import Iterable
from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from re import compile
from json import dump
from p_tqdm import p_uimap
from tqdm import tqdm

from eis1600.helper.CheckFileEndingActions import CheckIsDirAction
from eis1600.processing.preprocessing import get_yml_and_miu_df
from eis1600.repositories.repo import RESEARCH_DATA_REPO
from eis1600.training_data.online_editor_files import fix_formatting

# usage:
# test:
#   $ prepare_training_data eis1600-training/test2 tests/xxx TOPONYM -D
# real data:
#   $ cp -r eis1600-online-editor/data/production/tasks_output/12k_random_bios eis1600-training
#   $ cd eis1600-training/12k_random_bios ; gunzip * ; cd -
#   $
#   $ prepare_training_data eis1600-training/12k_random_bios TOPONYM/training_data_toponym TOPONYM
#   $ prepare_training_data eis1600-training/12k_random_bios ONOMASTIC_ELEMENTS/training_data_onomastic ONOMASTIC
#

stat = {'NOT REVIEWED': 0, 'REVIEWED': 0, 'REVIEWED2': 0, 'EXCLUDED': 0}


def get_label_dict(entities: Iterable[str]) -> dict:
    entities = [cl for pair in ((f"B-{c}", f"I-{c}") for c in entities) for cl in pair]
    entities.append("O")
    label_dict = {k: i for i, k in enumerate(entities)}
    return label_dict


def get_data(file: str,
             pattern: Pattern,
             bio_main_class: str,
             label_dict: dict,
             keep_automatic_tags: Optional[bool] = False,
             add_bio_class_as_prefix: Optional[bool] = False,
             empty_to_X: Optional[bool] = False) -> Tuple[str, Union[Dict, None]]:
    """
    :param file: miu to process.
    :param pattern: pattern describing the tag.
    :param str bio_main_class: String of two letters which are used to indicate the main entity, e.g. 'YY' for dates,
    'TO' for toponyms, etc.
    :param label_dict: labels associated to integer classes.
    :param keep_automatic_tags: Keep Ü-tags, defaults to false.
    :param add_bio_class_as_prefix: add bio_class as prefix in bio label,
        e.g. for toponym subclass "A", convert it to "TOA".
    :param empty_to_X: convert empty subclasses into X subclass, e.g. "T1" in training data must be changed to "T1X".
    :return: Tuple of reviewed status and bio-tags dict.
    """
    fix_formatting(file, update_ids_flag=False)

    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object, keep_automatic_tags, skip_subsections=True)

    stat[yml_handler.reviewed] = stat[yml_handler.reviewed] + 1
    if not yml_handler.reviewed.startswith('REVIEWED'):
        return yml_handler.reviewed, None

    s_notna = df['TAGS_LISTS'].loc[df['TAGS_LISTS'].notna()].apply(lambda tag_list: ','.join(tag_list))

    if keep_automatic_tags:
        s_notna = s_notna.str.replace('Ü', '')

    df_true = s_notna.str.extract(pattern).dropna(how='all')

    if df_true.empty:
        return yml_handler.reviewed, None

    df[["BIO", "num_tokens"]] = df.merge(
        df_true[["cat", "num_tokens"]],
        how="left",
        left_index=True,
        right_index=True
    )[["cat", "num_tokens"]]

    # add labels and num_tokens
    if add_bio_class_as_prefix:
        df["BIO"] = df["BIO"].apply(lambda c: bio_main_class + c if pd.notna(c) else None)
    else:
        df["BIO"] = df["BIO"].apply(lambda c: c if pd.notna(c) else None)
    df["BIO"] = df["BIO"].where(df["BIO"].notna(), None)
    df["num_tokens"] = pd.to_numeric(df["num_tokens"], errors="coerce").fillna(0).astype(int)

    # class "" is converted to "X"
    if empty_to_X:
        df["BIO"] = df["BIO"].replace(bio_main_class, bio_main_class+"X")

    # extend labels according to num_tokens and convert labels into B- or I-
    for index, row in enumerate(df.itertuples(index=False)):
        if row.BIO and row.num_tokens:
            for i in range(1, row.num_tokens):
                if index + i < len(df):
                    df.at[index + i, "BIO"] = "I-" + row.BIO
            df.at[index, "BIO"] = "B-" + row.BIO

    # convert None to "O"
    df["BIO"] = df["BIO"].replace({None: "O"})

    # add labels ids
    df["BIO_IDS"] = df["BIO"].apply(lambda val: label_dict[val])

    # remove nan in tokens
    df = df.dropna(subset=["TOKENS"])

    bio_tags = {
            'tokens': df['TOKENS'].to_list(),
            'ner_tags': df['BIO_IDS'].to_list(),
            'ner_classes': df['BIO'].to_list()
    }
    return yml_handler.reviewed, bio_tags


def main():
    arg_parser = ArgumentParser(
        prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
        description='''Script to extract annotations from MIUs and create training-data.'''
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
        'entities_class',
        type=str,
        choices=["NASAB", "NER", "ONOMASTIC", "PERSON_FCON", "PERSON_STN", "TOPONYM", "TOPONYM_DESC"],
        help='Class of labels to extract.',
    )
    arg_parser.add_argument(
        '--keep_automatic_tags',
        action='store_true',
        help='Keep Ü-tags.',
    )

    args = arg_parser.parse_args()

    mius = list(args.input.glob('*.EIS1600'))

    pattern, bio_main_class, label_dict = "", "", ""
    add_bio_class_as_prefix = False
    empty_to_X = False

    if args.entities_class == "TOPONYM":
        bio_main_class = "TO"
        classes = ["A", "B", "D", "G", "K", "O", "R", "V", "X"]
        category_to_class = {c: bio_main_class+c for c in classes}   # {"A": "TOA", ...}
        label_dict = get_label_dict(category_to_class.values())      # {"B-TOA": 0, "I-TOA", 1, ...}
        print("label_dict =", label_dict, sep="\n")
        pattern = compile(fr'T(?P<num_tokens>\d+)(?P<cat>[{"".join(category_to_class)}]*)')
        add_bio_class_as_prefix = True
        empty_to_X = True

    elif args.entities_class == "ONOMASTIC":
        bio_main_class = ""
        classes = ["ISM", "KUN", "LQB", "NAS", "NSB", "SHR"]
        category_to_class = {c: bio_main_class+c for c in classes}
        label_dict = get_label_dict(category_to_class.values())
        print("label_dict =", label_dict, sep="\n")
        pattern = compile(fr'(?P<cat>{"|".join(category_to_class)})(?P<num_tokens>\d+)')

    #TODO
    elif args.entities_class == "NASAB":
        ...
    elif args.entities_class == "NER":
        ...
    elif args.entities_class == "TOPONYM_DESC":
        ...
    elif args.entities_class == "PERSON_FCON":
        ...
    elif args.entities_class == "PERSON_FCON":
        ...

    class_args = {
        "pattern": pattern,
        "bio_main_class": bio_main_class,
        "label_dict": label_dict,
        "keep_automatic_tags": args.keep_automatic_tags,
        "add_bio_class_as_prefix": add_bio_class_as_prefix,
        "empty_to_X": empty_to_X
    }

    res = []
    if args.debug:
        for idx, miu in tqdm(list(enumerate(mius))):
            try:
                res.append(get_data(miu, **class_args))
            except Exception as e:
                print(f"Error idx={idx} miu={miu}: {e}")
    else:
        res += p_uimap(
            partial(get_data, **class_args),
            mius,
            total=len(mius)
        )

    reviewed, bio_dicts = zip(*res)
    bio_dicts = [r for r in bio_dicts if r is not None]

    out_file_path = RESEARCH_DATA_REPO + args.out_file + '_' + date.today().isoformat() + '.json'

    with open(out_file_path, 'w', encoding='utf-8') as fh:
        dump(bio_dicts, fh, indent=4, ensure_ascii=False)

    print(f'Output saved in file {out_file_path}')

    print(pd.Series(reviewed).value_counts())
    print('Done')
