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
