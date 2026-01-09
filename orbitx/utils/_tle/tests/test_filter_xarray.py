"""orbitx.tests.test_tle - tests for orbitx.tle"""

import unittest
import xarray as xr
import numpy as np
import numpy.typing as npt

from orbitx.utils._tle import filter_xarray
from orbitx import __version__

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


example_reference_date: np.datetime64 = np.datetime64("1970-01-01T00:00:00")
example_satellite_shortname = "S2A"
example_satellite_name = "Sentinel-2A"
time_delta: np.timedelta64 = (
    np.datetime64("2010-01-03T00:00:00") - np.datetime64("2010-01-01T00:00:00")
) / 10
example_tle_date: npt.NDArray[np.datetime64] = np.arange(
    np.datetime64("2010-01-01T00:00:00"),
    np.datetime64("2010-01-03T00:00:00") + time_delta,
    time_delta,
)
example_num_tle = example_tle_date.shape[0]
example_line_1 = ["" for _ in range(example_num_tle)]
example_line_2 = ["" for _ in range(example_num_tle)]


# array(['2010-01-01T00:00:00', '2010-01-01T04:48:00',
#        '2010-01-01T09:36:00', '2010-01-01T14:24:00',
#        '2010-01-01T19:12:00', '2010-01-02T00:00:00',
#        '2010-01-02T04:48:00', '2010-01-02T09:36:00',
#        '2010-01-02T14:24:00', '2010-01-02T19:12:00',
#        '2010-01-03T00:00:00'], dtype='datetime64[s]')


example_0_start_date = np.datetime64("2010-01-01T01:00:00")
example_0_end_date = np.datetime64("2010-01-02T23:00:00")

example_0 = xr.Dataset(
    data_vars={
        "reference_date": (example_reference_date),
        "start_date": (example_0_start_date),
        "end_date": (example_0_end_date),
        "tle_date": ("tle_index", example_tle_date),
        "line_1": ("tle_index", example_line_1),
        "line_2": ("tle_index", example_line_2),
        "reference_date_seconds_since1970": (104),
        "start_date_seconds_since": (104),
        "end_date_seconds_since": (104),
        "tle_date_seconds_since": ("tle_index", np.full((example_num_tle,), 104)),
        "argument_perigee": ("tle_index", np.full((example_num_tle,), 0.1)),
        "balistic_coefficient": ("tle_index", np.full((example_num_tle,), 0.2)),
        "drag_term": ("tle_index", np.full((example_num_tle,), 0.3)),
        "eccentricity": ("tle_index", np.full((example_num_tle,), 0.4)),
        "element_set_number": ("tle_index", np.full((example_num_tle,), 100)),
        "inclination": ("tle_index", np.full((example_num_tle,), 0.5)),
        "mean_anomaly": ("tle_index", np.full((example_num_tle,), 0.6)),
        "mean_motion": ("tle_index", np.full((example_num_tle,), 0.7)),
        "revolution_number": ("tle_index", np.full((example_num_tle,), 103)),
        "right_ascension": ("tle_index", np.full((example_num_tle,), 0.8)),
        "second_derivative": ("tle_index", np.full((example_num_tle,), 0.9)),
    },
    coords={"tle_index": np.arange(example_num_tle)},
    attrs={
        "satellite_shortname": example_satellite_shortname,
        "satellite_name": example_satellite_name,
        "catalog_number": "1",
        "classification": "2",
        "launch_number": 101,
        "launch_piece": "3",
        "launch_year": 102,
        "version": __version__,
        "creation_date": "1980-01-01T00:00:00",
    },
)

