from os.path import split, splitext
from typing import Tuple

from eis1600.processing.postprocessing import write_updated_miu_to_file

from eis1600.processing.preprocessing import get_yml_and_miu_df


def count_tokens(infile: str) -> Tuple[str, str, int]:
    """Count the number of tokens in this MI.

    :param str infile: Path of the MIU to count the tokens of.
    :return Tuple[str, str, int]: Tuple of the URI, the MIU's type and the number of tokens.
    """
    file_path, uri = split(infile)
    uri, ext = splitext(uri)

    with open(infile, 'r+', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object)

        number_of_tokens = df['TOKENS'].count()  # Count() counts all non-na values
        category = yml_handler.category

        yml_handler.set_number_of_tokens(number_of_tokens)

        write_updated_miu_to_file(miu_file_object, yml_handler, df)

    return uri, category, number_of_tokens
