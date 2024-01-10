from glob import glob
from os.path import splitext, split, exists
from typing import List, Optional
from pathlib import Path

from eis1600.markdown.md_to_bio import bio_to_md

from eis1600.dates.methods import date_annotate_miu_text
from eis1600.helper.markdown_patterns import CATEGORY_PATTERN, HEADER_END_PATTERN, HEADING_PATTERN, \
    NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN, MIU_TAG_PATTERN, \
    MIU_UID_PATTERN, NEW_LINE_INSIDE_PARAGRAPH_NOT_POETRY_PATTERN, PAGE_TAG_PATTERN, \
    PARAGRAPH_TAG_MISSING, EMPTY_PARAGRAPH_CHECK_PATTERN, \
    POETRY_ATTACHED_AFTER_PAGE_TAG, SIMPLE_MARKDOWN, \
    MISSING_DIRECTION_TAG_PATTERN, SPAN_ELEMENTS, TEXT_STARTS_WITH_PARAGRAPH, TILDA_HICKUPS_PATTERN
from eis1600.miu.HeadingTracker import HeadingTracker
from eis1600.miu.yml_handling import create_yml_header, extract_yml_header_and_text
from eis1600.nlp.utils import annotate_miu_text, insert_onom_tag, insert_onomastic_tags, aggregate_STFCON_classes, \
    merge_ner_with_person_classes, merge_ner_with_toponym_classes
from eis1600.processing.postprocessing import write_updated_miu_to_file
from eis1600.processing.preprocessing import get_yml_and_miu_df


def check_file_for_mal_formatting(infile: str, content: str):
    if TEXT_STARTS_WITH_PARAGRAPH.match(content) \
            or PARAGRAPH_TAG_MISSING.search(content) \
            or SIMPLE_MARKDOWN.search(content) \
            or NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN.search(content) \
            or TILDA_HICKUPS_PATTERN.search(content) \
            or NEW_LINE_INSIDE_PARAGRAPH_NOT_POETRY_PATTERN.search(content) \
            or EMPTY_PARAGRAPH_CHECK_PATTERN.search(content) \
            or SPAN_ELEMENTS.search(content) \
            or MISSING_DIRECTION_TAG_PATTERN.search(content):
        # Poetry is still to messed up, do not bother with it for now
        # or POETRY_ATTACHED_AFTER_PAGE_TAG.search(content):
        error = ''
        if TEXT_STARTS_WITH_PARAGRAPH.match(content):
            error += '\n * Text does not start with a MIU tag, check if the preface is tagged as PARATEXT.'
        if PARAGRAPH_TAG_MISSING.search(content):
            error += '\n * There are missing paragraph tags.'
        if SIMPLE_MARKDOWN.search(content):
            error += '\n * There is simple mARkdown left.'
        if NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN.search(content):
            error += '\n * There are elements missing the double newline (somewhere the emtpy line is missing).'
        if TILDA_HICKUPS_PATTERN.search(content):
            error += '\n * There is this pattern with tildes: `~\\n~`.'
        if NEW_LINE_INSIDE_PARAGRAPH_NOT_POETRY_PATTERN.search(content):
            error += '\n * There is a single newline inside a paragraph (somewhere the emtpy line is missing).'
        if EMPTY_PARAGRAPH_CHECK_PATTERN.search(content):
            error += '\n * There are empty paragraphs in the text.'
        if SPAN_ELEMENTS.search(content):
            error += '\n * There are span elements in the text.'
        if MISSING_DIRECTION_TAG_PATTERN.search(content):
            error += '\n * There are missing direction tags at the beginning of paragraphs, fix it by running ' \
                     f'`update_uids` on {infile}'
        # if POETRY_ATTACHED_AFTER_PAGE_TAG.search(content):
        #     error += '\n * There is poetry attached to a PageTag (there should be a linebreak instead).'

        raise ValueError(
                f'Correct the following errors and run\n'
                f'update_uids {infile}\n'
                f'open -a kate {infile}\n'
                f'kate {infile}\n'
                f'{error}'
        )


