"""orbitx.interface - file containing all interface functions"""

import os
import datetime
import xarray as xr

from typing import List, Optional

from orbitx.orbit import Orbit
from orbitx.matchup import Matchups

__author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
]

__all__ = ["return_matchups"]


def return_matchups(
    sats: List[str],
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    propagation_sampling_interval: float,
    interpolation_sampling_interval: float,
    cntr2cntr_dist: float,
    time_diff_threshold: float,
    output_path_sim_orbits: Optional[str] = None,
    output_path_matchups: Optional[str] = None,
    output: bool = False,
) -> Optional[xr.Dataset]:
    """
    Matchup event identification between multiple satellites. Creates an xr.Dataset
    containing position and time information for satellite matchups.

    If no output paths are specified, the dataset will be returned.
    If output paths are specified the data will be saved.
    If `output` is set to `True` the dataset will be returned regardless of whether or not it has been saved.

    Currently accepted satellites:
        * LS8 (Landsat-8)
        * S2A (Sentinel-2A)
        * S2B (Sentinel-2B)
        * S3A (Sentinel-3A)
        * S6 (Sentinel-6)

    :param sats: list of satellites
    :param start_time: start of time period of interest
    :param end_time: end of time period of interest
    :param propagation_sampling_interval: sampling rate of orbit propagation per sensor
    :param interpolation_sampling_interval: subsampling rate of orbit propagation per sensor by interpolation
    :param cntr2cntr_dist: matchup threshold for distance between the nadir position of the two satellites
    :param time_diff_threshold: matchup threshold for time difference between the two satellites
    :param output_path_sim_orbits: path to write evaluated propagated orbits to
    :param output_path_matchups: path to write matchups to
    :param output: whether or not to output the matchup dataset, if no output_path defined defaults to True else False
    """
    # simulate desired orbits
    orbit = Orbit()
    orbit_output = orbit.run(
        sats,
        start_time,
        end_time,
        propagation_sampling_interval,
        interpolation_sampling_interval,
    )

    # find matchups between orbits
    matchup = Matchups()
    matchup_output = matchup.matchup(orbit_output, time_diff_threshold, cntr2cntr_dist)

    if output_path_sim_orbits is not None:
        # save orbital data
        # orbit.save(orbit_output, output_path_sim_orbits)
        pass

    if output_path_matchups is not None:
        # save matchup data
        fname = f"matchup_{'_'.join(list(orbit_output.keys()))}_starttime_{start_time.strftime('%Y%m%d')}_endtime_{end_time.strftime('%Y%m%d')}_samplinginterval_{propagation_sampling_interval}_tmptol_{time_diff_threshold}.nc"

        matchup_output.to_netcdf(os.path.join(output_path_matchups, fname))
    else:
        output = True

    if output is True:
        return matchup_output
    else:
        return None
