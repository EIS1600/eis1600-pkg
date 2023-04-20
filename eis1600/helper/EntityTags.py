from importlib_resources import files
from typing import List
import pandas as pd
from eis1600.helper.Singleton import Singleton

path = files('eis1600.helper.data').joinpath('entity_tags.csv')


@Singleton
class EntityTags:
    __entity_tags_df = None
    __tag_list = None

    def __init__(self) -> None:
        entity_tags_df = pd.read_csv(path)
        EntityTags.__entity_tags_df = entity_tags_df
        EntityTags.__tag_list = entity_tags_df.loc[entity_tags_df['CATEGORY'].notna(), 'TAG'].to_list()

    @staticmethod
    def get_entity_tags_df() -> pd.DataFrame:
        return EntityTags.__entity_tags_df

    @staticmethod
    def get_entity_tags() -> List[str]:
        return EntityTags.__tag_list
