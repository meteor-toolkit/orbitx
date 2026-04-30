"""orbitx.tests.test_tle - tests for orbitx.tle"""

import unittest
import unittest.mock as mock
import numpy as np
import xarray as xr

from orbitx.utils._tle import create_xarray
from orbitx import __version__

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


example_0_tle_line_1 = [
    "1 33105U 08032A   10001.56483652 -.00000061  00000+0  00000+0 0  5178",
    "1 33105U 08032A   10001.95521637 -.00000061  00000+0  00000+0 0  5188",
    "1 33105U 08032A   10002.65790032 -.00000061  00000+0  00000+0 0  5183",
    "1 33105U 08032A   10003.82903964 -.00000061  00000+0  00000+0 0  5194",
    "1 33105U 08032A   10003.82903964 -.00000061  00000+0  00000+0 0  5228",
]
example_0_tle_line_2 = [
    "2 33105  66.0427  18.8487 0007802 268.8400  91.1724 12.80929371 71756",
    "2 33105  66.0427  18.0378 0007814 269.0188  90.9934 12.80929408 71803",
    "2 33105  66.0421  16.5778 0007820 268.8949  91.1182 12.80929406 71898",
    "2 33105  66.0422  14.1456 0007843 269.0908  90.9208 12.80929448 72049",
    "2 33105  66.0422  14.1456 0007843 269.0908  90.9208 12.80929448 72049",
]
example_0_reference_date = np.datetime64("1970-01-01T00:00:00")
example_0_start_date = np.datetime64("2010-01-02T00:00:00")
example_0_end_date = np.datetime64("2010-01-03T00:00:00")
example_0_satellite_shortname = "S2A"
example_0_satellite_name = "Sentinel-2A"
num_tle = len(example_0_tle_line_1)
result_0 = xr.Dataset(
    data_vars={
        "reference_date": (example_0_reference_date),
        "start_date": (example_0_start_date),
        "end_date": (example_0_end_date),
        "tle_date": (
            "tle_index",
            np.full((num_tle,), np.datetime64("2010-01-02T00:00:00")),
        ),
        "line_1": ("tle_index", example_0_tle_line_1),
        "line_2": ("tle_index", example_0_tle_line_2),
        "reference_date_seconds_since1970": (104),
        "start_date_seconds_since": (104),
        "end_date_seconds_since": (104),
        "tle_date_seconds_since": ("tle_index", np.full((num_tle,), 104)),
        "argument_perigee": ("tle_index", np.full((num_tle,), 0.1)),
        "balistic_coefficient": ("tle_index", np.full((num_tle,), 0.2)),
        "drag_term": ("tle_index", np.full((num_tle,), 0.3)),
        "eccentricity": ("tle_index", np.full((num_tle,), 0.4)),
        "element_set_number": ("tle_index", np.full((num_tle,), 100)),
        "inclination": ("tle_index", np.full((num_tle,), 0.5)),
        "mean_anomaly": ("tle_index", np.full((num_tle,), 0.6)),
        "mean_motion": ("tle_index", np.full((num_tle,), 0.7)),
        "revolution_number": ("tle_index", np.full((num_tle,), 103)),
        "right_ascension": ("tle_index", np.full((num_tle,), 0.8)),
        "second_derivative": ("tle_index", np.full((num_tle,), 0.9)),
    },
    coords={"tle_index": np.arange(num_tle)},
    attrs={
        "satellite_shortname": example_0_satellite_shortname,
        "satellite_name": example_0_satellite_name,
        "catalog_number": "1",
        "classification": "2",
        "launch_number": 101,
        "launch_piece": "3",
        "launch_year": 102,
        "version": __version__,
        "creation_date": "1980-01-01T00:00:00",
    },
)


class TestCreateXarray(unittest.TestCase):
    @mock.patch(
        "orbitx.utils._tle.create_xarray.get_argument_perigee", return_value=0.1
    )
    @mock.patch(
        "orbitx.utils._tle.create_xarray.get_ballistic_coefficient", return_value=0.2
    )
    @mock.patch("orbitx.utils._tle.create_xarray.get_catalog_number", return_value="1")
    @mock.patch("orbitx.utils._tle.create_xarray.get_classification", return_value="2")
    @mock.patch("orbitx.utils._tle.create_xarray.get_drag_term", return_value=0.3)
    @mock.patch("orbitx.utils._tle.create_xarray.get_eccentricity", return_value=0.4)
    @mock.patch(
        "orbitx.utils._tle.create_xarray.get_element_set_number", return_value=100
    )
    @mock.patch("orbitx.utils._tle.create_xarray.get_inclination", return_value=0.5)
    @mock.patch("orbitx.utils._tle.create_xarray.get_launch_number", return_value=101)
    @mock.patch("orbitx.utils._tle.create_xarray.get_launch_piece", return_value="3")
    @mock.patch("orbitx.utils._tle.create_xarray.get_launch_year", return_value=102)
    @mock.patch("orbitx.utils._tle.create_xarray.get_mean_anomaly", return_value=0.6)
    @mock.patch("orbitx.utils._tle.create_xarray.get_mean_motion", return_value=0.7)
    @mock.patch(
        "orbitx.utils._tle.create_xarray.get_revolution_number", return_value=103
    )
    @mock.patch("orbitx.utils._tle.create_xarray.get_right_ascension", return_value=0.8)
    @mock.patch(
        "orbitx.utils._tle.create_xarray.get_second_derivative", return_value=0.9
    )
    @mock.patch(
        "orbitx.utils._tle.create_xarray.get_tle_date",
        return_value=np.datetime64("1970-01-01T00:00:00"),
    )
    @mock.patch(
        "orbitx.utils._tle.create_xarray.datetime64_to_sec_since", return_value=104
    )
    @mock.patch(
        "orbitx.utils._tle.create_xarray.datetime64",
        return_value=np.datetime64("1980-01-01T00:00:00"),
    )
    def test_example_0(
        self,
        mock_get_argument_perigee,
        mock_get_ballistic_coefficient,
        mock_get_catalog_number,
        mock_get_classification,
        mock_get_drag_term,
        mock_get_eccentricity,
        mock_get_element_set_number,
        mock_get_inclination,
        mock_get_launch_number,
        mock_get_launch_piece,
        mock_get_launch_year,
        mock_get_mean_anomaly,
        mock_get_mean_motion,
        mock_get_revolution_number,
        mock_get_right_ascension,
        mock_get_second_derivative,
        mock_get_tle_date,
        mock_datetime64_to_sec_since,
        mock_datetime64,
    ):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(
            result_0,
            create_xarray(
                example_0_tle_line_1,
                example_0_tle_line_2,
                example_0_reference_date,
                example_0_start_date,
                example_0_end_date,
                example_0_satellite_shortname,
                example_0_satellite_name,
            ),
        )


if __name__ == "__main__":
    unittest.main()
