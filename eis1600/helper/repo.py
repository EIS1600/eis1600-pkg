from glob import glob
from os.path import split, splitext


def write_to_readme(path, files):
    if not path[-1] == '/':
        path += '/'
    file_list = []
    for file in files:
        file_path, uri = split(file)
        uri, ext = splitext(uri)
        file_list.append((uri + '.EIS1600\n', False))
    with open(path + 'README.md', 'r', encoding='utf8') as readme_h:
        out_file_start = ''
        out_file_end = ''
        line = next(readme_h)
        while line != '# Texts converted into `.EIS1600`\n':
            out_file_start += line
            line = next(readme_h)
        out_file_start += line
        out_file_start += next(readme_h)
        line = next(readme_h)
        while line != '\n':
            md, file = str(line).split('] ')
            file_list.append((file, md == '- [x'))
            line = next(readme_h)
        while line:
            out_file_end += line
            line = next(readme_h, None)

    file_list.sort()

    def get_entry(file_name, checked):
        x = 'x' if checked else ''
        return '- [' + x + '] ' + file_name

    with open(path + 'README.md', 'w', encoding='utf8') as readme_h:
        readme_h.write(out_file_start)
        readme_h.writelines([get_entry(file, checked) for file, checked in file_list])
        readme_h.write(out_file_end)


def get_files_from_eis1600_dir(path, file_ext_from, file_ext_to=None):
    if not path[-1] == '/':
        path += '/'

    file_list = []
    with open(path + 'README.md', 'r', encoding='utf8') as readme_h:
        line = next(readme_h)
        while line != '# Texts with fixed poetry\n':
            line = next(readme_h)
        next(readme_h)
        next(readme_h)
        line = next(readme_h)
        while line != '\n':
            file_list.append(line[2:-1])
            line = next(readme_h)

    path += 'data/'
    files = []
    for file in file_list:
        author, work, text = file.split('.')[:3]
        file_path = path + '/'.join([author, '.'.join([author, work]), '.'.join([author, work, text])])
        if file_ext_to and not glob(file_path + file_ext_to):
            if type(file_ext_from) == list:
                for ext in file_ext_from:
                    print(file_path + ext)
                    tmp = glob(file_path + ext)
                    if tmp:
                        files.extend(tmp)
            else:
                files.extend(glob(file_path + file_ext_from))
        elif not file_ext_to:
            files.extend(glob(file_path + file_ext_from))
    return files


def travers_eis1600_dir(path, file_ext_from, file_ext_to=None):
    if not path[-1] == '/':
        path += '/'
    path += 'data/*/*/'
    in_files = glob(path + file_ext_from)
    if not file_ext_to:
        return in_files
    else:
        exclude_files = glob(path + file_ext_to)
        files = []

        for file in in_files:
            path, ext = splitext(file)
            if not path + '.' + file_ext_to in exclude_files:
                files.append(file)

        return files
