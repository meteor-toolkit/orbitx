"""orbitx - Propagate satellite orbits to identify matchups."""

__author__ = "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>"
__all__ = []

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

from orbitx.OrbitX import return_matchups