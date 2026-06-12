from dataclasses import FrozenInstanceError

import pytest

from simultaneousness_analysis.meta.search import MetaSearch, MetaSearchResult


@pytest.fixture
def meta_search():
    return MetaSearch(
        stations_id=[2907],
        federal_states=["Schleswig-Holstein"],
        measurand_names=["air temperature"],
    )


def test_meta_search_result_initialization() -> None:
    """Test basic MetaSearchResult initialization with search argument."""
    result = MetaSearchResult(search=meta_search)
    assert result.search is meta_search
    assert result.paths is None


def test_meta_search_result_missing_search_argument() -> None:
    """Test that MetaSearchResult raises TypeError when no search argument is passed."""
    with pytest.raises(TypeError):
        MetaSearchResult()


def test_meta_search_result_with_non_empty_paths(meta_search) -> None:
    """Test MetaSearchResult with a non-empty paths list."""
    paths = ["file1.txt", "file2.txt"]
    result = MetaSearchResult(search=meta_search, paths=paths)
    assert result.paths == paths
    assert result.length == 2


def test_meta_search_result_with_empty_paths(meta_search) -> None:
    """Test MetaSearchResult with an empty paths list."""
    result = MetaSearchResult(search=meta_search, paths=[])
    assert result.paths == []
    assert result.length == 0


def test_meta_search_result_immutable(meta_search) -> None:
    """Test that MetaSearchResult is immutable (frozen dataclass)."""
    result = MetaSearchResult(search=meta_search, paths=["file1.txt"])
    with pytest.raises(FrozenInstanceError):
        result.paths = ["other.txt"]
