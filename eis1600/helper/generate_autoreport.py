from functools import partial
from logging import ERROR, Formatter
from glob import glob

from eis1600.helper.logging import setup_logger

from eis1600.miu.methods import disassemble_text

from eis1600.markdown.methods import insert_uids
from p_tqdm import p_uimap

from pandas import Series, read_csv

from eis1600.helper.repo import MIU_REPO, TEXT_REPO


def main():
    filepath = TEXT_REPO + '_EIS1600 - Text Selection - Serial Source Test - EIS1600_AutomaticSelectionForReview.csv'

    df = read_csv(filepath, usecols=['Book Title', 'PREPARED']).dropna()
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

    print('Insert_UIDs into ready texts')

    x = 0
    for i, file in enumerate(ready_files[x:]):
        print(i + x, file)
        insert_uids(file)

    # res = []
    # res += p_uimap(insert_uids, ready_files)

    print('Disassemble double-checked and ready texts')

    texts = double_checked_files + [r.replace('TMP', '') for r in ready_files]
    out_path = MIU_REPO + 'data/'

    x = 0
    # 110 is not cleaned yet

    formatter = Formatter('%(message)s\n\n\n')
    logger = setup_logger('mal_formatted_texts', TEXT_REPO + 'mal_formatted_texts.log', ERROR, formatter)
    count = 0
    csv = []
    for i, text in enumerate(texts[x:]):
        print(i + x, text)
        try:
            disassemble_text(text, out_path)
        except ValueError as e:
            csv.append(text)
            count += 1
            logger.error(e)

    series = Series(csv, name='mal-formatted text')
    series.to_csv(TEXT_REPO + 'mal-formatted-texts.csv', index=False)

    print(f'{count} texts need fixing')

    # res = []
    # res += p_uimap(partial(disassemble_text, out_path=out_path), texts)

    print('Done')

