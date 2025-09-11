"""A python function to compute the distance between two satellites"""

"""___Third-Party Modules___"""
import shapely.vectorized as vectorized

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._constants import LAND_GEOM

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"


def is_land(x, y):
    """Returns boolean land mask for x,y coordinates"""
    return vectorized.contains(LAND_GEOM, x, y)
