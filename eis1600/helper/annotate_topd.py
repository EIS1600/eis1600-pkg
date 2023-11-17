from argparse import ArgumentParser, RawDescriptionHelpFormatter
from glob import glob
from os.path import split
from sys import argv

from p_tqdm import p_uimap
from tqdm import tqdm

from eis1600.helper.repo import MIU_REPO, TOPO_REPO
from eis1600.markdown.md_to_bio import bio_to_md
from eis1600.models.ToponymDescriptionModel import ToponymDescriptionModel
from eis1600.processing.preprocessing import get_yml_and_miu_df
from eis1600.processing.postprocessing import merge_tagslists, reconstruct_miu_text_with_tags


def annotate_miu(file: str) -> str:
    outpath = TOPO_REPO + 'data/' + split(file)[1]
    
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object)

    toponym_labels = ToponymDescriptionModel().predict_sentence(df['TOKENS'].fillna('-').to_list())
    if 'B-TOPD' in toponym_labels:
        df['Q'] = bio_to_md(toponym_labels, umlaut_prefix=False)
        df['TAGS_LISTS'] = df.apply(lambda x: merge_tagslists(x['TAGS_LISTS'], x['Q']), axis=1)

        yml_handler.unset_reviewed()
        updated_text = reconstruct_miu_text_with_tags(df[['SECTIONS', 'TOKENS', 'TAGS_LISTS']])

        with open(outpath, 'w', encoding='utf-8') as ofh:
            ofh.write(str(yml_handler) + updated_text)

    return outpath


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to annotate toponym descriptions in MIUs.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')

    args = arg_parser.parse_args()
    debug = args.debug

    infiles = glob(MIU_REPO + 'data/*/*/MIUs/*[0-9].EIS1600')

    res = []
    if debug:
        for i, file in tqdm(list(enumerate(infiles))):
            print(i, file)
            res.append(annotate_miu(file))
    else:
        res += p_uimap(annotate_miu, infiles)

    print('Done')
