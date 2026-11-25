"""Predict automatic Q spans while preserving reviewed descriptions in the text."""

import re

from eis1600.bio.md_to_bio import bio_to_md
from eis1600.models.ToponymDescriptionModel import ToponymDescriptionModel


def predict_description_tags(df):
    tokens = df["TOKENS"].fillna("-").to_list()
    labels = ToponymDescriptionModel().predict_sentence(tokens)
    if len(labels) != len(tokens):
        raise ValueError("Toponym description predictions do not align with the input tokens")
    tags = bio_to_md(labels)
    reviewed = set()
    for i, source_tags in enumerate(df["TAGS_LISTS"]):
        if isinstance(source_tags, list):
            for tag in source_tags:
                match = re.fullmatch(r"Q(\d+)", tag)
                if match:
                    reviewed.update(range(i, i + int(match[1])))
    for i, tag in enumerate(tags):
        if isinstance(tag, str) and any(j in reviewed for j in range(i, i + int(tag[2:]))):
            tags[i] = None
    return tags
