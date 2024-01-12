from logging import Formatter, INFO
from glob import glob
from urllib import request

from pandas import read_csv

from eis1600.helper.logging import setup_logger
from eis1600.helper.repo import MIU_REPO, TEXT_REPO
from eis1600.markdown.methods import insert_uids
from eis1600.miu.methods import disassemble_text


def main():
    print(
        'Download latest version of "_EIS1600 - Text Selection - Serial Source Test - '
        'EIS1600_AutomaticSelectionForReview" from Google Spreadsheets'
        )
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
    df_ready = df.loc[df['PREPARED'].str.fullmatch('ready')]
    df_double_checked = df.loc[df['PREPARED'].str.fullmatch('double-checked')]

    print(len(df_ready))
    print(len(df_double_checked))

    double_checked_files = []
    ready_files = []

    print('URIs for double-checked files for whom no .EIS1600 file was found')
    for uri in df_double_checked['Book Title']:
        author, text = uri.split('.')
        text_path = TEXT_REPO + 'data/' + author + '/' + uri + '/'
        text_file = glob(text_path + '*.EIS1600')
        if text_file:
            double_checked_files.append(text_file[0])
        else:
            print(uri)

    print('URIs for ready files for whom no .EIS1600TMP file was found')
    for uri in df_ready['Book Title']:
        author, text = uri.split('.')
        text_path = TEXT_REPO + 'data/' + author + '/' + uri + '/'
        tmp_file = glob(text_path + '*.EIS1600TMP')
        eis_file = glob(text_path + '*.EIS1600')
        if tmp_file and not eis_file:
            ready_files.append(tmp_file[0])
        elif tmp_file and eis_file:
            double_checked_files.append(eis_file[0])
            # print(f'{uri} (both TMP and EIS1600)')
        elif eis_file and not tmp_file:
            double_checked_files.append(eis_file[0])
            print(f'{uri} (no TMP but EIS1600)')
        else:
            print(f'{uri} (missing)')

    formatter = Formatter('%(message)s\n\n\n')
    logger = setup_logger('mal_formatted_texts', TEXT_REPO + 'mal_formatted_texts.log', INFO, formatter)

    logger.info('insert_uids')
    print('Insert_UIDs into ready texts')

    x = 0
    for i, file in enumerate(ready_files[x:]):
        print(i + x, file)
        try:
            insert_uids(file)
        except ValueError as e:
            logger.error(f'{file}\n{e}')

    logger.info('\n\n\ndisassemble_text')
    print('Disassemble double-checked and ready texts')

    texts = double_checked_files + [r.replace('TMP', '') for r in ready_files]
    out_path = MIU_REPO + 'data/'

    count = 0
    x = 0
    for i, text in enumerate(texts[x:]):
        print(i + x, text)
        try:
            disassemble_text(text, out_path)
        except ValueError as e:
            count += 1
            logger.error(e)
        except FileNotFoundError:
            print(f'Missing: {text}')


    print(f'{count}/{len(texts)} texts need fixing')

    print('Done')

