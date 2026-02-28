from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .config import FILTER_FUNCTIONS

if TYPE_CHECKING:
    from pandas import Timestamp


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
