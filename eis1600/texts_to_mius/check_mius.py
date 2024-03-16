import os.path
import sys
import ujson as json
from tqdm import tqdm
from itertools import zip_longest
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from eis1600.repositories.repo import get_ready_and_double_checked_files, TEXT_REPO, JSON_REPO
from eis1600.corpus_analysis.text_methods import get_text_as_list_of_mius
from eis1600.helper.CheckFileEndingActions import CheckFileEndingEIS1600TextAction


def compare_mius(infile, debug=False):
    """ return None is no errors, or string with error messages if errors """

    try:
        _, mius_list = get_text_as_list_of_mius(infile)

        original_mius = []
        for miu_block in mius_list:
            _, miu_id = miu_block[0].rsplit(".", 1)
            original_mius.append(miu_id)

        json_file = infile.replace(TEXT_REPO, JSON_REPO)
        json_file = json_file.replace('.EIS1600', '.json')

    except ValueError:
        return f"file {infile} contains errors"

    if not os.path.exists(json_file):
        return f"file {json_file} does not exist"

    with open(json_file, "r", encoding="utf-8") as fp:
        data = json.load(fp)

        json_mius = [miu["yml"]["UID"] for miu in data]

        errors = []
        errors_found = False

        for ori_m, json_m in zip_longest(original_mius, json_mius):

            if ori_m != json_m:

                msg = (f"list of mius do not match!\n"
                       f"    original file = {infile}\n"
                       f"    json file     = {json_file}")

                if debug:
                    if not errors_found:
                        errors.append(msg)
                        errors_found = True
                    errors.append(f"    >> original miu {ori_m} != json miu {json_m}")
                else:
                    return msg

        if errors:
            return "\n".join(errors)


def main():
    arg_parser = ArgumentParser(
            prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
            description="check miu list is complete in json files"
    )
    arg_parser.add_argument(
            'infile', type=str, nargs='?',
            help='EIS1600 or EIS1600TMP file to process',
            action=CheckFileEndingEIS1600TextAction
    )
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
    arg_parser.add_argument(
        '-D',
        '--debug',
        action='store_true'
    )
    args = arg_parser.parse_args()

    if args.infile:
        if errors := compare_mius(args.infile, args.debug):
            print("Comparison was not successful!")
            print(errors)

    else:
        files_ready, files_double_checked = get_ready_and_double_checked_files()
        files = files_ready + files_double_checked

        if not files:
            print('There are no more EIS1600 files to process')
            sys.exit()

        errors = []
        err_count = 0

        for i, infile in tqdm(list(enumerate(files))):
            if args.debug:
                print(f"[{i+1}] {infile}")
            if err := compare_mius(infile, args.debug):
                errors.append(err)
                err_count += 1

        if errors:
            print("Comparison was not successful!")
            print("\n".join(errors))
            print(f"\n{err_count} files failed. "
                  "You can run `check_mius EIS1600_FILE --debug` to see the mismatch of a specific file")
        else:
            print("Everything matches")

