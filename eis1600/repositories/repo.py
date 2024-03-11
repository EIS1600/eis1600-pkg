"""

This module contains functions to work with the EIS1600 repositories. This includes retrieving files from repos, writing
files to repos, as well as reading and writing to README and AUTOREPORT files.

Functions:
:function write_to_readme(path, files, which, ext=None, checked=False, remove_duplicates=False):
:function read_files_from_readme(path, which):
:function update_texts_fixed_poetry_readme(path, which):
:function get_files_from_eis1600_dir(path, file_list, file_ext_from, file_ext_to):
:function travers_eis1600_dir(path, file_ext_from, file_ext_to): Discontinued
"""
from typing import List, Literal, Optional, Tuple, Generator

import re
import os


from glob import glob

from pandas import read_csv

from eis1600.markdown.markdown_patterns import FIXED_POETRY_OLD_PATH_PATTERN
from eis1600.texts_to_mius.download_text_selection_sheet import download_text_selection
from eis1600.helper.part_file_names import get_part_number

# Path variables

MIU_REPO = 'EIS1600_MIUs/'
TEXT_REPO = 'OpenITI_EIS1600_Texts/'
NEW_PARAGRAPHS_REPO_ERROR_LOG = 'OpenITI_EIS1600_Texts_New_Paragraphs/error_log/'
NEW_PARAGRAPHS_REPO = 'OpenITI_EIS1600_Texts_New_Paragraphs/'
JSON_REPO = 'EIS1600_JSONs/'
PRETRAINED_MODELS_REPO = 'EIS1600_Pretrained_Models/'
TOPO_REPO = 'Topo_Data/'
TRAINING_DATA_REPO = 'Training_Data/'
RESEARCH_DATA_REPO = 'Research_Data/'
TRAINING_RESULTS_REPO = 'Training_Results/'
GAZETTEERS_REPO = 'gazetteers/'
MC_REPO = 'MasterChronicle/'
BACKEND_REPO = 'backend/'
TOPO_TRAINING_REPO = 'topo_training/data/'
POETRY_TEST_RES_REPO = 'POETRY_TEST_RESULTS/'

SPLITTED_PART_NAME_INFIX = '_part'

# columns for tsv output
COLUMNS = ["MIUID", "ENTITY", "VALUE"]

# separators for tsv containing annotated tokens
SEP = ":::"
SEP2 = "==="


def get_part_filepath(file_path_base: str, i: int, file_ext: str) -> str:
    return f"{file_path_base}{SPLITTED_PART_NAME_INFIX}{i:04}{file_ext}"


def get_ready_and_double_checked_files(only_complete: bool = False) -> Tuple[List[str], List[str]]:
    """Get prepared texts prepared for the processing pipeline.

    :param bool only_complete: get only all complete EIS1600 files.
    :return Tuple[DataFrame, DataFrame]: returns two DataFrames, one for ready texts and the other for double-checked files.
    """
    csv_path = download_text_selection(TEXT_REPO)
    # csv_path = TEXT_REPO + '_EIS1600 - Text Selection - Serial Source Test - EIS1600_AutomaticSelectionForReview.csv'
    df = read_csv(csv_path, usecols=['Book Title', 'PREPARED']).dropna()
    df_ready = df.loc[df['PREPARED'].str.fullmatch('ready')]
    df_double_checked = df.loc[df['PREPARED'].str.fullmatch('double-checked')]

    print(f'Files marked as "ready": {len(df_ready)}')
    print(f'Files marked as "double-checked": {len(df_double_checked)}\n')

    double_checked_files = []
    ready_files = []

    #FIXME modify ready files logic !!

    # Check if any EIS1600TMP files are missing
    missing_texts = []
    for uri in df_ready['Book Title']:
        author, text = uri.split('.')
        text_path = TEXT_REPO + 'data/' + author + '/' + uri + '/'
        tmp_files = glob(text_path + '*.EIS1600TMP')
        eis_files = glob(text_path + '*.EIS1600')
        if tmp_files and not eis_files:
            ready_files.append(tmp_files[0])
        elif tmp_files and eis_files:
            double_checked_files.append(eis_files[0])
            # print(f'{uri} (both TMP and EIS1600)')
        elif eis_files and not tmp_files:
            double_checked_files.append(eis_files[0])
            missing_texts.append(f'{uri} (no TMP but EIS1600)')
        else:
            missing_texts.append(f'{uri} (missing)')

    if missing_texts:
        print('URIs for ready files for whom no .EIS1600TMP file was found')
        for uri in missing_texts:
            print(uri)
        print('\n')

    # Check if any EIS1600 files are missing
    missing_texts = []
    for uri in df_double_checked['Book Title']:
        author, text = uri.split('.')
        text_path = TEXT_REPO + 'data/' + author + '/' + uri + '/'
        eis_files = glob(text_path + '*.EIS1600')

        if eis_files:

            # get original EIS1600 complete files
            if only_complete:
                for eis_file in eis_files:
                    if SPLITTED_PART_NAME_INFIX not in eis_file and eis_file.endswith(".EIS1600"):
                        double_checked_files.append(eis_file)
                        break

            # get parts of file or original EIS1600 file if not splitted in parts
            else:
                if part_files := [f for f in eis_files if SPLITTED_PART_NAME_INFIX in f]:
                    part_files.sort(key=get_part_number)
                    for part_file in part_files:
                        double_checked_files.append(part_file)

                else:
                    for eis_file in eis_files:
                        if SPLITTED_PART_NAME_INFIX not in eis_file and eis_file.endswith(".EIS1600"):
                            double_checked_files.append(eis_file)
                            break
        else:
            missing_texts.append(uri)

    if missing_texts:
        print('URIs for double-checked files for whom no .EIS1600 file was found (check if URI in the Google Sheet '
              'matches with the OpenITI_EIS1600_Text repo')
        for uri in missing_texts:
            print(uri)
        print('\n')

    return ready_files, double_checked_files


