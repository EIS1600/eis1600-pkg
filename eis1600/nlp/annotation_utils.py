from typing import List, Optional

from numpy import nan

from eis1600.bio.md_to_bio import bio_to_md
from eis1600.models.Lemmatizer import Lemmatizer
from eis1600.models.POSTagger import POSTagger
from eis1600.models.NERModel import NERModel
from eis1600.models.Disambiguator import Disambiguator
from eis1600.models.NasabDetectionModel import NasabDetectionModel
from eis1600.models.OnomsticElementsModel import OnomasticElementsModel
from eis1600.models.FamilyContactOpinionModel import FCOModel
from eis1600.models.StudentTeacherModel import STModel
from eis1600.models.ToponymModel import ToponymModel


def insert_onom_tag(df, debug: Optional[bool] = False) -> List[str]:
    tokens = df['TOKENS'].fillna('-').to_list()
    nasab_tagger = NasabDetectionModel()
    shortend_list_of_tokens = tokens[1:]
    __shortend_list_limit = 120
    if len(tokens) > __shortend_list_limit:
        shortend_list_of_tokens = tokens[1:__shortend_list_limit]
    for idx, t in enumerate(shortend_list_of_tokens):
        if t.strip() == "":
            shortend_list_of_tokens[idx] = "-"
    nasab_labels = nasab_tagger.predict_sentence(shortend_list_of_tokens, debug)
    nasab = ['_']
    nasab_started = False
    for token, label in zip(shortend_list_of_tokens, nasab_labels):
        if label == "B-NASAB":
            # Start a new NASAB
            nasab.append("BONOM")
            nasab_started = True
        elif label == "I-NASAB":
            nasab.append(nan)
        else:
            if nasab_started:
                nasab.append("EONOM")
                nasab_started = False
            else:
                nasab.append(nan)
    if nasab_started:
        nasab[-1] = "EONOM"
    # merge the shortend list
    if len(tokens) > __shortend_list_limit:
        nasab.extend([nan] * (len(tokens) - __shortend_list_limit))
    return nasab


def insert_onomastic_tags(df, debug: Optional[bool] = False):
    onomastic_tagger = OnomasticElementsModel()
    onomastic_tags = [nan] * len(df['TOKENS'])
    start_nasab_id, end_nasab_id = -1, -1

    # Find BNASAB & ENASAB
    for idx, tag in enumerate(df['ONOM_TAGS'].to_list()):
        if "BONOM" == tag:
            start_nasab_id = idx
        elif "EONOM" == tag:
            end_nasab_id = idx
            break

    if 0 < start_nasab_id < end_nasab_id:
        nasab_tokens = df['TOKENS'].fillna('-').to_list()[start_nasab_id:end_nasab_id]
        onomastic_labels = onomastic_tagger.predict_sentence(nasab_tokens, debug)
        ono_tags = bio_to_md(onomastic_labels)

        for i, tag in enumerate(ono_tags):
            onomastic_tags[start_nasab_id + i] = tag

    return onomastic_tags


def annotate_miu_text(df, debug: Optional[bool] = False):
    lemmas, pos_tags, root_tags, ner_tags, st_tags, fco_tags, toponym_tags = ['_'], ['_'], ['_'], ['_'], ['_'], ['_'], ['_']
    section_id, temp_tokens = None, []
    for _section, _token in list(zip(df['SECTIONS'].to_list(), df['TOKENS'].fillna('-').to_list()))[1:]:
        if _section:
            # Start a new section
            if len(temp_tokens) > 0:
                # 1. process the previous section
                lemmas.extend(Lemmatizer().get_lemmas(temp_tokens, debug))
                pos_tags.extend(POSTagger().get_pos(temp_tokens, debug))
                root_tags.extend(Disambiguator().get_roots(temp_tokens, debug))
                ner_tags.extend(NERModel().predict_sentence(temp_tokens, debug))
                st_tags.extend(STModel().predict_sentence(temp_tokens, debug))
                fco_tags.extend(FCOModel().predict_sentence(temp_tokens, debug))
                toponym_tags.extend(ToponymModel().predict_sentence(temp_tokens, debug))

                # 2. reset variables
                section_id, temp_tokens = None, []

        token = _token if _token else '_'
        temp_tokens.append(token)

    if len(temp_tokens) > 0:
        lemmas.extend(Lemmatizer().get_lemmas(temp_tokens, debug))
        pos_tags.extend(POSTagger().get_pos(temp_tokens, debug))
        root_tags.extend(Disambiguator().get_roots(temp_tokens, debug))
        ner_tags.extend(NERModel().predict_sentence(temp_tokens, debug))
        st_tags.extend(STModel().predict_sentence(temp_tokens, debug))
        fco_tags.extend(FCOModel().predict_sentence(temp_tokens, debug))
        toponym_tags.extend(ToponymModel().predict_sentence(temp_tokens, debug))

    return ner_tags, lemmas, pos_tags, root_tags, st_tags, fco_tags, toponym_tags
