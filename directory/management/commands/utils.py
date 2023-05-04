import csv
import pandas as pd
import openpyxl
from textblob import TextBlob

from django.core.mail import BadHeaderError, send_mail, EmailMessage

from django.http import HttpResponse, HttpResponseRedirect
from ...constants import EMAIL_HOST_USER


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
        df.rename(columns={df.columns[i]: column.lower()}, inplace=True)
        i += 1
    print(df.columns)
    return clean_excel_data(df)


def sanitized(word):
    return TextBlob(word.strip().lower()).correct()

def send_email(subject, message, file, recipient):
    msg = EmailMessage(subject, message, EMAIL_HOST_USER, [recipient])
    msg.content_subtype = "html"
    msg.attach_file(file)
    msg.send()
