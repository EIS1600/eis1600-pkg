from bs4 import BeautifulSoup
import pandas as pd
from glob import glob
from p_tqdm import p_uimap


def get_entry(file):
    with open(file, 'r') as fh:
        html = fh.read()
        id = fh.name.split('/')[-1]

    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    categories = [elem.get_text(strip=True) for elem in table.find_all('td', 'category')]
    contents = [elem.get_text(strip=True) for elem in table.find_all('td', 'contents')]
    comments = [elem.get_text(strip=True) for elem in table.find_all('td', 'comments')]

    rows = []
    for cat, con, com in zip(categories, contents, comments):
        rows.append((id, cat, con, com))

    return rows


if __name__ == "__main__":
    files = glob('../../OnomasticonArabicum2020/scraped_data/*')

    res = []
    res += p_uimap(get_entry, files)

    data = [tpl for rows in res for tpl in rows]
    df = pd.DataFrame(data, columns=['id', 'category', 'content', 'comment'])

    df.to_csv('../../OnomasticonArabicum2020/oa2020/oa2020.tsv', sep='\t', index=False)
    df.to_csv('../../OnomasticonArabicum2020/oa2020/oa2020.csv', index=False)
