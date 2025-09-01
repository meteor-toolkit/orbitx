"""A python function that adds the land/ocean/coast mask to a matchup xarray"""

"""___Third-Party Modules___"""
import numpy as np
import datetime
from typing import Dict, Any
from numbers import Number
import numpy.typing as npt
"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._constants import LAND_GEOM
from orbitx.utils._matchup.landmask import landmask

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"

def get_land_ocean_mask(matchups: Dict[str, Dict[str, npt.NDArray]])->Dict[str, Dict[str, npt.NDArray]]:
    for sat_pair in matchups.keys():
        matchup_pair = matchups[sat_pair]

        land_mask_1 = np.empty((matchup_pair["lat1"].shape[0],), dtype = str)
        land_mask_2 = np.empty((matchup_pair["lat1"].shape[0],), dtype = str)
        matchup_type = np.empty((matchup_pair["lat1"].shape[0],), dtype = str)

        for i in range(land_mask_1.shape[0]):
            land_mask_1[i] = landmask(matchup_pair["lon1"][i], matchup_pair["lat1"][i])
            land_mask_2[i] = landmask(matchup_pair["lon2"][i], matchup_pair["lat2"][i])
            if land_mask_1[i] == land_mask_2[i]:
                matchup_type[i] = land_mask_1[i]
            else:
                matchup_type[i] = "COAST"

        matchup_pair["land_mask_1"] = land_mask_1
        matchup_pair["land_mask_2"] = land_mask_2
        matchup_pair["matchup_type"] = matchup_type
    return matchup_pair
