"""orbitx.utils._tle.get_launch_piece - """

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
__all__ = ["get_launch_piece"]

def get_launch_piece(line1: str) -> str:
    r"""Finds the launch piece identifier of this satellite.
    The launch piece identifier corresponds to the character 15 of the first line.
    When several objects are launched at once, the launch piece uniquely identifies the different objects launched.

    Args:
        line1 (str): The first line of the considered TLE

    Returns:
        str: The launch piece identifier of this satellite

    Example:
        .. code-block:: python3

            line1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
            launch_piece = get_launch_piece(line1)
            print(launch_number)
        
        .. code-block:: text

            A
    """
    return line1[14]
