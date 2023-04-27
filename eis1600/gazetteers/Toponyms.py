from __future__ import annotations
from importlib_resources import files
from typing import Dict, List, Tuple
import pandas as pd

from eis1600.helper.Singleton import Singleton
from eis1600.helper.ar_normalization import denormalize_list

file_path = files('eis1600.gazetteers.data')
thurayya_path = file_path.joinpath('toponyms.csv')
regions_path = file_path.joinpath('regions_gazetteer.csv')


def toponyms_from_rows(row: pd.Series) -> YAMLToponym:
    toponym = {
            'name': row['uri'],
            'geometry': {
                    'type': row['geometry_type'],
                    'coordinates': row['geometry_coords']
            }
    }
    return YAMLToponym(toponym)


class YAMLToponym:
    def __init__(self, attr: Dict):
        self.name = ''
        self.geometry = {
                'type': '',
                'coordinates': [0, 0]
        }

        for key, val in attr.items():
            self.__setattr__(key, val)

    def as_dict(self) -> Dict:
        return self.__dict__

    @property
    def attribute(self):
        return self._attribute

    def coords(self) -> List[float, float]:
        return self.geometry['coordinates']

    def __repr__(self) -> str:
        return str(type(self)) + str(self.__dict__)

    def __str__(self) -> str:
        return str(self.__dict__)

    def __hash__(self):
        return hash(self.name + str(self.geometry.get('coordinates')))


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

        def coords_as_list(coords: str) -> List[float, float]:
            coords_list = coords.strip('()').split(', ')
            x, y = coords_list
            return [float(x), float(y)]

        thurayya_df = pd.read_csv(thurayya_path, usecols=['uri', 'placeLabel', 'toponyms', 'province', 'typeLabel',
                                                          'geometry_type', 'geometry_coords'],
                                  converters={'toponyms': split_toponyms, 'geometry_coords': coords_as_list})
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
    def look_up_province(uri: str) -> YAMLToponym:
        """

        :param str uri: URI of the province to look up attributes
        :return:
        """
        # TODO lookup provinces from provinces gazetteer
        # TODO toponyms_from_rows(row)
        province = {
                'name': uri,
                'geometry': {
                        'type': 'point',
                        'coordinates': [0, 0]
                }
        }

        return YAMLToponym(province)

    @staticmethod
    def look_up_entity(entity: str) -> Tuple[str, str, List[YAMLToponym], List[str]]:
        """

        :param str entity: The token(s) which were tagged as toponym.
        :return: placeLabel(s) as str, URI(s) as str, list of toponym uri(s), list of province uri(s),
        list of toponym(s) coordinates, list of province(s) coordinates.
        """
        if entity in Toponyms.__places:
            matches = Toponyms.__df.loc[Toponyms.__df['toponyms'].str.fullmatch(entity), ['uri', 'placeLabel',
                                                                                          'province',
                                                                                          'geometry_type',
                                                                                          'geometry_coords']]
            uris = matches['uri'].to_list()
            provinces = matches['province'].to_list()
            place = matches['placeLabel'].unique()

            toponyms = [toponyms_from_rows(row) for idx, row in matches.iterrows()]
            return '::'.join(place), '@' + '@'.join(uris) + '@', toponyms, provinces
        else:
            return entity, '', [], []
