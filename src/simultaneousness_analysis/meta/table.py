from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from .search import MetaSearch
import pandas as pd

from simultaneousness_analysis.excel import ExcelTableOptions, create_excel_table
from simultaneousness_analysis.geo_utils import air_distance_km, get_coordinates

from .config import (
    META_JSON_COLUMN_MAPPING,
    META_JSON_FILES,
    META_MEASURAND_MAPPING,
    META_PRODUCT_COLUMNS,
)
from .search import MetaNearestStationResult, MetaSearchResult


@dataclass(frozen=True, kw_only=True)
class MetaStationInfo:
    """Metadata for a station, returned by station info lookups."""

    stations_id: int
    station_name: str | None
    federal_state: str | None
    latitude: float | None
    longitude: float | None
    altitude: float | None


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

    def get_station_info(self, station_id: int) -> MetaStationInfo:
        """Return metadata for the given station id.

        Args:
            station_id (int): Station identifier.

        Returns:
            MetaStationInfo: Station metadata including name, state, coordinates and altitude.

        Raises:
            ValueError: If the meta data table is not generated yet.
            KeyError: If no station exists with the given station id.
        """
        if self._df_stations is None:
            raise ValueError("Meta data table is not generated yet.")

        station_meta = self._df_stations.rename(columns=META_JSON_COLUMN_MAPPING)
        if station_id not in station_meta.index:
            msg = f"Station id {station_id} not found"
            raise KeyError(msg)

        row = station_meta.loc[station_id]
        station_name = row.get("station_name")
        federal_state = row.get("federal_state")
        latitude = row.get("latitude")
        longitude = row.get("longitude")
        altitude = row.get("altitude")

        return MetaStationInfo(
            stations_id=int(station_id),
            station_name=None if pd.isna(station_name) else str(station_name),
            federal_state=None if pd.isna(federal_state) else str(federal_state),
            latitude=None if pd.isna(latitude) else float(latitude),
            longitude=None if pd.isna(longitude) else float(longitude),
            altitude=None if pd.isna(altitude) else float(altitude),
        )

    def get_nearest_station_id_by_coordinates(
        self,
        latitude: float,
        longitude: float,
    ) -> MetaNearestStationResult:
        """Return the nearest station result for the given coordinates.

        Args:
            latitude (float): Latitude in decimal degrees.
            longitude (float): Longitude in decimal degrees.

        Returns:
            MetaNearestStationResult: The nearest station id and the distance in kilometers.
        """
        # Note: this rebuilds the station coordinate subset on each call.
        # If many nearest-station lookups are needed, cache the stations frame
        # once when the meta table is built.
        stations = self.table.reset_index()[["stations_id", "latitude", "longitude"]]
        stations["distance_km"] = stations.apply(
            lambda row: air_distance_km(
                (latitude, longitude),
                (float(row["latitude"]), float(row["longitude"])),
            ),
            axis=1,
        )

        nearest_index = stations["distance_km"].idxmin()
        return MetaNearestStationResult(
            stations_id=int(stations.loc[nearest_index, "stations_id"]),
            distance_km=float(stations.loc[nearest_index, "distance_km"]),
        )

    def get_nearest_station_id_by_address(
        self,
        street: str,
        house_number: str,
        zip_code: str,
        city: str,
    ) -> MetaNearestStationResult:
        """Convert a German address to coordinates (latitude, longitude) and return the nearest station result.

        Args:
            street (str): Street name of the address.
            house_number (str): House number of the address.
            zip_code (str): Postal code (ZIP) of the address.
            city (str): City of the address.

        Returns:
            MetaNearestStationResult: The nearest station id and the distance in kilometers.

        Raises:
            ValueError: If geocoding fails and coordinates cannot be obtained.
        """
        try:
            latitude, longitude = get_coordinates(
                street=street,
                house_number=house_number,
                zip_code=zip_code,
                city=city,
            )
        # Reraise geocoding errors with more context about the address that failed
        except ValueError as exc:
            address = f"{street} {house_number}, {zip_code} {city}, Germany"
            msg = f"Geocoding failed for address: {address}"
            raise ValueError(msg) from exc

        return self.get_nearest_station_id_by_coordinates(latitude, longitude)

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

    def export(self, suffix: str = "json", path: Path | None = None) -> None:
        """Exports the meta data table to an Excel file.

        Args:
            path (Path): Path to save the Excel file
                if none is provided, it will be saved in the data path with the name "meta_table.xlsx"

            suffix (str): Suffix of the file format to export, either "json" or "xlsx". Default is "json".

        Raises:
            ValueError: If the meta data table is not generated yet.
        """
        if self.table is None:
            raise ValueError("Meta data table is not generated yet.")

        valid_suffixes = ["json", "xlsx"]
        if suffix not in valid_suffixes:
            msg = f"Invalid suffix '{suffix}'. Valid suffixes are: {valid_suffixes}."
            raise ValueError(msg)

        if path is None:
            path = self.data_path / f"meta_table.{suffix}"

        if suffix == "json":
            self.table.to_json(path, orient="records", indent=4)
        if suffix == "xlsx":
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                dataframe_export = self.table.reset_index()
                dataframe_export.to_excel(writer, sheet_name="Meta Table", index=False)
                worksheet = writer.sheets["Meta Table"]
                options = ExcelTableOptions(
                    integer_columns={"stations_id"},
                    coordinate_columns={"latitude", "longitude"},
                )
                create_excel_table(
                    worksheet=worksheet,
                    dataframe=dataframe_export,
                    options=options,
                )