def get_entry(file_name: str, checked_entry: bool) -> str:
    """Formats README entry for that file_name.

    Only used internally.
    :param str file_name: The name of the file whose entry is added to the README
    :param bool checked_entry: Bool indicating if the checkbox of that entry is ticked or not
    :return str: The formatted entry which can be added to the README file
    """

    x = 'x' if checked_entry else ' '
    return '- [' + x + '] ' + file_name


def write_to_readme(path: str, files: List[str], which: str, ext: Optional[str] = None, checked: bool = False) -> None:
    """NOT USED ANY LONGER Write list of successfully processed files to the README.

    Write processed files to the respective section in the README, sorted into existing lists.

    :param str path: The root of the text repo, path to the README
    :param list[str] files: List of files to write to the respective section in the README
    :param str which: The section heading from the README indicating the section to write the list of files to.
    :param str or None ext: File extension of the files at the end of the process, optional.
    :param bool checked: Indicator if the checkboxes of the files are ticked, defaults to False.
    """

    file_list = []
    try:
        with open(path + 'README.md', 'r', encoding='utf8') as readme_h:
            out_file_start = ''
            out_file_end = ''
            checked_boxes = False
            line = next(readme_h)
            # Find section in the README to write to by finding the corresponding header line
            while line != which:
                out_file_start += line
                line = next(readme_h)
            out_file_start += line
            out_file_start += next(readme_h)
            line = next(readme_h)
            # Read existing entries from that section
            while line and line != '\n':
                if line.startswith('- ['):
                    checked_boxes = True
                    md, file = line.split('] ')
                    file_list.append((file, md == '- [x'))
                    line = next(readme_h, None)
                else:
                    file_list.append(line[2:])
                    line = next(readme_h, None)
            while line:
                out_file_end += line
                line = next(readme_h, None)

        # Change the file ending for files which have been processed if necessary (if new file ending is given)
        for file in files:
            file_path, uri = os.path.split(file)
            if ext:
                uri, _ = os.path.splitext(uri)
            else:
                uri, ext = os.path.splitext(uri)
            if checked_boxes:
                file_list.append((uri + ext + '\n', checked))
            else:
                file_list.append(uri + ext + '\n')

        # Remove duplicates
        file_list = list(set(file_list))
        # Sort list of all entries (old and new)
        file_list.sort()

        # Write new list to section in the readme
        with open(path + 'README.md', 'w', encoding='utf8') as readme_h:
            readme_h.write(out_file_start)
            if checked_boxes:
                readme_h.writelines([get_entry(file, checked_entry) for file, checked_entry in file_list])
            else:
                readme_h.writelines(['- ' + file for file in file_list])
            readme_h.write(out_file_end)

    except StopIteration:
        # Fallback option - if anything goes wrong at least print the list of changed files to a log
        file_list = []
        for file in files:
            file_path, uri = os.path.split(file)
            uri, ext = os.path.splitext(uri)
            file_list.append(uri + '.EIS1600\n')
        with open(path + 'FILE_LIST.log', 'w', encoding='utf8') as file_list_h:
            file_list_h.writelines(file_list)

        print(f'Could not write to the README file, check {path + "FILE_LIST.log"} for changed files')


def read_files_from_readme(path: str, which: str, only_checked: Optional[bool] = True) -> List[str]:
    """Get the list of files from the README to process further.

    Get the list of files from the README which are to be processed in further steps.
    :param str path: The root of the text repo, path to the README
    :param str which: The section heading from the README indicating the section from which to read the file list from.
    :param bool only_checked: If True, only read those lines with a ticked checkbox, defaults to True.
    :return list[str]: List of URIs from files to process further
    """

    file_list = []
    try:
        with open(path + 'README.md', 'r', encoding='utf8') as readme_h:
            line = next(readme_h)
            # Find section in the README to read from
            while line != which:
                line = next(readme_h)
            next(readme_h)
            line = next(readme_h)
            # Read files from that section
            while line and line != '\n':
                if line.startswith('- ['):
                    if only_checked:
                        # Only read those files which have been checked
                        if line.startswith('- [x'):
                            md, file = line.split('] ')
                            file_list.append(file[:-1])
                    else:
                        md, file = line.split('] ')
                        file_list.append(file[:-1])
                else:
                    file_list.append(line[2:-1])

                line = next(readme_h, None)
    except StopIteration:
        print(f'The README.md file does not seem to contain a "{which[:-1]}" section')

    return file_list


