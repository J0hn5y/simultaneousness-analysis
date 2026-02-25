from typing import Protocol

import pandas as pd


class DataFrameFilter(Protocol):
    """Protocol for filter functions that can be applied to a pandas DataFrame."""

    def __call__(self, df: pd.DataFrame, column: str, value: any) -> pd.DataFrame:
        """Calls filter function on DataFrame."""
        ...


def is_in(df: pd.DataFrame, column: str, value: any) -> pd.DataFrame:
    """Filters DataFrame by checking if values in column are in the provided Iterable.

    Args:
        df (pd.DataFrame): The DataFrame to be filtered.
        column (str): The name of the column to be filtered.
        value (any): The value(s) to check for in the column.

    Returns:
        pd.DataFrame: The filtered DataFrame.
    """
    return df[df[column].isin(value)]


def greater_equal(df: pd.DataFrame, column: str, value: any) -> pd.DataFrame:
    """Filters DataFrame by checking if values in column are greater than or equal to the provided value.

    Args:
        df (pd.DataFrame): The DataFrame to be filtered.
        column (str): The name of the column to be filtered.
        value (any): The value to compare against.

    Returns:
        pd.DataFrame: The filtered DataFrame.
    """
    return df[df[column] >= value]


def less_equal(df: pd.DataFrame, column: str, value: any) -> pd.DataFrame:
    """Filters DataFrame by checking if values in column are less than or equal to the provided value.

    Args:
        df (pd.DataFrame): The DataFrame to be filtered.
        column (str): The name of the column to be filtered.
        value (any): The value to compare against.

    Returns:
        pd.DataFrame: The filtered DataFrame.
    """
    return df[df[column] <= value]
