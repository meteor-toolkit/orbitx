"""orbitx.utils._tle.get_element_set_number - """

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
__all__ = ["get_element_set_number"]


def get_element_set_number(line1: str) -> int:
    r"""Finds the element set number of the TLE from the first line of the TLE.
    The element set number corresponds to characters 65 to 68 of the first line of the TLE.

    Args:
        line1 (str): The first line of the considered TLE

    Returns:
        int: The element set number

    Example:
        .. code-block:: python3

            line1 = "1 25544U 98067A   08264.51782528 -.00002182  12345-5 -11606-4 0  2927"
            element_set_number = get_element_set_number(line1)
            print(element_set_number)
        
        .. code-block:: text

            292
    """
    element_set_number_str = line1[64:68]
    
    return int(re.sub(' ', '', element_set_number_str))
