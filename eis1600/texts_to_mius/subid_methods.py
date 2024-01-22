from os.path import splitext

from eis1600.markdown.markdown_patterns import BIO_CHR_TO_NEWLINE_PATTERN, \
    HEADER_END_PATTERN, \
    MIU_SPLITTER_PATTERN, MIU_UID_TAG_PATTERN, SIMPLE_HEADING_OR_BIO_PATTERN, MISSING_DIRECTIONALITY_TAG_PATTERN, \
    MIU_TAG_AND_TEXT_PATTERN, \
    NEWLINES_CROWD_PATTERN, \
    NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN, ONLY_PAGE_TAG_PATTERN, PAGE_TAG_IN_BETWEEN_PATTERN, \
    PAGE_TAG_ON_NEWLINE_TMP_PATTERN, PAGE_TAG_PATTERN, \
    PAGE_TAG_SPLITTING_PARAGRAPH_PATTERN, UID_TAG_PATTERN, MIU_UID_TAG_AND_TEXT_SAME_LINE_PATTERN, \
    PARAGRAPH_UID_TAG_PATTERN
from eis1600.texts_to_mius.SubIDs import SubIDs
from eis1600.texts_to_mius.UIDs import UIDs
from eis1600.texts_to_mius.check_formatting_methods import check_formatting_before_update_ids


def pre_clean_text(text: str) -> str:
    text = NEWLINES_CROWD_PATTERN.sub('\n\n', text)
    text = NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN.sub('\n\n', text)
    text = text.replace(' \n', '\n')
    text = text.replace('\n ', '\n')
    text = PAGE_TAG_ON_NEWLINE_TMP_PATTERN.sub(r' \1', text)

    return text


def insert_ids(text: str) -> str:
    # disassemble text into paragraphs
    text = text.split('\n\n')
    text_updated = []

    uids = UIDs()

    text_iter = text.__iter__()
    paragraph = next(text_iter)
    prev_p = ''

    sub_ids = None

    # Insert UIDs and EIS1600 tags into the text
    while paragraph is not None:
        next_p = next(text_iter, None)

        if paragraph:
            # Only do this if paragraph is not empty
            if paragraph.startswith('#'):
                uid = uids.get_uid()
                sub_ids = SubIDs(uid)
                # Move content to an individual line
                paragraph = BIO_CHR_TO_NEWLINE_PATTERN.sub(r'\1\n\2', paragraph)
                paragraph = paragraph.replace('#', f'_ء_#={uid}=')
                # Insert a paragraph tag
                heading_and_text = paragraph.splitlines()
                if len(heading_and_text) == 2:
                    paragraph = heading_and_text[0] + f'\n\n_ء_={sub_ids.get_id()}= ::UNDEFINED:: ~\n_ء_ ' + \
                                heading_and_text[1]
                elif len(heading_and_text) > 2:
                    raise ValueError(
                            f'There is a single new line in this paragraph:\n{paragraph}'
                    )
                text_updated.append(paragraph)
            elif '%~%' in paragraph:
                paragraph = f'_ء_={sub_ids.get_id()}= ::POETRY:: ~\n_ء_ ' + '\n_ء_ '.join(paragraph.splitlines())
                text_updated.append(paragraph)
            elif PAGE_TAG_PATTERN.fullmatch(paragraph):
                page_tag = PAGE_TAG_PATTERN.match(paragraph).group('page_tag')
                if PAGE_TAG_SPLITTING_PARAGRAPH_PATTERN.search('\n\n'.join([prev_p, paragraph, next_p])):
                    if text_updated:
                        if text_updated[-1][-1] == ' ':
                            text_updated[-1] += page_tag + ' ' + next_p
                        else:
                            text_updated[-1] += ' ' + page_tag + ' ' + next_p
                        paragraph = next_p
                        next_p = next(text_iter, None)
                elif text_updated:
                    text_updated[-1] += ' ' + page_tag
            elif paragraph.startswith('::'):
                p_pieces = paragraph.splitlines()
                section_header = p_pieces[0]

                if '%~%' in paragraph:
                    paragraph = '\n_ء_ '.join(p_pieces[1:])
                elif len(p_pieces) > 2:
                    raise ValueError(
                            f'There is a single new line in this paragraph:\n{paragraph}'
                    )
                elif len(p_pieces) == 2:
                    paragraph = p_pieces[1]
                else:
                    raise ValueError(
                            'There is an empty paragraph, check with\n'
                            '::\\n[^هسءگؤقأذپيمجثاڤوضآرتنكزفبعٱشىصلدطغإـئظحةچخ_]'
                    )

                paragraph = f'_ء_={sub_ids.get_id()}= {section_header} ~\n_ء_ ' + paragraph
                text_updated.append(paragraph)
            else:
                paragraph = f'_ء_={sub_ids.get_id()}= ::UNDEFINED:: ~\n_ء_ ' + paragraph
                text_updated.append(paragraph)

        prev_p = paragraph
        paragraph = next_p

    # reassemble text
    text = '\n\n'.join(text_updated)

    return text


