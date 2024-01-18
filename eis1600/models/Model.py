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

    @staticmethod
    def predict_sentence_with_windowing(tokens: List[str]) -> List[str]:
        windows = []
        batch_length = 450
        window_size = 50

        i = 0
        # TODO give more overlap to last window because left-over string could be only 3 tokens long -> cannot be
        #  analysed
        last_window_overlap = 0
        while len(tokens) > i * batch_length:
            start = i * batch_length
            if i > 0:
                start -= window_size
            end = (i + 1) * batch_length
            if end >= len(tokens):
                end = len(tokens) - 1
            windows.append(tokens[start: end])
            i += 1

        prediction_lists = []
        with Model.__lock:
            for window in windows:
                prediction_lists.append(Model.__model.predict_sentence(window))

        # Align windows
        predictions = []
        for idx, pred_list in enumerate(prediction_lists):
            preds = pred_list[window_size:]
            if idx == 0:
                preds = pred_list
            predictions.extend(preds)

        print(f'Tokens: {len(tokens)}, Predictions: {len(predictions)}')
        return prediction_lists
