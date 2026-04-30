"""A python function to simulate the orbit of a satellite from on a requested time frame using a collection of TLE's"""

"""___Third-Party Modules___"""
from typing import List, Tuple
import numpy as np
import numpy.typing as npt

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._orbit.form_sample_space import form_sample_space
from orbitx.utils._orbit.get_matching_indices import get_matching_indices
from orbitx.utils._orbit.propagate_orbit import propagate_orbit
from orbitx import TLE

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"


def simulate_orbit(
    start_date: np.datetime64,
    end_date: np.datetime64,
    tle: TLE,
    propagation_sampling_interval: np.timedelta64,
    reference_date: np.datetime64 = np.datetime64("1970-01-01T00:00:00"),
) -> Tuple[
    npt.NDArray[np.float64],
    npt.NDArray[np.datetime64],
    npt.NDArray[np.float64],
    npt.NDArray[np.float64],
]:
    """Return latitude, longitude and time arrays for full simulated orbit

    Args:
        start_date (np.datetime64): The date from which the orbit needs to be simulated
        end_date (np.datetime64): The date until which the orbit needs to be simulated
        tle (TLE): The TLE object containing relevant information
        propagation_sampling_interval (np.timedelta64): propagation sampling interval in seconds
        reference_date (_type_, optional): _description_. Defaults to np.datetime64("1970-01-01T00:00:00").

    Returns:
        Tuple[ npt.NDArray[np.float64], npt.NDArray[np.datetime64], npt.NDArray[np.float64], npt.NDArray[np.float64], ]: A tuple containing the simultation times in seconds since the reference date, the simulation time in numpy datetime64, latitudes and longitudes.
    """
    smpl_space, smpl_space_secs_since = form_sample_space(
        start_date, end_date, propagation_sampling_interval, reference_date
    )
    sat_smpl_breakup_idx, tle_ref_lines = get_matching_indices(
        smpl_space_secs_since, tle.tle_date_seconds_since
    )
    sat_lat_sim: npt.NDArray[np.float64] = np.empty((0,), dtype=np.float64)
    sat_lon_sim: npt.NDArray[np.float64] = np.empty((0,), dtype=np.float64)
    sat_sec_since: npt.NDArray[np.float64] = np.empty((0,), dtype=np.float64)
    sat_date: npt.NDArray[np.datetime64] = np.empty((0,), dtype=np.datetime64)

    if len(tle_ref_lines) == 1:
        secsince1, date, lat1, lon1, _, _, _ = propagate_orbit(
            tle.tle_line_1[tle_ref_lines[0]],
            tle.tle_line_2[tle_ref_lines[0]],
            start_date,
            end_date,
            propagation_sampling_interval,
            reference_date,
        )
        sat_lat_sim = lat1
        sat_lon_sim = lon1
        sat_sec_since = secsince1
        sat_date = date

    else:
        # Change the second-to-last timestamp of the sampling step, to the last one (the end_time). This is to
        # simulate orbit for the exact end-time without handling exceptions outside the loop for a single time
        # stamp.
        smpl_space[-2] = smpl_space[-1]
        for i in range(len(tle_ref_lines) - 1):
            secsince1, date, lat1, lon1, _, _, _ = propagate_orbit(
                tle.tle_line_1[tle_ref_lines[i]],
                tle.tle_line_2[tle_ref_lines[i]],
                smpl_space[sat_smpl_breakup_idx[i]],
                smpl_space[sat_smpl_breakup_idx[i + 1] - 1],
                propagation_sampling_interval,
                reference_date,
            )
            sat_lat_sim = np.append(sat_lat_sim, lat1)
            sat_lon_sim = np.append(sat_lon_sim, lon1)
            sat_sec_since = np.append(sat_sec_since, secsince1)
            sat_date = np.append(sat_date, date)

    return (
        sat_sec_since,
        sat_date,
        sat_lat_sim,
        sat_lon_sim,
    )
