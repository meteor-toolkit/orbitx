"""orbitx.utils._tle.get_argument_perigee -"""

"""___Third-Party Modules___"""
import xarray as xr
import numpy as np
from typing import List
from numpy import datetime64

"""___NPL Modules___"""
"""__Built-In Modules__"""
from orbitx.utils._tle.get_argument_perigee import get_argument_perigee
from orbitx.utils._tle.get_ballistic_coefficient import get_ballistic_coefficient
from orbitx.utils._tle.get_catalog_number import get_catalog_number
from orbitx.utils._tle.get_classification import get_classification
from orbitx.utils._tle.get_drag_term import get_drag_term
from orbitx.utils._tle.get_eccentricity import get_eccentricity
from orbitx.utils._tle.get_element_set_number import get_element_set_number
from orbitx.utils._tle.get_inclination import get_inclination
from orbitx.utils._tle.get_launch_number import get_launch_number
from orbitx.utils._tle.get_launch_piece import get_launch_piece
from orbitx.utils._tle.get_launch_year import get_launch_year
from orbitx.utils._tle.get_mean_anomaly import get_mean_anomaly
from orbitx.utils._tle.get_mean_motion import get_mean_motion
from orbitx.utils._tle.get_revolution_number import get_revolution_number
from orbitx.utils._tle.get_right_ascension import get_right_ascension
from orbitx.utils._tle.get_second_derivative import get_second_derivative
from orbitx.utils._tle.get_tle_date import get_tle_date

from orbitx.utils._date_utils import datetime64_to_sec_since
from orbitx import __version__

"""___Authorship___"""
__author__ = __author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>",
]
__created__ = "29/09/2025"
__version__ = 1.0
__maintainer__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>",
]
__status__ = "Development"
__all__ = ["create_xarray"]


def create_xarray(
    tle_line_1: List[str],
    tle_line_2: List[str],
    reference_date: np.datetime64,
    start_date: np.datetime64,
    end_date: np.datetime64,
    satellite_shortname: str,
    satellite_name: str,
) -> xr.Dataset:
    """create_xarray Generate an xarray containing all the information from the TLE file

    Args:
        tle_line_1 (List[str]): The list of first TLE lines
        tle_line_2 (List[str]): The list of second TLE lines
        reference_date (np.datetime64): The date used as a reference when providing dates in "seconds since"
        start_date (np.datetime64): The date from which the orbit will be simulated
        end_date (np.datetime64): The date until which the orbit will be simulated
        satellite_shortname (str): The short name of the satellite (e.g., S3A)
        satellite_name (str): The name of the satellite (e.g., Sentinel-3A)

    Returns:
        xr.Dataset: An xarray containing all information from the TLE file
    """
    tle_dates = np.array(
        [get_tle_date(line1) for line1 in tle_line_1], dtype="datetime64[s]"
    )
    tle_dates_seconds_since = np.array(
        [datetime64_to_sec_since(d, reference_date) for d in tle_dates]
    )
    tle_xarray = xr.Dataset(
        data_vars={
            "reference_date": (reference_date),
            "start_date": (start_date),
            "end_date": (end_date),
            "tle_date": ("tle_index", tle_dates),
            "line_1": ("tle_index", tle_line_1),
            "line_2": ("tle_index", tle_line_2),
            "reference_date_seconds_since1970": (
                datetime64_to_sec_since(
                    reference_date, np.datetime64("1970-01-01T00:00:00")
                )
            ),
            "start_date_seconds_since": (
                datetime64_to_sec_since(start_date, reference_date)
            ),
            "end_date_seconds_since": (
                datetime64_to_sec_since(end_date, reference_date)
            ),
            "tle_date_seconds_since": ("tle_index", tle_dates_seconds_since),
            "argument_perigee": (
                "tle_index",
                np.array(
                    [get_argument_perigee(line2) for line2 in tle_line_2], dtype=float
                ),
            ),
            "balistic_coefficient": (
                "tle_index",
                np.array(
                    [get_ballistic_coefficient(line1) for line1 in tle_line_1],
                    dtype=float,
                ),
            ),
            "drag_term": (
                "tle_index",
                np.array([get_drag_term(line1) for line1 in tle_line_1], dtype=float),
            ),
            "eccentricity": (
                "tle_index",
                np.array(
                    [get_eccentricity(line2) for line2 in tle_line_2], dtype=float
                ),
            ),
            "element_set_number": (
                "tle_index",
                np.array(
                    [get_element_set_number(line1) for line1 in tle_line_1], dtype=float
                ),
            ),
            "inclination": (
                "tle_index",
                np.array([get_inclination(line2) for line2 in tle_line_2], dtype=float),
            ),
            "mean_anomaly": (
                "tle_index",
                np.array(
                    [get_mean_anomaly(line2) for line2 in tle_line_2], dtype=float
                ),
            ),
            "mean_motion": (
                "tle_index",
                np.array([get_mean_motion(line2) for line2 in tle_line_2], dtype=float),
            ),
            "revolution_number": (
                "tle_index",
                np.array(
                    [get_revolution_number(line2) for line2 in tle_line_2], dtype=float
                ),
            ),
            "right_ascension": (
                "tle_index",
                np.array(
                    [get_right_ascension(line2) for line2 in tle_line_2], dtype=float
                ),
            ),
            "second_derivative": (
                "tle_index",
                np.array(
                    [get_second_derivative(line1) for line1 in tle_line_1], dtype=float
                ),
            ),
        },
        coords={"tle_index": np.arange(len(tle_line_1))},
        attrs={
            "satellite_shortname": satellite_shortname,
            "satellite_name": satellite_name,
            "catalog_number": get_catalog_number(tle_line_1[0]),
            "classification": get_classification(tle_line_1[0]),
            "launch_number": get_launch_number(tle_line_1[0]),
            "launch_piece": get_launch_piece(tle_line_1[0]),
            "launch_year": get_launch_year(tle_line_1[0]),
            "version": __version__,
            "creation_date": str(datetime64("now")),
        },
    )
    return tle_xarray
