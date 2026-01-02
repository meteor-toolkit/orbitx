"""A python function to compute the distance between two satellites"""

"""___Third-Party Modules___"""
import numpy as np
import xarray as xr

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._constants import EARTH_RADIUS

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"
__all__ = ["get_dist"]

def get_dist(
    existing_orbits: xr.Dataset,
    new_orbit: xr.Dataset
) -> np.array:
    """Calculate the largest distance in kilometers on the earth (specified in decimal degrees)
    between a collection of orbits and a new orbit at each time stamp

    Args:
        existing_orbits (xr.Dataset): the orbits which have already been matched up
        new_orbit (xr.Dataset): the new orbit

    Returns:
        np.array: at each time stamp, the largest of the distances between the new orbit and each of the existing orbits
    """
    # compute the lat and lon difference
    dlon = (existing_orbits["lon"] - new_orbit["lon"])
    dlat = (existing_orbits["lat"] - new_orbit["lat"])
    # haversine formula

    a = np.sin(dlat / 2) ** 2 + np.cos(existing_orbits["lat"]) * np.cos(new_orbit["lat"]) * np.sin(dlon / 2) ** 2
    c = 2 * np.asin(np.sqrt(a))
    r = EARTH_RADIUS
    return c * r
