from .column_filter import DataFrameFilter, greater_equal, is_in, less_equal

META_JSON_FILES = (
    "station_metadata_temperature.json",
    "station_metadata_solar.json",
    "station_metadata_wind.json",
)

META_MEASURAND_MAPPING = {
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

FILTER_FUNCTIONS: dict[str, DataFrameFilter] = {
    "measurand_names": is_in,
    "from_date": greater_equal,
    "to_date": less_equal,
    "stations_id": is_in,
    "station_names": is_in,
    "federal_states": is_in,
}
