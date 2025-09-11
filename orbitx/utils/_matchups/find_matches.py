"""A python function that finds the matchups in orbits"""

"""___Third-Party Modules___"""
import numpy as np
from typing import Dict, Any
from numbers import Number

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx import Orbit
from orbitx.utils._matchups.get_dist import get_distance

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
    sat1 = orbit.satellites[0]
    other_sats = orbit.satellites[1:]

    # Prepare the output: a dictionary with an entry per "other satellite". The entry is named <name of ref sat>_<name of other sat>
    # each entry contains a dictionary with the following entries:
    # lat1     the lattitude of the ref satellite at each match up
    # lon1     the longitude of the ref satellite at each match up
    # lat2     the lattitude of the other satellite at each match up
    # lon2     the longitude of the other satellite at each match up
    # delay    the time spent between the arrival of each satellite at the match up location
    # time     the date-time at which the matchup happens
    # distance the distance between the satellites at the matchup time
    # for now each sub-entry has the length
    match = dict(
        [
            (
                f"{sat1}_{s}",
                {
                    "lat1": orbit.orbits["lat1"].values,
                    "lon1": orbit.orbits["lon1"].values,
                    "lat2": np.empty((len(orbit),), dtype=float),
                    "lon2": np.empty((len(orbit),), dtype=float),
                    "distance": np.empty((len(orbit),), dtype=float),
                    "time": orbit.orbits["time"].values,
                    "time_datetime": orbit.orbits["time_datetime"].values,
                    "time2": np.empty((len(orbit),), dtype=float),
                    "time_datetime2": np.empty((len(orbit),), dtype="datetime64[s]"),
                    "delay": np.repeat(2 * time_diff_threshold, (len(orbit),)),
                },
            )
            for s in other_sats
        ]
    )

    # extract coordinates of the reference satellite
    s1_lat = orbit.orbits["lat1"].values
    s1_lon = orbit.orbits["lon1"].values
    s1_date = orbit.orbits["time_datetime"].values

    # Vector indicating which entries havea matchup:
    has_matchup = np.array([False for _ in range(len(orbit))])

    # Calculate number of interpolation sampling bins fit into the time difference threshold and generate vector of numbers of bins
    acceptable_bin_shifts = range(
        -abs(int(time_diff_threshold / orbit.interpolation_sampling_interval)),
        +abs(int(time_diff_threshold / orbit.interpolation_sampling_interval)),
    )

    for index_sat, s in enumerate(other_sats):
        # roll through the accepted time window through the lons and lats
        for i in acceptable_bin_shifts:
            indices_s1 = np.arange(s1_lat.shape[0])
            # extract the coordinate of the other satellite with an appropriate lag
            s2_lat = np.roll(orbit.orbits[f"lat{index_sat + 2}"].values, i)
            s2_lon = np.roll(orbit.orbits[f"lon{index_sat + 2}"].values, i)
            s2_time = np.roll(orbit.orbits["time"].values, i)
            s2_date = np.roll(orbit.orbits["time_datetime"].values, i)

            indices_s2 = np.roll(np.arange(s2_lat.shape[0]), i)
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
                indices_s1 = indices_s1[:i]
                indices_s2 = indices_s2[:i]
            elif i > 0:
                position = position[i:, :]
                s2_date = s2_date[i:]
                s2_time = s2_time[i:]
                indices_s1 = indices_s1[i:]
                indices_s2 = indices_s2[i:]
            distance = get_distance(*tuple(position.transpose()))

            # check distance is within the c2c_dist (centre to centre)
            for index_dist, dist in enumerate(distance):
                # The index in the orbit array corresponding to the distance being considered
                current_index_s1 = indices_s1[index_dist]
                if (
                    (dist <= space_diff_threshold)
                    and (
                        (s1_date[current_index_s1] < end_date)
                        or (s2_date[index_dist] < end_date)
                    )
                    and (
                        (s1_date[current_index_s1] > start_date)
                        or (s2_date[index_dist] > start_date)
                    )
                ):
                    # If there is no matchup for this entry yet or if this new matchup has a smaller delay, update the entry
                    if (not has_matchup[current_index_s1]) or (
                        np.abs(match[f"{sat1}_{s}"]["delay"][current_index_s1])
                        > np.abs(i * orbit.interpolation_sampling_interval)
                    ):
                        # match[f"{sat1}_{s}"]["lat1"][current_index_s1] = position[index_dist, 0]
                        # match[f"{sat1}_{s}"]["lon1"][current_index_s1] = position[index_dist, 1]
                        match[f"{sat1}_{s}"]["lat2"][current_index_s1] = position[
                            index_dist, 2
                        ]
                        match[f"{sat1}_{s}"]["lon2"][current_index_s1] = position[
                            index_dist, 3
                        ]
                        match[f"{sat1}_{s}"]["distance"][current_index_s1] = dist
                        # match[f"{sat1}_{s}"]["time"][current_index_s1] = s1_time[current_index_s1]
                        # match[f"{sat1}_{s}"]["time_datetime"][current_index_s1] = s1_date[current_index_s1]
                        match[f"{sat1}_{s}"]["time2"][current_index_s1] = s2_time[
                            index_dist
                        ]
                        match[f"{sat1}_{s}"]["time_datetime2"][current_index_s1] = (
                            s2_date[index_dist]
                        )
                        match[f"{sat1}_{s}"]["delay"][current_index_s1] = (
                            i * orbit.interpolation_sampling_interval
                        )
                        has_matchup[current_index_s1] = True
        # remove all entries which do not have a matchup
        for key in match[f"{sat1}_{s}"].keys():
            match[f"{sat1}_{s}"][key] = match[f"{sat1}_{s}"][key][np.where(has_matchup)]
    return match
