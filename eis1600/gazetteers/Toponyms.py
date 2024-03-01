from __future__ import annotations

from eis1600.helper.Singleton import singleton
from importlib_resources import files
from typing import List, Tuple
from pandas import isna, read_csv

from eis1600.helper.ar_normalization import denormalize_list

toponyms_path = files('eis1600.gazetteers.data').joinpath('toponyms_gazetteer.csv')


@singleton
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
        try:
            df = read_csv(toponyms_path, usecols=['URI_GRAVITON', 'LABEL', 'TOPONYM', 'METAREGION', 'TYPE'])
        except Exception as e:
            print(f'Check if the {self.__class__.__name__} gazetteer is correctly formatted with commas and not tabs.')
        prefixes = ['ب', 'و', 'وب', 'ل', 'ول']

        def get_all_variations(top: str) -> List[str]:
            variations = denormalize_list(top)
            prefixed_variations = [prefix + t for prefix in prefixes for t in variations]
            return variations + prefixed_variations

        df['TOPONYMS'] = df['TOPONYM'].apply(get_all_variations)

        topos = df.explode('TOPONYMS', ignore_index=True)

        Toponyms.__settlements = topos.loc[topos['TYPE'] != 'province', 'TOPONYMS'].to_list()
        Toponyms.__provinces = topos.loc[topos['TYPE'] == 'province', 'TOPONYMS'].to_list()
        Toponyms.__df = topos
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
        :return: placeLabel(s) as str, URI(s)-tag as str, list of settlement uri(s), list of province uri(s),
        list of settlement(s) coordinates, list of province(s) coordinates.
        """
        if entity in Toponyms.__total:
            matches = Toponyms.__df.loc[Toponyms.__df['TOPONYMS'].str.fullmatch(entity), ['URI_GRAVITON',
                                                                                          'METAREGION',
                                                                                          'LABEL']]
            uris = matches['URI_GRAVITON'].to_list()
            provinces = [m for m in matches['METAREGION'].to_list() if m != '']
            place = matches['LABEL'].unique()

            return '::'.join(place), '@' + '@'.join(uris) + '@', uris, provinces
        else:
            return entity, '', [], []
