from urllib import request


def download_text_selection(text_repo: str) -> str:
    """Download the Google Sheet which keeps tracks of prepared texts.

    :param text_repo: TEXT_REPO cannot be import due to circular import, hence as param.
    :return str: return path to the downloaded CSV file.
    """
    print(
            'Download latest version of "_EIS1600 - Text Selection - Serial Source Test - '
            'EIS1600_AutomaticSelectionForReview" from Google Spreadsheets'
    )
    latest_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR60MrlXJjtrd3bid1CR3xK5Pv" \
                 "-aUz1qWEfHfowU1DPsh6RZBvbtW2mA-83drzboIS1fxZdsDO-ny0r/pub?gid=2075964223&single=true&output=csv"
    request.urlcleanup()
    response = request.urlopen(latest_csv)
    lines = [line.decode('utf-8') for line in response.readlines()]
    csv_path = text_repo + '_EIS1600 - Text Selection - Serial Source Test - ' \
                           'EIS1600_AutomaticSelectionForReview.csv'
    with open(csv_path, 'w', encoding='utf-8') as csv_fh:
        csv_fh.writelines(lines)

    print('Saved as csv in ' + text_repo + '\n')

    return csv_path
