"""orbitx.test.test_get_2LEs - tests for orbitx.get_2LEs"""
import numpy as np
import os.path
import random
import string
import shutil
import unittest
import datetime
from orbitx.tle import TLEInfo
from orbitx import add_to_tle_path
from pathlib import Path
from datetime import datetime as dt
from orbitx.orbit import Orbit
from orbitx import S6_ORBIT_PATH
import netCDF4 as nc
from math import pi

__author__ = "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>"


class TestORBIT(unittest.TestCase):
    def test_form_sample_space(self):
        # Start at 1st of Jan. 2000, and sample every 12 hours until 2nd of Jan. 2000, one o'clock am.
        start_time = datetime.datetime(2000, 1, 1)
        end_time = datetime.datetime(2000, 1, 2, 1)
        prop_smpl_interval = 12 * 60 * 60

        # We are expecting 3 samples:
        exp_smpl_space = [
            datetime.datetime(2000, 1, 1, 0, 0),
            datetime.datetime(2000, 1, 1, 12, 0),
            datetime.datetime(2000, 1, 2, 0, 0),
        ]
        exp_smpl_space_secs_since_2000 = np.array([0.0, 43200.0, 86400.0])

        smpl_space, smpl_space_secs_since_2000 = Orbit.form_sample_space(
            start_time, end_time, prop_smpl_interval
        )

        self.assertEqual(exp_smpl_space, smpl_space)
        self.assertTrue(
            (exp_smpl_space_secs_since_2000 == smpl_space_secs_since_2000).all()
        )

    def test_get_matching_indices(self):
        # attention:
        # When testing this function, tle_time should not contain any value which is smaller than the smallest value of
        # sim_time, or greater than the greatest value of sim_time, because we force this onto the process. There is
        # only one exception to this rule, and that is when the [start-time, end-time] is so short, that there is no
        # TLE in between. In that case, we use the closest available TLE to propagate the orbit, and the case is handled
        # as an exception.

        tle_time = [1, 4, 7, 10, 15, 17]  # These are the TLE time stamps
        sim_time = [
            1,
            1.5,
            2,
            3,
            4.2,
            6.7,
            8,
            9,
            10,
            78,
        ]  # These are the simulation (propagation) time stamps

        exp_idx_tle = [
            0,
            1,
            2,
            3,
            5,
        ]  # These are the indices of the corresponding time stamps in TLE time vector
        exp_idx_sim = [
            0,
            4,
            6,
            8,
            9,
        ]  # These are the indices of the corresponding time stamps in simulation vector

        idx_sim, idx_tle = Orbit.get_matching_indices(
            np.array(sim_time), np.array(tle_time)
        )

        self.assertEqual(exp_idx_tle, idx_tle)
        self.assertEqual(exp_idx_sim, idx_sim)

    def test_simulate_orbit(self):
        # Read sample Sentinel-6 file
        ds = nc.Dataset(S6_ORBIT_PATH[0], mode="r")
        exp_time = ds.groups["data_01"].variables["time"][:]
        exp_lat = ds.groups["data_01"].variables["latitude"][:]
        exp_lon = ds.groups["data_01"].variables["longitude"][:]

        # Convert start-time and end-time of S6 track to datetime
        S6_start_time = datetime.timedelta(seconds=exp_time[0]) + datetime.datetime(
            2000, 1, 1, 0, 0, 0
        )
        S6_end_time = datetime.timedelta(
            seconds=exp_time[len(exp_time) - 1]
        ) + datetime.datetime(2000, 1, 1, 0, 0, 0)

        # Simulate S6 orbit at 1 Hz
        sat = "S6"
        propagation_sampling_interval = 1

        tle = TLEInfo()
        orbit = Orbit()
        orbit.start_time = S6_start_time
        orbit.end_time = S6_end_time

        tle_info = tle.get_tle(sat, S6_start_time, S6_end_time)
        time, lat, lon = orbit.simulate_orbit(*tle_info, propagation_sampling_interval)

        # Calculate the Haversine distance between simulated and real orbit at 1 Hz sampling rate
        distance = [
            cal_dist_d2m(lat[i], lon[i], exp_lat[i], exp_lon[i])
            for i in range(len(lat))
        ]
        # Make sure that at all instances, the distance is less than 1 km (which is an acceptable deviation for S6)
        self.assertTrue((np.array(distance) < 1).all())

    def test_interpolate_orbit(self):
        sat_sec_since = [0, 86400]
        sat_lat_sim = [0, 24]
        sat_lon_sim = [0, 24]
        interpolation_sampling_interval = 60 * 60  # interpolate to every one hour

        exp_time = np.arange(0, 86400, 3600)
        exp_lat = [i for i in range(0, 24)]
        exp_lon = [i for i in range(0, 24)]

        orbit = Orbit()
        orbit.start_time = datetime.datetime(2000, 1, 1)
        orbit.end_time = datetime.datetime(2000, 1, 2)

        lat, lon, time = orbit.interpolate_orbit(
            np.array(sat_sec_since),
            np.array(sat_lat_sim),
            np.array(sat_lon_sim),
            interpolation_sampling_interval,
        )

        self.assertTrue((exp_lat == lat).all())
        self.assertTrue((exp_lon == lon).all())
        self.assertTrue((exp_time == time).all())


if __name__ == "__main__":
    unittest.main()


# TODO - Ask whether you can simply use a new function inside your test_X.
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
