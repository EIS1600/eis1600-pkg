from typing import Any

import pandas as pd

def fix_bonom_position(df: pd.DataFrame) -> pd.DataFrame:
    """
    BONOM tag is sometimes added to an empty section below. It should be moved to the next section.
        Example input:
            SECTION      TOKEN      TAG
            section_a    tok1       None
            None         None       MYTAG
            section_b    tok2       None
            None         tok3       None
            None         tok4       None
        Example output:
            SECTION      TOKEN      TAG
            section_a    tok1       None
            None         None       None
            section_b    tok2       MYTAG
            None         tok3       None
            None         tok4       None
    """
    # find the indices of rows where ONOM_TAG is BONOM
    mytag_indices = df[df['ONOM_TAGS'] == 'BONOM'].index

    # create masks for previous and next rows
    prev_mask = mytag_indices - 1 >= 0
    next_mask = mytag_indices + 1 < len(df)

    prev_section_not_none = df.loc[mytag_indices - 1, 'SECTIONS'].notna().values
    next_section_not_none = df.loc[mytag_indices + 1, 'SECTIONS'].notna().values

    misplaced_bonom = prev_mask & next_mask & prev_section_not_none & next_section_not_none
    df.loc[mytag_indices[misplaced_bonom], 'ONOM_TAGS'] = None
    df.loc[mytag_indices[misplaced_bonom] + 1, 'ONOM_TAGS'] = 'BONOM'

    return df


def _extract_value(tags_list: list, value: str) -> str | None:
    for tag in tags_list:
        if value in tag:
            return tag
    return None


def add_missing_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a column with the pages tags so that they are not lost when the text is reconstructed.
    Potentially other tags can be easily added just by including the pair (COL, VAl) below.
    """
    for col, val in (("PAGES", "Page"),):
        df[col] = df['TAGS_LISTS'].apply(
            lambda x: _extract_value(x, val) if x is not None and isinstance(x, list) else None
        )
    return df
