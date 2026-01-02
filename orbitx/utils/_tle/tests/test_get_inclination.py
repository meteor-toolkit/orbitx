"""orbitx.utils._tle.get_inclination -"""

"""___Third-Party Modules___"""
import re

"""___NPL Modules___"""
"""__Built-In Modules__"""

"""___Authorship___"""
__author__ = __author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>",
]
__created__ = "29/09/2025"
__version__ = 1.0
__maintainer__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>",
]
__status__ = "Development"
__all__ = ["get_inclination"]


def get_inclination(line2: str) -> float:
    r"""Finds the inclination of the satellite from the second line of the TLE.
    The inclination corresponds to the characters nine to 16 of the second line.

    Args:
        line2 (str): The second line of the considered TLE

    Returns:
        float: The inclination of the satellite

    Example:
        .. code-block:: python3

            line2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
            inclination = get_inclination(line2)
            print(inclination)

        .. code-block:: text

            51.6416
    """
    inclination_str = line2[8:16]

    return float(re.sub(" ", "", inclination_str))
