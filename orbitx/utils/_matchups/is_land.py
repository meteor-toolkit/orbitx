"""A python function to compute the distance between two satellites"""

"""___Third-Party Modules___"""
import numpy as np
import numpy.typing as npt
from shapely import contains_xy

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx import LAND_GEOM

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"


def is_land(x: npt.ArrayLike, y: npt.ArrayLike) -> npt.NDArray[np.bool_]:
    """Returns boolean land mask for x,y coordinates

    Args:
        x (float): The longitude of the point
        y (float): The latitude of the point

    Returns:
        bool: True if the point is on land, false otherwise
    """
    return contains_xy(LAND_GEOM, x, y)
