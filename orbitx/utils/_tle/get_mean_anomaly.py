"""orbitx.utils._tle.get_mean_anomaly - """

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
__all__ = ["get_mean_anomaly"]

def get_mean_anomaly(line2: str) -> float:
    r"""Finds the mean anomaly in degrees from the second line of the TLE.
    The the mean anomaly corresponds to the characters 44 to 51 of the second line.

    Args:
        line2 (str): The second line of the considered TLE

    Returns:
        float: The mean anomaly

    Example:
        .. code-block:: python3

            line2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
            mean_anomaly = get_mean_anomaly(line2)
            print(mean_anomaly)
        
        .. code-block:: text

            325.0288
    """
    mean_anomaly_str = line2[43:51]
    mean_anomaly_str = re.sub(' ', '', mean_anomaly_str)
    
    return float(mean_anomaly_str)
