from pathlib import Path

from meta import MetaSearch, MetaSearchResult, MetaTable
import pandas as pd


def main() -> None:
    """Runs the meta analysis.

    Runs the meta analysis by creating a meta table,
    defining search parameters, searching the meta table
    with the search parameters and accessing the search results.
    """
    data_path = Path.cwd() / "data" / "cdc" / "raw"
    meta_table = MetaTable(data_path=data_path)
    # print(f"{meta_table._df_product.head()=}")
    # print(f"{meta_table._df_stations.head()=}")
    print(f"{meta_table.table.head()=}")

    # Define search parameters
    # search_param = MetaSearch(
    #     measurand_names=["solar radiation"],
    #     from_date=pd.Timestamp(year=2020, month=1, day=1),
    #     station_ids=[1200, 2961],
    # )

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


if __name__ == "__main__":
    main()
