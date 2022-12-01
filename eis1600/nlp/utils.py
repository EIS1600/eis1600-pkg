from typing import List

from eis1600.nlp.cameltools import lemmatize_and_tag_ner


def annotate_miu_text(df):
    lemmas, ner_tags, pos_tags = ['_'], ['_'], ['_']
    section_id, temp_tokens = None, []
    for entry in list(zip(df['SECTIONS'].to_list(), df['TOKENS'].to_list()))[1:]:
        _section, _token = entry[0], entry[1]
        if _section is not None:
            # Start a new section
            if len(temp_tokens) > 0:
                # 1. process the previous section
                _labels = lemmatize_and_tag_ner(temp_tokens)
                _, _ner_tags, _lemmas, _dediac_lemmas, _pos_tags = zip(*_labels)
                ner_tags.extend(_ner_tags)
                lemmas.extend(_dediac_lemmas)
                pos_tags.extend(_pos_tags)

                # 2. reset variables
                section_id, temp_tokens = None, []

        token = _token if _token not in ['', None] else '_'
        temp_tokens.append(token)

    if len(temp_tokens) > 0:
        _labels = lemmatize_and_tag_ner(temp_tokens)
        _, _ner_tags, _lemmas, _dediac_lemmas, _pos_tags = zip(*_labels)
        ner_tags.extend(_ner_tags)
        lemmas.extend(_dediac_lemmas)
        pos_tags.extend(_pos_tags)
    return ner_tags, lemmas, pos_tags


def camel2md_as_list(labels: list) -> List[str]:
    default_str = ''
    types_mapping = {
        'LOC': 'ÜT',
        'PERS': 'ÜP'
    }
    converted_tokens, temp_tokens, temp_class = [], [], None
    for _label in labels:
        if _label is None:
            converted_tokens.append(default_str)
        else:
            # Check if the first letter of the label is 'o' or 'B' a Begining of an NE
            if _label[0] in ['O', 'B', '_']:
                if len(temp_tokens) > 0 and temp_class is not None:
                    converted_tokens.append(f"{types_mapping.get(temp_class, 'ÜM')}{len(temp_tokens)}")  # e.g. ÜP3
                    converted_tokens.extend([default_str] * (len(temp_tokens) - 1))
                    # reset temp variables
                    temp_tokens, temp_class = [], None

                if _label in ['O', '_']:
                    converted_tokens.append(default_str)
                else:
                    temp_tokens.append(_label)
                    temp_class = _label[2:]

            else:
                if temp_class is not None:
                    temp_tokens.append(_label)
                else:
                    converted_tokens.append(default_str)
    if len(temp_tokens) > 0 and temp_class is not None:
        converted_tokens.append(f"{types_mapping.get(temp_class, 'ÜM')}{len(temp_tokens)}")
        converted_tokens.extend([default_str] * (len(temp_tokens) - 1))
    return converted_tokens