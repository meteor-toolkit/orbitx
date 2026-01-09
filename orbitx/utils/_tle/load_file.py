"""orbitx.utils._tle.load_file - a function reading the TLEs and returning the list of first lines and the list of second lines"""

"""___Third-Party Modules___"""
from typing import Tuple, List
import numpy as np

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
__all__ = ["load_file"]


def load_file(tle_filepath: str) -> Tuple[List[str], List[str]]:
    """Getting the list of first lines and the list of second lines of all TLEs in the file.

    Args:
        tle_filepath (str): The path of the file containing the TLEs

    Returns:
        tle_line_1 (List[str]): The list of all first TLE lines
        tle_line_2 (List[str]): The list of all second TLE lines
    """
    with open(tle_filepath, "r") as f:
        lines = np.array(f.read().splitlines(), dtype=str)
    # endregion

    # region Access indexes of line-1 and line-2
    length = len(lines)
    if (
        len(lines[0]) < 69
    ):  # If the file includes the name of the mission at the beginning of each TLE, the name is at position 0, 3, ... (and we do not care about it)
        line_1_indexes = np.arange(1, length, 3)  # Line 1's are at position 1, 4, ...
        line_2_indexes = np.arange(2, length, 3)  # Line 2's are at position 2, 5, ...
    else:  # If the name is not included
        line_1_indexes = np.arange(0, length, 2)  # Line 1's are at position 0, 2, ...
        line_2_indexes = np.arange(1, length, 2)  # Line 2's are at position 1, 3, ...

    tle_line_1 = lines[line_1_indexes]  # list of all line 1s
    tle_line_2 = lines[line_2_indexes]  # list of all line 2s
    return tle_line_1, tle_line_2
