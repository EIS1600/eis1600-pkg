from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pandas import isna, DataFrame, notna

from eis1600.markdown.markdown_patterns import PARAGRAPH_UID_TAG_PATTERN, PUNCTUATION
from eis1600.models.BiosPunctuationModel import BiosPunctuationModel
from eis1600.models.EventsPunctuationModel import EventsPunctuationModel
from eis1600.models.PoetryDetectionModel import PoetryDetectionModel
from eis1600.processing.preprocessing import get_yml_and_miu_df, tokenize_miu_text
from eis1600.processing.postprocessing import merge_tagslists_without_duplicates, reconstruct_miu_text_with_tags
from eis1600.repositories.repo import NEW_PARAGRAPHS_REPO_ERROR_LOG


def test_for_poetry(tokens: List[str], debug: Optional[bool] = False):
    return PoetryDetectionModel().predict_is_poetry(tokens, debug)


def remove_punctuation(df: DataFrame) -> DataFrame:
    sections, tokens, tags = [], [], []
    for section, token, tag in df.itertuples(index=False):
        if token in PUNCTUATION:
            if not isna(section):
                raise ValueError(
                    'First token in this section is punctuation:\n'
                    f'{section}\n'
                    'This is not allowed during the re-splitting routine.\n'
                    )
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


def remove_original_paragraphs(old_paragraphs: List[Tuple[str, List[str]]]) -> \
        Tuple[List[Tuple[str, List[str]]], List[Dict]]:
    mergeable_paragraphs = []
    unsplitted = []
    poetry_test_res = []
    lines = []
    for cat, tokens in old_paragraphs:
        if cat == 'POETRY':
            curr_line = []
            for token in tokens:
                if token == '\n':
                    lines.append(curr_line)
                    curr_line = []
                else:
                    curr_line.append(token)
            lines.append(curr_line)
        else:
            lines.append(tokens)

    is_poetry = False
    curr_meter = None
    for line in lines:
        if 20 >= len(line) >= 3:
            is_poetry, res = test_for_poetry(line)
            poetry_test_res.append(res)
            if is_poetry:
                if '%~%' not in line:
                    line = ['%~%'] + line

                if curr_meter:
                    if curr_meter == res['label']:
                        mergeable_paragraphs.extend(['\n'] + line)
                    else:
                        unsplitted.append(('POETRY', mergeable_paragraphs))
                        mergeable_paragraphs = line
                        curr_meter = res['label']
                else:
                    unsplitted.append(('UNDEFINED', mergeable_paragraphs))
                    mergeable_paragraphs = line
                    curr_meter = res['label']
            else:
                is_poetry = False
                if curr_meter:
                    unsplitted.append(('POETRY', mergeable_paragraphs))
                    mergeable_paragraphs = line
                    curr_meter = None
                else:
                    mergeable_paragraphs.extend(line)

        else:
            is_poetry = False
            if curr_meter:
                unsplitted.append(('POETRY', mergeable_paragraphs))
                mergeable_paragraphs = []
                curr_meter = None

            mergeable_paragraphs.extend(line)

    if mergeable_paragraphs:
        if is_poetry:
            unsplitted.append(('POETRY', mergeable_paragraphs))
        else:
            unsplitted.append(('UNDEFINED', mergeable_paragraphs))

    return unsplitted, poetry_test_res


def split_by_model(tokens: List[str], is_bio: bool) -> List[Tuple[str, str]]:
    if is_bio:
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
    paragraphs = text_with_punctuation.split('PERIOD ')

    # TODO its not _ its COMMA etc
    return [('UNDEFINED', paragraph + 'PERIOD') if paragraph[-1] != '_' else ('UNDEFINED', paragraph)
            for paragraph in paragraphs if paragraph]


