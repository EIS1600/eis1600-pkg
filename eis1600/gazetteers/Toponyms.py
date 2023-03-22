from importlib_resources import files
from typing import List, Tuple
import pandas as pd
from eis1600.helper.Singleton import Singleton

file_path = files('eis1600.gazetteers.data')
thurayya_path = file_path.joinpath('toponyms.csv')
regions_path = file_path.joinpath('regions_gazetteer.csv')


def split_toponyms(tops: str) -> List[str]:
    return tops.split('، ')


@Singleton
class Toponyms:
    """
    Gazetteer

    :ivar __places List[str]: List of all place names and their prefixed variants.
    :ivar __regions List[str]: List of all region names and their prefixed variants.
    :ivar __total List[str]: List of all toponyms and their prefixed variants.
    :ivar __rpl List[Tuple[str, str]]: List of tuples: expression and its replacement.
    """
    __places = None
    __regions = None
    __total = None
    __rpl = None

    def __init__(self) -> None:
        thurayya_df = pd.read_csv(thurayya_path, usecols=['placeLabel', 'toponyms', 'typeLabel', 'geometry'],
                                  converters={'toponyms': split_toponyms})
        regions_df = pd.read_csv(regions_path)
        prefixes = ['ب', 'و', 'وب']

        places = thurayya_df['toponyms'].explode().to_list()
        Toponyms.__places = places + [prefix + top for prefix in prefixes for top in places]
        regions = regions_df['region'].to_list()
        Toponyms.__regions = regions + [prefix + reg for prefix in prefixes for reg in regions]

        Toponyms.__total = Toponyms.__places + Toponyms.__regions
        Toponyms.__rpl = [(elem, elem.replace(' ', '_')) for elem in Toponyms.__total if ' ' in elem]

    @staticmethod
    def places() -> List[str]:
        return Toponyms.__places

    @staticmethod
    def regions() -> List[str]:
        return Toponyms.__regions

    @staticmethod
    def total() -> List[str]:
        return Toponyms.__total

    @staticmethod
    def replacements() -> List[Tuple[str, str]]:
        return Toponyms.__rpl
