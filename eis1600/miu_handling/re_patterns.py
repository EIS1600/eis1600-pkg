import re


UID = r'#\$(?P<UID>\d{12})\$#?\s'
UID_PATTERN = re.compile(UID)
HEADER_END_PATTERN = re.compile(r'(#META#Header#End#)')

MUI_HEADER_PATTERN = re.compile(r'#MUI#Header#')

# Fix mARkdown files
SPACES_PATTERN = re.compile(r' +')
NEWLINES_PATTERN = re.compile(r'\n{3,}')
SPACES_AFTER_NEWLINES_PATTERN = re.compile(r'\n +')
POETRY_PATTERN = re.compile(r'(%~% [^\n]+\n)\n([^\n]+ %~%)')
BELONGS_TO_PREV_PARAGRAPH_PATTERN = re.compile(r'\n(.{1,10})\n')
