from pathlib import Path
import re

import pandas as pd
from pandas.api.types import CategoricalDtype

# from word2number import w2n  # why cant this module be found?

# 1. function: provide dataframe of all products with their attributes parsed from file names


def generate_meta_search_table(data_path: Path) -> pd.DataFrame:
    """Seg!

    Args:
        data_path (Path): _description_

    Returns:
        pd.DataFrame: _description_
    """
    # fetch all file names anmd store thwm in a list
    file_paths = list(data_path.glob("**/*.txt"))
    # metadata are excluded because they are json files
    file_names = [fp.name for fp in file_paths]
    # TODO usefp.stem und .suffixto avoid using re

    # split file name on every "_" and every "." to gain all intel from the name
    product_list = [re.split(r"[_.]", fn) for fn in file_names]
    # path/path/example produkt_zehn_min_tu_19910417_19991231_04466.txt

    # add file_path as last element to each product entry
    for i, file_path in enumerate(file_paths):
        product_list[i].append(file_path)
    # all appended file paths should be path objects

    product_kwargs = {
        "columns": [
            "type",
            "resolution_value",
            "resolution_unit",
            "measurand",
            "from_date",
            "to_date",
            "stations_id",
            "format",
            "path",
        ],
    }
    product_df = pd.DataFrame(product_list, **product_kwargs)
    # parse dates as dates-dtype, resolution value integer and id as integer
    product_df["from_date"] = pd.to_datetime(product_df["from_date"], format="%Y%m%d")
    product_df["to_date"] = pd.to_datetime(product_df["to_date"], format="%Y%m%d")
    product_df["stations_id"] = product_df["stations_id"].astype(int)
    # TODO parse resolution_value as integer with package "word2number" because the values are written as words in german
    # resolution_value_list = []
    # for value in product_df["resolution_value"]:
    #    resolution_value_list.append(w2n.word_to_num(value))
    # product_df["resolution_value"] = resolution_value_list

    # translate measurand codes to full names
    measurand_mapping = {
        "sd": "solar radiation",
        "tu": "air temperature",
        "ff": "wind speed",
    }
    product_df["measurand_names"] = (
        product_df["measurand"].map(measurand_mapping).astype("category")
    )
    product_df["measurand"] = product_df["measurand"].astype("category")
    # all other are strings and can be stored as categorical too
    product_df["type"] = product_df["type"].astype("category")
    product_df["resolution_unit"] = product_df["resolution_unit"].astype("category")
    product_df["format"] = product_df["format"].astype("category")

    # 2. join metadata
    # Metadata file paths (constants)
    META_DATA_TEMPERATURE = data_path / "station_metadata_temperature.json"
    META_DATA_SOLAR = data_path / "station_metadata_solar.json"
    META_DATA_WIND = data_path / "station_metadata_wind.json"
    print(META_DATA_TEMPERATURE)
    # station metadata (attributes that are independent from measurements)
    # Remove date range columns as they depend on the measurements
    # and remove abgabe as it is not relevant for this use case
    metadata_temperature = pd.read_json(META_DATA_TEMPERATURE)
    metadata_temperature = metadata_temperature.drop(
        columns=["von_datum", "bis_datum", "Abgabe"],
    )
    print(len(metadata_temperature))
    metadata_temperature.set_index(["Stations_id"], inplace=True)

    metadata_solar = pd.read_json(META_DATA_SOLAR)
    metadata_solar.drop(columns=["von_datum", "bis_datum", "Abgabe"], inplace=True)
    metadata_solar.set_index(["Stations_id"], inplace=True)
    print(len(metadata_solar))

    metadata_wind = pd.read_json(META_DATA_WIND)
    metadata_wind.drop(columns=["von_datum", "bis_datum", "Abgabe"], inplace=True)
    metadata_wind.set_index(["Stations_id"], inplace=True)
    print(len(metadata_wind))

    # TODO ensure that these attributes are the same for all metadata files
    metadata_station = metadata_temperature.copy()
    metadata_station.combine_first(metadata_solar)
    metadata_station.combine_first(metadata_wind)
    metadata_station

    # merge product dataframe with metadata dataframe on station id
    product_metadata_df = product_df.merge(
        metadata_station,
        left_on="stations_id",
        right_index=True,
        how="left",
    )

    # rename columns to english
    product_metadata_df.rename(
        columns={
            "Bundesland": "federal_state",
            "Stationshoehe": "altitude",
            "geoBreite": "latitude",
            "geoLaenge": "longitude",
            "Stationsname": "station_name",
        },
        inplace=True,
    )
    return product_metadata_df.set_index("path")


def search_paths_by_meta_data(
    search_table: pd.DataFrame,
    measurand_names: list | None = None,
    from_date: pd.Timestamp | None = None,
    to_date: pd.Timestamp | None = None,
    station_ids: list[int] | None = None,
    station_names: list[str] | None = None,
    federal_states: list[str] | None = None,
) -> list:
    # use default factory or set default to None or empty list to avoid mutable default arguments
    """Search paths by meta data from search table!

    Args:
        search_table (pd.DataFrame): _description_
        measurand_names (list, optional): _description_. Defaults to [].
        from_date (_type_, optional): _description_. Defaults to None.
        to_date (_type_, optional): _description_. Defaults to None.
        station_ids (list, optional): _description_. Defaults to [].
        station_names (list, optional): _description_. Defaults to [].
        federal_states (list, optional): _description_. Defaults to [].

    Returns:
        list: path objects matching the filter criteria

    """
    # 3. function: "simple" filter dataframe by measurand, date range, station id and return list of paths
    filtered = search_table.copy()

    if measurand_names is not None:
        filtered = filtered[filtered["measurand_names"].isin(measurand_names)]

    if from_date is not None:
        filtered = filtered[filtered["from_date"] >= from_date]

    if to_date is not None:
        filtered = filtered[filtered["to_date"] <= to_date]

    if station_ids is not None:
        filtered = filtered[filtered["stations_id"].isin(station_ids)]

    if station_names is not None:
        filtered = filtered[filtered["station_name"].isin(station_names)]

    if federal_states is not None:
        filtered = filtered[filtered["federal_state"].isin(federal_states)]

    # possible filter parameters:
    # measurand ("code")
    # resolution (value + unit)
    # format
    # type
    # Area (altitude, latitude, longitude and PLZ,.. after merging with additional metadata)

    path_list = filtered.index.tolist()
    return path_list


def main() -> None:
    # Data folder paths (constants)
    DATA_PATH = Path.cwd() / "data" / "cdc" / "raw"

    meta_search_table = generate_meta_search_table(DATA_PATH)
    # to cache meta data search tabele it es nessassary to use relative paths with working directory as root

    # use request-class?
    # search paths by meta data
    result = search_paths_by_meta_data(
        search_table=meta_search_table,
        measurand_names=["solar radiation"],
        station_ids=[1200, 2961],
    )
    print(result)
    # next step is to convert paths into dataframes with the real data


if __name__ == "__main__":
    main()
