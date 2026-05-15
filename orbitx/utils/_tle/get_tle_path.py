"""orbitx.utils._tle.get_tle_path -"""

"""___Third-Party Modules___"""
import os

"""___NPL Modules___"""

"""__Built-In Modules__"""

"""___Authorship___"""
__author__ = __author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>",
]
__created__ = "22/09/2025"
__version__ = 1.0
__maintainer__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>",
]
__status__ = "Development"
__all__ = ["get_tle_path"]


def get_tle_path(satellite_name: str) -> str:
    r"""Returns path for TLE file for defined satellite

    :param satellite_name: satellite short name as included in TLE file name ``TLEset_XXX``, where ``XXX`` may be ``S2A`` for the Sentinel-2A mission
    :type satellite_name: str
    :return: satellite TLE file path
    :rtype: Optional[str]
    """
    from orbitx import TLE_PATH

    path = ""
    found: bool = False
    for tle_dir in TLE_PATH:
        path = os.path.abspath(
            os.path.join(tle_dir, "TLEset_" + satellite_name + ".txt")
        )
        if os.path.isfile(path):
            found = True
            break
    if not found:
        raise FileNotFoundError(
            "No TLE file for this satellite. Use a custom satellite argument with your own file."
        )
    return path
