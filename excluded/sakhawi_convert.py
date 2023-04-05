import re
from eis1600.helper.markdown_patterns import AR_STR, AR_STR_AND_TAGS, PAGE_TAG

UID_PATTERN = re.compile(r'###\$\d{12,13}\$')
ORPHANED_PAGE_TAG_PATTERN = re.compile(r'\n ?(' + PAGE_TAG + r') ?\n(?!\n)')
ORPHANED_PAGE_TAG_2_PATTERN = re.compile(r'\n ?(' + PAGE_TAG + r') ?\n\n')
ORPHANED_PAGE_TAG_IN_POETRY_PATTERN = re.compile(r'(?<=%~%)\n ?(' + PAGE_TAG + r') ?\n+(?=%~%)')
LINE_PATTERN = re.compile(r'(' + AR_STR_AND_TAGS + r'(?: ?[.:،]?) ?)\n( ?' + AR_STR_AND_TAGS + r')')
BIO_HEADING_PATTERN = re.compile(r'(# [$]+( \d+)?) ?')
ID_MISSING_PATTERN = re.compile(r'(?<=\n)★ID_Missing★ ?(?!\n)')
ID_MISSING_W_D_PATTERN = re.compile(r'(?<=\n)ID_missing★ (\d+)★ ?(?!\n)')
ID_MISSING_W_D_2_PATTERN = re.compile(r'(?<=\n)★(\d+)ID_missing★ ?(?!\n)')
ID_MISSING_W_D_3_PATTERN = re.compile(r'(?<=\n)(\d+)★ID_missing★ ?(?!\n)')
SPACE_CROWD_PATTERN = re.compile(r'  +')
FIX_POETRY_PATTERN = re.compile(r'(%~%) (' + AR_STR + r' ?(?:: ?)?\n%~%)')
FIX_POETRY_MD_PATTERN = re.compile(r'%~% ([^%\n]+%~%[^%\n]+) %~%')
FIX_POETRY_MD_2_PATTERN = re.compile(r'(%~% [^%\n]+) %~%')
FIX_POETRY_QALA_PATTERN = re.compile(r'(\n\n[وف](?:قال|قوله|منه) ?:)(?: ?' + PAGE_TAG + r')? ?\n\n')


if __name__ == "__main__":
    path = '../../OpenITI_EIS1600_Texts/data/0902Sakhawi/0902Sakhawi.DawLamic/0902Sakhawi.DawLamic.ITO20230111-ara1'
    with open(path + '.mARkdown', 'r', encoding='utf-8') as fh:
        content = fh.read()

    with open(path + '.EIS1600TMP', 'w', encoding='utf-8') as fh:
        content_updated = UID_PATTERN.sub('', content)
        content_updated = ORPHANED_PAGE_TAG_PATTERN.sub(r' \g<1> ', content_updated)
        content_updated = ORPHANED_PAGE_TAG_2_PATTERN.sub(r' \g<1>\n\n', content_updated)
        content_updated = ORPHANED_PAGE_TAG_IN_POETRY_PATTERN.sub(r' \g<1>\n', content_updated)
        content_updated, n = BIO_HEADING_PATTERN.subn(r'\g<1>\n', content_updated)
        print(f'BIO_HEADING to new line: {n}')
        content_updated, n = ID_MISSING_PATTERN.subn(r'# $\n', content_updated)
        print(f'ID_MISSING to new line: {n}')
        content_updated, n = ID_MISSING_W_D_PATTERN.subn(r'# $ \g<1>\n', content_updated)
        print(f'ID_MISSING with ID to new line: {n}')
        content_updated, n = ID_MISSING_W_D_2_PATTERN.subn(r'# $ \g<1>\n', content_updated)
        print(f'ID_MISSING with ID 2 to new line: {n}')
        content_updated, n = ID_MISSING_W_D_3_PATTERN.subn(r'# $ \g<1>\n', content_updated)
        print(f'ID_MISSING with ID 3 to new line: {n}')
        content_updated = LINE_PATTERN.sub(r'\g<1> \g<2>', content_updated)
        content_updated = SPACE_CROWD_PATTERN.sub(' ', content_updated)
        content_updated = FIX_POETRY_PATTERN.sub(r'\g<1>\n\n\g<2>', content_updated)
        content_updated = FIX_POETRY_MD_PATTERN.sub(r'\g<1>', content_updated)
        content_updated = FIX_POETRY_MD_2_PATTERN.sub(r'\g<1>', content_updated)
        content_updated = FIX_POETRY_QALA_PATTERN.sub(r'\g<1>\n', content_updated)

        fh.write(content_updated)

