import re

from eis1600.markdown.re_pattern import AR_STR

ABU_ABI = re.compile('[اأ]ب[ويى] ')
UMM = re.compile('[و]?[اأ]م ')
IBN_IBNA = re.compile('[اإ](بن[ةه]?) ')
BN_BNT = re.compile(' (بن[ت]?) ')
DIN_DAULA = re.compile(' (الدين|الدول[ةه])')
BANU_BANI = re.compile('بن[ويى] ')
YURIFA_K_BI = re.compile('(يعرف) (ك' + AR_STR + ') (ب)')

DATES = re.compile('\[[^\]]+\]')
PARENTHESIS = re.compile('\(([^)]+)\)')
QUOTES = re.compile('"[^"]+"')
PUNCTUATION = re.compile('[.،؟!:؛,;?|]')

SPACES = re.compile(' {2,}')
