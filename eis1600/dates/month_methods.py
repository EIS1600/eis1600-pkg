from numpy import nan
from openiti.helper.ara import normalize_ara_heavy
from pandas import DataFrame, Series

from eis1600.dates.Month import Month
from eis1600.dates.date_patterns import MONTHS_NOR, MONTH_IN_CONTEXT_PATTERN
from eis1600.processing.preprocessing import get_tokens_and_tags


def tag_months_fulltext(text: str) -> str:
    text_updated = text

    m = MONTH_IN_CONTEXT_PATTERN.search(text_updated)
    while m:
        if m.group('month'):
            month_str = m.group('month')
            if month_str.startswith('ال'):
                month_str = month_str[2:]
            month_str = normalize_ara_heavy(month_str)
            month = MONTHS_NOR.get(month_str)
            if month == -1:
                # This is not a valid month but still needed in the dict so that the regex for dates matches
                m = MONTH_IN_CONTEXT_PATTERN.search(text_updated, m.end('month'))
            else:
                date = Month(month, len(m.group('month').split()))
                pos = m.start('month')
                text_updated = text_updated[:pos] + date.get_tag() + text_updated[pos:]

                # Recognize next date phrase
                m = MONTH_IN_CONTEXT_PATTERN.search(text_updated, m.end('month') + len(date.get_tag()))
        else:
            # Recognize next date phrase
            m = MONTH_IN_CONTEXT_PATTERN.search(text_updated, m.end('month'))

    return text_updated


def month_annotate_miu_text(ner_df: DataFrame, file: str) -> Series:
    """Annotate dates in the headings and in the MIU text, returns a list of tag per token.

    :param DataFrame ner_df: df containing the 'TOKENS' column.
    :param str file: file name.
    :return Series: List of date tags per token, which can be added as additional column to the df.
    """
    df = ner_df.mask(ner_df == '', None)
    tokens = df['TOKENS'].dropna()
    ar_text = ' '.join(tokens)

    try:
        tagged_text = tag_months_fulltext(ar_text)
    except ValueError as e:
        print(e)
        print(f'Check {file}')

        return Series([nan] * len(df))
    else:
        ar_tokens, tags = get_tokens_and_tags(tagged_text)
        df.loc[df['TOKENS'].notna(), 'MONTH_TAGS'] = tags

        return df['MONTH_TAGS']
