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

import codecs
import csv
from datetime import time
from math import floor
from typing import Sequence, Optional

from pkg_resources import resource_stream


def half_hour_block(at: time) -> int:
    return at.hour * 2 + floor(at.minute / 30)


class CarbonIntensityData:
    def __init__(self) -> None:
        data_csv_resource = resource_stream(__name__, "data/data.csv")
        self.__data = list(csv.DictReader(codecs.getreader("utf-8")(data_csv_resource)))
        data_csv_resource.close()

    def greenest_region(
        self, at: time, candidate_regions: Optional[Sequence[str]] = None
    ) -> str:
        """
        Return the Google Cloud region with the lowest carbon intensity at at_time.
        :param candidate_regions: A sequence of regions from which to select the greenest, or None to select from all
        regions.
        :param at: The time at which to measure the carbon intensity of the regions.
        :return:
        """

        return min(
            [
                item
                for item in self.__data
                if (candidate_regions is None or item["Region"] in candidate_regions)
                and int(item["Block"]) == half_hour_block(at)
            ],
            key=lambda x: float(x["Intensity_gCO2_kWh"]),
        )["Region"]
