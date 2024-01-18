from typing import List, Tuple

from pandas import isna, DataFrame
from camel_tools.tokenizers.word import simple_word_tokenize

from eis1600.markdown.markdown_patterns import PARAGRAPH_UID_PATTERN
from eis1600.models.Model import Model
from eis1600.processing.preprocessing import get_yml_and_miu_df, tokenize_miu_text
from eis1600.processing.postprocessing import reconstruct_miu_text_with_tags
from eis1600.repositories.repo import TEXT_REPO


def test_for_poetry(text: str):
    return False


def get_old_paragraphs(df: DataFrame) -> List[Tuple[str, str]]:
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
        elif PARAGRAPH_UID_PATTERN.match(section):
            paragraphs.append((curr_section_type, ' '.join(tokens)))
            curr_section_type = PARAGRAPH_UID_PATTERN.match(section).group('cat')
            tokens = [token]

    paragraphs.append((curr_section_type, ' '.join(tokens)))
    return paragraphs[1:]  # First element is (None, '') due to the MIU header


def remove_original_paragraphs(old_paragraphs: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    mergeable_paragraphs = []
    unsplitted = []
    for cat, text in old_paragraphs:
        if cat == 'POETRY' or '%~%' in text or (len(text.split()) < 60 and test_for_poetry(text)):
            unsplitted.append(('UNDEFINED', ' '.join(mergeable_paragraphs)))
            mergeable_paragraphs = []
            if '%~%' not in text:
                text = '%~% ' + text
            unsplitted.append(('POETRY', text))
        else:
            mergeable_paragraphs.append(text)
    if mergeable_paragraphs:
        unsplitted.append(('UNDEFINED', ' '.join(mergeable_paragraphs)))

    return unsplitted


def split_by_model(unsplitted: str) -> List[Tuple[str, str]]:
    tokenized = simple_word_tokenize(unsplitted)
    # model = Model()
    # punctuation_predictions = model.predict_sentence_with_windowing(tokenized)
    # TODO Translate predictions into punctuation, and add double newline and then split according into paragraphs
    # Do we remove old/original punctuation?
    text_with_punctuation = unsplitted
    paragraphs = text_with_punctuation.split('\n\n')

    return [('UNDEFINED', paragraph) for paragraph in paragraphs]


def redefine_paragraphs(uid: str, miu_as_text: str) -> None:
    yml_handler, df_original = get_yml_and_miu_df(miu_as_text)
    miu_header = df_original['SECTIONS'].iloc[0]

    # DEBUG
    df_original.to_csv(TEXT_REPO + f'Footnotes_noise_example.{uid}_original.csv')

    old_paragraphs = get_old_paragraphs(df_original)
    unsplitted_text = remove_original_paragraphs(old_paragraphs)

    new_paragraphs = []
    for cat, unsplitted in unsplitted_text:
        if cat == 'UNDEFINED':
            new_paragraphs.extend(split_by_model(unsplitted))
        else:
            new_paragraphs.append((cat, unsplitted))

    # And now puzzle everything together
    text_with_new_paragraphs = miu_header + '\n\n'
    for cat, paragraph in new_paragraphs:
        text_with_new_paragraphs += f'::{cat}::\n{paragraph}\n\n'

    text_with_new_paragraphs = text_with_new_paragraphs[:-2]    # delete new-lines from the end
    zipped = tokenize_miu_text(text_with_new_paragraphs, simple_mARkdown=True)
    df_new = DataFrame(zipped, columns=['SECTIONS', 'TOKENS', 'TAGS_LISTS'])
    df_new['TAGS_LISTS'] = None

    count = 0
    for row in df_new.itertuples():
        token = row.TOKENS
        idx = row.Index
        if token == df_original['TOKENS'].iloc[count]:
            df_new['TAGS_LISTS'].iloc[idx] = df_original['TAGS_LISTS'].iloc[count]
            count += 1

    # DEBUG
    df_new.to_csv(TEXT_REPO + f'Footnotes_noise_example.{uid}.csv')

    updated_text = reconstruct_miu_text_with_tags(df_new)
    with open(TEXT_REPO + f'Footnotes_noise_example.{uid}.EIS1600', 'w', encoding='utf-8') as fh:
        fh.write(updated_text)
