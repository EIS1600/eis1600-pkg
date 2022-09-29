import sys
import os

from eis1600.miu_handling import reassembling


if __name__ == "__main__":
    try:
        infile_name = sys.argv[1]
    except IndexError:
        print('Pass in a <uri.EIS1600> file to begin')
        sys.exit()

    path, uri = os.path.split(infile_name)
    uri, ext = os.path.splitext(uri)
    print(f'Reassemble {uri + ext} from MUI files')
    reassembling.reassemble_text('.' + path + '/' + uri, uri)

    print('Done')
