from importlib_resources import files
from typing import List, Tuple
import pandas as pd
from eis1600.helper.Singleton import Singleton


path = files('eis1600.gazetteers.data').joinpath('toponyms.csv')


def split_toponyms(tops: str) -> List[str]:
    return tops.split('، ')


@Singleton
class Toponyms:
    """
    Gazetteer

    :ivar _tot List[str]: List of all toponyms and their prefixed variants
    :ivar _rpl List[Tuple[str, str]]: List of tuples: expression and its replacement.
    """
    __tot = None
    __rpl = None

    def __init__(self) -> None:
        df = pd.read_csv(path, usecols=['placeLabel', 'toponyms', 'typeLabel', 'geometry'], converters={'toponyms':
                                                                                                            split_toponyms})
        prefixes = ['ب']

        tot = df['toponyms'].explode().to_list()
        regions = ['الشام', 'مصر', 'العراق', 'اليمن', 'المغرب']
        tot.extend([regions])
        Toponyms.__tot = tot + [prefix + top for prefix in prefixes for top in tot]

        Toponyms.__rpl = [(elem, elem.replace(' ', '_')) for elem in Toponyms.__tot if ' ' in elem]

    @staticmethod
    def total() -> List[str]:
        return Toponyms.__tot

    @staticmethod
    def replacements() -> List[Tuple[str, str]]:
        return Toponyms.__rpl
