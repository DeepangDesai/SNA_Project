import pandas as pd
from difflib import SequenceMatcher


def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def to_1D(series):
    return pd.Series([x for _list in series for x in _list])


def frequency(df):
    hash_dict = {}
    hash_dict = to_1D(df["hashtags"]).value_counts()
    return hash_dict
