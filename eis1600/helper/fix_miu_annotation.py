import re
from glob import glob
from p_tqdm import p_uimap
from eis1600.preprocessing.methods import get_yml_and_MIU_df, write_updated_miu_to_file


sheikhuna = re.compile('[و]?شيخنا')


def untag_sheikhuna(row):
    if row['TOKENS'] and sheikhuna.match(row['TOKENS']) and row['TAGS_LISTS'] and [tag for tag in row['TAGS_LISTS']
                                                                                   if tag.startswith('P1')]:
        if len(row['TAGS_LISTS']) > 1:
            row['TAGS_LISTS'].pop()
            return row['TAGS_LISTS'], True
        else:
            return None, True
    else:
        return row['TAGS_LISTS'], False


def check_file(file):
    with open(file, 'r+', encoding='utf-8') as fh:
        fh.readline()
        fh.readline()
        if fh.readline() == 'reviewed    : REVIEWED2\n':
            fh.seek(0)
            yml, df = get_yml_and_MIU_df(fh)
            df['TAGS_LISTS'], changed = zip(*df[['TOKENS', 'TAGS_LISTS']].apply(untag_sheikhuna, axis=1))
            if any(changed):
                write_updated_miu_to_file(fh, yml, df)


def main():
    files = glob('*.EIS1600')

    res = []
    res += p_uimap(check_file, files)



