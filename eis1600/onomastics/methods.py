from camel_tools.tokenizers.word import simple_word_tokenize
from eis1600.miu.YAMLHandler import YAMLHandler
from typing import List, Tuple, Type

from eis1600.gazetteers.Onomastics import Onomastics
from eis1600.gazetteers.Toponyms import Toponyms
from eis1600.onomastics.re_pattern import ABU_ABI, BANU_BANI, IBN_IBNA, BN_BNT, DIN_DAULA, DATES, PARENTHESIS, \
    QUOTES, PUNCTUATION, SPACES, UMM, YURIFA_K_BI
from eis1600.preprocessing.methods import get_yml_and_MIU_df


def nasab_filtering(file, og: Type[Onomastics], tg: Type[Toponyms]) -> Tuple[List[str], str, str, str]:
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_header, df = get_yml_and_MIU_df(miu_file_object)

    # if not yml_header.is_bio():
    #     return [], '', ''

    idcs = df[df['TOKENS'].isin(og.end())].index
    idx = idcs[0] if idcs.any() else min(49, len(df))

    text = ' '.join(df['TOKENS'][df['TOKENS'].notna()].iloc[:idx - 1])
    text_w_cutoff = f'{file}\n' + ' '.join(df['TOKENS'][df['TOKENS'].notna()].iloc[:idx])

    text_mnpld = text
    text_mnpld = PARENTHESIS.sub(r'\g<1>', text_mnpld)
    text_mnpld = QUOTES.sub('', text_mnpld)
    text_mnpld = DATES.sub('', text_mnpld)
    text_mnpld = PUNCTUATION.sub('', text_mnpld)
    text_mnpld = SPACES.sub(' ', text_mnpld)
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

    return unknown, text, text_mnpld, text_w_cutoff


def tag_nasab(text: str, og: Type[Onomastics]) -> str:
    text_updated = text
    m = og.get_ngrams_regex().search(text_updated)
    while m:
        tag = og.get_ngram_tag(m.group(1))
        pos = m.start()
        if m.group(0)[0] == ' ':
            pos += 1
        text_updated = text_updated[:pos] + tag + text_updated[pos:]

        m = og.get_ngrams_regex().search(text_updated, m.end() + len(tag))

    return text_updated


# def nasab_annotation(file, og: Type[Onomastics], tg: Type[Toponyms]) -> Tuple[List[str], Type[YAMLHandler], str]:
def nasab_annotation(file, og: Type[Onomastics], tg: Type[Toponyms]) -> str:
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_header, df = get_yml_and_MIU_df(miu_file_object)

    # if not yml_header.is_bio():
    #     return [], '', ''

    idcs = df[df['TOKENS'].isin(og.end())].index
    idx = idcs[0] if idcs.any() else min(49, len(df))

    text = ' '.join(df['TOKENS'][df['TOKENS'].notna()].iloc[:idx - 1])

    tagged_text = tag_nasab(text, og)

    return f'{file}\n_ء_ ' + tagged_text

    # tokens = simple_word_tokenize(tagged_text)
    # ar_tokens, tags = [], []
    # tag = None
    # for t in tokens:
    #     if TAG_PATTERN.match(t):
    #         tag = t
    #     else:
    #         ar_tokens.append(t)
    #         tags.append(tag)
    #         tag = None

    # df.loc[df['TOKENS'].notna(), 'NASAB_TAGS'] = tags

    # return df['NASAB_TAGS'].fillna('').tolist(), yml_header, text_w_cutoff
