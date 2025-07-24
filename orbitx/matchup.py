"""orbitx.matchup - class to find matchups between satellite orbits"""

import numpy as np
import xarray as xr
import datetime

from math import radians, cos, sin, asin, sqrt

from typing import Dict, Union

__author__ = [
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
]

__all__ = ["Matchups", "get_range", "get_distance", "get_dist"]

# function to get range for each element in a set of arrays
get_range = np.vectorize(lambda *delay: max(delay) - min(delay))


def get_dist(
    lon1: Union[int, float],
    lat1: Union[int, float],
    lon2: Union[int, float],
    lat2: Union[int, float],
) -> float:
    """
    Calculate the distance in kilometers between two points
    on the earth (specified in decimal degrees)

    :param lon1: longitude value of point one
    :param lat1: latitude value of point one
    :param lon2: longitude value of point two
    :param lat2: latitude value of point two
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
    """
    Class to find matchup events between multiple satellites
    """

    def matchup(
        self,
        orbit_output: Dict[str, Dict[str, list]],
        time_diff_threshold: float,
        cntr2cntr_dist: float,
    ):
        """matchup Return information relating to matchup instances between satellites

        .. code-block:: bash

            orbit_output = {"S3A":
                                {"lon": [ -98.71854066,   61.60710602, -138.93439662, ..., 14.49443229,  168.04845583],
                                "lat": [-71.11043521,  81.69396844, -70.91783791, ..., 81.03528723,  66.59527834],
                                "time": List[float]
                                },
                            "LS8":
                                {"lon": [ -97.3285552 ,   46.20308181, -142.9947944 , ..., 2.37331828,  171.198296  ],
                                "lat": [-68.67058448,  80.91129054, -72.89258064, ..., 79.45075576,  64.39909769],
                                "time": List[float],
                                },
                            }

        NB
        Time is given in seconds since 1970 in the orbit_output dictionary
        :param orbit_output: dictionary containing the satellites and their lon, lat and time arrays
        :type orbit_output: Dict[str, Dict[str, list]]
        :param time_diff_threshold: max accepted time difference (in seconds) between satellites to qualify as a matchup
        :type time_diff_threshold: float
        :param cntr2cntr_dist: max accepted distance (in km) between satellites to qualify as a matchup
        :type cntr2cntr_dist: float
        :return: _description_
        :rtype: _type_
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

                position = np.array([s1_lon, s1_lat, s2_lon, s2_lat])[
                    :, [j for j in np.arange(len(s1_lon))]  # if j in match_peak]
                ]

                distance = get_distance(*tuple(position))

                # check distance is within the c2c_dist (centre to centre)
                for item, dist in enumerate(distance):
                    if dist <= cntr2cntr_dist:
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
                                1970, 1, 1
                            ) + datetime.timedelta(seconds=s1_time[item])
                            match[f"{sat1}_{s}"]["distance"][item] = dist
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
    def to_ds(matchup_info: Dict[str, Dict[str, list]], attrs: dict) -> xr.Dataset:
        """
        Convert matchup dictionary to xarray dataset. For matchup events between more than two satellites, matchups
        are filtered to only those where all satellites are within the desired time threshold (specified in attrs).

        The input matchup information dictionary is generated in Matchups.matchup and is of form:

        .. code-block:: bash

            matchup_info = {"S2A_LS8":
                                {"lat1": list,
                                 "lon1": list,
                                 "lat2": list,
                                 "lon2": list,
                                 "delay": list,
                                 "time": list,
                                 "distance": list,
                                },
                            }

        where in this case "S2A" is the first satellite used for the comparison and "LS8" is the second
        satellite. Matchups between multiple satellites would have matchup_info dictionaries that look like:

        .. code-block:: bash

            matchup_info = {"S2A_LS8":
                                {...},
                            "S2A_S3A":
                                {...},
                            }

        where the ellipse (...) contains the same keys as the example above.

        The input attrs dictionary generated in Matchups.matchup is of the form:

        .. code-block:: bash

            attrs = {
                        "time_threshold": time_diff_threshold,
                        "distance_threshold": cntr2cntr_dist,
                        "interpolation_sampling_interval": interpolation_sampling_interval,
                    }

        :param matchup_info: matchup information dict containing lat, lon, distance and time info for matchup events
        :param attrs: dictionary of attributes to be added to the output dataset, must include "time_threshold"
        """

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
            ds_list[i + 1].attrs.update(
                {f"sat{i + 3}": ds_list[i + 1].attrs.pop("sat2")}
            )
        merged_ds = xr.merge(
            [ds.sel(time=times) for ds in ds_list], combine_attrs="no_conflicts"
        )

        return merged_ds.isel(
            time=np.where(
                get_range(*[merged_ds[i] for i in merged_ds if "delay" in str(i)])
                < attrs["time_threshold"]
            )[0]
        )