result_0 = xr.Dataset(
    data_vars={
        "reference_date": (example_reference_date),
        "start_date": (example_0_start_date),
        "end_date": (example_0_end_date),
        "tle_date": ("tle_index", example_tle_date[:-1]),
        "line_1": ("tle_index", example_line_1[:-1]),
        "line_2": ("tle_index", example_line_2[:-1]),
        "reference_date_seconds_since1970": (104),
        "start_date_seconds_since": (104),
        "end_date_seconds_since": (104),
        "tle_date_seconds_since": ("tle_index", np.full((example_num_tle - 1,), 104)),
        "argument_perigee": ("tle_index", np.full((example_num_tle - 1,), 0.1)),
        "balistic_coefficient": ("tle_index", np.full((example_num_tle - 1,), 0.2)),
        "drag_term": ("tle_index", np.full((example_num_tle - 1,), 0.3)),
        "eccentricity": ("tle_index", np.full((example_num_tle - 1,), 0.4)),
        "element_set_number": ("tle_index", np.full((example_num_tle - 1,), 100)),
        "inclination": ("tle_index", np.full((example_num_tle - 1,), 0.5)),
        "mean_anomaly": ("tle_index", np.full((example_num_tle - 1,), 0.6)),
        "mean_motion": ("tle_index", np.full((example_num_tle - 1,), 0.7)),
        "revolution_number": ("tle_index", np.full((example_num_tle - 1,), 103)),
        "right_ascension": ("tle_index", np.full((example_num_tle - 1,), 0.8)),
        "second_derivative": ("tle_index", np.full((example_num_tle - 1,), 0.9)),
    },
    coords={"tle_index": np.arange(example_num_tle - 1)},
    attrs={
        "satellite_shortname": example_satellite_shortname,
        "satellite_name": example_satellite_name,
        "catalog_number": "1",
        "classification": "2",
        "launch_number": 101,
        "launch_piece": "3",
        "launch_year": 102,
        "version": __version__,
        "creation_date": "1980-01-01T00:00:00",
    },
)

example_1_start_date = np.datetime64("2009-12-31T23:00:00")
example_1_end_date = np.datetime64("2010-01-02T23:00:00")
example_1 = xr.Dataset(
    data_vars={
        "reference_date": (example_reference_date),
        "start_date": (example_1_start_date),
        "end_date": (example_1_end_date),
        "tle_date": ("tle_index", example_tle_date),
        "line_1": ("tle_index", example_line_1),
        "line_2": ("tle_index", example_line_2),
        "reference_date_seconds_since1970": (104),
        "start_date_seconds_since": (104),
        "end_date_seconds_since": (104),
        "tle_date_seconds_since": ("tle_index", np.full((example_num_tle,), 104)),
        "argument_perigee": ("tle_index", np.full((example_num_tle,), 0.1)),
        "balistic_coefficient": ("tle_index", np.full((example_num_tle,), 0.2)),
        "drag_term": ("tle_index", np.full((example_num_tle,), 0.3)),
        "eccentricity": ("tle_index", np.full((example_num_tle,), 0.4)),
        "element_set_number": ("tle_index", np.full((example_num_tle,), 100)),
        "inclination": ("tle_index", np.full((example_num_tle,), 0.5)),
        "mean_anomaly": ("tle_index", np.full((example_num_tle,), 0.6)),
        "mean_motion": ("tle_index", np.full((example_num_tle,), 0.7)),
        "revolution_number": ("tle_index", np.full((example_num_tle,), 103)),
        "right_ascension": ("tle_index", np.full((example_num_tle,), 0.8)),
        "second_derivative": ("tle_index", np.full((example_num_tle,), 0.9)),
    },
    coords={"tle_index": np.arange(example_num_tle)},
    attrs={
        "satellite_shortname": example_satellite_shortname,
        "satellite_name": example_satellite_name,
        "catalog_number": "1",
        "classification": "2",
        "launch_number": 101,
        "launch_piece": "3",
        "launch_year": 102,
        "version": __version__,
        "creation_date": "1980-01-01T00:00:00",
    },
)
result_1 = xr.Dataset(
    data_vars={
        "reference_date": (example_reference_date),
        "start_date": (example_1_start_date),
        "end_date": (example_1_end_date),
        "tle_date": ("tle_index", example_tle_date),
        "line_1": ("tle_index", example_line_1),
        "line_2": ("tle_index", example_line_2),
        "reference_date_seconds_since1970": (104),
        "start_date_seconds_since": (104),
        "end_date_seconds_since": (104),
        "tle_date_seconds_since": ("tle_index", np.full((example_num_tle,), 104)),
        "argument_perigee": ("tle_index", np.full((example_num_tle,), 0.1)),
        "balistic_coefficient": ("tle_index", np.full((example_num_tle,), 0.2)),
        "drag_term": ("tle_index", np.full((example_num_tle,), 0.3)),
        "eccentricity": ("tle_index", np.full((example_num_tle,), 0.4)),
        "element_set_number": ("tle_index", np.full((example_num_tle,), 100)),
        "inclination": ("tle_index", np.full((example_num_tle,), 0.5)),
        "mean_anomaly": ("tle_index", np.full((example_num_tle,), 0.6)),
        "mean_motion": ("tle_index", np.full((example_num_tle,), 0.7)),
        "revolution_number": ("tle_index", np.full((example_num_tle,), 103)),
        "right_ascension": ("tle_index", np.full((example_num_tle,), 0.8)),
        "second_derivative": ("tle_index", np.full((example_num_tle,), 0.9)),
    },
    coords={"tle_index": np.arange(example_num_tle)},
    attrs={
        "satellite_shortname": example_satellite_shortname,
        "satellite_name": example_satellite_name,
        "catalog_number": "1",
        "classification": "2",
        "launch_number": 101,
        "launch_piece": "3",
        "launch_year": 102,
        "version": __version__,
        "creation_date": "1980-01-01T00:00:00",
    },
)

