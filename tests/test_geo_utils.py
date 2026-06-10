from types import SimpleNamespace

import pytest

from simultaneousness_analysis import geo_utils

# Unit tests for ``geo_utils``. These tests mock the external geocoder
# so they run offline and deterministically.


def test_get_coordinates_success(monkeypatch):
    """Returns coordinates when geocoder finds a location."""

    # Replace the real network call with a deterministic fake location for Kiel.
    def fake_geocode(self, address: str):
        return SimpleNamespace(latitude=54.3233, longitude=10.1228)

    monkeypatch.setattr(geo_utils.Nominatim, "geocode", fake_geocode)

    lat, lon = geo_utils.get_coordinates("Rathausplatz", "1", "24103", "Kiel")
    assert (lat, lon) == (54.3233, 10.1228)


def test_get_coordinates_not_found(monkeypatch):
    """Raises ValueError when geocoder returns None."""
    # Simulate a failed lookup by returning None from the geocoder.
    monkeypatch.setattr(geo_utils.Nominatim, "geocode", lambda self, addr: None)

    with pytest.raises(ValueError):
        geo_utils.get_coordinates("Nowhere", "0", "00000", "Nocity")


def test_air_distance_km_properties():
    """Distance is symmetric, positive and rounded to 3 decimals."""
    # Schleswig-Holstein example coordinates: Kiel and Husby.
    kiel = (54.3233, 10.1228)
    husby = (54.5589, 9.3917)

    d1 = geo_utils.air_distance_km(kiel, husby)
    d2 = geo_utils.air_distance_km(husby, kiel)

    assert isinstance(d1, float)
    assert d1 > 0
    assert d1 == d2
    # Ensure the function rounds to 3 decimal places.
    assert round(d1, 3) == d1
