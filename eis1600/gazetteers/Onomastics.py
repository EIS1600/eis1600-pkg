from importlib_resources import files
from typing import List, Tuple
import pandas as pd
from eis1600.helper.Singleton import Singleton


path = files('eis1600.gazetteers.data').joinpath('onomastics.csv')


@Singleton
class Onomastics:
    """
    Gazetteer

    :ivar _end List[str]: List of terms which indicate the end of the NASAB.
    :ivar _exp List[str]: List of explanatory terms used in the onomastic information.
    :ivar _ism List[str]: List of isms/first names.
    :ivar _laq List[str]: List of laqabs (including mamluk shortforms).
    :ivar _nsb List[str]: List of nisbas.
    :ivar _swm List[str]: List of professions.
    :ivar _tot List[str]: List of all onomastic terms: _exp + _ism + _laq + _nsb + _swm
    :ivar _rpl List[Tuple[str, str]]: List of tuples: expression and its replacement.
    """
    __end = None
    __exp = None
    __ism = None
    __laq = None
    __nsb = None
    __swm = None
    __tot = None
    __rpl = None

    def __init__(self) -> None:
        df = pd.read_csv(path)
        Onomastics.__end = df.loc[df['category'] == 'END', 'value'].to_list()
        Onomastics.__exp = df.loc[df['category'] == 'EXP', 'value'].to_list()
        Onomastics.__ism = df.loc[df['category'] == 'ISM', 'value'].to_list()
        Onomastics.__laq = df.loc[df['category'] == 'LAQ', 'value'].to_list()
        Onomastics.__nsb = df.loc[df['category'] == 'NSB', 'value'].to_list()
        Onomastics.__swm = df.loc[df['category'] == 'SWM', 'value'].to_list()

        Onomastics.__tot = Onomastics.__ism + Onomastics.__laq + Onomastics.__nsb + Onomastics.__swm + Onomastics.__exp
        expression = Onomastics.__exp + Onomastics.__swm + Onomastics.__ism
        Onomastics.__rpl = [(elem, elem.replace(' ', '_')) for elem in expression if ' ' in elem]

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
