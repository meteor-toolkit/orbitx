"""orbitx.utils._tle.get_launch_number -"""

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
__all__ = ["get_launch_number"]

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
__all__ = ["get_launch_number"]


def get_launch_number(line1: str) -> int:
    r"""Finds the launch number of this satellite in the launch year.
    The launch number corresponds to the characters 12 to 14 of the first line.

    Args:
        line1 (str): The first line of the considered TLE

    Returns:
        str: The launch number of the satellite

    Example:
        .. code-block:: python3

            line1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
            launch_number = get_launch_number(line1)
            print(launch_number)

        .. code-block:: text

            67
    """
    return int(line1[11:14])
