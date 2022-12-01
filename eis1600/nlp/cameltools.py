from camel_tools.ner import NERecognizer
from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.disambig.mle import MLEDisambiguator
from camel_tools.tagger.default import DefaultTagger
from camel_tools.utils.dediac import dediac_ar

from typing import Union


class CamelToolsModels:
    __pos_tagger = None
    __mled_disambiguator = None
    __lemmatizer = None
    __ner_tagger = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if CamelToolsModels.__ner_tagger is None or CamelToolsModels.__lemmatizer is None:
            CamelToolsModels()
        return CamelToolsModels.__ner_tagger, CamelToolsModels.__lemmatizer, CamelToolsModels.__pos_tagger

    def __init__(self):
        """ Virtually private constructor. """
        if CamelToolsModels.__ner_tagger is not None:
            raise Exception("This class is a singleton!")
        else:
            CamelToolsModels.__mled_disambiguator = MLEDisambiguator.pretrained()
            CamelToolsModels.__lemmatizer = DefaultTagger(CamelToolsModels.__mled_disambiguator, 'lex')
            CamelToolsModels.__pos_tagger = DefaultTagger(CamelToolsModels.__mled_disambiguator, 'pos')
            CamelToolsModels.__ner_tagger = NERecognizer.pretrained()


def lemmatize_and_tag_ner(tokens: Union[str, list]) -> list:
    """Lemmatize the text and annotate named-entities.

        Lemmatize the text and annotated named-entities using Camel Tools models.
        :param tokens: a  string or a list of tokens to be annotated
        """
    ner_tagger, lemmatizer, pos_tagger = CamelToolsModels.getInstance()
    # if tokens is a string, then tokenize it
    if isinstance(tokens, str):
        tokens = simple_word_tokenize(tokens)
    ner_labels = ner_tagger.predict_sentence(tokens)
    lemmas = lemmatizer.tag(tokens)
    pos_tags = pos_tagger.tag(tokens)
    dediac_lemmas = [dediac_ar(lemma) for lemma in lemmas]
    return list(zip(tokens, ner_labels, lemmas, dediac_lemmas, pos_tags))
