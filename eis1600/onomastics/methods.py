import pandas as pd

from eis1600.miu.YAMLHandler import YAMLHandler
from typing import List, Tuple, Type

from eis1600.gazetteers.Onomastics import Onomastics
from eis1600.gazetteers.Toponyms import Toponyms
from eis1600.onomastics.re_pattern import ABU_ABI, BANU_BANI, IBN_IBNA, BN_BNT, DIN_DAULA, DATES, PARENTHESIS, \
    QUOTES, PUNCTUATION, SPACES, SPELLING, UMM, YURIFA_K_BI
from eis1600.preprocessing.methods import get_tokens_and_tags, get_yml_and_MIU_df, reconstruct_miu_text_with_tags, \
    write_updated_miu_to_file


def nasab_filtering(nasab_text, og: Type[Onomastics], tg: Type[Toponyms]) -> Tuple[List[str], str]:
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

    tokens = text_mnpld.split()
    unknown = [t for t in tokens if '_' not in t and t not in og.total() + tg.total()]

    return unknown, text_mnpld


def tag_nasab(text: str, og: Type[Onomastics]) -> str:
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
    text_updated = text
    m = SPELLING.search(text_updated)
    while m:
        tag = 'ÜSPL' + str(len(m.group(0).split())) + ' '
        pos = m.start()
        text_updated = text_updated[:pos] + tag + text_updated[pos:]

        m = SPELLING.search(text_updated, m.end() + len(tag))

    return text_updated


# def nasab_annotation(file, og: Type[Onomastics], tg: Type[Toponyms]) -> Tuple[List[str], Type[YAMLHandler], str]:
def nasab_annotation(file, og: Type[Onomastics], tg: Type[Toponyms]) -> Tuple[str, List[str]]:
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_header, df = get_yml_and_MIU_df(miu_file_object)

    # if not yml_header.is_bio():
    #     return [], '', ''
    if '$' not in df.iloc[0]['SECTIONS'] or '$$$' in df.iloc[0]['SECTIONS'] or not yml_header.is_reviewed():
        return '', []

    # For not annotated MIUs
    # idcs = df[df['TOKENS'].notna() & df['TOKENS'].isin(og.end())].index
    # idx = idcs[0] if idcs.any() else min(49, len(df))

    # Only for pre-annotated MIUs
    s_notna = df['TAGS_LISTS'].loc[df['TAGS_LISTS'].notna()].apply(lambda tag_list: ','.join(tag_list))
    idx = s_notna.loc[s_notna.str.contains('NASAB')].index[0]

    nasab_idx = df['TOKENS'].loc[df['TOKENS'].notna()].iloc[:idx - 2].index

    text = ' '.join(df['TOKENS'].loc[nasab_idx])

    unknown, nasab_filtered = nasab_filtering(text, og, tg)
    yml_header.add_nasab_filtered(nasab_filtered)
    yml_header.unset_reviewed()

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

    tagged_onomastics = tag_nasab(text, og)
    ar_tokens, tags = get_tokens_and_tags(tagged_onomastics)
    df.loc[nasab_idx, 'NASAB_TAGS'] = tags

    if idx != len(df):
        # TODO make NASAB stay on same line
        df.loc[idx - 1, 'NASAB_END'] = 'NASAB'

    reconstructed_miu = reconstruct_miu_text_with_tags(df[['SECTIONS', 'TOKENS', 'NASAB_TAGS']])

    output_path = str(file).replace('training_data', 'training_nasab')
    with open(output_path, 'w', encoding='utf-8') as out_file_object:
        write_updated_miu_to_file(
            out_file_object, yml_header, df[['SECTIONS', 'TOKENS', 'TAGS_LISTS', 'NASAB_TAGS']], True
        )

    # return df['NASAB_TAGS'].fillna('').tolist(), yml_header, text_w_cutoff

    return f'{file}\n' + reconstructed_miu, unknown
