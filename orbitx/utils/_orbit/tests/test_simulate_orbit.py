"""orbitx.tests.test_orbit - tests for orbitx.orbit"""

import numpy as np
import unittest
import unittest.mock as mock
import datetime
from orbitx import TLE
from orbitx import __version__
from orbitx.utils._date_utils import sec_since_to_datetime64
from orbitx.utils._orbit.simulate_orbit import simulate_orbit
from orbitx import S6_ORBIT_PATH
import netCDF4 as nc
from math import pi
import xarray as xr

__author__ = "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>"


def cal_dist_d2m(lat1, lon1, lat2, lon2):
    """
    Get lat and lon pairs in degree and return distance in kilometer
    :param lat1:
    :param lon1:
    :param lat2:
    :param lon2:
    :return:
    """
    lon1 = lon1 * pi / 180.0
    lat1 = lat1 * pi / 180.0
    lon2 = lon2 * pi / 180.0
    lat2 = lat2 * pi / 180.0

    R = 6373.0  # radius of the Earth [kms] meaning that the result will also be in kms
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c  # Haversine formula
    return distance


class TestSimulateOrbit(unittest.TestCase):
    def test_valid_simulate_orbit(self):
        # Read sample Sentinel-6 file
        ds = nc.Dataset(S6_ORBIT_PATH[0], mode="r")
        exp_time = np.array(ds.groups["data_01"].variables["time"][:])
        reference_date = np.datetime64("2000-01-01T00:00:00")
        exp_date = [
            sec_since_to_datetime64(
                exp_sec_since, reference_date=reference_date
            )
            for exp_sec_since in exp_time
        ]
        exp_lat = ds.groups["data_01"].variables["latitude"][:]
        exp_lon = ds.groups["data_01"].variables["longitude"][:]
        # Convert start-time and end-time of S6 track to datetime. Notice that altimetry satellites (in this case
        # Sentinel-6MF) do report time as seconds since 2000. This is not to be mistaken with OrbitX's reference time
        # which is 1970.
        S6_start_date = np.min(exp_date)
        S6_end_date = np.max(exp_date)
        # Simulate S6 orbit at 1 Hz
        sat = "S6"
        propagation_sampling_interval = np.array(1, dtype="timedelta64[s]")

        tle = TLE.from_sat_shortname(
            sat,
            S6_start_date,
            S6_end_date,
            reference_date
        )
        sat_secs_since, sat_date, sat_lat_sim, sat_lon_sim = simulate_orbit(
            S6_start_date,
            S6_end_date,
            tle,
            propagation_sampling_interval,
            reference_date,
        )
        
        np.testing.assert_equal(sat_secs_since, exp_time)
        np.testing.assert_equal(sat_date, exp_date)
        # Calculate the Haversine distance between simulated and real orbit at 1 Hz sampling rate
        distance = [
            cal_dist_d2m(sat_lat_sim[i], sat_lon_sim[i], exp_lat[i], exp_lon[i])
            for i in range(len(sat_lat_sim))
        ]
        
        # Make sure that at all instances, the distance is less than 1 km (which is an acceptable deviation for S6)
        self.assertTrue((np.array(distance) < 1).all())

    @mock.patch(
        "orbitx.utils._orbit.simulate_orbit.propagate_orbit",
        return_value=([12], [13], [14], [15], [], [], []),
    )
    @mock.patch(
        "orbitx.utils._orbit.simulate_orbit.get_matching_indices",
        return_value=([7], [0]),
    )
    @mock.patch(
        "orbitx.utils._orbit.simulate_orbit.form_sample_space", return_value=([], [9])
    )
    def test_simulate_orbit_1_tle_ref(self, mock_form_ss, mock_match_idx, mock_prop):
        start_date = np.datetime64("1970-01-01T00:00:00")
        end_date = np.datetime64("1970-01-01T00:00:05")
        
        tle = TLE(
            xr.Dataset(
                data_vars={
                    "reference_date": (np.datetime64("1970-01-01T00:00:00")),
                    "start_date": (start_date),
                    "end_date": (end_date),
                    "tle_date": ("tle_index", [np.datetime64("1970-01-01T00:00:32")]),
                    "line_1": ("tle_index", ["12"]),
                    "line_2": ("tle_index", ["23"]),
                    "reference_date_seconds_since1970": (0),
                    "start_date_seconds_since": (0),
                    "end_date_seconds_since": (5),
                    "tle_date_seconds_since": ("tle_index", [32]),
                    "argument_perigee": ("tle_index", [0]),
                    "balistic_coefficient": ("tle_index", [0]),
                    "drag_term": ("tle_index", [0]),
                    "eccentricity": ("tle_index", [0]),
                    "element_set_number": ("tle_index", [0]),
                    "inclination": ("tle_index", [0]),
                    "mean_anomaly": ("tle_index", [0]),
                    "mean_motion": ("tle_index", [0]),
                    "revolution_number": ("tle_index", [0]),
                    "right_ascension": ("tle_index", [0]),
                    "second_derivative": ("tle_index", [0]),
                },
                coords={"tle_index": [0]},
                attrs={
                    "satellite_shortname": "S6",
                    "satellite_name": "Sentinel-6",
                    "catalog_number": "1",
                    "classification": "2",
                    "launch_number": 101,
                    "launch_piece": "3",
                    "launch_year": 102,
                    "version": __version__,
                    "creation_date": "1980-01-01T00:00:00",
                },
            )
        )
        self.assertEqual(
            simulate_orbit(
                start_date=start_date,
                end_date=end_date,
                tle=tle,
                propagation_sampling_interval=np.array(2, dtype="timedelta64[s]"),
                reference_date=np.datetime64("1970-01-01T00:00:00"),
            ),
            ([12], [13], [14], [15]),
        )
        mock_form_ss.assert_called_with(
            np.datetime64("1970-01-01T00:00:00"),
            np.datetime64("1970-01-01T00:00:05"),
            np.array(2, dtype="timedelta64[s]"),
            np.datetime64("1970-01-01T00:00:00"),
        )
        mock_match_idx.assert_called_with([9], [32])
        mock_prop.assert_called_with(
            "12",
            "23",
            np.datetime64("1970-01-01T00:00:00"),
            np.datetime64("1970-01-01T00:00:05"),
            np.array(2, dtype="timedelta64[s]"),
            np.datetime64("1970-01-01T00:00:00"),
        )

    @mock.patch(
        "orbitx.utils._orbit.simulate_orbit.propagate_orbit",
        return_value=([12], [13], [14], [15], [], [], []),
    )
    @mock.patch(
        "orbitx.utils._orbit.simulate_orbit.get_matching_indices",
        return_value=([7], [0]),
    )
    @mock.patch(
        "orbitx.utils._orbit.simulate_orbit.form_sample_space", return_value=(
            [
                np.datetime64("1970-01-01T00:00:00"),
                np.datetime64("1970-01-01T00:00:30"),
                np.datetime64("1970-01-01T00:01:00")
            ],
            [
                314
            ]
        )
    )
    def test_simulate_orbit_2_tle_ref(
        self, mock_form_smpl, mock_get_mtch_idx, mock_prop_orb
    ):
        start_date = np.datetime64("1970-01-01T00:00:00")
        end_date = np.datetime64("1970-01-01T00:01:00")
        propagation_sampling_interval=np.array(30, dtype="timedelta64[s]")

        tle = TLE(
            xr.Dataset(
                data_vars={
                    "reference_date": (np.datetime64("1970-01-01T00:00:00")),
                    "start_date": (start_date),
                    "end_date": (end_date),
                    "tle_date": ("tle_index", [np.datetime64("1970-01-01T00:00:00")]),
                    "line_1": ("tle_index", ["1"]),
                    "line_2": ("tle_index", ["3"]),
                    "reference_date_seconds_since1970": (0),
                    "start_date_seconds_since": (0),
                    "end_date_seconds_since": (5),
                    "tle_date_seconds_since": ("tle_index", [13]),
                    "argument_perigee": ("tle_index", [0]),
                    "balistic_coefficient": ("tle_index", [0]),
                    "drag_term": ("tle_index", [0]),
                    "eccentricity": ("tle_index", [0]),
                    "element_set_number": ("tle_index", [0]),
                    "inclination": ("tle_index", [0]),
                    "mean_anomaly": ("tle_index", [0]),
                    "mean_motion": ("tle_index", [0]),
                    "revolution_number": ("tle_index", [0]),
                    "right_ascension": ("tle_index", [0]),
                    "second_derivative": ("tle_index", [0]),
                },
                coords={"tle_index": [0]},
                attrs={
                    "satellite_shortname": "S6",
                    "satellite_name": "Sentinel-6",
                    "catalog_number": "1",
                    "classification": "2",
                    "launch_number": 101,
                    "launch_piece": "3",
                    "launch_year": 102,
                    "version": __version__,
                    "creation_date": "1980-01-01T00:00:00",
                },
            )
        )

        self.assertEqual(
            simulate_orbit(
                start_date=start_date,
                end_date=end_date,
                tle = tle,
                propagation_sampling_interval=propagation_sampling_interval,
                reference_date=np.datetime64("1970-01-01T00:00:00"),
            ),
            ([12], [13], [14], [15]),
        )
        mock_form_smpl.assert_called_with(
            np.datetime64("1970-01-01T00:00:00"),
            np.datetime64("1970-01-01T00:01:00"),
            np.array(30, dtype="timedelta64[s]"),
            np.datetime64("1970-01-01T00:00:00"),
        )
        mock_form_smpl.assert_called_once()
        mock_get_mtch_idx.assert_called_with(
            [314],
            [13]
        )
        mock_get_mtch_idx.assert_called_once()
        mock_prop_orb.assert_called_with(
            np.str_("1"),
            np.str_("3"),
            np.datetime64("1970-01-01T00:00:00"),
            np.datetime64("1970-01-01T00:01:00"),
            np.array(30, dtype="timedelta64[s]"),
            np.datetime64("1970-01-01T00:00:00"),
        )
        mock_prop_orb.assert_called_once()

if __name__ == "__main__":
    unittest.main()
