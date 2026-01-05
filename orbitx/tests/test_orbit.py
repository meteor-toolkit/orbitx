"""orbitx.tests.test_orbit - tests for orbitx.orbit"""

import numpy as np
import unittest
import unittest.mock as mock
from orbitx import Orbit, TLE
from orbitx import __version__
import xarray as xr

__author__ = "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>"


class TestOrbit(unittest.TestCase):
    @mock.patch(
        "orbitx.orbit.interpolate_orbit",
        return_value=(
            np.linspace(0, 86400, 129),
            np.linspace(0, 86400, 129, dtype="datetime64[s]"),
            np.concatenate(
                (
                    np.linspace(-70, 70, 65, dtype=float),
                    np.linspace(70, -70, 65, dtype=float)[1:],
                )
            ),
            np.concatenate(
                (
                    np.linspace(-180, 180, 65, dtype=float)[:-1],
                    np.linspace(-180, 180, 65, dtype=float)[:-1],
                    [-180],
                )
            ),
        ),
    )
    @mock.patch(
        "orbitx.orbit.simulate_orbit",
        return_value=(
            "simulate return time",
            "simulate return date",
            "simulate return lat",
            "simulate return lon",
        ),
    )
    @mock.patch(
        "orbitx.TLE.from_sat_shortname",
        return_value= TLE(
            xr.Dataset(
                data_vars={
                    "tle_date": ("tle_index", [1]),
                    "line_1": ("tle_index", ["line_1"]),
                    "line_2": ("tle_index", ["line_2"]),
                },
                coords={"tle_index": [0]},
                attrs = {
                    "satellite_shortname": "",
                    "satellite_name": "",
                    "catalog_number": "",
                    "classification": "",
                    "launch_number": "",
                    "launch_piece": "",
                    "launch_year": "",
                    "version": __version__,
                    "creation_date": str(np.datetime64("1980-01-01T00:00:00")),
                }
            )
        )
    )
    @mock.patch(
        'orbitx.utils._orbit.orbit_dict_to_xarray.datetime64',
        return_value = np.datetime64("1980-01-01T00:00:00")
    )
    def test_simulate(self, mock_datetime64, mock_TLE, mock_sim_orb, mock_interp_orb):
        expected_result = Orbit(
            xr.Dataset(
                data_vars={
                    "reference_date": (np.datetime64("1970-01-01T00:00:00")),
                    "time_datetime": (
                        ["time"],
                        np.linspace(0, 86400, 129, dtype="datetime64[s]"),
                    ),
                    "lat": (
                        ["time", "satellite"],
                        np.concatenate(
                            (
                                np.linspace(-70, 70, 65, dtype=float),
                                np.linspace(70, -70, 65, dtype=float)[1:],
                            )
                        )[:,np.newaxis],
                    ),
                    "lon": (
                        ["time", "satellite"],
                        np.concatenate(
                            (
                                np.linspace(-180, 180, 65, dtype=float)[:-1],
                                np.linspace(-180, 180, 65, dtype=float)[:-1],
                                [-180],
                            )
                        )[:,np.newaxis],
                    ),
                },
                coords={
                    "time": np.linspace(0, 86400, 129),
                    "satellite": [""],
                },
                attrs={
                    "satellite_shortname": [""],
                    "satellite_name": [""],
                    "start_date": 0,
                    "end_date": 86400,
                    "propagation_sampling_interval": 2700,
                    "interpolation_sampling_interval": 675,
                    "version": __version__,
                    "creation_date": np.datetime64("1980-01-01T00:00:00"),
                },
            )
        )
        simulated_orbit = Orbit.simulate(
            satellites=[""],
            start_date=np.datetime64("1970-01-01T00:00:00"),
            end_date=np.datetime64("1970-01-02T00:00:00"),
            propagation_sampling_interval=np.array(2700, dtype="timedelta64[s]"),
            interpolation_sampling_interval=np.array(675, dtype="timedelta64[s]"),
        )
        self.assertEqual(simulated_orbit, expected_result)
        mock_TLE.assert_called_with(
            "",
            np.datetime64("1970-01-01T00:00:00"),
            np.datetime64("1970-01-02T00:00:00"),
            np.datetime64("1970-01-01T00:00:00"),
        )
        mock_TLE.assert_called_once()
        mock_sim_orb.assert_called_once()
        mock_interp_orb.assert_called_with(
            np.datetime64("1970-01-01T00:00:00"),
            np.datetime64("1970-01-02T00:00:00"),
            "simulate return time",
            "simulate return lat",
            "simulate return lon",
            np.array(675, dtype="timedelta64[s]"),
            np.datetime64("1970-01-01T00:00:00"),
        )
        mock_interp_orb.assert_called_once()


if __name__ == "__main__":
    unittest.main()