example_2_start_date = np.datetime64("2009-12-01T00:00:00")
example_2_end_date = np.datetime64("2009-12-31T00:00:00")
example_2 = xr.Dataset(
    data_vars={
        "reference_date": (example_reference_date),
        "start_date": (example_2_start_date),
        "end_date": (example_2_end_date),
        "tle_date": ("tle_index", example_tle_date),
        "line_1": ("tle_index", example_line_1),
        "line_2": ("tle_index", example_line_2),
        "reference_date_seconds_since1970": (104),
        "start_date_seconds_since": (104),
        "end_date_seconds_since": (104),
        "tle_date_seconds_since": ("tle_index", np.full((example_num_tle,), 104)),
        "argument_perigee": ("tle_index", np.full((example_num_tle,), 0.1)),
        "balistic_coefficient": ("tle_index", np.full((example_num_tle,), 0.2)),
        "drag_term": ("tle_index", np.full((example_num_tle,), 0.3)),
        "eccentricity": ("tle_index", np.full((example_num_tle,), 0.4)),
        "element_set_number": ("tle_index", np.full((example_num_tle,), 100)),
        "inclination": ("tle_index", np.full((example_num_tle,), 0.5)),
        "mean_anomaly": ("tle_index", np.full((example_num_tle,), 0.6)),
        "mean_motion": ("tle_index", np.full((example_num_tle,), 0.7)),
        "revolution_number": ("tle_index", np.full((example_num_tle,), 103)),
        "right_ascension": ("tle_index", np.full((example_num_tle,), 0.8)),
        "second_derivative": ("tle_index", np.full((example_num_tle,), 0.9)),
    },
    coords={"tle_index": np.arange(example_num_tle)},
    attrs={
        "satellite_shortname": example_satellite_shortname,
        "satellite_name": example_satellite_name,
        "catalog_number": "1",
        "classification": "2",
        "launch_number": 101,
        "launch_piece": "3",
        "launch_year": 102,
        "version": __version__,
        "creation_date": "1980-01-01T00:00:00",
    },
)
result_2 = xr.Dataset(
    data_vars={
        "reference_date": (example_reference_date),
        "start_date": (example_2_start_date),
        "end_date": (example_2_end_date),
        "tle_date": ("tle_index", [example_tle_date[0]]),
        "line_1": ("tle_index", [example_line_1[0]]),
        "line_2": ("tle_index", [example_line_2[0]]),
        "reference_date_seconds_since1970": (104),
        "start_date_seconds_since": (104),
        "end_date_seconds_since": (104),
        "tle_date_seconds_since": ("tle_index", [104]),
        "argument_perigee": ("tle_index", [0.1]),
        "balistic_coefficient": ("tle_index", [0.2]),
        "drag_term": ("tle_index", [0.3]),
        "eccentricity": ("tle_index", [0.4]),
        "element_set_number": ("tle_index", [100]),
        "inclination": ("tle_index", [0.5]),
        "mean_anomaly": ("tle_index", [0.6]),
        "mean_motion": ("tle_index", [0.7]),
        "revolution_number": ("tle_index", [103]),
        "right_ascension": ("tle_index", [0.8]),
        "second_derivative": ("tle_index", [0.9]),
    },
    coords={"tle_index": [0]},
    attrs={
        "satellite_shortname": example_satellite_shortname,
        "satellite_name": example_satellite_name,
        "catalog_number": "1",
        "classification": "2",
        "launch_number": 101,
        "launch_piece": "3",
        "launch_year": 102,
        "version": __version__,
        "creation_date": "1980-01-01T00:00:00",
    },
)

