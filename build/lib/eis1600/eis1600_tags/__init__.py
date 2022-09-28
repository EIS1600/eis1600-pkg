import re


UID = r'_ء_#\$(?P<UID>\d{12})\$\s'
UID_PATTERN = re.compile(UID)
HEADER_END_PATTERN = re.compile(r'#META#Header#End#')

MUI_HEADER_PATTERN = re.compile(r'#MUI#Header#')
MUI_NEWLINE_PATTERN = re.compile(r'\n{3,}')

PAGE_STR = r'(?:Beg|End|PageStart)?V(?P<volume>\d{2})P(?P<page>\d{3,4})'
PAGE_PATTERN = re.compile(PAGE_STR)


TAG_PATTERN = re.compile(r'@?(?:[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)?)|' + PAGE_STR + '')
