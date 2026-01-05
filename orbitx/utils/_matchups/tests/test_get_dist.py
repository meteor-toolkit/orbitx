"""orbitx.tests.test_matchup - tests for orbitx.matchup"""

import unittest

import numpy as np
import xarray as xr
from orbitx.utils._matchups.get_dist import get_dist

__author__ = "Mattea Goalen <mattea.goalen@npl.co.uk>"


class TestGetDist(unittest.TestCase):
    def test_get_dist_1_existing(self):
        existing_orbits = xr.Dataset(
            data_vars={
                "lat": (["matchup_index", "satellite"], np.array([60, 65, 70, 75, 80])[:, np.newaxis]),
                "lon": (["matchup_index", "satellite"], np.array([40, 45, 50, 55, 60])[:, np.newaxis]),
            },
            coords={
                "matchup_index": np.arange(5),
                "satellite": [""]
            }
        )

        new_orbit = xr.Dataset(
            data_vars={
                "lat": (["matchup_index", "satellite"], np.array([70, 75, 80, 85, 90])[:, np.newaxis]),
                "lon": (["matchup_index", "satellite"], np.array([50, 55, 60, 65, 70])[:, np.newaxis]),
            },
            coords={
                "matchup_index": np.arange(5),
                "satellite": [""]
            }
        )

        np.array_equal(
            get_dist(existing_orbits, new_orbit).round(3),
            np.array([1203.538, 1171.348, 1144.580, 1124.453, 1111.949]),
        )

        
    def test_get_dist_2_existing(self):
        existing_orbits = xr.Dataset(
            data_vars={
                "lat": (["matchup_index", "satellite"], np.array([[60, 65, 70, 75, 80], [60, 65, 70, 75, 80]]).transpose()),
                "lon": (["matchup_index", "satellite"], np.array([[40, 45, 50, 55, 60], [40, 45, 50, 55, 60]]).transpose()),
            },
            coords={
                "matchup_index": np.arange(5),
                "satellite": ["0", "1"]
            }
        )

        new_orbit = xr.Dataset(
            data_vars={
                "lat": (["matchup_index", "satellite"], np.array([70, 75, 80, 85, 90])[:, np.newaxis]),
                "lon": (["matchup_index", "satellite"], np.array([50, 55, 60, 65, 70])[:, np.newaxis]),
            },
            coords={
                "matchup_index": np.arange(5),
                "satellite": ["2"]
            }
        )

        np.array_equal(
            get_dist(existing_orbits, new_orbit).round(3),
            np.array([[1203.538, 1171.348, 1144.580, 1124.453, 1111.949], [1203.538, 1171.348, 1144.580, 1124.453, 1111.949]]).transpose(),
        )


if __name__ == "__main__":
    unittest.main()
