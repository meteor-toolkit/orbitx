"""orbitx.matchup - class to find matchups between satellite orbits"""

import os
import datetime
import numpy as np

from math import pi
from typing import Tuple, List, Union

__author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
]

__all__ = ["MatchUp"]


# TODO - move into class
def cal_dist_d2m(lat1, lon1, lat2, lon2):
    """
    Get lat and lon pairs in degree and return distance in meter
    :param lat1:
    :param lon1:
    :param lat2:
    :param lon2:
    :return:
    """
    lon1 = lon1 * pi / 180.0
    lat1 = lat1 * pi / 180.0
    lon2 = lon2 * pi / 180.0
    lat2 = lat2 * pi / 180.0

    R = 6373.0  # radius of the Earth [kms] meaning that the result will also be in kms
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c  # Haversine formula
    return distance


class MatchUp:
    """
    Class to find satellite overlap occurrences from satellite orbits

    inputs:
        orbital information (lat, lon, secs since)

    attributes:

    methods:
        roi_indices
        sat_to_sat_matchups
        search
        save_matchups
    """

    @staticmethod
    def roi_indices(orbits: dict, latmin, latmax, lonmin, lonmax, interpolation_sampling_interval):
        """
        Find indices of orbits corresponding to the points where a satellite overpasses the specified region of interest

        :param orbits:
        :param latmin:
        :param latmax:
        :param lonmin:
        :param lonmax:
        :param interpolation_sampling_interval:
        """
        sats_inROI_time = []
        sats_inROI_lat = []
        sats_inROI_lon = []
        sats_jump_start_idx = []
        sats_jump_stop_idx = []

        # iterate over for each satellite orbit provided in orbits
        for sat, orbit in orbits.items():
            sat_inROI_idx = (
                    (orbit["lat"] > latmin)
                    & (orbit["lat"] < latmax)
                    & (orbit["lon"] > lonmin)
                    & (orbit["lon"] < lonmax)
            )

            sat_inROI_time = orbit["time"][sat_inROI_idx]
            sat_inROI_lat = orbit["lat"][sat_inROI_idx]
            sat_inROI_lon = orbit["lon"][sat_inROI_idx]

            sat_time_dif = (
                    sat_inROI_time[1: len(sat_inROI_time)]
                    - sat_inROI_time[0: len(sat_inROI_time) - 1]
            )
            sat_jump_boolean = sat_time_dif != interpolation_sampling_interval
            sat_jump_stop_idx = [i for i, val in enumerate(sat_jump_boolean) if val]
            sat_jump_start_idx = [i + 1 for i in sat_jump_stop_idx]
            if sat_jump_stop_idx[0] < sat_jump_start_idx[0]:
                sat_jump_stop_idx.remove(sat_jump_stop_idx[0])
                sat_jump_start_idx = sat_jump_start_idx[0: len(sat_jump_stop_idx)]

            # add satellite specific variables to list
            sats_inROI_time.append(sat_inROI_time)
            sats_inROI_lat.append(sat_inROI_lat)
            sats_inROI_lon.append(sat_inROI_lon)
            sats_jump_start_idx.append(sat_jump_start_idx)
            sats_jump_stop_idx.append(sat_jump_stop_idx)

        return sats_inROI_time, sats_inROI_lat, sats_inROI_lon, sats_jump_start_idx, sats_jump_stop_idx

    @staticmethod
    def sat_to_sat_matchup(sat1_jump_start_idx, sat1_jump_stop_idx, sat1_inROI_time, sat2_jump_start_idx,
                           sat2_jump_stop_idx, sat2_inROI_time, time_diff_threshold):
        """
        Return matchup index information for two satellites

        :param sat1_jump_start_idx:
        :param sat1_jump_stop_idx:
        :param sat1_inROI_time:
        :param sat2_jump_start_idx:
        :param sat2_jump_stop_idx:
        :param sat2_inROI_time:
        :param time_diff_threshold:
        :return:
        """
        match_event_idx = []
        if len(sat1_jump_start_idx) <= len(sat2_jump_start_idx):
            for i in range(len(sat1_jump_start_idx)):
                # timevec1 = []
                timevec1 = sat1_inROI_time[sat1_jump_start_idx[i]: sat1_jump_stop_idx[i]]

                for j in range(len(sat2_jump_start_idx)):
                    # timevec2 = []
                    timevec2 = sat2_inROI_time[
                               sat2_jump_start_idx[j]: sat2_jump_stop_idx[j]
                               ]

                    if np.abs(np.mean(timevec2) - np.mean(timevec1)) <= time_diff_threshold:
                        match_event_idx.append(
                            [i, j, np.abs(np.mean(timevec2) - np.mean(timevec1))]
                        )
        return match_event_idx

    def search(self, orbits: dict, latmin, latmax, lonmin, lonmax, interpolation_sampling_interval,
               time_diff_threshold):
        """
        Return matchups between different orbits
        """
        # get satellite indices corresponding to when they overpass the region of interest
        sat_inROI_time, sat_inROI_lat, sat_inROI_lon, sat_jump_start_index, sat_jump_stop_index = self.roi_indices(
            orbits, latmin, latmax, lonmin,
            lonmax,
            interpolation_sampling_interval)

        if len(sat_inROI_time) == 2:
            match_event_idx = self.sat_to_sat_matchup(sat_jump_start_index[0], sat_jump_stop_index[0],
                                                      sat_inROI_time[0],
                                                      sat_jump_start_index[1], sat_jump_stop_index[1],
                                                      sat_inROI_time[1],
                                                      time_diff_threshold)

            # separate variables in match_event_idx into lists
            sat_match_event_idx = [[i[0] for i in match_event_idx], [i[1] for i in match_event_idx]]
            sat_to_sat_tmpdist = [i[2] for i in match_event_idx]

        elif len(sat_inROI_time) > 2 and not isinstance(sat_inROI_time[0], (float, int)):
            # figure out how to run for multiple orbits
            sat_match_event_idx = []
            sat_to_sat_tmpdist = []  # could be the greatest temporal distance between any pair of satellites
            pass
        else:
            # only one orbit selected, not enough for a matchup/comparison
            raise ValueError("""
            Only one satellite orbit input, two or more are required for a satellite-to-satellite matchup.""")

        sat_number = len(orbits.keys())
        # change time format before saving
        sat_inROI_datetime = [[datetime.datetime(2000, 1, 1) + datetime.timedelta(seconds=i) for i in j] for j in
                              sat_inROI_time]
        sat_starttime = [[sat_inROI_datetime[i][sat_jump_start_index[i][k]] for k in sat_match_event_idx[i]] for i in
                         range(sat_number)]
        sat_stoptime = [[sat_inROI_datetime[i][sat_jump_stop_index[i][k]] for k in sat_match_event_idx[i]] for i in
                        range(sat_number)]

        # get latitude and longitude values using indices
        sat_startlat = [[
            sat_inROI_lat[i][sat_jump_start_index[i][j]] for j in sat_match_event_idx[i]
        ] for i, k in enumerate(orbits.keys())]
        sat_stoplat = [[
            sat_inROI_lat[i][sat_jump_stop_index[i][j]] for j in sat_match_event_idx[i]
        ] for i, k in enumerate(orbits.keys())]
        sat_startlon = [[
            sat_inROI_lon[i][sat_jump_start_index[i][j]] for j in sat_match_event_idx[i]
        ] for i, k in enumerate(orbits.keys())]
        sat_stoplon = [[
            sat_inROI_lon[i][sat_jump_stop_index[i][j]] for j in sat_match_event_idx[i]
        ] for i, k in enumerate(orbits.keys())]

        # place matchup variables in a nested list
        matchup_info = []
        for i, k in enumerate(orbits.keys()):
            matchup_info.append([
                [k] * len(sat_match_event_idx[0]),
                sat_starttime[i],
                sat_stoptime[i],
                sat_startlat[i],
                sat_stoplat[i],
                sat_startlon[i],
                sat_stoplon[i],
            ])
        matchup_info = [i for j in matchup_info for i in j]
        matchup_info.append(sat_to_sat_tmpdist)

        return matchup_info

    @staticmethod
    def save(matchup_info, path, fname):
        """
        Save matchup information
        """
        sat_no = len(fname.split("_starttime")[0].split("_")) - 1
        first_line = ", ".join([j for sublist in [
            [f"sat{i + 1}"] + ["starttime", "stoptime", "startlat", "stoplat", "startlon", "stoplon"] for i in
            range(sat_no)]
                                for j in sublist]) + ", temporal_distance\n"
        with open(os.path.join(path, fname), "w") as file:
            file.write(
                first_line
            )
            for x in zip(*matchup_info):
                file.write(
                    "},{".join([str(i) for i in range(len(first_line.split(",")))]).join(["{", "}\n"]).format(
                        *x
                    )
                )

