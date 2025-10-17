"""orbitx.utils._tle.get_launch_year - """

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
__all__ = ["get_launch_year"]

def get_launch_year(line1: str) -> int:
    r"""Finds the launch year of the satellite from the first line of the TLE.
    The launch year corresponds to the characters ten and eleven of the first line.

    Args:
        line1 (str): The first line of the considered TLE

    Returns:
        str: The launch year of the satellite

    Example:
        .. code-block:: python3

            line1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
            launch_year = get_launch_year(line1)
            print(launch_year)
        
        .. code-block:: bash

            >>> 1998
    """
    short_year_launch = int(line1[9:11])
    if short_year_launch > 70:
        return 1900 + short_year_launch
    else:
        return 2000 + short_year_launch
