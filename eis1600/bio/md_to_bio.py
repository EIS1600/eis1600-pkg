from typing import Dict, List, Optional, Pattern, Tuple, Union

from eis1600.markdown.EntityTags import EntityTags
from numpy import nan
from pandas import DataFrame, Series


def get_bio_dict(bio_main_class: str, categories: List[str]) -> Dict:
    """

    :param str bio_main_class: String of two letters which are used to indicate the main entity, e.g. 'YY' for dates,
    'TO' for toponyms, etc.
    :param List[str] categories: List of letters used for the categories.
    :return:
    """
    bio = ["B", "I"]

    labels = [bi + "-" + bio_main_class + c for c in categories for bi in bio] + ["O"]
    label_dict = {}

    for i, label in enumerate(labels):
        label_dict[label] = i

    return label_dict


def md_to_bio(
        df: DataFrame, column_name: str, pattern: Pattern, bio_main_class: str, bio_dict: Dict,
        less_categories: Optional[bool] = False, replacements: Optional[Dict] = None
) -> Dict:
    """Parses EIS100 mARkdown tags to BIO labels.

    :param DataFrame df: DataFrame must have these two columns: 'TOKENS' and a second column named <column_name> which
    contains the EIS1600 tags to parse to the BIO labels.
    :param str column_name: Name of the DataFrames column which contains the EIS1600 tags to parse to BIO labels.
    :param Pattern pattern: Pattern must match named capturing groups for: 'num_tokens' and 'cat'.
    :param str bio_main_class: String of two letters which are used to indicate the main entity, e.g. 'YY' for dates,
    'TO' for toponyms, etc.
    :param Dict bio_dict: dictionary whose keys are the BIO labels and the values are integers (see method
    get_label_dict in this file).
    :param less_categories: Flag to indicate combining certain classes into broader categories.
    :param replacements: If less_categories is true, this is a dictionary with the replacement for the categories.
    :return: Dictionary with three entries: 'tokens', a list of the tokens which have been classified; 'ner_tags',
    a list of the numerical representation of the BIO labels assigned to the tokens; 'ner_classes', a list of the
    str representation of the BIO labels assigned to the tokens.
    """
    if any(df[column_name].notna()):
        s_notna = df[column_name].loc[df[column_name].notna()]
        df_matches = s_notna.str.extract(pattern).dropna(how='all')

        if df_matches.empty:
            df['BIO'] = 'O'
        else:
            # This line is needed due to this new bug in pandas where nan is cast to str in str columns, therefore set
            # column explicitly to dtype object so we can call isna() (otherwise == 'nan', which does not make sense)
            df['BIO'] = Series(index=df.index, dtype=object)
            for index, row in df_matches.iterrows():
                processed_tokens = 0
                num_tokens = int(row['num_tokens'])
                cat = row['cat']
                if less_categories and cat in replacements.keys():
                    cat = replacements.get(cat)
                while processed_tokens < num_tokens:
                    if processed_tokens == 0:
                        df.loc[index, 'BIO'] = 'B-' + bio_main_class + cat
                    else:
                        df.loc[index + processed_tokens, 'BIO'] = 'I-' + bio_main_class + cat

                    processed_tokens += 1

            df['BIO'].loc[df['BIO'].isna()] = 'O'
    else:
        df['BIO'] = 'O'

    df['BIO_IDS'] = df['BIO'].apply(lambda bio_tag: bio_dict[bio_tag])
    idcs = df['TOKENS'].loc[df['TOKENS'].notna()].index

    return {
            'tokens': df['TOKENS'].loc[idcs].to_list(),
            'ner_tags': df['BIO_IDS'].loc[idcs].to_list(),
            'ner_classes': df['BIO'].loc[idcs].to_list()
    }


def get_temp_class_es(_label: Union[str, None], sub_class: bool) -> Tuple[str, Union[None, str]]:
    temp_sub_class = None
    if _label[2:] == 'LOC':
        _label = _label.replace('LOC', 'TOX')
        temp_class = _label[2]
    elif _label[2:] in EntityTags().get_onom_tags():
        temp_class = _label[2:]
    elif _label[2:] == 'TOPD':
        temp_class = 'Q'
    else:
        temp_class = _label[2]
    if sub_class:
        temp_sub_class = _label[-1]

    return temp_class, temp_sub_class


def bio_to_md(bio_labels: List[str], sub_class: Optional[bool] = False, umlaut_prefix: Optional[bool] = True) -> List[
    str]:
    """Converts BIO labels to EIS1600 tags.

    Converter method for BIO labels to EIS100 tags. BI labels must follow this pattern: [BI]-[AMPTY].* with
    * [A]ge
    * [M]ISC
    * [P]erson
    * [Q]
    * [T]oponym
    * [Y]ear
    Usually, EIS1600 BIO labels have a three letter code: [YY][BDKP] with YY for year and [BDKP] for the sub-class.
    :param List[str] bio_labels: List containing the BIO label for each token.
    :param bool sub_class: if set to True, last char of BIO label indicates sub-class, e.g. YYB for date with
    sub-class date of birth, defaults to False.
    :param bool umlaut_prefix: if set to False, the md-tags will not be prefixed with 'Ü', defaults to True.
    :return List[str]: List containing the respective EIS1600 tags
    """
    converted_tokens, temp_tokens, temp_class, temp_sub_class = [], [], None, None

    for _label in bio_labels:
        if _label is None:
            converted_tokens.append(nan)
        else:
            # Check if the first letter of the label is 'O' or 'B' because this will terminate the previous entity
            # and 'B' will additionally start a new entity
            if _label[0] in ['O', 'B']:
                if len(temp_tokens):
                    # Generate EIS1600 tag for entity
                    if sub_class:
                        if umlaut_prefix:
                            converted_tokens.append(f"Ü{temp_class}{len(temp_tokens)}{temp_sub_class}")  # e.g. ÜP3X
                        else:
                            converted_tokens.append(f"{temp_class}{len(temp_tokens)}{temp_sub_class}")  # e.g. ÜP3X
                    else:
                        if umlaut_prefix:
                            converted_tokens.append(f"Ü{temp_class}{len(temp_tokens)}")  # e.g. ÜP3
                        else:
                            converted_tokens.append(f"{temp_class}{len(temp_tokens)}")  # e.g. ÜP3
                    # Mask I-tags with nan
                    converted_tokens.extend([nan] * (len(temp_tokens) - 1))
                    temp_tokens = []
                    temp_class = None
                    temp_sub_class = None
                if _label[0] == 'B':
                    # Start new entity
                    temp_class, temp_sub_class = get_temp_class_es(_label, sub_class)
                    temp_tokens = [_label]
                elif _label == 'O':
                    converted_tokens.append(nan)
            elif _label[0] == 'I':
                temp_tokens.append(_label)
                if temp_class is None:
                    temp_class, temp_sub_class = get_temp_class_es(_label, sub_class)
            else:
                converted_tokens.append(nan)

    if len(temp_tokens):
        # Add last entity
        if sub_class:
            converted_tokens.append(f"Ü{temp_class}{len(temp_tokens)}{temp_sub_class}")  # e.g. ÜP3X
        else:
            converted_tokens.append(f"Ü{temp_class}{len(temp_tokens)}")  # e.g. ÜP3
        converted_tokens.extend([nan] * (len(temp_tokens) - 1))

    return converted_tokens
