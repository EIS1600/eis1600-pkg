import os
import gzip
from sys import argv
import ujson as json
import pandas as pd
from io import StringIO
from pathlib import Path
from functools import partial
from p_tqdm  import p_uimap
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from eis1600.repositories.repo import get_ready_and_double_checked_files, TEXT_REPO, JSON_REPO, RECONSTRUCTED_REPO, \
                                       RECONSTRUCTED_INFIX
from eis1600.helper.CheckFileEndingActions import CheckFileEndingEIS1600JsonAction
from eis1600.helper.fix_dataframe import add_missing_columns
from eis1600.processing.postprocessing import write_updated_miu_to_file
from eis1600.yml.YAMLHandler import YAMLHandler


TAGS_LIST_FOR_RECONSTRUCTION = ('MSS', 'PAGES', 'DATE_TAGS', 'MONTH_TAGS', 'ONOM_TAGS', 'ONOMASTIC_TAGS', 'NER_TAGS')


def reconstruct_file(
        fpath: str,
        tags_list: tuple[str],
        force: bool = False,
        add_annotations_yml: bool = False,
        ):

    if fpath.endswith(".json.gz"):
        out_fpath = fpath.replace(".json.gz", f"{RECONSTRUCTED_INFIX}.EIS1600")
    else:
        fpath = fpath.replace(TEXT_REPO, JSON_REPO)
        out_fpath = fpath.replace(".EIS1600", f"{RECONSTRUCTED_INFIX}.EIS1600")
        fpath = fpath.replace('.EIS1600', '.json.gz')

    out_fpath = out_fpath.replace(JSON_REPO, RECONSTRUCTED_REPO)

    if not Path(fpath).is_file():
        print(f"Warning! file {fpath} not found")
        return

    # do not process file if it's already generated and it should not be overwritten
    if Path(out_fpath).is_file() and not force:
        return

    dir_path, _ = os.path.split(out_fpath)
    Path(dir_path).mkdir(parents=True, exist_ok=True)

    with gzip.open(fpath, "rt", encoding="utf-8") as fp, \
         open(out_fpath, "w", encoding="utf-8") as outfp:

        print(f"{fpath}")

        data = json.load(fp)
        yml = data[0]["yml"]
        yml_handler = YAMLHandler(yml, ignore_annotations=not add_annotations_yml)
        df = pd.concat([pd.read_json(StringIO(miu["df"])) for miu in data], ignore_index=True)
        df = add_missing_columns(df)
        df["TAGS_LISTS"] = None
        if 'ONOM_TAGS' in df:
            df['ONOM_TAGS'] = df['ONOM_TAGS'].map(lambda s: '' if s == '_' else s)
        write_updated_miu_to_file(
            outfp,
            yml_handler,
            df,
            target_columns=tags_list,
            forced_re_annotation=True,
            add_annotations_to_yml=add_annotations_yml
        )


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description="Script to reconstruct an EIS1600 text file form the json output."
    )
    arg_parser.add_argument(
            'infile', type=str, nargs='?',
            help='json file to process',
            action=CheckFileEndingEIS1600JsonAction
    )
    arg_parser.add_argument(
            '--tags', nargs='+',
            choices=TAGS_LIST_FOR_RECONSTRUCTION,
            default=TAGS_LIST_FOR_RECONSTRUCTION,
            help='list of tags to include in the reconstructed text. All by default'
    )
    arg_parser.add_argument(
            '--force', action='store_true',
            help='create file even though it is already created'
    )
    arg_parser.add_argument(
            '--add_annotations_to_yml', action='store_true',
            help='add all annotations to yml header'
    )
    args = arg_parser.parse_args()

    tags_list = tuple(args.tags)

    if args.infile:
        reconstruct_file(args.infile, tags_list=tags_list, force=True)

    else:
        files_ready, files_double_checked = get_ready_and_double_checked_files()
        files = files_ready + files_double_checked

        list(p_uimap(partial(reconstruct_file,
                             tags_list=tags_list,
                             force=args.force,
                             add_annotations_yml=args.add_annotations_to_yml
                             ),
                     files,
                     num_cpus=0.7)
             )

        print(f"Reconstructed files have been saved in {RECONSTRUCTED_REPO} directory.")
