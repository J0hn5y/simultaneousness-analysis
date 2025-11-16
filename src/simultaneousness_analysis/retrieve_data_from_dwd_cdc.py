from http import HTTPStatus
from pathlib import Path
from re import findall
from time import sleep
from urllib.parse import urljoin
from urllib.request import urlretrieve
from zipfile import ZipFile

import pandas as pd
import requests

# Settings
DELAY_SECONDS: int = 5  # Sekunden zwischen Requests

# Prepare data folder structure
DATA_BASE_PATH: Path = Path.cwd() / "data"
DATA_DIRECTORIES = {
    "temperature": DATA_BASE_PATH / "cdc" / "raw" / "air_temperature",
    "solar": DATA_BASE_PATH / "cdc" / "raw" / "solar",
    "wind": DATA_BASE_PATH / "cdc" / "raw" / "wind",
    "zip": DATA_BASE_PATH / "cdc" / "raw" / "zip",
}

# DWD CDC URLs and metadata
BASE_URL: str = (
    "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/"
)
DATA_URLS: dict[str, str] = {
    "temperature": urljoin(BASE_URL, "10_minutes/air_temperature/historical/"),
    "wind": urljoin(BASE_URL, "10_minutes/wind/historical/"),
    "solar": urljoin(BASE_URL, "10_minutes/solar/historical/"),
}
METADATA_FILE: dict[str, str] = {
    "temperature": urljoin(
        DATA_URLS["temperature"],
        "zehn_min_tu_Beschreibung_Stationen.txt",
    ),
    "wind": urljoin(DATA_URLS["wind"], "zehn_min_ff_Beschreibung_Stationen.txt"),
    "solar": urljoin(DATA_URLS["solar"], "zehn_min_sd_Beschreibung_Stationen.txt"),
}
BUNDESLAND: str = "Schleswig-Holstein"


def create_data_folder_structure() -> None:
    """Creates the necessary data folder structure if it does not exist."""
    for directory in DATA_DIRECTORIES.values():
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            print(f"Created data directory: {directory}")


def get_station_metadata(metadata_url: str, bundesland: str) -> pd.DataFrame:
    """Retrieve a list of station IDs for weather stations in a specific German state.

    This function reads fixed-width formatted metadata from the German Weather Service (DWD)
    and filters stations by the specified Bundesland (state).
    No separator found in the metadata file; hence, pandas' read_fwf is used. Colspecs is definining the column widths.

    Args:
        metadata_url (str): URL or file path to the DWD metadata file in fixed-width format
        bundesland (str): The name of the German state (Bundesland) to filter stations by.

    Returns:
        DataFrame with MetaData for all station in state.
    """
    df = pd.read_fwf(
        metadata_url,
        encoding="ISO-8859-1",
        colspecs=[
            (0, 6),
            (6, 15),
            (15, 24),
            (24, 40),
            (40, 50),
            (50, 60),
            (60, 100),
            (100, 130),
            (130, 140),
        ],
        skiprows=[1],
    )
    df.columns = [
        "Stations_id",
        "von_datum",
        "bis_datum",
        "Stationshoehe",
        "geoBreite",
        "geoLaenge",
        "Stationsname",
        "Bundesland",
        "Abgabe",
    ]
    df = df[df["Bundesland"] == bundesland]
    return df


def save_station_metadata_json(df: pd.DataFrame, measurement: str) -> None:
    """Save station metadata to a JSON file.

    Exports the provided DataFrame containing station metadata to a JSON file
    in the CDC raw data directory with a filename based on the measurement type.

    Args:
        df (pd.DataFrame): DataFrame containing station metadata to be saved.
        measurement (str): The measurement type used to construct the output
            filename (e.g., 'temperature', 'precipitation').
    """
    df.to_json(
        DATA_BASE_PATH / "cdc" / "raw" / f"station_metadata_{measurement}.json",
        orient="records",
        indent=4,
        force_ascii=False,
    )


def get_station_ids_from_metadata(df: pd.DataFrame) -> list[str]:
    """Extract and format station IDs from metadata DataFrame.

    Converts station IDs from the DataFrame to strings and pads them with leading
    zeros to ensure they are 5 digits long.

    Args:
         df: DataFrame containing weather station metadata with a 'Stations_id' column.

    Returns:
        A list of station IDs formatted as 5-digit strings.
    """
    station_ids = df["Stations_id"].astype(str).str.zfill(5).tolist()
    return station_ids


def find_filenames_for_station(measurement: str, station_id: str) -> list[str]:
    """Retrieve ZIP file links for a specific weather station from DWD CDC.

    Fetches the website from the DWD (Deutscher Wetterdienst) Climate Data Center
    and filters the html links for ZIP files matching the given station ID.

    Args:
        measurement: The type of measurement (e.g., 'temperature', 'wind, 'solar').
                    Must be a key in the DATA_URLS dictionary.
        station_id: The unique identifier of the weather station to filter for.

    Returns:
        A list of ZIP file URLs containing data for the specified station.
        Returns an empty list if no matching files are found.

    Raises:
        ConnectionError: If the HTTP request to the data URL fails with a status
                        code other than 200 (OK).
    """
    data_url = DATA_URLS[measurement]
    response = requests.get(data_url, timeout=10)
    if response.status_code != HTTPStatus.OK:
        msg = f"Error while retrieving data from: {data_url}"
        raise ConnectionError(msg)
    zip_links = findall(r'href="([^"]+\.zip)"', response.text)
    station_links = [link for link in zip_links if f"_{station_id}_" in link]
    return station_links


def unpack_and_remove_zip(
    zip_file_path: Path,
    extract_to: Path,
) -> None:
    """Extracts a ZIP file and optionally removes the original archive.

    Args:
        zip_file_path (Path): file path to the ZIP archive.
        extract_to (Path): directory path where the ZIP contents will be extracted to.
    """
    #  TODO(<Brian>): Add error handling for file operations
    with ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    Path(zip_file_path).unlink()


def retrieve_data_for_station(measurement: str, station_id: str) -> None:
    """Retrieve and store data files for a specific weather station.

    Downloads ZIP files from the DWD CDC for the specified measurement type
    and station ID, then extracts the contents to the appropriate data directory.

    Args:
        measurement: The type of measurement (e.g., 'temperature', 'wind', 'solar').
                    Must be a key in the DATA_URLS dictionary.
        station_id: The unique identifier of the weather station to retrieve data for.
    """
    filenames = find_filenames_for_station(measurement, station_id)
    for filename in filenames:
        file_url = urljoin(DATA_URLS[measurement], filename)
        zip_filename = DATA_DIRECTORIES["zip"] / filename
        urlretrieve(file_url, zip_filename)

        unpack_and_remove_zip(
            zip_file_path=zip_filename,
            extract_to=DATA_DIRECTORIES[measurement],
        )
        print(
            f"Retrieved and extracted data for station {station_id} from {filename} into {DATA_DIRECTORIES[measurement]}",
        )


def main() -> None:
    """Main function to retrieve data for all stations in a specified german state."""
    create_data_folder_structure()

    for measurement in DATA_URLS:
        df_station_metadata = get_station_metadata(
            metadata_url=METADATA_FILE[measurement],
            bundesland=BUNDESLAND,
        )
        save_station_metadata_json(
            df=df_station_metadata,
            measurement=measurement,
        )
        station_ids = get_station_ids_from_metadata(df_station_metadata)

        for station_id in station_ids:
            retrieve_data_for_station(measurement=measurement, station_id=station_id)
            sleep(DELAY_SECONDS)


if __name__ == "__main__":
    main()
