from pathlib import Path

import pandas as pd

from .geo_utils import air_distance_km, get_coordinates
from .meta import MetaSearch, MetaSearchResult, MetaTable
from .retrieve_data_from_dwd_cdc import main as retrieve_data

RETRIEVE_DATA: bool = False
META_ANALYSIS: bool = True


def run_meta_analysis() -> None:
    """Run meta analysis."""
    data_path = Path.cwd() / "data" / "cdc" / "raw"
    meta_table = MetaTable(data_path=data_path)
    # print(f"{meta_table._df_product.head()=}")
    # print(f"{meta_table._df_stations.head()=}")
    print(f"{meta_table.table.head()=}")
    meta_table.export(suffix="json")
    meta_table.export(suffix="xlsx")

    search_param = MetaSearch(
        measurand_names=["solar radiation"],
        to_date=pd.Timestamp(year=2000, month=1, day=1),
        stations_id=[4466],
    )
    # Search meta table with search parameters
    search_result: MetaSearchResult = meta_table.search(search_param=search_param)

    # access search results
    print(f"{search_result.paths=}")
    print(f"{search_result.length=}")

    # Example: find the nearest station by German address
    address = {
        "street": "Rathausplatz",
        "house_number": "1",
        "zip_code": "24103",
        "city": "Kiel",
    }
    station_id = meta_table.get_nearest_station_id_by_address(**address)
    print(f"Nearest station id for Kiel address: {station_id}")


def main() -> None:
    """Main function."""
    if RETRIEVE_DATA:
        retrieve_data()

    if META_ANALYSIS:
        run_meta_analysis()


if __name__ == "__main__":
    main()
