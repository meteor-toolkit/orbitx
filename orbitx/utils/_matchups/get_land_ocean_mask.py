"""A python function that adds the land/ocean/coast mask to a matchup xarray"""

"""___Third-Party Modules___"""
import numpy as np
from typing import Dict
import numpy.typing as npt
import xarray as xr
"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._matchups.landmask import landmask

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"

def get_land_ocean_mask(
        matchups: xr.Dataset)->Dict[str, Dict[str, npt.NDArray]]:
    matchup_type = np.empty((matchups["lat1"].shape[0],), dtype = str)
    land_mask_sat = np.empty((matchups["lat1"].shape[0],), dtype = str)
    for sat_index, _ in enumerate(matchups.attrs["satellites"]):
        for i in range(land_mask_sat.shape[0]):
            land_mask_sat[i] = landmask(matchups[f"lat{sat_index+1}"].values[i], matchups[f"lon{sat_index+1}"].values[i])
        matchups = matchups.assign(
            variables = {
                f"land_mask{sat_index+1}": ("time", land_mask_sat)
            }
        )
    for matchup_index in range(matchups["lat1"].shape[0]):
        matchup_types = np.unique([matchups[f"land_mask{sat_index+1}"].values[matchup_index] for sat_index in range(len(matchups.attrs["satellites"]))])
        if len(matchup_types) > 1:
            for sat_pair in matchups.keys():
                matchup_type[matchup_index] = "COAST"
        else:
            matchup_type[matchup_index] = matchup_types[0]
    matchups = matchups.assign(
            variables = {
                f"matchup_type": ("time", matchup_type)
            }
        )
    return matchups
