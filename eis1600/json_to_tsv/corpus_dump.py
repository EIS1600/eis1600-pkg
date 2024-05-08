import gzip
import os.path
import jsonpickle
import ujson as json
import pandas as pd
from pathlib import Path
from sys import argv
from tqdm import tqdm
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from eis1600.repositories.repo import get_ready_and_double_checked_files, TEXT_REPO, JSON_REPO, TSV_YML_REPO, \
    TSV_DF_REPO, COLUMNS, SEP, SEP2
from eis1600.helper.CheckFileEndingActions import CheckFileEndingEIS1600JsonAction


ALL_LABELS = ("SECTIONS", "TOKENS", "TAGS_LISTS", "NER_LABELS", "LEMMAS", "POS_TAGS", "ROOTS", "TOPONYM_LABELS",
              "NER_TAGS", "DATE_TAGS", "MONTH_TAGS", "ONOM_TAGS", "ONOMASTIC_TAGS")


def dump_file(fpath: str, label_list: tuple[str] = ALL_LABELS):

    if not fpath.endswith(".json.gz"):
        fpath = fpath.replace(TEXT_REPO, JSON_REPO)
        fpath = fpath.replace('.EIS1600', '.json.gz')

    structural_data, content_data = [], []

    if not Path(fpath).is_file():
        print(f"Warning! file {fpath} not found")
        return

    with gzip.open(fpath, "rt", encoding="utf-8") as fp:
        data = json.load(fp)

    for miu in data:
        header = miu["yml"]
        uid = header["UID"]

        # get structural data
        for entity in header.keys():
            if entity == "UID":
                continue
            value = header[entity]
            if type(value) in (str, int, bool):
                structural_data.append((uid, entity, value))
            elif type(value) == list:
                for sub_value in value:
                    if type(sub_value) == dict:
                        parsed_sub_value = SEP.join(f"{k}{SEP2}{v}" for k, v in sub_value.items())
                        structural_data.append((uid, entity, parsed_sub_value))
                    elif type(sub_value) == list:
                        parsed_sub_value = SEP.join(sub_value)
                        structural_data.append((uid, entity, parsed_sub_value))
                    else:
                        structural_data.append((uid, entity, sub_value))
            elif type(value) == dict:
                for sub_entity, sub_value in value.items():
                    if type(sub_value) == list:
                        for val in sub_value:
                            structural_data.append((uid, entity, f"{sub_entity}{SEP}{val}"))
                    elif type(sub_value) == dict:
                        # e.g. onomastics elements
                        for sub_sub_ent, sub_sub_val in sub_value.items():
                            structural_data.append((uid, entity, f"{sub_entity}{SEP}{sub_sub_ent}{SEP2}"))
                    else:
                        structural_data.append((uid, entity, f"{sub_entity}{SEP}{sub_value}"))
            else:
                raise ValueError(f'Fatal error dumping data of "{fpath}".')

        # get content data
        miu_df = jsonpickle.decode(miu["df"])
        for entity in label_list:
            if entity not in miu_df:
                continue
            for j, (_, value) in enumerate(miu_df[entity].items(), 1):
                if type(value) == list:
                    value = SEP2.join(value)
                if value:
                    content_data.append((uid, entity, f"{j}{SEP}{value}"))

    fpath_yml = fpath.replace(JSON_REPO, TSV_YML_REPO)
    fpath_yml = fpath_yml.replace(".json.gz", "")
    dir_path_yml, _ = os.path.split(fpath_yml)
    Path(dir_path_yml).mkdir(parents=True, exist_ok=True)

    struct_df = pd.DataFrame(structural_data, columns=COLUMNS)
    struct_df.to_csv(f"{fpath_yml}_yml.tsv.gz", sep="\t", index=False, compression='gzip')

    fpath_df = fpath.replace(JSON_REPO, TSV_DF_REPO)
    fpath_df = fpath_df.replace(".json.gz", "")
    dir_path_df, _ = os.path.split(fpath_df)
    Path(dir_path_df).mkdir(parents=True, exist_ok=True)

    content_df = pd.DataFrame(content_data, columns=COLUMNS)
    content_df.to_csv(f"{fpath_df}_df.tsv.gz", sep="\t", index=False, compression='gzip')


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description="Script to dump all eis1600 corpus into a tsv with the structure and "
                        "another tsv file with the enriched textual information."
    )
    arg_parser.add_argument(
            'infile', type=str, nargs='?',
            help='json file to process',
            action=CheckFileEndingEIS1600JsonAction
    )
    arg_parser.add_argument(
        "--label_list",
        nargs="*",
        default=ALL_LABELS,
        help="entities from content data to add to output. The default is all entities: "
             "SECTIONS, TOKENS, TAGS_LISTS, NER_LABELS, LEMMAS, POS_TAGS, ROOTS, TOPONYM_LABELS, "
             "NER_TAGS, DATE_TAGS, MONTH_TAGS, ONOM_TAGS, ONOMASTIC_TAGS"
    )
    args = arg_parser.parse_args()

    if args.infile:
        dump_file(args.infile, args.label_list)

    else:
        files_ready, files_double_checked = get_ready_and_double_checked_files()
        files = files_ready + files_double_checked

        for fpath in tqdm(files):

            dump_file(fpath, args.label_list)

        print(f"Processed {len(files)} files")
        print(f"For each json file in {JSON_REPO} directory, "
              f"a tsv with the yml data and a tsv with the df data have been generated.")

