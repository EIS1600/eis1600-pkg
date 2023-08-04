from re import compile

from eis1600.helper.EntityTags import EntityTags

AR_LETTERS_CHARSET = frozenset(
        u'\u0621\u0622\u0623\u0624\u0625\u0626\u0627'
        u'\u0628\u0629\u062a\u062b\u062c\u062d\u062e'
        u'\u062f\u0630\u0631\u0632\u0633\u0634\u0635'
        u'\u0636\u0637\u0638\u0639\u063a\u0640\u0641'
        u'\u0642\u0643\u0644\u0645\u0646\u0647\u0648'
        u'\u0649\u064a\u0671\u067e\u0686\u06a4\u06af'
)
AR_CHR = r'[' + u''.join(AR_LETTERS_CHARSET) + ']'
AR_STR = AR_CHR + '+'
AR_STR_AND_TAGS = r'[' + u''.join(AR_LETTERS_CHARSET) + 'a-zA-ZÜ0-9]+'
WORD = r'(?:\s' + AR_STR + ')'

# EIS1600 mARkdown
UID = r'_ء_(#)?=(?P<UID>\d{12})= '
UID_PATTERN = compile(UID)
MIU_UID = r'_ء_#=(?P<UID>\d{12})= '
MIU_UID_PATTERN = compile(MIU_UID)
HEADER_END_PATTERN = compile(r'(#META#Header#End#)\n')
MIU_HEADER = r'#MIU#Header#'
MIU_HEADER_PATTERN = compile(MIU_HEADER)
HEADING_PATTERN = compile(UID + r'(?P<level>[|]+) (?P<heading>.*)\n')
EMPTY_PARAGRAPH_PATTERN = compile(UID + r'::UNDEFINED:: ~')
EMPTY_FIRST_PARAGRAPH_PATTERN = compile(r'_ء_#=\d{12}=')
PAGE_TAG = r' ?(?P<page_tag>PageV\d{2}P\d{3,})'
PAGE_TAG_PATTERN = compile(PAGE_TAG)
ONLY_PAGE_TAG = UID + r'::UNDEFINED:: ~\n' + PAGE_TAG
ONLY_PAGE_TAG_PATTERN = compile(ONLY_PAGE_TAG)
PAGE_TAG_IN_BETWEEN_PATTERN = compile(
        AR_STR + r' ?' + r'\n\n' + ONLY_PAGE_TAG + r'\n\n' + r'_ء_=\d{12}= ::[A-Z]+:: ~\n' + AR_STR
)
PARAGRAPH_TAG_MISSING = compile('\n\n[^_]')
SIMPLE_MARKDOWN = compile('\n#')

# MIU_TAG_PATTERN is used to split text - indices depend on the number of capturing groups so be careful when
# changing them
MIU_TAG_PATTERN = compile(r'(' + MIU_UID + r'(?P<category>[^\n]+))')
CATEGORY_PATTERN = compile(r'[$|@]+(?:[A-Z]+[|])?')
SECTION_TAG = r'_ء_=\d{12}= ::[A-Z]+:: ~'
SECTION_PATTERN = compile(SECTION_TAG)
SECTION_SPLITTER_PATTERN = compile(r'\n\n(' + SECTION_TAG + ')\n(?:_ء_)?')
TAG_PATTERN = compile(r'Ü?(?:[a-zA-Z0-9_%~]+(?:\.[a-zA-Z0-9_%~]+)?)|' + PAGE_TAG + '|(?:::)')
NOR_DIGIT_NOR_AR_STR = r'[^\d\n' + u''.join(AR_LETTERS_CHARSET) + ']+?'
TAG_AND_TEXT_SAME_LINE = r'([$@]+' + NOR_DIGIT_NOR_AR_STR + r'\d*' + NOR_DIGIT_NOR_AR_STR + r') ?((?:[(\[] ?)?' + AR_STR + r')'
UID_TAG_AND_TEXT_SAME_LINE_PATTERN = compile(
        r'(_ء_#=\d{12}= )' + TAG_AND_TEXT_SAME_LINE)
MIU_TAG_AND_TEXT_PATTERN = compile(r'(' + MIU_UID + r'[$@]+?(?: \d+)?)\n((?:\( ?)?' + AR_STR + r')')

# MIU entity tags
entity_tags = '|'.join(EntityTags.instance().get_entity_tags())
ENTITY_TAGS_PATTERN = compile(r'\bÜ?(?P<full_tag>'
                              r'(?P<entity>' + entity_tags + r')(?P<length>\d{1,2})'
                                                             r'(?:(?P<sub_cat>[A-Z]+)|['r'A-Z0-9]+)?)\b')
YEAR_PATTERN = compile(r'Ü?Y(?P<num_tokens>\d{1,2})(?P<cat>[A-Z])(?P<written>\d{4}|None)(?P<i>I)?Y(?P<real>\d{4})?')
AGE_PATTERN = compile(r'Ü?A\d(?P<cat>[A-Z])(?P<written>\d{2,3})(?P<i>I)?A(?P<real>\d{2,3})?')
onom_tags = '|'.join(EntityTags.instance().get_onom_tags())
ONOM_TAGS_PATTERN = compile(r'Ü?(?P<entity>' + onom_tags + r')(?P<length>\d{1,2})')

# EIS1600 light mARkdown
HEADING_OR_BIO_PATTERN = compile(r'# [|$]+')
MIU_LIGHT_OR_EIS1600_PATTERN = compile(r'#|_ء_#')

# Fix mARkdown files
SPACES_CROWD_PATTERN = compile(r' +')
NEWLINES_CROWD_PATTERN = compile(r'\n{3,}')
SPACES_AFTER_NEWLINES_PATTERN = compile(r'\n +')
POETRY_PATTERN = compile(
        r'# (' + AR_STR_AND_TAGS + '(?: ' + AR_STR_AND_TAGS + ')* %~% ' + AR_STR_AND_TAGS + '(?: ' +
        AR_STR_AND_TAGS +
        r')*) ?'
)
BELONGS_TO_PREV_PARAGRAPH_PATTERN = compile(r'\n(.{1,10})\n')
PAGE_TAG_ON_NEWLINE_PATTERN = compile(r'\n' + PAGE_TAG)
PAGE_TAG_SPLITTING_PARAGRAPH_PATTERN = compile(
        '(' + AR_STR + ' ?)' + r'\n\n' + PAGE_TAG + r'\n\n' + '(' + AR_STR +
        ')'
)
NORMALIZE_BIO_CHR_MD_PATTERN = compile('# ([$@]((BIO|CHR)_[A-Z]+[$@])| RAW)')
BIO_CHR_TO_NEWLINE_PATTERN = compile(TAG_AND_TEXT_SAME_LINE)

# Fixed poetry old file path pattern
FIXED_POETRY_OLD_PATH_PATTERN = compile(r'/Users/romanov/_OpenITI/_main_corpus/\w+/data/')
