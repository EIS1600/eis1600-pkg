from logging import Logger
from pathlib import Path
from typing import Optional

import pandas as pd
from numpy import nan
from pandas import Series

from eis1600.miu.YAMLHandler import YAMLHandler

from eis1600.gazetteers.Onomastics import Onomastics
from eis1600.gazetteers.Toponyms import Toponyms
from eis1600.onomastics.re_pattern import ABU_ABI, BANU_BANI, IBN_IBNA, BN_BNT, DIN_DAULA, DATES, PARENTHESIS, \
    QUOTES, PUNCTUATION, SPACES, SPELLING, UMM, YURIFA_K_BI
from eis1600.preprocessing.methods import get_tokens_and_tags, get_yml_and_miu_df, reconstruct_miu_text_with_tags, \
    write_updated_miu_to_file


def nasab_filtering(nasab_text: str, yml_handler: YAMLHandler, logger_nasab: Logger) -> None:
    """Filters elements from the nasab which were not recognized by the current onomastic gazetteer.

    Filters elements from the nasab which were not recognized by the current onomastic gazetteer. Unrecognized uni-
    and bi-grams are logged and the manipulated nasab string is added to the YAMLHandler.
    :param str nasab_text: nasab text as one single string which was cleaned from spelling information.
    :param YAMLHandler yml_handler: YAMLHandler of the MIU to which the manipulated nasab string is added.
    :param Logger logger_nasab: logger for unrecognized uni- and bi-grams.
    """
    og = Onomastics.instance()
    tg = Toponyms.instance()
    text_mnpld = nasab_text
    text_mnpld = PARENTHESIS.sub(r'\g<1>', text_mnpld)
    text_mnpld = QUOTES.sub('', text_mnpld)
    text_mnpld = DATES.sub('', text_mnpld)
    text_mnpld = PUNCTUATION.sub('', text_mnpld)
    text_mnpld = SPACES.sub(' ', text_mnpld)
    m = SPELLING.search(text_mnpld)
    while m:
        text_mnpld = text_mnpld[:m.start()] + m.group(0).replace(' ', '_') + text_mnpld[m.end():]
        m = SPELLING.search(text_mnpld, m.end())

    m = og.get_ngrams_regex().search(text_mnpld)
    while m:
        text_mnpld = text_mnpld[:m.start()] + m.group(1) + m.group(2).replace(' ', '_') + text_mnpld[m.end():]
        m = og.get_ngrams_regex().search(text_mnpld, m.end())

    # They should be catched by regex - no manual manipulation
    # text_mnpld = ABU_ABI.sub(' ابو_', text_mnpld)
    # text_mnpld = UMM.sub(' ام_', text_mnpld)
    # text_mnpld = IBN_IBNA.sub(r'\g<1>', text_mnpld)
    # text_mnpld = BN_BNT.sub(r'_\g<1>_', text_mnpld)
    # text_mnpld = DIN_DAULA.sub(r'_\g<1>', text_mnpld)
    # text_mnpld = YURIFA_K_BI.sub('\g<1>_\g<2>_\g<3>', text_mnpld)
    text_mnpld = BANU_BANI.sub('<بنو_', text_mnpld)
    for elem in tg.total():
        text_mnpld = text_mnpld.replace('نائب ' + elem, 'نائب_' + elem)
    for elem, repl in tg.replacements():
        text_mnpld = text_mnpld.replace(elem, repl)

    yml_handler.add_nasab_filtered(text_mnpld)

    if logger_nasab:
        # Log unidentified tokens as uni- and bi-grams
        tokens = text_mnpld.split()
        unknown_uni = [t for t in tokens if '_' not in t and t not in og.total() + tg.total()]
        prev = None
        unknown_bi = []
        for t in tokens:
            if not prev and '_' not in t and t not in og.total() + tg.total() + ['بن', 'بنت']:
                prev = t
            else:
                if '_' not in t and t not in og.total() + tg.total() + ['بن', 'بنت']:
                    unknown_bi.append(prev + ' ' + t)
                    prev = t
                else:
                    prev = None
        logger_nasab.info('\n'.join(unknown_uni + unknown_bi))


