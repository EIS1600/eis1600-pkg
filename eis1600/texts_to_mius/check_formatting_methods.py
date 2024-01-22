from eis1600.markdown.markdown_patterns import NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN, \
    NEW_LINE_INSIDE_PARAGRAPH_NOT_POETRY_PATTERN, PARAGRAPH_TAG_MISSING, EMPTY_PARAGRAPH_CHECK_PATTERN, \
    SIMPLE_MARKDOWN, MISSING_DIRECTIONALITY_TAG_PATTERN, SPAN_ELEMENTS, TEXT_START_PATTERN, TILDA_HICKUPS_PATTERN
from eis1600.markdown.markdown_patterns import SIMPLE_MARKDOWN_TEXT_START_PATTERN


def check_file_for_mal_formatting(infile: str, content: str):
    if not TEXT_START_PATTERN.match(content) \
            or PARAGRAPH_TAG_MISSING.search(content) \
            or SIMPLE_MARKDOWN.search(content) \
            or NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN.search(content) \
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
