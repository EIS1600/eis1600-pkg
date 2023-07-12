from typing import Dict, List, Pattern
from pandas import DataFrame


def get_label_dict(bio_main_class: str, categories: List[str]) -> Dict:
    """

    :param str bio_main_class: String of two letters which are used to indicate the main entity, e.g. 'YY' for dates,
    'TO' for toponyms, etc.
    :param List[str] categories: List of letters used for the categories.
    :return:
    """
    categories = [bio_main_class + c for c in categories]
    BIO = ["B", "I"]

    labels = [bi + "-" + c for c in categories for bi in BIO] + ["O"]
    label_dict = {}

    for i, label in enumerate(labels):
        label_dict[label] = i

    return label_dict


def md_to_bio(df: DataFrame, column_name: str, pattern: Pattern, bio_main_class: str, label_dict: Dict) -> Dict:
    """Parses EIS100 mARkdown tags to BIO annotation.

    :param DataFrame df: DataFrame must have these two columns: 'TOKENS' and a second column named <column_name> which
    contains the EIS1600 tags to parse to the BIO tags.
    :param str column_name: Name of the DataFrames column which contains the EIS1600 tags to parse to BIO tags.
    :param Pattern pattern: Pattern must match named capturing groups for: 'num_tokens' and 'cat'.
    :param str bio_main_class: String of two letters which are used to indicate the main entity, e.g. 'YY' for dates,
    'TO' for toponyms, etc.
    :param Dict label_dict: dictionary whose keys are the BIO labels and the values are integers (see method
    get_label_dict in this file).
    :return: Dictionary with three entries: 'tokens', a list of the tokens which have been classified; 'ner_tags',
    a list of the numerical representation of the BIO classes assigned to the tokens; 'ner_classes', a list of the
    str representation of the BIO classes assigned to the tokens.
    """
    if any(df[column_name].notna()):
        s_notna = df[column_name].loc[df[column_name].notna()]
        df_matches = s_notna.str.extract(pattern).dropna(how='all')

        if df_matches.empty:
            df["BIO"] = "O"
        else:
            for index, row in df_matches.iterrows():
                processed_tokens = 0
                num_tokens = int(row['num_tokens'])
                while processed_tokens < num_tokens:
                    if processed_tokens == 0:
                        df.loc[index, 'BIO'] = 'B-' + bio_main_class + row['cat']
                    else:
                        df.loc[index + processed_tokens, 'BIO'] = 'I-' + bio_main_class + row['cat']

                    processed_tokens += 1

            df["BIO"].loc[df["BIO"].isna()] = "O"
    else:
        df["BIO"] = "O"

    df["BIO_IDS"] = df["BIO"].apply(lambda bio_tag: label_dict[bio_tag])
    idcs = df["TOKENS"].loc[df["TOKENS"].notna()].index

    return {
            "tokens": df["TOKENS"].loc[idcs].to_list(),
            "ner_tags": df["BIO_IDS"].loc[idcs].to_list(),
            "ner_classes": df["BIO"].loc[idcs].to_list()
    }

