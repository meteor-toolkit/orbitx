"""orbitx.utils._tle.get_mean_motion - """

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
__all__ = ["get_mean_motion"]

def get_mean_motion(line2: str) -> float:
    r"""Finds the mean motion in revolutions per day from the second line of the TLE.
    The the mean motion corresponds to the characters 53 to 63 of the second line.

    Args:
        line2 (str): The second line of the considered TLE

    Returns:
        float: The mean motion

    Example:
        .. code-block:: python3

            line2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
            mean_motion = get_mean_motion(line2)
            print(mean_motion)
        
        .. code-block:: bash

            >>> 15.72125391
    """
    mean_motion_str = line2[52:63]
    mean_motion_str = re.sub(' ', '', mean_motion_str)
    
    return float(mean_motion_str)
