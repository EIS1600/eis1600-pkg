from typing import List, Optional, Tuple

from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
from glob import iglob
from re import compile

from p_tqdm import p_uimap
from pandas import concat, DataFrame, read_csv
from openiti.helper.ara import denormalize

from eis1600.gazetteers.Spellings import Spellings
from eis1600.gazetteers.Toponyms import Toponyms
from markdown.markdown_patterns import WORD, NOISE_ELEMENTS
from repositories.repo import MIU_REPO, TOPO_REPO
from eis1600.processing.preprocessing import get_yml_and_miu_df

place_terms = ['كورة', 'كور', 'قرية', 'قرى', 'مدينة', 'مدن', 'ناحية', 'نواح', 'نواحي', 'محلة', 'محال', 'محلات', 'بلد',
               'بلاد', 'ارباع', 'رستاق', 'رساتيق', 'أعمال']  # 'ربع'
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


PLACES_REGEX = compile(
    r'(?P<context>(?:' + WORD + NOISE_ELEMENTS +
    r'(?P<spelling> [وب]?(?:ال)?(?:' + '|'.join(dn_spelling) + ')(?:ها)?' + NOISE_ELEMENTS + r')*){1,10})'
    r' (?P<place_term>' + '|'.join(dn_pt) + r')(?P<more_context>' + WORD + NOISE_ELEMENTS + r'){1,7}'
    )
TT_REGEX = compile(r'|'.join(dn_pt + dn_tt + dn_spelling + dn_toponyms))


def annotate_miu(file: str, debug: Optional[bool] = False) -> List[Tuple[str, str, str]]:
    with open(file, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object)

    miu = Path(file).name.replace('.EIS1600', '')
    passages = []

    text = ' '.join(df['TOKENS'].loc[df['TOKENS'].notna()].to_list())
    text_updated = text

    if debug:
        print(text)

    if PLACES_REGEX.search(text_updated):
        m = PLACES_REGEX.search(text_updated)
        while m:
            start = m.start()
            end = m.end()
            if debug:
                print(m.group(0))
                print('Context :', m.group('context'))
                print('Place Term: ', m.group('place_term'))
            if len(TT_REGEX.findall(m.group(0))) >= 3:
                passages.append((miu, m.group(0), m.group(0)))
                text_updated = text_updated[:start] + ' BTOPD' + text_updated[start:end] + ' ETOPD' + text_updated[end:]
                m = PLACES_REGEX.search(text_updated, end + 12)
            else:
                m = PLACES_REGEX.search(text_updated, end)

    return passages


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to annotate onomastic information in gold-standard MIUs.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')
    arg_parser.add_argument(
            'input', type=str, nargs='?',
            help='EIS1600 file to process'
    )

    args = arg_parser.parse_args()
    debug = args.debug

    if args.input:
        author, text, version, uid = args.input.split('.')
        file_path = MIU_REPO + 'data/' + '/'.join([author, '.'.join([author, text])]) + \
                    '/MIUs/' + args.input + '.EIS1600'
        annotate_miu(file_path, debug)
    else:
        sheets = iglob(TOPO_REPO + 'sheet_[0-9].csv')
        sheets_df = DataFrame(None, columns=['MIU', 'ORIGINAL', 'MODIFIABLE', 'STATUS'])

        for sheet in sheets:
            tmp = read_csv(sheet).dropna()
            sheets_df = concat([sheets_df, tmp])

        sheets_df['STATUS'].loc[sheets_df['STATUS'].str.fullmatch('TOPOPONYM')] = 'TOPONYM'
        # entries = sheets_df.loc[sheets_df['STATUS'].str.fullmatch('TOPONYM|NISBA|CORRECT')]
        incomplete_mius = sheets_df.loc[sheets_df['STATUS'].str.fullmatch('INCOMPLETE'), 'MIU'].to_list()

        infiles = []

        for miu in incomplete_mius:
            author, text, version, uid = miu.split('.')
            file_path = MIU_REPO + 'data/' + '/'.join([author, '.'.join([author, text])]) + \
                        '/MIUs/' + miu + '.EIS1600'
            infiles.append(file_path)

        res = []
        if debug:
            for i, file in enumerate(infiles[:20]):
                print(i, file)
                res.append(annotate_miu(file))
        else:
            res += p_uimap(annotate_miu, infiles)

        tuples = []
        [tuples.extend(r) for r in res if r]

        df = DataFrame(tuples, columns=['MIU', 'ORIGINAL', 'MODIFIABLE'])
        df['STATUS'] = None
        df.to_csv(TOPO_REPO + 'topod_incomplete.csv', index=False)

    print('Done')
