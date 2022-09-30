import sys
import os
import argparse

from eis1600.miu_handling import reassembling


if __name__ == "__main__":
<<<<<<<< HEAD:build/scripts-3.8/reassemble_from_mui_files.py
    try:
        infile_name = sys.argv[1]
    except IndexError:
        print('Pass in a <uri.EIS1600> file to begin')
        sys.exit()

    path, uri = os.path.split(infile_name)
    uri, ext = os.path.splitext(uri)
    print(f'Reassemble {uri + ext} from MUI files')
    reassembling.reassemble_text('.' + path + '/' + uri, uri)
========
    argparser = argparse.ArgumentParser(prog=sys.argv[0])
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('infilename', type=str, help='text to process')
    args = argparser.parse_args()
    if args.infilename:
        infilename = args.infilename
    else:
        print('Pass in a <uri.EIS1600> filename to begin')
        sys.exit()

    verbose = args.verbose
    if verbose:
        print(f'verbose')

    path, uri = os.path.split(infilename)
    uri, ext = os.path.splitext(uri)
    print(f'Reassemble {uri + ext} from MUI files')
    reassembling.reassemble_text('.' + path + '/' + uri, uri, verbose)
>>>>>>>> main:eis1600/bin/reassemble_from_mui_files.py

    print('Done')
