from datetime import time
from math import floor
from typing import Sequence

from pandas import read_csv


def half_hour_block(at: time) -> int:
    return at.hour * 2 + floor(at.minute / 30)


class CarbonIntensityData:

    def __init__(self):
        self.data = read_csv("data.csv")

    def greenest_region(self, candidate_regions: Sequence[str], at_time: time) -> str:
        row_number_for_optimal_region = \
            self.data[(self.data["Region"].isin(candidate_regions)) &
                      (self.data["Block"] == half_hour_block(at_time))]["Intensity_gCO2_kWh"].idxmin()

        return self.data["Region"][row_number_for_optimal_region]
