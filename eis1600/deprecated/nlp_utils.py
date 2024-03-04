from depricated.cameltools import lemmatize_and_tag_ner


def annotate_miu_text_old_routine(df):
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

