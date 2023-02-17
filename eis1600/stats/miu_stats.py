from collections import Counter
from functools import partial

import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from p_tqdm import p_uimap

from eis1600.stats.methods import extract_categories
from eis1600.helper.repo import read_files_from_readme, get_files_from_eis1600_dir


def main():
    arg_parser = ArgumentParser(
            prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to generate statistics on MIU files.'''
    )
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    args = arg_parser.parse_args()

    verbose = args.verbose

    input_dir = './'

    print(f'Statistics on MIUs')
    files_list = read_files_from_readme(input_dir, '# Texts disassembled into MIU files\n')

    infiles = get_files_from_eis1600_dir(input_dir, files_list, 'YAMLDATA.yml')
    if not infiles:
        print('There are no YAMLDATA files to process')
        sys.exit()

    counter_categories = Counter()
    counter_reviewers = Counter()

    res = []
    res += p_uimap(partial(extract_categories, verbose=verbose), infiles)
    categories = [cat for cats, revs in res for cat in cats]
    reviewers = [rev for cats, revs in res for rev in revs]
    counter_categories.update(categories)
    counter_reviewers.update(reviewers)

    with open('STATS.md', 'w', encoding='utf-8') as stats_fh:
        stats_fh.write('# Stats\n\n')
        stats_fh.write('## Categories\n\n')

        for key, val in counter_categories.items():
            line = key + '  : ' + str(val) + '\n'
            stats_fh.write(line)
        stats_fh.write('\ntotal    : ' + str(sum(counter_categories.values())) + '\n\n')

        stats_fh.write('## Reviewers\n\n')

        for key, val in counter_reviewers.items():
            line = key + '  : ' + str(val) + '\n'
            stats_fh.write(line)
        stats_fh.write('\ntotal    : ' + str(sum(counter_reviewers.values())) + '\n\n')

    print('Done')
