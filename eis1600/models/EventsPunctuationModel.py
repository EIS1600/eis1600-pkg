from typing import List, Optional

from eis1600.models.Model import Model
from eis1600.helper.Singleton import singleton


@singleton
class EventsPunctuationModel(Model):

    def __init__(self) -> None:
        super().__init__('EIS1600_Pretrained_Models/camelbert-ca-events-punctuation/')

    def predict_sentence(self, tokens: List[str], debug: Optional[bool] = False) -> List[str]:
        class2punct = {"B-COMMA": "COMMA", "B-PERIOD": "PERIOD", "B-COLON": "COLON"}

        preds_class = super().predict_sentence(tokens, debug)
        preds_punct = [class2punct[p] if p in class2punct.keys() else None for p in preds_class]

        return preds_punct
