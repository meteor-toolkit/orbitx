"""orbitx.tests.test_matchup - tests for orbitx.matchup"""

import unittest
import unittest.mock as mock

import numpy as np
import datetime as dt

from orbitx.matchup import Matchups, get_range, get_distance, get_dist

__author__ = "Mattea Goalen <mattea.goalen@npl.co.uk>"


class TestMatchups(unittest.TestCase):
    def test_get_range(self):
        array_1 = np.array([1, 2, 5, 3, 6, 7])
        array_2 = np.array([4, 6, 2, 4, 6, 2])
        array_3 = np.array([5, 4, 2, 9, 4, 3])
        output_array = np.array([4, 4, 3, 6, 2, 4])
        np.array_equal(get_range(array_1, array_2, array_3), output_array)

    def test_get_dist(self):
        input_1 = (40, 60)
        input_2 = (50, 70)

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

    @mock.patch("orbitx.matchup.Matchups.to_ds")
    @mock.patch("orbitx.matchup.get_distance")
    def test_matchup(self, mock_get_dist, mock_to_ds):
        def mock_get_distance(lon1, lat1, lon2, lat2):
            dlon = abs(lon1 - lon2)
            dlat = abs(lat1 - lat2)
            return dlon + dlat

        mock_get_dist.side_effect = np.vectorize(mock_get_distance)

        input_orbits = {
            "S3A": {
                "lat": np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
                "lon": np.array([2, 1, 0, 3, 6, 5, 8, 6, 10, 11]),
                "time": [float(i) for i in np.arange(10)],
            },
            "LS8": {
                "lat": np.array([1, 3, 5, 7, 9, 11, 13, 15, 17, 19]),
                "lon": np.array([-3, -2, -1, 0, 1, 2, 3, 4, 5, 6]),
                "time": [float(i) for i in np.arange(10)],
            },
        }
        time_diff_threshold = 3
        cntr2cntr_dist = 4
        np.array(
            [
                1,
                np.sqrt(2),
                np.sqrt(13),
                np.sqrt(34),
            ]
        )
        matchup = Matchups()
        matchup.matchup(input_orbits, time_diff_threshold, cntr2cntr_dist)

        mock_to_ds.assert_called_with(
            {
                "S3A_LS8": {
                    "lat1": np.array([3.0]),
                    "lon1": np.array([0.0]),
                    "lat2": np.array([7.0]),
                    "lon2": np.array([0.0]),
                    "delay": np.array([-1.0]),
                    "time": np.array([dt.datetime(1970, 1, 1, 0, 0, 2)], dtype=object),
                    "distance": np.array([4.0]),
                }
            },
            {
                "time_threshold": 3,
                "distance_threshold": 4,
                "interpolation_sampling_interval": 1.0,
            },
        )

    def test_to_ds(self):
        pass


if __name__ == "__main__":
    unittest.main()
