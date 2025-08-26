"""A python function to compute the distance between two satellites"""

"""___Third-Party Modules___"""
from math import radians, cos, sin, asin, sqrt
import numpy as np
from typing import Union

"""___NPL Modules___"""

"""__Built-In Modules__"""


"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"

def get_dist(
    lon1: Union[int, float],
    lat1: Union[int, float],
    lon2: Union[int, float],
    lat2: Union[int, float],
) -> float:
    """
    Calculate the distance in kilometers between two points
    on the earth (specified in decimal degrees)

    :param lon1: longitude value of point one
    :param lat1: latitude value of point one
    :param lon2: longitude value of point two
    :param lat2: latitude value of point two
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r


# function to get distance between two lon lat points
get_distance = np.vectorize(get_dist)