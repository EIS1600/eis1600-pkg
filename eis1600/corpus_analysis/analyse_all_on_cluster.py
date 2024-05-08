import sys
import gzip
import glob
import os.path
from typing import Optional
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from functools import partial
from pathlib import Path
from logging import INFO
from time import process_time, time
from random import shuffle

import jsonpickle
from tqdm import tqdm
from p_tqdm import p_uimap

from torch import cuda

from eis1600.corpus_analysis.miu_methods import analyse_miu
from eis1600.corpus_analysis.text_methods import get_text_as_list_of_mius
from eis1600.json_to_tsv.corpus_dump import dump_file
from eis1600.helper.logging import setup_persistent_logger
from eis1600.helper.parse_range import parse_range
from eis1600.repositories.repo import JSON_REPO, TEXT_REPO, PART_NAME_INFIX, PART_NUM_REGEX, \
                                       get_ready_and_double_checked_files

from eis1600.processing.short_miu_generation import get_short_miu, save_ids


def routine_per_text(
        infile: str,
        parallel: Optional[bool] = False,
        force: Optional[bool] = False,
        clean_out_dir: Optional[bool] = False,
        debug: Optional[bool] = False,
    ):
    """Entry into analysis routine per text.

    Each text is disassembled into the list of MIUs. Analysis is applied to each MIU. Writes a JSON file containing
    the list of MIUs with their analysis results.
    :param ste infile: EIS1600 text which is analysed.
    :param bool parallel: Parallel flag for parallel processing, otherwise serial processing.
    :param bool force: Do processing even though file already exists.
    :param bool clean_out_dir: When processing all files, clean json output in case there are previous splitting.
        This param will remove all json files in subfolder when file is original or part 1.
    :param bool debug: Debug flag for more console messages.
    """
    out_path = infile.replace(TEXT_REPO, JSON_REPO)
    out_path = out_path.replace('.EIS1600', '.json.gz')

    # do not process file if it's already generated and it should not be overwritten
    if Path(out_path).is_file() and not force:
        return

    meta_data_header, mius_list = get_text_as_list_of_mius(infile)

    res = []
    error = ''
    if parallel:
        res += p_uimap(partial(analyse_miu, debug=debug), mius_list)
    else:
        for idx, tup in tqdm(list(enumerate(mius_list))):
            try:
                res.append(analyse_miu(tup, debug))
            except ValueError as e:
                uid, *_ = tup
                error += f'{uid}\n{e}\n\n\n'
            except Exception:
                raise

    dir_path, _ = os.path.split(out_path)
    Path(dir_path).mkdir(parents=True, exist_ok=True)

    # if file is original or part 1, it might be good to remove previous json files
    # to avoid problems with previous chunking
    if clean_out_dir and (PART_NAME_INFIX not in out_path or int(PART_NUM_REGEX.search(out_path).group(1)) == 1):
        if os.path.exists(dir_path):
            for json_file in glob.iglob(os.path.join(dir_path, "*.json.gz")):
                os.remove(json_file)

    # add short id to each miu object
    for miu_obj in res:
        old_id = f'{miu_obj["yml"]["author"]}.{miu_obj["yml"]["text"]}.{miu_obj["yml"]["UID"]}'
        miu_obj["yml"] = {"id": get_short_miu(old_id), **miu_obj["yml"]}

    with gzip.open(out_path, 'wt', encoding='utf-8') as fh:
        jsonpickle.set_encoder_options('json', indent=4, ensure_ascii=False)
        json_str = jsonpickle.encode(res, unpicklable=False)
        fh.write(json_str)

    save_ids()

    if error:
        raise ValueError(error)


def main():
    arg_parser = ArgumentParser(
            prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to parse whole corpus to annotated MIUs.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')
    arg_parser.add_argument('-P', '--parallel', action='store_true')
    arg_parser.add_argument(
        '--no_tsv',
        action='store_true',
        help='do not make tsv conversion'
    )
    arg_parser.add_argument(
            '--range',
            metavar="ini,end",
            type=parse_range,
            help='process file range [i,j] (both are optional)'
    )
    arg_parser.add_argument(
            "--random", "-r",
            action="store_true",
            help="randomise list of files"
    )
    arg_parser.add_argument(
            "--clean_out_dir",
            action="store_true",
            help="clean previous processing, in case there has been a different chunking"
    )
    arg_parser.add_argument(
            "--force", "-f",
            action="store_true",
            help="process file regardless if it exist and overwrite it"
    )

    args = arg_parser.parse_args()
    debug = args.debug
    parallel = args.parallel
    force = args.force
    clean_out_dir = args.clean_out_dir

    print(f'GPU available: {cuda.is_available()}')

    st = time()
    stp = process_time()

    # Retrieve all double-checked texts
    files_ready, files_double_checked = get_ready_and_double_checked_files()
    infiles = files_ready + files_double_checked

    if not infiles:
        print('There are no EIS1600 files to process')
        exit()

    logger = setup_persistent_logger('analyse_all_on_cluster', 'analyse_all_on_cluster.log', INFO)

    if args.range:
        infiles = infiles[args.range[0]:args.range[1]]

    infiles_indexes = list(range(len(infiles)))

    if args.random:
        shuffle(infiles_indexes)

    for i in tqdm(infiles_indexes):
        infile = infiles[i]
        print(f"[{i+1}] {infile}")

        try:
            routine_per_text(infile, parallel=parallel, force=force, clean_out_dir=clean_out_dir, debug=debug)
            if not args.no_tsv:
                dump_file(infile)
        except ValueError as e:
            logger.error(f'{infile}\n{e}')
        except Exception as e:
            print(e)
            logger.exception(f'{infile}\n{e}')

    et = time()
    etp = process_time()

    print('Done')
    print(f'Processing time: {etp - stp} seconds')
    print(f'Execution time: {et - st} seconds')
