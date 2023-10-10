from typing import List

from importlib_resources import files
from pandas import read_csv

from eis1600.helper.Singleton import Singleton
from openiti.helper.ara import denormalize

path = files('eis1600.gazetteers.data').joinpath('spelling_gazetteer.csv')


@Singleton
class Spellings:
    __tot = None

    def __init__(self) -> None:
        df = read_csv(path)
        df['NGRAM'] = df['NGRAM'].astype('uint8')
        df['CATEGORY'] = df['CATEGORY'].astype('category')

        sorted_df = df.sort_values(by=['NGRAM'], ascending=False)
        Spellings.__tot = sorted_df['VALUE'].to_list()

    @staticmethod
    def get_denormalized_list() -> List[str]:
        return [denormalize(t) for t in Spellings.__tot]
