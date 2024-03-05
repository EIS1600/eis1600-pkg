
import os
import sys
from argparse import ArgumentParser

from eis1600.repositories.repo import get_ready_and_double_checked_files


def main():
    arg_parser = ArgumentParser(
        prog=sys.argv[0],
        description="Simple script to show sizes in MB of all input files"
    )
    arg_parser.add_argument(
        "--sort_asc", "-a",
        action="store_true",
        help="sort files by size in ascending order"
    )
    arg_parser.add_argument(
        "--sort_desc", "-d",
        action="store_true",
        help="sort files by size in descending order"
    )
    args = arg_parser.parse_args()

    files_ready, files_double_checked = get_ready_and_double_checked_files()
    infiles = files_ready + files_double_checked

    if not infiles:
        print('There are no EIS1600 files to process')
        sys.exit()

    infiles = [(f, os.path.getsize(f)) for f in infiles]

    if args.sort_asc:
        infiles.sort(key=lambda x: x[1])
    elif args.sort_desc:
        infiles.sort(key=lambda x: x[1], reverse=True)

    for i, (file, size) in enumerate(infiles, 1):
       mb = size >> 20
       i = f"[{i}]"
       print(f"{i:<6} {mb:<2} {file}")
