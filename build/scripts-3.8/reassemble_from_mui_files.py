import sys
import os
import argparse

from eis1600.mui_handling import reassembling


if __name__ == "__main__":
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

    print('Done')
