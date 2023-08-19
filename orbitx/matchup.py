"""orbitx.matchup - class to find matchups between satellite orbits"""

import os
import numpy as np
import xarray as xr
import datetime

from math import radians, cos, sin, asin, sqrt

from typing import Optional
from scipy.signal import find_peaks

__author__ = [
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
]

__all__ = ["Matchups", "get_range", "get_distance", "get_dist"]

# function to get range for each element in a set of arrays
get_range = np.vectorize(lambda *delay: max(delay) - min(delay))


def get_dist(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r


# function to get distance between two lon lat points
get_distance = np.vectorize(get_dist)


class Matchups:
    def matchup(
        self,
        orbit_output: dict,
        time_diff_threshold: float,
        cntr2cntr_dist: float,
    ):
        """
        Return information relating to matchup instances between satellites

        :param orbit_output: dictionary containing the satellites and their lon, lat and time arrays
        :param time_diff_threshold:
        :param cntr2cntr_dist:
        """
        # choose one satellite to remain stable and loop through the rest with respect to it
        sat1 = list(orbit_output.keys())[0]
        other_sats = [i for i in orbit_output.keys() if i != sat1]

        # get interpolation sampling interval from orbit_output
        interpolation_sampling_interval = (
            orbit_output[sat1]["time"][1] - orbit_output[sat1]["time"][0]
        )
        # set attributes
        attrs = {
            "time_threshold": time_diff_threshold,
            "distance_threshold": cntr2cntr_dist,
            "interpolation_sampling_interval": interpolation_sampling_interval,
        }

        match = dict(
            [
                (
                    f"{sat1}_{s}",
                    {
                        "lat1": -68787 * np.ones(len(orbit_output[sat1]["lat"])),
                        "lon1": -68787 * np.ones(len(orbit_output[sat1]["lat"])),
                        "lat2": -68787 * np.ones(len(orbit_output[sat1]["lat"])),
                        "lon2": -68787 * np.ones(len(orbit_output[sat1]["lat"])),
                        "delay": -68787 * np.ones(len(orbit_output[sat1]["lat"])),
                        "time": np.array(
                            [datetime.datetime(1, 1, 1)]
                            * len(orbit_output[sat1]["lat"])
                        ),
                        "distance": -68787 * np.ones(len(orbit_output[sat1]["lat"])),
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
                position = np.array([s1_lon, s1_lat, s2_lon, s2_lat])[
                    :, [j for j in np.arange(len(s1_lon)) if j in match_peak]
                ]
                distance = get_distance(*tuple(position))
                match_peak = list(match_peak[np.where(distance <= cntr2cntr_dist)])
                max_distance = list(distance[np.where(distance <= cntr2cntr_dist)])

                for idx, item in enumerate(match_peak):
                    if (
                        match[f"{sat1}_{s}"]["delay"][item] == -68787
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
                        match[f"{sat1}_{s}"]["distance"][item] = max_distance[idx]
            for key in match[f"{sat1}_{s}"].keys():
                if key != "time":
                    match[f"{sat1}_{s}"][key] = match[f"{sat1}_{s}"][key][
                        match[f"{sat1}_{s}"][key] != -68787
                    ]
                else:
                    match[f"{sat1}_{s}"][key] = match[f"{sat1}_{s}"][key][
                        match[f"{sat1}_{s}"][key] != datetime.datetime(1, 1, 1)
                    ]
        return self.to_ds(match, attrs)

    @staticmethod
    def to_ds(matchup_info, attrs: Optional[dict] = None) -> xr.Dataset:
        """
        Convert matchup dictionary to xarray dataset

        :param matchup_info:
        :param attrs:
        """
        if attrs is None:
            attrs = {}

        ds_list = [
            xr.Dataset.from_dict(
                dict(
                    [
                        (k, {"dims": "time", "data": v})
                        for k, v in matchup_info[key].items()
                    ]
                )
            ).assign_attrs(
                {
                    **attrs,
                    **dict(
                        [(s, key.split("_")[i]) for i, s in enumerate(["sat1", "sat2"])]
                    ),
                }
            )
            for key in matchup_info.keys()
        ]

        if len(ds_list) == 1:
            return ds_list[0]

        times = ds_list[0].time.data
        for i in range(len(ds_list) - 1):
            times = list(set(ds_list[i + 1].time.data).intersection(times))
            ds_list[i + 1] = ds_list[i + 1].rename(
                {
                    "lat2": f"lat{i + 3}",
                    "lon2": f"lon{i + 3}",
                    "delay": f"delay{i + 2}",
                    "distance": f"distance{i + 2}",
                }
            )
            ds_list[i + 1].assign_attrs(
                {f"sat{i + 3}": ds_list[i + 1].attrs.pop("sat2")}
            )
        merged_ds = xr.merge(
            [ds.sel(time=times) for ds in ds_list], combine_attrs="no_conflicts"
        )

        return merged_ds.isel(
            time=np.where(
                get_range(*[merged_ds[i] for i in merged_ds if "delay" in i])
                < attrs["time_threshold"]
            )[0]
        )
