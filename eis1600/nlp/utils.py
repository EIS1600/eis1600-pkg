import re
from typing import List

from pandas import notna


def aggregate_STFCON_classes(st_list: list, fco_list: list) -> List[str]:
    label_dict = {
        "B-BIOGRAPHEE": "B",
        "I-BIOGRAPHEE": "B",
        "B-ISNAD": "I",
        "I-ISNAD": "I",
        "B-MAWLA": "M",
        "I-MAWLA": "M",
        "B-FAMILY": "F",
        "I-FAMILY": "F",
        "B-CONTACT": "C",
        "I-CONTACT": "C",
        "B-OPINION": "O",
        "I-OPINION": "O",
        "O": "",
        "_": "",
        "B-TEACHER": "T",
        "I-TEACHER": "T",
        "B-STUDENT": "S",
        "I-STUDENT": "S",
        "I-NEUTRAL": "X",
        "B-NEUTRAL": "X",
    }
    aggregated_labels = []
    for a, b in zip(st_list, fco_list):
        labels = f"{label_dict.get(a, '')}{label_dict.get(b, '')}"
        if a == b:
            labels = label_dict.get(a, '')
        else:
            labels = labels.replace("X", "")
        aggregated_labels.append(labels)
    return aggregated_labels


def merge_ner_with_person_classes(ner_labels, aggregated_stfco_labels):
    merged_labels = []
    for a, b in zip(ner_labels, aggregated_stfco_labels):
        if notna(a) and a[:2] == "ÜP":
            postfix = "X"
            if b.strip() != "":
                postfix = b.strip()
            a = a + postfix
        merged_labels.append(a)
    return merged_labels


def merge_ner_with_toponym_classes(ner_labels: List[str], toponym_labels: List[str]) -> List[str]:
    """Attach the role at a location start while preserving the detected NER span."""
    if len(ner_labels) != len(toponym_labels):
        raise ValueError("NER and place roles must have one prediction per token")
    merged_labels = []
    for entity, role_tag in zip(ner_labels, toponym_labels):
        if isinstance(entity, str) and entity.startswith("ÜT"):
            role = re.fullmatch(r"ÜT\d+([ABDGKORVX])", role_tag) if isinstance(role_tag, str) else None
            entity += role[1] if role else "X"
        merged_labels.append(entity)
    return merged_labels
