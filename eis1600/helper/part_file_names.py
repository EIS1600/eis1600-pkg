
import os.path


def get_part_number(file_name: str) -> int:
    """ get part number from file
    e.g. '0748Dhahabi.TarikhIslam.MGR20180917-ara1_part0016.EIS1600' -> 16
    """
    file_base, _ = os.path.splitext(file_name)
    part_number = file_base.rpartition("_")[-1]
    return int(part_number[4:])
