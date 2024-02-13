from threading import Lock
from typing import List, Optional

from camel_tools.disambig.mle import MLEDisambiguator
from camel_tools.tagger.default import DefaultTagger
from eis1600.helper.Singleton import singleton


@singleton
class POSTagger:
    def __init__(self) -> None:
        self.model = DefaultTagger(MLEDisambiguator.pretrained(), 'pos')
        self.lock = Lock()

    def get_pos(self, tokens: List[str], debug: Optional[bool] = False) -> List[str]:
        with self.lock:
            if debug:
                print('POS')
            return self.model.tag(tokens)