def redefine_paragraphs(uid: str, miu_as_text: str) -> Tuple[List[Dict], str]:
    yml_handler, df_original = get_yml_and_miu_df(miu_as_text)
    miu_header = df_original['SECTIONS'].iat[0]

    # Remove original punctuation and paragraphs
    df_new = remove_punctuation(df_original)
    old_paragraphs = get_old_paragraphs(df_new)
    unsplitted_text, poetry_test_res = remove_original_paragraphs(old_paragraphs)

    # Get new punctuation and paragraphs
    new_paragraphs = []
    for cat, unsplitted in unsplitted_text:
        if cat == 'UNDEFINED':
            new_paragraphs.extend(split_by_model(unsplitted, yml_handler.is_bio()))
        else:
            new_paragraphs.append((cat, ' '.join(unsplitted)))

    # And now put everything back together
    text_with_new_paragraphs = miu_header + '\n\n'
    for cat, paragraph in new_paragraphs:
        text_with_new_paragraphs += f'::{cat}::\n{paragraph}\n\n'

    # Get DataFrame of new punctuation and paragraphs
    zipped = tokenize_miu_text(text_with_new_paragraphs, simple_mARkdown=True)
    df_punctuation = DataFrame(zipped, columns=['SECTIONS', 'TOKENS', 'PUNCTUATION'])

    df_original['TOKENS'].mask(isna(df_original['TOKENS']), other='', inplace=True)

    data = []
    tmp = []
    idx_original = 0
    idx_punctuation = 1
    while idx_original < len(df_original):
        section = df_original['SECTIONS'].iat[idx_original]
        token = df_original['TOKENS'].iat[idx_original]
        tags_list = df_original['TAGS_LISTS'].iat[idx_original]
        automated_punctuation = df_punctuation['PUNCTUATION'].iat[idx_punctuation]
        automated_section = df_punctuation['SECTIONS'].iat[idx_punctuation]

        tmp.append((token, token == df_punctuation['TOKENS'].iat[idx_punctuation], df_punctuation['TOKENS'].iat[idx_punctuation], idx_punctuation))
        if idx_original == 0:
            data.append((section, token, tags_list, None))
            idx_original += 1
        elif notna(token) and token == df_punctuation['TOKENS'].iat[idx_punctuation]:
            # Token in df_original and df_punctuation are the same
            data.append((automated_section, token, tags_list, automated_punctuation))
            idx_original += 1
            idx_punctuation += 1
        elif notna(token) and token in PUNCTUATION or token == '':
            # Token in df_original and df_punctuation are not the same because the original token was punctuation or
            # end of a paragraph which got removed in the new version
            data.append((section, token, tags_list, None))
            idx_original += 1
        elif notna(token) and df_punctuation['TOKENS'].iat[idx_punctuation] == '':
            # Token in df_original and df_punctuation are not the same because in the new version we arrived at the
            # end of a paragraph which was not there in the original version
            data.append((automated_section, '', None, automated_punctuation))
            idx_punctuation += 1
        else:
            print(token, df_punctuation['TOKENS'].iat[idx_punctuation])
            Path(NEW_PARAGRAPHS_REPO_ERROR_LOG).mkdir(exist_ok=True, parents=True)
            df_original.to_csv(NEW_PARAGRAPHS_REPO_ERROR_LOG + f'{uid}_original.csv')
            df_punctuation.to_csv(NEW_PARAGRAPHS_REPO_ERROR_LOG + f'{uid}_punc.csv')
            DataFrame(tmp, columns=['token', 'equals', 'punc', 'idx_punctuation']).to_csv(
                    NEW_PARAGRAPHS_REPO_ERROR_LOG + f'Footnotes_noise_example.{uid}_tmp.csv'
            )
            DataFrame(data, columns=['SECTIONS', 'TOKENS', 'TAGS_LISTS', 'PUNCTUATION']).to_csv(
                    NEW_PARAGRAPHS_REPO_ERROR_LOG + f'{uid}_new.csv'
            )
            error = f'Something in the alignment broke, check the DataFrames in {NEW_PARAGRAPHS_REPO_ERROR_LOG}'
            raise IndexError(error)

    df_new = DataFrame(data, columns=['SECTIONS', 'TOKENS', 'TAGS_LISTS', 'PUNCTUATION'])
    df_new['TAGS_LISTS'] = df_new[['TAGS_LISTS', 'PUNCTUATION']].apply(merge_tagslists_without_duplicates,
                                                                       key='PUNCTUATION', axis=1)

    updated_text = reconstruct_miu_text_with_tags(df_new[['SECTIONS', 'TOKENS', 'TAGS_LISTS']])

    return poetry_test_res, updated_text
