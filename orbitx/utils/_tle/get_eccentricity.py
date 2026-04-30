"""orbitx.utils._tle.get_eccentricity -"""

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
__all__ = ["get_eccentricity"]


def get_eccentricity(line2: str) -> float:
    r"""Finds the eccentricity from the second line of the TLE.
    The the right ascention corresponds to the characters 27 to 33 of the second line.

    Args:
        line2 (str): The second line of the considered TLE

    Returns:
        float: The eccentricity

    Example:
        .. code-block:: python3

            line2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
            eccentricity = get_eccentricity(line2)
            print(eccentricity)

        .. code-block:: text

            0.0006703
    """
    eccentricity_str = line2[26:33]
    eccentricity_str = re.sub(" ", "", eccentricity_str)
    eccentricity_str = f"0.{eccentricity_str}"

    return float(eccentricity_str)
