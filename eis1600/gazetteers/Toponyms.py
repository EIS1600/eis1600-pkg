from __future__ import annotations
from importlib_resources import files
from typing import List, Tuple
from pandas import concat, isna, read_csv

from eis1600.helper.Singleton import Singleton
from eis1600.helper.ar_normalization import denormalize_list

file_path = files('eis1600.gazetteers.data')
toponyms_path = file_path.joinpath('toponyms.csv')
provinces_path = file_path.joinpath('regions.csv')


@Singleton
class Toponyms:
    """
    Gazetteer

    :ivar DataFrame __df: The dataFrame.
    :ivar __settlements List[str]: List of all settlement names and their prefixed variants.
    :ivar __provinces List[str]: List of all province names and their prefixed variants.
    :ivar __total List[str]: List of all toponyms and their prefixed variants.
    :ivar __rpl List[Tuple[str, str]]: List of tuples: expression and its replacement.
    """
    __df = None
    __settlements = None
    __provinces = None
    __total = None
    __rpl = None

    def __init__(self) -> None:
        def split_toponyms(tops: str) -> List[str]:
            return tops.split('، ')

        def coords_as_list(coords: str) -> List[float, float]:
            coords_list = coords.strip('()').split(', ')
            x, y = coords_list
            return [float(x), float(y)]

        thurayya_df = read_csv(toponyms_path, usecols=['uri', 'place_label', 'toponyms', 'province_uri',
                                                       'type_label'], converters={'toponyms': split_toponyms})
        provinces_df = read_csv(provinces_path, usecols=['uri', 'place_label', 'toponyms'],
                                  converters={'toponyms': split_toponyms})
        prefixes = ['ب', 'و', 'وب', 'ل', 'ول']

        def get_all_variations(tops: List[str]) -> List[str]:
            variations = denormalize_list(tops)
            prefixed_variations = [prefix + top for prefix in prefixes for top in variations]
            return variations + prefixed_variations

        uris = thurayya_df['uri'].to_list()
        regions = [uri[:-1] + 'R' for uri in uris if uri[-1] == 'S' and uri[:-1] + 'R' in uris]
        regions_idcs = thurayya_df.loc[thurayya_df['uri'].str.fullmatch('|'.join(regions))].index
        thurayya_df.drop(index=regions_idcs, inplace=True)
        thurayya_df['toponyms'] = thurayya_df['toponyms'].apply(get_all_variations)
        provinces_df['toponyms'] = provinces_df['toponyms'].apply(get_all_variations)

        settlements = thurayya_df.explode('toponyms', ignore_index=True)
        provinces = provinces_df.explode('toponyms', ignore_index=True)

        Toponyms.__settlements = settlements['toponyms'].to_list()
        Toponyms.__provinces = provinces['toponyms'].to_list()
        Toponyms.__df = concat([settlements, provinces], ignore_index=True)
        Toponyms.__df.mask(isna(Toponyms.__df), '', inplace=True)

        Toponyms.__total = Toponyms.__settlements + Toponyms.__provinces
        Toponyms.__rpl = [(elem, elem.replace(' ', '_')) for elem in Toponyms.__total if ' ' in elem]

    @staticmethod
    def settlements() -> List[str]:
        return Toponyms.__settlements

    @staticmethod
    def provinces() -> List[str]:
        return Toponyms.__provinces

    @staticmethod
    def total() -> List[str]:
        return Toponyms.__total

    @staticmethod
    def replacements() -> List[Tuple[str, str]]:
        return Toponyms.__rpl

    @staticmethod
    def look_up_entity(entity: str) -> Tuple[str, str, List[str], List[str]]:
        """Look up tagged entity in settlements (there is no gazetteer of provinces so far).

        :param str entity: The token(s) which were tagged as toponym.
        :return: placeLabel(s) as str, URI(s) as str, list of settlement uri(s), list of province uri(s),
        list of settlement(s) coordinates, list of province(s) coordinates.
        """
        if entity in Toponyms.__total:
            matches = Toponyms.__df.loc[Toponyms.__df['toponyms'].str.fullmatch(entity), ['uri', 'province_uri',
                                                                                          'place_label']]
            uris = matches['uri'].to_list()
            provinces = matches['province_uri'].to_list()
            place = matches['place_label'].unique()

            return '::'.join(place), '@' + '@'.join(uris) + '@', uris, provinces
        else:
            return entity, '', [], []
