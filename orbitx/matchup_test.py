"""

"""

import numpy as np
import math
import datetime

from scipy.signal import find_peaks

__author__ = [
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
]

__all__ = ["matchup"]


def matchup(
    orbit_output: dict,
    time_diff_threshold: float,
    interpolation_sampling_interval: float,
    cntr2cntr_dist: float,
):
    """
    Return information relating to matchup instances between satellites

    :param orbit_output:
    :param time_diff_threshold:
    :param interpolation_sampling_interval:
    :param cntr2cntr_dist:
    """
    # function to get distance between two lon lat points
    x = (
        lambda lon1, lat1, lon2, lat2: 6373
        * 2
        * np.arctan2(
            np.sqrt(
                np.sin((lat2 - lat1) / 2) ** 2
                + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
            ),
            np.sqrt(
                1
                - np.sqrt(
                    np.sin((lat2 - lat1) / 2) ** 2
                    + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
                )
            ),
        )
    )

    # orbit_output is a dictionary containing the satellites and their lon, lat and time arrays
    # next step is to get rid of the common nan values from lists
    start_value = None
    stop_value = None
    for sat in orbit_output.values():
        start_value = (
            list(np.isnan(sat["lat"])).index(False)
            if start_value is None
            or start_value < list(np.isnan(sat["lat"])).index(False)
            else start_value
        )
        stop_value = (
            list(np.isnan(sat["lat"]))[::-1].index(False)
            if stop_value is None
            or stop_value < list(np.isnan(sat["lat"]))[::-1].index(False)
            else stop_value
        )

    for sat in orbit_output.keys():
        if stop_value == 0:
            orbit_output[sat]["lat"] = orbit_output[sat]["lat"][start_value:]
            orbit_output[sat]["lon"] = orbit_output[sat]["lon"][start_value:]
            orbit_output[sat]["time"] = orbit_output[sat]["time"][start_value:]
        else:
            orbit_output[sat]["lat"] = orbit_output[sat]["lat"][start_value:-stop_value]
            orbit_output[sat]["lon"] = orbit_output[sat]["lon"][start_value:-stop_value]
            orbit_output[sat]["time"] = orbit_output[sat]["time"][start_value:-stop_value]

    # choose one satellite to remain stable and loop through the rest with respect to it
    sat1 = list(orbit_output.keys())[0]
    other_sats = [i for i in orbit_output.keys() if i != sat1]

    match = dict(
        [
            (
                f"{sat1}_{s}",
                {
                    "lat1": -1 * np.ones(len(orbit_output[sat1]["lat"])),
                    "lon1": -1 * np.ones(len(orbit_output[sat1]["lat"])),
                    "lat2": -1 * np.ones(len(orbit_output[sat1]["lat"])),
                    "lon2": -1 * np.ones(len(orbit_output[sat1]["lat"])),
                    "delay": -1 * np.ones(len(orbit_output[sat1]["lat"])),
                    "time": np.array(
                        [datetime.datetime(1, 1, 1)] * len(orbit_output[sat1]["lat"])
                    ),
                    "distance": -1 * np.ones(len(orbit_output[sat1]["lat"])),
                },
            )
            for s in other_sats
        ]
    )

    for s in other_sats:
        # roll through the accepted time window through the lons and lats
        for i in range(
            -abs(int(time_diff_threshold / interpolation_sampling_interval)),
            +abs(int(time_diff_threshold / interpolation_sampling_interval)),
        ):
            s1_lat = orbit_output[sat1]["lat"]
            s1_lon = orbit_output[sat1]["lon"]
            s1_time = orbit_output[sat1]["time"]
            s2_lat = np.roll(orbit_output[s]["lat"], i)
            s2_lon = np.roll(orbit_output[s]["lon"], i)
            difflat = np.abs(s1_lat - s2_lat)
            difflon = np.abs(s1_lon - s2_lon)
            match_peak, _ = find_peaks(
                -(difflat + difflon)
            )  # local minima peaks of latlon difference (max of negative val)
            # check distance is within the c2c_dist (centre to centre)
            match_peak = [j for j in match_peak if x(*tuple(
                np.array([s1_lon[j], s1_lat[j], s2_lon[j], s2_lat[j]]) * math.pi / 180)) <= cntr2cntr_dist]
            # gets values for matching peaks and saves if not repeated at each delay step
            for item in match_peak:
                if (
                    match[f"{sat1}_{s}"]["delay"][item] == -1
                    or match[f"{sat1}_{s}"]["delay"][item]
                    > i * interpolation_sampling_interval
                ):
                    match[f"{sat1}_{s}"]["lat1"][item] = s1_lat[item]
                    match[f"{sat1}_{s}"]["lon1"][item] = s1_lon[item]
                    match[f"{sat1}_{s}"]["lat2"][item] = s2_lat[item]
                    match[f"{sat1}_{s}"]["lon2"][item] = s2_lon[item]
                    match[f"{sat1}_{s}"]["delay"][item] = (
                        i * interpolation_sampling_interval
                    )
                    match[f"{sat1}_{s}"]["time"][item] = datetime.datetime(
                        2000, 1, 1
                    ) + datetime.timedelta(seconds=s1_time[item])
                    match[f"{sat1}_{s}"]["distance"][item] = x(
                        *tuple(
                            [
                                (k * math.pi / 180)
                                for k in (
                                    s1_lon[item],
                                    s1_lat[item],
                                    s2_lon[item],
                                    s2_lat[item],
                                )
                            ]
                        )
                    )
        for key in match[f"{sat1}_{s}"].keys():
            if key != "time":
                match[f"{sat1}_{s}"][key] = match[f"{sat1}_{s}"][key][
                    match[f"{sat1}_{s}"][key] != -1
                ]
            else:
                match[f"{sat1}_{s}"][key] = match[f"{sat1}_{s}"][key][
                    match[f"{sat1}_{s}"][key] != datetime.datetime(1, 1, 1)
                ]
    return match
