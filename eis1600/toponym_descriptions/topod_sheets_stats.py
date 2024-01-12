from time import time
from requests import get

from pandas import concat, DataFrame, read_csv

from eis1600.repositories.repo import TOPO_REPO


def main():
    sheets = {
        '1': '1vjTQICH_dsJosnhA46Pqbs1ow9CHkptELIiTXDfQS04',
        '2': '1fg56kEs16-_DGdZK2VeR-qtF39U6-qSEQ1p6B5g4zTI',
        '3': '1hThigHwxj1n4mro68eAA4O3wpF2-PuONBmea1x5Yc0o',
        '4': '1lbNzqjdPnonshNU8nVwVTTE7CqCNNhmTpj9CrIXNmYs',
        '5': '12GsdOvkGXWad1v5LUQ9kAyt8ablurFy9wOylcz6SmCY',
        '6': '13cu3OcAMN25VU2X49NYKMoJyPG2CbWFS0LobKSSAwYY',
        '7': '18yBjszyZTZ29c-7Wj7VThPQkJudSxYXSEzJHrZLZxhw',
        '8': '1vxhEZu06BPjbGuljpRXVj60kjsuanvvHfLjVw5Y5tQA',
        '9': '1LtAkJIdujcbEp1qKA31PrpNSIwRryIAuP95BKx-qmNQ',
        'incomplete': '1MPCFunhszG9GNigrGpfebbPE7qdmxQIe6VRF3quIWpE'
    }

    for key, uri in sheets.items():
        start_s = time()
        url = 'https://docs.google.com/spreadsheets/d/' + uri + '/export?format=csv'

        print('Sheet_' + key)
        print(url)

        response = get(url)
        end_s = time()
        print(f'download time: {end_s-start_s}')

        if response.status_code == 200:
            filepath = TOPO_REPO + 'sheet_' + key + '.csv'
            with open(filepath, 'wb') as f:
                f.write(response.content)
        else:
            print(f'Error downloading Google Sheet: {response.status_code}')
            print(f'Sheet_{key} could not be downloaded')

    df = DataFrame(None, columns=['MIU', 'ORIGINAL', 'MODIFIABLE', 'STATUS'])
    for key in sheets.keys():
        tmp = read_csv(TOPO_REPO + 'sheet_' + key + '.csv').dropna()
        df = concat([df, tmp])

    print(df.value_counts(['STATUS']))

    print('Done')
            