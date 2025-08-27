"""A python function that finds the matchups in orbits"""

"""___Third-Party Modules___"""
import numpy as np
import datetime
from typing import Dict, Any
from numbers import Number
"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx import Orbit
from orbitx.utils._matchup.get_dist import get_distance

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"

def find_matches(
        orbit:Orbit,
        time_diff_threshold:Number,
        space_diff_threshold:Number,
        start_time:datetime.datetime,
        end_time:datetime.datetime
)->Dict[str, Dict[str, Any]]:
    """find_matches _summary_

    _extended_summary_

    :param orbit: _description_
    :type orbit: Orbit
    :param time_diff_threshold: _description_
    :type time_diff_threshold: Number
    :param space_diff_threshold: _description_
    :type space_diff_threshold: Number
    :param start_time: _description_
    :type start_time: datetime.datetime
    :param end_time: _description_
    :type end_time: datetime.datetime
    :return: _description_
    :rtype: Dict[str, Dict[str, Any]]
    """
    # choose one satellite to remain stable and loop through the rest with respect to it
    sat1 = list(orbit.satellites)[0]
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
                    "lat1": np.empty((len(orbit),), dtype = float),
                    "lon1": np.empty((len(orbit),), dtype = float),
                    "lat2": np.empty((len(orbit),), dtype = float),
                    "lon2": np.empty((len(orbit),), dtype = float),
                    "delay": np.empty((len(orbit),), dtype = float),
                    "time": np.empty((len(orbit),), dtype = datetime.datetime),
                    "distance": np.empty((len(orbit),), dtype = float),
                },
            )
            for s in other_sats
        ]
    )

    # extract coordinates of the referrence satellite
    s1_lat = orbit.orbits[sat1]["lat"]
    s1_lon = orbit.orbits[sat1]["lon"]
    s1_time = orbit.orbits[sat1]["time"]

    # Vector indicating which entries havea matchup:
    has_matchup = np.array([False for _ in range(len(orbit))])

    # Calculate number of interpolation sampling bins fit into the time difference threshold and generate vector of numbers of bins
    acceptable_bin_shifts = range(
            -abs(int(time_diff_threshold / orbit.interpolation_sampling_interval)),
            +abs(int(time_diff_threshold / orbit.interpolation_sampling_interval)),
        )
    
    for s in other_sats:
        # roll through the accepted time window through the lons and lats
        for i in acceptable_bin_shifts:
            # extract the coordinate of the other satellite with an appropriate lag
            s2_lat = np.roll(orbit.orbits[s]["lat"], i)
            s2_lon = np.roll(orbit.orbits[s]["lon"], i)

            # create an array of all positions
            position = np.array([s1_lat, s1_lon, s2_lat, s2_lon]).transpose()

            # remove entries where the roll creates matches between too different dates
            # e.g., if i = 1, the last position of the other sat becomes first,
            # and will be compared with the first position of the ref satellite
            # the first entry must hence be removed (and so on for other values of i)
            indeces_array = range(position.shape[0])
            if i < 0:
                position = position[:i, :]
                indeces_array = indeces_array[:i]
            elif i > 0:
                position = position[i:, :]
                indeces_array = indeces_array[i:]

            distance = get_distance(*tuple(position))

            # check distance is within the c2c_dist (centre to centre)
            for item, dist in enumerate(distance):
                # The index in the orbit array corresponding to the distance being considered
                current_index = indeces_array[item]
                if (
                    (dist <= space_diff_threshold)
                    and (s1_time[current_index] < end_time)):
                    # If there is no matchup for this entry yet or if this new matchup has a smaller delay, update the entry
                    if (
                        ((not has_matchup[current_index])
                        or (np.abs(match[f"{sat1}_{s}"]["delay"][current_index])
                        > np.abs(i * orbit.interpolation_sampling_interval)))
                    ):
                        match[f"{sat1}_{s}"]["lat1"][current_index] = position[0, item]
                        match[f"{sat1}_{s}"]["lon1"][current_index] = position[1, item]
                        match[f"{sat1}_{s}"]["lat2"][current_index] = position[2, item]
                        match[f"{sat1}_{s}"]["lon2"][current_index] = position[3, item]
                        match[f"{sat1}_{s}"]["delay"][current_index] = (
                            i * orbit.interpolation_sampling_interval
                        )
                        match[f"{sat1}_{s}"]["time"][current_index] = datetime.datetime(
                            1970, 1, 1
                        ) + datetime.timedelta(seconds=s1_time[current_index])
                        match[f"{sat1}_{s}"]["distance"][current_index] = dist
                        has_matchup[current_index] = True
        # remove all entries which do not have a matchup
        for key in match[f"{sat1}_{s}"].keys():
            match[f"{sat1}_{s}"][key] = match[f"{sat1}_{s}"][key][has_matchup]
    return match