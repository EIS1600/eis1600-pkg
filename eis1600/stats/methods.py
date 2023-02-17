from os.path import split

from typing import List, Optional, Tuple


def extract_categories(infile: str, verbose: Optional[bool] = None) -> Tuple[List[str], List[str]]:
    path, uri = split(infile)
    uri, ext = uri.split('.YAMLDATA.yml')

    if verbose:
        print(f'Check {uri}')
        print(infile)

    with open(infile, 'r', encoding='utf-8') as yml_data_fh:
        content = yml_data_fh.read()

    mius = content.split('#MIU#Header#End#')
    categories = []
    reviewers = []

    for miu in mius:
        cat = [line.lstrip('category   : ').strip('"') for line in miu.split('\n') if line.startswith('category')]
        categories.extend(cat)
        rev = [line.lstrip('reviewer   : ').strip('"') for line in miu.split('\n') if line.startswith('reviewer')]
        reviewers.extend(rev)

    return categories, reviewers
