import csv
import pandas as pd
import openpyxl


def clean_excel_data(df):
    records = df.to_dict('records')
    return records


def parse_reader(in_file, delimiter: str = '|'):
    """

    :param in_file: input file name
    :param delimiter: default delimiter
    :return: reader object

    """
    df = pd.read_excel(in_file, header=[0, 1])
    df.columns = df.columns.map('_'.join)
    i = 0
    for column in df.columns:
        a = column.replace("\n", " ").split("_")
        column = a[0] if "Unnamed" in a[1] else a[1]
        df.rename(columns={df.columns[i]: column}, inplace=True)
        i += 1
    return clean_excel_data(df)
