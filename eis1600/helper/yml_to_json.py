from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
import jsonpickle
from p_tqdm import p_uimap

from eis1600.processing.preprocessing import get_yml
from eis1600.helper.repo import BACKEND_REPO, TRAINING_DATA_REPO


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to generate JSON from MIU YAMLHeaders.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')
    args = arg_parser.parse_args()

    debug = args.debug
    with open(TRAINING_DATA_REPO + 'gold_standard.txt', 'r', encoding='utf-8') as fh:
        files_txt = fh.read().splitlines()
    infiles = [TRAINING_DATA_REPO + 'gold_standard_topo/' + file for file in files_txt if Path(
            TRAINING_DATA_REPO + 'gold_standard_topo/' + file
    ).exists()]

    res = []
    if debug:
        for file in infiles[:10]:
            print(file)
            res.append(get_yml(file))
    else:
        res = p_uimap(get_yml, infiles)

    yml_dict = []
    for path, yml in res:
        key = path.replace(TRAINING_DATA_REPO + 'gold_standard_nasab/', '').replace('.EIS1600', '')
        author, text, version, UID = key.split('.')
        yml_init = {'author': author, 'text': text, 'version': version, 'UID': UID}
        yml_dict.append(yml.to_json(yml_init))

    with open(BACKEND_REPO + 'data.json', 'w', encoding='utf-8') as fh:
        jsonpickle.set_encoder_options('json', indent=4, ensure_ascii=False)
        json_str = jsonpickle.encode(yml_dict, unpicklable=False)
        fh.write(json_str)

    print('Done')
