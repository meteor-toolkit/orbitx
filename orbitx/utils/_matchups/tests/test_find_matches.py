"""orbitx.tests.test_matchup - tests for orbitx.matchup"""

import unittest
import unittest.mock as mock

import numpy as np
import xarray as xr
from math import pi
from orbitx.utils._matchups import find_matches
from orbitx import Orbit
from orbitx import __version__

__author__ = "Mattea Goalen <mattea.goalen@npl.co.uk>"


class TestFindMatches(unittest.TestCase):
    @mock.patch("orbitx.utils._matchups.find_matches.get_dist")
    def test_find_matches_2_orbits(self, mock_get_distance):
        def mock_get_dist(existing_orbits, new_orbit):
            dlon = np.abs((existing_orbits["lon"] - new_orbit["lon"]))
            dlat = np.abs((existing_orbits["lat"] - new_orbit["lat"]))
            return dlon + dlat

        mock_get_distance.side_effect = mock_get_dist

        satellites = ["S3A", "LS8"]
        time_diff_threshold = np.array(1, dtype="timedelta64[s]")
        space_diff_threshold = 4.0
        check_before = False
        check_after = False
        has_land_ocean_mask = False

        orbit = Orbit(
            xr.Dataset(
                data_vars={
                    "reference_date": (np.datetime64("1970-01-01T00:00:00")),
                    "time_datetime": (
                        ["time"],
                        np.linspace(0, 3, 4, dtype="datetime64[s]"),
                    ),
                    "lat": (
                        ["time", "satellite"],
                        np.array([[1, 2, 3, 4], [2, 3, 5, 8]]).transpose() * 180 / pi,
                    ),
                    "lon": (
                        ["time", "satellite"],
                        np.array([[3, 2, 0, 3], [-1, -2, -1, 0]]).transpose() * 180 / pi,
                    ),
                },
                coords={
                    "time": np.array(np.arange(4), dtype=float),
                    "satellite": ["S3A", "LS8"],
                },
                attrs={
                    "satellite_shortname": ["S3A", "LS8"],
                    "satellite_name": ["Sentinel-3A", "Landsat-8"],
                    "start_date": 0,
                    "end_date": 9,
                    "propagation_sampling_interval": 2,
                    "interpolation_sampling_interval": 1,
                    "version": __version__,
                    "creation_date": np.datetime64("1980-01-01T00:00:00"),
                },
            )
        )
        expected_result = xr.Dataset(
            data_vars={
                "reference_date": (np.datetime64("1970-01-01T00:00:00")),
                "time_datetime": (
                    ["matchup_index", "satellite"],
                    [
                        [
                            np.datetime64("1970-01-01T00:00:01"),
                            np.datetime64("1970-01-01T00:00:00"),
                        ],
                        [
                            np.datetime64("1970-01-01T00:00:02"),
                            np.datetime64("1970-01-01T00:00:02"),
                        ],
                    ],
                ),
                "time": (
                    ["matchup_index", "satellite"],
                    [[1, 0], [2, 2]],
                ),
                "lat": (
                    ["matchup_index", "satellite"],
                    np.array([[2, 2], [3, 5]]) * 180 / pi,
                ),
                "lon": (
                    ["matchup_index", "satellite"],
                    np.array([[2, -1], [0, -1]]) * 180 / pi,
                ),
                "distance": (
                    ["matchup_index", "satellite_pair"],
                    np.array([[3], [3]]),
                ),
                "delay": (
                    ["matchup_index", "satellite_pair"],
                    np.array([[1], [0]], dtype="timedelta64[s]"),
                ),
            },
            coords={
                "matchup_index": np.arange(2),
                "satellite": satellites,
                "satellite_pair": ["S3A_LS8"],
            },
            attrs={
                "satellite_shortname": satellites,
                "satellite_name": ["Sentinel-3A", "Landsat-8"],
                "start_date": 0,
                "end_date": 9,
                "propagation_sampling_interval": 2,
                "interpolation_sampling_interval": 1,
                "time_diff_threshold": time_diff_threshold.item().total_seconds(),
                "space_diff_threshold": space_diff_threshold,
                "check_before": int(check_before),
                "check_after": int(check_after),
                "has_land_ocean_mask": int(has_land_ocean_mask),
                "version": __version__,
                "creation_date": str(np.datetime64("now")),
            },
        )

        matchups = find_matches(
            orbit=orbit,
            time_diff_threshold=time_diff_threshold,
            space_diff_threshold=space_diff_threshold,
            check_before=check_before,
            check_after=check_after,
            has_land_ocean_mask=has_land_ocean_mask,
        )
        xr.testing.assert_equal(matchups, expected_result)

    @mock.patch("orbitx.utils._matchups.find_matches.get_dist")
    def test_find_matches_3_orbits(self, mock_get_distance):
        def mock_get_dist(existing_orbits, new_orbit):
            dlon = np.abs((existing_orbits["lon"] - new_orbit["lon"]))
            dlat = np.abs((existing_orbits["lat"] - new_orbit["lat"]))
            return dlon + dlat

        mock_get_distance.side_effect = mock_get_dist

        satellites = ["S3A", "LS8", "S6"]
        time_diff_threshold = np.array(1, dtype="timedelta64[s]")
        space_diff_threshold = 4.0
        check_before = False
        check_after = False
        has_land_ocean_mask = False

        orbit = Orbit(
            xr.Dataset(
                data_vars={
                    "reference_date": (np.datetime64("1970-01-01T00:00:00")),
                    "time_datetime": (
                        ["time"],
                        np.linspace(0, 3, 4, dtype="datetime64[s]"),
                    ),
                    "lat": (
                        ["time", "satellite"],
                        np.array(
                            [
                                [1, 2, 3, 4],
                                [2, 3, 5, 8],
                                [2, 3, 5, 8],
                            ]
                        ).transpose()
                        * 180
                        / pi,
                    ),
                    "lon": (
                        ["time", "satellite"],
                        np.array(
                            [
                                [3, 2, 0, 3],
                                [-1, -2, -1, 0],
                                [-1, -2, -1, 0],
                            ]
                        ).transpose()
                        * 180
                        / pi,
                    ),
                },
                coords={
                    "time": np.array(np.arange(4), dtype=float),
                    "satellite": satellites,
                },
                attrs={
                    "satellite_shortname": satellites,
                    "satellite_name": ["Sentinel-3A", "Landsat-8", "Sentinel-6"],
                    "start_date": 0,
                    "end_date": 9,
                    "propagation_sampling_interval": 2,
                    "interpolation_sampling_interval": 1,
                    "version": __version__,
                    "creation_date": np.datetime64("1980-01-01T00:00:00"),
                },
            )
        )
        expected_result = xr.Dataset(
            data_vars={
                "reference_date": (np.datetime64("1970-01-01T00:00:00")),
                "time_datetime": (
                    ["matchup_index", "satellite"],
                    [
                        [
                            np.datetime64("1970-01-01T00:00:01"),
                            np.datetime64("1970-01-01T00:00:00"),
                            np.datetime64("1970-01-01T00:00:00"),
                        ],
                        [
                            np.datetime64("1970-01-01T00:00:02"),
                            np.datetime64("1970-01-01T00:00:02"),
                            np.datetime64("1970-01-01T00:00:02"),
                        ],
                    ],
                ),
                "time": (
                    ["matchup_index", "satellite"],
                    [[1, 0, 0], [2, 2, 2]],
                ),
                "lat": (
                    ["matchup_index", "satellite"],
                    np.array([[2, 2, 2], [3, 5, 5]]) * 180 / pi,
                ),
                "lon": (
                    ["matchup_index", "satellite"],
                    np.array([[2, -1, -1], [0, -1, -1]]) * 180 / pi,
                ),
                "distance": (
                    ["matchup_index", "satellite_pair"],
                    np.array([[3, 3, 0], [3, 3, 0]]),
                ),
                "delay": (
                    ["matchup_index", "satellite_pair"],
                    np.array([[1, 1, 0], [0, 0, 0]], dtype="timedelta64[s]"),
                ),
            },
            coords={
                "matchup_index": np.arange(2),
                "satellite": satellites,
                "satellite_pair": ["S3A_LS8", "S3A_S6", "LS8_S6"],
            },
            attrs={
                "satellite_shortname": satellites,
                "satellite_name": ["Sentinel-3A", "Landsat-8", "Sentinel-6"],
                "start_date": 0,
                "end_date": 9,
                "propagation_sampling_interval": 2,
                "interpolation_sampling_interval": 1,
                "time_diff_threshold": time_diff_threshold.item().total_seconds(),
                "space_diff_threshold": space_diff_threshold,
                "check_before": int(check_before),
                "check_after": int(check_after),
                "has_land_ocean_mask": int(has_land_ocean_mask),
                "version": __version__,
                "creation_date": str(np.datetime64("now")),
            },
        )

        matchups = find_matches(
            orbit=orbit,
            time_diff_threshold=time_diff_threshold,
            space_diff_threshold=space_diff_threshold,
            check_before=check_before,
            check_after=check_after,
            has_land_ocean_mask=has_land_ocean_mask,
        )
        xr.testing.assert_equal(matchups, expected_result)


if __name__ == "__main__":
    unittest.main()
