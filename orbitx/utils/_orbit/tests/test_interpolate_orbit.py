"""orbitx.tests.test_orbit - tests for orbitx.orbit"""

import numpy as np
import unittest
import unittest.mock as mock
from orbitx.utils._orbit.interpolate_orbit import interpolate_orbit

__author__ = "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>"


class TestInterpolateOrbit(unittest.TestCase):
    @mock.patch(
        "orbitx.utils._orbit.interp_circ.interp_circ_",
        return_value=np.concatenate(
            (
                np.linspace(-180, 180, 65, dtype=float)[:-1],
                np.linspace(-180, 180, 65, dtype=float)[:-1],
                [-180],
            )
        ),
    )
    def test_interpolate_orbit(self, mock_interp_circ):
        sat_sec_since = np.linspace(0, 86400, 33)
        _sat_date = np.linspace(0, 86400, 33, dtype="datetime64[s]")
        sat_lat_sim = np.concatenate(
            (
                np.linspace(-70, 70, 17, dtype=float),
                np.linspace(70, -70, 17, dtype=float)[1:],
            )
        )
        sat_lon_sim = np.concatenate(
            (
                np.linspace(-180, 180, 17, dtype=float)[:-1],
                np.linspace(-180, 180, 17, dtype=float)[:-1],
                [-180],
            )
        )
        interpolation_sampling_interval = np.array(675, dtype="timedelta64[s]")

        exp_time = np.linspace(0, 86400, 129)
        exp_date = np.linspace(0, 86400, 129, dtype="datetime64[s]")
        exp_lat = np.concatenate(
            (
                np.linspace(-70, 70, 65, dtype=float),
                np.linspace(70, -70, 65, dtype=float)[1:],
            )
        )
        exp_lon = np.concatenate(
            (
                np.linspace(-180, 180, 65, dtype=float)[:-1],
                np.linspace(-180, 180, 65, dtype=float)[:-1],
                [-180],
            )
        )

        start_date = np.datetime64("1970-01-01T00:00:00")
        end_date = np.datetime64("1970-01-02T00:00:00")

        time, date, lat, lon = interpolate_orbit(
            start_date,
            end_date,
            sat_sec_since,
            sat_lat_sim,
            sat_lon_sim,
            interpolation_sampling_interval,
        )

        self.assertCountEqual(exp_lat, lat)
        self.assertCountEqual(exp_lon, lon)
        self.assertTrue((exp_time == time).all())
        self.assertTrue((exp_date == date).all())


if __name__ == "__main__":
    unittest.main()
