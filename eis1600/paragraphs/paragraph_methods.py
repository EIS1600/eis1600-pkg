from typing import List, Literal, Optional, Tuple

from pandas import isna, DataFrame

from eis1600.markdown.markdown_patterns import MIU_TAG_PATTERN, PARAGRAPH_UID_TAG_PATTERN
from eis1600.models.BiosPunctuationModel import BiosPunctuationModel
from eis1600.models.EventsPunctuationModel import EventsPunctuationModel
from eis1600.models.PoetryDetectionModel import PoetryDetectionModel
from eis1600.processing.preprocessing import get_yml_and_miu_df, tokenize_miu_text
from eis1600.processing.postprocessing import reconstruct_miu_text_with_tags
from eis1600.repositories.repo import TEXT_REPO

PUNCTUATION = ['.', ',', '،', ':']


def test_for_poetry(tokens: List[str], debug: Optional[bool] = False):
    return PoetryDetectionModel().predict_is_poetry(tokens, debug)


def remove_punctuation(df: DataFrame) -> DataFrame:
    sections, tokens, tags = [], [], []
    for section, token, tag in df.itertuples(index=False):
        if token in PUNCTUATION:
            if not isna(section):
                raise ValueError('First token in this section is punctuation:\n'
                                 f'{section}\n'
                                 'This is not allowed during the re-splitting routine.\n')
            elif not isna(tag):
                # Extend TAGS_LIST of prev token with tags from the punctuation token
                if not isna(tags[-1]):
                    tags[-1].extend(tag)
                else:
                    tags[-1] = tag

        else:
            sections.append(section)
            tokens.append(token)
            tags.append(tag)

    return DataFrame(zip(sections, tokens, tags), columns=['SECTIONS', 'TOKENS', 'TAGS_LISTS'])


def get_old_paragraphs(df: DataFrame) -> List[Tuple[str, List[str]]]:
    paragraphs = []

    tokens = []
    curr_section_type = None
    for section, token, tags in df.itertuples(index=False):
        if isna(section):
            if not isna(token):
                if tags:
                    if 'NEWLINE' in tags:
                        tokens.append('\n')
                    if 'HEMISTICH' in tags:
                        tokens.append('%~%')
                tokens.append(token)
        elif PARAGRAPH_UID_TAG_PATTERN.match(section):
            paragraphs.append((curr_section_type, tokens))
            curr_section_type = PARAGRAPH_UID_TAG_PATTERN.match(section).group('cat')
            tokens = [token]

    paragraphs.append((curr_section_type, tokens))
    return paragraphs[1:]  # First element is (None, '') due to the MIU header


def remove_original_paragraphs(old_paragraphs: List[Tuple[str, List[str]]]) -> List[Tuple[str, List[str]]]:
    mergeable_paragraphs = []
    unsplitted = []
    for cat, tokens in old_paragraphs:
        if cat == 'POETRY' or '%~%' in tokens or (len(tokens) < 60 and test_for_poetry(tokens)):
            unsplitted.append(('UNDEFINED', mergeable_paragraphs))
            mergeable_paragraphs = []
            if '%~%' not in tokens:
                tokens = ['%~%'] + tokens
            unsplitted.append(('POETRY', tokens))
        else:
            mergeable_paragraphs.extend(tokens)
    if mergeable_paragraphs:
        unsplitted.append(('UNDEFINED', mergeable_paragraphs))

    return unsplitted


def split_by_model(tokens: List[str], miu_cat: Literal['B', 'C']) -> List[Tuple[str, str]]:
    if miu_cat == 'B':
        # TODO insert Bio Punctuation model after training
        # punctuation_predictions = BiosPunctuationModel().predict_sentence(tokens)
        punctuation_predictions = [None] * len(tokens)
    else:
        punctuation_predictions = EventsPunctuationModel().predict_sentence(tokens)
    text_with_punctuation = ''
    for t, p in zip(tokens, punctuation_predictions):
        text_with_punctuation += t + ' '
        if p:
            text_with_punctuation += p + ' '
    paragraphs = text_with_punctuation.split('. ')

    return [('UNDEFINED', paragraph + '.') for paragraph in paragraphs if paragraph]


def redefine_paragraphs(uid: str, miu_as_text: str) -> None:
    yml_handler, df_original = get_yml_and_miu_df(miu_as_text)
    miu_header = df_original['SECTIONS'].iloc[0]
    if MIU_TAG_PATTERN.match(miu_header).group('category').startswith('$'):
        miu_cat = 'B'   # MIU is a biography
    else:
        miu_cat = 'C'     # MIU is not a biography and therefore we assume it is events

    print(miu_header)

    # DEBUG
    df_original.to_csv(TEXT_REPO + f'Footnotes_noise_example.{uid}_original.csv')

    df_new = remove_punctuation(df_original)
    old_paragraphs = get_old_paragraphs(df_new)
    unsplitted_text = remove_original_paragraphs(old_paragraphs)

    new_paragraphs = []
    for cat, unsplitted in unsplitted_text:
        if cat == 'UNDEFINED':
            new_paragraphs.extend(split_by_model(unsplitted, miu_cat))
        else:
            new_paragraphs.append((cat, unsplitted))

    # And now puzzle everything together
    text_with_new_paragraphs = miu_header + '\n\n'
    for cat, paragraph in new_paragraphs:
        text_with_new_paragraphs += f'::{cat}::\n{paragraph}\n\n'

    text_with_new_paragraphs = text_with_new_paragraphs[:-2]    # delete new-lines from the end
    # TODO How to aline with TAGS_LISTS?
    zipped = tokenize_miu_text(text_with_new_paragraphs, simple_mARkdown=True)
    sections, tokens, punctuation = [], [], []
    for section, token, _ in zipped:
        if token in PUNCTUATION:
            punctuation[-1] = token
        else:
            sections.append(section)
            tokens.append(token)
            punctuation.append(None)

    df_punctuation = DataFrame(zip(sections, tokens, punctuation), columns=['SECTIONS', 'TOKENS', 'PUNCTUATION'])
    df_new['TAGS_LISTS'] = None

    count = 0
    for row in df_new.itertuples():
        token = row.TOKENS
        idx = row.Index
        if token == df_original['TOKENS'].iloc[count]:
            df_new['TAGS_LISTS'].iloc[idx] = df_original['TAGS_LISTS'].iloc[count]
            count += 1

    # DEBUG
    df_punctuation.to_csv(TEXT_REPO + f'Footnotes_noise_example.{uid}_pun.csv')
    df_new.to_csv(TEXT_REPO + f'Footnotes_noise_example.{uid}_new.csv')

    updated_text = reconstruct_miu_text_with_tags(df_new)
    with open(TEXT_REPO + f'Footnotes_noise_example.{uid}.EIS1600', 'w', encoding='utf-8') as fh:
        fh.write(updated_text)
