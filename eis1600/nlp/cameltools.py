from os.path import isdir

from camel_tools.ner import NERecognizer
from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.disambig.mle import MLEDisambiguator
from camel_tools.tagger.default import DefaultTagger
from camel_tools.utils.dediac import dediac_ar
from typing import Iterator, Tuple, Union

from eis1600.helper.repo import PRETRAINED_MODELS_REPO


class CamelToolsModels:
    __pos_tagger = None
    __mled_disambiguator = None
    __lemmatizer = None
    __ner_tagger = None
    __nasab_tagger = None
    __onomastic_tagger = None
    __st_tagger = None
    __fco_tagger = None
    __toponym_tagger = None

    __NASAB_MODEL_PATH = PRETRAINED_MODELS_REPO + "camelbert-ca-finetuned_nasab/"
    __NER_MODEL_PATH = PRETRAINED_MODELS_REPO + "camelbert-ca-finetuned_ner/"
    __ONOMASTIC_MODEL_PATH = PRETRAINED_MODELS_REPO + "camelbert-ca-finetuned_onomastic/"
    __STN_MODEL_PATH = PRETRAINED_MODELS_REPO + "camelbert-ca-finetuned_person_classification_STN/"
    __FCON_MODEL_PATH = PRETRAINED_MODELS_REPO + "camelbert-ca-finetuned_person_classification_FCN/"
    __TOPO_MODEL_PATH = PRETRAINED_MODELS_REPO + "camelbert-ca-finetuned_toponyms/"

    @staticmethod
    def getInstance():
        """ Static access method. """
        if CamelToolsModels.__ner_tagger is None or CamelToolsModels.__lemmatizer is None:
            CamelToolsModels()
        return CamelToolsModels.__mled_disambiguator, CamelToolsModels.__ner_tagger, CamelToolsModels.__lemmatizer, \
               CamelToolsModels.__pos_tagger, CamelToolsModels.__st_tagger, CamelToolsModels.__fco_tagger, \
               CamelToolsModels.__toponym_tagger

    @staticmethod
    def getNasabModel():
        """ Static access method. """
        if CamelToolsModels.__nasab_tagger is None:
            CamelToolsModels.__nasab_tagger = NERecognizer(CamelToolsModels.__NASAB_MODEL_PATH)
        return CamelToolsModels.__nasab_tagger

    @staticmethod
    def getOnomasticModel():
        """ Static access method. """
        if CamelToolsModels.__onomastic_tagger is None:
            CamelToolsModels.__onomastic_tagger = NERecognizer(CamelToolsModels.__ONOMASTIC_MODEL_PATH)
        return CamelToolsModels.__onomastic_tagger

    def __init__(self):
        """ Virtually private constructor. """
        if not isdir(PRETRAINED_MODELS_REPO):
            raise Exception(f'We miss our custom ML models in {PRETRAINED_MODELS_REPO}')

        if CamelToolsModels.__ner_tagger is not None:
            raise Exception("This class is a singleton!")
        else:
            CamelToolsModels.__mled_disambiguator = MLEDisambiguator.pretrained()
            CamelToolsModels.__lemmatizer = DefaultTagger(CamelToolsModels.__mled_disambiguator, 'lex')
            CamelToolsModels.__pos_tagger = DefaultTagger(CamelToolsModels.__mled_disambiguator, 'pos')
            CamelToolsModels.__ner_tagger = NERecognizer(CamelToolsModels.__NER_MODEL_PATH)  # .pretrained
            CamelToolsModels.__st_tagger = NERecognizer(CamelToolsModels.__STN_MODEL_PATH)
            CamelToolsModels.__fco_tagger = NERecognizer(CamelToolsModels.__FCON_MODEL_PATH)
            CamelToolsModels.__toponym_tagger = NERecognizer(CamelToolsModels.__TOPO_MODEL_PATH)


def lemmatize_and_tag_ner(tokens: Union[str, list]) -> Iterator[Tuple[str, ...]]:
    """Lemmatize the text and annotate named-entities.

    Lemmatize the text and annotated named-entities using Camel Tools models.
    :param tokens: a  string or a list of tokens to be annotated
    """
    mled_disambiguator, ner_tagger, lemmatizer, pos_tagger, st_tager, fco_tagger, toponym_tagger = \
        CamelToolsModels.getInstance()
    # if tokens is a string, then tokenize it
    if isinstance(tokens, str):
        tokens = simple_word_tokenize(tokens)
    ner_labels = ner_tagger.predict_sentence(tokens)
    st_labels = st_tager.predict_sentence(tokens)
    fco_labels = fco_tagger.predict_sentence(tokens)
    toponym_labels = toponym_tagger.predict_sentence(tokens)
    lemmas = lemmatizer.tag(tokens)
    pos_tags = pos_tagger.tag(tokens)
    root_tags = [d.analyses[0].analysis['root'] for d in mled_disambiguator.disambiguate(tokens)]
    dediac_lemmas = [dediac_ar(lemma) for lemma in lemmas]

    return zip(tokens, ner_labels, lemmas, dediac_lemmas, pos_tags, root_tags, st_labels, fco_labels, toponym_labels)
