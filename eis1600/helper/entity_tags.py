from typing import List
from importlib_resources import files

import pandas as pd

path = files('eis1600.helper.data').joinpath('entity_tags.csv')
entity_tags_df = pd.read_csv(path)


def get_entity_tags_df() -> pd.DataFrame:
    return entity_tags_df


def get_entity_tags() -> List[str]:
    return entity_tags_df.loc[entity_tags_df['CATEGORY'].notna(), 'TAG'].to_list()