example_3_start_date = np.datetime64("2010-01-01T01:00:00")
example_3_end_date = np.datetime64("2010-01-03T01:00:00")
example_3 = xr.Dataset(
    data_vars={
        "reference_date": (example_reference_date),
        "start_date": (example_3_start_date),
        "end_date": (example_3_end_date),
        "tle_date": ("tle_index", example_tle_date),
        "line_1": ("tle_index", example_line_1),
        "line_2": ("tle_index", example_line_2),
        "reference_date_seconds_since1970": (104),
        "start_date_seconds_since": (104),
        "end_date_seconds_since": (104),
        "tle_date_seconds_since": ("tle_index", np.full((example_num_tle,), 104)),
        "argument_perigee": ("tle_index", np.full((example_num_tle,), 0.1)),
        "balistic_coefficient": ("tle_index", np.full((example_num_tle,), 0.2)),
        "drag_term": ("tle_index", np.full((example_num_tle,), 0.3)),
        "eccentricity": ("tle_index", np.full((example_num_tle,), 0.4)),
        "element_set_number": ("tle_index", np.full((example_num_tle,), 100)),
        "inclination": ("tle_index", np.full((example_num_tle,), 0.5)),
        "mean_anomaly": ("tle_index", np.full((example_num_tle,), 0.6)),
        "mean_motion": ("tle_index", np.full((example_num_tle,), 0.7)),
        "revolution_number": ("tle_index", np.full((example_num_tle,), 103)),
        "right_ascension": ("tle_index", np.full((example_num_tle,), 0.8)),
        "second_derivative": ("tle_index", np.full((example_num_tle,), 0.9)),
    },
    coords={"tle_index": np.arange(example_num_tle)},
    attrs={
        "satellite_shortname": example_satellite_shortname,
        "satellite_name": example_satellite_name,
        "catalog_number": "1",
        "classification": "2",
        "launch_number": 101,
        "launch_piece": "3",
        "launch_year": 102,
        "version": __version__,
        "creation_date": "1980-01-01T00:00:00",
    },
)
result_3 = xr.Dataset(
    data_vars={
        "reference_date": (example_reference_date),
        "start_date": (example_3_start_date),
        "end_date": (example_3_end_date),
        "tle_date": ("tle_index", example_tle_date),
        "line_1": ("tle_index", example_line_1),
        "line_2": ("tle_index", example_line_2),
        "reference_date_seconds_since1970": (104),
        "start_date_seconds_since": (104),
        "end_date_seconds_since": (104),
        "tle_date_seconds_since": ("tle_index", np.full((example_num_tle,), 104)),
        "argument_perigee": ("tle_index", np.full((example_num_tle,), 0.1)),
        "balistic_coefficient": ("tle_index", np.full((example_num_tle,), 0.2)),
        "drag_term": ("tle_index", np.full((example_num_tle,), 0.3)),
        "eccentricity": ("tle_index", np.full((example_num_tle,), 0.4)),
        "element_set_number": ("tle_index", np.full((example_num_tle,), 100)),
        "inclination": ("tle_index", np.full((example_num_tle,), 0.5)),
        "mean_anomaly": ("tle_index", np.full((example_num_tle,), 0.6)),
        "mean_motion": ("tle_index", np.full((example_num_tle,), 0.7)),
        "revolution_number": ("tle_index", np.full((example_num_tle,), 103)),
        "right_ascension": ("tle_index", np.full((example_num_tle,), 0.8)),
        "second_derivative": ("tle_index", np.full((example_num_tle,), 0.9)),
    },
    coords={"tle_index": np.arange(example_num_tle)},
    attrs={
        "satellite_shortname": example_satellite_shortname,
        "satellite_name": example_satellite_name,
        "catalog_number": "1",
        "classification": "2",
        "launch_number": 101,
        "launch_piece": "3",
        "launch_year": 102,
        "version": __version__,
        "creation_date": "1980-01-01T00:00:00",
    },
)

