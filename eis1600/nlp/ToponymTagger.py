from os.path import isdir
from typing import List

from camel_tools.ner import NERecognizer
from eis1600.helper.Synchronized import synchronized

from eis1600.helper.Singleton import singleton

from eis1600.helper.repo import PRETRAINED_MODELS_REPO


@singleton
class ToponymTagger:
    __model = None

    def __init__(self) -> None:
        model_path = PRETRAINED_MODELS_REPO + 'camelbert-ca-finetuned_toponyms/'
        if not isdir(PRETRAINED_MODELS_REPO):
            raise Exception(f'We miss our custom ML models in {PRETRAINED_MODELS_REPO}')
        if not isdir(model_path):
            raise Exception(f'There is no {model_path} model')

        ToponymTagger.__model = NERecognizer(model_path)

    @synchronized
    @staticmethod
    def predict(tokens: List[str]) -> List[str]:
        predicions = ToponymTagger.__model.predict_sentence(tokens)
        return ['_'] + predicions
