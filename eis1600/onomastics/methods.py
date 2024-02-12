from os import makedirs
from os.path import dirname
from pathlib import Path
from typing import Optional
from numpy import nan
from pandas import Series
from pandas import DataFrame, notna

from eis1600.gazetteers.Onomastics import Onomastics
from eis1600.gazetteers.Toponyms import Toponyms
from eis1600.helper.logging import setup_logger
from eis1600.onomastics.re_pattern import ABI, ABU, BN_BNT, CRF_PATTERN, IBN_IBNA, SHR_PATTERN, SPELLING, UMM
from eis1600.processing.postprocessing import write_updated_miu_to_file
from eis1600.processing.preprocessing import get_tokens_and_tags, get_yml_and_miu_df
from eis1600.repositories.repo import GAZETTEERS_REPO
from eis1600.yml.YAMLHandler import YAMLHandler

__log_filename = GAZETTEERS_REPO + 'logs/nasab_unknown.log'
makedirs(dirname(__log_filename), exist_ok=True)
LOGGER_NASAB_UNKNOWN = setup_logger('nasab_unknown', __log_filename)


def get_nas(text: str) -> str:
    """Add the list of forefathers to the YAMLHeader and return nasab part with tagged NAS and manipulated so it is
    ignored for further onomastic analysis (all elements which refere to ancestors are filtered here).

    :param str text: nasab str.
    :return str: nasab str with tagged and manipulated nas elements.
    """
    text_mnpld = ABU.sub(' ابو_', text)
    text_mnpld = UMM.sub(' ام_', text_mnpld)
    text_mnpld = ABI.sub(' ابي_', text_mnpld)
    text_mnpld = IBN_IBNA.sub(r' \g<1>', text_mnpld)

    m = Onomastics().get_ngrams_regex().search(text_mnpld)
    while m:
        text_mnpld = text_mnpld[:m.start()] + m.group(1) + m.group(2).replace(' ', '_') + text_mnpld[m.end():]
        m = Onomastics().get_ngrams_regex().search(text_mnpld, m.end())

    m_bn = list(BN_BNT.finditer(text_mnpld))
    if m_bn:
        start = m_bn[0].start()
        end = m_bn[-1].end()
        pos_abu = text_mnpld[start:end].find(' ابو_')
        pos_umm = text_mnpld[start:end].find(' ام_')
        pos = max(pos_abu, pos_umm)
        if pos > 1:
            end = min(end, start + pos - 1)
        last_ancestor = text_mnpld[end + 1:].find(' ')
        if last_ancestor == -1:
            ancestors = BN_BNT.split(text_mnpld[start:])
        else:
            ancestors = BN_BNT.split(text_mnpld[start:end + 1 + last_ancestor])
        if ancestors[0] == '':
            ancestors = ancestors[1:]
        nas_w_tags = ''
        # Insert NAS tags
        for elem in ancestors:
            if not elem.startswith('بن'):
                num_tokens = len(elem.replace('_', ' ').split())
                nas_w_tags += ' ÜNAS' + str(max(1, num_tokens))
            nas_w_tags += ' ' + elem
        # Connect NAS elements with _ so they are ignored in further analysis
        if last_ancestor == -1:
            text_w_tags = text_mnpld[:start + 1].replace('_', ' ') + \
                          nas_w_tags[1:].replace(' ', '_')
        else:
            text_w_tags = text_mnpld[:start + 1].replace('_', ' ') + \
                          nas_w_tags[1:].replace(' ', '_') + \
                          text_mnpld[end + 1 + last_ancestor:].replace('_', ' ')

        return text_w_tags

    return text_mnpld


def tag_nasab(text: str) -> str:
    """Annotate the nasab part of the MIU.

    :param str text: nasab part of the MIU as one single string with tagged and filtered NAS elements (NAS is
    connected with '_' and therefore does not match with the gazetteer).
    :return str: the nasab part pf the MIU which contains also the tags in front of the recognized elements,
    '_' are removed.
    """
    text_mnpld = text.replace(' بن ', ' بن_')
    # for m in BANU_BANI.finditer(text_mnpld):
    #     print(f'{m.group(0)} last: {text_mnpld[m.end()]}')
    text_mnpld = text_mnpld.replace('من ولد ', 'من_ولد_')
    m = Onomastics().get_ngrams_regex().search(text_mnpld)
    while m:
        tag = Onomastics().get_ngram_tag(m.group(2))
        pos = m.start()
        end = m.end()
        if m.group(1) == ' ':
            pos += 1
        if tag.startswith('ÜEXP'):
            if CRF_PATTERN.search(m.group(2)) or SHR_PATTERN.search(m.group(2)):
                tag = 'ÜSHR'
                if text_mnpld[end:].startswith('ابن '):
                    tag += '2 '
                    text_mnpld = text_mnpld[:end] + text_mnpld[end + 1:].replace(' ', '_', 1)
                else:
                    tag += '1 '
                if m.group(2).endswith(' ب'):
                    end -= 1

                text_mnpld = text_mnpld[:end] + tag + text_mnpld[end:]
                text_mnpld = text_mnpld[:pos] + \
                             text_mnpld[pos + 1:end + len(tag) + 1].replace(' ', '_') + \
                             text_mnpld[end + len(tag) + 1:]
            # else:
            #     tag = ''
            #     print(f'start: {text_mnpld[pos:end]} end: {text_mnpld[end:]}')
        else:
            text_mnpld = text_mnpld[:pos] + tag + text_mnpld[pos:]

        end += len(tag)

        m = Onomastics().get_ngrams_regex().search(text_mnpld, end)

    # Log unidentified tokens as uni- and bi-grams
    filtered = text_mnpld
    m = Onomastics().get_ngrams_regex().search(filtered)
    while m:
        filtered = filtered[:m.start()] + m.group(1) + m.group(2).replace(' ', '_') + filtered[m.end():]
        m = Onomastics().get_ngrams_regex().search(filtered, m.end())
    tokens = [token for token in filtered.split() if not token.startswith('Ü')]
    unknown_uni = [t for t in tokens if not ('_' in t or t in Onomastics().total() + Toponyms().total())]
    prev = None
    unknown_bi = []
    for t in tokens:
        if not prev and not ('_' in t or t in Onomastics().total() + Toponyms().total() + ['بن', 'بنت']):
            prev = t
        else:
            if not ('_' in t or t in Onomastics().total() + Toponyms().total() + ['بن', 'بنت']):
                unknown_bi.append(prev + ' ' + t)
                prev = t
            else:
                prev = None
    if unknown_uni or unknown_bi:
        LOGGER_NASAB_UNKNOWN.info('\n'.join(unknown_uni + unknown_bi))

    return text_mnpld.replace('_', ' ')


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


