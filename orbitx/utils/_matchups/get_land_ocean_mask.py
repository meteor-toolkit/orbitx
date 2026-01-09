"""A python function that adds the land/ocean/coast mask to a matchup xarray"""

"""___Third-Party Modules___"""
import numpy as np
from typing import Dict
import numpy.typing as npt
import xarray as xr

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._matchups.land_mask import land_mask

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"


def get_land_ocean_mask(matchups: xr.Dataset) -> xr.Dataset:
    """Adds a matchup_type variable to a matchups dataset corresponding to the land / ocean / coast mask for each matchup

    Args:
        matchups (xr.Dataset): a matchup Dataset

    Returns:
        xr.Dataset: The matchup dataset augmented with a land / ocean / coast mask variable
    """
    num_matchups = matchups["matchup_index"].shape[0]
    num_sat = matchups["satellite"].shape[0]
    matchup_type = np.empty((num_matchups,), dtype=str)
    land_mask_sat = np.empty((num_matchups,), dtype=str)

    matchups = matchups.assign(
        variables={
            "land_mask": (
                ["matchup_index", "satellite"],
                np.empty((num_matchups, num_sat), dtype=str),
            ),
            "matchup_type": (["matchup_index"], np.empty((num_matchups), dtype=str)),
        }
    )
    for sat in matchups["satellite"]:
        lattitudes = matchups[f"lat"].sel(satellite=sat)
        longitudes = matchups[f"lon"].sel(satellite=sat)
        for i in range(num_matchups):

            land_mask_sat[i] = land_mask(
                lattitudes.values[i],
                longitudes.values[i],
            )
        matchups["land_mask"].loc[dict(satellite=sat)] = land_mask_sat
    for matchup_index in matchups["matchup_index"]:
        matchup_types = np.unique(
            matchups["land_mask"].sel(matchup_index=matchup_index).values
        )
        if len(matchup_types) > 1:
            matchups["matchup_type"].loc[dict(matchup_index=matchup_index)] = "COAST"
        else:
            matchups["matchup_type"].loc[dict(matchup_index=matchup_index)] = (
                matchup_types[0]
            )
    return matchups
