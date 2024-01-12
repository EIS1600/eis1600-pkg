from typing import List, Tuple

from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
from glob import glob
from re import compile
from math import floor

from pandas import DataFrame
from p_tqdm import p_uimap
from openiti.helper.ara import denormalize

from eis1600.gazetteers.Spellings import Spellings
from eis1600.gazetteers.Toponyms import Toponyms
from eis1600.markdown.markdown_patterns import WORD
from eis1600.processing.preprocessing import get_yml_and_miu_df
from eis1600.repositories.repo import MIU_REPO, TOPO_REPO

place_terms = ['كورة', 'كور', 'قرية', 'قرى', 'مدينة', 'مدن', 'ناحية', 'نواح', 'نواحي', 'محلة', 'محال', 'محلات', 'بلد',
              'بلاد', 'ارباع', 'رستاق', 'رساتيق', 'أعمال']      #  'ربع'
technical_terms = ['من', 'بين',
                   'نسبة',
                   'يوم', 'يوما',
                   'مرحلة', 'مرحلتان', 'مرحلتين', 'مراحل',
                   'فرسخ', 'فرسخا', 'فراسخ',
                   'ميل', 'ميلا', 'أميال']
dn_pt = [denormalize(t) for t in place_terms]
dn_tt = [denormalize(t) for t in technical_terms]
dn_spelling = Spellings().get_denormalized_list()
dn_toponyms = Toponyms().total()

PLACES_REGEX = compile(r'(?:' + WORD + '(?: [،.():])?){1,7} (?:' + '|'.join(dn_pt) + r')(?:' + WORD + '){1,7}')
TT_REGEX = compile(r'|'.join(dn_pt + dn_tt + dn_spelling + dn_toponyms))


def annotate_miu(file: str) -> List[Tuple[str, str, str]]:
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object)

    miu = Path(file).name.replace('.EIS1600', '')
    write_out = False
    passages = []

    text = ' '.join(df['TOKENS'].loc[df['TOKENS'].notna()].to_list())
    text_updated = text

    if PLACES_REGEX.search(text_updated):
        m = PLACES_REGEX.search(text_updated)
        while m:
            start = m.start()
            end = m.end()
            if len(TT_REGEX.findall(m.group(0))) >= 3:
                write_out = True
                passages.append((miu, m.group(0), m.group(0)))
                text_updated = text_updated[:start] + ' BTOPD' + text_updated[start:end] + ' ETOPD' + text_updated[end:]
                m = PLACES_REGEX.search(text_updated, end + 12)
            else:
                m = PLACES_REGEX.search(text_updated, end)

        # if write_out:
        #     ar_tokens, tags = get_tokens_and_tags(text_updated)
        #     df.loc[df['TOKENS'].notna(), 'TAGS_LISTS'] = [[t] if t else t for t in tags]

        #     yml_handler.unset_reviewed()
        #     updated_text = reconstruct_miu_text_with_tags(df[['SECTIONS', 'TOKENS', 'TAGS_LISTS']])

        #     outpath = TOPO_REPO + 'data/' + miu + '.EIS1600'
        #     with open(outpath, 'w', encoding='utf-8') as ofh:
        #         ofh.write(str(yml_handler) + updated_text)

    return passages


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to annotate onomastic information in gold-standard MIUs.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')

    args = arg_parser.parse_args()
    debug = args.debug

    infiles = glob(MIU_REPO + 'data/*/*/MIUs/*[0-9].EIS1600')

    res = []
    if debug:
        for i, file in enumerate(infiles):
            print(i, file)
            res.append(annotate_miu(file))
    else:
        res += p_uimap(annotate_miu, infiles)

    tuples = []
    [tuples.extend(r) for r in res if r]

    df = DataFrame(tuples, columns=['MIU', 'ORIGINAL', 'MODIFIABLE'])
    df.to_csv(TOPO_REPO + 'topod.csv', index=False)
    c = floor(len(df)/5000)
    i = 0
    while i < c:
        idx = str(i+1)
        while len(idx) < 4:
            idx = str(0) + idx
        df.iloc[i*5000:(i+1)*5000].to_csv(TOPO_REPO + 'topod_' + str(i+1) + '.csv', index=False)
        i += 1
    df.iloc[i*5000:].to_csv(TOPO_REPO + 'topod_' + str(i+1) + '.csv', index=False)

    print('Done')
