import re

UID = r'#\$(?P<UID>\d{12})\$#?\s'
UID_PATTERN = re.compile(UID)
HEADER_END_PATTERN = re.compile(r'(#META#Header#End#)')

MIU_HEADER_PATTERN = re.compile(r'#MIU#Header#')

# Fix mARkdown files
SPACES_PATTERN = re.compile(r' +')
NEWLINES_PATTERN = re.compile(r'\n{3,}')
SPACES_AFTER_NEWLINES_PATTERN = re.compile(r'\n +')
POETRY_PATTERN = re.compile(r'(%~% [^\n]+\n)\n([^\n]+ %~%)')
BELONGS_TO_PREV_PARAGRAPH_PATTERN = re.compile(r'\n(.{1,10})\n')

PAGE_STR = r'(?:Beg|End|PageStart)?V(?P<volume>\d{2})P(?P<page>\d{3,4})'
PAGE_PATTERN = re.compile(PAGE_STR)

TAG_PATTERN = re.compile(r'@?(?:[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)?)|' + PAGE_STR + '')
