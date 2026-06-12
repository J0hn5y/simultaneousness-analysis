from geopy.geocoders import Nominatim
from haversine import Unit, haversine


def get_coordinates(
    street: str,
    house_number: str,
    zip_code: str,
    city: str,
) -> tuple[float, float]:
    """Convert a German address into latitude and longitude.

    Args:
        street: Street name.
        house_number: House number.
        zip_code: Postal code.
        city: City name.

    Returns:
        Latitude and longitude as a tuple in decimal degrees.

    Raises:
        ValueError: If the address cannot be geocoded.
    """
    address = f"{street} {house_number}, {zip_code} {city}, Germany"
    geolocator = Nominatim(
        # Required by Terms of Service: https://operations.osmfoundation.org/policies/nominatim/
        user_agent="simultaneousness_analysis.geo_utils/0.1, hansenbrian039@gmail.com",
    )
    location = geolocator.geocode(address)

    if location is None:
        msg = f"Address not found: {address}"
        raise ValueError(msg)

    return (location.latitude, location.longitude)


def air_distance_km(
    point_a: tuple[float, float],
    point_b: tuple[float, float],
) -> float:
    """Calculate the air distance between two latitude/longitude points.

    Args:
        point_a: First point as a (lat, lon) tuple.
        point_b: Second point as a (lat, lon) tuple.

    Returns:
        Distance between the points in kilometers.
    """
    return round(haversine(point_a, point_b, unit=Unit.KILOMETERS), 3)


# Example usage:
if __name__ == "__main__":
    husby = get_coordinates("Bregning-West", "4a", "24975", "Husby")
    print("Coordinates Husby:", husby)

    kiel = get_coordinates("Schevenbrücke", "7", "24103", "Kiel")
    print("Coordinates Kiel:", kiel)

    print("Air Distance from Husby to Kiel:", air_distance_km(husby, kiel), "km")
