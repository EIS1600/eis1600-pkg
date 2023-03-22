import re

from importlib_resources import files
from typing import List, Tuple, Pattern
import pandas as pd
from eis1600.helper.Singleton import Singleton
from openiti.helper.ara import denormalize

path = files('eis1600.gazetteers.data').joinpath('onomastic_gazetteer.csv')


@Singleton
class Onomastics:
    """
    Gazetteer

    :ivar __end List[str]: List of terms which indicate the end of the NASAB.
    :ivar __exp List[str]: List of explanatory terms used in the onomastic information.
    :ivar __ism List[str]: List of isms/first names.
    :ivar __laq List[str]: List of laqabs (including mamluk shortforms).
    :ivar __nsb List[str]: List of nisbas.
    :ivar __swm List[str]: List of professions.
    :ivar __tot List[str]: List of all onomastic terms: _exp + _ism + _laq + _nsb + _swm
    :ivar __rpl List[Tuple[str, str]]: List of tuples: expression and its replacement.
    :ivar __ngrams DataFrame: Subset of the df containing all name parts which are ngrams with n > 1.
    :ivar __ngrams_regex re: re of all name parts which are ngrams with n > 1, sorted from longest to shortest ngrams.
    """
    __end = None
    __exp = None
    __ism = None
    __laq = None
    __nsb = None
    __swm = None
    __tot = None
    __rpl = None
    __ngrams = None
    __ngrams_regex = None

    def __init__(self) -> None:
        df = pd.read_csv(path)
        df['ngram'] = df['ngram'].astype('uint8')
        df['category'] = df['category'].astype('category')
        Onomastics.__end = df.loc[df['category'] == 'END', 'value'].to_list()
        Onomastics.__exp = df.loc[df['category'] == 'EXP', 'value'].to_list()
        Onomastics.__ism = df.loc[df['category'] == 'ISM', 'value'].to_list()
        Onomastics.__laq = df.loc[df['category'] == 'LAQ', 'value'].to_list()
        Onomastics.__nsb = df.loc[df['category'] == 'NSB', 'value'].to_list()
        Onomastics.__swm = df.loc[df['category'] == 'SWM', 'value'].to_list()

        Onomastics.__tot = Onomastics.__ism + Onomastics.__laq + Onomastics.__nsb + Onomastics.__swm + Onomastics.__exp
        expression = Onomastics.__exp + Onomastics.__swm + Onomastics.__ism
        Onomastics.__rpl = [(elem, elem.replace(' ', '_')) for elem in expression if ' ' in elem]

        def rplc_to_aba(row):
            new_row = row
            new_row['value'] = row['value'].replace('أيو', 'أبا')
            return new_row

        def rplc_to_abi(row):
            new_row = row
            new_row['value'] = row['value'].replace('أيو', 'أبي')
            return new_row

        abu_rows = df.loc[df['value'].str.contains('أيو')]
        spelling_variations_1 = abu_rows.apply(rplc_to_aba, axis=1)
        spelling_variations_2 = abu_rows.apply(rplc_to_abi, axis=1)
        df_abu_variations = pd.concat([df, spelling_variations_1, spelling_variations_2])

        # Sort from longest to shortest ngrams - longest need to come first in regex otherwise only the shorter one
        # will be matched
        Onomastics.__ngrams = df_abu_variations.sort_values(by=['ngram'], ascending=False)
        ngrams = Onomastics.__ngrams['value'].to_list()
        Onomastics.__ngrams_regex = re.compile('(?:^| )(' + denormalize('|'.join(ngrams)) + ')')

    @staticmethod
    def exp() -> List[str]:
        return Onomastics.__exp

    @staticmethod
    def end() -> List[str]:
        return Onomastics.__end

    @staticmethod
    def total() -> List[str]:
        return Onomastics.__tot

    @staticmethod
    def replacements() -> List[Tuple[str, str]]:
        return Onomastics.__rpl

    @staticmethod
    def get_ngrams_regex() -> Pattern[str]:
        return Onomastics.__ngrams_regex

    @staticmethod
    def get_ngram_tag(ngram) -> str:
        lookup = Onomastics.__ngrams.loc[Onomastics.__ngrams['value'] == ngram]
        if len(lookup) > 1:
            all_pos = [cat + str(n) for cat, n in zip(lookup['category'].to_list(), lookup['ngram'].to_list())]
            return '/'.join(all_pos) + ' '
        elif len(lookup) == 1:
            return str(lookup.iloc[0]['category']) + str(lookup.iloc[0]['ngram']) + ' '
        else:
            return '???' + str(len(ngram)) + ' '

