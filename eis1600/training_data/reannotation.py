from glob import glob
from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import List, Union
from re import compile

from eis1600.nlp.annotation_utils import insert_onom_tag, insert_onomastic_tags

from eis1600.markdown.EntityTags import EntityTags

from tqdm import tqdm

from eis1600.helper.CheckFileEndingActions import CheckIsDirAction
from eis1600.processing.postprocessing import write_updated_miu_to_file
from eis1600.processing.preprocessing import get_yml_and_miu_df
from eis1600.training_data.online_editor_files import fix_formatting

OLD_ONOMASTIC_TAGS_PATTERN = compile(r'Ü?(?:' + '|'.join(EntityTags().get_onom_tags()) + ')')
OLD_NER_TAGS_PATTERN = compile(r'Ü?(?:(?:P\d{1,2}[STFCOX]{0,2})|(?:T\d[BDKOPRX]))')


def remove_old_ner_tags(tags_list: Union[None, List[str]]) -> Union[None, List[str]]:
    if tags_list:
        kept_tags_str = OLD_NER_TAGS_PATTERN.sub(','.join(tags_list), '')
        return [t for t in kept_tags_str.split(',') if t]

    return tags_list


def remove_old_tags(tags_list: Union[None, List[str]], which_annotations: List[str]) \
        -> Union[None, List[str]]:
    if tags_list:
        kept_tags_str = ','.join(tags_list)
        if 'NER' in which_annotations:
            kept_tags_str = OLD_NER_TAGS_PATTERN.sub(kept_tags_str, '')
        if 'O' in which_annotations:
            kept_tags_str = OLD_ONOMASTIC_TAGS_PATTERN.sub(kept_tags_str, '')
        if 'P' in which_annotations:
            pass
        if 'T' in which_annotations:
            pass

        return [t for t in kept_tags_str.split(',') if t]

    return tags_list


def reannotation(path: str, which_annotations: List[str]):
    with open(path, 'r+', encoding='utf-8') as miu_file_object:
        # 1. open miu file and disassemble the file to its parts
        yml_handler, df = get_yml_and_miu_df(miu_file_object)
        df['TAGS_LISTS'] = df['TAGS_LISTS'].apply(remove_old_tags, which_annotations=which_annotations)

        if 'NER' in which_annotations:
            df = df
        if 'O' in which_annotations:
            df['ONOM_TAGS'] = insert_onom_tag(df)
            df['ONOMASTIC_TAGS'] = insert_onomastic_tags(df)
        if 'P' in which_annotations:
            df = df
        if 'T' in which_annotations:
            df = df

        write_updated_miu_to_file(
            miu_file_object, yml_handler, df[['SECTIONS', 'TOKENS', 'TAGS_LISTS', 'ONOM_TAGS', 'ONOMASTIC_TAGS']],
            forced_re_annotation=True
        )


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to re-annotated files from the online-editor.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')
    arg_parser.add_argument('-ner', '--NER', action='store_true')
    arg_parser.add_argument('-o', '--onomastics', action='store_true')
    arg_parser.add_argument('-p', '--persons', action='store_true')
    arg_parser.add_argument('-t', '--toponyms', action='store_true')
    arg_parser.add_argument(
            'input', type=str, nargs='1',
            help='Directory which holds the files to process or individual file to annotate',
            action=CheckIsDirAction
    )

    which_annotations = []

    args = arg_parser.parse_args()
    debug = args.debug
    if args.NER:
        which_annotations.append('NER')
    if args.onomastics:
        which_annotations.append('O')
    if args.persons:
        which_annotations.append('P')
    if args.toponyms:
        which_annotations.append('T')

    in_dir = args.input
    if in_dir[-1] != '/':
        in_dir += '/'
    infiles = glob(in_dir + '*.EIS1600')

    x = 0
    for idx, file in tqdm(list(enumerate(infiles))):
        try:
            # Needed for online editor files
            # TODO better this is run while files are exported from DB
            fix_formatting(file)
        except ValueError:
            print(idx + x, file)
        except Exception as e:
            print(idx + x, file)
            print(e)

        reannotation(file, which_annotations)
