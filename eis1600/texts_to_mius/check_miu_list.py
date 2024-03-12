
import sys
import ujson as json
from tqdm import tqdm
from itertools import zip_longest
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from eis1600.repositories.repo import get_ready_and_double_checked_files, get_output_json_files, JSON_REPO
from eis1600.corpus_analysis.text_methods import get_text_as_list_of_mius


def main():
    arg_parser = ArgumentParser(
            prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
            description="check miu list is complete in json files"
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')
    arg_parser.add_argument(
        '--ignore_errors',
        action='store_true',
        help='ignore errors when retrieving list of MIUs'
    )
    arg_parser.add_argument(
        '--ignore_missing',
        action='store_true',
        help='do not show warnings for missing json files'
    )
    args = arg_parser.parse_args()

    files_ready, files_double_checked = get_ready_and_double_checked_files()
    files = files_ready + files_double_checked

    if not files:
        print('There are no more EIS1600 files to process')
        sys.exit()

    #
    # get original mius from input root folder
    #

    original_data = {}
    error_found = False

    for i, infile in tqdm(list(enumerate(files))):
        if args.debug:
            print(f"[{i+1}] {infile}")

        try:
            _, mius_list = get_text_as_list_of_mius(infile)
            book, _ = mius_list[0][0].rsplit(".", 1)

            miu_ids_ = []
            for miu_block in mius_list:
                _, miu_id = miu_block[0].rsplit(".", 1)
                miu_ids_.append(miu_id)

                original_data[book] = miu_ids_

        except ValueError:
            error_found = True

    if error_found:
        print("There are formatting errors in the input root directory. "
              "Run `check_formatting` and fix the errors before running this command.")
        if not args.ignore_errors:
            print("CHECK MIU LIST FAILED!")
            sys.exit(1)

    #
    # process json output folder
    #

    files = list(get_output_json_files(JSON_REPO))

    books_collected = set()

    print("\nChecking json files...")
    for i, fpath in tqdm(enumerate(files, 1), total=len(files)):
        if args.debug:
            print(f"[{i}] {fpath}")

        with open(fpath, "r", encoding="utf-8") as fp:
            data = json.load(fp)

            header = data[0]["yml"]
            book = f'{header["author"]}.{header["text"]}.{header["edition"]}'

            if book not in original_data:
                print(f"ERROR! {book} not found in original data")
                sys.exit(1)

            books_collected.add(book)

            mius_ori = original_data[book]
            mius_out = [miu["yml"]["UID"] for miu in data]

            for m_ori, m_out in zip_longest(mius_ori, mius_out):
                if m_ori != m_out:
                    print(f"ERROR! miu {m_ori} in original does not match miu {m_ori} in {m_out} in book {book}")
                    sys.exit(1)

    if not args.ignore_missing:
        print("\nChecking missing original files...")
        for ori_book in original_data:
            if ori_book not in books_collected:
                print(f"Warning! book {ori_book} from input root folder not found in json files")
