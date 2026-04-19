from pandas import Timestamp
import pytest

from simultaneousness_analysis.meta.search import MetaSearch


def test_meta_search_initialization() -> None:
    """Test basic MetaSearch initialization with default values."""
    search = MetaSearch()
    assert search.measurand_names is None
    assert search.from_date is None
    assert search.to_date is None
    assert search.stations_id is None
    assert search.station_names is None
    assert search.federal_states is None
    assert search.filters is not None


def test_meta_search_with_measurand_names() -> None:
    """Test MetaSearch initialization with measurand names."""
    names = ["air temperature", "solar radiation", "wind speed"]
    search = MetaSearch(measurand_names=names)
    assert search.measurand_names == names


def test_meta_search_with_stations_id() -> None:
    """Test MetaSearch initialization with station IDs."""
    ids = [2907, 2564, 2429]
    search = MetaSearch(stations_id=ids)
    assert search.stations_id == ids


def test_meta_search_with_station_names() -> None:
    """Test MetaSearch initialization with station names."""
    names = ["Flensburg", "Schleswig"]
    search = MetaSearch(station_names=names)
    assert search.station_names == names
    assert search.federal_states is None


def test_meta_search_with_federal_states() -> None:
    """Test MetaSearch initialization with federal states."""
    states = ["Schleswig-Holstein", "Hamburg"]
    search = MetaSearch(federal_states=states)
    assert search.federal_states == states
    assert search.measurand_names is None


def test_meta_search_with_from_date() -> None:
    """Test MetaSearch initialization with from_date."""
    from_date = Timestamp(year=2005, month=11, day=29)
    search = MetaSearch(from_date=from_date)
    assert search.from_date == from_date
    assert isinstance(search.from_date, Timestamp)


def test_meta_search_with_to_date() -> None:
    """Test MetaSearch initialization with to_date."""
    to_date = Timestamp(year=2024, month=9, day=30)
    search = MetaSearch(to_date=to_date)
    assert search.to_date == to_date
    assert isinstance(search.to_date, Timestamp)


def test_meta_search_frozen() -> None:
    """Test that MetaSearch is frozen and immutable."""
    search = MetaSearch(measurand_names=["air temperature"])
    with pytest.raises(AttributeError):
        search.measurand_names = ["wind speed"]


def test_meta_search_all_parameters() -> None:
    """Test MetaSearch with all parameters set."""
    search = MetaSearch(
        measurand_names=["air temperature"],
        stations_id=[1200],
        from_date=Timestamp(year=2000, month=1, day=1),
        to_date=Timestamp(year=2020, month=12, day=31),
        station_names=["Elpersbüttel"],
        federal_states=["Schleswig-Holstein"],
    )
    assert search.measurand_names == ["air temperature"]
    assert search.stations_id == [1200]
    assert search.station_names == ["Elpersbüttel"]
    assert search.federal_states == ["Schleswig-Holstein"]
    assert search.from_date == Timestamp(year=2000, month=1, day=1)
    assert search.to_date == Timestamp(year=2020, month=12, day=31)


def test_meta_search_filters_default() -> None:
    """Test that filters are populated with default values."""
    search = MetaSearch()
    assert isinstance(search.filters, dict)
    assert len(search.filters) > 0
    assert "measurand_names" in search.filters
    assert callable(search.filters["measurand_names"])


def test_meta_search_filters_for_each_attribute() -> None:
    """Test that there is a filter for each attribute."""
    search = MetaSearch()
    for attr in search.__dataclass_fields__:
        if attr == "filters":
            continue
        assert attr in search.filters
        assert callable(search.filters[attr])
