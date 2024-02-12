from threading import Lock
from typing import List, Optional

from camel_tools.disambig.mle import MLEDisambiguator
from camel_tools.tagger.default import DefaultTagger
from eis1600.helper.Singleton import singleton


@singleton
class Lemmatizer:
    def __init__(self) -> None:
        self.model = DefaultTagger(MLEDisambiguator.pretrained(), 'lex')
        self.lock = Lock()

    def get_lemmas(self, tokens: List[str], debug: Optional[bool] = False) -> List[str]:
        with self.lock:
            if debug:
                print('lemmatize')
            return self.model.tag(tokens)
