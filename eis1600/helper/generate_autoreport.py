from sys import exit
from requests import get

from pandas import read_csv

from eis1600.helper.repo import TEXT_REPO


def main():
    key = '1Rg4FHMy36nDJZ_BTRTOUtO9Uhv30FtPZ4lGjXvju-28'
    url = 'https://docs.google.com/spreadsheets/d/' + key + '/export?format=csv'
    response = get(url)

    filepath = TEXT_REPO + 'sheet_' + key + '.csv'

    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            f.write(response.content)
    else:
        print(f'Error downloading Google Sheet: {response.status_code}')
        print(f'Sheet_{key} could not be downloaded')
        exit()

    df = read_csv(filepath, usecols=['Book Title', 'PREPARED'])
    df_ready = df.loc[df['PREPARED'].str.fullmatch('ready')]
    df_double_checked = df.loc[df['PREPARED'].str.fullmatch('double-checked')]

    print(len(df_ready))
    print(len(df_double_checked))