example_4_start_date = np.datetime64("2010-01-03T01:00:00")
example_4_end_date = np.datetime64("2010-01-03T23:00:00")
example_4 = xr.Dataset(
    data_vars={
        "reference_date": (example_reference_date),
        "start_date": (example_4_start_date),
        "end_date": (example_4_end_date),
        "tle_date": ("tle_index", example_tle_date),
        "line_1": ("tle_index", example_line_1),
        "line_2": ("tle_index", example_line_2),
        "reference_date_seconds_since1970": (104),
        "start_date_seconds_since": (104),
        "end_date_seconds_since": (104),
        "tle_date_seconds_since": ("tle_index", np.full((example_num_tle,), 104)),
        "argument_perigee": ("tle_index", np.full((example_num_tle,), 0.1)),
        "balistic_coefficient": ("tle_index", np.full((example_num_tle,), 0.2)),
        "drag_term": ("tle_index", np.full((example_num_tle,), 0.3)),
        "eccentricity": ("tle_index", np.full((example_num_tle,), 0.4)),
        "element_set_number": ("tle_index", np.full((example_num_tle,), 100)),
        "inclination": ("tle_index", np.full((example_num_tle,), 0.5)),
        "mean_anomaly": ("tle_index", np.full((example_num_tle,), 0.6)),
        "mean_motion": ("tle_index", np.full((example_num_tle,), 0.7)),
        "revolution_number": ("tle_index", np.full((example_num_tle,), 103)),
        "right_ascension": ("tle_index", np.full((example_num_tle,), 0.8)),
        "second_derivative": ("tle_index", np.full((example_num_tle,), 0.9)),
    },
    coords={"tle_index": np.arange(example_num_tle)},
    attrs={
        "satellite_shortname": example_satellite_shortname,
        "satellite_name": example_satellite_name,
        "catalog_number": "1",
        "classification": "2",
        "launch_number": 101,
        "launch_piece": "3",
        "launch_year": 102,
        "version": __version__,
        "creation_date": "1980-01-01T00:00:00",
    },
)
result_4 = xr.Dataset(
    data_vars={
        "reference_date": (example_reference_date),
        "start_date": (example_4_start_date),
        "end_date": (example_4_end_date),
        "tle_date": ("tle_index", [example_tle_date[-1]]),
        "line_1": ("tle_index", [example_line_1[-1]]),
        "line_2": ("tle_index", [example_line_2[-1]]),
        "reference_date_seconds_since1970": (104),
        "start_date_seconds_since": (104),
        "end_date_seconds_since": (104),
        "tle_date_seconds_since": ("tle_index", [104]),
        "argument_perigee": ("tle_index", [0.1]),
        "balistic_coefficient": ("tle_index", [0.2]),
        "drag_term": ("tle_index", [0.3]),
        "eccentricity": ("tle_index", [0.4]),
        "element_set_number": ("tle_index", [100]),
        "inclination": ("tle_index", [0.5]),
        "mean_anomaly": ("tle_index", [0.6]),
        "mean_motion": ("tle_index", [0.7]),
        "revolution_number": ("tle_index", [103]),
        "right_ascension": ("tle_index", [0.8]),
        "second_derivative": ("tle_index", [0.9]),
    },
    coords={"tle_index": [0]},
    attrs={
        "satellite_shortname": example_satellite_shortname,
        "satellite_name": example_satellite_name,
        "catalog_number": "1",
        "classification": "2",
        "launch_number": 101,
        "launch_piece": "3",
        "launch_year": 102,
        "version": __version__,
        "creation_date": "1980-01-01T00:00:00",
    },
)

