import re

AR_LETTERS_CHARSET = frozenset(
        u'\u0621\u0622\u0623\u0624\u0625\u0626\u0627'
        u'\u0628\u0629\u062a\u062b\u062c\u062d\u062e'
        u'\u062f\u0630\u0631\u0632\u0633\u0634\u0635'
        u'\u0636\u0637\u0638\u0639\u063a\u0640\u0641'
        u'\u0642\u0643\u0644\u0645\u0646\u0647\u0648'
        u'\u0649\u064a\u0671\u067e\u0686\u06a4\u06af'
)
AR_STR = r'[' + u''.join(AR_LETTERS_CHARSET) + ']+'
AR_STR_AND_TAGS = r'[' + u''.join(AR_LETTERS_CHARSET) + 'a-zA-ZÜ0-9]+'
WORD = r'(?:\s' + AR_STR + ')'

# EIS1600 mARkdown
UID = r'_ء_(#)?=(?P<UID>\d{12})= '
UID_PATTERN = re.compile(UID)
MIU_UID = r'_ء_#=(?P<UID>\d{12})= '
MIU_UID_PATTERN = re.compile(MIU_UID)
HEADER_END_PATTERN = re.compile(r'(#META#Header#End#)\n')
MIU_HEADER = r'#MIU#Header#'
MIU_HEADER_PATTERN = re.compile(MIU_HEADER)
HEADING_PATTERN = re.compile(UID + r'(?P<level>[|]+) (?P<heading>.*)\n')
EMPTY_PARAGRAPH_PATTERN = re.compile(UID + r'::UNDEFINED:: ~')
EMPTY_FIRST_PARAGRAPH_PATTERN = re.compile(r'_ء_#=\d{12}=')
PAGE_TAG = r' ?(?P<page_tag>PageV\d{2}P\d{3,})'
PAGE_TAG_PATTERN = re.compile(PAGE_TAG)
ONLY_PAGE_TAG = UID + r'::UNDEFINED:: ~\n' + PAGE_TAG
ONLY_PAGE_TAG_PATTERN = re.compile(ONLY_PAGE_TAG)
PAGE_TAG_IN_BETWEEN_PATTERN = re.compile(
        AR_STR + r' ?' + r'\n\n' + ONLY_PAGE_TAG + r'\n\n' + r'_ء_=\d{12}= ::[A-Z]+:: ~\n' + AR_STR
)

MIU_TAG_PATTERN = re.compile(r'(' + MIU_UID + r'[^\n]+)')
SECTION_TAG = r'_ء_=\d{12}= ::[A-Z]+:: ~'
SECTION_PATTERN = re.compile(SECTION_TAG)
SECTION_SPLITTER_PATTERN = re.compile(r'\n\n(' + SECTION_TAG + ')\n(?:_ء_)?')
TAG_PATTERN = re.compile(r'Ü?(?:[a-zA-Z0-9_%~]+(?:\.[a-zA-Z0-9_%~]+)?)|' + PAGE_TAG)
NOR_DIGIT_NOR_AR_STR = r'[^\d\n' + u''.join(AR_LETTERS_CHARSET) + ']+?'
TAG_AND_TEXT_SAME_LINE_PATTERN = re.compile(
        r'(_ء_#=\d{12}= [$@]+(?:' + NOR_DIGIT_NOR_AR_STR + r')?(?:\d+)?(?:' + NOR_DIGIT_NOR_AR_STR + r')?) ('
                                                                                                               r'(?:\( ?)?' +
        AR_STR + r')'
)
MIU_TAG_AND_TEXT_PATTERN = re.compile(r'(' + MIU_UID + r'[$@]+(?: RAW)?(?: \d+)?)\n((?:\( ?)?' + AR_STR + r')')

# EIS1600 light mARkdown
HEADING_OR_BIO_PATTERN = re.compile(r'# [|$]+')
MIU_LIGHT_OR_EIS1600_PATTERN = re.compile(r'#|_ء_#')

# Fix mARkdown files
SPACES_CROWD_PATTERN = re.compile(r' +')
NEWLINES_CROWD_PATTERN = re.compile(r'\n{3,}')
SPACES_AFTER_NEWLINES_PATTERN = re.compile(r'\n +')
POETRY_PATTERN = re.compile(
        r'# (' + AR_STR_AND_TAGS + '(?: ' + AR_STR_AND_TAGS + ')* %~% ' + AR_STR_AND_TAGS + '(?: ' +
        AR_STR_AND_TAGS +
        r')*) ?'
)
BELONGS_TO_PREV_PARAGRAPH_PATTERN = re.compile(r'\n(.{1,10})\n')
PAGE_TAG_ON_NEWLINE_PATTERN = re.compile(r'\n' + PAGE_TAG)
PAGE_TAG_SPLITTING_PARAGRAPH_PATTERN = re.compile(
        '(' + AR_STR + ' ?)' + r'\n\n' + PAGE_TAG + r'\n\n' + '(' + AR_STR +
        ')'
)
BIO_CHR_TO_NEWLINE_PATTERN = re.compile(
        r'(# [$@]+(?:' + NOR_DIGIT_NOR_AR_STR + r')?(?:\d+)?(?:' + NOR_DIGIT_NOR_AR_STR + r')?) ((?:\( ?)?'
        + AR_STR + r')'
)

# Fixed poetry old file path pattern
FIXED_POETRY_OLD_PATH_PATTERN = re.compile(r'/Users/romanov/_OpenITI/_main_corpus/\w+/data/')
