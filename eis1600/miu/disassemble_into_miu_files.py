import sys
import os
from argparse import ArgumentParser, Action, RawDescriptionHelpFormatter
from multiprocessing import Pool

from eis1600.helper.repo import get_path_to_other_repo, read_files_from_readme, get_files_from_eis1600_dir, \
    write_to_readme
from eis1600.miu.methods import disassemble_text


class CheckFileEndingAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and os.path.isfile(input_arg):
            filepath, fileext = os.path.splitext(input_arg)
            if fileext != '.EIS1600':
                parser.error('You need to input a EIS1600 file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, None)


def main():
    arg_parser = ArgumentParser(
            prog=sys.argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to disassemble EIS1600 file(s) into MIU file(s).
-----
Give a single EIS1600 file as input
or 
Use -e <EIS1600_repo> to batch process all EIS1600 files in the EIS1600 directory.
'''
    )
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument(
            '-e', '--eis1600_repo', type=str,
            help='Takes a path to the EIS1600 file repo and batch processes all files'
    )
    arg_parser.add_argument(
            'input', type=str, nargs='?',
            help='EIS1600 file to process',
            action=CheckFileEndingAction
    )
    args = arg_parser.parse_args()

    verbose = args.verbose

    if args.input:
        infile = './' + args.input
        out_path = get_path_to_other_repo(infile, 'MIU')
        print(f'Disassemble {infile}')
        disassemble_text(infile, out_path, verbose)
        infiles = [infile.split('/')[-1]]
        path = out_path.split('data')[0]
        write_to_readme(path, infiles, '# Texts disassembled into MIU files\n')
    elif args.eis1600_repo:
        input_dir = args.eis1600_repo
        if not input_dir[-1] == '/':
            input_dir += '/'
        out_path = get_path_to_other_repo(input_dir, 'MIU')

        print(f'Disassemble EIS1600 files from the EIS1600 repo')
        files_list = read_files_from_readme(input_dir, '# Texts converted into `.EIS1600`\n')
        files_list_done = read_files_from_readme(input_dir, '# Texts disassembled into MIU files\n')
        files_list = [file for file in files_list if file not in files_list_done]
        infiles = get_files_from_eis1600_dir(input_dir, files_list, 'EIS1600')
        if not infiles:
            print('There are no EIS1600 files to process')
            sys.exit()

        params = [(infile, out_path, verbose) for infile in infiles]

        with Pool() as p:
            p.starmap_async(disassemble_text, params).get()

        write_to_readme(out_path, infiles, '# Texts disassembled into MIU files\n')
    else:
        print(
                'Pass in a <uri.EIS1600> file to process a single file or use the -e option for batch processing'
        )
        sys.exit()

    print('Done')
