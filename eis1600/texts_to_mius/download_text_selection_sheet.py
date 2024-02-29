from sys import exit
from os.path import isfile
from urllib import request
from urllib.error import URLError


def download_text_selection(text_repo: str) -> str:
    """Download the Google Sheet which keeps tracks of prepared texts.

    :param text_repo: TEXT_REPO cannot be import due to circular import, hence as param.
    :return str: return path to the downloaded CSV file.
    """
    csv_path = text_repo + '_EIS1600 - Text Selection - Serial Source Test - EIS1600_AutomaticSelectionForReview.csv'
    print(
            'Download latest version of "_EIS1600 - Text Selection - Serial Source Test - '
            'EIS1600_AutomaticSelectionForReview" from Google Spreadsheets'
    )
    latest_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR60MrlXJjtrd3bid1CR3xK5Pv" \
                 "-aUz1qWEfHfowU1DPsh6RZBvbtW2mA-83drzboIS1fxZdsDO-ny0r/pub?gid=2075964223&single=true&output=csv"
    request.urlcleanup()
    try:
        response = request.urlopen(latest_csv)
    except URLError:
        print('Could not download latest version, fall back to locally saved version')
        if isfile(csv_path):
            return csv_path
        else:
            print(f'There is no local version of that file, please download it manually and save it here:\n{csv_path}')
            exit()
    else:
        lines = [line.decode('utf-8') for line in response.readlines()]
        with open(csv_path, 'w', encoding='utf-8') as csv_fh:
            csv_fh.writelines(lines)

        print('Saved as csv in ' + text_repo + '\n')

        return csv_path
