from typing import List, Pattern
from importlib_resources import files
from re import compile
from pandas import concat, read_csv

from eis1600.helper.Singleton import singleton
from openiti.helper.ara import denormalize

path = files('eis1600.gazetteers.data').joinpath('onomastic_gazetteer.csv')


@singleton
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
    __kun = None
    __laq = None
    __nsb = None
    __swm = None
    __tot = None
    __ngrams = None
    __ngrams_regex = None

    def __init__(self) -> None:
        try:
            oa_df = read_csv(path)
        except Exception as e:
            print(f'Check if the {self.__class__.__name__} gazetteer is correctly formatted with commas and not tabs.')
        oa_df['NGRAM'] = oa_df['NGRAM'].astype('uint8')
        oa_df['CATEGORY'] = oa_df['CATEGORY'].astype('category')

        Onomastics.__end = oa_df.loc[oa_df['CATEGORY'] == 'END', 'VALUE'].to_list()
        Onomastics.__exp = oa_df.loc[oa_df['CATEGORY'] == 'EXP', 'VALUE'].to_list()
        Onomastics.__ism = oa_df.loc[oa_df['CATEGORY'] == 'ISM', 'VALUE'].to_list()
        Onomastics.__ism = oa_df.loc[oa_df['CATEGORY'] == 'KUN', 'VALUE'].to_list()
        Onomastics.__laq = oa_df.loc[oa_df['CATEGORY'] == 'LAQ', 'VALUE'].to_list()
        Onomastics.__nsb = oa_df.loc[oa_df['CATEGORY'] == 'NSB', 'VALUE'].to_list()
        Onomastics.__swm = oa_df.loc[oa_df['CATEGORY'] == 'SWM', 'VALUE'].to_list()

        Onomastics.__tot = Onomastics.__ism + Onomastics.__laq + Onomastics.__nsb + Onomastics.__swm + Onomastics.__exp
        expression = Onomastics.__exp + Onomastics.__swm + Onomastics.__ism

        def rplc_to_aba(row):
            new_row = row
            new_row['VALUE'] = row['VALUE'].replace('أبو', 'أبا')
            return new_row

        def rplc_to_abi(row):
            new_row = row
            new_row['VALUE'] = row['VALUE'].replace('أبو', 'أبي')
            return new_row

        abu_rows = oa_df.loc[oa_df['VALUE'].str.contains('أبو')]
        spelling_variations_1 = abu_rows.apply(rplc_to_aba, axis=1)
        spelling_variations_2 = abu_rows.apply(rplc_to_abi, axis=1)
        df_abu_variations = concat([oa_df.loc[oa_df['CATEGORY'] != 'END'], spelling_variations_1,
                                       spelling_variations_2])

        # Sort from longest to shortest ngrams - longest need to come first in regex otherwise only the shorter one
        # will be matched
        Onomastics.__ngrams = df_abu_variations.sort_values(by=['NGRAM'], ascending=False)
        ngrams = Onomastics.__ngrams['VALUE'].to_list()
        Onomastics.__ngrams_regex = compile('(^| )(' + denormalize('|'.join(ngrams)) + ')')

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
    def get_ngrams_regex() -> Pattern[str]:
        return Onomastics.__ngrams_regex

    @staticmethod
    def get_ngram_tag(ngram: str) -> str:
        lookup = Onomastics.__ngrams.loc[Onomastics.__ngrams['VALUE'].str.fullmatch(denormalize(ngram))]
        if len(lookup) > 1:
            all_pos = ['Ü' + cat + str(n) for cat, n in zip(lookup['CATEGORY'].to_list(), lookup['NGRAM'].to_list())]
            return '___'.join(all_pos) + ' '
        elif len(lookup) == 1:
            return 'Ü' + str(lookup.iat[0]['CATEGORY']) + str(lookup.iat[0]['NGRAM']) + ' '
        else:
            return 'ÜNaN' + str(len(ngram)) + ' '
