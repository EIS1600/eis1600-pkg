from importlib_resources import files
from typing import List
from pandas import read_csv, DataFrame

from eis1600.helper.Singleton import singleton

entities_path = files('eis1600.markdown.data').joinpath('entity_tags.csv')


@singleton
class EntityTags:
    __entity_tags_df = None
    __tag_list = None
    __onom_tag_list = None

    def __init__(self) -> None:
        entity_tags_df = read_csv(entities_path)
        EntityTags.__entity_tags_df = entity_tags_df
        EntityTags.__tag_list = entity_tags_df.loc[entity_tags_df['CATEGORY'].notna(), 'TAG'].to_list()
        EntityTags.__onom_tag_list = entity_tags_df.loc[entity_tags_df['CATEGORY'] == 'ONOMASTIC', 'TAG'].to_list()

    @staticmethod
    def get_entity_tags_df() -> DataFrame:
        return EntityTags.__entity_tags_df

    @staticmethod
    def get_entity_tags() -> List[str]:
        return EntityTags.__tag_list

    @staticmethod
    def get_onom_tags() -> List[str]:
        return EntityTags.__onom_tag_list
