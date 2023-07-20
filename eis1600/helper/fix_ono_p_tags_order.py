from glob import glob
from os.path import isfile, splitext
from sys import argv
from argparse import Action, ArgumentParser, RawDescriptionHelpFormatter
from p_tqdm import p_uimap
from re import compile

from eis1600.processing.preprocessing import get_yml_and_miu_df
from eis1600.processing.postprocessing import write_updated_miu_to_file
from eis1600.helper.markdown_patterns import onom_tags
from eis1600.helper.repo import TRAINING_DATA_REPO

PATTERN = compile(r'(ÜP\d+[A-Z]),((?:BONOM,)?Ü(?:' + onom_tags + r')\d)')


def fix_ono_o_tag_order(file) -> bool:
    with open(file, 'r+', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object, keep_automatic_tags=True)
        s_notna = df['TAGS_LISTS'].loc[df['TAGS_LISTS'].notna()].apply(lambda tag_list: ','.join(tag_list))
        s_replaced = s_notna.str.replace(PATTERN, lambda m: m.group(2) + ',' + m.group(1))
        s_new = s_replaced.apply(lambda tags_str: tags_str.split(','))
        df.loc[s_replaced.index, 'TAGS_LISTS'] = s_new

        write_updated_miu_to_file(
                miu_file_object, yml_handler, df[['SECTIONS', 'TOKENS', 'TAGS_LISTS']]
        )

    return True


class CheckFileEndingAction(Action):
    def __call__(self, parser, namespace, input_arg, option_string=None):
        if input_arg and isfile(input_arg):
            filepath, fileext = splitext(input_arg)
            if fileext != '.IDs' and fileext != '.EIS1600':
                parser.error('You need to input an IDs file or a single MIU file')
            else:
                setattr(namespace, self.dest, input_arg)
        else:
            setattr(namespace, self.dest, None)


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to generate JSON from MIU YAMLHeaders.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')
    arg_parser.add_argument(
            'input', type=str, nargs='?',
            help='IDs or MIU file to process',
            action=CheckFileEndingAction
    )
    args = arg_parser.parse_args()

    debug = args.debug
    file = args.input

    if file:
        fix_ono_o_tag_order(file)
    else:
        infiles = glob(TRAINING_DATA_REPO + '5k_gold_standard/*.EIS1600')
        res = []

        if debug:
            for i, file in enumerate(infiles[:10]):
                print(f'{i} {file}')
                res.append(fix_ono_o_tag_order(file))
        else:
            res += p_uimap(fix_ono_o_tag_order, infiles)

    print('Done')
