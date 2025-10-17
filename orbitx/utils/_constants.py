"""Global Constants for orbits"""

"""___Third-Party Modules___"""
from typing import Dict

"""___NPL Modules___"""

"""__Built-In Modules__"""

"""___Authorship___"""
__author__ = __author__ = ["Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>"]
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = ["Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>"]
__status__ = "Development"

SATELLITE_DICT:Dict[str, str] = {
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
    "N20": "NOAA-20",
}
"""Dictionary containing the short name (as keys) and full name (as values) of the satellites supported by this package.
To add more satellites, obtain the TLE's of the desired satellite (using `celestrak`_), and add them as a file with name `TLEset_<sat_short_name>.txt` (replacing `<sat_short_name>` accordingly) in the `data/tle` folder.
Then, add the `"short_name": "full-name"` pair to the dictionary above.

.. _celestrak: https://celestrak.org/
"""


# Radius of earth in kilometers
EARTH_RADIUS:float = 6371.
"""Earth radius in kilometers"""

# inches to cm conversion constant
CM:float = 1 / 2.54
"""Constant for conversion of inches into centimeters (used for plots)"""
