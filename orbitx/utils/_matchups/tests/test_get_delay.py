"""orbitx.tests.test_matchup - tests for orbitx.matchup"""

import unittest

import numpy as np
import xarray as xr

from orbitx.utils._matchups.get_delay import get_delay

__author__ = "Mattea Goalen <mattea.goalen@npl.co.uk>"


class TestGetDelay(unittest.TestCase):
    def test_get_delay_1_existing(self):
        existing_orbits = xr.Dataset(
            data_vars={
                "time_datetime": (
                    ["matchup_index", "satellite"],
                    np.array([
                        "1970-01-01T00:00:00",
                        "1970-01-01T00:00:00",
                        "1970-01-01T00:00:00"
                    ], dtype = "datetime64[s]")[:, np.newaxis]),
            },
            coords={
                "matchup_index": np.arange(3),
                "satellite": [""]
            }
        )

        new_orbit = xr.Dataset(
            data_vars={
                "time_datetime": (
                    ["matchup_index", "satellite"],
                    np.array([
                        "1970-01-01T00:00:00",
                        "1969-12-31T23:59:55",
                        "1970-01-01T00:00:05",
                    ], dtype = "datetime64[s]")[:, np.newaxis]),
            },
            coords={
                "matchup_index": np.arange(3),
                "satellite": [""]
            }
        )

        np.array_equal(
            get_delay(existing_orbits, new_orbit),
            np.array([
                0,
                -5,
                5
            ], dtype = "timedelta64[s]"),
        )

        
    def test_get_delay_2_existing(self):
        existing_orbits = xr.Dataset(
            data_vars={
                "time_datetime": (
                    ["matchup_index", "satellite"],
                    np.array([
                        ["1970-01-01T00:00:00", "1970-01-01T00:00:00"],
                        ["1970-01-01T00:00:00", "1970-01-01T00:00:00"],
                        ["1970-01-01T00:00:00", "1970-01-01T00:00:00"]
                    ], dtype = "datetime64[s]")),
            },
            coords={
                "matchup_index": np.arange(3),
                "satellite": ["0", "1"]
            }
        )

        new_orbit = xr.Dataset(
            data_vars={
                "time_datetime": (
                    ["matchup_index", "satellite"],
                    np.array([
                        "1970-01-01T00:00:00",
                        "1969-12-31T23:59:55",
                        "1970-01-01T00:00:05",
                    ], dtype = "datetime64[s]")[:, np.newaxis]),
            },
            coords={
                "matchup_index": np.arange(3),
                "satellite": ["2"]
            }
        )

        np.array_equal(
            get_delay(existing_orbits, new_orbit),
            np.array([
                [0, 0],
                [-5, -5],
                [5, 5]
            ], dtype = "timedelta64[s]"),
        )



if __name__ == "__main__":
    unittest.main()
