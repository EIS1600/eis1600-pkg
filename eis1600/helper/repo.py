"""

This module contains functions to work with the EIS1600 text repo. This includes retrieving files from the repo,
as well as reading and writing to the README file of that repo.

Functions:
:function write_to_readme(path, files, which, ext=None, checked=False, remove_duplicates=False):
:function read_files_from_readme(path, which):
:function update_texts_fixed_poetry_readme(path, which):
:function get_files_from_eis1600_dir(path, file_list, file_ext_from, file_ext_to):
:function travers_eis1600_dir(path, file_ext_from, file_ext_to): Discontinued
"""

from glob import glob
from os.path import split, splitext
from typing import List, Literal, Optional

from eis1600.markdown.re_patterns import FIXED_POETRY_OLD_PATH_PATTERN


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
    """Write list of successfully processed files to the README.

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
            file_path, uri = split(file)
            if ext:
                uri, _ = splitext(uri)
            else:
                uri, ext = splitext(uri)
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
            file_path, uri = split(file)
            uri, ext = splitext(uri)
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
    write_to_readme(path, file_list, which)


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
        author, work, text = file.split('.')[:3]
        file_path = path + '/'.join([author, '.'.join([author, work]), '.'.join([author, work, text])]) + '.'
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
    out_path = '../'

    if 'data' in infile:
        out_path += infile.split('data')[0][2:]
    elif infile == './':
        pass
    else:
        depth = len(infile.split('/'))
        print(depth)
        if depth == 1:
            out_path += '../../../'
        elif depth == 2:
            out_path += '../../'
        elif depth == 3:
            out_path += '../'
        else:
            out_path += '../'

    if which == 'MIU':
        out_path += 'OpenITI_EIS1600_MIUs/data/'
    else:
        out_path += 'OpenITI_EIS1600_Texts/data/'

    return out_path
