"""A python function to simulate the orbit of a satellite from on a requested time frame using a collection of TLE's"""

"""___Third-Party Modules___"""
from typing import List, Union, Tuple
import numpy as np
from datetime import datetime

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._orbit import form_sample_space, get_matching_indices, propagate_orbit

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"


def simulate_orbit(
    start_time:datetime,
    end_time:datetime,
    line1: List[str],
    line2: List[str],
    seconds_since_1970: np.ndarray,
    propagation_sampling_interval: Union[float, int],
) -> Tuple[List[float], List[float], List[float]]:
    """
    Return latitude, longitude and time arrays for full simulated orbit

    :param line1: first lines of TLE set
    :param line2: second lines of TLE set
    :param seconds_since_1970: timing of TLE set in seconds since 1970
    :param propagation_sampling_interval: propagation sampling interval in seconds
    :return: tuple containing elements - time of simulation, simulated latitude, simulated longitude
    """
    smpl_space, smpl_space_secs_since_1970 = form_sample_space(
        start_time, end_time, propagation_sampling_interval
    )
    sat_smpl_breakup_idx, tle_ref_lines = get_matching_indices(
        smpl_space_secs_since_1970, seconds_since_1970
    )
    sat_lat_sim: np.ndarray = np.empty((0,), dtype=float)
    sat_lon_sim: np.ndarray = np.empty((0,), dtype=float)
    sat_sec_since: np.ndarray = np.empty((0,), dtype=float)

    if len(tle_ref_lines) == 1:
        secsince1, lat1, lon1, alt1, el1, az1 = propagate_orbit(
            line1[tle_ref_lines[0]],
            line2[tle_ref_lines[0]],
            start_time,
            end_time,
            propagation_sampling_interval,
        )
        sat_lat_sim = lat1
        sat_lon_sim = lon1
        sat_sec_since = secsince1

    else:
        # Change the second-to-last timestamp of the sampling step, to the last one (the end_time). This is to
        # simulate orbit for the exact end-time without handling exceptions outside the loop for a single time
        # stamp.
        smpl_space[-2] = smpl_space[-1]
        for i in range(len(tle_ref_lines) - 1):
            secsince1, lat1, lon1, alt1, el1, az1 = propagate_orbit(
                line1[tle_ref_lines[i]],
                line2[tle_ref_lines[i]],
                smpl_space[sat_smpl_breakup_idx[i]],
                smpl_space[sat_smpl_breakup_idx[i + 1] - 1],
                propagation_sampling_interval,
            )
            sat_lat_sim = np.append(sat_lat_sim, lat1)
            sat_lon_sim = np.append(sat_lon_sim, lon1)
            sat_sec_since = np.append(sat_sec_since, secsince1)

    return (
        sat_sec_since,
        sat_lat_sim,
        sat_lon_sim,
    )