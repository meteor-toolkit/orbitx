"""A python function that finds the matchups in orbits"""

"""___Third-Party Modules___"""
import numpy as np
from typing import Dict, Any
from numbers import Number
import xarray as xr
from typing import List

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx import Orbit
from orbitx.utils._matchups.get_dist import get_distance
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
    space_diff_threshold: Number,
    start_date: np.datetime64,
    end_date: np.datetime64,
    check_before: bool,
    check_after: bool,
    has_land_ocean_mask: bool
) -> Dict[str, Dict[str, Any]]:
    """find_matches Finds matchups between each pair of satellites

    Provided with the simulated orbit of each satellite (as an Orbit object), will return a Dictionary where each entry has the name of the two satellites as key, and a dictionnary as value.
    The dictionnary associated with a pair of satellites has the following structure:

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

    :param orbit: _description_
    :type orbit: Orbit
    :param time_diff_threshold: _description_
    :type time_diff_threshold: Number
    :param space_diff_threshold: _description_
    :type space_diff_threshold: Number
    :param start_date: _description_
    :type start_date: datetime.datetime
    :param end_date: _description_
    :type end_date: datetime.datetime
    :return: _description_
    :rtype: Dict[str, Dict[str, Any]]
    """
    # choose one satellite to remain stable and loop through the rest with respect to it
    satellite_shortnames = orbit.satellite_shortname
    num_sats = len(satellite_shortnames)
    ref_sat = satellite_shortnames[0]
    other_sats = satellite_shortnames[1:]
    satellite_pairs = np.array([[f"{satellite_shortnames[i]}_{satellite_shortnames[j]}" for j in range(i + 1, num_sats)] for i in range(num_sats - 1)]).flatten()
    num_pairs = satellite_pairs.shape[0]
    matchups_xr: xr.Dataset = xr.Dataset(
        data_vars={
            "reference_date": (orbit.reference_date),
            "time_datetime": (["matchup_index", "satellite"], np.repeat(orbit.orbits["time_datetime"].values[:, np.newaxis], num_sats, axis = 1)),
            "time": (["matchup_index", "satellite"], np.repeat(orbit.orbits["time"].values[:, np.newaxis], num_sats, axis = 1)),
            "lat": (["matchup_index", "satellite"], orbit.orbits["lat"].values),
            "lon": (["matchup_index", "satellite"], orbit.orbits["lon"].values),
            "distance": (["matchup_index", "satellite_pair"], np.empty((len(orbit), num_pairs), dtype=float)),
            "delay": (["matchup_index", "satellite_pair"], np.full((len(orbit), num_pairs), 2 * time_diff_threshold)),
        },
        coords={
            "matchup_index": np.arange(orbit.orbits["time"].shape[0]),
            "satellite": satellite_shortnames,
            "satellite_pair": satellite_pairs
        },
        attrs={
            "satellite_shortname": orbit.satellite_shortname,
            "satellite_name": orbit.satellite_name,
            "start_date": orbit.start_date,
            "end_date": orbit.end_date,
            "propagation_sampling_interval": orbit.propagation_sampling_interval,
            "interpolation_sampling_interval": orbit.interpolation_sampling_interval,
            "time_diff_threshold": time_diff_threshold,
            "space_diff_threshold": space_diff_threshold,
            "check_before": check_before,
            "check_after": check_after,
            "has_land_ocean_mask": has_land_ocean_mask,
            "version": __version__,
            "creation_date": str(np.datetime64("now"))
        },
    )
    print(matchups_xr["time_datetime"].values)
    # Calculate number of interpolation sampling bins fit into the time difference threshold and generate vector of numbers of bins
    acceptable_bin_shifts = range(
        -abs(int(time_diff_threshold / orbit.interpolation_sampling_interval)),
        +abs(int(time_diff_threshold / orbit.interpolation_sampling_interval)),
    )
    
    # Vector indicating which entries have a matchup:
    has_matchup = np.array([True for _ in range(matchups_xr["matchup_index"].shape[0])])

    for other_sat in other_sats:
        satellite_pair = f"{ref_sat}_{other_sat}"
        # extract coordinates of the reference satellite
        
        matchup_indeces = matchups_xr["matchup_index"][np.where(has_matchup)]
        s1_lat = matchups_xr["lat"].sel(satellite = ref_sat, matchup_index = matchup_indeces).values
        s1_lon = matchups_xr["lon"].sel(satellite = ref_sat, matchup_index = matchup_indeces).values
        s1_date = matchups_xr["time_datetime"].sel(satellite = ref_sat).values

        found_matchup_other_sat = np.array([False for _ in range(s1_lat.shape[0])])

        # roll through the accepted time window through the lons and lats
        for i in acceptable_bin_shifts:
            # extract the coordinate of the other satellite with an appropriate lag
            s2_lat = np.roll(matchups_xr["lat"].sel(satellite = other_sat).values, i)
            s2_lat = s2_lat[matchup_indeces]
            s2_lon = np.roll(matchups_xr["lon"].sel(satellite = other_sat).values, i)
            s2_lon = s2_lat[matchup_indeces]
            s2_time = np.roll(matchups_xr["time"].sel(satellite = other_sat).values, i)
            s2_time = s2_lat[matchup_indeces]
            s2_date = np.roll(matchups_xr["time_datetime"].sel(satellite = other_sat).values, i)
            s2_date = s2_lat[matchup_indeces]

            # create an array of all positions
            position = np.array([s1_lat, s1_lon, s2_lat, s2_lon]).transpose()

            # remove entries where the roll creates matches between too different dates
            # e.g., if i = 1, the last position of the other sat becomes first,
            # and will be compared with the first position of the ref satellite
            # the first entry must hence be removed (and so on for other values of i)
            if i < 0:
                position = position[:i, :]
                s2_date = s2_date[:i]
                s2_time = s2_time[:i]
            elif i > 0:
                position = position[i:, :]
                s2_date = s2_date[i:]
                s2_time = s2_time[i:]
            distance = get_distance(*tuple(position.transpose()))

            # check distance is within the c2c_dist (centre to centre)
            for index_dist, dist in enumerate(distance):
                # The index in the orbit array corresponding to the distance being considered
                current_matchup_index = matchup_indeces[index_dist]
                print(s1_date[index_dist])
                print(s2_date[index_dist])
                print(end_date)
                if (
                    (dist <= space_diff_threshold)
                    and (
                        (s1_date[index_dist] < end_date)
                        or (s2_date[index_dist] < end_date)
                    )
                    and (
                        (s1_date[index_dist] > start_date)
                        or (s2_date[index_dist] > start_date)
                    )
                ):
                    # If there is no matchup for this entry yet or if this new matchup has a smaller delay, update the entry
                    if (not found_matchup_other_sat[index_dist]) or (
                        np.abs(
                            matchups_xr["delay"].sel(
                                matchup_index = current_matchup_index,
                                satellite_pair = satellite_pair
                            ).values
                        ))> np.abs(i * orbit.interpolation_sampling_interval):
                        matchups_xr["lat"].loc[dict(
                                matchup_index = current_matchup_index,
                                satellite = other_sat
                            )].data = position[index_dist, 2]
                        matchups_xr["lon"].loc[dict(
                                matchup_index = current_matchup_index,
                                satellite = other_sat
                            )].data = position[index_dist, 3]
                        matchups_xr["distance"].loc[dict(
                                matchup_index = current_matchup_index,
                                satellite_pair = satellite_pair
                            )].data = dist
                        matchups_xr["time"].loc[dict(
                                matchup_index = current_matchup_index,
                                satellite = other_sat
                            )].data = s2_time[
                            index_dist
                        ]
                        matchups_xr["time_datetime"].loc[dict(
                                matchup_index = current_matchup_index,
                                satellite = other_sat
                            )].data = (
                            s2_date[index_dist]
                        )
                        matchups_xr["delay"].loc[dict(
                                matchup_index = current_matchup_index,
                                satellite_pair = satellite_pair
                            )].data = (
                            i * orbit.interpolation_sampling_interval
                        )
                        found_matchup_other_sat[index_dist] = True
        has_matchup[np.logical_not(found_matchup_other_sat)] = False
        # remove all entries which do not have a matchup
    matchup_indeces = matchups_xr["matchup_index"][np.where(has_matchup)]
    matchups_xr = matchups_xr.loc[dict(matchup_index = matchup_indeces)]
    matchups_xr = matchups_xr.assign_coords({"matchup_index": np.arange(matchups_xr["matchup_index"].values.shape[0])})
    matchups_xr[f"time"].attrs["units"] = f"seconds since {orbit.reference_date}"
    matchups_xr[f"distance"].attrs["units"] = "km"
    matchups_xr[f"delay"].attrs["units"] = "s"
    matchups_xr[f"lat"].attrs["units"] = "degrees"
    matchups_xr[f"lon"].attrs["units"] = "degrees"
    return matchups_xr
