from pathlib import Path

import pandas as pd

from simultaneousness_analysis.meta import MetaSearch, MetaSearchResult, MetaTable
from simultaneousness_analysis.retrieve_data_from_dwd_cdc import main as retrieve_data

RETRIEVE_DATA: bool = False
META_ANALYSIS: bool = True


def run_meta_analysis() -> MetaTable:
    """Run meta analysis from an external script entrypoint.

    Returns:
        MetaTable: Loaded and exported metadata table.
    """
    data_path = Path.cwd() / "data" / "cdc" / "raw"
    meta_table = MetaTable(data_path=data_path)
    print(f"{meta_table.table.head()=}")
    meta_table.export(suffix="json")
    meta_table.export(suffix="xlsx")
    return meta_table


def run_search(meta_table: MetaTable) -> None:
    """Search meta table for solar radiation data.

    Args:
        meta_table: MetaTable instance to search.
    """
    search_param = MetaSearch(
        measurand_names=["solar radiation"],
        to_date=pd.Timestamp(year=2000, month=1, day=1),
        stations_id=[4466],
    )

    search_result: MetaSearchResult = meta_table.search(search_param=search_param)
    print(f"{search_result.paths=}")
    print(f"{search_result.length=}")


def run_nearest_station_search(meta_table: MetaTable) -> None:
    """Find and display nearest weather station by address.

    Args:
        meta_table: MetaTable instance to query.
    """
    address = {
        "street": "Rathausplatz",
        "house_number": "1",
        "zip_code": "24103",
        "city": "Kiel",
    }
    nearest_station = meta_table.get_nearest_station_id_by_address(**address)
    print(
        f"Nearest station for Kiel address: {nearest_station.stations_id} "
        f"({nearest_station.distance_km:.2f} km)",
    )
    station_info = meta_table.get_station_info(nearest_station.stations_id)
    print(
        f"Nearest station for Kiel address in {nearest_station.distance_km:.2f} km: {station_info}",
    )


def main() -> None:
    """Execute full analysis pipeline with optional data retrieval."""
    if RETRIEVE_DATA:
        retrieve_data()
    if META_ANALYSIS:
        meta_table = run_meta_analysis()
        run_search(meta_table)
        run_nearest_station_search(meta_table)


if __name__ == "__main__":
    main()
