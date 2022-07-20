"""
Copyright 2022 OVO Energy Ltd

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import logging
from datetime import timedelta
from json import loads
from time import sleep
from typing import Sequence, Optional

import requests_cache
from geocoder import ip, osm, distance
from googleapiclient.discovery import build


class CloudRunRegions:
    def __init__(self, project_id: str, co2_signal_api_key: str) -> None:
        """
        Location and carbon intensity data for regions supported by Google Cloud Run.
        :param project_id: The GCP project to connect to.
        :param co2_signal_api_key: The auth token for the CO2 Signal API from which to obtain carbon intensity data.
        """
        self.project_id = project_id
        self.co2_signal_api_key = co2_signal_api_key

        self.__all = self.__get_all_regions()

    def __get_all_regions(self) -> list[dict[str, str | float]]:
        client = build("run", "v1")
        raw = (
            client.projects()
            .locations()
            .list(name=f"projects/{self.project_id}")
            .execute()["locations"]
        )

        all_regions: list[dict[str, str | float]] = []
        for region in raw:
            try:
                geojson = osm(region["displayName"]).geojson["features"][0][
                    "properties"
                ]
                all_regions.append(
                    {
                        "id": str(region["locationId"]),
                        "name": str(region["displayName"]),
                        "lat": float(geojson["lat"]),
                        "lon": float(geojson["lng"]),
                    }
                )
            except IndexError:  # Isolated to a single location. Other types should throw loudly.
                logging.warning(
                    f"Could not get geolocation data for region {region['locationId']}"
                )

        return all_regions

    @property
    def closest(self) -> dict[str, str | float | int]:
        """
        Return the Google Cloud region closest to this machine.
        :return: A dictionary of data about the closest region.
        """
        geolocation = ip("me").latlng

        here = dict()
        here["lat"], here["lon"] = geolocation[0], geolocation[1]

        distances_from_here = [
            region
            | {
                "distance_from_current_location": int(
                    distance((here["lat"], here["lon"]), (region["lat"], region["lon"]))
                )
            }
            for region in self.__all
        ]

        closest = min(
            distances_from_here, key=lambda x: x["distance_from_current_location"]
        )

        return closest | {
            "carbon_intensity": self.__carbon_intensity(str(closest["id"]))
        }

    def greenest(
            self, candidate_regions: Optional[Sequence[str]] = None
    ) -> dict[str, str | float | int]:
        """
        Return the Google Cloud region with the lowest carbon intensity now.
        :param candidate_regions: A sequence of region IDs from which to select the greenest, or None to select from all
        regions.
        :return: A dictionary of data about the greenest region.
        """

        if candidate_regions:
            assert set(candidate_regions).issubset(
                {region["id"] for region in self.__all}
            ), f"Invalid region(s) provided. Allowed Cloud Run regions: {self.__all}"
            regions = [
                region for region in self.__all if region["id"] in candidate_regions
            ]

        else:
            regions = self.__all

        carbon_intensity_for_candidate_regions: list[dict[str, str | float | int]] = []

        for region in regions:
            try:
                carbon_intensity_for_candidate_regions.append(
                    region
                    | {"carbon_intensity": self.__carbon_intensity(str(region["id"]))}
                )
            except LookupError:  # Skip over errors for individual regions.
                logging.warning(
                    f"Could not get carbon intensity data for region {region['id']}, so it was skipped."
                )

        if (
                carbon_intensity_for_candidate_regions == []
        ):  # If all regions failed, throw now.
            raise LookupError(f"Could not get carbon intensity data for any region.")

        return min(
            carbon_intensity_for_candidate_regions, key=lambda x: x["carbon_intensity"]
        )

    def __carbon_intensity(self, region: str) -> int:
        """
        Return the carbon intensity of a Google Cloud Region with a given ID, using data from CO2 Signal API.
        Uses locally-cached API data where possible, to prevent hitting rate limits.
        :param region: The ID of the region.
        :return: The carbon intensity (in gCO2eq/kWh)
        """
        sleep(1)  # To avoid API rate limits.
        region_obj = [r for r in self.__all if region == r["id"]][0]

        try:
            session = requests_cache.CachedSession("co2_signal_cache", expire_after=timedelta(hours=1))
            request = session.get(
                f"https://api.co2signal.com/v1/latest?lon={region_obj['lon']}&lat={region_obj['lat']}",
                headers={"auth-token": self.co2_signal_api_key},
            )
            assert (
                    request.status_code == 200
            ), f"Got bad response code {request.status_code} from CO2 Signal API."
        except Exception as e:
            raise ConnectionError(
                f"Failed to get carbon intensity data from CO2 Signal. Check your internet connection and API key.\n{repr(e)}"
            )
        response = loads(request.content)

        if "carbonIntensity" not in response["data"].keys():
            raise LookupError(
                f"Carbon intensity data not available from CO2 Signal for region {region}."
            )
        return int(response["data"]["carbonIntensity"])
