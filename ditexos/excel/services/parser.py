import pandas as pd


def get_columns(file):
    df = pd.read_excel(file)
    columns = df.columns.tolist()
    return columns
