from sys import argv, exit
from os.path import split, splitext
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path

from numpy import number
from p_tqdm import p_uimap
from pandas import DataFrame

from eis1600.depricated.disassemble_reassemble_methods import get_mius
from eis1600.helper.CheckFileEndingActions import CheckFileEndingEIS1600OrIDsAction
from eis1600.repositories.repo import RESEARCH_DATA_REPO, get_files_from_eis1600_dir, read_files_from_readme, MIU_REPO
from eis1600.statistics.methods import count_tokens


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to count tokens per MIU file(s).
-----
Give an IDs file or a single MIU file as input
otherwise 
all files in the MIU directory are batch processed.
'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')
    arg_parser.add_argument(
            'input', type=str, nargs='?',
            help='IDs or MIU file to process',
            action=CheckFileEndingEIS1600OrIDsAction
    )
    args = arg_parser.parse_args()

    debug = args.debug

    if args.input:
        infile = './' + args.input
        filepath, fileext = splitext(infile)
        if fileext == '.IDs':
            mius = get_mius(infile)[1:]  # First element is path to the OPENITI HEADER
            print(f'NER annotate MIUs of {infile}')
            res = []
            if debug:
                for i, miu in enumerate(mius):
                    print(f'{i} {miu}')
                    res.append(count_tokens(miu))
            else:
                res += p_uimap(count_tokens, mius)
        else:
            print(f'NER annotate {infile}')
            count_tokens(infile)
    else:
        input_dir = MIU_REPO

        if not Path(input_dir).exists():
            print('Your working directory seems to be wrong, make sure it is set to the parent dir of '
                  '`EIS1600_MIUs/`.')
            exit()

        data_path = RESEARCH_DATA_REPO + 'token_count/data/'
        Path(data_path).mkdir(parents=True, exist_ok=True)
        stats_path = RESEARCH_DATA_REPO + 'token_count/stats/'
        Path(stats_path).mkdir(parents=True, exist_ok=True)

        print(f'Count tokens per MIU')
        files_list = read_files_from_readme(input_dir, '# Texts disassembled into MIU files\n')
        infiles = get_files_from_eis1600_dir(input_dir, files_list, 'IDs')
        if not infiles:
            print('There are no IDs files to process')
            exit()

        for n, infile in enumerate(infiles):
            file_path, uri = split(infile)
            uri, ext = splitext(uri)
            if not debug:
                print(f'{n} {uri}')

            mius = get_mius(infile)[1:]  # First element is path to the OPENITI HEADER
            res = []
            if debug:
                for i, miu in enumerate(mius):
                    print(f'{i} {miu}')
                    res.append(count_tokens(miu))
            else:
                res += p_uimap(count_tokens, mius)

            df = DataFrame(res, columns=['URI', 'CATEGORY', 'NUMBER_OF_TOKENS'])
            df = df.astype({'CATEGORY': 'category', 'NUMBER_OF_TOKENS': 'int32'})
            df.to_csv(data_path + uri + '.csv', index=False)
            
            df.describe(include=[number, 'category']).to_csv(stats_path + uri + '_info.csv')
            df.groupby('CATEGORY').describe().to_csv(stats_path + uri + '_info_per_type.csv')

    print('Done')
