""".py file containing a function implementing interpolation for a quantity taking value on the circle (e.g., the longitude)"""

"""__Built-In Modules__"""

"""___Third-Party Modules___"""
import numpy as np
from numpy import typing as npt
from scipy import interpolate
from typing import Callable
from functools import partial
import warnings

"""___NPL Modules___"""
"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "30/07/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"


def interp_circ(
    x: np.ndarray,
    y: np.ndarray,
    period: float = 360.0
) -> Callable[[npt.NDArray], npt.NDArray]:
    """interp_circ interpolation for periodic-valued data

    Creates a function to interpolate data valued on a circle (for period = 360, a datapoint with value 359 is at distance 2 of a datapoint with value 1)

    :param x: The values of the time-axis variable for the data to interpolate (not periodic)
    :type x: np.ndarray
    :param y: The values to interpolate (periodic)
    :type y: np.ndarray
    :return: A function which takes time axis values as input and returns the interpolated values
    :rtype: Callable[[npt.NDArray], npt.NDArray]
    """
    if np.any(y > period / 2):
        warnings.warn("Some of the values in y are larger than the indicated period.")
    if np.any(y < -period / 2):
        warnings.warn("Some of the values in y are smaller than 0.")
    complement_period = np.unwrap(y + period / 2, period=period)
    return partial(interp_circ_, x=x, y=complement_period, period=period)


def interp_circ_(
    x_new: np.ndarray, x: np.ndarray, y: np.ndarray, period: float = 360.0
) -> np.ndarray:
    """interp_circ_ _summary_

    _extended_summary_

    :param x: The values of the time-axis variable for the data to interpolate (not periodic)
    :type x: np.ndarray
    :param y: The values to interpolate (periodic)
    :type y: np.ndarray
    :param x_new: New locations at which to evaluate y
    :type x_new: np.ndarray
    :param period: The preiod of the variable y
    :type period: float
    :return: The estimated values of y at the requested values of x
    :rtype: np.ndarray
    """
    f = interpolate.interp1d(x, y, kind="linear", bounds_error=False, fill_value=None)
    complement_interp = f(x_new)
    return (complement_interp % period) - (period / 2)
