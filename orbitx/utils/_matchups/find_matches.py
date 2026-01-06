"""A python function that finds the matchups in orbits"""

"""___Third-Party Modules___"""
from datetime import timedelta
import numpy as np
import numpy.typing as npt
import xarray as xr
from typing import SupportsFloat
from math import pi

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx import Orbit
from orbitx.utils._matchups.get_dist import get_dist
from orbitx.utils._matchups.get_delay import get_delay
from orbitx.utils._date_utils import datetime64_to_sec_since
from orbitx import __version__

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"


def find_matches(
    orbit: Orbit,
    time_diff_threshold: np.timedelta64,
    space_diff_threshold: SupportsFloat,
    check_before: bool,
    check_after: bool,
    has_land_ocean_mask: bool,
) -> xr.Dataset:
    """Finds matchups between each pair of satellites

    Provided with the simulated orbit of each satellite (as an Orbit object), will return an xarray Dataset of matchups between the different orbits.
    The structure of the returned xarray is as follows:

    .. code-block:: bash

        matchups_dict = {"S2A_LS8":
                                {
                                    "lat1": npt.NDArray,
                                    "lon1": npt.NDArray,
                                    "lat2": npt.NDArray,
                                    "lon2": npt.NDArray,
                                    "delay": npt.NDArray,
                                    "time": npt.NDArray,
                                    "time_datetime": npt.NDArray,
                                    "distance": npt.NDArray,
                                },
                            }

    Args:
        orbit (Orbit): _description_
        time_diff_threshold (np.timedelta64): _description_
        space_diff_threshold (Number): _description_
        check_before (bool): _description_
        check_after (bool): _description_
        has_land_ocean_mask (bool): _description_

    Returns:
        xr.Dataset: _description_
    """
    # choose one satellite to remain stable and loop through the rest with respect to it
    satellite_shortnames = orbit.satellite_shortname
    num_sats = len(satellite_shortnames)
    orbit_length = len(orbit)
    satellite_pairs = np.array([], dtype = str)
    for i in range(num_sats - 1):
        satellite_pairs = np.append(satellite_pairs, [
                f"{satellite_shortnames[i]}_{satellite_shortnames[j]}"
                for j in range(i + 1, num_sats)
            ])
    num_pairs = satellite_pairs.shape[0]

    time_diff_threshold_timedelta: timedelta = time_diff_threshold.item()
    time_diff_threshold_float: float = time_diff_threshold_timedelta.total_seconds()


    matchups_xr: xr.Dataset = xr.Dataset(
        data_vars={
            "reference_date": (orbit.reference_date),
            "time_datetime": (
                ["matchup_index", "satellite"],
                np.repeat(
                    orbit.orbits["time_datetime"].values[:, np.newaxis],
                    num_sats,
                    axis=1,
                ),
            ),
            "time": (
                ["matchup_index", "satellite"],
                np.repeat(orbit.orbits["time"].values[:, np.newaxis], num_sats, axis=1),
            ),
            "lat": (["matchup_index", "satellite"], orbit.orbits["lat"].values * pi / 180),
            "lon": (["matchup_index", "satellite"], orbit.orbits["lon"].values * pi / 180),
            "distance": (
                ["matchup_index", "satellite_pair"],
                np.empty((len(orbit), num_pairs), dtype=float),
            ),
            "delay": (
                ["matchup_index", "satellite_pair"],
                np.full((len(orbit), num_pairs), 2 * time_diff_threshold, dtype = "timedelta64[s]"),
            ),
        },
        coords={
            "matchup_index": np.arange(orbit.orbits["time"].shape[0]),
            "satellite": satellite_shortnames,
            "satellite_pair": satellite_pairs,
        },
        attrs={
            "satellite_shortname": orbit.satellite_shortname,
            "satellite_name": orbit.satellite_name,
            "start_date": datetime64_to_sec_since(orbit.start_date, reference_date=orbit.reference_date),
            "end_date": datetime64_to_sec_since(orbit.end_date, reference_date=orbit.reference_date),
            "propagation_sampling_interval": orbit._orbits.attrs["propagation_sampling_interval"],
            "interpolation_sampling_interval": orbit._orbits.attrs["interpolation_sampling_interval"],
            "time_diff_threshold": time_diff_threshold_float,
            "space_diff_threshold": space_diff_threshold,
            "check_before": int(check_before),
            "check_after": int(check_after),
            "has_land_ocean_mask": int(has_land_ocean_mask),
            "version": __version__,
            "creation_date": str(np.datetime64("now")),
        },
    )
    
    # Calculate number of interpolation sampling bins fit into the time difference threshold and generate vector of numbers of bins
    acceptable_bin_shifts_unsorted: range = range(
        -abs(int(time_diff_threshold / orbit.interpolation_sampling_interval)),
        1+abs(int(time_diff_threshold / orbit.interpolation_sampling_interval)),
    )

    acceptable_bin_shifts: npt.NDArray[np.int64] = np.array(sorted(acceptable_bin_shifts_unsorted, key = lambda shift: np.abs(shift)))

    # Vector indicating which entries have a matchup:
    has_matchup = np.array([True for _ in range(matchups_xr["matchup_index"].shape[0])])

    for new_sat_ind in range(1, len(satellite_shortnames)):
        new_sat = satellite_shortnames[new_sat_ind]
        # Among the remaining rows, rows which have a matchup found with the current other satellite
        found_matchup_other_sat = np.array([False for _ in range(matchups_xr["matchup_index"].shape[0])])

        # roll through the accepted time window through the lons and lats
        for bin_shift in acceptable_bin_shifts:
            # Remove entries where some mission considered before the current one did not have a matchup
            # remove entries where we have already found a matchup for the current mission
            # remove entries where the roll creates matches between dates which are too different
            # e.g., if i = 1, the last position of the other sat becomes first,
            # and will be compared with the first position of the ref satellite
            # the first entry must hence be removed (and so on for other values of i)
            if bin_shift <= 0:
                relevant_indeces = matchups_xr["matchup_index"][
                    np.where(
                        has_matchup &
                        np.logical_not(found_matchup_other_sat) &
                        (matchups_xr["matchup_index"].values < (orbit_length + bin_shift))
                    )
                ].values
            else:
                relevant_indeces = matchups_xr["matchup_index"][
                    np.where(
                        has_matchup &
                        np.logical_not(found_matchup_other_sat) &
                        (matchups_xr["matchup_index"].values >= bin_shift)
                    )
                ].values
            # extract the coordinate of the other satellite with an appropriate lag
            new_sat_orbit_roll = matchups_xr.sel(satellite = new_sat).roll(matchup_index = bin_shift).sel(matchup_index = relevant_indeces)
            matchups_so_far_roll = matchups_xr.isel({"satellite": range(new_sat_ind)}).sel(matchup_index = relevant_indeces)
            distance = get_dist(matchups_so_far_roll, new_sat_orbit_roll)
            delay = get_delay(matchups_so_far_roll, new_sat_orbit_roll)
            distance_max = np.max(distance, axis = 1)
            delay_max = np.max(delay, axis = 1)
            new_matchups = xr.ufuncs.logical_and(distance_max <= space_diff_threshold, delay_max <= time_diff_threshold)
            new_matchup_indeces = relevant_indeces[new_matchups]
            if len(new_matchup_indeces) > 0:
                matchups_xr["lat"].loc[dict(satellite = new_sat, matchup_index = new_matchup_indeces)] = new_sat_orbit_roll["lat"].loc[dict(matchup_index = new_matchup_indeces)].values
                matchups_xr["lon"].loc[dict(satellite = new_sat, matchup_index = new_matchup_indeces)] = new_sat_orbit_roll["lon"].loc[dict(matchup_index = new_matchup_indeces)].values
                matchups_xr["time"].loc[dict(satellite = new_sat, matchup_index = new_matchup_indeces)] = new_sat_orbit_roll["time"].loc[dict(matchup_index = new_matchup_indeces)].values
                matchups_xr["time_datetime"].loc[dict(satellite = new_sat, matchup_index = new_matchup_indeces)] = new_sat_orbit_roll["time_datetime"].loc[dict(matchup_index = new_matchup_indeces)].values
                
                for previous_sat_ind in range(new_sat_ind):
                    previous_sat = satellite_shortnames[previous_sat_ind]
                    satellite_pair = f"{previous_sat}_{new_sat}"
                    matchups_xr["distance"].loc[dict(satellite_pair = satellite_pair, matchup_index = new_matchup_indeces)] = distance.loc[dict(matchup_index = new_matchup_indeces, satellite = previous_sat)]
                    matchups_xr["delay"].loc[dict(satellite_pair = satellite_pair, matchup_index = new_matchup_indeces)] = delay.loc[dict(matchup_index = new_matchup_indeces, satellite = previous_sat)]
                found_matchup_other_sat[new_matchup_indeces] = True

        has_matchup[np.logical_not(found_matchup_other_sat)] = False
        # remove all entries which do not have a matchup
    matchup_indeces = matchups_xr["matchup_index"][np.where(has_matchup)]
    matchups_xr = matchups_xr.loc[dict(matchup_index=matchup_indeces)]
    matchups_xr = matchups_xr.assign_coords(
        {"matchup_index": np.arange(matchups_xr["matchup_index"].values.shape[0])}
    )
    
    matchups_xr["lat"] = matchups_xr["lat"] / pi * 180
    matchups_xr["lon"] = matchups_xr["lon"] / pi * 180
    matchups_xr["time"].attrs["units"] = f"seconds since {orbit.reference_date}"
    matchups_xr["distance"].attrs["units"] = "km"
    matchups_xr["lat"].attrs["units"] = "degrees"
    matchups_xr["lon"].attrs["units"] = "degrees"
    return matchups_xr
