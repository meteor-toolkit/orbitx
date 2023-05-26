"""orbitx - Propagate satellite orbits to identify matchups."""

__author__ = "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>"
__all__ = []

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

import os
this_directory = os.path.dirname(__file__)

import orekit
vm = orekit.initVM()
from orekit.pyhelpers import setup_orekit_curdir
setup_orekit_curdir(filename=os.path.join(this_directory, "data", "orekit-data.zip"))

from orbitx.OrbitX import return_matchups