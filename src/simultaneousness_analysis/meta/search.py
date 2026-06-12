from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .column_filter import DataFrameFilter, greater_equal, is_in, less_equal

if TYPE_CHECKING:
    from pandas import Timestamp

FILTER_FUNCTIONS: dict[str, DataFrameFilter] = {
    "measurand_names": is_in,
    "from_date": greater_equal,
    "to_date": less_equal,
    "stations_id": is_in,
    "station_names": is_in,
    "federal_states": is_in,
}


@dataclass(frozen=True, kw_only=True)
class MetaSearch:
    """Object containing search parameters and custom filter functions for each parameter."""

    measurand_names: list[str] | None = None
    from_date: Timestamp | None = None
    to_date: Timestamp | None = None
    stations_id: list[int] | None = None
    station_names: list[str] | None = None
    federal_states: list[str] | None = None
    filters: dict[str, callable] = field(
        repr=False,
        init=False,
        default_factory=lambda: FILTER_FUNCTIONS,
    )


@dataclass(frozen=True, kw_only=True)
class MetaSearchResult:
    """Object containing the results of a metadata search and the search parameters used for the search."""

    search: MetaSearch
    paths: list[str] | None = None

    @property
    def length(self) -> int:
        """Returns the number of paths in the search results.

        Returns:
            int: Number of paths in the search results.
        """
        return len(self.paths) if self.paths is not None else 0


@dataclass(frozen=True, kw_only=True)
class MetaNearestStationResult:
    """Nearest station lookup result containing station id and distance."""

    stations_id: int
    distance_km: float
