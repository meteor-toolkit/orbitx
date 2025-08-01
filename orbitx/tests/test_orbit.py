"""orbitx.tests.test_orbit - tests for orbitx.orbit"""

import numpy as np
import unittest
import unittest.mock as mock
import datetime
from orbitx.tle import TLEInfo
from orbitx.orbit import Orbit, AbsoluteDate
from orbitx import S6_ORBIT_PATH
import netCDF4 as nc
from math import pi

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


class TestORBIT(unittest.TestCase):
    def test_form_sample_space(self):
        # Start at 1st of Jan. 1970, and sample every 12 hours until 2nd of Jan. 1970, one o'clock am.
        start_time = datetime.datetime(1970, 1, 1)
        end_time = datetime.datetime(1970, 1, 2, 1)
        prop_smpl_interval = 12 * 60 * 60

        # We are expecting 4 samples:
        exp_smpl_space = [
            datetime.datetime(1970, 1, 1, 0, 0),
            datetime.datetime(1970, 1, 1, 12, 0),
            datetime.datetime(1970, 1, 2, 0, 0),
            datetime.datetime(1970, 1, 2, 12, 0),
        ]
        exp_smpl_space_secs_since_1970 = np.array([0.0, 43200.0, 86400.0, 129600.0])

        smpl_space, smpl_space_secs_since_1970 = Orbit.form_sample_space(
            start_time, end_time, prop_smpl_interval
        )

        self.assertCountEqual(exp_smpl_space, smpl_space)
        self.assertCountEqual(
            exp_smpl_space_secs_since_1970, smpl_space_secs_since_1970
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

        exp_idx_tle = np.array(
            [
                0,
                1,
                2,
                3,
                5,
            ]
        )  # These are the indices of the corresponding time stamps in TLE time vector
        exp_idx_sim = np.array(
            [
                0,
                4,
                6,
                8,
                9,
            ]
        )  # These are the indices of the corresponding time stamps in simulation vector

        idx_sim, idx_tle = Orbit.get_matching_indices(
            np.array(sim_time), np.array(tle_time)
        )

        self.assertCountEqual(exp_idx_tle, idx_tle)
        self.assertCountEqual(exp_idx_sim, idx_sim)

    def test_valid_simulate_orbit(self):
        # Read sample Sentinel-6 file
        ds = nc.Dataset(S6_ORBIT_PATH[0], mode="r")
        exp_time = ds.groups["data_01"].variables["time"][:]
        exp_lat = ds.groups["data_01"].variables["latitude"][:]
        exp_lon = ds.groups["data_01"].variables["longitude"][:]

        # Convert start-time and end-time of S6 track to datetime. Notice that altimetry satellites (in this case
        # Sentinel-6MF) do report time as seconds since 2000. This is not to be mistaken with OrbitX's reference time
        # which is 1970.
        S6_start_time = datetime.timedelta(seconds=exp_time[0]) + datetime.datetime(
            2000, 1, 1, 0, 0, 0
        )
        S6_end_time = datetime.timedelta(seconds=exp_time[-1]) + datetime.datetime(
            2000, 1, 1, 0, 0, 0
        )

        # Simulate S6 orbit at 1 Hz
        sat = "S6"
        propagation_sampling_interval = 1

        tle = TLEInfo()
        orbit = Orbit()
        orbit.start_time = S6_start_time
        orbit.end_time = S6_end_time

        tle_info = tle.get_tle(sat, S6_start_time, S6_end_time)
        time, lat, lon = orbit.simulate_orbit(*tle_info, propagation_sampling_interval)

        time_diff = [np.abs(time[i] - exp_time[i]) for i in range(len(lat))]
        # Calculate the Haversine distance between simulated and real orbit at 1 Hz sampling rate
        distance = [
            cal_dist_d2m(lat[i], lon[i], exp_lat[i], exp_lon[i])
            for i in range(len(lat))
        ]
        # Make sure that at all instances, the distance is less than 1 km (which is an acceptable deviation for S6)
        self.assertTrue((np.array(distance) < 1).all())

    #
    @mock.patch(
        "orbitx.orbit.absolutedate_to_datetime",
        return_value=datetime.datetime(1970, 1, 1),
    )
    @mock.patch("orbitx.orbit.TopocentricFrame")
    @mock.patch("orbitx.orbit.GeodeticPoint")
    @mock.patch("orbitx.orbit.TLEPropagator.selectExtrapolator")
    @mock.patch("orbitx.orbit.TLE", return_value=([3]))
    @mock.patch("orbitx.orbit.FramesFactory.getEME2000")
    @mock.patch("orbitx.orbit.OneAxisEllipsoid")
    @mock.patch("orbitx.orbit.FramesFactory.getITRF")
    @mock.patch("orbitx.orbit.TimeScalesFactory.getUTC")
    @mock.patch("orbitx.orbit.PVCoordinatesProvider.cast_")
    @mock.patch("orbitx.orbit.CelestialBodyFactory.getSun")
    @mock.patch("orbitx.orbit.AbsoluteDate")
    def test_propagate_orbit(
        self,
        mock_AbsoluteDate,
        mock_CBF_getSun,
        mock_PVCP_cast_,
        mock_TSF_getUTC,
        mock_FF_getITRF,
        mock_OneAxisEllipsoid,
        mock_FF_getEME2000,
        mock_TLE,
        mock_TLEP_selectExtrapolator,
        mock_GeodeticPoint,
        mock_TopocentricFrame,
        mock_absolutedate_to_datetime,
    ):
        mock_AbsoluteDate_1 = mock.MagicMock(spec=AbsoluteDate)
        mock_AbsoluteDate_1.compareTo.side_effect = [-7, -6, -5, -4, -3, -2, -1, 0, 1]
        mock_AbsoluteDate_1.shiftedBy.return_value = mock_AbsoluteDate_1

        mock_AbsoluteDate_2 = mock.MagicMock(spec=AbsoluteDate)
        mock_AbsoluteDate_2.compareTo.side_effect = [-7, -6, -5, -4, -3, -2, -1, 0, 1]
        mock_AbsoluteDate_2.shiftedBy.return_value = mock_AbsoluteDate_2

        mock_AbsoluteDate.side_effect = [mock_AbsoluteDate_1, mock_AbsoluteDate_2]

        mock_OneAxisEllipsoid().transform().getLatitude.return_value = 0
        mock_OneAxisEllipsoid().transform().getLongitude.return_value = 0
        mock_OneAxisEllipsoid().transform().getAltitude.return_value = []

        mock_TopocentricFrame().getAzimuth.return_value = 0
        mock_TopocentricFrame().getElevation.return_value = 0

        orbit = Orbit()
        julian_date, pos_s0_lat, pos_s0_lon, pos_s0_alt, sel, saz = (
            orbit.propagate_orbit(
                "", "", datetime.datetime(1970, 1, 1), datetime.datetime(1970, 1, 2), 1
            )
        )
        self.assertCountEqual(
            julian_date, np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=float)
        )
        self.assertCountEqual(
            pos_s0_lat, np.array([0, 0, 0, 0, 0, 0, 0, 0], dtype=float)
        )
        self.assertCountEqual(
            pos_s0_lon, np.array([0, 0, 0, 0, 0, 0, 0, 0], dtype=float)
        )
        np.testing.assert_equal(
            pos_s0_alt,
            np.array(
                [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
                dtype=float,
            ),
        )
        self.assertCountEqual(sel, np.array([0, 0, 0, 0, 0, 0, 0, 0], dtype=float))
        self.assertCountEqual(saz, np.array([0, 0, 0, 0, 0, 0, 0, 0], dtype=float))

        mock_AbsoluteDate.assert_called()
        mock_CBF_getSun.assert_called()
        mock_PVCP_cast_.assert_called()
        mock_TSF_getUTC.assert_called()
        mock_FF_getITRF.assert_called()
        mock_OneAxisEllipsoid.assert_called()
        mock_FF_getEME2000.assert_called_with()
        mock_TLE.assert_called_with("", "")
        mock_TLEP_selectExtrapolator.assert_called_with([3])
        mock_GeodeticPoint.assert_called()
        mock_TopocentricFrame.assert_called()
        mock_absolutedate_to_datetime.assert_called()

        pass

    @mock.patch(
        "orbitx.orbit.Orbit.propagate_orbit",
        return_value=([12], [13], [14], [], [], []),
    )
    @mock.patch("orbitx.orbit.Orbit.get_matching_indices", return_value=([3], [0]))
    @mock.patch(
        "orbitx.orbit.Orbit.form_sample_space",
        return_value=(
            [
                datetime.datetime(1970, 1, 1, 0, 0, 0),
                datetime.datetime(1970, 1, 1, 0, 0, 2),
                datetime.datetime(1970, 1, 1, 0, 0, 4),
                datetime.datetime(1970, 1, 1, 0, 0, 6),
            ],
            [0.0, 2.0, 4.0, 6.0],
        ),
    )
    def test_simulate_orbit_1_tle_ref(self, mock_form_ss, mock_match_idx, mock_prop):
        orbit = Orbit()
        orbit.start_time = datetime.datetime(1970, 1, 1, 0, 0, 0)
        orbit.end_time = datetime.datetime(1970, 1, 1, 0, 0, 5)

        self.assertEqual(
            orbit.simulate_orbit(["12"], ["23"], [32], 2), ([12], [13], [14])
        )
        mock_form_ss.assert_called_with(
            datetime.datetime(1970, 1, 1, 0, 0, 0),
            datetime.datetime(1970, 1, 1, 0, 0, 5),
            2,
        )
        mock_match_idx.assert_called_with([0.0, 2.0, 4.0, 6.0], [32])
        mock_prop.assert_called_with(
            "12",
            "23",
            datetime.datetime(1970, 1, 1, 0, 0, 0),
            datetime.datetime(1970, 1, 1, 0, 0, 5),
            2,
        )

    @mock.patch(
        "orbitx.orbit.Orbit.propagate_orbit", return_value=([1], [1], [1], [], [], [])
    )
    @mock.patch(
        "orbitx.orbit.Orbit.get_matching_indices", return_value=([1, 2], [1, 2])
    )
    @mock.patch(
        "orbitx.orbit.Orbit.form_sample_space", return_value=([1, 2, 3, 5, 6], [])
    )
    def test_simulate_orbit_2_tle_ref(
        self, mock_form_smpl, mock_get_mtch_idx, mock_prop_orb
    ):
        orbit = Orbit()
        orbit.start_time = ""
        orbit.end_time = ""

        self.assertEqual(
            orbit.simulate_orbit(["1", "2"], ["2", "3"], [2], 1), ([1], [1], [1])
        )
        mock_form_smpl.assert_called_with("", "", 1)
        mock_form_smpl.assert_called_once()
        mock_get_mtch_idx.assert_called_with([], [2])
        mock_get_mtch_idx.assert_called_once()
        mock_prop_orb.assert_called_with("2", "3", 2, 2, 1)
        mock_prop_orb.assert_called_once()

    def test_interpolate_orbit(self):
        sat_sec_since = [0, 86400]
        sat_lat_sim = [0, 24]
        sat_lon_sim = [0, 24]
        interpolation_sampling_interval = 60 * 60  # interpolate to every one hour

        exp_time = np.arange(0, 86400 + 60 * 60, 3600)
        exp_lat = [i for i in range(0, 25)]
        exp_lon = [i for i in range(0, 25)]

        orbit = Orbit()
        orbit.start_time = datetime.datetime(1970, 1, 1)
        orbit.end_time = datetime.datetime(1970, 1, 2)

        lat, lon, time = orbit.interpolate_orbit(
            np.array(sat_sec_since),
            np.array(sat_lat_sim),
            np.array(sat_lon_sim),
            interpolation_sampling_interval,
        )

        self.assertTrue((exp_lat == lat).all())
        self.assertTrue((exp_lon == lon).all())
        self.assertTrue((exp_time == time).all())

    @mock.patch("orbitx.orbit.Orbit.interpolate_orbit", return_value=([2], ["B"], []))
    @mock.patch("orbitx.orbit.Orbit.simulate_orbit", return_value=([2], ["b"], []))
    @mock.patch("orbitx.tle.TLEInfo.get_tle", return_value=([1], [], [""]))
    def test_run(self, mock_get_tle, mock_sim_orb, mock_interp_orb):
        orbit = Orbit()
        self.assertEqual(
            orbit.run([""], 1, 2, [3], [4]),
            {"": {"lat": [2], "lon": ["B"], "time": []}},
        )
        mock_get_tle.assert_called_with("", 1, 2)
        mock_get_tle.assert_called_once()
        mock_sim_orb.assert_called_with([1], [], [""], [3])
        mock_sim_orb.assert_called_once()
        mock_interp_orb.assert_called_with([2], ["b"], [], [4])
        mock_interp_orb.assert_called_once()


if __name__ == "__main__":
    unittest.main()
