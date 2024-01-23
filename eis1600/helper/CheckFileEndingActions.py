from argparse import Action
from os.path import isdir, isfile, splitext


class CheckFileEndingMARKdownAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and isfile(input_arg):
            filepath, fileext = splitext(input_arg)
            if fileext not in ['.mARkdown', '.inProgess', '.completed']:
                parser.error('You need to input a mARkdown file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, None)


class CheckFileEndingEIS1600MIUAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and isfile(input_arg):
            filepath, fileext = splitext(input_arg)
            if fileext != '.EIS1600' and filepath[-1:-12].isdigit():
                parser.error('Input must be a single MIU file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, None)


class CheckFileEndingEIS1600TextAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and isfile(input_arg):
            filepath, fileext = splitext(input_arg)
            if fileext != '.EIS1600' and not filepath[-1:-12].isdigit():
                parser.error('Input must be a single MIU file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, None)


class CheckFileEndingEIS1600OrEIS1600TMPAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and isfile(input_arg):
            filepath, fileext = splitext(input_arg)
            if not fileext.startswith('.EIS1600'):
                parser.error('You need to input an EIS1600 or EIS1600TMP file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, None)


class CheckFileEndingEIS1600OrIDsAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and isfile(input_arg):
            filepath, fileext = splitext(input_arg)
            if fileext != '.IDs' and fileext != '.EIS1600':
                parser.error('You need to input an IDs file or a single MIU file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, None)


class CheckIsDirAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        input_arg = input_arg[0]
        if input_arg and isdir(input_arg):
            setattr(namespace, self.dest, input_arg)
        else:
            print('You need to specify a valid path to the directory holding the files which have been annotated')
            raise IOError
