import sys

import pandas as pd
from camel_tools.tokenizers.word import simple_word_tokenize

from eis1600.markdown.re_pattern import TAG_PATTERN
from eis1600.miu.YAMLHandler import YAMLHandler
from typing import List, Tuple, Type

from eis1600.gazetteers.Onomastics import Onomastics
from eis1600.gazetteers.Toponyms import Toponyms
from eis1600.onomastics.re_pattern import ABU_ABI, BANU_BANI, IBN_IBNA, BN_BNT, DIN_DAULA, DATES, PARENTHESIS, \
    QUOTES, PUNCTUATION, SPACES, SPELLING, UMM, YURIFA_K_BI
from eis1600.preprocessing.methods import get_yml_and_MIU_df, reconstruct_miu_text_with_tags


def nasab_filtering(file, og: Type[Onomastics], tg: Type[Toponyms]) -> Tuple[List[str], str, str, str, str]:
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_header, df = get_yml_and_MIU_df(miu_file_object)

    # if not yml_header.is_bio():
    #     return [], '', ''

    idcs = df[df['TOKENS'].isin(og.end())].index
    idx = idcs[0] if idcs.any() else min(49, len(df))

    text = ' '.join(df['TOKENS'][df['TOKENS'].notna()].iloc[:idx - 1])
    text_w_cutoff = f'{file}\n' + ' '.join(df['TOKENS'][df['TOKENS'].notna()].iloc[:idx])
    spelling = f'{file}\n'

    text_mnpld = text
    text_mnpld = PARENTHESIS.sub(r'\g<1>', text_mnpld)
    text_mnpld = QUOTES.sub('', text_mnpld)
    text_mnpld = DATES.sub('', text_mnpld)
    text_mnpld = PUNCTUATION.sub('', text_mnpld)
    text_mnpld = SPACES.sub(' ', text_mnpld)
    if SPELLING.search(text_mnpld):
        m = SPELLING.search(text_mnpld)
        spelling += m.group(0) + '\n'
        text_mnpld = text_mnpld[:m.start()] + m.group(0).replace(' ', '_') + text_mnpld[m.end():]
    text_mnpld = ABU_ABI.sub(' ابو_', text_mnpld)
    text_mnpld = UMM.sub(' ام_', text_mnpld)
    text_mnpld = IBN_IBNA.sub(r'ا\g<1>_', text_mnpld)
    text_mnpld = BN_BNT.sub(r'_\g<1>_', text_mnpld)
    text_mnpld = DIN_DAULA.sub(r'_\g<1>', text_mnpld)
    text_mnpld = BANU_BANI.sub('<بنو_', text_mnpld)
    for elem in tg.total():
        text_mnpld = text_mnpld.replace('نائب ' + elem, 'نائب_' + elem)
    for elem, repl in og.replacements():
        text_mnpld = text_mnpld.replace(elem, repl)
    for elem, repl in tg.replacements():
        text_mnpld = text_mnpld.replace(elem, repl)
    text_mnpld = YURIFA_K_BI.sub('\g<1>_\g<2>_\g<3>', text_mnpld)

    tokens = text_mnpld.split()
    unknown = [t for t in tokens if '_' not in t and t not in og.total() + tg.total()]

    return unknown, text, text_mnpld, text_w_cutoff, spelling


def tag_nasab(text: str, og: Type[Onomastics]) -> str:
    text_updated = text
    m = og.get_ngrams_regex().search(text_updated)
    while m:
        tag = og.get_ngram_tag(m.group(1))
        pos = m.start()
        # TODO not needed for MIUs as they always start with _ء_ followed by space
        if m.group(0)[0] == ' ':
            pos += 1
        text_updated = text_updated[:pos] + tag + text_updated[pos:]

        m = og.get_ngrams_regex().search(text_updated, m.end() + len(tag))

    return text_updated


def tag_spelling(text: str) -> str:
    text_updated = text
    m = SPELLING.search(text_updated)
    while m:
        tag = 'ÜSPL' + str(len(m.group(0).split())) + ' '
        pos = m.start()
        text_updated = text_updated[:pos] + tag + text_updated[pos:]

        m = SPELLING.search(text_updated, m.end() + len(tag))

    return text_updated


# def nasab_annotation(file, og: Type[Onomastics], tg: Type[Toponyms]) -> Tuple[List[str], Type[YAMLHandler], str]:
def nasab_annotation(file, og: Type[Onomastics], tg: Type[Toponyms]) -> str:
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_header, df = get_yml_and_MIU_df(miu_file_object)

    # if not yml_header.is_bio():
    #     return [], '', ''

    idcs = df[df['TOKENS'].notna() & df['TOKENS'].isin(og.end())].index
    idx = idcs[0] if idcs.any() else min(49, len(df))
    if idx != len(df):
        # TODO make NASAB stay on same line
        df.loc[idx - 1, 'NASAB_END'] = 'NASAB'

    nasab_idx = df['TOKENS'].loc[df['TOKENS'].notna()].iloc[:idx - 1].index

    text = ' '.join(df['TOKENS'].loc[nasab_idx])

    tagged_spelling = tag_spelling(text)

    tokens = simple_word_tokenize(tagged_spelling)
    ar_tokens, tags = [], []
    tag = None
    for t in tokens:
        if TAG_PATTERN.match(t):
            tag = t
        else:
            ar_tokens.append(t)
            tags.append(tag)
            tag = None

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

    tagged_text = tag_nasab(text, og)

    tokens = simple_word_tokenize(tagged_text)
    ar_tokens, tags = [], []
    tag = None
    for t in tokens:
        if TAG_PATTERN.match(t):
            tag = t
        else:
            ar_tokens.append(t)
            tags.append(tag)
            tag = None

    try:
        df.loc[nasab_idx, 'NASAB_TAGS'] = [tag.replace('___', '/') if tag else None for tag in tags]
    except ValueError:
        print(tagged_text)
        print(tags)
        print(f'{len(tags)} and nasab_idx {len(nasab_idx)}')
        print(df)
        print(nasab_idx)
        sys.exit()

    df['NASAB_TAGS'].loc[df['NASAB_TAGS'].notna()] = df['NASAB_TAGS'].loc[df['NASAB_TAGS'].notna()].apply(lambda tag:
                                                                                                          [tag])

    reconstructed_miu = reconstruct_miu_text_with_tags(df[['SECTIONS', 'TOKENS', 'NASAB_TAGS']])

    # return df['NASAB_TAGS'].fillna('').tolist(), yml_header, text_w_cutoff

    return f'{file}\n' + reconstructed_miu
