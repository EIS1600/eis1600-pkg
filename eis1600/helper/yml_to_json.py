import json
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path

from eis1600.helper.my_json_ecoder import MyJSONEncoder
from p_tqdm import p_uimap

from eis1600.processing.preprocessing import get_yml


def main():
    arg_parser = ArgumentParser(
            prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to generate JSON from MIU YAMLHeaders.'''
    )
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    args = arg_parser.parse_args()

    verbose = args.verbose
    with open('OpenITI_EIS1600_MIUs/gold_standard.txt', 'r', encoding='utf-8') as fh:
        files_txt = fh.read().splitlines()
    infiles = ['OpenITI_EIS1600_MIUs/training_nasab/' + file for file in files_txt if Path(
            'OpenITI_EIS1600_MIUs/training_nasab/' + file
    ).exists()]

    res = []
    # res = p_uimap(get_yml, infiles)

    for file in infiles[:10]:
        print(file)
        res.append(get_yml(file))

    paths, ymls = zip(*res)

    with open('OpenITI_EIS1600_MIUs/gold_standard_yml.json', 'w', encoding='utf-8') as fh:
        json.dump(ymls, fh, cls=MyJSONEncoder, indent='\t', ensure_ascii=False)

    print('Done')
