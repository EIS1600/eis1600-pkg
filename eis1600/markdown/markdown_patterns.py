from re import compile

from eis1600.markdown.EntityTags import EntityTags

PUNCTUATION_DICT = {'.': 'PERIOD', ',': 'LATINCOMMA', '،': 'COMMA', ':': 'COLON'}
PUNCTUATION = PUNCTUATION_DICT.keys()

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
WORD = r'(?:(^|\s)' + AR_STR + ')'
NOISE_ELEMENTS = r'(?: [\[\]0-9،.():~|-])*'
AR_CHR_AND_NOISE = r'[' + u''.join(AR_LETTERS_CHARSET) + r'0-9"({\[«-]'

# EIS1600 mARkdown
UID = r'(?P<UID>\d{12}(?:-\d{8})?)'
UID_WITHOUT_CAPTURING_GROUP = r'\d{12}(?:-\d{8})?'
UID_TAG = r'_ء_(#)?=' + UID + '= '
UID_TAG_PATTERN = compile(UID_TAG)
MIU_UID_TAG = r'_ء_#=(?P<UID>\d{12})= '
MIU_UID_TAG_WITHOUT_CAPTURING_GROUP = r'_ء_#=\d{12}= '
MIU_UID_TAG_PATTERN = compile(MIU_UID_TAG)
MIU_SPLITTER_PATTERN = compile(r'(?:^|\n\n)(?=' + MIU_UID_TAG + ')')
PARAGRAPH_CAT = '::(?P<cat>[A-Z_]+)::'
PARAGRAPH_CAT_PATTERN = compile(PARAGRAPH_CAT)
PARAGRAPH_CAT_WITHOUT_CAPTURING_GROUPS = '::[A-Z_]+::'
PARAGRAPH_SIMPLE_SPLITTER_PATTERN = compile('\n\n(' + PARAGRAPH_CAT_WITHOUT_CAPTURING_GROUPS + ')\n')
PARAGRAPH_UID_TAG = r'_ء_=' + UID_WITHOUT_CAPTURING_GROUP + '= ' + PARAGRAPH_CAT + ' ~'
PARAGRAPH_UID_TAG_WITHOUT_CAPTURING_GROUPS = r'_ء_=' + UID_WITHOUT_CAPTURING_GROUP + '= ' + PARAGRAPH_CAT_WITHOUT_CAPTURING_GROUPS + ' ~'
PARAGRAPH_UID_TAG_PATTERN = compile(PARAGRAPH_UID_TAG)
HEADER_END_PATTERN = compile(r'(#META#Header#End#)\n')
MIU_HEADER = r'#MIU#Header#'
MIU_HEADER_PATTERN = compile(MIU_HEADER)
#HEADING_PATTERN = compile(UID_TAG + r'(?P<level>[|]+) (?P<heading>.*)\n')  #FIXME
HEADING_PATTERN = compile(UID_TAG + '(?:LONG )?' + r'(?P<level>[|]+) (?P<heading>.*)\n') #FIXME keep LONG temporarily
PAGE_TAG = r' ?(?P<page_tag>PageV\d{2}P\d{3,})'
PAGE_TAG_PATTERN = compile(PAGE_TAG)
ONLY_PAGE_TAG = PARAGRAPH_UID_TAG + r'\n' + PAGE_TAG
ONLY_PAGE_TAG_PATTERN = compile(ONLY_PAGE_TAG)
PAGE_TAG_IN_BETWEEN_PATTERN = compile(
        AR_STR + r' ?' + r'\n\n' + ONLY_PAGE_TAG + r'\n\n' + PARAGRAPH_UID_TAG_WITHOUT_CAPTURING_GROUPS + ' ~\n' + AR_STR
)
#TEXT_START_PATTERN = compile(MIU_UID_TAG + r'[|]') #FIXME
TEXT_START_PATTERN = compile(MIU_UID_TAG + r'(?:LONG )?[|]')  #FIXME  keep LONG temporarily
SIMPLE_MARKDOWN_TEXT_START_PATTERN = compile(r'# [|]')
PARAGRAPH_TAG_MISSING = compile(r'(\n\n[^_])|(\n\n' + MIU_UID_TAG + r'[^\n]+\n(?:_ء_ )?)' + AR_CHR)
SIMPLE_MARKDOWN = compile(r'\n#')
SPAN_ELEMENTS = compile(r'</?span/?>')
POETRY_ATTACHED_AFTER_PAGE_TAG = compile('Page[VP0-9]+[^\n%]+%')

# MIU_TAG_PATTERN is used to split text - indices depend on the number of capturing groups so be careful when
# changing them
MIU_TAG_PATTERN = compile(r'(' + MIU_UID_TAG + r'(?P<category>[^\n]+))')
CATEGORY_PATTERN = compile(r'[$|@]+(?:[A-Z_]+[|$])?')
PARAGRAPH_SPLITTER_PATTERN = compile(r'\n\n(' + PARAGRAPH_UID_TAG_WITHOUT_CAPTURING_GROUPS + ')\n(?:_ء_)?')
TAG_PATTERN = compile(r'Ü?(?:[a-zA-Z_%~]+(?:\.[a-zA-Z0-9_%~]+)?)|' + PAGE_TAG + '|::|' +
                      '|'.join(PUNCTUATION_DICT.values()))
