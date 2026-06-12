import pandas as pd
import pytest

from simultaneousness_analysis.meta.search import MetaNearestStationResult
import simultaneousness_analysis.meta.table as table_mod
from simultaneousness_analysis.meta.table import MetaTable


def _sample_table():
    # Small in-memory stations table using Schleswig-Holstein coordinates.
    return pd.DataFrame(
        {
            "stations_id": [1, 2, 3],
            "latitude": [54.5589, 54.3233, 53.8655],
            "longitude": [9.3917, 10.1228, 10.6866],
        },
    )


def test_get_nearest_by_coordinates():
    """Selects the nearest station by explicit coordinates."""
    # Create a MetaTable-like object without running initialization I/O.
    mt = object.__new__(MetaTable)
    mt.table = _sample_table()

    # Coordinates chosen near Kiel -> expect the nearest station to be station 2.
    station = mt.get_nearest_station_id_by_coordinates(54.32, 10.12)
    assert station == MetaNearestStationResult(
        stations_id=2,
        distance_km=pytest.approx(0.41, abs=0.05),
    )


def test_get_nearest_by_address(monkeypatch):
    """Delegates to get_coordinates and returns the same nearest station."""
    mt = object.__new__(MetaTable)
    mt.table = _sample_table()

    # Mock get_coordinates to return Kiel coordinates near station 2 so no network call.
    def fake_get_coordinates(*args, **kwargs):
        return (54.3233, 10.1228)

    monkeypatch.setattr(table_mod, "get_coordinates", fake_get_coordinates)

    # The address lookup should delegate to the coordinates-based lookup.
    station = mt.get_nearest_station_id_by_address(
        "Rathausplatz",
        "1",
        "24103",
        "Kiel",
    )
    assert station == MetaNearestStationResult(
        stations_id=2,
        distance_km=pytest.approx(0.0, abs=1e-6),
    )
