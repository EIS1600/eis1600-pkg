from argparse import ArgumentParser, RawDescriptionHelpFormatter
from sys import argv
from glob import iglob

from dask.dataframe import from_pandas
from pandas import concat, DataFrame, read_csv

from eis1600.helper.repo import MIU_REPO, TOPO_REPO
from eis1600.helper.topod_extract_incomplete import PLACES_REGEX, TT_REGEX
from eis1600.processing.preprocessing import get_yml_and_miu_df, get_tokens_and_tags
from eis1600.processing.postprocessing import merge_tagslists, reconstruct_miu_text_with_tags


def annotated_to_miu(row):
    infile = row['infile']
    outfile = TOPO_REPO + 'MIUs/' + row['MIU'] + '.EIS1600'
    with open(infile, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object)

    text = ' '.join(df['TOKENS'].loc[df['TOKENS'].notna()].to_list())
    for phrase in row['MODIFIABLE']:
        p = phrase.strip()
        tag = 'TPD' + str(len(p.split())) + ' '
        text = text.replace(p, tag + p)

    tokens, tags = get_tokens_and_tags(text)

    df.loc[df['TOKENS'].notna(), 'TPD_TAGS'] = tags
    df['TAGS_LISTS'] = df.apply(lambda x: merge_tagslists(x['TAGS_LISTS'], x['TPD_TAGS']), axis=1)

    updated_text = reconstruct_miu_text_with_tags(df[['SECTIONS', 'TOKENS', 'TAGS_LISTS']])

    yml_handler.set_reviewed('HRH')

    with open(outfile, 'w', encoding='utf-8') as outfile_h:
        outfile_h.write(str(yml_handler) + updated_text)


def annotate_without_status(row):
    infile = row['infile']
    outfile = '../../' + TOPO_REPO + 'MIUs/' + row['MIU'] + '.EIS1600'
    with open(infile, 'r', encoding='utf-8') as miu_file_object:
        yml_handler, df = get_yml_and_miu_df(miu_file_object)

    text = ' '.join(df['TOKENS'].loc[df['TOKENS'].notna()].to_list())
    text_updated = text

    if PLACES_REGEX.search(text_updated):
        m = PLACES_REGEX.search(text_updated)
        while m:
            start = m.start()
            end = m.end()
            if len(TT_REGEX.findall(m.group(0))) >= 3:
                p = m.group(0).strip()
                tag = 'TPD' + str(len(p.split())) + ' '
                text_updated = text_updated.replace(p, tag + p)
                m = PLACES_REGEX.search(text_updated, end + len(tag))
            else:
                m = PLACES_REGEX.search(text_updated, end)

    tokens, tags = get_tokens_and_tags(text_updated)

    df.loc[df['TOKENS'].notna(), 'TPD_TAGS'] = tags
    df['TAGS_LISTS'] = df.apply(lambda x: merge_tagslists(x['TAGS_LISTS'], x['TPD_TAGS']), axis=1)

    updated_text = reconstruct_miu_text_with_tags(df[['SECTIONS', 'TOKENS', 'TAGS_LISTS']])

    with open(outfile, 'w', encoding='utf-8') as outfile_h:
        outfile_h.write(str(yml_handler) + updated_text)


def get_infile_path(miu: str) -> str:
    author, text, version, uid = miu.split('.')
    return MIU_REPO + 'data/' + '/'.join([author, '.'.join([author, text])]) + '/MIUs/' + miu + '.EIS1600'


def main():
    arg_parser = ArgumentParser(
            prog=argv[0], formatter_class=RawDescriptionHelpFormatter,
            description='''Script to annotate onomastic information in gold-standard MIUs.'''
    )
    arg_parser.add_argument('-D', '--debug', action='store_true')

    args = arg_parser.parse_args()
    debug = args.debug

    sheets = iglob(TOPO_REPO + 'sheet_[0-9].csv')
    sheets_df = DataFrame(None, columns=['MIU', 'ORIGINAL', 'MODIFIABLE', 'STATUS'])

    for sheet in sheets:
        tmp = read_csv(sheet)
        sheets_df = concat([sheets_df, tmp])

    sheets_df['STATUS'].loc[sheets_df['STATUS'].str.fullmatch('TOPOPONYM')] = 'TOPONYM'
    entries = sheets_df.loc[sheets_df['STATUS'].str.fullmatch('TOPONYM|NISBA|CORRECT')]
    df_by_files = DataFrame(entries.groupby('MIU')['MODIFIABLE'].apply(list)).reset_index()
    infiles = [get_infile_path(miu) for miu in df_by_files['MIU'].to_list()]

    df_by_files['infile'] = infiles
    # df_by_files.apply(annotated_to_miu, axis=1)

    ddf = from_pandas(df_by_files, npartitions=10)
    ddf.apply(annotated_to_miu, axis=1, meta=ddf).compute()

    entries = sheets_df.loc[sheets_df['STATUS'].isna()]
    df_by_files = DataFrame(entries.groupby('MIU')['MODIFIABLE'].apply(list)).reset_index()
    infiles = [get_infile_path(miu) for miu in df_by_files['MIU'].to_list()]

    df_by_files['infile'] = infiles
    # df_by_files.apply(annotate_without_status, axis=1)

    ddf = from_pandas(df_by_files, npartitions=10)
    ddf.apply(annotate_without_status, axis=1, meta=ddf).compute()

    print('Done')
