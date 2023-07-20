"""orbitx.interface - file containing all interface functions"""

import datetime
import math

import numpy as np

from scipy.signal import find_peaks
from typing import List

from orbitx.orbit import Orbit
from orbitx.matchup import MatchUp
from orbitx.matchup_test import matchup

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
    latmin: float,
    latmax: float,
    lonmin: float,
    lonmax: float,
    output_path_sim_orbits: str,
    output_path_matchups: str,
) -> None:
    """
    Save

    :param sats: list of satellites
    :param start_time: start of time period of interest
    :param end_time: end of time period of interest
    :param propagation_sampling_interval: sampling rate of orbit propagation per sensor
    :param interpolation_sampling_interval: subsampling rate of orbit propagation per sensor by interpolation
    :param cntr2cntr_dist: matchup threshold for distance between the nadir position of the two satellites
    :param time_diff_threshold: matchup threshold for time difference between the two satellites
    :param latmin: minimum latitude for region of interest
    :param latmax: maximum latitude for region of interest
    :param lonmin: minimum longitude for region of interest
    :param lonmax: maximum longitude for region of interest
    :param output_path_sim_orbits: path to write evaluated propagated orbits to
    :param output_path_matchups: path to write matchups to
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

    match = matchup(orbit_output, time_diff_threshold,
                    interpolation_sampling_interval,
                    cntr2cntr_dist)

    # save orbital data
    # orbit.save(orbit_output, output_path_sim_orbits)
    import matplotlib.pyplot as plt
    lon1 = [j for i, j in enumerate(match["S3A_LS8"]["lon1"]) if -60 <= match["S3A_LS8"]["lat1"][i] <= 60]
    lat1 = [j for i, j in enumerate(match["S3A_LS8"]["lat1"]) if -60 <= match["S3A_LS8"]["lat1"][i] <= 60]

    lon2 = [j for i, j in enumerate(match["S3A_LS8"]["lon2"]) if -60 <= match["S3A_LS8"]["lat1"][i] <= 60]
    lat2 = [j for i, j in enumerate(match["S3A_LS8"]["lat2"]) if -60 <= match["S3A_LS8"]["lat1"][i] <= 60]

    plt.scatter(lon1, lat1)
    plt.scatter(lon2, lat2)
    plt.show()

    # find matchups between orbits
    matchups = MatchUp()
    matchup_output = matchups.search(
        orbit_output,
        latmin,
        latmax,
        lonmin,
        lonmax,
        interpolation_sampling_interval,
        time_diff_threshold,
    )

    # save matchup data
    fname = f"matchup_{'_'.join(list(orbit_output.keys()))}_starttime_{start_time.strftime('%Y%m%d')}_endtime_{end_time.strftime('%Y%m%d')}_samplinginterval_{propagation_sampling_interval}_tmptol_{time_diff_threshold}.txt"

    matchups.save(matchup_output, output_path_matchups, fname)
