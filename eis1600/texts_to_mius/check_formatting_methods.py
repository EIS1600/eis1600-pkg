
from os import remove
from os.path import splitext, exists
from itertools import zip_longest
from eis1600.markdown.markdown_patterns import MIU_UID_TAG_AND_TEXT_SAME_LINE_PATTERN, \
    NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN, NEW_LINE_INSIDE_PARAGRAPH_NOT_POETRY_PATTERN, PARAGRAPH_TAG_MISSING, \
    EMPTY_PARAGRAPH_CHECK_PATTERN, SIMPLE_MARKDOWN, MISSING_DIRECTIONALITY_TAG_PATTERN, SPAN_ELEMENTS, \
    TEXT_START_PATTERN, TILDA_HICKUPS_PATTERN, HEADER_END_PATTERN
from eis1600.markdown.markdown_patterns import SIMPLE_MARKDOWN_TEXT_START_PATTERN
from eis1600.repositories.repo import get_part_filepath


def check_file_for_mal_formatting(infile: str, content: str):
    if not TEXT_START_PATTERN.match(content) \
            or PARAGRAPH_TAG_MISSING.search(content) \
            or SIMPLE_MARKDOWN.search(content) \
            or NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN.search(content) \
            or MIU_UID_TAG_AND_TEXT_SAME_LINE_PATTERN.search(content) \
            or TILDA_HICKUPS_PATTERN.search(content) \
            or NEW_LINE_INSIDE_PARAGRAPH_NOT_POETRY_PATTERN.search(content) \
            or EMPTY_PARAGRAPH_CHECK_PATTERN.search(content) \
            or SPAN_ELEMENTS.search(content) \
            or MISSING_DIRECTIONALITY_TAG_PATTERN.search(content):
        # Poetry is still to messed up, do not bother with it for now
        # or POETRY_ATTACHED_AFTER_PAGE_TAG.search(content):
        error = ''
        if not TEXT_START_PATTERN.match(content):
            error += '\n * Text does not start with a MIU tag, check if the preface is tagged as PARATEXT.'
        if PARAGRAPH_TAG_MISSING.search(content):
            error += '\n * There are missing paragraph tags.'
        if SIMPLE_MARKDOWN.search(content):
            error += '\n * There is simple mARkdown left.'
        if NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN.search(content):
            error += '\n * There are elements missing the double newline (somewhere the emtpy line is missing).'
        if MIU_UID_TAG_AND_TEXT_SAME_LINE_PATTERN.search(content):
            error += '\n * There is text on the same line as the start of a biography, fix it by running ' \
                     f'`ids_insert_or_update` on {infile}'
        if TILDA_HICKUPS_PATTERN.search(content):
            error += '\n * There is this pattern with tildes: `~\\n~`.'
        if NEW_LINE_INSIDE_PARAGRAPH_NOT_POETRY_PATTERN.search(content):
            error += '\n * There is a single newline inside a paragraph (somewhere the emtpy line is missing).'
        if EMPTY_PARAGRAPH_CHECK_PATTERN.search(content):
            error += '\n * There are empty paragraphs in the text.'
        if SPAN_ELEMENTS.search(content):
            error += '\n * There are span elements in the text.'
        if MISSING_DIRECTIONALITY_TAG_PATTERN.search(content):
            error += '\n * There are missing direction tags at the beginning of paragraphs, fix it by running ' \
                     f'`ids_insert_or_update` on {infile}'
        # if POETRY_ATTACHED_AFTER_PAGE_TAG.search(content):
        #     error += '\n * There is poetry attached to a PageTag (there should be a linebreak instead).'

        raise ValueError(
                f'Correct the following errors\n'
                f'open -a kate {infile}\n'
                f'kate {infile}\n'
                f'{error}\n\n'
                f'And now run\n'
                f'ids_insert_or_update {infile}\n'
                f'Check if everything is working with\n'
                f'check_formatting {infile}\n'
        )


def check_formatting(infile: str):
    with open(infile, 'r', encoding='utf8') as text:
        header_text = text.read().split('#META#Header#End#\n\n')

        try:
            check_file_for_mal_formatting(infile, header_text[1])
        except ValueError:
            raise


def check_formatting_before_update_ids(infile: str, content: str):
    if not TEXT_START_PATTERN.match(content) and not SIMPLE_MARKDOWN_TEXT_START_PATTERN.match(content) \
            or NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN.search(content) \
            or TILDA_HICKUPS_PATTERN.search(content) \
            or NEW_LINE_INSIDE_PARAGRAPH_NOT_POETRY_PATTERN.search(content) \
            or EMPTY_PARAGRAPH_CHECK_PATTERN.search(content) \
            or SPAN_ELEMENTS.search(content):

        error = ''
        if not TEXT_START_PATTERN.match(content) and not SIMPLE_MARKDOWN_TEXT_START_PATTERN.match(content):
            error += '\n * Text does not start with Header or PARATEXT, check if the preface is tagged.'
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

        raise ValueError(
                f'Correct the following errors\n'
                f'open -a kate {infile}\n'
                f'kate {infile}\n'
                f'{error}\n\n'
                f'And now run\n'
                f'ids_insert_or_update {infile}\n'
                f'Check if everything is working with\n'
                f'check_formatting {infile}\n'
        )


def check_file_split(infile: str, debug: bool = False):

    with open(infile) as infp:
        original_content = infp.read()
    file_base, file_ext = splitext(infile)

    i = 1
    chunks = []
    header = ""
    part_paths = []  # in case of error they will be removed

    while True:

        if not exists(part_fpath := get_part_filepath(file_base, i, file_ext)):
            break

        part_paths.append(part_fpath)

        with open(part_fpath) as infp:
            part_content = infp.read()

        header_and_text = HEADER_END_PATTERN.split(part_content)
        header = header_and_text[0] + header_and_text[1]
        text = header_and_text[2].lstrip('\n')

        chunks.append(text)
        i += 1

    if original_content == (complete := header + '\n\n' + "\n".join(chunks)):
        #if debug:
        #    print(f"File {infile} has been splitted correctly or has only one part")
        return

    if debug:
        max_lines_print = 50
        print(f"\nError splitting file {infile}. These lines differ (original vs reconstructed):\n")
        for ori, part in zip_longest(original_content.splitlines(True), complete.splitlines(True)):
            if ori != part:
                print(f"{repr(ori):>100}  ≠  {repr(part):>100}")
                max_lines_print -= 1
            if not max_lines_print:
                print("...")
                break

    for fpath in part_paths:
        remove(fpath)

    raise f"splitting of file {infile} failed!"

