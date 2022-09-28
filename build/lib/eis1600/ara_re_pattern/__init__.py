AR_LETTERS_CHARSET = frozenset(u'\u0621\u0622\u0623\u0624\u0625\u0626\u0627'
                               u'\u0628\u0629\u062a\u062b\u062c\u062d\u062e'
                               u'\u062f\u0630\u0631\u0632\u0633\u0634\u0635'
                               u'\u0636\u0637\u0638\u0639\u063a\u0640\u0641'
                               u'\u0642\u0643\u0644\u0645\u0646\u0647\u0648'
                               u'\u0649\u064a\u0671\u067e\u0686\u06a4\u06af')
AR_STR = r'[' + u''.join(AR_LETTERS_CHARSET) + ']+'
WORD = r'(?:\s' + AR_STR + ')'
