from .retrieve_data_from_dwd_cdc import main as retrieve_data

# Set True to retrieve data from DWD CDC for station in S-H
RETRIEVE_DATA: bool = False


def main() -> None:
    """Main function."""
    if RETRIEVE_DATA:
        retrieve_data()


if __name__ == "__main__":
    main()