def read_files_from_autoreport(path: str) -> List[str]:
    """Get the list of files from the README to process further.

    Get the list of files from the README which are to be processed in further steps.
    :param str path: The root of the text repo, path to the README
    :return list[str]: List of URIs from files to process further
    """

    which_pattern = re.compile(r'## DOUBLE-CHECKED Files \(\d+\) - ready for MIU\n')
    file_list = []

    try:
        with open(path + 'AUTOREPORT.md', 'r', encoding='utf8') as autoreport_h:
            line = next(autoreport_h)
            # Find section in the AUTOREPORT to read from
            while not which_pattern.match(line):
                line = next(autoreport_h)
            next(autoreport_h)
            line = next(autoreport_h)
            # Read files from that section
            while line and line != '\n':
                file_list.append(line[4:-19])
                line = next(autoreport_h, None)
    except StopIteration:
        print(f'Something went wrong with reading the AUTOREPORT')

    return file_list


def update_texts_fixed_poetry_readme(path: str, which: str) -> None:
    """Update list of texts with fixed poetry in the README.

    Read list of texts with fixed poetry from the text file in the scipt folder and update the respective list in the
    README.

    :param str path: Path to the text directory root.
    :param str which: The section heading from the README indicating the section where the texts with fixed poetry
    are listed.
    """

    # Read the list of files with fixed poetry from other file and write it to the README
    with open(path + 'scripts/poetry_fixed.txt', 'r', encoding='utf8') as readme_h:
        files_text = readme_h.read()
    files_text = FIXED_POETRY_OLD_PATH_PATTERN.sub('', files_text)
    file_list = files_text.split('\n')


def get_files_from_eis1600_dir(
        path: str, file_list: List[str], file_ext_from: List[str] or str, file_ext_to: Optional[str] = None
) -> List[str]:
    """Get list of files to process from the EIS1600 text repo.

    Get list of the files with exact path from list of URIs. Do not select those files which have already been
    processed (those files already exist with the new file extension).

    :param str path: Path to the text directory root.
    :param list[str] file_list: List of URIs of files.
    :param str or list[str] file_ext_from: File extension(s) the unprocessed files have.
    :param str file_ext_to: File extension already processed files have, optional.
    :return list[str]: List of all files to process with exact path, not containing those files which have already
    been processed.
    """

    path += 'data/'
    files = []
    for file in file_list:
        author, text, version = file.split('.')[:3]
        file_path = path + '/'.join([author, '.'.join([author, text]), '.'.join([author, text, version])]) + '.'
        if file_ext_to and not glob(file_path + file_ext_to):
            # Only do if the target file does not exist
            if type(file_ext_from) == list:
                for ext in file_ext_from:
                    tmp = glob(file_path + ext)
                    if tmp:
                        files.extend(tmp)
            else:
                files.extend(glob(file_path + file_ext_from))
        elif not file_ext_to:
            # Do if file ending stays the same
            files.extend(glob(file_path + file_ext_from))
    return files


def get_path_to_other_repo(infile: str, which: Literal['MIU', 'TEXT']) -> str:
    """

    :param str infile: file which gives URI of the text.
    :param Literal which: Indicating which repo you want to get the path to, accepts 'MIU' or 'TEXT'.
    :return str: path to the same URI in the requested repo
    """
    if infile.startswith('./OpenITI_EIS1600_') or infile.startswith('./EIS1600_'):
        if which == 'MIU':
            return MIU_REPO + 'data/'
        else:
            return TEXT_REPO + 'data/'
    else:
        out_path = '../'

        if 'data' in infile:
            out_path += infile.split('data')[0][2:]
        elif infile != './':
            depth = len(infile.split('/'))
            if depth == 1:
                out_path += '../../../../'
            elif depth == 2:
                out_path += '../../../'
            elif depth == 3:
                out_path += '../../'
            else:
                out_path += '../'

        if which == 'MIU':
            return out_path + MIU_REPO + 'data/'
        else:
            return out_path + TEXT_REPO + 'data/'


def get_output_json_files(path: str) -> Generator[str, None, None]:
    """Get list of json files to from output EIS1600 directory.

    :param str path: Path to the json directory root.
    :return list[str]: List of all files to process with exact path, not containing those files which have already
    been processed.
    """
    path += 'data/'
    for author_fobj in os.scandir(path):
        if not author_fobj.is_dir():
            continue
        for text_fobj in os.scandir(author_fobj):
            if not text_fobj.is_dir():
                continue
            part_files = [fo.path for fo in os.scandir(text_fobj) if fo.name.endswith(".json")]
            if len(part_files) == 1:
                yield part_files[0]
            else:
                part_files.sort(key=get_part_number)
                yield from part_files
