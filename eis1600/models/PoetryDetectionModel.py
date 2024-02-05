from threading import Lock
from typing import List, Optional

from transformers import pipeline

from eis1600.helper.Singleton import singleton


@singleton
class PoetryDetectionModel:
    def __init__(self) -> None:
        self.model = pipeline('text-classification', model='CAMeL-Lab/bert-base-arabic-camelbert-mix-poetry')
        self.lock = Lock()

    def predict_is_poetry(self, tokens: List[str], debug: Optional[bool] = False) -> bool:
        not_poetry = ['شعر حر', 'شعر التفعيلة', '']
        with self.lock:
            if debug:
                print('CAMeL-Lab/bert-base-arabic-camelbert-mix-poetry')
            res = self.model(' '.join(tokens))
            print(res)
            res = res[0]
            if res['label'] in not_poetry or res['score'] < 0.75:
                return False
            else:
                return True

