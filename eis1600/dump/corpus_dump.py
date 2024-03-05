import jsonpickle
from os import remove
from os.path import exists, splitext
from sys import argv
import ujson as json
import pandas as pd
from tqdm import tqdm
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from eis1600.repositories.repo import JSON_REPO, STRUCTURAL_TSV, CONTENT_TSV, COLUMNS, SEP, SEP2, \
    get_output_json_files, get_part_filepath


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

    # remove previous complete and part content files
    file_path_base, file_ext = splitext(CONTENT_TSV)
    i = 1
    if exists(CONTENT_TSV):
        remove(CONTENT_TSV)
    while exists(old_part_file := get_part_filepath(file_path_base, i, file_ext)):
        remove(old_part_file)
        i += 1

    files = list(get_output_json_files(JSON_REPO))

    structural_data, content_data = [], []

    if args.parts != 0:
        chunk_size = len(files) // args.parts
        i_chunk = 0
        i_part = 1
        created_part_files = []

    for i, file in tqdm(enumerate(files, 1), total=len(files)):
        if args.debug:
            print(f"[{i}] {file}")

        with open(file, "r", encoding="utf-8") as fp:
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
                        raise ValueError(f'Fatal error dumping data of "{file}".')

                # get content data
                miu_df = jsonpickle.decode(miu["df"])
                for entity in args.label_list:
                    if entity not in miu_df:
                        continue
                    for _, value in miu_df[entity].items():
                        if type(value) == list:
                            content_data.append((uid, entity, SEP.join(value)))
                        else:
                            if value:
                                content_data.append((uid, entity, value))

        if args.parts != 0:
            if i_chunk > chunk_size:
                content_df = pd.DataFrame(content_data, columns=COLUMNS)
                part_file = get_part_filepath(file_path_base, i_part, file_ext)
                content_df.to_csv(part_file, sep="\t", index=False)
                created_part_files.append(part_file)
                i_chunk = 0
                i_part += 1
                content_data = []
            else:
                i_chunk += 1

    struct_df = pd.DataFrame(structural_data, columns=COLUMNS)
    struct_df.to_csv(STRUCTURAL_TSV, sep="\t", index=False)

    if args.parts != 0:
        content_df = pd.DataFrame(content_data, columns=COLUMNS)
        part_file = get_part_filepath(file_path_base, i_part, file_ext)
        content_df.to_csv(part_file, sep="\t", index=False)
        created_part_files.append(part_file)
    else:
        content_df = pd.DataFrame(content_data, columns=COLUMNS)
        content_df.to_csv(CONTENT_TSV, sep="\t", index=False)

    print(f"Processed {len(files)} files")
    print(f"Structural eis1600 data saved in file {STRUCTURAL_TSV}")
    if args.parts != 0:
        for i, part_file in enumerate(created_part_files, 1):
            print(f"Part {i} of content eis1600 data saved in file {part_file}")
    else:
        print(f"Content eis1600 data saved in file {CONTENT_TSV}")
