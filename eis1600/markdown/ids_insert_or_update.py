from glob import glob
from logging import ERROR, Formatter
from sys import argv, exit
from os.path import isfile, splitext
from argparse import ArgumentParser, Action, RawDescriptionHelpFormatter

from urllib import request
from p_tqdm import p_uimap
from pandas import read_csv
from tqdm import tqdm

from eis1600.helper.logging import setup_logger
from eis1600.helper.repo import TEXT_REPO
from eis1600.markdown.subid_methods import add_ids


class CheckFileEndingAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and isfile(input_arg):
            filepath, fileext = splitext(input_arg)
            if not fileext.startswith('.EIS1600'):
                parser.error('You need to input an EIS1600 or EIS1600TMP file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, None)


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to insert UIDs in EIS1600TMP file(s) and thereby converting them to final EIS1600 
            file(s).
-----
Give a single EIS1600 or EIS1600TMP file as input.

Run without input arg to batch process all double-checked and ready files from the OpenITI_EIS1600_Texts directory.
'''
            )
    arg_parser.add_argument('-D', '--debug', action='store_true')
    arg_parser.add_argument(
            'input', type=str, nargs='?',
            help='EIS1600 or EIS1600TMP file to process',
            action=CheckFileEndingAction
            )
    args = arg_parser.parse_args()

    infile = args.input
    debug = args.debug

    if infile:
        add_ids(infile, ids_update=True)
    else:
        print('Download latest version of "_EIS1600 - Text Selection - Serial Source Test - '
              'EIS1600_AutomaticSelectionForReview" from Google Spreadsheets')
        latest_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR60MrlXJjtrd3bid1CR3xK5Pv" \
                    "-aUz1qWEfHfowU1DPsh6RZBvbtW2mA-83drzboIS1fxZdsDO-ny0r/pub?gid=2075964223&single=true&output=csv"
        response = request.urlopen(latest_csv)
        lines = [line.decode('utf-8') for line in response.readlines()]
        csv_path = TEXT_REPO + '_EIS1600 - Text Selection - Serial Source Test - ' \
                               'EIS1600_AutomaticSelectionForReview.csv'
        with open(csv_path, 'w', encoding='utf-8') as csv_fh:
            csv_fh.writelines(lines)

        print('Saved as csv in ' + TEXT_REPO)

        df = read_csv(csv_path, usecols=['Book Title', 'PREPARED']).dropna()
        df_processable_files = df.loc[df['PREPARED'].str.fullmatch('double-checked|ready')]

        infiles = []

        print('URIs of files for whom no .EIS1600 file was found')
        for uri in df_processable_files['Book Title']:
            author, text = uri.split('.')
            text_path = TEXT_REPO + 'data/' + author + '/' + uri + '/'
            text_file = glob(text_path + '*.EIS1600')
            if text_file:
                infiles.append(text_file[0])
            else:
                print(uri)

        if not infiles:
            print(
                    'There are no more EIS1600 files to process'
            )
            exit()

        print('\nAdd IDs')
        formatter = Formatter('%(message)s\n\n\n')
        logger = setup_logger('sub_ids', TEXT_REPO + 'sub_ids.log', ERROR, formatter)
        res = []
        count = 0
        if debug:
            x = 1
            for i, infile in tqdm(list(enumerate(infiles[x:]))):
                print(i + x, infile)
                try:
                    add_ids(infile)
                except ValueError as e:
                    logger.error(f'{infile}\n{e}\n\n')
                    count += 1

            print(f'{len(infiles)-count}/{len(infiles)} processed')
        else:
            res += p_uimap(add_ids, infiles)

    print('Done')



