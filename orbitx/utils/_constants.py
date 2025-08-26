"""Global Constants for orbits"""

"""___Third-Party Modules___"""
import cartopy.io.shapereader as shpreader
import shapely.geometry as sgeom
import numpy as np

"""___NPL Modules___"""

"""__Built-In Modules__"""

"""___Authorship___"""
__author__ = __author__ = [
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>"
]
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = [
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>"
]
__status__ = "Development"

SATELLITE_DICT = {
    "LS8": "Landsat-8",
    "LS9": "Landsat-9",
    "S2A": "Sentinel-2A",
    "S2B": "Sentinel-2B",
    "S3A": "Sentinel-3A",
    "S3B": "Sentinel-3B",
    "S6": "Sentinel-6",
    "J2": "JASON-2",
    "J3": "JASON-3",
    "SA": "Saral-AltiKa",
    "CS2": "CryoSat-2",
    "LINCS2": "Lin-CryoSat-2",
    "N20": "NOAA-20"
}

__land_shp_fname = shpreader.natural_earth(resolution='50m',
                                         category='physical', name='land')

__geoms = list(shpreader.Reader(__land_shp_fname).geometries())
__multipol_loc = np.where([isinstance(geom, sgeom.MultiPolygon) for geom in __geoms])[0]
for loc in __multipol_loc:
    __multipols = list(__geoms[loc].geoms)
    [__geoms.append(multipol) for multipol in __multipols]
    __geoms.pop(loc)

LAND_GEOM = sgeom.MultiPolygon([sgeom.shape(geom)
                                for geom in __geoms])