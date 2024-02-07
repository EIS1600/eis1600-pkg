from typing import List, Optional
from threading import Lock
from importlib_resources import files

from pandas import read_csv
from transformers import pipeline

from eis1600.helper.Singleton import singleton

poetic_meters_path = files('eis1600.model.data').joinpath('poetic_meters.csv')


@singleton
class PoetryDetectionModel:
    def __init__(self) -> None:
        self.model = pipeline('text-classification', model='CAMeL-Lab/bert-base-arabic-camelbert-mix-poetry')
        self.lock = Lock()
        poetic_meters__df = read_csv(poetic_meters_path, columns=['METER', 'TRANSLIT', 'POETRY'])
        self.not_poetry = poetic_meters__df.loc[~poetic_meters__df['POETRY'], 'METER']

    def predict_is_poetry(self, tokens: List[str], debug: Optional[bool] = False) -> bool:
        with self.lock:
            if debug:
                print('CAMeL-Lab/bert-base-arabic-camelbert-mix-poetry')
            res = self.model(' '.join(tokens))
            print(res)
            res = res[0]
            if res['label'] in self.not_poetry or res['score'] < 0.75:
                return False
            else:
                return True

