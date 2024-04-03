
from enum import Enum
from collections import namedtuple


BIO_MAN = "$BIO_MAN$"
BIO_WOM = "$BIO_WOM$"
BIO_REP = "$BIO_REP$"
BIO_LST = "$BIO_LST$"

BIO_TAGS = (BIO_MAN, BIO_WOM, BIO_REP, BIO_LST)
EVENT_TAGS = ("@", "|", "||", "|||", "||||", "|||||", "||||||", "|||||||", "||||||||", "|||||||||", "||||||||||")
OTHER_TAGS = ("$DIC_BIB$", "$DIC_LEX$", "$DIC_NIS$", "$DIC_TOP$")
EXTERNAL = ("|APPENDIX|", "|PARATEXT|", "|EDITOR|")


class CategoryType(Enum):
    EVENT = "event"
    BIOGRAPHY = "biography"
    OTHER = "other"
    EXTERNAl = "external"


class Category:

    type: CategoryType = None
    value: str = None

    def __init__(self, value: str):
        if value in BIO_TAGS:
            category = CategoryType.BIOGRAPHY
        elif value in EVENT_TAGS:
            category = CategoryType.EVENT
        elif value in OTHER_TAGS:
            category = CategoryType.OTHER
        elif value in EXTERNAL:
            category = CategoryType.EXTERNAl
        else:
            raise ValueError(f"category {value} not recognised")
        self.value = value
        self.type = category

    def is_bio(self) -> bool:
        return self.type == CategoryType.BIOGRAPHY


def convert_to_longer_bio_tag(value: str) -> str:
    if any(tag in value for tag in BIO_TAGS+OTHER_TAGS):
        return value
    if "$$$$" in value:
        value = value.replace("$$$$", BIO_LST)
    elif "$$$" in value:
        value = value.replace("$$$", BIO_REP)
    elif "$$" in value:
        value = value.replace("$$", BIO_WOM)
    elif "$" in value:
        value = value.replace("$", BIO_MAN)
    return value
