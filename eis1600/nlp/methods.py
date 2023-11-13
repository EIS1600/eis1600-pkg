from os.path import exists

from eis1600.nlp.ToponymTagger import ToponymTagger

from eis1600.processing.preprocessing import get_yml_and_miu_df


def annotate_miu_file(path: str, tsv_path=None, output_path=None, force_annotation=False):
    if output_path is None:
        output_path = path
    if tsv_path is None:
        tsv_path = path.replace('.EIS1600', '.tsv')

    # if the file is already annotated, do nothing
    if exists(tsv_path) and not force_annotation:
        return

    with open(path, 'r+', encoding='utf-8') as miu_file_object:
        # 1. open miu file and disassemble the file to its parts
        yml_handler, df = get_yml_and_miu_df(miu_file_object)

        # 2. annotate NEs, POS and lemmatize. NE are: person + relation(s), toponym + relation, onomastic information
        df['NER_LABELS'], df['LEMMAS'], df['POS_TAGS'], df['ROOTS'], ST_labels, FCO_labels, \
            df['TOPONYM_LABELS'] = annotate_miu_text(df)

        # TODO check if this is really faster

        # 3. convert cameltools labels format to markdown format
        aggregated_stfco_labels = aggregate_STFCON_classes(ST_labels, FCO_labels)
        ner_tags = bio_to_md(df['NER_LABELS'].to_list())  # camel2md_as_list(df['NER_LABELS'].tolist())
        ner_tags_with_person_classes = merge_ner_with_person_classes(ner_tags, aggregated_stfco_labels)
        toponym_labels_md = bio_to_md(df['TOPONYM_LABELS'].to_list(), sub_class=True)
        df['NER_TAGS'] = merge_ner_with_toponym_classes(ner_tags_with_person_classes, toponym_labels_md)

        # 4. annotate dates
        df['DATE_TAGS'] = date_annotate_miu_text(df[['TOKENS']], path, yml_handler)

        # 5. insert BONOM and EONOM tags with the pretrained transformer model
        df['ONOM_TAGS'] = insert_onom_tag(df)

        # 6. annotate onomastic information
        df['ONOMASTIC_TAGS'] = insert_onomastic_tags(df)

        # TODO 6. disambiguation of toponyms (same toponym, different places) --> replace ambiguous toponyms flag
        # TODO 9. get frequencies of unidentified entities (toponyms, nisbas)

        # 10. save csv file
        df.to_csv(tsv_path, index=False, sep='\t')

        # 11. reconstruct the text, populate yml with annotated entities and save it to the output file
        if output_path == path:
            write_updated_miu_to_file(
                miu_file_object, yml_handler, df[['SECTIONS', 'TOKENS', 'TAGS_LISTS', 'DATE_TAGS', 'ONOM_TAGS',
                                                  'ONOMASTIC_TAGS', 'NER_TAGS']]
                )
        else:
            with open(output_path, 'w', encoding='utf-8') as out_file_object:
                write_updated_miu_to_file(
                        out_file_object, yml_handler, df[['SECTIONS', 'TOKENS', 'TAGS_LISTS', 'DATE_TAGS', 'ONOM_TAGS',
                                                          'ONOMASTIC_TAGS', 'NER_TAGS']]
                )
