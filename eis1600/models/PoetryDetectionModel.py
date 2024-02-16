from typing import Dict, List, Optional, Tuple
from threading import Lock
from importlib_resources import files

from pandas import read_csv
from transformers import pipeline

from eis1600.helper.Singleton import singleton

poetic_meters_path = files('eis1600.models.data').joinpath('poetic_meters.csv')


@singleton
class PoetryDetectionModel:
    def __init__(self) -> None:
        self.model = pipeline('text-classification', model='CAMeL-Lab/bert-base-arabic-camelbert-mix-poetry')
        self.lock = Lock()
        poetic_meters__df = read_csv(poetic_meters_path)
        self.not_poetry = poetic_meters__df.loc[~poetic_meters__df['POETRY'], 'METER']

    def predict_is_poetry(self, tokens: List[str], debug: Optional[bool] = False) -> Tuple[bool, Dict]:
        with self.lock:
            if debug:
                print('CAMeL-Lab/bert-base-arabic-camelbert-mix-poetry')
            res = self.model(' '.join(tokens))
            res = res[0]
            res['text'] = ' '.join(tokens)
            if res['label'] in self.not_poetry or res['score'] < 0.95:
                return False, res
            else:
                return True, res

