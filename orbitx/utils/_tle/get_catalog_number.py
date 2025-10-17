"""orbitx.utils._tle.get_catalog_number - """

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
__all__ = ["get_catalog_number"]

def get_catalog_number(line1: str) -> str:
    r"""Finds the catalog number in the first line of the TLE.
    This corresponds to characters three to seven of the first line of the TLE.

    Args:
        line1 (str): The first line of the considered TLE

    Returns:
        str: The catalog number of the satellite

    Example:
        .. code-block:: python3

            line1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
            catalog_number = get_catalog_number(line1)
            print(catalog_number)
        
        .. code-block:: bash

            >>> 25544
    """
    return line1[2:7]