"""orbitx.utils._tle.get_argument_perigee -"""

"""___Third-Party Modules___"""
import xarray as xr
import warnings
import numpy as np
import numpy.typing as npt
from typing import Tuple, List

"""___NPL Modules___"""
"""__Built-In Modules__"""

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
__all__ = ["filter xarray"]


def filter_xarray(tle_xarray: xr.Dataset) -> xr.Dataset:
    """Selecting TLEs that are relevant to the time span of the simulation.

    Args:
        tle_xarray (xr.Dataset): The full TLE xarray

    Returns:
        tle_xarray (xr.Dataset): The TLE xarray filtered
    """
    # Filter time
    # lower_bound_tle_time = np.array([
    #     t for t in tle_xarray["tle_date"].values if t <= tle_xarray["start_date"].values
    # ])
    previous_tle_times: npt.NDArray[np.datetime64] = tle_xarray.where(
        lambda x: x["tle_date"] < tle_xarray["start_date"].values
    )["tle_date"].values
    if previous_tle_times.shape[0] == 0:
        warnings.warn(
            f"""The oldest TLE file is more recent than the start time requested.
Oldest TLE file: {np.min(tle_xarray["start_date"].values)}
Start time requested: {tle_xarray["start_date"].values}"""
        )
        lower_bound_tle_time: npt.NDArray[np.datetime64] = tle_xarray["start_date"].values
    else:
        lower_bound_tle_time = np.max(previous_tle_times)

    later_tle_times: npt.NDArray[np.datetime64] = tle_xarray.where(
        lambda x: x["tle_date"] >= tle_xarray["end_date"].values
    )["tle_date"].values
    # upper_bound_tle_time = [
    #     t for t in tle_xarray["tle_date"].values if t >= tle_xarray["end_date"].values
    # ]
    if len(later_tle_times) == 0:
        warnings.warn(
            f"""The most recent TLE file is older than the end time requested.
Oldest TLE file: {np.max(tle_xarray["tle_date"].values)}
Start time requested: {tle_xarray["end_date"]}"""
        )
        upper_bound_tle_time: npt.NDArray[np.datetime64] = tle_xarray["end_date"].values
    else:
        upper_bound_tle_time = np.min(later_tle_times)
    idx = [
        i
        for i, t_i in enumerate(tle_xarray["tle_date"])
        if (t_i >= lower_bound_tle_time) and (t_i < upper_bound_tle_time)
    ]

    if not idx:
        # If there is no TLE between start- and end-time, just get the one TLE which is closest to start_time
        closest_tle = np.argmin(
            np.abs(tle_xarray["tle_date"].values - tle_xarray["start_date"].values)
        )
        tle_xarray = tle_xarray.isel(tle_index=[closest_tle])

    else:
        # Filter TLE set
        tle_xarray = tle_xarray.isel(tle_index=idx)

    return tle_xarray
