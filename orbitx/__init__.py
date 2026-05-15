"""orbitx - Propagate satellite orbits to identify matchups."""

__author__ = "MetEOR Toolkit Team <team@comet-toolkit.org>"
__all__ = [
    "LAND_GEOM",
    "TLE_PATH",
    "add_to_tle_path",
    "setup_orekit",
    "Orbit",
    "Matchups",
    "TLE",
]
import os
from importlib.metadata import PackageNotFoundError, version
from typing import Optional

import cartopy.io.shapereader as shpreader
import numpy as np
import shapely.geometry as sgeom

from orbitx.deps import init_orekit

try:
    __version__ = version("orbitx")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"


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
SHP_PATH = os.path.join(data_directory, "land_mask", "ne_50m_land.shp")
__geoms_with_multipol = list(shpreader.Reader(SHP_PATH).geometries())

__geoms = np.empty((0,), dtype=sgeom.Polygon)
for geom in __geoms_with_multipol:
    if isinstance(geom, sgeom.MultiPolygon):
        multipol = list(geom.geoms)
        for polygon in multipol:
            __geoms = np.append(__geoms, [polygon])
    else:
        __geoms = np.append(__geoms, geom)

LAND_GEOM = sgeom.MultiPolygon([sgeom.shape(geom) for geom in __geoms])


from orbitx.tle import TLE
from orbitx.orbit import Orbit
from orbitx.matchups import Matchups


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
    init_orekit(data_path=orekit_data_path)