def update_ids(text: str) -> str:
    # 1. disassemble text into paragraphs
    text = text.split('\n\n')
    text_updated = []

    used_ids = []

    # 2. Collect existing UIDs
    for idx, paragraph in enumerate(text):
        if MIU_UID_TAG_PATTERN.match(paragraph):
            uid = int(MIU_UID_TAG_PATTERN.match(paragraph).group('UID'))
            if uid not in used_ids:
                used_ids.append(uid)
            else:
                # If in the review process an UID was accidentally inserted twice, just remove the second occurrence
                # - this element will get a new UID in the next steps.
                if MIU_UID_TAG_PATTERN.match(paragraph).group(1):
                    # Python returns None for empty capturing groups which messes up the string
                    text[idx] = MIU_UID_TAG_PATTERN.sub('\1', paragraph)
                else:
                    text[idx] = MIU_UID_TAG_PATTERN.sub('', paragraph)

    uids = UIDs(used_ids)

    text_iter = text.__iter__()
    paragraph = next(text_iter)
    prev_p = None

    # 3. Update MIU_UIDs (sub_ids are adjusted in the next step) and fix some structural problems
    while paragraph is not None:
        next_p = next(text_iter, None)

        if paragraph:
            # Only do this if paragraph is not empty
            if SIMPLE_HEADING_OR_BIO_PATTERN.match(paragraph):
                # Move content to an individual line
                paragraph = BIO_CHR_TO_NEWLINE_PATTERN.sub(r'\1\n\2', paragraph)
                uid = uids.get_uid()
                paragraph = paragraph.replace('#', f'_ء_#={uid}=')
                # Insert a paragraph tag
                heading_and_text = paragraph.splitlines()
                if len(heading_and_text) == 2:
                    paragraph = heading_and_text[0] + f'\n\n::UNDEFINED::\n\n_ء_ {heading_and_text[1]}'
                elif len(heading_and_text) > 2:
                    raise ValueError(
                            f'There is a single new line in this paragraph:\n{paragraph}'
                    )
            elif not UID_TAG_PATTERN.match(paragraph):
                if paragraph.startswith('::'):
                    p_pieces = paragraph.splitlines()
                    section_header = p_pieces[0]
                    if '%~%' in paragraph:
                        paragraph = '\n'.join(p_pieces[1:])
                    elif len(p_pieces) > 2:
                        raise ValueError(
                                f'There is a single new line in this paragraph:\n{paragraph}'
                        )
                    elif len(p_pieces) == 2:
                        paragraph = p_pieces[1]
                    else:
                        raise ValueError(
                                'There is an empty paragraph'
                        )
                else:
                    cat = 'POETRY' if '%~%' in paragraph else 'UNDEFINED'
                    section_header = f'::{cat}::'
                    if cat == 'POETRY':
                        paragraph = '\n'.join(paragraph.splitlines())

                paragraph = f'{section_header}\n' + paragraph
            elif MIU_UID_TAG_AND_TEXT_SAME_LINE_PATTERN.match(paragraph):
                paragraph = MIU_UID_TAG_AND_TEXT_SAME_LINE_PATTERN.sub(r'\1\2\n\3', paragraph)
                # Insert a paragraph tag
                heading_and_text = paragraph.splitlines()
                if '%~%' in '\n'.join(heading_and_text[1:]):
                    paragraph = heading_and_text[0] + f'\n\n::POETRY::\n_ء_ ' + '\n'.join(heading_and_text[1:])
                elif len(heading_and_text) > 2:
                    raise ValueError(
                            f'There is a single new line in this paragraph:\n{paragraph}'
                    )
                else:
                    paragraph = heading_and_text[0] + f'\n\n::UNDEFINED::\n_ء_ ' + heading_and_text[1]
            elif MIU_TAG_AND_TEXT_PATTERN.match(paragraph):
                # TODO
                uid = MIU_TAG_AND_TEXT_PATTERN.match(paragraph).group('UID')
                sub_ids = SubIDs(uid)
                # Insert a paragraph tag
                heading_and_text = paragraph.splitlines()
                if '%~%' in '\n'.join(heading_and_text[1:]):
                    paragraph = heading_and_text[0] + f'\n\n::POETRY::\n_ء_ ' + '\n'.join(heading_and_text[1:])
                elif len(heading_and_text) > 2:
                    raise ValueError(
                            f'There is a single new line in this paragraph:\n{paragraph}'
                    )
                else:
                    paragraph = heading_and_text[0] + f'\n\n::UNDEFINED::\n_ء_ ' + heading_and_text[1]

            if ONLY_PAGE_TAG_PATTERN.fullmatch(paragraph):
                # Add page tags to previous paragraph if there is no other information contained in the current
                # paragraph
                page_tag = ONLY_PAGE_TAG_PATTERN.match(paragraph).group('page_tag')
                if PAGE_TAG_IN_BETWEEN_PATTERN.search('\n\n'.join([prev_p, paragraph, next_p])):
                    if text_updated:
                        next_p_text = next_p.split('::UNDEFINED::\n_ء_ ')[1]
                        if text_updated[-1][-1] == ' ':
                            text_updated[-1] += page_tag + ' ' + next_p_text
                        else:
                            text_updated[-1] += ' ' + page_tag + ' ' + next_p_text
                        paragraph = next_p
                        next_p = next(text_iter, None)
                elif text_updated:
                    text_updated[-1] += ' ' + page_tag
            elif not PARAGRAPH_UID_TAG_PATTERN.fullmatch(paragraph):
                # Do not add empty paragraphs to the updated text
                text_updated.append(paragraph)

            prev_p = paragraph
            paragraph = next_p

    # 4. Update sub_ids
    text = '\n\n'.join(text_updated)
    mius = MIU_SPLITTER_PATTERN.split(text)[1:]     # First element is None because the regex matches the text beginning
    uids = [elem for idx, elem in enumerate(mius) if idx % 2 == 0]
    mius = [elem for idx, elem in enumerate(mius) if idx % 2 == 1]

    text_updated = []

    for uid, miu in zip(uids, mius):
        miu = PARAGRAPH_UID_TAG_PATTERN.sub(r'::\g<cat>::', miu)
        sub_ids = SubIDs(uid)
        paragraphs = miu.split('\n\n')

        for paragraph in paragraphs:
            if paragraph.startswith('::'):
                p_pieces = paragraph.splitlines()
                section_header = p_pieces[0]
                if '%~%' in paragraph:
                    paragraph = '\n'.join(p_pieces[1:])
                elif len(p_pieces) > 2:
                    raise ValueError(
                            f'There is a single new line in this paragraph:\n{paragraph}'
                    )
                elif len(p_pieces) == 2:
                    paragraph = p_pieces[1]
                else:
                    raise ValueError(
                            'There is an empty paragraph, check with\n'
                            '::\\n[^هسءگؤقأذپيمجثاڤوضآرتنكزفبعٱشىصلدطغإـئظحةچخ_]'
                    )
                paragraph = f'_ء_={sub_ids.get_id()}= {section_header} ~\n' + paragraph
            elif not MIU_UID_TAG_PATTERN.match(paragraph):
                paragraph = f'_ء_={sub_ids.get_id()}= ::UNDEFINED:: ~\n' + paragraph

            text_updated.append(paragraph)

    # 5. Reassemble text
    text = '\n\n'.join(text_updated)
    return text


