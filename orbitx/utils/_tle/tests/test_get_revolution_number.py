"""orbitx.utils._tle.get_revolution_number -"""

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
__all__ = ["get_revolution_number"]


def get_revolution_number(line2: str) -> int:
    r"""Finds the revolution number from the second line of the TLE.
    The the revolution number corresponds to the characters 64 to 68 of the second line.

    Args:
        line2 (str): The second line of the considered TLE

    Returns:
        int: The revolution number

    Example:
        .. code-block:: python3

            line2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
            revolution_number = get_revolution_number(line2)
            print(revolution_number)

        .. code-block:: text

            56353
    """
    revolution_number_str = line2[63:68]
    revolution_number_str = re.sub(" ", "", revolution_number_str)

    return int(revolution_number_str)
