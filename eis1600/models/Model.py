from threading import Lock
from typing import List

from camel_tools.ner import NERecognizer


class Model:
    __model = None
    __lock = Lock()

    def __init__(self, model_path: str) -> None:
        Model.__model = NERecognizer(model_path)
        Model.__lock = Lock()

    @staticmethod
    def predict_sentence(tokens: List[str]) -> List[str]:
        with Model.__lock:
            return Model.__model.predict_sentence(tokens)
