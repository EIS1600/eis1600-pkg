from typing import Tuple, Union
from argparse import ArgumentTypeError


def parse_range(arg: str) -> Tuple[int, Union[int, None]]:
    try:
        i, j = arg.split(",")
        i = int(i) - 1 if i else 0
        j = int(j) if j else None
        return i, j
    except ValueError:
        raise ArgumentTypeError("range must be i,j with both i and j being integers")

