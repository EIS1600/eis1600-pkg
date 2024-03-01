from logging import Formatter, INFO

from eis1600.helper.logging import setup_logger
from eis1600.repositories.repo import TEXT_REPO, get_ready_and_double_checked_files
from eis1600.texts_to_mius.check_formatting_methods import check_formatting
from eis1600.texts_to_mius.subid_methods import add_ids


def main():
    """Script to check file formatting based on text selection."""
    ready_files, double_checked_files = get_ready_and_double_checked_files(only_complete=True)

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

