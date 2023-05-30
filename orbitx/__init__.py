"""orbitx - Propagate satellite orbits to identify matchups."""

__author__ = "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>"
__all__ = ["TLE_PATH", "add_to_tle_path", "setup_orekit", "return_matchups"]

from ._version import get_versions
import os
from typing import Optional
import orekit
from orekit.pyhelpers import setup_orekit_curdir
from orbitx.OrbitX import return_matchups


__version__ = get_versions()["version"]
del get_versions


this_directory = os.path.dirname(__file__)
data_directory = os.path.join(this_directory, "data")
TLE_PATH = [os.path.join(data_directory, "tle")]


def add_to_tle_path(new_tle_path: str, prepend: bool = True) -> None:
    """
    The TLE_PATH list defines the directory locations orbitx looks for TLE files.
    This function adds new paths to this list.

    :param new_tle_path: Directory containing
    :param prepend: (default: ``True``) ``True`` if add to start of TLE_PATH list, ``False`` if add to end
    """

    if not prepend:
        TLE_PATH.append(new_tle_path)
    else:
        TLE_PATH.insert(0, new_tle_path)


def setup_orekit(orekit_data_path: Optional[str] = None) -> None:

    vm = orekit.initVM()
    setup_orekit_curdir(filename=orekit_data_path)


setup_orekit(os.path.join(data_directory, "orekit-data.zip"))




