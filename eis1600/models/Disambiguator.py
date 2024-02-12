from threading import Lock
from typing import List, Optional

from camel_tools.disambig.mle import MLEDisambiguator
from eis1600.helper.Singleton import singleton


@singleton
class Disambiguator:
    def __init__(self) -> None:
        self.model = MLEDisambiguator.pretrained()
        self.lock = Lock()

    def get_roots(self, tokens: List[str], debug: Optional[bool] = False) -> List[str]:
        with self.lock:
            if debug:
                print('Roots')
            return [d.analyses[0].analysis['root'] for d in self.model.disambiguate(tokens)]