def disassemble_text(infile: str, out_path: str, verbose: Optional[bool] = None) -> None:
    """Disassemble text into MIU files (only used to check formatting)

    Retrieve MIU files by disassembling the text based on the EIS1600 mARkdown.
    :param str infile: Path to the file which is to be disassembled.
    :param str out_path: Path to the MIU repo.
    :param bool verbose: If True outputs a notification of the file which is currently processed, optional.
    """

    heading_tracker = HeadingTracker()
    path, uri = split(infile)
    uri, ext = splitext(uri)
    author, work, edition = uri.split('.')
    path = out_path + '/'.join([author, '.'.join([author, work])]) + '/'
    ids_file = path + uri + '.IDs'
    yml_status = path + uri + '.STATUS.yml'
    yml_data = path + uri + '.YAMLDATA.yml'
    miu_dir = Path(path + 'MIUs/')
    uid = ''
    miu_text = ''
    yml_header = ''

    if verbose:
        print(f'Disassemble {uri}')

    miu_dir.mkdir(parents=True, exist_ok=True)
    miu_uri = miu_dir.__str__() + '/' + uri + '.'

    mal_formatted = []

    with open(infile, 'r', encoding='utf8') as text:
        header_text = text.read().split('#META#Header#End#\n\n')

        try:
            check_file_for_mal_formatting(infile, header_text[1])
        except ValueError:
            raise

        text.seek(0)

        with open(ids_file, 'w', encoding='utf8') as ids_tree:
            with open(yml_data, 'w', encoding='utf-8') as yml_data_fh:
                text.seek(0)
                for text_line in iter(text):
                    if HEADER_END_PATTERN.match(text_line):
                        uid = 'header'
                        miu_text += text_line
                        with open(miu_uri + uid + '.EIS1600', 'w', encoding='utf8') as miu_file:
                            miu_file.write(miu_text + '\n')
                            ids_tree.write(uid + '\n')
                        miu_text = ''
                        uid = 'preface'
                        next(text)  # Skip empty line after header
                    elif MIU_UID_PATTERN.match(text_line):
                        if HEADING_PATTERN.match(text_line):
                            m = HEADING_PATTERN.match(text_line)
                            heading_text = m.group('heading')
                            if PAGE_TAG_PATTERN.search(heading_text):
                                heading_text = PAGE_TAG_PATTERN.sub('', heading_text)
                            heading_tracker.track_headings(len(m.group('level')), heading_text)
                        if miu_text:
                            # Do not create a preface MIU file if there is no preface
                            with open(miu_uri + uid + '.EIS1600', 'w', encoding='utf8') as miu_file:
                                miu_file.write(miu_text + '\n')
                                ids_tree.write(uid + '\n')
                            yml_data_fh.write('#' + uid + '\n---\n' + yml_header)
                        m = MIU_TAG_PATTERN.match(text_line)
                        uid = m.group('UID')
                        category = ''
                        try:
                            category = CATEGORY_PATTERN.search(m.group('category')).group(0)
                        except AttributeError:
                            mal_formatted.append(m.group('category'))
                        yml_header = create_yml_header(category, heading_tracker.get_curr_state())
                        miu_text = yml_header
                        miu_text += text_line
                    else:
                        miu_text += text_line

                    if PAGE_TAG_PATTERN.search(text_line):
                        heading_tracker.track_pages(PAGE_TAG_PATTERN.search(text_line).group(0))

                # last MIU needs to be written to file when the for-loop is finished
                with open(miu_uri + uid + '.EIS1600', 'w', encoding='utf8') as miu_file:
                    miu_file.write(miu_text + '\n')
                    ids_tree.write(uid + '\n')
                yml_data_fh.write('#' + uid + '\n---\n' + yml_header + '\n\n')

                if mal_formatted:
                    error = f'Something seems to be mal-formatted, check:\n{infile}'
                    for elem in mal_formatted:
                        error += f'\n * {elem}'
                    raise ValueError(error)


def reassemble_text(infile: str, out_path: str, verbose: Optional[bool] = None) -> None:
    """Reassemble text from MIU files.

    Reassemble text from MIU files.
    :param str infile: Path to the IDs file of the text to reassemble from MIU files.
    :param str out_path: Path to the TEXT repo.
    :param bool verbose: If True outputs a notification of the file which is currently processed, optional.
    """
    file_path, uri = split(infile)
    file_path += '/'
    uri, ext = splitext(uri)
    author, work, text = uri.split('.')
    path = out_path + '/'.join([author, '.'.join([author, work])]) + '/' + uri
    ids = []

    if verbose:
        print(f'Reassemble {uri}')

    with open(file_path + uri + '.IDs', 'r', encoding='utf-8') as ids_file:
        ids.extend([line[:-1] for line in ids_file.readlines()])

    with open(path + '.EIS1600', 'w', encoding='utf-8') as text_file:
        with open(file_path + uri + '.YAMLDATA.yml', 'w', encoding='utf-8') as yml_data:
            for i, miu_id in enumerate(ids):
                miu_file_path = file_path + 'MIUs/' + uri + '.' + miu_id + '.EIS1600'
                with open(miu_file_path, 'r', encoding='utf-8') as miu_file_object:
                    miu_text_line_iter = iter(miu_file_object)
                    yml_header, text = extract_yml_header_and_text(miu_text_line_iter, i == 0)
                text_file.write(text)
                yml_data.write('#' + miu_id + '\n---\n' + yml_header + '\n\n')


def get_mius(infile: str) -> List[str]:
    """Get a list of paths to all MIU files from the infile text (including the HEADER MIU)

    :param infile: URI of text for which all MIU files are retrieved
    :return List[str]: A List of path to all the MIU files from the text
    """
    file_path, uri = split(infile)
    uri, ext = splitext(uri)
    file_path += '/'
    ids = []
    mius = []

    with open(infile, 'r', encoding='utf-8') as ids_file:
        ids.extend([line[:-1] for line in ids_file.readlines()])

    for i, miu_id in enumerate(ids):
        if miu_id != 'preface':
            mius.extend(glob(file_path + 'MIUs/' + uri + '.' + miu_id + '.EIS1600'))

    return mius


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
