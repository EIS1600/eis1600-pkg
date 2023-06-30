from pathlib import Path
from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import Dict, Union
from re import compile

from json import dump
from p_tqdm import p_uimap

from eis1600.helper.repo import TOPO_TRAINING_REPO, TRAINING_DATA_REPO
from eis1600.miu.methods import get_yml_and_miu_df
from eis1600.toponyms.toponym_categories import TOPONYM_CATEGORIES

print(TOPONYM_CATEGORIES)
CATS = ''.join(TOPONYM_CATEGORIES)
TOP_PATTERN = compile(r"T(?P<num_tokens>\d)(?P<category>[" + CATS + "])")
categories = ["TO" + c for c in TOPONYM_CATEGORIES]
BIO = ["B", "I"]

labels = [bi + "-" + c for c in categories for bi in BIO] + ["O"]
label_dict = {}

for i, label in enumerate(labels):
    label_dict[label] = i


def top_tag_to_bio(md_tag):
    m = TOP_PATTERN.search(md_tag)
    num_tokens = int(m.group("len"))
    cat = m.group("cat")

    bio_tags = []
    while len(bio_tags) < num_tokens:
        if len(bio_tags) == 0:
            bio_tags.append("B-TO" + cat)
        else:
            bio_tags.append("I-TO" + cat)

    return bio_tags


def md_to_bio(file: str) -> Union[Dict, None]:
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object, keep_automatic_tags=True)

    if not yml_handler.is_bio():
        return None

    s_notna = df['TAGS_LISTS'].loc[df['TAGS_LISTS'].notna()].apply(lambda tag_list: ','.join(tag_list))
    df_matches = s_notna.str.extract(TOP_PATTERN).dropna()

    if df_matches.empty:
        return None

    for index, row in df_matches.iterrows():
        processed_tokens = 0
        num_tokens = int(row['num_tokens'])
        while processed_tokens < num_tokens:
            if processed_tokens == 0:
                df.loc[index, 'BIO'] = 'B-TO' + row['category']
            else:
                df.loc[index + processed_tokens, 'BIO'] = 'I-TO' + row['category']

            processed_tokens += 1

    df["BIO"].loc[df["BIO"].isna()] = "O"
    df["BIO_IDS"] = df["BIO"].apply(lambda bio_tag: label_dict[bio_tag])

    idcs = df["TOKENS"].loc[df["TOKENS"].notna()].index

    return {
            "tokens": df["TOKENS"].loc[idcs].to_list(),
            "ner_tags": df["BIO_IDS"].loc[idcs].to_list(),
            "ner_classes": df["BIO"].loc[idcs].to_list()
    }


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to annotate onomastic information in gold-standard MIUs.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')

    args = arg_parser.parse_args()
    debug = args.debug

    with open(TRAINING_DATA_REPO + 'gold_standard.txt', 'r', encoding='utf-8') as fh:
        files_txt = fh.read().splitlines()

    infiles = [TRAINING_DATA_REPO + 'gold_standard_topo/' + file for file in files_txt if Path(
            TRAINING_DATA_REPO + 'gold_standard_topo/' + file).exists()]

    if debug:
        for file in infiles[:20]:
            print(file)
            md_to_bio(file)
    else:
        res = []
        res += p_uimap(md_to_bio, infiles)

        print(len(res))
        print(len([r for r in res if r is not None]))

        with open(TOPO_TRAINING_REPO + 'toponyms_category_training_data.json', 'w', encoding='utf-8') as fh:
            dump([r for r in res if r is not None], fh, indent=4, ensure_ascii=False)

    print('Done')