NOR_DIGIT_NOR_AR_STR = r'[^\d\n' + u''.join(AR_LETTERS_CHARSET) + ']*?'
TAG_AND_TEXT_SAME_LINE = r'([$@]+' + NOR_DIGIT_NOR_AR_STR + r'\d*' + NOR_DIGIT_NOR_AR_STR + r') ?((?:[(\[] ?)?' + AR_STR + r')'
MIU_UID_TAG_AND_TEXT_SAME_LINE_PATTERN = compile(r'(' + MIU_UID_TAG_WITHOUT_CAPTURING_GROUP + ')' + TAG_AND_TEXT_SAME_LINE)
# for chunking the files by first level headings
#FIRST_LEVEL_HEADING_PATTERN = r"^_ء_#=[0-9]+= ?\|(?![PEA|])" #FIXME
FIRST_LEVEL_HEADING_PATTERN = r"^_ء_#=[0-9]+=(?: LONG)? ?\|(?![PEA|])" #FIXME keep LONG temporarily

# Catches MIU tags for BIO, CHR and PARATEXT, EDITOR, etc. (everything in between pipes).
# Does not catch HEADERS!
MIU_TAG_AND_TEXT_PATTERN = compile(r'(' + MIU_UID_TAG + r'(?:[$@]+?|\|[A-Z]+\|)(?: \d+)?)\n((?:\( ?)?' + AR_STR + r')')

# MIU entity tags
entity_tags = '|'.join(EntityTags().get_entity_tags())
ENTITY_TAGS_PATTERN = compile(r'\bÜ?(?P<full_tag>'
                              r'(?P<entity>' + entity_tags + r')(?P<length>\d{1,2})'
                                                             r'(?:(?P<sub_cat>[A-Z]+)|['r'A-Z0-9]+)?)\b')
YEAR_PATTERN = compile(r'Ü?Y(?P<num_tokens>\d{1,2})(?P<cat>[A-Z])(?P<written>\d{4}|None)(?P<i>I)?Y(?P<real>\d{4})?')
AGE_PATTERN = compile(r'Ü?A\d(?P<cat>[A-Z])(?P<written>\d{2,4})(?P<i>I)?A(?P<real>\d{2,4})?')
LUNAR_PATTERN = compile(r'Ü?L\d(?P<cat>X)(?P<written>\d{2})L')
TOPONYM_PATTERN = compile(r'Ü?T(?P<num_tokens>\d{1,2})(?P<cat>[A-Z])')
onom_tags = '|'.join(EntityTags().get_onom_tags())
ONOM_TAGS_PATTERN = compile(r'Ü?(?P<entity>' + onom_tags + r')(?P<length>\d{1,2})')

# EIS1600 light mARkdown
SIMPLE_HEADING_OR_BIO_PATTERN = compile(r'# [|$]+')
MIU_LIGHT_OR_EIS1600_PATTERN = compile(r'#|_ء_#')
PAGE_TAG_ON_NEWLINE_TMP_PATTERN = compile(r'(?<!\n)\n' + PAGE_TAG + r'(?=\n)')
SIMPLE_PARAGRAPH_PATTERN = compile(r'\n' + PARAGRAPH_CAT)

# Fix mARkdown files
SPACES_CROWD_PATTERN = compile(r'  +')
NEWLINES_CROWD_PATTERN = compile(r'\n{3,}')
NEW_LINE_BUT_NO_EMPTY_LINE_PATTERN = compile(r'[^\n]\n(?:(?:# [|$])|(?:' + UID_TAG + '))')
NEW_LINE_INSIDE_PARAGRAPH_NOT_POETRY_PATTERN = compile(r'(?<=\n)[^\n%~]+\n[^\n%]+\n')
TILDA_HICKUPS_PATTERN = compile(r'~\n~')
MISSING_DIRECTIONALITY_TAG_PATTERN = compile(r'(\n+)(' + AR_CHR_AND_NOISE + '|%~%|Page|ms)')
EMPTY_PARAGRAPH = r'::( ~)?\n(?!' + AR_CHR_AND_NOISE + '|%~%|Page|ms|_ء_)'
EMPTY_PARAGRAPH_CHECK_PATTERN = compile(EMPTY_PARAGRAPH)
SPACES_AFTER_NEWLINES_PATTERN = compile(r'\n +')
POETRY_PATTERN = compile(
        r'# (' + AR_STR_AND_TAGS + '(?: ' + AR_STR_AND_TAGS + ')* %~% ' + AR_STR_AND_TAGS + '(?: ' +
        AR_STR_AND_TAGS +
        r')*) ?'
)
BELONGS_TO_PREV_PARAGRAPH_PATTERN = compile(r'\n(.{1,10})\n')
PAGE_TAG_ON_NEWLINE_MARKDOWN_PATTERN = compile(r'\n' + PAGE_TAG)
PAGE_TAG_SPLITTING_PARAGRAPH_PATTERN = compile(
        '(' + AR_STR + ' ?)' + r'\n\n' + PAGE_TAG + r'\n\n' + '(' + AR_STR +
        ')'
)
NORMALIZE_BIO_CHR_MD_PATTERN = compile('# ([$@]((BIO|CHR)_[A-Z]+[$@])| RAW)')
BIO_CHR_TO_NEWLINE_PATTERN = compile(TAG_AND_TEXT_SAME_LINE)

# Fixed poetry old file path pattern
FIXED_POETRY_OLD_PATH_PATTERN = compile(r'/Users/romanov/_OpenITI/_main_corpus/\w+/data/')
