from dataclasses import dataclass

from meta.search import MetaSearch


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
