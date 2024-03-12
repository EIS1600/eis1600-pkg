import os.path

import jsonpickle
from sys import argv
import ujson as json
import pandas as pd
from tqdm import tqdm
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from eis1600.repositories.repo import JSON_REPO, COLUMNS, SEP, SEP2, get_output_json_files


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description="Script to dump all eis1600 corpus into a tsv with the structure and "
                        "another tsv file with the enriched textual information."
    )
    arg_parser.add_argument(
        "--parts",
        metavar="n",
        type=int,
        default=4,
        help="split content tsv into n number of parts [DEFAULT 4]"
    )
    arg_parser.add_argument(
        "--label_list",
        nargs="*",
        default=["SECTIONS", "TOKENS", "TAGS_LISTS", "NER_LABELS", "LEMMAS", "POS_TAGS", "ROOTS", "TOPONYM_LABELS",
                 "NER_TAGS", "DATE_TAGS", "MONTH_TAGS", "ONOM_TAGS", "ONOMASTIC_TAGS"],
        help="entities from content data to add to output. The default is all entities: "
             "SECTIONS, TOKENS, TAGS_LISTS, NER_LABELS, LEMMAS, POS_TAGS, ROOTS, TOPONYM_LABELS, "
             "NER_TAGS, DATE_TAGS, MONTH_TAGS, ONOM_TAGS, ONOMASTIC_TAGS"
    )
    arg_parser.add_argument("-D", "--debug", action="store_true")
    args = arg_parser.parse_args()

    files = list(get_output_json_files(JSON_REPO))

    structural_data, content_data = [], []

    for i, fpath in tqdm(enumerate(files, 1), total=len(files)):
        if args.debug:
            print(f"[{i}] {fpath}")

        with open(fpath, "r", encoding="utf-8") as fp:
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
                                    structural_data.append((uid, entity, f"{sub_entity}{SEP}{sub_sub_ent}{SEP2}{val}"))
                            else:
                                structural_data.append((uid, entity, f"{sub_entity}{SEP}{sub_value}"))
                    else:
                        raise ValueError(f'Fatal error dumping data of "{fpath}".')

                # get content data
                miu_df = jsonpickle.decode(miu["df"])
                for entity in args.label_list:
                    if entity not in miu_df:
                        continue
                    for j, (_, value) in enumerate(miu_df[entity].items(), 1):
                        if type(value) == list:
                            value = SEP2.join(value)
                        if value:
                            content_data.append((uid, entity, f"{j}{SEP}{value}"))

        fbase, _ = os.path.splitext(fpath)

        content_df = pd.DataFrame(content_data, columns=COLUMNS)
        content_df.to_csv(f"{fbase}_df.tsv", sep="\t", index=False)

        struct_df = pd.DataFrame(structural_data, columns=COLUMNS)
        struct_df.to_csv(f"{fbase}_yml.tsv", sep="\t", index=False)

        structural_data, content_data = [], []

    print(f"Processed {len(files)} files")
    print(f"For each json file in {JSON_REPO} directory, "
          f"a tsv with the yml data and a tsv with the df data have been generated.")
