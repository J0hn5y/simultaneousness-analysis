import pandas as pd
import pytest

from simultaneousness_analysis.meta.column_filter import (
    greater_equal,
    is_in,
    less_equal,
)


@pytest.fixture
def df():
    return pd.DataFrame(
        {
            "A": [1, 2, 3, 4, 5],
            "B": [10, 20, 30, 40, 50],
        },
    )


def test_is_in_filter(df) -> None:
    """Test the is_in filter function."""
    filtered_df = is_in(df, "A", [1, 3])
    assert len(filtered_df) == 2
    assert set(filtered_df["A"]) == {1, 3}


def test_greater_equal_filter(df) -> None:
    """Test the greater_equal filter function."""
    filtered_df = greater_equal(df, "B", 30)
    assert len(filtered_df) == 3
    assert set(filtered_df["B"]) == {30, 40, 50}


def test_less_equal_filter(df) -> None:
    """Test the less_equal filter function."""
    filtered_df = less_equal(df, "A", 3)
    assert len(filtered_df) == 3
    assert set(filtered_df["A"]) == {1, 2, 3}
