from pathlib import Path

from meta.config import (
    META_JSON_COLUMN_MAPPING,
    META_JSON_FILES,
    META_MEASURAND_MAPPING,
    META_PRODUCT_COLUMNS,
)
from meta.search import MetaSearch
from meta.search_result import MetaSearchResult
import pandas as pd


class MetaTable:
    """Table of Meta Data for CDC data set.

    Generated from file names of data files and station metadata from json files. Provides search functionality for data files based on meta data.
    """

    def __init__(self, data_path: Path) -> None:
        """Initialize MetaTable.

        Args:
            data_path (Path): Data path to raw data of CDC data set (e.g. "data/cdc/raw").
        """
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
        """Reads meta data from file names.

        Returns:
            list[list[any]]: List of meta data for each file in the format of [measurand, from_date,
                 to_date, stations_id, type, resolution_value, resolution_unit, format, path].
        """
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
        """Generates meta data table from list of meta data from file names (products).

        Args:
            product_list (list[list[any]]): List of meta data for each file in the format of
                [measurand, from_date, to_date, stations_id, type, resolution_value, resolution_unit, format, path].

        Returns:
            pd.DataFrame: Meta data table for all products in the data path.
        """
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
        """Reads station metadata from a JSON file.

        Args:
            data_path_json (Path): Path to JSON file containing station metadata
                (e.g. "data/cdc/raw/station_meta_data.json").

        Returns:
            pd.DataFrame: Station metadata table.
        """
        df = pd.read_json(data_path_json)
        df = df.drop(
            columns=["von_datum", "bis_datum", "Abgabe"],
        )
        df = df.set_index(["Stations_id"])
        return df

    def _merge_station_metadata(self, dfs_metadata: list[pd.DataFrame]) -> pd.DataFrame:
        """Merges station metadata tables to a single table.

        Args:
            dfs_metadata (list[pd.DataFrame]):
                List of all station metadata tables from JSON files for solar, temperature and wind.

        Returns:
            pd.DataFrame: Merged station metadata table.
        """
        df_merge_on = dfs_metadata[0].copy()
        for df in dfs_metadata[1:]:
            df_merge_on = df_merge_on.combine_first(df)
        self._df_stations = df_merge_on
        return self._df_stations

    def _merge_meta_data(self) -> pd.DataFrame:
        """Merges product meta data table with station metadata table to a single meta data table.

        Also renames columns to english and sets path as index.

        Returns:
            pd.DataFrame: meta data table with station and product information.
        """
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
        """Searches the meta data table with the given search parameters.

        Args:
            search_param (MetaSearch):
                Object containing search parameters and custom filter functions for each parameter.

        Returns:
            MetaSearchResult: Object containinig the list of paths of data files matching the search parameters
        """
        df = self.table.copy()

        for field, value in search_param.__dict__.items():
            if value is None:
                continue

            filter_fn = search_param.filters.get(field)
            if filter_fn is not None:
                df = filter_fn(df, field, value)

        return MetaSearchResult(search=search_param, paths=df.index.tolist())
