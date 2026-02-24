from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

# Constants
# TODO: Move to configuration file

META_JSON_FILES = (
    "station_metadata_temperature.json",
    "station_metadata_solar.json",
    "station_metadata_wind.json",
)

MEASURAND_MAPPING = {
    "sd": "solar radiation",
    "tu": "air temperature",
    "ff": "wind speed",
}

META_PRODUCT_COLUMNS = [
    "type",
    "resolution_value",
    "resolution_unit",
    "measurand",
    "from_date",
    "to_date",
    "stations_id",
    "format",
    "path",
]

META_JSON_COLUMN_MAPPING = {
    "Bundesland": "federal_state",
    "Stationshoehe": "altitude",
    "geoBreite": "latitude",
    "geoLaenge": "longitude",
    "Stationsname": "station_name",
}

FILTER_FUNCTIONS = {
    "measurand_names": lambda df, value: df[df["measurand_names"].isin(value)],
    "from_date": lambda df, value: df[df["from_date"] >= value],
    "to_date": lambda df, value: df[df["to_date"] <= value],
    "station_ids": lambda df, value: df[df["stations_id"].isin(value)],
    "station_names": lambda df, value: df[df["station_name"].isin(value)],
    "federal_states": lambda df, value: df[df["federal_state"].isin(value)],
}


@dataclass(frozen=True, kw_only=True)
class MetaSearchParameters:
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
    search: MetaSearchParameters
    paths: list[str] | None = None

    @property
    def length(self) -> int:
        return len(self.paths) if self.paths is not None else 0


def read_meta_data(data_path: Path) -> list[list[any]]:
    file_paths = list(data_path.glob("**/*.txt"))
    # metadata are excluded because they are json files
    file_names = [fp.stem for fp in file_paths]
    file_suffixes = [fp.suffix for fp in file_paths]
    product_info = [fn.split("_") for fn in file_names]

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


def generate_meta_search_table(product_list: list[list[any]]) -> pd.DataFrame:
    product_kwargs = {
        "columns": META_PRODUCT_COLUMNS,
    }
    product_df = pd.DataFrame(product_list, **product_kwargs)
    # parse dates as dates-dtype, resolution value integer and id as integer
    product_df["from_date"] = pd.to_datetime(product_df["from_date"], format="%Y%m%d")
    product_df["to_date"] = pd.to_datetime(product_df["to_date"], format="%Y%m%d")
    product_df["stations_id"] = product_df["stations_id"].astype(int)

    # translate measurand codes to full names
    product_df["measurand_names"] = (
        product_df["measurand"].map(MEASURAND_MAPPING).astype("category")
    )
    # all other are strings and can be stored as categorical too
    product_df["measurand"] = product_df["measurand"].astype("category")
    product_df["type"] = product_df["type"].astype("category")
    product_df["resolution_unit"] = product_df["resolution_unit"].astype("category")
    product_df["format"] = product_df["format"].astype("category")
    return product_df


def read_json_meta_data(data_path_json: Path) -> pd.DataFrame:
    df = pd.read_json(data_path_json)
    df = df.drop(
        columns=["von_datum", "bis_datum", "Abgabe"],
    )
    df.set_index(["Stations_id"], inplace=True)
    return df


def merge_json_metadata(dfs_metadata: list[pd.DataFrame]) -> pd.DataFrame:
    df_merged = dfs_metadata[0].copy()
    for df in dfs_metadata[1:]:
        df_merged = df_merged.combine_first(df)
    return df_merged


def merge_all_metadata(
    product_df: pd.DataFrame,
    metadata_station: pd.DataFrame,
) -> pd.DataFrame:
    df = product_df.merge(
        metadata_station,
        left_on="stations_id",
        right_index=True,
        how="left",
    )

    # rename columns to english
    df = df.rename(columns=META_JSON_COLUMN_MAPPING)
    return df.set_index("path")


def search_paths_by_meta_data(
    search_table: pd.DataFrame,
    search_param: MetaSearchParameters,
) -> MetaSearchResult:
    df = search_table.copy()

    for field, value in search_param.__dict__.items():
        if value is None:
            continue

        filter_fn = search_param.filters.get(field)
        if filter_fn is not None:
            df = filter_fn(df, value)

    return MetaSearchResult(search=search_param, paths=df.index.tolist())


def main() -> None:
    data_path = Path.cwd() / "data" / "cdc" / "raw"
    product_list = read_meta_data(data_path=data_path)
    meta_search_table = generate_meta_search_table(product_list=product_list)

    dfs_meta_json = [
        read_json_meta_data(data_path_json=data_path / json_file)
        for json_file in META_JSON_FILES
    ]

    df_meta_json = merge_json_metadata(dfs_metadata=dfs_meta_json)

    meta_search_table = merge_all_metadata(
        product_df=meta_search_table,
        metadata_station=df_meta_json,
    )

    # Define search parameters
    search_param = MetaSearchParameters(
        measurand_names=["solar radiation"],
        from_date=pd.Timestamp(year=2020, month=1, day=1),
        station_ids=[1200, 2961],
    )

    # search paths by meta data
    search_result = search_paths_by_meta_data(
        search_table=meta_search_table,
        search_param=search_param,
    )
    print(search_result.length)


if __name__ == "__main__":
    main()
