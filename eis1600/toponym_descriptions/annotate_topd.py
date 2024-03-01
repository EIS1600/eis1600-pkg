from pathlib import Path
from typing import Optional, Tuple, Union
from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from logging import Formatter, INFO
from time import process_time, time
from random import shuffle

from p_tqdm import p_uimap
from tqdm import tqdm
from torch import cuda

from eis1600.bio.md_to_bio import bio_to_md
from eis1600.corpus_analysis.text_methods import get_text_as_list_of_mius
from eis1600.helper.logging import setup_logger
from eis1600.helper.parse_range import parse_range
from eis1600.models.ToponymDescriptionModel import ToponymDescriptionModel
from eis1600.processing.preprocessing import get_yml_and_miu_df
from eis1600.processing.postprocessing import merge_tagslists, reconstruct_miu_text_with_tags
from eis1600.repositories.repo import TEXT_REPO, TOPO_REPO, get_ready_and_double_checked_files


def q_annotate_miu(tup: Tuple[str, str, bool]) -> Union[str, None]:
    uid, miu_as_text, analyse_flag = tup
    yml_handler, df = get_yml_and_miu_df(miu_as_text)

    toponym_labels = ToponymDescriptionModel().predict_sentence(df['TOKENS'].fillna('-').to_list())
    if 'B-TOPD' in toponym_labels:
        df['Q'] = bio_to_md(toponym_labels, umlaut_prefix=False)
        df['TAGS_LISTS'] = df.apply(merge_tagslists, key='Q', axis=1)

        updated_text = reconstruct_miu_text_with_tags(df[['SECTIONS', 'TOKENS', 'TAGS_LISTS']])

        return updated_text
    else:
        return None


def routine_per_text(
        infile: str,
        parallel: Optional[bool] = False,
        force: Optional[bool] = False,
        debug: Optional[bool] = False
    ):
    meta_data_header, mius_list = get_text_as_list_of_mius(infile)
    out_path = infile.replace(TEXT_REPO, TOPO_REPO)

    res = []
    error = ''
    if parallel:
        res += p_uimap(q_annotate_miu, mius_list)
    else:
        for idx, tup in tqdm(list(enumerate(mius_list))):
            try:
                res.append(q_annotate_miu(tup))
            except Exception as e:
                uid, miu_as_text, analyse_flag = tup
                error += f'{uid}\n{e}\n\n\n'

    dir_path = '/'.join(out_path.split('/')[:-1])
    Path(dir_path).mkdir(parents=True, exist_ok=True)

    if not all(r is None for r in res):
        with open(out_path, 'w', encoding='utf-8') as fh:
            fh.write('\n\n'.join([r for r in res if r]))

    if error:
        raise ValueError(error)


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to q_annotate whole corpus (e.g. for TOPD annotation).'''
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

    formatter = Formatter('%(message)s\n\n\n')
    logger = setup_logger('q_analyse', 'q_analyse.log', INFO, formatter)

    if args.range:
        infiles = infiles[args.range[0]:args.range[1]]

    infiles_indexes = list(range(len(infiles)))
    if args.random:
        shuffle(infiles_indexes)

    for i in tqdm(infiles_indexes):
        infile = infiles[infiles_indexes[i]]
        try:
            print(f'[{i}] {infile}')
            routine_per_text(infile, parallel, force, debug)
        except ValueError as e:
            logger.error(f'{infile}\n{e}')

    et = time()
    etp = process_time()

    print('Done')
    print(f'Processing time: {etp - stp} seconds')
    print(f'Execution time: {et - st} seconds')
