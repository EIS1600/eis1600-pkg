from pathlib import Path
from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import Dict, Tuple

from p_tqdm import p_uimap

from json import dump
from datetime import datetime
from numpy import nan
from pandas import notna

from eis1600.bio.md_to_bio import md_to_bio
from eis1600.markdown.markdown_patterns import TOPONYM_PATTERN
from eis1600.model_evaluations.EvalResultsEncoder import EvalResultsEncoder
from eis1600.model_evaluations.eval_date_model import eval_dates_entity_recognition_and_classification
from eis1600.depricated.disassemble_reassemble_methods import get_yml_and_miu_df
from eis1600.repositories.repo import TRAINING_DATA_REPO, TRAINING_RESULTS_REPO
from eis1600.toponyms.methods import toponym_category_annotate_miu
from eis1600.toponyms.toponym_categories import TOPONYM_CATEGORIES_REPLACEMENTS, TOPONYM_LABEL_DICT


def combine_tokens_and_tags(row) -> str:
    return row['TOPONYMS_TRUE'][:-1] + ' ' + row['TOKENS']


def remove_category(val: str) -> str:
    if notna(val):
        return val[:-1]
    else:
        return val


def reconstruct_automated_tag(row) -> str:
    return 'ÜT' + row['num_tokens'] + row['cat']


def get_dates_true_and_pred(file: str) -> Tuple[Dict, Dict]:
    """Get ground-truth and prediction on labels and numerical values for MIU.

    :param str file: file path for MIU file.
    :param Dict bio_dict: BIO labels dictionary.
    :return Tuple[DataFrame, Dict, Dict]: DataFrame year contains two columns ('true' and 'pred'), the other two are
    dictionaries, one with the BIO labels derived from the ground-truth and the other with the BIO labels based on
    the predictions.
    """
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object)

    # Extract the ground-truth annotated with EIS1600 tags
    s_notna = df['TAGS_LISTS'].loc[df['TAGS_LISTS'].notna()].apply(lambda tag_list: ','.join(tag_list))
    df_true = s_notna.str.extract(TOPONYM_PATTERN).dropna(how='all')
    toponyms = df_true.apply(reconstruct_automated_tag, axis=1)
    toponyms.name = 'TOPONYMS_TRUE'

    if not toponyms.empty:
        df = df.join(toponyms)
    else:
        df['TOPONYMS_TRUE'] = nan

    # Predict dates based on the text as EIS1600 tags
    df['TOPONYMS_PRED'] = toponym_category_annotate_miu(df['TOKENS'], df['TOPONYMS_TRUE'].apply(remove_category))

    # Parse EIS1600 tags to BIO tags for predictions and ground-truth
    bio_true = md_to_bio(
            df[['TOKENS', 'TOPONYMS_TRUE']],
            'TOPONYMS_TRUE',
            TOPONYM_PATTERN,
            'TO',
            TOPONYM_LABEL_DICT,
            True,
            TOPONYM_CATEGORIES_REPLACEMENTS
    )
    bio_pred = md_to_bio(
            df[['TOKENS', 'TOPONYMS_PRED']],
            'TOPONYMS_PRED',
            TOPONYM_PATTERN,
            'TO',
            TOPONYM_LABEL_DICT,
            True,
            TOPONYM_CATEGORIES_REPLACEMENTS
    )

    return bio_true, bio_pred


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to annotate onomastic information in gold-standard MIUs.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')

    args = arg_parser.parse_args()
    debug = args.debug

    with open(TRAINING_DATA_REPO + '5k_gold_standard.txt', 'r', encoding='utf-8') as fh:
        files_txt = fh.read().splitlines()

    infiles = [TRAINING_DATA_REPO + '5k_gold_standard/' + file for file in files_txt if Path(
            TRAINING_DATA_REPO + '5k_gold_standard/' + file
    ).exists()]

    res = []
    if debug:
        for i, file in enumerate(infiles):
            print(i, file)
            res.append(get_dates_true_and_pred(file))
    else:
        res += p_uimap(get_dates_true_and_pred, infiles)

        truth, predictions = zip(*res)

        with open(TRAINING_DATA_REPO + 'toponyms_truth.json', 'w', encoding='utf-8') as fh:
            dump(truth, fh, indent=4, ensure_ascii=False)
        with open(TRAINING_DATA_REPO + 'toponyms_predictions.json', 'w', encoding='utf-8') as fh:
            dump(predictions, fh, indent=4, ensure_ascii=False)

    truth = []
    predictions = []

    for bio_true, bio_pred in res:
        truth.append(bio_true['ner_classes'])
        predictions.append(bio_pred['ner_classes'])

    all_metrics = {
            'model': 'toponyms-rule-based'
    }
    all_metrics.update(eval_dates_entity_recognition_and_classification(truth, predictions))

    with open(TRAINING_RESULTS_REPO + 'toponyms/result-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.json', 'w',
              encoding='utf-8') as fh:
        dump(all_metrics, fh, cls=EvalResultsEncoder)

    print('Done')
