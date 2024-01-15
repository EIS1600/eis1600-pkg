from logging import Formatter, INFO
from glob import glob

from eis1600.helper.logging import setup_logger
from eis1600.repositories.repo import TEXT_REPO, get_ready_and_double_checked_texts
from eis1600.texts_to_mius.check_formatting_methods import check_formatting
from eis1600.texts_to_mius.subid_methods import add_ids


def main():
    """Script to check file formatting based on text selection."""

    df_ready, df_double_checked = get_ready_and_double_checked_texts()
    double_checked_files = []
    ready_files = []

    missing_texts = []
    for uri in df_double_checked['Book Title']:
        author, text = uri.split('.')
        text_path = TEXT_REPO + 'data/' + author + '/' + uri + '/'
        text_file = glob(text_path + '*.EIS1600')
        if text_file:
            double_checked_files.append(text_file[0])
        else:
            missing_texts.append(uri)

    if missing_texts:
        print('URIs for double-checked files for whom no .EIS1600 file was found')
        for uri in missing_texts:
            print(uri)
        print('\n')

    missing_texts = []
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
            missing_texts.append(f'{uri} (no TMP but EIS1600)')
        else:
            missing_texts.append(f'{uri} (missing)')

    if missing_texts:
        print('URIs for ready files for whom no .EIS1600TMP file was found')
        for uri in missing_texts:
            print(uri)
        print('\n')

    formatter = Formatter('%(message)s\n\n\n')
    logger = setup_logger('mal_formatted_texts', TEXT_REPO + 'mal_formatted_texts.log', INFO, formatter)

    logger.info('insert_uids')
    print('Insert UIDs into ready texts')

    x = 0
    for i, file in enumerate(ready_files[x:]):
        print(i + x, file)
        try:
            add_ids(file)
        except ValueError as e:
            logger.error(f'{file}\n{e}')

    logger.info('\n\n\ndisassemble_text')
    print('Check formatting for double-checked and ready texts')

    texts = double_checked_files + [r.replace('TMP', '') for r in ready_files]

    count = 0
    x = 0
    for i, text in enumerate(texts[x:]):
        print(i + x, text)
        try:
            check_formatting(text)
        except ValueError as e:
            count += 1
            logger.error(e)
        except FileNotFoundError:
            print(f'Missing: {text}')

    print(f'\n{count}/{len(texts)} texts need fixing\n')

    print('Done')

