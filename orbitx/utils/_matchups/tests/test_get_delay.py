"""A python function to compute the distance between two satellites"""

"""___Third-Party Modules___"""
import numpy as np
import xarray as xr

"""___NPL Modules___"""

"""__Built-In Modules__"""

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"
__all__ = ["get_delay"]

def get_delay(
    existing_orbits: xr.Dataset,
    new_orbit: xr.Dataset
) -> np.array:
    """Calculate the largest delay in seconds
    between a collection of orbits and a new orbit at each time stamp

    Args:
        existing_orbits (xr.Dataset): the orbits which have already been matched up
        new_orbit (xr.Dataset): the new orbit

    Returns:
        np.array: at each matchup, the maximal delay between the new orbit and the existing orbits
    """
    # compute the lat and lon difference
    delay = np.abs(existing_orbits["time_datetime"] - new_orbit["time_datetime"])
    return delay
