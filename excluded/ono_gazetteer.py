import pandas as pd


if __name__ == "__main__":
    df = pd.read_csv('../../OnomasticonArabicum2020/oa2020.csv')
    df['category'].astype('category')

    print(df['category'].unique())

    ism_cats = ['ISM', 'IAB', 'GAD', 'ABG', 'GAG']

    isms = df.loc[df['category'].isin(ism_cats)]

    isms['content'].value_counts().to_csv('../../OnomasticonArabicum2020/oa2020/ism.csv')
