"""orbitx - Propagate satellite orbits to identify matchups."""

__author__ = "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>"
__all__ = ["TLE_PATH", "add_to_tle_path", "setup_orekit", "return_matchups", "Orbit", "Matchups"]

from orbitx.orbit import Orbit
from orbitx.matchups import Matchups

from ._version import get_versions
import os
from typing import Optional
import orekit
from orekit.pyhelpers import setup_orekit_curdir


__version__ = get_versions()["version"]
del get_versions


this_directory = os.path.dirname(__file__)
data_directory = os.path.join(this_directory, "data")
TLE_PATH = [os.path.join(data_directory, "tle")]
S6_ORBIT_PATH = [
    os.path.join(
        data_directory,
        "Sentinel6_sample_orbit",
        "S6A_P4_2__LR_STD__NT_050_155_20220324T131606_20220324T141219_F05_unvalidated.nc",
    )
]


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
    if orekit_data_path:
        setup_orekit_curdir(filename=orekit_data_path)
    else:
        setup_orekit_curdir()


setup_orekit(os.path.join(data_directory, "orekit-data.zip"))
