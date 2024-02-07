from numpy import nan

from pandas import DataFrame, Series
from typing import Match, Optional

from openiti.helper.ara import normalize_ara_heavy

from eis1600.dates.Date import Date
from eis1600.dates.date_patterns import DATE_CATEGORIES_NOR, DATE_CATEGORY_PATTERN, DATE_PATTERN, MONTHS_NOR, \
    ONES_NOR, TEN_NOR, HUNDRED_NOR, THOUSAND_NOR, ONES_HINDI, SANA_PATTERN
from eis1600.processing.preprocessing import get_tokens_and_tags
from eis1600.yml.YAMLHandler import YAMLHandler


def parse_year(m: Match[str]) -> (int, int):
    """

    :param m:
    :return:
    :raise ValueError:
    """
    year = 0
    year_digits = 0
    length = len(m.group('sana').split())  # (?P<sana>سنة|عام|في حدود)
    if m.group('ones'):
        year += ONES_NOR.get(normalize_ara_heavy(m.group('ones')))
        length += 1
    if m.group('ten'):
        year += TEN_NOR.get(normalize_ara_heavy(m.group('ten')))
        length += 1
    if m.group('hundred'):
        year += HUNDRED_NOR.get(normalize_ara_heavy(m.group('hundred')))
        length += len(m.group('hundred').split())
    if m.group('thousand'):
        year += THOUSAND_NOR.get(normalize_ara_heavy(m.group('thousand')))
        length += 1
    if m.group('digits'):
        digits = m.group('digits')
        if digits.isdigit():
            year_digits = int(digits)
        else:
            multiplier = [1, 10, 100, 1000]
            c = len(digits)
            while c:
                year_digits += ONES_HINDI.get(digits[c - 1]) * multiplier[c - 1]

        length += len(m.group('digits_str').strip().split())

        if year == 0:
            year = year_digits
        elif year != year_digits:
            raise ValueError(
                    f"Date recognition: parsed value and given value are at odds. Check {m.group(0)}\n"
                    f"given: {year_digits}\n"
                    f"parsed: {year}"
            )

    return year, length


def get_dates_headings(yml_handler: YAMLHandler) -> None:
    """Checks the headings for date statements and if a such a statement is found, it is converted into a tag and
    added to the yml header.

    :param YAMLHandler yml_handler: arabic text.
    """
    headings = yml_handler.headings
    for key, val in headings:
        if DATE_PATTERN.search(val):
            m = DATE_PATTERN.search(val)
            year, length = parse_year(m)
            yml_handler.add_date_headings(year)


def tag_dates_fulltext(text: str) -> str:
    """Inserts EIS1600 date tags in the arabic text and returns the text with the tags.

    This is a rule-based model to recognize, classify and parse date phrases in Arabic texts.
    The text is returned with all recognized dates annotated with EIS1600 tags for dates.
    :param str text: arabic text.
    :return str: arabic text with EIS1600 tags for the recognized and classified dates.
    """
    text_updated = text
    # Regex that recognizes date phrases (and unfortunately age phrases as well)
    m = DATE_PATTERN.search(text_updated)
    while m:
        # While date phrases are recognized in the text
        if m.group('year') and not SANA_PATTERN.fullmatch(m.group('year')):
            # Check if phrase is an actual date. Date phrases give the years after the word sana. In
            # contrast, age phrases give the years before the word sana.
            year = 0
            length = 1
            month = None
            day = 0
            weekday = None
            # Length is one because sana is definitely recognized
            try:
                year, length = parse_year(m)
            except ValueError as e:
                raise e
            else:
                # Date classification
                if DATE_CATEGORY_PATTERN.search(m.group('context')):
                    last = DATE_CATEGORY_PATTERN.findall(m.group('context'))[-1]
                    date_category = DATE_CATEGORIES_NOR.get(normalize_ara_heavy(last))
                else:
                    date_category = 'X'

                # Parsing of other information from the date phrase as day of the week, day of the month, month
                # Currently not of interest
                # if m.group('weekday'):
                #     weekday = WEEKDAYS_NOR.get(normalize_ara_heavy(m.group('weekday')))
                # if m.group('day_ones'):
                #     day += DAY_ONES_NOR.get(normalize_ara_heavy(m.group('day_ones')))
                # if m.group('day_ten'):
                #     day += DAY_TEN_NOR.get(normalize_ara_heavy(m.group('day_ten')))
                # if m.group('month'):
                #     month_str = normalize_ara_heavy(m.group('month'))
                #     month = MONTHS_NOR.get(month_str)
                # else:
                #     mm = MONTH_PATTERN.search(m[0])
                #     if mm:
                #         month_str = mm[0]
                #         month = MONTHS.get(month_str)

                # if day == 0:
                #     day = None
                if year == 0:
                    year = None

                # Get extracted information bundled as date object and insert EIS600 tag for date into the text
                date = Date(year, length, date_category)
                pos = m.start('sana')
                text_updated = text_updated[:pos] + date.get_tag() + text_updated[pos:]

                # Recognize next date phrase
                m = DATE_PATTERN.search(text_updated, m.end('sana') + len(date.get_tag()))
        else:
            # Recognize next date phrase
            m = DATE_PATTERN.search(text_updated, m.end('sana'))

    return text_updated


def date_annotate_miu_text(ner_df: DataFrame, file: str, yml: Optional[YAMLHandler] = None) -> Series:
    """Annotate dates in the headings and in the MIU text, returns a list of tag per token.

    :param DataFrame ner_df: df containing the 'TOKENS' column.
    :param str file: file name.
    :param YAMLHandler yml: yml_header to collect date tags in.
    :return Series: List of date tags per token, which can be added as additional column to the df.
    """
    if yml:
        get_dates_headings(yml)

    df = ner_df.mask(ner_df == '', None)
    tokens = df['TOKENS'].dropna()
    ar_text = ' '.join(tokens)

    try:
        tagged_text = tag_dates_fulltext(ar_text)
    except ValueError as e:
        print(e)
        print(f'Check {file}')

        return Series([nan] * len(df))
    else:
        ar_tokens, tags = get_tokens_and_tags(tagged_text)
        df.loc[df['TOKENS'].notna(), 'DATE_TAGS'] = tags

        return df['DATE_TAGS']
