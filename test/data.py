from typing import Dict, List, Type, Callable, Any
from unittest import TestCase
from unittest.mock import MagicMock, patch

from os import path, remove

import requests
import requests_mock

from src.data import CloudRunRegions, Geolocation


def clear_co2_signal_cache() -> None:
    cache_path = "co2_signal_cache.sqlite"
    if path.exists(cache_path):
        remove(cache_path)


def clear_cache_first(test: Callable) -> Callable:
    def wrapper(*args: Any, **kwargs: Any) -> None:
        clear_co2_signal_cache()
        test(*args, **kwargs)

    return wrapper


def mock_carbon_intensity(region: str) -> int:
    if region == "europe-west1":
        carbon_intensity = 100
    elif region == "europe-west2":
        carbon_intensity = 200
    elif region == "europe-west4":
        carbon_intensity = 300
    elif region == "europe-west6":
        carbon_intensity = 400
    return carbon_intensity


def make_mock_Geolocation() -> Type[Geolocation]:
    mock_Geolocation = Geolocation

    def mock_of(name: str) -> Dict[str, float]:
        if name == "Belgium":
            value = {"lat": 50.6402809, "lon": 4.6667145}
        elif name == "London":
            value = {"lat": 51.5073219, "lon": -0.1276474}
        elif name == "Frankfurt":
            raise LookupError(f"Could not geolocate Frankfurt.")
        elif name == "Netherlands":
            value = {"lat": 52.2434979, "lon": 5.6343227}
        elif name == "Zurich":
            value = {"lat": 47.3744489, "lon": 8.5410422}
        return value

    mock_Geolocation.of = MagicMock(side_effect=mock_of)  # type: ignore #https://github.com/python/mypy/issues/2427

    # Mock current location as Bristol.
    mock_Geolocation.here = MagicMock(  # type: ignore #https://github.com/python/mypy/issues/2427
        return_value={"lat": 51.4538022, "lon": -2.5972985}
    )

    return mock_Geolocation


