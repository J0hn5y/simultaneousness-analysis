from dataclasses import dataclass, field
from pathlib import Path

from meta_config import (
    FILTER_FUNCTIONS,
    META_JSON_COLUMN_MAPPING,
    META_JSON_FILES,
    META_MEASURAND_MAPPING,
    META_PRODUCT_COLUMNS,
)
import pandas as pd


class MetaTable:
    def __init__(self, data_path: Path) -> None:
        self.data_path = data_path
        self._df_product: pd.Dataframe | None = None
        self._df_stations: pd.Dataframe | None = None
        self.table: pd.Dataframe | None = None

        product_list = self._read_file_info()
        self._generate_table(product_list=product_list)

        # list of dataframes for station metadata from json files for solar, temperature and wind
        dfs_meta_json = [
            self._read_station_meta_data(self.data_path / json_file)
            for json_file in META_JSON_FILES
        ]

        self._merge_station_metadata(dfs_metadata=dfs_meta_json)
        self.table = self._merge_meta_data()

    def _read_file_info(self) -> list[list[any]]:
        file_paths = list(self.data_path.glob("**/*.txt"))
        # metadata are excluded because they are json files
        file_names = [fp.stem for fp in file_paths]
        file_suffixes = [fp.suffix for fp in file_paths]
        product_info = [fn.split("_") for fn in file_names]

        # unpack and combine product info with suffix and path in a flat list for each file
        product_list = [
            [*names, suffix, path]
            for names, suffix, path in zip(
                product_info,
                file_suffixes,
                file_paths,
                strict=True,
            )
        ]
        return product_list

    def _generate_table(self, product_list: list[list[any]]) -> pd.DataFrame:
        product_kwargs = {
            "columns": META_PRODUCT_COLUMNS,
        }
        df = pd.DataFrame(product_list, **product_kwargs)
        # parse dates as dates-dtype, resolution value integer and id as integer
        df["from_date"] = pd.to_datetime(df["from_date"], format="%Y%m%d")
        df["to_date"] = pd.to_datetime(df["to_date"], format="%Y%m%d")
        df["stations_id"] = df["stations_id"].astype(int)

        # translate measurand codes to full names
        df["measurand_names"] = (
            df["measurand"].map(META_MEASURAND_MAPPING).astype("category")
        )
        # all other are strings and can be stored as categorical too
        df["measurand"] = df["measurand"].astype("category")
        df["type"] = df["type"].astype("category")
        df["resolution_unit"] = df["resolution_unit"].astype("category")
        df["format"] = df["format"].astype("category")
        self._df_product = df
        return self._df_product

    @staticmethod
    def _read_station_meta_data(data_path_json: Path) -> pd.DataFrame:
        df = pd.read_json(data_path_json)
        df = df.drop(
            columns=["von_datum", "bis_datum", "Abgabe"],
        )
        df = df.set_index(["Stations_id"])
        return df

    def _merge_station_metadata(self, dfs_metadata: list[pd.DataFrame]) -> pd.DataFrame:
        df_merge_on = dfs_metadata[0].copy()
        for df in dfs_metadata[1:]:
            df_merge_on = df_merge_on.combine_first(df)
        self._df_stations = df_merge_on
        return self._df_stations

    def _merge_meta_data(
        self,
    ) -> pd.DataFrame:
        df = self._df_product.merge(
            self._df_stations,
            left_on="stations_id",
            right_index=True,
            how="left",
        )

        # rename columns to english
        df = df.rename(columns=META_JSON_COLUMN_MAPPING)
        df = df.set_index("path")
        self.table = df
        return self.table

    def search(
        self,
        search_param: MetaSearch,
    ) -> MetaSearchResult:
        df = self.table.copy()

        for field, value in search_param.__dict__.items():
            if value is None:
                continue

            filter_fn = search_param.filters.get(field)
            if filter_fn is not None:
                df = filter_fn(df, value)

        return MetaSearchResult(search=search_param, paths=df.index.tolist())


@dataclass(frozen=True, kw_only=True)
class MetaSearch:
    measurand_names: list[str] | None = None
    from_date: pd.Timestamp | None = None
    to_date: pd.Timestamp | None = None
    station_ids: list[int] | None = None
    station_names: list[str] | None = None
    federal_states: list[str] | None = None
    filters: dict[str, callable] = field(
        repr=False,
        init=False,
        default_factory=lambda: FILTER_FUNCTIONS,
    )


@dataclass(frozen=True, kw_only=True)
class MetaSearchResult:
    search: MetaSearch
    paths: list[str] | None = None

    @property
    def length(self) -> int:
        return len(self.paths) if self.paths is not None else 0


def main() -> None:
    data_path = Path.cwd() / "data" / "cdc" / "raw"
    meta_table = MetaTable(data_path=data_path)
    # print(f"{meta_table._df_product.head()=}")
    # print(f"{meta_table._df_stations.head()=}")
    print(f"{meta_table.table.head()=}")

    # Define search parameters
    search_param = MetaSearch(
        measurand_names=["solar radiation"],
        from_date=pd.Timestamp(year=2020, month=1, day=1),
        station_ids=[1200, 2961],
    )
    # Search meta table with search parameters
    search_result = meta_table.search(search_param=search_param)

    # access search results
    print(f"{search_result.paths=}")
    print(f"{search_result.length=}")


if __name__ == "__main__":
    main()
