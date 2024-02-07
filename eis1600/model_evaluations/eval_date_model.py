from pathlib import Path
from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import Dict, List, Tuple

from p_tqdm import p_uimap

from json import dump
from datetime import datetime
from numpy import nan
from pandas import concat, DataFrame, notna, Series
import evaluate
from tensorflow import constant
from tensorflow.python.keras.metrics import MeanAbsoluteError, MeanAbsolutePercentageError

from eis1600.bio.md_to_bio import md_to_bio
from eis1600.dates.date_patterns import DATE_CATEGORIES_REPLACEMENTS, DATE_LABEL_DICT
from eis1600.dates.date_methods import date_annotate_miu_text
from eis1600.markdown.markdown_patterns import YEAR_PATTERN
from eis1600.model_evaluations.EvalResultsEncoder import EvalResultsEncoder
from eis1600.depricated.disassemble_reassemble_methods import get_yml_and_miu_df
from eis1600.repositories.repo import TRAINING_DATA_REPO, TRAINING_RESULTS_REPO


def reconstruct_automated_tag(row) -> str:
    return 'ÜY' + row['num_tokens'] + row['cat'] + row['written'] + 'Y'


def get_year_true_pred(row: Series) -> Series:
    """Get numerical values for ground-truth and prediction.

    :param Series row: row has values for 'written_true' and 'written_pred'.
    :return Series: Series of 'true' and 'pred'.
    """
    if notna(row['written_true']):
        v_true = int(row['written_true'])
    else:
        v_true = nan

    if notna(row['written_pred']) and row['written_pred'] != 'None':
        v_pred = int(row['written_pred'])
    else:
        v_pred = nan

    return Series([v_true, v_pred], index=['true', 'pred'])


def get_dates_true_and_pred(file: str) -> Tuple[DataFrame, Dict, Dict]:
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
    df_true = s_notna.str.extract(YEAR_PATTERN).dropna(how='all')
    dates = df_true.apply(reconstruct_automated_tag, axis=1)
    dates.name = 'DATES_TRUE'

    if not dates.empty:
        df = df.join(dates)
    else:
        df['DATES_TRUE'] = nan

    # Predict dates based on the text as EIS1600 tags
    df['DATES_PRED'] = date_annotate_miu_text(df[['TOKENS']], file)

    if any(df['DATES_PRED'].notna()):
        df_pred = df['DATES_PRED'].str.extract(YEAR_PATTERN).dropna(how='all')
    else:
        df_pred = DataFrame(columns=['written'])

    year = DataFrame(columns=['true', 'pred'])

    # Get information from the EIS1600 tags for predictions and ground-truth
    if not dates.empty:
        df_year = df_true[['written']].join(df_pred['written'], lsuffix='_true', rsuffix='_pred')
        year[['true', 'pred']] = df_year.apply(get_year_true_pred, axis=1)
    elif not df_pred.empty:
        df_year = df_pred[['written']].join(df_true['written'], rsuffix='_true', lsuffix='_pred')
        year[['true', 'pred']] = df_year.apply(get_year_true_pred, axis=1)

    year.dropna(inplace=True)

    # Parse EIS1600 tags to BIO tags for predictions and ground-truth
    bio_true = md_to_bio(
            df[['TOKENS', 'DATES_TRUE']],
            'DATES_TRUE',
            YEAR_PATTERN,
            'YY',
            DATE_LABEL_DICT,
            True,
            DATE_CATEGORIES_REPLACEMENTS
    )
    bio_pred = md_to_bio(
            df[['TOKENS', 'DATES_PRED']],
            'DATES_PRED',
            YEAR_PATTERN,
            'YY',
            DATE_LABEL_DICT,
            True,
            DATE_CATEGORIES_REPLACEMENTS
    )

    return year, bio_true, bio_pred


def eval_dates_entity_recognition_and_classification(truth: List[List[str]], predictions: List[List[str]]) -> Dict:
    """Evaluates predicted BIO-labels based on their ground-truth.

    Evaluates predicted BIO-labels based on their ground-truth, giving each of the following metrics for every class:
    precision, recall, F1-score, accuracy.

    :param List[List[str]] truth: A list of records, where each record is a list of the true BIO-tags for that text.
    :param List[List[str]] predictions: A list of records, where each record is a list of the predicted BIO-tags for
    that text.
    :return Dict: Dict containing the evaluation results: precision, recall, F1 for each class.
    """
    all_metrics = evaluate.load("seqeval").compute(predictions=predictions, references=truth)

    return all_metrics


def eval_year(year: DataFrame) -> Dict:
    """Evaluates the predictions of the numerical value of all recognized date with MAPE and MAE.

    :param DataFrame year: DataFrame with two columns, column 'true' with the ground-truth values and column 'pred'
    with the predicted values.
    :return Dict: Dict containing the evaluation results: Mean Average Percentage Error and Mean Average Error.
    """
    all_metrics = {}
    truth = constant(year['true'].astype('float32'))
    predictions = constant(year['pred'].astype('float32'))

    mape = MeanAbsolutePercentageError()
    mape.update_state(y_true=truth, y_pred=predictions)
    mae_no_nan = MeanAbsoluteError()
    mae_no_nan.update_state(y_true=truth, y_pred=predictions)

    all_metrics['mape'] = mape.result().numpy()
    all_metrics['mae'] = mae_no_nan.result().numpy()

    return all_metrics


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

    infiles = [TRAINING_DATA_REPO + 'gold_standard/' + file for file in files_txt if Path(
            TRAINING_DATA_REPO + 'gold_standard/' + file).exists()]

    res = []
    if debug:
        for i, file in enumerate(infiles):
            print(i, file)
            res.append(get_dates_true_and_pred(file))
    else:
        res += p_uimap(get_dates_true_and_pred, infiles)

        years, truth, predictions = zip(*res)

        with open(TRAINING_DATA_REPO + 'dates_truth.json', 'w', encoding='utf-8') as fh:
            dump(truth, fh, indent=4, ensure_ascii=False)
        with open(TRAINING_DATA_REPO + 'dates_predictions.json', 'w', encoding='utf-8') as fh:
            dump(predictions, fh, indent=4, ensure_ascii=False)

    truth = []
    predictions = []
    year_df = DataFrame(columns=['true', 'pred'])

    for year, bio_true, bio_pred in res:
        truth.append(bio_true['ner_classes'])
        predictions.append(bio_pred['ner_classes'])
        if not year.empty:
            year_df = concat([year_df, year])

    all_metrics = {
            'model': 'dates-rule-based'
    }
    all_metrics.update(eval_dates_entity_recognition_and_classification(truth, predictions))
    all_metrics.update(eval_year(year_df))

    with open(TRAINING_RESULTS_REPO + 'dates/result-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.json', 'w',
              encoding='utf-8') as fh:
        dump(all_metrics, fh, cls=EvalResultsEncoder)

    print('Done')
