from typing import List
import string

from eis1600.markdown.md_to_bio import bio_to_md
from numpy import nan
from pandas import notna

from eis1600.nlp.cameltools import lemmatize_and_tag_ner, CamelToolsModels


def annotate_miu_text(df):
    lemmas, ner_tags, pos_tags, root_tags, st_tags, fco_tags, toponym_tags = ['_'], ['_'], ['_'], ['_'], ['_'], ['_'], ['_']
    section_id, temp_tokens = None, []
    # TODO STOP processing per section - rather, use overlapping windows of tokens. Sections are not a reliable unit
    for entry in list(zip(df['SECTIONS'].to_list(), df['TOKENS'].fillna('-').to_list()))[1:]:
        _section, _token = entry[0], entry[1]
        if _section is not None:
            # Start a new section
            if len(temp_tokens) > 0:
                # 1. process the previous section
                _labels = lemmatize_and_tag_ner(temp_tokens)
                _, _ner_tags, _lemmas, _dediac_lemmas, _pos_tags, _root_tags, _st_tags, _fco_tags, _toponym_tags = zip(
                        *_labels)
                ner_tags.extend(_ner_tags)
                lemmas.extend(_dediac_lemmas)
                pos_tags.extend(_pos_tags)
                root_tags.extend(_root_tags)
                fco_tags.extend(_fco_tags)
                st_tags.extend(_st_tags)
                toponym_tags.extend(_toponym_tags)
                # 2. reset variables
                section_id, temp_tokens = None, []

        token = _token if _token not in ['', None] else '_'
        temp_tokens.append(token)

    if len(temp_tokens) > 0:
        _labels = lemmatize_and_tag_ner(temp_tokens)
        _, _ner_tags, _lemmas, _dediac_lemmas, _pos_tags, _root_tags, _st_tags, _fco_tags, _toponym_tags = zip(*_labels)
        ner_tags.extend(_ner_tags)
        lemmas.extend(_dediac_lemmas)
        pos_tags.extend(_pos_tags)
        root_tags.extend(_root_tags)
        fco_tags.extend(_fco_tags)
        st_tags.extend(_st_tags)
        toponym_tags.extend(_toponym_tags)

    return ner_tags, lemmas, pos_tags, root_tags, st_tags, fco_tags, toponym_tags


def aggregate_STFCON_classes(st_list: list, fco_list: list) -> List[str]:
    label_dict = {
        "B-FAMILY": "F",
        "I-FAMILY": "F",
        "B-CONTACT": "C",
        "I-CONTACT": "C",
        "B-OPINION": "O",
        "I-OPINION": "O",
        "O": "",
        "_": "",
        "B-TEACHER": "T",
        "I-TEACHER": "T",
        "B-STUDENT": "S",
        "I-STUDENT": "S",
        "I-NEUTRAL": "X",
        "B-NEUTRAL": "X",
    }
    aggregated_labels = []
    for a, b in zip(st_list, fco_list):
        labels = f"{label_dict.get(a, '')}{label_dict.get(b, '')}"
        if a == b:
            labels = label_dict.get(a, '')
        else:
            labels = labels.replace("X", "")
        aggregated_labels.append(labels)
    return aggregated_labels


def merge_ner_with_person_classes(ner_labels, aggregated_stfco_labels):
    merged_labels = []
    for a, b in zip(ner_labels, aggregated_stfco_labels):
        if notna(a) and a[:2] == "ÜP":
            postfix = "X"
            if b.strip() != "":
                postfix = b.strip()
            a = a + postfix
        merged_labels.append(a)
    return merged_labels


def merge_ner_with_toponym_classes(ner_labels: List[str], toponym_labels: List[str]) -> List[str]:
    merged_labels = []
    for a, b in zip(ner_labels, toponym_labels):
        if notna(a) and a[:2] == 'ÜT':
            if b:
                merged_labels.append(b)
            else:
                merged_labels.append(a + 'X')
        else:
            merged_labels.append(a)
    return merged_labels


def insert_onom_tag(df) -> list:
    tokens = df['TOKENS'].fillna('-').to_list()
    nasab_tagger = CamelToolsModels.getNasabModel()
    shortend_list_of_tokens = tokens[1:]
    __shortend_list_limit = 120
    if len(tokens) > __shortend_list_limit:
        shortend_list_of_tokens = tokens[1:__shortend_list_limit]
    for idx, t in enumerate(shortend_list_of_tokens):
        if t.strip() == "":
            shortend_list_of_tokens[idx] = "-"
    nasab_labels = nasab_tagger.predict_sentence(shortend_list_of_tokens)
    punct = "..،_" + string.punctuation
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


def insert_onomastic_tags(df):
    onomastic_tagger = CamelToolsModels.getOnomasticModel()
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
        onomastic_labels = onomastic_tagger.predict_sentence(nasab_tokens)
        ono_tags = bio_to_md(onomastic_labels)

        for i, tag in enumerate(ono_tags):
            onomastic_tags[start_nasab_id + i] = tag

    return onomastic_tags
