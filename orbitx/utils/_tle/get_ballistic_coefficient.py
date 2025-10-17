"""orbitx.utils._tle.get_ballistic_coefficient - """

"""___Third-Party Modules___"""
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
__all__ = ["get_ballistic_coefficient"]

def get_ballistic_coefficient(line1: str) -> float:
    r"""Finds the ballistic coefficient (first derivate of the mean motion) of the satellite from the first line of the TLE.
    The ballistic coefficient corresponds to the characters 34 to 43 of the first line.

    Args:
        line1 (str): The first line of the considered TLE

    Returns:
        float: The ballistic coefficient

    Example:
        .. code-block:: python3

            line1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
            ballistic_coefficient = get_ballistic_coefficient(line1)
            print(ballistic_coefficient)
        
        .. code-block:: bash

            >>> -2.182e-05
    """
    return float(line1[33:43])
