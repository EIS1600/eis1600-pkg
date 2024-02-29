from typing import List

from eis1600.helper.ar_normalization import denormalize_list
from importlib_resources import files
from pandas import read_csv

from eis1600.helper.Singleton import singleton

path = files('eis1600.gazetteers.data').joinpath('spelling_gazetteer.csv')


@singleton
class Spellings:
    __tot = None
    __denormalized = None
    __regex = ''

    def __init__(self) -> None:
        try:
            df = read_csv(path)
        except Exception as e:
            print(f'Check if the {self.__class__.__name__} gazetteer is correctly formatted with commas and not tabs.')
        df['NGRAM'] = df['NGRAM'].astype('uint8')
        df['CATEGORY'] = df['CATEGORY'].astype('category')

        sorted_df = df.sort_values(by=['NGRAM'], ascending=False)
        Spellings.__tot = sorted_df['VALUE'].to_list()
        denormalized = []
        [denormalized.extend(denormalize_list(t)) for t in Spellings.__tot]
        Spellings.__denormalized = denormalized
        Spellings.__regex = r'(?P<spelling> [وب]?(?:ال)?(?:' + '|'.join(denormalized) + ')(?:ها)?)'

    @staticmethod
    def get_denormalized_list() -> List[str]:
        return Spellings.__denormalized

    @staticmethod
    def get_regex() -> str:
        return Spellings.__regex
