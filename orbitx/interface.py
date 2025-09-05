"""orbitx.interface - file containing all interface functions"""

import os
import datetime
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from typing import List, Optional

from orbitx.orbit import Orbit
from orbitx.matchups import Matchups, get_range

__author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
]

__all__ = ["return_matchups", "plot_matchups"]



def return_matchups(
    sats: List[str],
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    propagation_sampling_interval: float,
    interpolation_sampling_interval: float,
    cntr2cntr_dist: float,
    time_diff_threshold: float,
    check_before:Optional[bool]=False,
    check_after:Optional[bool]=False,
    get_land_ocean:Optional[bool]=False,
    output_path_sim_orbits: Optional[str] = None,
    output_path_matchups: Optional[str] = None,
    output: bool = False,
) -> Optional[xr.Dataset]:
    """Matchup event identification between multiple satellites. Creates an xr.Dataset
    containing position and time information for satellite matchups.

    If no output paths are specified, the dataset will be returned.
    If output paths are specified the data will be saved.
    If `output` is set to `True` the dataset will be returned regardless of whether or not it has been saved.

    Currently accepted satellites:
        * LS8 (Landsat-8)
        * LS9 (Landsat-9)
        * S2A (Sentinel-2A)
        * S2B (Sentinel-2B)
        * S3A (Sentinel-3A)
        * S3B (Sentinel-3B)
        * S6 (Sentinel-6)
        * J3 (Jason-3)
        * SA (Saral-Altika)

    :param sats: list of satellites
    :type sats: List[str]
    :param start_time: start of time period of interest
    :type start_time: datetime.datetime
    :param end_time: end of time period of interest
    :type end_time: datetime.datetime
    :param propagation_sampling_interval: sampling rate of orbit propagation per sensor
    :type propagation_sampling_interval: float
    :param interpolation_sampling_interval: subsampling rate of orbit propagation per sensor by interpolation
    :type interpolation_sampling_interval: float
    :param cntr2cntr_dist: matchup threshold for distance between the nadir position of the two satellites (kilometres)
    :type cntr2cntr_dist: float
    :param time_diff_threshold: matchup threshold for time difference between the two satellites (seconds)
    :type time_diff_threshold: float
    :param check_before: whether matchups where strictly one of the two satellites appears before the start date, defaults to False
    :type check_before: Optional[bool], optional
    :param check_after: whether matchups where strictly one of the two satellites appears after the end date, defaults to False
    :type check_after: Optional[bool], optional
    :param get_land_ocean: whether the output should contain a land - ocean - coast label, defaults to False
    :type get_land_ocean: Optional[bool], optional
    :param output_path_sim_orbits: path to write evaluated propagated orbits to, defaults to None
    :type output_path_sim_orbits: Optional[str], optional
    :param output_path_matchups: path to write matchups to (as a netcdf file), defaults to None
    :type output_path_matchups: Optional[str], optional
    :param output: whether or not to output the matchup dataset, if no output_path defined defaults to True else False, defaults to False
    :type output: bool, optional
    :return: _description_
    :rtype: Optional[xr.Dataset]
    """
    # simulate desired orbits
    orbit_start_time = start_time
    orbit_end_time = end_time
    if check_before:
        orbit_start_time = orbit_start_time - time_diff_threshold
    if check_after:
        orbit_end_time = orbit_end_time + time_diff_threshold
    orbit = Orbit(
        satellites=sats,
        start_time=orbit_start_time,
        end_time=orbit_end_time,
        propagation_sampling_interval=propagation_sampling_interval,
        interpolation_sampling_interval=interpolation_sampling_interval
    )

    if not output_path_sim_orbits is None:
        orbit.to_netcdf(output_path_sim_orbits)

    # find matchups between orbits
    matchup = Matchups(orbit, time_diff_threshold, cntr2cntr_dist, get_land_ocean)

    if output_path_matchups is not None:
        matchup.to_netcdf(output_path=output_path_matchups)
    if output is True:
        return matchup.to_ds()
    else:
        return None

