from re import MULTILINE

import re

AR_LETTERS_CHARSET = frozenset(u'\u0621\u0622\u0623\u0624\u0625\u0626\u0627'
                               u'\u0628\u0629\u062a\u062b\u062c\u062d\u062e'
                               u'\u062f\u0630\u0631\u0632\u0633\u0634\u0635'
                               u'\u0636\u0637\u0638\u0639\u063a\u0640\u0641'
                               u'\u0642\u0643\u0644\u0645\u0646\u0647\u0648'
                               u'\u0649\u064a\u0671\u067e\u0686\u06a4\u06af')
AR_STR = r'[' + u''.join(AR_LETTERS_CHARSET) + ']+'
WORD = r'(?:\s' + AR_STR + ')'

# EIS1600 mARkdown
UID = r'_ء_#?=(?P<UID>\d{12})= '
UID_PATTERN = re.compile(UID)
MIU_UID_PATTERN = re.compile(r'_ء_#=(?P<UID>\d{12})= ')
HEADER_END_SPLIT_PATTERN = re.compile(r'(#META#Header#End#)\n\n')
HEADER_END_PATTERN = re.compile(r'(#META#Header#End#)\n')
MIU_HEADER = r'#MIU#Header#'
MIU_HEADER_PATTERN = re.compile(MIU_HEADER)
# PARAGRAPH_PATTERN = re.compile(r'::[A-Z]+:: ~')
HEADING_PATTERN = re.compile(UID + r'(?P<level>[|]+) (?P<heading>.*)\n')

# EIS1600 light mARkdown
HEADING_OR_BIO_PATTERN = re.compile(r'# [|$]+')
MIU_LIGHT_OR_EIS1600_PATTERN = re.compile(r'#|_ء_#')

# Fix mARkdown files
SPACES_PATTERN = re.compile(r' +')
NEWLINES_PATTERN = re.compile(r'\n{3,}')
SPACES_AFTER_NEWLINES_PATTERN = re.compile(r'\n +')
POETRY_PATTERN = re.compile(r'# (' + AR_STR + '(?: ' + AR_STR + ')* %~% ' + AR_STR + '(?: ' + AR_STR + r')*)')
POETRY_TO_PARAGRAPH = re.compile(r'(\n[^%\n]+)\n(' + AR_STR + '(?: ' + AR_STR + r')* %~%)', MULTILINE)
BELONGS_TO_PREV_PARAGRAPH_PATTERN = re.compile(r'\n(.{1,10})\n')
PAGE_TAG_ON_NEWLINE_PATTERN = re.compile(r'\n(PageV\d{2}P\d{3}\n)')
BIO_CHR_TO_NEWLINE_PATTERN = re.compile(r'(\n[^' + u''.join(AR_LETTERS_CHARSET) + r'\n]+[$@](?: RAW)?(?: \d+)?)(?: '
                                                                                  r'-)? (('
                                                                                r'?:\( ?)?' + AR_STR + r')')

# Fixed poetry old file path pattern
FIXED_POETRY_OLD_PATH_PATTERN = re.compile(r'/Users/romanov/_OpenITI/_main_corpus/\w+/data/')