def add_ids(infile: str) -> None:
    """Insert UIDs and EIS1600 tags into EIS1600TMP file and thereby convert it to EIS1600 format.


    :param str infile: Path of the file to convert.
    :return None:
    """
    file_path, file_ext = splitext(infile)

    if file_ext == '.EIS1600':
        # EIS1600 file extension
        with open(infile, 'r+', encoding='utf8') as infile_h:
            text = infile_h.read()

            header_and_text = HEADER_END_PATTERN.split(text)
            header = header_and_text[0] + header_and_text[1]
            text = header_and_text[2].lstrip('\n')  # Ignore new lines after #META#Header#End#
            text = pre_clean_text(text)
            text = MISSING_DIRECTIONALITY_TAG_PATTERN.sub('\g<1>_ء_ \g<2>', text)

            check_formatting_before_update_ids(infile, text)
            text = update_ids(text)

            final = header + '\n\n' + text
            if final[-1] != '\n':
                final += '\n'

            infile_h.seek(0)
            infile_h.write(final)
            infile_h.truncate()
    else:
        # EIS1600TMP file extension
        with open(infile, 'r', encoding='utf8') as infile_h:
            text = infile_h.read()

        header_and_text = HEADER_END_PATTERN.split(text)
        header = header_and_text[0] + header_and_text[1]
        text = header_and_text[2].lstrip('\n')  # Ignore new lines after #META#Header#End#
        text = pre_clean_text(text)

        text = insert_ids(text)

        final = header + '\n\n' + text
        if final[-1] != '\n':
            final += '\n'

        outfile = infile.replace('TMP', '')
        with open(outfile, 'w', encoding='utf8') as outfile_h:
            outfile_h.write(final)
