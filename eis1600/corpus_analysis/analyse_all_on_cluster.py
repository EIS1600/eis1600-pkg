from typing import Optional
from sys import argv, exit
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


from eis1600.helper.logging import setup_persistent_logger
from eis1600.helper.parse_range import parse_range
from eis1600.repositories.repo import JSON_REPO, TEXT_REPO, get_ready_and_double_checked_files


def routine_per_text(
        infile: str,
        parallel: Optional[bool] = False,
        force: Optional[bool] = False,
        debug: Optional[bool] = False,
):
    """Entry into analysis routine per text.

    Each text is disassembled into the list of MIUs. Analysis is applied to each MIU. Writes a JSON file containing
    the list of MIUs with their analysis results.
    :param ste infile: EIS1600 text which is analysed.
    :param bool parallel: Parallel flag for parallel processing, otherwise serial processing.
    :param bool force: Do processing even though file already exists.
    :param bool debug: Debug flag for more console messages.
    """
    out_path = infile.replace(TEXT_REPO, JSON_REPO)
    out_path = out_path.replace('.EIS1600', '.json')

    # do not process file if it's already generated
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
                uid, miu_as_text, analyse_flag = tup
                error += f'{uid}\n{e}\n\n\n'
            except Exception:
                raise

    dir_path = '/'.join(out_path.split('/')[:-1])
    Path(dir_path).mkdir(parents=True, exist_ok=True)

    with open(out_path, 'w', encoding='utf-8') as fh:
        jsonpickle.set_encoder_options('json', indent=4, ensure_ascii=False)
        json_str = jsonpickle.encode(res, unpicklable=False)
        fh.write(json_str)

    if error:
        raise ValueError(error)


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to parse whole corpus to annotated MIUs.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')
    arg_parser.add_argument('-P', '--parallel', action='store_true')
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
            "--force", "-f",
            action="store_true",
            help="process file regardless if it exist and overwrite it"
    )

    args = arg_parser.parse_args()
    debug = args.debug
    parallel = args.parallel
    force = args.force

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
            routine_per_text(infile, parallel, force, debug)
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
