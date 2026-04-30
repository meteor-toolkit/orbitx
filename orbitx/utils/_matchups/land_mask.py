"""A python function to compute the distance between two satellites"""

"""___Third-Party Modules___"""
from typing import Literal
import numpy as np

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._matchups.is_land import is_land

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"


def land_mask(
    lat_c: float, lon_c: float, swath_width: float = 1.0
) -> Literal["OCEAN"] | Literal["LAND"] | Literal["COAST"]:
    """Computes an estimate of land fraction for a scene with centre of (lon_c,lat_c) +/- swath width to deduce whether the correct mask is "LAND", "OCEAN", or "COAST"

    Returns:
        str: The correct mask for this position
    """

    xmin, xmax, ymin, ymax = (
        lon_c - swath_width,
        lon_c + swath_width,
        lat_c - swath_width,
        lat_c + swath_width,
    )
    xx, yy = np.meshgrid(np.linspace(xmin, xmax, 100), np.linspace(ymin, ymax, 100))
    xc = xx.flatten()
    yc = yy.flatten()

    land_cover = is_land(yc, xc)
    land_fraction = sum(np.where(land_cover == True, 1, 0)) / len(land_cover)

    if land_fraction == 0:
        mask = "OCEAN"
    elif land_fraction == 1:
        mask = "LAND"
    else:
        mask = "COAST"
    return mask