example_5_start_date = np.datetime64("2009-12-31T23:00:00")
example_5_end_date = np.datetime64("2010-01-03T01:00:00")
example_5 = xr.Dataset(
    data_vars={
        "reference_date": (example_reference_date),
        "start_date": (example_5_start_date),
        "end_date": (example_5_end_date),
        "tle_date": ("tle_index", example_tle_date),
        "line_1": ("tle_index", example_line_1),
        "line_2": ("tle_index", example_line_2),
        "reference_date_seconds_since1970": (104),
        "start_date_seconds_since": (104),
        "end_date_seconds_since": (104),
        "tle_date_seconds_since": ("tle_index", np.full((example_num_tle,), 104)),
        "argument_perigee": ("tle_index", np.full((example_num_tle,), 0.1)),
        "balistic_coefficient": ("tle_index", np.full((example_num_tle,), 0.2)),
        "drag_term": ("tle_index", np.full((example_num_tle,), 0.3)),
        "eccentricity": ("tle_index", np.full((example_num_tle,), 0.4)),
        "element_set_number": ("tle_index", np.full((example_num_tle,), 100)),
        "inclination": ("tle_index", np.full((example_num_tle,), 0.5)),
        "mean_anomaly": ("tle_index", np.full((example_num_tle,), 0.6)),
        "mean_motion": ("tle_index", np.full((example_num_tle,), 0.7)),
        "revolution_number": ("tle_index", np.full((example_num_tle,), 103)),
        "right_ascension": ("tle_index", np.full((example_num_tle,), 0.8)),
        "second_derivative": ("tle_index", np.full((example_num_tle,), 0.9)),
    },
    coords={"tle_index": np.arange(example_num_tle)},
    attrs={
        "satellite_shortname": example_satellite_shortname,
        "satellite_name": example_satellite_name,
        "catalog_number": "1",
        "classification": "2",
        "launch_number": 101,
        "launch_piece": "3",
        "launch_year": 102,
        "version": __version__,
        "creation_date": "1980-01-01T00:00:00",
    },
)
result_5 = xr.Dataset(
    data_vars={
        "reference_date": (example_reference_date),
        "start_date": (example_5_start_date),
        "end_date": (example_5_end_date),
        "tle_date": ("tle_index", example_tle_date),
        "line_1": ("tle_index", example_line_1),
        "line_2": ("tle_index", example_line_2),
        "reference_date_seconds_since1970": (104),
        "start_date_seconds_since": (104),
        "end_date_seconds_since": (104),
        "tle_date_seconds_since": ("tle_index", np.full((example_num_tle,), 104)),
        "argument_perigee": ("tle_index", np.full((example_num_tle,), 0.1)),
        "balistic_coefficient": ("tle_index", np.full((example_num_tle,), 0.2)),
        "drag_term": ("tle_index", np.full((example_num_tle,), 0.3)),
        "eccentricity": ("tle_index", np.full((example_num_tle,), 0.4)),
        "element_set_number": ("tle_index", np.full((example_num_tle,), 100)),
        "inclination": ("tle_index", np.full((example_num_tle,), 0.5)),
        "mean_anomaly": ("tle_index", np.full((example_num_tle,), 0.6)),
        "mean_motion": ("tle_index", np.full((example_num_tle,), 0.7)),
        "revolution_number": ("tle_index", np.full((example_num_tle,), 103)),
        "right_ascension": ("tle_index", np.full((example_num_tle,), 0.8)),
        "second_derivative": ("tle_index", np.full((example_num_tle,), 0.9)),
    },
    coords={"tle_index": np.arange(example_num_tle)},
    attrs={
        "satellite_shortname": example_satellite_shortname,
        "satellite_name": example_satellite_name,
        "catalog_number": "1",
        "classification": "2",
        "launch_number": 101,
        "launch_piece": "3",
        "launch_year": 102,
        "version": __version__,
        "creation_date": "1980-01-01T00:00:00",
    },
)


class TestFilterXarray(unittest.TestCase):
    def test_example_0(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_0, filter_xarray(example_0))

    def test_example_1(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_1, filter_xarray(example_1))

    def test_example_2(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_2, filter_xarray(example_2))

    def test_example_3(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_3, filter_xarray(example_3))

    def test_example_4(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_4, filter_xarray(example_4))

    def test_example_5(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_5, filter_xarray(example_5))


if __name__ == "__main__":
    unittest.main()
