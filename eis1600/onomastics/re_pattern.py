import re

from eis1600.helper.markdown_patterns import AR_STR

ABU_ABI = re.compile(r' [و]?[اأ]ب[ويى] ')
UMM = re.compile(r' [و]?[اأ]م ')
IBN_IBNA = re.compile(r'[اإ](بن[ةه]?)(?= )')
BN_BNT = re.compile(r' (بن[ت]?) ')
DIN_DAULA = re.compile(r' (الدين|الدول[ةه])')
BANU_BANI = re.compile(r'بن[ويى] ')
YURIFA_K_BI = re.compile(r'([تي]عرف) (ك' + AR_STR + r') (ب)')

DATES = re.compile(r'\[[^\]]+\]')
PARENTHESIS = re.compile(r'\(([^)]+)\)')
QUOTES = re.compile(r'"[^"]+"')
PUNCTUATION = re.compile(r'[.،؟!:؛,;?|]')

SPACES = re.compile(r' {2,}')

LETTERS = r'(?:[أا]لف)|(?:باء)|(?:تاء)|(?:ثاء)|(?:جيم)|(?:حاء)|(?:خاء)|(?:داء)|(?:دال)|(?:ذاء)|(?:ذال)|(?:راء)|(' \
          r'?:زاء)|(?:زاي)|(?:زين)|(?:سين)|(?:شين)|(?:صاد)|(?:ضاد)|(?:طاء)|(?:ظاء)|(?:عين)|(?:غين)|(?:فاء)|(?:قاف)|(' \
          r'?:كاف)|(?:كاء)|(?:لام)|(?:ميم)|(?:نون)|(?:هاء)|(?:واو)|(?:ياء)|(?:همزة)|(?:تاء مربوطة)|(?:تاء ت[أا]نيث)|(' \
          r'?:[أا]لف مقصورة)|(?:تاء ثالثة)|(?:فتحة)|(?:فتح)|(?:مفتوحة)|(?:فتحتين)|(?:مفتوحتين)|(?:ضمة)|(?:ضم)|(' \
          r'?:مضمومة)|(?:ضمتين)|(?:مضمومتين)|(?:كسرة)|(?:كسر)|(?:مكسورة، كسرتين)|(?:مكسورتين)|(?:مدة)|(?:شدة)|(' \
          r'?:مشددة)|(?:تشديد)|(?:سكون)|(?:ساكنة)|(?:دون)|(?:ثم)|(?:بعدها)|(?:بينهما)|(?:أو)|(?:معجمة)|(?:حروف)|(' \
          r'?:آخر الحروف)|(?:مهملة)|(?:مهملتين)|(?:موحدة)|(?:موحدتين)|(?:مثناة)|(?:مثناتين)|(?:[أا]ولى)|(?:ثانية)|(' \
          r'?:ثالثة)|(?:في آخره)|(?:آخره)|(?:[أا]وله)|(?:تحتانية)|(?:تصريف)'

SPELLING = re.compile(r'(?<= )([بو]?(?:ال)?(?:' + LETTERS + r') ){2,}')
