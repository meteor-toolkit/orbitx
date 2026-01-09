"""orbitx.utils._tle.get_argument_perigee -"""

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
__all__ = ["get_argument_perigee"]


def get_argument_perigee(line2: str) -> float:
    r"""Finds the argument of the perigee in degrees from the second line of the TLE.
    The the argument of the perigee corresponds to the characters 35 to 42 of the second line.

    Args:
        line2 (str): The second line of the considered TLE

    Returns:
        float: The argument of the perigee

    Example:
        .. code-block:: python3

            line2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
            arg_perigee = get_argument_perigee(line2)
            print(arg_perigee)

        .. code-block:: text

            130.536
    """
    arg_perigee_str = line2[34:42]
    arg_perigee_str = re.sub(" ", "", arg_perigee_str)

    return float(arg_perigee_str)
