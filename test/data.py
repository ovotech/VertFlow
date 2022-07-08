from datetime import time
from unittest import TestCase

from src.data import half_hour_block, CarbonIntensityData


class TestData(TestCase):
    def setUp(self) -> None:
        self.data = CarbonIntensityData()

    def test_half_hour_block(self) -> None:
        self.assertEqual(half_hour_block(time(0, 0, 0)), 0)
        self.assertEqual(half_hour_block(time(23, 45, 0)), 47)
        self.assertEqual(half_hour_block(time(12, 45, 38)), 25)

    def test_greenest_region(self) -> None:
        self.assertEqual(self.data.greenest_region(time(0, 0, 0)), "europe-north1")
        self.assertEqual(
            self.data.greenest_region(time(0, 0, 0), ["us-east1", "us-west1"]),
            "us-west1",
        )
