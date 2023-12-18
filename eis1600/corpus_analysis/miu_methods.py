from typing import Dict, Tuple

from eis1600.dates.methods import date_annotate_miu_text
from eis1600.markdown.md_to_bio import bio_to_md
from eis1600.miu.yml_handling import add_annotated_entities_to_yml
from eis1600.nlp.utils import aggregate_STFCON_classes, annotate_miu_text, insert_onom_tag, \
    insert_onomastic_tags, merge_ner_with_person_classes, merge_ner_with_toponym_classes
from eis1600.processing.postprocessing import merge_tagslists, reconstruct_miu_text_with_tags
from eis1600.processing.preprocessing import get_yml_and_miu_df


def analyse_miu(tup: Tuple[str, str, bool]) -> Dict:
    """Analysis the miu with our models.

    This methods applies our models to the text of the MIU and thereby runs different analysis (NER, POS, LEMMAS,
    ROOTS, TOPONYMS, PERSONS, ONOMASTICS, DATES). Results are added to the df representation of the MIU. Returns a
    JSON object which contains yml information, as well as the df with all analysis results.
    :param Tuple tup: Params are given as a Tuple: (uid: str, miu_as_text: str, analyse_flag: bool).
    :return Dict: JSON representation of the miu, including yml header and analysis results.
    """
    uid, miu_as_text, analyse_flag = tup

    # 1. open miu file and disassemble the file to its parts
    yml_handler, df = get_yml_and_miu_df(miu_as_text)

    if analyse_flag:
        # 2. annotate NEs, POS and lemmatize. NE are: person + relation(s), toponym + relation, onomastic information
        df['NER_LABELS'], df['LEMMAS'], df['POS_TAGS'], df['ROOTS'], ST_labels, FCO_labels, \
        df['TOPONYM_LABELS'] = annotate_miu_text(df)

        # 3. convert cameltools labels format to markdown format
        aggregated_stfco_labels = aggregate_STFCON_classes(ST_labels, FCO_labels)
        ner_tags = bio_to_md(df['NER_LABELS'].to_list())  # camel2md_as_list(df['NER_LABELS'].tolist())
        ner_tags_with_person_classes = merge_ner_with_person_classes(ner_tags, aggregated_stfco_labels)
        toponym_labels_md = bio_to_md(df['TOPONYM_LABELS'].to_list(), sub_class=True)
        df['NER_TAGS'] = merge_ner_with_toponym_classes(ner_tags_with_person_classes, toponym_labels_md)

        # 4. annotate dates
        df['DATE_TAGS'] = date_annotate_miu_text(df[['TOKENS']], uid, yml_handler)

        # 5. insert BONOM and EONOM tags with the pretrained transformer model
        df['ONOM_TAGS'] = insert_onom_tag(df)

        # 6. annotate onomastic information
        df['ONOMASTIC_TAGS'] = insert_onomastic_tags(df)

        # TODO 6. disambiguation of toponyms (same toponym, different places) --> replace ambiguous toponyms flag
        # TODO 9. get frequencies of unidentified entities (toponyms, nisbas)

        # 11. reconstruct the text, populate yml with annotated entities and save it to the output file
        columns_of_automated_tags = ['DATE_TAGS', 'ONOM_TAGS', 'ONOMASTIC_TAGS', 'NER_TAGS']
        for col in columns_of_automated_tags:
            if col in df.columns:
                df['TAGS_LISTS'] = df.apply(lambda x: merge_tagslists(x['TAGS_LISTS'], x[col]), axis=1)
        df_subset = df[['SECTIONS', 'TOKENS', 'TAGS_LISTS']]

        add_annotated_entities_to_yml(df_subset, yml_handler, uid)
        # updated_text = reconstruct_miu_text_with_tags(df_subset)

    # return as JSON Object
    author, text, edition, miu_uid = uid.split('.')
    yml_init = {'author': author, 'text': text, 'edition': edition, 'UID': miu_uid}
    miu_as_json = {'yml': yml_handler.to_json(yml_init), 'df': df.to_json(force_ascii=False, compression=None)}

    return miu_as_json
