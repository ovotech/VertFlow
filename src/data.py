import codecs
import csv
from datetime import time
from math import floor
from typing import Sequence

from pkg_resources import resource_stream


def half_hour_block(at: time) -> int:
    return at.hour * 2 + floor(at.minute / 30)


class CarbonIntensityData:

    def __init__(self):
        self.data = list(csv.DictReader(codecs.getreader("utf-8")(resource_stream(__name__, "data/data.csv"))))

    def greenest_region(self, candidate_regions: Sequence[str], at_time: time) -> str:
        return min([item for item in self.data if
                    item["Region"] in candidate_regions and int(item["Block"]) == half_hour_block(at_time)],
                   key=lambda x: float(x["Intensity_gCO2_kWh"]))["Region"]
