from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
from sys import argv, exit
from typing import Optional
from logging import ERROR

import jsonpickle
from tqdm import tqdm
from p_tqdm import p_uimap

from eis1600.corpus_analysis.miu_methods import analyse_miu
from eis1600.corpus_analysis.text_methods import get_text_as_list_of_mius
from eis1600.helper.logging import setup_logger
from eis1600.helper.repo import JSON_REPO, TEXT_REPO, get_files_from_eis1600_dir, read_files_from_autoreport

def routine_per_text(infile: str, debug: Optional[bool] = False):
    mius_list = get_text_as_list_of_mius(infile)

    res = []
    if debug:
        for idx, tup in tqdm(list(enumerate(mius_list[:20]))):
            res.append(analyse_miu(tup))
    else:
        res += p_uimap(analyse_miu, mius_list[:20])

    out_path = infile.replace(TEXT_REPO, JSON_REPO)
    out_path = out_path.replace('.EIS1600', '.json')
    dir_path = '/'.join(out_path.split('/')[:-1])
    Path(dir_path).mkdir(parents=True, exist_ok=True)

    with open(out_path, 'w', encoding='utf-8') as fh:
        jsonpickle.set_encoder_options('json', indent=4, ensure_ascii=False)
        json_str = jsonpickle.encode(res, unpicklable=False)
        fh.write(json_str)


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to parse whole corpus to annotated MIUs.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')

    args = arg_parser.parse_args()
    debug = args.debug

    # TODO torch.cuda.is_available()

    # Retrieve all double-checked texts
    input_dir = TEXT_REPO
    files_list = read_files_from_autoreport(input_dir)

    infiles = get_files_from_eis1600_dir(input_dir, files_list, 'EIS1600')
    if not infiles:
        print('There are no EIS1600 files to process')
        exit()

    logger = setup_logger('disassemble', 'disassemble.log')
    for i, infile in tqdm(list(enumerate(infiles[:5]))):
        try:
            print(f'{i} {infile}')
            routine_per_text(infile, debug)
        except ValueError as e:
            errors = True
            logger.log(ERROR, f'{infile}\n{e}')

    print('Done')