def tag_nasab(text: str) -> str:
    """Annotate the nasab part of the MIU.

    :param str text: nasab part of the MIU as one single string.
    :return str: the nasab part pf the MIU which contains also the tags in front of the recognized elements.
    """
    og = Onomastics.instance()
    text_updated = text
    m = og.get_ngrams_regex().search(text_updated)
    while m:
        tag = og.get_ngram_tag(m.group(2))
        pos = m.start()
        if m.group(1) == ' ':
            pos += 1
        text_updated = text_updated[:pos] + tag + text_updated[pos:]

        m = og.get_ngrams_regex().search(text_updated, m.end() + len(tag))

    return text_updated


def tag_spelling(text: str) -> str:
    """Tags spelling information which is stated in the nasab part of the MIU text.

    Spelling is detected when two elements of the spelling gazetteer are found successively.
    :param str text: the nasab part as one string.
    :return str: nasab part as one string including tags for found spelling.
    """
    text_updated = text
    m = SPELLING.search(text_updated)
    while m:
        tag = 'ÜSPL' + str(len(m.group(0).split())) + ' '
        pos = m.start()
        text_updated = text_updated[:pos] + tag + text_updated[pos:]

        m = SPELLING.search(text_updated, m.end() + len(tag))

    return text_updated


def nasab_annotate_miu(df: pd.DataFrame, yml_handler: YAMLHandler, file: str, logger_nasab: Optional[Logger]) -> \
        Series:
    """Onomastic analysis of the nasab part of the MIU.

    :param DataFrame df: DataFrame of the MIU.
    :param YAMLHandler yml_handler: YAMLHandler of the MIU.
    :param Path file: the MIU which was opened.
    :param Logger logger_nasab: logs unrecognized uni- and bi-grams to a log file, optional.
    :return Series: a series of the same length as the df containing the nasab tags corresponding to the tokens.
    """
    if not yml_handler.is_bio():
        return Series([nan] * len(df))

    s_notna = df['TAGS_LISTS'].loc[df['TAGS_LISTS'].notna()].apply(lambda tag_list: ','.join(tag_list))
    try:
        idx = s_notna.loc[s_notna.str.contains('NASAB')].index[0]
    except IndexError:
        print(
                f'MIU does not have a NASAB tag, most likely the MIU is not a biography but a cross reference. '
                f'Check:\n{file}'
        )
        return Series([nan] * len(df))

    nasab_idx = df['TOKENS'].loc[df['TOKENS'].notna()].iloc[:idx - 2].index

    text = ' '.join(df['TOKENS'].loc[nasab_idx])

    nasab_filtering(text, yml_handler, logger_nasab)

    tagged_spelling = tag_spelling(text)
    ar_tokens, tags = get_tokens_and_tags(tagged_spelling)
    df.loc[nasab_idx, 'NASAB_TAGS'] = tags

    count = 0
    spl_idcs = []
    for row in df.loc[nasab_idx].itertuples():
        if pd.notna(row[4]):
            count = int(row[4][-1])
        if count > 0:
            count -= 1
            spl_idcs.append(row[0])

    nasab_idx = df.loc[nasab_idx.difference(spl_idcs)].index
    text = ' '.join(df['TOKENS'].loc[nasab_idx])

    tagged_onomastics = tag_nasab(text)
    ar_tokens, tags = get_tokens_and_tags(tagged_onomastics)
    df.loc[nasab_idx, 'NASAB_TAGS'] = tags

    if idx != len(df):
        # TODO make NASAB stay on same line
        df.loc[idx - 1, 'NASAB_END'] = 'NASAB'

    return df['NASAB_TAGS'].to_list()


def nasab_annotation(file: str, logger_nasab: Logger) -> str:
    """Only used for onomastic_annotation cmdline script."""
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object)
    if '$' not in df.iloc[0]['SECTIONS'] or '$$$' in df.iloc[0]['SECTIONS'] or not yml_handler.is_reviewed():
        df['NASAB_TAGS'] = Series([nan] * len(df))
    else:
        yml_handler.set_category('$')
        df['NASAB_TAGS'] = nasab_annotate_miu(df, yml_handler, file, logger_nasab)

    yml_handler.unset_reviewed()

    reconstructed_miu = reconstruct_miu_text_with_tags(df[['SECTIONS', 'TOKENS', 'NASAB_TAGS']])

    output_path = str(file).replace('training_data', 'training_nasab')
    with open(output_path, 'w', encoding='utf-8') as out_file_object:
        write_updated_miu_to_file(
            out_file_object, yml_handler, df[['SECTIONS', 'TOKENS', 'TAGS_LISTS', 'NASAB_TAGS']]
        )

    return f'{file}\n' + reconstructed_miu
