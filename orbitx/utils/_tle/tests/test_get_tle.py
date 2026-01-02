"""orbitx.utils._tle.get_tle -"""

"""___Third-Party Modules___"""
import numpy as np
from typing import List, Tuple
import warnings

"""___NPL Modules___"""
"""__Built-In Modules__"""
from orbitx.utils._date_utils import datetime64_to_sec_since

"""___Authorship___"""
__author__ = __author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>",
]
__created__ = "22/09/2025"
__version__ = 1.0
__maintainer__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>",
]
__status__ = "Development"
__all__ = ["get_tle"]


def get_tle(
    self,
    satellite: str,
    start_date: np.datetime64,
    end_date: np.datetime64,
    reference_date: np.datetime64 = np.datetime64("1970-01-01T00:00:00"),
) -> Tuple[List[str], List[str], np.ndarray]:
    r"""
    Returns two-line elements within defined time window, with seconds since reference date

    :param satellite: satellite short name as included in TLE file name ``TLEset_XXX``,
            where ``XXX`` may be ``S2A`` for the Sentinel-2A mission
    :param start_date: start of time window
    :param end_date: end of time window

    :return: tuple containing elements - first TLE lines, second TLE lines, times of TLEs in seconds since reference date
    """

    # region Read TLE file.
    tle_path = self.return_tle_path(satellite)
    if tle_path is None:
        raise ValueError(f"No TLE file found for '{satellite}'")
    with open(tle_path, "r") as f:
        lines = np.array(f.read().splitlines())
    # endregion

    # region Access indexes of line-1 and line-2
    length = len(lines)
    if (
        len(lines[0]) < 69
    ):  # If the file includes the name of the mission at the beginning of each TLE, the name is at position 0, 3, ... (and we do not care about it)
        line_1_indexes = np.arange(1, length, 3)  # Line 1's are at position 1, 4, ...
        line_2_indexes = np.arange(2, length, 3)  # Line 2's are at position 2, 5, ...
    else:  # If the name is not included
        line_1_indexes = np.arange(0, length, 2)  # Line 1's are at position 0, 2, ...
        line_2_indexes = np.arange(1, length, 2)  # Line 2's are at position 1, 3, ...

    tle_line_1 = lines[line_1_indexes]  # list of all line 1s
    tle_line_2 = lines[line_2_indexes]  # list of all line 2s
    # endregion

    # Get date times
    tle_date = np.array(
        [self.return_date_from_tle(tle_line_1_i) for tle_line_1_i in tle_line_1]
    )
    tle_time_since = np.array(
        [datetime64_to_sec_since(d, reference_date) for d in tle_date]
    )
    start_time_since = datetime64_to_sec_since(start_date, reference_date)
    end_time_since = datetime64_to_sec_since(end_date, reference_date)

    # Filter time
    lower_bound_tle_time = [t for t in tle_time_since if t <= start_time_since]
    if len(lower_bound_tle_time) == 0:
        warnings.warn(
            "The oldest TLE file is more recent than the start time requested.\n Oldest TLE file: {}\n Start time requested: {}".format(
                np.min(tle_date), start_date
            )
        )
    lower_bound_tle_time = (
        start_time_since
        if len(lower_bound_tle_time) == 0
        else np.max(lower_bound_tle_time)
    )
    upper_bound_tle_time = [t for t in tle_time_since if t >= end_time_since]
    if len(upper_bound_tle_time) == 0:
        warnings.warn(
            "The most recent TLE file is older than the end time requested.\n Oldest TLE file: {}\n Start time requested: {}".format(
                np.max(tle_date), end_date
            )
        )
    upper_bound_tle_time = (
        end_time_since
        if len(upper_bound_tle_time) == 0
        else np.min(upper_bound_tle_time)
    )
    idx = [
        i
        for i, t_i in enumerate(tle_time_since)
        if (t_i >= lower_bound_tle_time) and (t_i < upper_bound_tle_time)
    ]

    if not idx:
        # If there is no TLE between start- and end-time, just get the one TLE which is closest to start_time
        closest_tle = np.argmin(np.abs(tle_time_since - start_time_since))

        tle_line_1 = [tle_line_1[closest_tle]]
        tle_line_2 = [tle_line_2[closest_tle]]
        tle_time_since = np.array([tle_time_since[closest_tle]])

    else:
        # Filter TLE set
        tle_line_1 = tle_line_1[idx]
        tle_line_2 = tle_line_2[idx]
        tle_time_since = tle_time_since[idx]
    return tle_line_1, tle_line_2, tle_time_since
