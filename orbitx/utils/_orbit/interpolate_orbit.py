"""A python function to interpolate an orbit from a simulated orbit"""

"""___Third-Party Modules___"""
import numpy as np
import numpy.typing as npt
from typing import Tuple, Any, Callable
from scipy.interpolate import interp1d

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._orbit.interp_circ import interp_circ
from orbitx.utils._date_utils import datetime64_to_sec_since

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"


def interpolate_orbit(
    start_date: np.datetime64,
    end_date: np.datetime64,
    sat_sec_since: npt.NDArray,
    sat_lat_sim: npt.NDArray,
    sat_lon_sim: npt.NDArray,
    interpolation_sampling_interval: np.timedelta64,
    reference_date: np.datetime64 = np.datetime64("1970-01-01T00:00:00"),
) -> Tuple[
    npt.NDArray[np.float64],
    npt.NDArray[np.datetime64],
    npt.NDArray[np.float64],
    npt.NDArray[np.float64],
]:
    """interpolate_orbit Interpolate the orbit at desired time resolution

    Used to interpolate the physics-simulated orbits at a sufficiently high resolution

    :param start_date: 
    :type start_date: datetime.datetime
    :param end_date: 
    :type end_date: datetime.datetime
    :param sat_sec_since: 
    :type sat_sec_since: npt.NDArray
    :param sat_lat_sim: 
    :type sat_lat_sim: npt.NDArray
    :param sat_lon_sim: 
    :type sat_lon_sim: npt.NDArray
    :param interpolation_sampling_interval: 
    :type interpolation_sampling_interval: float
    :param reference_date: 
    :type reference_date: datetime.datetime, optional
    :return: 
    :rtype: Tuple[npt.NDArray, npt.NDArray, npt.NDArray, npt.NDArray]

    Args:
        start_date (np.datetime64): The date from which the orbit should be interpolated
        end_date (np.datetime64): The date until which the orbit should be simulated
        sat_sec_since (npt.NDArray): The times at which the orbits were simulated with physics (in seconds since a reference date)
        sat_lat_sim (npt.NDArray): The simulated latitudes of the satellites
        sat_lon_sim (npt.NDArray): The simulated longitudes of the satellites
        interpolation_sampling_interval (np.timedelta64): The time lapse between two successive interpolation times
        reference_date (_type_, optional): The time variables are given in seconds since a reference date. This input sets the reference date used. Defaults to np.datetime64("1970-01-01T00:00:00").

    Returns:
        Tuple[ npt.NDArray[np.float64], npt.NDArray[np.datetime64], npt.NDArray[np.float64], npt.NDArray[np.float64], ]: A tuple containing the times at which the interpolated values are obtained (in seconds since the reference date), and the times at which the interpolated values are obtained (in numpy datetime64 format), the interpolated latitude, the interpolated longitude
    """
    f1_lat_linear: interp1d[npt.NDArray[np.float64], npt.NDArray[np.float64]] = (
        interp1d(sat_sec_since, sat_lat_sim)
    )
    f1_lon_linear: Callable[[npt.NDArray[np.float64]], npt.NDArray[np.float64]] = (
        interp_circ(sat_sec_since, sat_lon_sim)
    )

    end_date = end_date + interpolation_sampling_interval
    interpolate_date: npt.NDArray[np.datetime64] = np.arange(
        start=start_date, stop=end_date, step=interpolation_sampling_interval
    )
    interpolate_time = np.array(
        [
            datetime64_to_sec_since(date, reference_date=reference_date)
            for date in interpolate_date
        ],
        dtype=np.float64,
    )
    return (
        interpolate_time,
        interpolate_date,
        f1_lat_linear(interpolate_time),
        f1_lon_linear(interpolate_time),
    )