class TestCloudRunRegions(TestCase):
    def setUp(self) -> None:
        self.api_key = "pretend_good_key"
        self.project_id = "pretend-project"

    @clear_cache_first
    def test_carbon_intensity(self) -> None:
        """Given a region ID, an integer value is returned for that region's carbon intensity."""

        with requests_mock.Mocker() as m:
            m.get(
                f"https://api.co2signal.com/v1/latest?lon=4.6667145&lat=50.6402809",
                headers={"auth-token": self.api_key},
                text='{"_disclaimer":"This data is the exclusive property of electricityMap and/or related parties. If you\'re in doubt about your rights to use this data, please contact api@co2signal.com","status":"ok","countryCode":"GB","data":{"datetime":"2022-08-19T15:00:00.000Z","carbonIntensity":100,"fossilFuelPercentage":42.02},"units":{"carbonIntensity":"gCO2eq/kWh"}}',
            )
            obtained = CloudRunRegions(self.project_id, self.api_key)._carbon_intensity(
                "europe-west1"
            )
        expected = 100
        self.assertEqual(expected, obtained)

    @patch(
        "src.constants.ALL_CLOUD_RUN_REGIONS",
        [
            {
                "id": "europe-west1",
                "name": "Belgium",
                "lat": 50.6402809,
                "lon": 4.6667145,
            },
            {
                "id": "europe-west2",
                "name": "London",
                "lat": 51.5073219,
                "lon": -0.1276474,
            },
        ],
    )
    @clear_cache_first
    def test_carbon_intensity_bad_key(self) -> None:
        """Given a region ID, a ConnectionError is thrown if the API key is bad."""

        with self.assertRaises(ConnectionError):
            with requests_mock.Mocker() as m:
                m.get(
                    f"https://api.co2signal.com/v1/latest?lon=4.6667145&lat=50.6402809",
                    request_headers={"auth-token": "bad_api_key"},
                    status_code=403,
                    text='{"message":"Invalid authentication credentials"}',
                )
                CloudRunRegions(self.project_id, "bad_api_key")._carbon_intensity(
                    "europe-west1"
                )

    @patch(
        "src.constants.ALL_CLOUD_RUN_REGIONS",
        [
            {
                "id": "europe-west1",
                "name": "Belgium",
                "lat": 50.6402809,
                "lon": 4.6667145,
            },
            {
                "id": "europe-west2",
                "name": "London",
                "lat": 51.5073219,
                "lon": -0.1276474,
            },
        ],
    )
    @clear_cache_first
    def test_carbon_intensity_bad_connection(self) -> None:
        """Given a region ID, a ConnectionError is thrown if the machine cannot connect."""

        with self.assertRaises(ConnectionError):
            with requests_mock.Mocker() as m:
                m.get(
                    f"https://api.co2signal.com/v1/latest?lon=4.6667145&lat=50.6402809",
                    exc=requests.exceptions.ConnectionError,
                )
                CloudRunRegions(self.project_id, self.api_key)._carbon_intensity(
                    "europe-west1"
                )

    @patch("src.data.Geolocation", make_mock_Geolocation())
    @patch(
        "src.constants.ALL_CLOUD_RUN_REGIONS",
        [
            {
                "id": "europe-west1",
                "name": "Belgium",
                "lat": 50.6402809,
                "lon": 4.6667145,
            },
            {
                "id": "europe-west2",
                "name": "London",
                "lat": 51.5073219,
                "lon": -0.1276474,
            },
        ],
    )
    @clear_cache_first
    def test_closest(self) -> None:
        """Pretending we are based in Bristol, London is returned as the closest region, with accompanying CO2 data."""

        regions = CloudRunRegions(self.project_id, self.api_key)
        regions._carbon_intensity = MagicMock(  # type: ignore #https://github.com/python/mypy/issues/2427
            side_effect=mock_carbon_intensity
        )

        obtained = regions.closest
        expected = {
            "carbon_intensity": 200,
            "distance_from_current_location": 171,
            "id": "europe-west2",
            "lat": 51.5073219,
            "lon": -0.1276474,
            "name": "London",
        }
        self.assertEqual(expected, obtained)

    @clear_cache_first
    def test_greenest_bad_region(self) -> None:
        """Given a list of candidate regions containing an invalid one, greenest throws AssertionError."""

        with self.assertRaises(AssertionError):
            CloudRunRegions(self.project_id, self.api_key).greenest(
                ["europe-west2", "fake-region"]
            )

    @clear_cache_first
    def test_greenest_all_cannot_get_carbon_intensity(self) -> None:
        """Given a list of valid candidate regions, if the carbon intensity for ALL of them cannot be found, raise."""
        with self.assertRaises(LookupError):
            with requests_mock.Mocker() as m:
                m.get(
                    f"https://api.co2signal.com/v1/latest?lon=4.6667145&lat=50.6402809",
                    request_headers={"auth-token": self.api_key},
                    status_code=200,
                    text='{"message":"No data"}',
                )
                m.get(
                    f"https://api.co2signal.com/v1/latest?lon=-0.1276474&lat=51.5073219",
                    headers={"auth-token": self.api_key},
                    text='{"message":"No data"}',
                )
                CloudRunRegions(self.project_id, self.api_key).greenest(
                    ["europe-west1", "europe-west2"]
                )

    @clear_cache_first
    def test_greenest_one_region_cannot_get_carbon_intensity(self) -> None:
        """Given a list of valid candidate regions, if the carbon intensity for one of them cannot be found, log a warning and continue."""
        with self.assertLogs() as captured_logs:
            with requests_mock.Mocker() as m:
                m.get(
                    f"https://api.co2signal.com/v1/latest?lon=4.6667145&lat=50.6402809",
                    request_headers={"auth-token": self.api_key},
                    status_code=200,
                    text='{"message":"No data"}',
                )
                m.get(
                    f"https://api.co2signal.com/v1/latest?lon=-0.1276474&lat=51.5073219",
                    headers={"auth-token": self.api_key},
                    text='{"_disclaimer":"This data is the exclusive property of electricityMap and/or related parties. If you\'re in doubt about your rights to use this data, please contact api@co2signal.com","status":"ok","countryCode":"GB","data":{"datetime":"2022-08-19T15:00:00.000Z","carbonIntensity":100,"fossilFuelPercentage":42.02},"units":{"carbonIntensity":"gCO2eq/kWh"}}',
                )
                CloudRunRegions(self.project_id, self.api_key).greenest(
                    ["europe-west1", "europe-west2"]
                )

            expected_log_message = "Could not get carbon intensity data for region europe-west1, so it was skipped."
            self.assertEqual(len(captured_logs.records), 1)
            self.assertEqual(
                expected_log_message, captured_logs.records[0].getMessage()
            )

    @patch(
        "src.data.ALL_CLOUD_RUN_REGIONS",
        [
            {
                "id": "europe-west1",
                "name": "Belgium",
                "lat": 50.6402809,
                "lon": 4.6667145,
            },
            {
                "id": "europe-west2",
                "name": "London",
                "lat": 51.5073219,
                "lon": -0.1276474,
            },
            {
                "id": "europe-west4",
                "name": "Netherlands",
                "lat": 52.2434979,
                "lon": 5.6343227,
            },
            {
                "id": "europe-west6",
                "name": "Zurich",
                "lat": 47.3744489,
                "lon": 8.5410422,
            },
        ],
    )
    @clear_cache_first
    def test_greenest_no_candidate_regions(self) -> None:
        """Given no list of candidate regions, greenest returns the greenest of all possible regions."""

        regions = CloudRunRegions(self.project_id, self.api_key)
        regions._carbon_intensity = MagicMock(  # type: ignore #https://github.com/python/mypy/issues/2427
            side_effect=mock_carbon_intensity
        )

        obtained = regions.greenest()
        expected = {
            "id": "europe-west1",
            "name": "Belgium",
            "lat": 50.6402809,
            "lon": 4.6667145,
            "carbon_intensity": 100,
        }
        self.assertEqual(expected, obtained)

    @patch(
        "src.data.ALL_CLOUD_RUN_REGIONS",
        [
            {
                "id": "europe-west1",
                "name": "Belgium",
                "lat": 50.6402809,
                "lon": 4.6667145,
            },
            {
                "id": "europe-west2",
                "name": "London",
                "lat": 51.5073219,
                "lon": -0.1276474,
            },
            {
                "id": "europe-west4",
                "name": "Netherlands",
                "lat": 52.2434979,
                "lon": 5.6343227,
            },
            {
                "id": "europe-west6",
                "name": "Zurich",
                "lat": 47.3744489,
                "lon": 8.5410422,
            },
        ],
    )
    @clear_cache_first
    def test_greenest_good_candidate_regions(self) -> None:
        """Given a list of good candidate regions, greenest returns the greenest of the candidates."""

        regions = CloudRunRegions(self.project_id, self.api_key)
        regions._carbon_intensity = MagicMock(  # type: ignore #https://github.com/python/mypy/issues/2427
            side_effect=mock_carbon_intensity
        )

        obtained = regions.greenest(["europe-west4", "europe-west6"])
        expected = {
            "id": "europe-west4",
            "name": "Netherlands",
            "lat": 52.2434979,
            "lon": 5.6343227,
            "carbon_intensity": 300,
        }
        self.assertEqual(expected, obtained)
