from typing import Dict, List
from unittest import TestCase
from unittest.mock import MagicMock, patch

import requests
import requests_mock

from src.data import CloudRunRegions, Geolocation


def mock_carbon_intensity(region: str) -> int:
    if region == "europe-west1":
        return 100
    elif region == "europe-west2":
        return 200
    elif region == "europe-west4":
        return 300
    elif region == "europe-west6":
        return 400


def make_mock_Geolocation() -> Geolocation:
    mock_Geolocation = Geolocation

    def mock_of(name) -> Dict[str, float]:
        if name == "Belgium":
            return {'lat': 50.6402809, 'lon': 4.6667145}
        elif name == "London":
            return {'lat': 51.5073219, 'lon': -0.1276474}
        elif name == "Frankfurt":
            raise LookupError(f"Could not geolocate Frankfurt.")
        elif name == "Netherlands":
            return {'lat': 52.2434979, 'lon': 5.6343227}
        elif name == "Zurich":
            return {'lat': 47.3744489, 'lon': 8.5410422}

    mock_Geolocation.of = MagicMock(side_effect=mock_of)

    # Mock current location as Bristol.
    mock_Geolocation.here = MagicMock(return_value={'lat': 51.4538022, 'lon': -2.5972985})

    return mock_Geolocation


class TestCloudRunRegions(TestCase):

    def setUp(self) -> None:
        self.api_key = "pretend_good_key"
        self.project_id = "pretend-project"

    @patch("src.data.Geolocation", make_mock_Geolocation())
    @patch("src.constants.ALL_CLOUD_RUN_REGIONS", [
        {"id": "europe-west1", "name": "Belgium", "lat": 50.6402809, "lon": 4.6667145},
        {"id": "europe-west2", "name": "London", "lat": 51.5073219, "lon": -0.1276474}])
    def test_closest(self) -> None:
        """Pretending we are based in Bristol, London is returned as the closest region, with accompanying CO2 data."""
        with requests_mock.Mocker() as m:
            m.get(f"https://api.co2signal.com/v1/latest?lon=4.6667145&lat=50.6402809",
                  headers={"auth-token": self.api_key},
                  text='{"_disclaimer":"This data is the exclusive property of electricityMap and/or related parties. If you\'re in doubt about your rights to use this data, please contact api@co2signal.com","status":"ok","countryCode":"GB","data":{"datetime":"2022-08-19T15:00:00.000Z","carbonIntensity":100,"fossilFuelPercentage":42.02},"units":{"carbonIntensity":"gCO2eq/kWh"}}')
            m.get(f"https://api.co2signal.com/v1/latest?lon=-0.1276474&lat=51.5073219",
                  headers={"auth-token": self.api_key},
                  text='{"_disclaimer":"This data is the exclusive property of electricityMap and/or related parties. If you\'re in doubt about your rights to use this data, please contact api@co2signal.com","status":"ok","countryCode":"GB","data":{"datetime":"2022-08-19T15:00:00.000Z","carbonIntensity":237,"fossilFuelPercentage":42.02},"units":{"carbonIntensity":"gCO2eq/kWh"}}')
            obtained = CloudRunRegions(self.project_id, self.api_key).closest
        expected = {'carbon_intensity': 237,
                    'distance_from_current_location': 171,
                    'id': 'europe-west2',
                    'lat': 51.5073219,
                    'lon': -0.1276474,
                    'name': 'London'}
        self.assertEqual(expected, obtained)

    @patch("src.constants.ALL_CLOUD_RUN_REGIONS", [
        {"id": "europe-west1", "name": "Belgium", "lat": 50.6402809, "lon": 4.6667145},
        {"id": "europe-west2", "name": "London", "lat": 51.5073219, "lon": -0.1276474}])
    def test_carbon_intensity(self) -> None:
        """Given a region ID, an integer value is returned for that region's carbon intensity."""
        with requests_mock.Mocker() as m:
            m.get(f"https://api.co2signal.com/v1/latest?lon=4.6667145&lat=50.6402809",
                  headers={"auth-token": self.api_key},
                  text='{"_disclaimer":"This data is the exclusive property of electricityMap and/or related parties. If you\'re in doubt about your rights to use this data, please contact api@co2signal.com","status":"ok","countryCode":"GB","data":{"datetime":"2022-08-19T15:00:00.000Z","carbonIntensity":100,"fossilFuelPercentage":42.02},"units":{"carbonIntensity":"gCO2eq/kWh"}}')
            obtained = CloudRunRegions(self.project_id, self.api_key)._carbon_intensity('europe-west1')
        expected = 100
        self.assertEqual(expected, obtained)

    @patch("src.constants.ALL_CLOUD_RUN_REGIONS", [
        {"id": "europe-west1", "name": "Belgium", "lat": 50.6402809, "lon": 4.6667145},
        {"id": "europe-west2", "name": "London", "lat": 51.5073219, "lon": -0.1276474}])
    def test_carbon_intensity_bad_key(self) -> None:
        """Given a region ID, a ConnectionError is thrown if the API key is bad."""
        with self.assertRaises(ConnectionError):
            with requests_mock.Mocker() as m:
                m.get(f"https://api.co2signal.com/v1/latest?lon=4.6667145&lat=50.6402809",
                      headers={"auth-token": "bad_api_key"},
                      status_code=403,
                      text='{"message":"Invalid authentication credentials"}')
                CloudRunRegions(self.project_id, "bad_api_key")._carbon_intensity('europe-west1')

    @patch("src.constants.ALL_CLOUD_RUN_REGIONS", [
        {"id": "europe-west1", "name": "Belgium", "lat": 50.6402809, "lon": 4.6667145},
        {"id": "europe-west2", "name": "London", "lat": 51.5073219, "lon": -0.1276474}])
    def test_carbon_intensity_bad_connection(self) -> None:
        """Given a region ID, a ConnectionError is thrown if the machine cannot connect."""
        with self.assertRaises(ConnectionError):
            with requests_mock.Mocker() as m:
                m.get(f"https://api.co2signal.com/v1/latest?lon=4.6667145&lat=50.6402809",
                      exc=requests.exceptions.ConnectionError)
                CloudRunRegions(self.project_id, self.api_key)._carbon_intensity('europe-west1')

    @patch("src.constants.ALL_CLOUD_RUN_REGIONS", [
        {"id": "europe-west1", "name": "Belgium", "lat": 50.6402809, "lon": 4.6667145},
        {"id": "europe-west2", "name": "London", "lat": 51.5073219, "lon": -0.1276474}])
    def test_greenest_bad_region(self) -> None:
        """Given a list of candidate regions containing an invalid one, greenest throws AssertionError."""
        with self.assertRaises(AssertionError):
            CloudRunRegions(self.project_id, self.api_key).greenest(['europe-west2', 'europe-west3'])

    @patch("src.constants.ALL_CLOUD_RUN_REGIONS", [
        {'name': 'trading-nonprod/locations/europe-west1', 'locationId': 'europe-west1', 'displayName': 'Belgium'},
        {'name': 'trading-nonprod/locations/europe-west2', 'locationId': 'europe-west2', 'displayName': 'London'},
        {'name': 'trading-nonprod/locations/europe-west4', 'locationId': 'europe-west4', 'displayName': 'Netherlands'},
        {'name': 'trading-nonprod/locations/europe-west6', 'locationId': 'europe-west6', 'displayName': 'Zurich'}])
    def test_greenest_no_candidate_regions(self) -> None:
        """Given no list of candidate regions, greenest returns the greenest of all possible regions."""
        regions = CloudRunRegions(self.project_id, self.api_key)
        regions._carbon_intensity = MagicMock(side_effect=mock_carbon_intensity)

        obtained = regions.greenest()
        expected = {'id': 'europe-west1', 'name': 'Belgium', 'lat': 50.6402809, 'lon': 4.6667145,
                    'carbon_intensity': 100}
        self.assertEqual(expected, obtained)

    @patch("src.constants.ALL_CLOUD_RUN_REGIONS", [
        {'name': 'trading-nonprod/locations/europe-west4', 'locationId': 'europe-west4', 'displayName': 'Netherlands'},
        {'name': 'trading-nonprod/locations/europe-west6', 'locationId': 'europe-west6', 'displayName': 'Zurich'}])
    def test_greenest_good_candidate_regions(self) -> None:
        """Given a list of good candidate regions, greenest returns the greenest of the candidates."""
        regions = CloudRunRegions(self.project_id, self.api_key)
        regions._carbon_intensity = MagicMock(side_effect=mock_carbon_intensity)

        obtained = regions.greenest()
        expected = {'id': 'europe-west4', 'name': 'Netherlands', 'lat': 52.2434979, 'lon': 5.6343227,
                    'carbon_intensity': 300}
        self.assertEqual(expected, obtained)

    """
    TESTS TO ADD:
    Provide way to turn off cache.
    Greenest:
    -Warning if single region can't lookup
    -Throws if all regions can't lookup.
    """