def nasab_annotate_miu(
        df: DataFrame,
        yml_handler: YAMLHandler,
        file: str,
        test: Optional[bool] = False
) -> Series:
    """Onomastic analysis of the nasab part of the MIU.

    :param DataFrame df: DataFrame of the MIU.
    :param YAMLHandler yml_handler: YAMLHandler of the MIU.
    :param Path file: the MIU which was opened.
    :param bool test: run on test data set, optional.
    :return Series: a series of the same length as the df containing the nasab tags corresponding to the tokens.
    """
    if not yml_handler.is_bio():
        return Series([nan] * len(df))

    s_notna = df['TAGS_LISTS'].loc[df['TAGS_LISTS'].notna()].apply(lambda tag_list: ','.join(tag_list))
    try:
        if test:
            # training_data batch uses old NASAB tag, not new ENASAB tag
            idx = s_notna.loc[s_notna.str.contains('NASAB')].index[0]
        else:
            idx = s_notna.loc[s_notna.str.contains('ENASAB')].index[0]
    except IndexError:
        print(
                f'MIU does not have a ENASAB tag, most likely the MIU is not a biography but a cross reference and '
                f'wrongly labeled. '
                f'Check:\n{file}'
        )
        return Series([nan] * len(df))

    # The following blacklisted elements are considered noise in the text data and are therefore ignored but kept
    blacklist = ['(', ')', '[', ']', '"', "'", '.', '،', '؟', '!', ':', '؛', ',', ';', '?', '|']
    nasab_idx = df.loc[df['TOKENS'].notna() & ~df['TOKENS'].isin(blacklist) & df.index.isin(df.iat[:idx].index)].index

    text = ' '.join(df['TOKENS'].loc[nasab_idx])

    tagged_spelling = tag_spelling(text)
    ar_tokens, tags = get_tokens_and_tags(tagged_spelling)
    df.loc[nasab_idx, 'ONONMASTIC_TAGS'] = tags

    count = 0
    spl_idcs = []
    for row in df.loc[nasab_idx].itertuples():
        if notna(row[4]):
            count = int(row[4][-1])
        if count > 0:
            count -= 1
            spl_idcs.append(row[0])

    nasab_idx = df.loc[nasab_idx.difference(spl_idcs)].index
    text = ' '.join(df['TOKENS'].loc[nasab_idx])

    text_w_mnpld_nas = get_nas(text)
    tagged_onomastics = tag_nasab(text_w_mnpld_nas)
    ar_tokens, tags = get_tokens_and_tags(tagged_onomastics)
    df.loc[nasab_idx, 'ONONMASTIC_TAGS'] = tags

    if idx != len(df):
        # TODO make NASAB stay on same line
        df.loc[idx - 1, 'NASAB_END'] = 'NASAB'

    return df['ONONMASTIC_TAGS'].to_list()


def nasab_annotation(file: str, test: Optional[bool] = False):
    """Helper to run onomastic annotation standalone as cmdline script.

    :param str file: Path of the miu file to annotate.
    :param bool test: Indicating if the script is run with test data, defaults to false.
    """
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object)
    if test:
        # Only used if run on training_data batch because this information is missing there
        if '$' not in df.iat[0]['SECTIONS'] or '$$$' in df.iat[0]['SECTIONS'] or not yml_handler.is_reviewed():
            df['ONOM_TAGS'] = Series([nan] * len(df))
        else:
            yml_handler.set_category('$')
            df['ONOM_TAGS'] = nasab_annotate_miu(df, yml_handler, file, test)
    else:
        # Run on new data batch
        df['ONOM_TAGS'] = nasab_annotate_miu(df, yml_handler, file, test)
    yml_handler.unset_reviewed()

    if test:
        output_path = str(file).replace('gold_standard', 'gold_standard_nasab')
    else:
        output_path = str(file)

    with open(output_path, 'w', encoding='utf-8') as out_file_object:
        write_updated_miu_to_file(
                out_file_object, yml_handler, df[['SECTIONS', 'TOKENS', 'TAGS_LISTS', 'ONOM_TAGS']]
        )
