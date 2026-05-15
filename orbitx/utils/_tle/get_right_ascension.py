"""orbitx.utils._tle.get_right_assention -"""

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
__all__ = ["get_right_ascension"]


def get_right_ascension(line2: str) -> float:
    r"""Finds the right ascension of the ascending node in the ECI reference frame measured from the vernal point from the second line of the TLE.
    The the right ascention corresponds to the characters 18 to 25 of the second line.

    Args:
        line2 (str): The second line of the considered TLE

    Returns:
        float: The right ascension

    Example:
        .. code-block:: python3

            line2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
            right_ascension = get_right_ascension(line2)
            print(right_ascension)

        .. code-block:: text

            247.4627
    """
    right_ascension_str = line2[17:25]

    return float(re.sub(" ", "", right_ascension_str))
