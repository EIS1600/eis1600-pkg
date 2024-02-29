from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from eis1600.corpus_analysis.analyse_all_on_cluster import routine_per_text
from eis1600.helper.CheckFileEndingActions import CheckFileEndingEIS1600TextAction


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to re-annotated files from the online-editor.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')
    arg_parser.add_argument('-P', '--parallel', action='store_true')
    arg_parser.add_argument(
            'input', type=str, nargs='?',
            help='EIS1600 text file to annotate.',
            action=CheckFileEndingEIS1600TextAction
    )
    args = arg_parser.parse_args()
    debug = args.debug
    parallel = args.parallel
    infile = args.input

    routine_per_text(infile, parallel, force=True, debug=debug)
