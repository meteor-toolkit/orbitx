"""orbitx.tests.test_matchup - tests for orbitx.matchup"""

import unittest
import unittest.mock as mock

import numpy as np
import datetime
import xarray as xr

from orbitx import Matchups
from orbitx.utils._matchups.get_dist import get_dist, get_distance
from orbitx.utils._matchups.matchup_dict_to_xarray import _get_range
from orbitx import Orbit

__author__ = "Mattea Goalen <mattea.goalen@npl.co.uk>"


class TestMatchups(unittest.TestCase):
    def test__get_range(self):
        array_1 = np.array([1, 2, 5, 3, 6, 7])
        array_2 = np.array([4, 6, 2, 4, 6, 2])
        array_3 = np.array([5, 4, 2, 9, 4, 3])
        output_array = np.array([4, 4, 3, 6, 2, 4])
        np.array_equal(_get_range(array_1, array_2, array_3), output_array)

    def test_get_dist(self):
        input_1 = (60, 40)
        input_2 = (70, 50)

        self.assertEqual(round(get_dist(*input_1, *input_2), 3), 1203.538)

    def test_get_distance(self):
        lon1 = np.array([40, 45, 50, 55, 60])
        lat1 = np.array([60, 65, 70, 75, 80])
        lon2 = np.array([50, 55, 60, 65, 70])
        lat2 = np.array([70, 75, 80, 85, 90])

        np.array_equal(
            get_distance(lon1, lat1, lon2, lat2).round(3),
            np.array([1203.538, 1171.348, 1144.580, 1124.453, 1111.949]),
        )

    @mock.patch(
        "orbitx.orbit.Orbit.simulate",
        return_value=Orbit(
            satellites = ["S3A", "LS8"],
            start_date = datetime.datetime(1970, 1, 1, 0, 0, 0),
            end_date = datetime.datetime(1970, 1, 1, 0, 0, 0) + datetime.timedelta(seconds = 9),
            propagation_sampling_interval = 2,
            interpolation_sampling_interval = 1,
            reference_date=datetime.datetime(1970, 1, 1, 0, 0, 0),
            orbit = xr.Dataset(
                data_vars = {
                    "reference_date": (0),
                    "time_datetime": ("time", np.array([datetime.datetime(1970, 1, 1, 0, 0, 0) + datetime.timedelta(seconds=float(i)) for i in np.arange(10)])),
                    "lat1": ("time", np.array([1, 2,   3, 4, 5, 6, 7, 8,  9, 10], dtype = float)),
                    "lon1": ("time", np.array([3, 2,   0, 3, 6, 5, 8, 6, 10, 11], dtype = float)),
                    "lat2": ("time", np.array([ 1,  3,  5, 7, 9, 11, 13, 15, 17, 19], dtype = float)),
                    "lon2": ("time", np.array([-3, -2, -1, 0, 1,  2,  3,  4,  5,  6], dtype = float)),
                    "time2": ("time", np.array([float(i) for i in np.arange(10)], dtype = float)),
                    "time_datetime2": ("time", np.array([datetime.datetime(1970, 1, 1, 0, 0, 0) + datetime.timedelta(seconds=float(i)) for i in np.arange(10)]))
                },
                coords = {"time": np.array([float(i) for i in np.arange(10)], dtype = float)},
                attrs={
                    "satellites": ["S3A", "LS8"],
                    "start_date": datetime.datetime(1970, 1, 1, 0, 0, 0),
                    "end_date": datetime.datetime(1970, 1, 1, 0, 0, 0) + datetime.timedelta(seconds = 9),
                    "propagation_sampling_interval": 2,
                    "interpolation_sampling_interval": 1
                }
            )
        )
    )
    @mock.patch("orbitx.matchups.matchup_dict_to_xarray")
    @mock.patch("orbitx.utils._matchups.find_matches.get_distance")
    def test_matchup(self, mock_get_distance, mock_matchup_dict_to_xarray, mock_orbit_simulate):
        def mock_get_dist(lat1, lon1, lat2, lon2):

            dlat = abs(lat1 - lat2)
            dlon = abs(lon1 - lon2)
            return dlon + dlat

        mock_get_distance.side_effect = np.vectorize(mock_get_dist)

        satellites = ["S3A", "LS8"]
        start_date = datetime.datetime(1970, 1, 1, 0, 0, 0)
        end_date = datetime.datetime(1970, 1, 1, 0, 0, 0) + datetime.timedelta(seconds = 9)
        propagation_sampling_interval = 2
        interpolation_sampling_interval = 1
        time_diff_threshold = 3
        space_diff_threshold = 4
        check_before = False
        check_after = False
        has_land_ocean_mask = False

        _ = Matchups.find_matchups(
            satellites = satellites,
            start_date = start_date,
            end_date = end_date,
            propagation_sampling_interval = propagation_sampling_interval,
            interpolation_sampling_interval = interpolation_sampling_interval,
            space_diff_threshold = space_diff_threshold,
            time_diff_threshold = time_diff_threshold,
            check_before = check_before,
            check_after = check_after,
            has_land_ocean_mask = has_land_ocean_mask
        )
        mock_orbit_simulate.assert_called_with(
            satellites = satellites,
            start_date = start_date,
            end_date = end_date,
            propagation_sampling_interval = propagation_sampling_interval,
            interpolation_sampling_interval = interpolation_sampling_interval,
            reference_date = datetime.datetime(1970, 1, 1, 0, 0, 0)
        )
        mock_matchup_dict_to_xarray.assert_called_with(
            {
                "S3A_LS8": {
                    "lat1": np.array([3.0]),
                    "lon1": np.array([0.0]),
                    "lat2": np.array([5.0]),
                    "lon2": np.array([-1.0]),
                    "distance": np.array([3.0]),
                    "time": np.array([2.0]),
                    "time_datetime": np.array([datetime.datetime(1970, 1, 1, 0, 0, 2)], dtype=object),
                    'time2': np.array([2.]),
                    'time_datetime2': np.array([datetime.datetime(1970, 1, 1, 0, 0, 2)], dtype=object),
                    "delay": np.array([0.0]),
                }
            },
            {
            "satellites": satellites,
            "start_date": start_date,
            "end_date": end_date,
            "time_diff_threshold": time_diff_threshold,
            "space_diff_threshold": space_diff_threshold,
            "check_before": check_before,
            "check_after": check_after,
            "has_land_ocean_mask": has_land_ocean_mask,
            "interpolation_sampling_interval": 1,
            "propagation_sampling_interval": 2
            },
        )


if __name__ == "__main__":
    unittest.main()
