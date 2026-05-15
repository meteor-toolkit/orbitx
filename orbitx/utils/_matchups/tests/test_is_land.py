"""orbitx.tests.test_matchup - tests for orbitx.matchup"""

import unittest
import os

import numpy as np
import pandas as pd

from orbitx import data_directory
from orbitx.utils._matchups import is_land

__author__ = "Mattea Goalen <mattea.goalen@npl.co.uk>"


class TestIsLand(unittest.TestCase):
    def test_is_land_capitals(self):
        file_path = os.path.join(data_directory, "world_capitals.csv")
        capital_list = pd.read_csv(file_path, index_col=0, header=0)
        self.assertTrue(
            np.all(is_land(capital_list["Longitude"], capital_list["Latitude"]))
        )

    def test_is_land_seas(self):
        file_path = os.path.join(data_directory, "sea_list.csv")
        sea_list = pd.read_csv(file_path, index_col=0, header=0)
        self.assertTrue(
            np.all(np.logical_not(is_land(sea_list["Longitude"], sea_list["Latitude"])))
        )


if __name__ == "__main__":
    unittest.main()
