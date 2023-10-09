from argparse import ArgumentParser, RawDescriptionHelpFormatter
from sys import argv
from glob import glob
from re import compile

from eis1600.processing.postprocessing import reconstruct_miu_text_with_tags
from p_tqdm import p_uimap
from openiti.helper.ara import denormalize

from eis1600.helper.repo import TRAINING_DATA_REPO
from eis1600.processing.preprocessing import get_tokens_and_tags, get_yml_and_miu_df

place_terms = ['كورة', 'كور', 'قرية', 'قرى', 'مدينة', 'مدن', 'ناحية', 'نواح', 'نواحي', 'محلة', 'محلات', 'بلد', 'بلاد', 'ربع', 'ارباع', 'رستاق', 'رساتيق', 'أعمال']
plr_pt = ['كور', 'قرى', 'بلاد', 'أعمال']
dn_pt = [denormalize(t) for t in place_terms]
plr_dn_pt = [denormalize(t) for t in plr_pt]

PLACES_REGEX_W_MIN = compile(r'من (?:' + '|'.join(plr_dn_pt) + r')')
PLACES_REGEX = compile(r'\\b(?:' + '|'.join(dn_pt) + r')\\b')


def annotate_miu(file: str) -> str:
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object)

    text = ' '.join(df['TOKENS'].loc[df['TOKENS'].notna()].to_list())
    text_updated = text

    if PLACES_REGEX.search(text_updated):
        outpath = file.replace('5k_gold_standard', 'topo_descriptions')

        m = PLACES_REGEX.search(text_updated)
        while m:
            start = m.start()
            end = m.end()
            text_updated = text_updated[:start] + ' BTOPD ' + text_updated[start:end] + ' ETOPD ' + text_updated[end:]
            m = PLACES_REGEX.search(text_updated, end + 14)

        ar_tokens, tags = get_tokens_and_tags(text_updated)
        df.loc[df['TOKENS'].notna(), 'TAGS_LISTS'] = tags

        yml_handler.unset_reviewed()
        updated_text = reconstruct_miu_text_with_tags(df[['SECTIONS', 'TOKENS', 'TAGS_LISTS']])

        with open(outpath, 'w', encoding='utf-8') as ofh:
            ofh.write(str(yml_handler) + updated_text)

    if PLACES_REGEX_W_MIN.search(text_updated):
        outpath = file.replace('5k_gold_standard', 'topo_descriptions_w_min')

        m = PLACES_REGEX_W_MIN.search(text_updated)
        while m:
            start = m.start()
            end = m.end()
            text_updated = text_updated[:start] + ' BTOPD ' + text_updated[start:end] + ' ETOPD ' + text_updated[end:]
            m = PLACES_REGEX_W_MIN.search(text_updated, end + 15)

        ar_tokens, tags = get_tokens_and_tags(text_updated)
        df.loc[df['TOKENS'].notna(), 'TAGS_LISTS'] = tags

        yml_handler.unset_reviewed()
        updated_text = reconstruct_miu_text_with_tags(df[['SECTIONS', 'TOKENS', 'TAGS_LISTS']])

        with open(outpath, 'w', encoding='utf-8') as ofh:
            ofh.write(str(yml_handler) + updated_text)

    return file


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to annotate onomastic information in gold-standard MIUs.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')

    args = arg_parser.parse_args()
    debug = args.debug

    infiles = glob(TRAINING_DATA_REPO + '5k_gold_standard/*.EIS1600')

    res = []
    if debug:
        for i, file in enumerate(infiles):
            print(i, file)
            res.append(annotate_miu(file))
    else:
        res += p_uimap(annotate_miu, infiles)

    print('Done')
