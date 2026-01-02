"""orbitx.utils._tle - A submodule for backend in TLE class."""

__author__ = "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>"
__all__ = [
    "get_argument_perigee",
    "get_ballistic_coefficient",
    "get_catalog_number",
    "get_classification",
    "get_drag_term",
    "get_eccentricity",
    "get_element_set_number",
    "get_inclination",
    "get_launch_number",
    "get_launch_piece",
    "get_launch_year",
    "get_mean_anomaly",
    "get_mean_motion",
    "get_revolution_number",
    "get_right_ascension",
    "get_second_derivative",
    "get_tle_date",
    "get_tle_path",
    "load_file",
    "create_xarray",
    "filter_xarray",
]

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
from orbitx.utils._tle.get_tle_path import get_tle_path
from orbitx.utils._tle.load_file import load_file
from orbitx.utils._tle.create_xarray import create_xarray
from orbitx.utils._tle.filter_xarray import filter_xarray
