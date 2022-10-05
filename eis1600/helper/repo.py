from glob import glob
from os.path import split, splitext


def travers_eis1600_dir(path, file_ext_from, file_ext_to=None):
    path += 'data/*/*/'
    in_files = glob(path + file_ext_from)
    if not file_ext_to:
        return in_files
    else:
        exclude_files = glob(path + file_ext_to)
        files = []

        for file in in_files:
            path, uri = split(file)
            uri, ext = splitext(uri)
            if not path + '/' + uri + '.' + file_ext_to in exclude_files:
                files.append(file)

        return files
