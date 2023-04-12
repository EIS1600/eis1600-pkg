from eis1600.helper.ar_normalization import denormalize_list
from importlib_resources import files
from typing import List, Tuple
import pandas as pd
from eis1600.helper.Singleton import Singleton

file_path = files('eis1600.gazetteers.data')
thurayya_path = file_path.joinpath('toponyms.csv')
regions_path = file_path.joinpath('regions_gazetteer.csv')


@Singleton
class Toponyms:
    """
    Gazetteer

    :ivar DataFrame __df: The dataFrame.
    :ivar __places List[str]: List of all place names and their prefixed variants.
    :ivar __regions List[str]: List of all region names and their prefixed variants.
    :ivar __total List[str]: List of all toponyms and their prefixed variants.
    :ivar __rpl List[Tuple[str, str]]: List of tuples: expression and its replacement.
    """
    __df = None
    __places = None
    __regions = None
    __total = None
    __rpl = None

    def __init__(self) -> None:
        def split_toponyms(tops: str) -> List[str]:
            return tops.split('، ')

        thurayya_df = pd.read_csv(thurayya_path, usecols=['uri', 'placeLabel', 'toponyms', 'province', 'typeLabel',
                                                          'geometry'],
                                  converters={'toponyms': split_toponyms})
        regions_df = pd.read_csv(regions_path)
        prefixes = ['ب', 'و', 'وب']

        def get_all_variations(tops: List[str]) -> List[str]:
            variations = denormalize_list(tops)
            prefixed_variations = [prefix + top for prefix in prefixes for top in variations]
            return variations + prefixed_variations

        thurayya_df['toponyms'] = thurayya_df['toponyms'].apply(get_all_variations)
        Toponyms.__df = thurayya_df.explode('toponyms', ignore_index=True)
        Toponyms.__places = Toponyms.__df['toponyms'].to_list()
        regions = regions_df['REGION'].to_list()
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

    @staticmethod
    def look_up_entity(entity: str) -> Tuple[str, str, List[str], List[str]]:
        if entity in Toponyms.__places:
            matches = Toponyms.__df.loc[Toponyms.__df['toponyms'].str.fullmatch(entity), ['uri', 'placeLabel',
                                                                                          'province']]
            uris = matches['uri'].to_list()
            provinces = matches['province'].to_list()
            place = matches['placeLabel'].unique()
            if len(place) == 1:
                return place[0], '@' + '@'.join(uris) + '@', uris, provinces
            else:
                return '::'.join(place), '@' + '@'.join(uris) + '@', uris, provinces
        else:
            return entity, '', [], []
