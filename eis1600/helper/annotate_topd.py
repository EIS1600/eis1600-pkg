from argparse import ArgumentParser, RawDescriptionHelpFormatter
from sys import argv
from pathlib import Path
from typing import List

from camel_tools.ner import NERecognizer
from p_tqdm import p_uimap

from eis1600.helper.repo import TRAINING_DATA_REPO
from eis1600.processing.preprocessing import get_yml_and_miu_df
from eis1600.processing.postprocessing import reconstruct_miu_text_with_tags


def ner_to_md(toponym_labels: List[str]) -> List[str]:
    md_tags = []
    prev = None
    for label in toponym_labels:
        if label == 'B-TOPD' or prev == 'O' and label == 'I-TOPD':
            md_tags.append(['BTOPD'])
        elif prev == 'I-TOPD' and label == 'O':
            md_tags.append(['ETOPD'])
        else:
            md_tags.append(None)
            
        prev = label
        
    return md_tags            


def annotate_miu(file: str) -> str:
    outpath = file.replace('gold_standard', 'topo_descriptions')
    
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object)

    toponym_labels = NERecognizer('EIS1600_Pretrained_Models/camelbert-ca-toponyms-description/').predict_sentence(df['TOKENS'].fillna('-').to_list())
    if 'B-TOPD' in toponym_labels:
        df['TAGS_LISTS'] = ner_to_md(toponym_labels)
        print(list(zip(toponym_labels, df['TAGS_LISTS'])))
        
        yml_handler.unset_reviewed()
        updated_text = reconstruct_miu_text_with_tags(df[['SECTIONS', 'TOKENS', 'TAGS_LISTS']]) 
        
        with open(outpath, 'w', encoding='utf-8') as ofh:
            ofh.write(str(yml_handler) + updated_text)

    return outpath


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to annotate onomastic information in gold-standard MIUs.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')

    args = arg_parser.parse_args()
    debug = args.debug

    with open(TRAINING_DATA_REPO + 'gold_standard.txt', 'r', encoding='utf-8') as fh:
        files_txt = fh.read().splitlines()

    infiles = [TRAINING_DATA_REPO + 'gold_standard/' + file for file in files_txt if Path(
            TRAINING_DATA_REPO + 'gold_standard/' + file
    ).exists()]

    res = []
    if debug:
        for i, file in enumerate(infiles):
            print(i, file)
            res.append(annotate_miu(file))
    else:
        res += p_uimap(annotate_miu, infiles)

    print('Done')
