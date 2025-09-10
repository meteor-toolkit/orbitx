"""orbitx.tests.test_orbit - tests for orbitx.orbit"""

import numpy as np
import unittest
import unittest.mock as mock
import datetime
from orbitx.tle import TLEInfo
from orbitx.orbit import Orbit
from orbitx.utils._date_utils import sec_since_to_datetime64
from orbitx.utils._orbit.propagate_orbit import AbsoluteDate
from orbitx.utils._orbit.propagate_orbit import propagate_orbit
from orbitx.utils._orbit.interpolate_orbit import interpolate_orbit
from orbitx.utils._orbit.form_sample_space import form_sample_space
from orbitx.utils._orbit.get_matching_indices import get_matching_indices
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


class TestORBIT(unittest.TestCase):
    def test_form_sample_space(self):
        # Start at 1st of Jan. 1970, and sample every 12 hours until 2nd of Jan. 1970, one o'clock am.
        start_date = np.datetime64("1970-01-01T00:00:00")
        end_date = np.datetime64("1970-01-02T01:00:00")
        prop_smpl_interval = 12 * 60 * 60

        # We are expecting 4 samples:
        exp_smpl_space = [
            np.datetime64("1970-01-01T00:00:00"),
            np.datetime64("1970-01-01T12:00:00"),
            np.datetime64("1970-01-02T00:00:00"),
            np.datetime64("1970-01-02T12:00:00")
        ]
        exp_smpl_space_secs_since_1970 = np.array([0.0, 43200.0, 86400.0, 129600.0])

        smpl_space, smpl_space_secs_since_1970 = form_sample_space(
            start_date, end_date, prop_smpl_interval
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

        idx_sim, idx_tle = get_matching_indices(
            np.array(sim_time), np.array(tle_time)
        )

        self.assertCountEqual(exp_idx_tle, idx_tle)
        self.assertCountEqual(exp_idx_sim, idx_sim)

    def test_valid_simulate_orbit(self):
        # Read sample Sentinel-6 file
        ds = nc.Dataset(S6_ORBIT_PATH[0], mode="r")
        exp_time = ds.groups["data_01"].variables["time"][:]
        exp_date = [
            sec_since_to_datetime64(
                exp_sec_since,
                reference_date=np.datetime64("2000-01-01T00:00:00")
            ) for exp_sec_since in exp_time
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
        propagation_sampling_interval = np.array(1, dtype = "timedelta64[s]")

        tle = TLEInfo()

        tle_line_1, tle_line_2, tle_time_s1970 = tle.get_tle(sat, S6_start_date, S6_end_date, reference_date=np.datetime64("2000-01-01T00:00:00"))

        time, date, lat, lon = simulate_orbit(
            start_date=S6_start_date,
            end_date=S6_end_date,
            line1=tle_line_1,
            line2=tle_line_2,
            seconds_since_tle=tle_time_s1970,
            propagation_sampling_interval=propagation_sampling_interval,
            reference_date=np.datetime64("2000-01-01T00:00:00"))
        self.assertCountEqual(time, exp_time)
        self.assertCountEqual(date, exp_date)
        # Calculate the Haversine distance between simulated and real orbit at 1 Hz sampling rate
        distance = [
            cal_dist_d2m(lat[i], lon[i], exp_lat[i], exp_lon[i])
            for i in range(len(lat))
        ]
        print(np.min(distance), np.max(distance))
        # Make sure that at all instances, the distance is less than 1 km (which is an acceptable deviation for S6)
        self.assertTrue((np.array(distance) < 1).all())

    
    @mock.patch(
        "orbitx.utils._orbit.propagate_orbit.datetime_to_datetime64",
        return_value=np.datetime64("1970-01-01T00:00:00"),
    )
    @mock.patch(
        "orbitx.utils._orbit.propagate_orbit.absolutedate_to_datetime",
        return_value=datetime.datetime(1970, 1, 1, 0, 0, 0),
    )
    @mock.patch("orbitx.utils._orbit.propagate_orbit.TopocentricFrame")
    @mock.patch("orbitx.utils._orbit.propagate_orbit.GeodeticPoint")
    @mock.patch("orbitx.utils._orbit.propagate_orbit.TLEPropagator.selectExtrapolator")
    @mock.patch("orbitx.utils._orbit.propagate_orbit.TLE", return_value=([3]))
    @mock.patch("orbitx.utils._orbit.propagate_orbit.FramesFactory.getEME2000")
    @mock.patch("orbitx.utils._orbit.propagate_orbit.OneAxisEllipsoid")
    @mock.patch("orbitx.utils._orbit.propagate_orbit.FramesFactory.getITRF")
    # @mock.patch("orbitx.utils._orbit.propagate_orbit.TimeScalesFactory.getUTC")
    @mock.patch("orbitx.utils._orbit.propagate_orbit.PVCoordinatesProvider.cast_")
    @mock.patch("orbitx.utils._orbit.propagate_orbit.CelestialBodyFactory.getSun")
    # @mock.patch("orbitx.utils._orbit.propagate_orbit.AbsoluteDate")
    def test_propagate_orbit(
        self,
        # mock_AbsoluteDate,
        mock_CBF_getSun,
        mock_PVCP_cast_,
        # mock_TSF_getUTC,
        mock_FF_getITRF,
        mock_OneAxisEllipsoid,
        mock_FF_getEME2000,
        mock_TLE,
        mock_TLEP_selectExtrapolator,
        mock_GeodeticPoint,
        mock_TopocentricFrame,
        mock_absolutedate_to_datetime,
        mock_datetime_to_datetime64
    ):
        # mock_AbsoluteDate_1 = mock.MagicMock(spec=AbsoluteDate)
        # mock_AbsoluteDate_1.compareTo.side_effect = [-7, -6, -5, -4, -3, -2, -1, 0, 1]
        # mock_AbsoluteDate_1.shiftedBy.return_value = mock_AbsoluteDate_1

        # mock_AbsoluteDate_2 = mock.MagicMock(spec=AbsoluteDate)
        # mock_AbsoluteDate_2.compareTo.side_effect = [-7, -6, -5, -4, -3, -2, -1, 0, 1]
        # mock_AbsoluteDate_2.shiftedBy.return_value = mock_AbsoluteDate_2

        # mock_AbsoluteDate.side_effect = [mock_AbsoluteDate_1, mock_AbsoluteDate_2]

        mock_OneAxisEllipsoid().transform().getLatitude.return_value = 0
        mock_OneAxisEllipsoid().transform().getLongitude.return_value = 0
        mock_OneAxisEllipsoid().transform().getAltitude.return_value = []

        mock_TopocentricFrame().getAzimuth.return_value = 0
        mock_TopocentricFrame().getElevation.return_value = 0

        julian_date, _, pos_s0_lat, pos_s0_lon, pos_s0_alt, sel, saz = (
            propagate_orbit(
                tle_line1 = "",
                tle_line2 = "",
                start_date = np.datetime64("1970-01-01T00:00:00"),
                end_date = np.datetime64("1970-01-02T00:00:00"),
                propagation_sampling_interval = np.array(1, dtype = "timedelta64[s]")
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
        mock_datetime_to_datetime64.assert_called()

        pass

    @mock.patch(
        "orbitx.utils._orbit.simulate_orbit.propagate_orbit",
        return_value=([12], [13], [14], [15], [], [], []),
    )
    @mock.patch("orbitx.utils._orbit.simulate_orbit.get_matching_indices", return_value=([7], [0]))
    @mock.patch(
        "orbitx.utils._orbit.simulate_orbit.form_sample_space", return_value=([], [9]))
    def test_simulate_orbit_1_tle_ref(self, mock_form_ss, mock_match_idx, mock_prop):
        start_date = np.datetime64("1970-01-01T00:00:00")
        end_date = np.datetime64("1970-01-01T00:00:05")

        self.assertEqual(
            simulate_orbit(
                start_date=start_date,
                end_date=end_date,
                line1=["12"],
                line2=["23"],
                seconds_since_tle=[32],
                propagation_sampling_interval=np.array(2, dtype = "timedelta64[s]"),
                reference_date=np.datetime64("1970-01-01T00:00:00")), ([12], [13], [14], [15])
        )
        mock_form_ss.assert_called_with(
            np.datetime64("1970-01-01T00:00:00"),
            np.datetime64("1970-01-01T00:00:05"),
            np.array(2, dtype = "timedelta64[s]"),
            np.datetime64("1970-01-01T00:00:00")
        )
        mock_match_idx.assert_called_with([9], [32])
        mock_prop.assert_called_with(
            "12",
            "23",
            np.datetime64("1970-01-01T00:00:00"),
            np.datetime64("1970-01-01T00:00:05"),
            np.array(2, dtype = "timedelta64[s]"),
            np.datetime64("1970-01-01T00:00:00")
        )

    @mock.patch(
        "orbitx.utils._orbit.simulate_orbit.propagate_orbit", return_value=([12], [13], [14], [15], [], [], [])
    )
    @mock.patch(
        "orbitx.utils._orbit.simulate_orbit.get_matching_indices", return_value=([7], [0])
    )
    @mock.patch(
        "orbitx.utils._orbit.simulate_orbit.form_sample_space", return_value=([], [9])
    )
    def test_simulate_orbit_2_tle_ref(
        self, mock_form_smpl, mock_get_mtch_idx, mock_prop_orb
    ):
        start_date = np.datetime64("1970-01-01T00:00:00")
        end_date = np.datetime64("1970-01-01T00:00:05")

        self.assertEqual(
            simulate_orbit(
                start_date=start_date,
                end_date=end_date,
                line1=["1", "2"],
                line2=["3", "4"],
                seconds_since_tle=[2],
                propagation_sampling_interval=np.array(1, dtype = "timedelta64[s]"),
                reference_date=np.datetime64("1970-01-01T00:00:00")),
                ([12], [13], [14], [15])
        )
        mock_form_smpl.assert_called_with(
            np.datetime64("1970-01-01T00:00:00"),
            np.datetime64("1970-01-01T00:00:05"),
            np.array(1, dtype = "timedelta64[s]"),
            np.datetime64("1970-01-01T00:00:00"))
        mock_form_smpl.assert_called_once()
        mock_get_mtch_idx.assert_called_with([9], [2])
        mock_get_mtch_idx.assert_called_once()
        mock_prop_orb.assert_called_with(
            "1",
            "3",
            np.datetime64("1970-01-01T00:00:00"),
            np.datetime64("1970-01-01T00:00:05"),
            np.array(1, dtype = "timedelta64[s]"),
            np.datetime64("1970-01-01T00:00:00"))
        mock_prop_orb.assert_called_once()

    def test_interpolate_orbit(self):
        sat_sec_since = np.linspace(0, 86400, 33)
        sat_date =np.linspace(0, 86400, 33, dtype = "datetime64[s]")
        sat_lat_sim = np.concatenate((np.linspace(-70, 70, 17, dtype=float), np.linspace(70, -70, 17, dtype=float)[1:]))
        sat_lon_sim = np.concatenate((np.linspace(-180, 180, 17, dtype=float)[:-1], np.linspace(-180, 180, 17, dtype=float)[:-1], [-180]))
        interpolation_sampling_interval = np.array(675, dtype = "timedelta64[s]")

        exp_time = np.linspace(0, 86400, 129)
        exp_date = np.linspace(0, 86400, 129, dtype = "datetime64[s]")
        exp_lat = np.concatenate((np.linspace(-70, 70, 65, dtype=float), np.linspace(70, -70, 65, dtype=float)[1:]))
        exp_lon = np.concatenate((np.linspace(-180, 180, 65, dtype=float)[:-1], np.linspace(-180, 180, 65, dtype=float)[:-1], [-180]))

        start_date = np.datetime64("1970-01-01T00:00:00")
        end_date = np.datetime64("1970-01-02T00:00:00")

        time, date, lat, lon = interpolate_orbit(
            start_date,
            end_date,
            sat_sec_since,
            sat_lat_sim,
            sat_lon_sim,
            interpolation_sampling_interval
        )
        
        self.assertCountEqual(exp_lat, lat)
        self.assertCountEqual(exp_lon, lon)
        self.assertTrue((exp_time == time).all())
        self.assertTrue((exp_date == date).all())

    @mock.patch(
        "orbitx.orbit.interpolate_orbit",
        return_value=(
            np.linspace(0, 86400, 129),
            np.linspace(0, 86400, 129, dtype = "datetime64[s]"),
            np.concatenate((np.linspace(-70, 70, 65, dtype=float), np.linspace(70, -70, 65, dtype=float)[1:])),
            np.concatenate((np.linspace(-180, 180, 65, dtype=float)[:-1], np.linspace(-180, 180, 65, dtype=float)[:-1], [-180]))
        )
    )
    @mock.patch(
        "orbitx.orbit.simulate_orbit",
        return_value=(
            "simulate return time",
            "simulate return date",
            "simulate return lat",
            "simulate return lon"
        )
    )
    @mock.patch("orbitx.tle.TLEInfo.get_tle", return_value=([1], [], [""]))
    def test_simulate(
        self,
        mock_get_tle,
        mock_sim_orb,
        mock_interp_orb
    ):
        dummy_orbit = Orbit(
            satellites=[""],
            start_date=np.datetime64("1970-01-01T00:00:00"),
            end_date=np.datetime64("1970-01-02T00:00:00"),
            propagation_sampling_interval=np.array(2700, dtype = "timedelta64[s]"),
            interpolation_sampling_interval=np.array(675, dtype = "timedelta64[s]"),
            reference_date=np.datetime64("1970-01-01T00:00:00"),
            orbit=xr.Dataset(
                data_vars = {
                    "reference_date": (np.datetime64("1970-01-01T00:00:00")),
                    "time_datetime": ("time", np.linspace(0, 86400, 129, dtype = "datetime64[s]")),
                    "lat1": ("time", np.concatenate((np.linspace(-70, 70, 65, dtype=float), np.linspace(70, -70, 65, dtype=float)[1:]))),
                    "lon1": ("time", np.concatenate((np.linspace(-180, 180, 65, dtype=float)[:-1], np.linspace(-180, 180, 65, dtype=float)[:-1], [-180]))),
                },
                coords = {"time": np.linspace(0, 86400, 129)},
                attrs={
                    "satellites": [""],
                    "start_date": 0.,
                    "end_date": 86400.,
                    "propagation_sampling_interval": 2700.,
                    "interpolation_sampling_interval": 675.
                }
            )
        )
        simulated_orbit = Orbit.simulate(
            satellites = [""],
            start_date = np.datetime64("1970-01-01T00:00:00"),
            end_date = np.datetime64("1970-01-02T00:00:00"),
            propagation_sampling_interval = np.array(2700, dtype = "timedelta64[s]"),
            interpolation_sampling_interval = np.array(675, dtype = "timedelta64[s]")
        )
        self.assertEqual(
            simulated_orbit,
            dummy_orbit
        )
        mock_get_tle.assert_called_with(
            "",
            np.datetime64("1970-01-01T00:00:00"),
            np.datetime64("1970-01-02T00:00:00"))
        mock_get_tle.assert_called_once()
        mock_sim_orb.assert_called_with(
            np.datetime64("1970-01-01T00:00:00"),
            np.datetime64("1970-01-02T00:00:00"),
            [1],
            [],
            [""],
            np.array(2700, dtype = "timedelta64[s]"),
            np.datetime64("1970-01-01T00:00:00")
        )
        mock_sim_orb.assert_called_once()
        mock_interp_orb.assert_called_with(
            np.datetime64("1970-01-01T00:00:00"),
            np.datetime64("1970-01-02T00:00:00"),
            "simulate return time",
            "simulate return lat",
            "simulate return lon",
            np.array(675, dtype = "timedelta64[s]"),
            np.datetime64("1970-01-01T00:00:00")
        )
        mock_interp_orb.assert_called_once()


if __name__ == "__main__":
    unittest.main()
