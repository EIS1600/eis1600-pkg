from sys import argv
from tqdm import tqdm
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from eis1600.corpus_analysis.analyse_all_on_cluster import routine_per_text
from eis1600.helper.CheckFileEndingActions import CheckFileEndingEIS1600TextAction
from eis1600.repositories.repo import get_all_part_files
from eis1600.helper.part_file_names import get_part_number
from eis1600.json_to_tsv.corpus_dump import dump_file


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to re-annotated files from the online-editor.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')
    arg_parser.add_argument('-P', '--parallel', action='store_true')
    arg_parser.add_argument(
        '--parts', action='store_true',
        help="process all related part files if any"
    )
    arg_parser.add_argument(
            'input', type=str,
            help='EIS1600 text file to annotate.',
            action=CheckFileEndingEIS1600TextAction
    )
    arg_parser.add_argument(
        '--no_tsv',
        action='store_true',
        help='do not make tsv conversion'
    )
    args = arg_parser.parse_args()

    if args.parts:
        for infile in tqdm(sorted(get_all_part_files(args.input), key=get_part_number)):
            if args.debug:
                print(f"** {infile}")
            routine_per_text(infile, parallel=args.parallel, force=True, debug=args.debug)
            if not args.no_tsv:
                dump_file(infile)
    else:
        routine_per_text(args.input, parallel=args.parallel, force=True, debug=args.debug)
        if not args.no_tsv:
            dump_file(args.input)
