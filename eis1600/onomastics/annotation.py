from eis1600.gazetteers.Toponyms import Toponyms
from functools import partial
from glob import glob

from p_tqdm import p_uimap
from typing import List, Tuple, Type

import pandas as pd

from eis1600.gazetteers.Onomastics import Onomastics
from eis1600.onomastics.re_pattern import ABU_ABI, BANU_BANI, IBN_IBNA, BN_BNT, DIN_DAULA, DATES, PARENTHESIS, \
    QUOTES, PUNCTUATION, SPACES, UMM, YURIFA_K_BI
from eis1600.preprocessing.methods import get_yml_and_MIU_df


def nasab_analysis(file, og: Type[Onomastics], tg: Type[Toponyms]) -> Tuple[List[str], str, str, str]:
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_header, df = get_yml_and_MIU_df(miu_file_object)

    # if not yml_header.is_bio():
    #     return [], '', ''

    idcs = df[df['TOKENS'].isin(og.end())].index
    idx = idcs[0] if idcs.any() else min(99, len(df))

    text = ' '.join(df['TOKENS'][df['TOKENS'].notna()].iloc[:idx - 1])
    text_w_cutoff = f'{file}\n' + ' '.join(df['TOKENS'][df['TOKENS'].notna()].iloc[:idx])

    text_mnpld = text
    text_mnpld = PARENTHESIS.sub(r'\g<1>', text_mnpld)
    text_mnpld = QUOTES.sub('', text_mnpld)
    text_mnpld = DATES.sub('', text_mnpld)
    text_mnpld = PUNCTUATION.sub('', text_mnpld)
    text_mnpld = SPACES.sub(' ', text_mnpld)
    text_mnpld = ABU_ABI.sub('ابو_', text_mnpld)
    text_mnpld = UMM.sub('ام_', text_mnpld)
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

    return unknown, text, text_mnpld, text_w_cutoff


def main():
    og = Onomastics.instance()
    tg = Toponyms.instance()
    infiles = glob('OpenITI_EIS1600_MIUs/training_data/*.EIS1600')#[:100]

    res = []
    res += p_uimap(partial(nasab_analysis, og=og, tg=tg), infiles)

    unknown, nasabs, manipulated, cutoff = zip(*res)

    with open('OnomasticonArabicum2020/oa2020/nasabs.txt', 'w', encoding='utf-8') as fh:
        fh.write('\n\n'.join([f'1\n{nsb}\n2\n{co}' for u, nsb, m, co in res]))

    with open('OnomasticonArabicum2020/oa2020/manipulated.txt', 'w', encoding='utf-8') as fh:
        fh.write('\n\n'.join(manipulated))

    unknown_flat = pd.Series([elem for sub in unknown for elem in sub])
    unknown_flat.value_counts().to_csv('OnomasticonArabicum2020/oa2020/unknown.csv')
