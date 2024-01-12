from typing import Dict, Union

from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from re import compile
from datetime import date
from json import dump

from p_tqdm import p_uimap

from eis1600.markdown.markdown_patterns import PAGE_TAG_PATTERN, SPACES_CROWD_PATTERN
from eis1600.processing.preprocessing import get_tokens_and_tags
from eis1600.repositories.repo import TOPO_TRAINING_REPO

DESCRIPTION_PATTERN = compile('BTOPD((?:\n|.)+?)ETOPD')

BIO_DICT = {'B-TOPD': 0, 'I-TOPD': 1}


def to_bio(entry: str) -> Dict:
    tokens, tags = get_tokens_and_tags(entry)
    bio, bio_ids = [], []
    inside = False
    
    for token, tag in zip(tokens, tags):
        if tag == 'BTOPD':
            inside = True
            bio.append('B-TOPD')
            bio_ids.append(0)
        elif tag == 'ETOPD':
            inside = False
            bio.append('O')
            bio_ids.append(2)
        elif inside:
            bio.append('I-TOPD')
            bio_ids.append(1)
        else:
            bio.append('O')
            bio_ids.append(2)

    return {
            "tokens": tokens,
            "ner_tags": bio_ids,
            "ner_classes": bio
    }


def check_if_entry_is_annotated(entry: str) -> Union[Dict, None]:
    if entry.startswith('$DIC_TOP$') and DESCRIPTION_PATTERN.search(entry):
        return to_bio(SPACES_CROWD_PATTERN.sub(' ', PAGE_TAG_PATTERN.sub('', entry[9:].replace('\n', ' '))))
    else:
        return None


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to annotate onomastic information in gold-standard MIUs.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')

    args = arg_parser.parse_args()
    debug = args.debug

    with open('geographical_dictionaries/data/0900IbnCabdMuncimHimyari.RawdMictar.Shamela0001043-ara1.EIS1600TMP') as fh:
        text = fh.read()

    text = text.split('#META#Header#End#')[1]
    entries = text.split('\n\n# ')
    
    with open('geographical_dictionaries/data/0626YaqutHamawi.MucjamBuldan.Shamela0023735-ara1.EIS1600TMP') as fh:
        text = fh.read()

    text = text.split('#META#Header#End#')[1]
    entries.extend(text.split('\n\n# '))

    res = []
    if debug:
        for entry in entries:
            print(entry)
            res.append(check_if_entry_is_annotated(entry))
    else:
        res += p_uimap(check_if_entry_is_annotated, entries)

    with open(
            TOPO_TRAINING_REPO + 'toponyms_description_training_data_' + date.today().isoformat() + '.json',
            'w',
            encoding='utf-8'
    ) as fh:
        dump([r for r in res if r is not None], fh, indent=4, ensure_ascii=False)

    print('Done')



