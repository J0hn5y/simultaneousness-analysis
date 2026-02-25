from typing import Protocol

import pandas as pd


class DataFrameFilter(Protocol):
    def __call__(self, df: pd.DataFrame, column: str, value: any) -> pd.DataFrame: ...


def is_in(df: pd.DataFrame, column: str, value: any) -> pd.DataFrame:
    return df[df[column].isin(value)]


def greater_equal(df: pd.DataFrame, column: str, value: any) -> pd.DataFrame:
    return df[df[column] >= value]


def less_equal(df: pd.DataFrame, column: str, value: any) -> pd.DataFrame:
    return df[df[column] <= value]
