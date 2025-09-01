"""A python function to interpolate an orbit from a simulated orbit"""

"""___Third-Party Modules___"""
import datetime
import numpy as np
from typing import Tuple, Any
from scipy.interpolate import interp1d

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._orbit.interp_circ import interp_circ

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"



def interpolate_orbit(
        start_time,
        end_time,
        sat_sec_since,
        sat_lat_sim,
        sat_lon_sim,
        interpolation_sampling_interval
) -> Tuple[Any, Any, np.ndarray]:
    """
    Interpolate the propagated orbit for a higher spatiotemporal sampling rate.

    :param sat_sec_since: time of simulated/propagated orbit
    :param sat_lat_sim: latitude of simulated/propagated orbit
    :param sat_lon_sim: longitude of simulated/propagated orbit
    :param interpolation_sampling_interval: interpolation sampling interval
    :return: tuple containing latitude, longitude, and time of the simulated/interpolated orbit
    """
    f1_lat_linear = interp1d(sat_sec_since, sat_lat_sim)
    f1_lon_linear = interp_circ(sat_sec_since, sat_lon_sim)

    interp_smpl_space = np.arange(
        (start_time - datetime.datetime(1970, 1, 1, 0, 0, 0)).total_seconds(),
        (end_time - datetime.datetime(1970, 1, 1, 0, 0, 0)).total_seconds()
        + interpolation_sampling_interval,
        interpolation_sampling_interval,
    )
    interpolate_date = np.array([datetime.datetime(1970, 1, 1, 0, 0, 0) + datetime.timedelta(seconds = time_delta) for time_delta in interp_smpl_space])
    return (
        f1_lat_linear(interp_smpl_space),
        f1_lon_linear(interp_smpl_space),
        interp_smpl_space,
        interpolate_date
    )