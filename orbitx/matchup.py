"""orbitx.matchup - class to find matchups between satellite orbits"""


"""___Third-Party Modules___"""
import numpy as np
import xarray as xr
import datetime
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from typing import Optional, List

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx import Orbit
from orbitx.utils._matchup.get_dist import get_distance
from orbitx.utils._constants import SATELLITE_DICT

__author__ = [
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
]

__all__ = ["Matchups", "get_range", "get_distance", "get_dist"]

# function to get range for each element in a set of arrays
get_range = np.vectorize(lambda *delay: max(delay) - min(delay))

class Matchups:
    """
    Class to find matchup events between multiple satellites
    """
    def __init__(
            self,
            satellites: List[str],
            start_time: datetime.datetime,
            end_time: datetime.datetime,
            time_diff_threshold: float,
            space_diff_threshold: float,
            check_before: Optional[bool]=False,
            check_after: Optional[bool]=False,
            propagation_sampling_interval: float = 60,
            interpolation_sampling_interval: float = 5,
            has_land_ocean_mask: bool = False):
        
        self._start_time = start_time
        self._end_time = end_time
        self._time_diff_threshold = time_diff_threshold
        self._space_diff_threshold = space_diff_threshold
        self._interpolation_sampling_interval = interpolation_sampling_interval
        self._has_land_ocean_mask = has_land_ocean_mask
        self._satellites = satellites

        orbit = Orbit(
            self.satellites,
            self.start_time,
            self.end_time,
            self.propagation_sampling_interval,
            self.interpolation_sampling_interval)
        
        self.eval(orbit)
        if self.has_land_ocean_mask:
            self.land_ocean_mask()

    def eval(
        self,
        orbit: Orbit
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
        sat1 = list(orbit.satellites)[0]
        other_sats = [i for i in orbit.satellites if i != sat1]

        # set attributes
        attrs = {
            "time_threshold": self.time_diff_threshold,
            "distance_threshold": self.space_diff_threshold,
            "interpolation_sampling_interval": self.interpolation_sampling_interval,
        }

        match = dict(
            [
                (
                    f"{sat1}_{s}",
                    {
                        "lat1": -68787 * np.ones(len(orbit.orbits[sat1]["lat"])),
                        "lon1": -68787 * np.ones(len(orbit.orbits[sat1]["lat"])),
                        "lat2": -68787 * np.ones(len(orbit.orbits[sat1]["lat"])),
                        "lon2": -68787 * np.ones(len(orbit.orbits[sat1]["lat"])),
                        "delay": -68787 * np.ones(len(orbit.orbits[sat1]["lat"])),
                        "time": np.array(
                            [datetime.datetime(1, 1, 1)]
                            * len(orbit.orbits[sat1]["lat"])
                        ),
                        "distance": -68787 * np.ones(len(orbit.orbits[sat1]["lat"])),
                    },
                )
                for s in other_sats
            ]
        )

        s1_lat = orbit.orbits[sat1]["lat"]
        s1_lon = orbit.orbits[sat1]["lon"]
        s1_time = orbit.orbits[sat1]["time"]

        # Calculate number of interpolation sampling bins fit into the time difference threshold and generate vector of numbers of bins
        acceptable_bin_shifts = range(
                -abs(int(self.time_diff_threshold / self.interpolation_sampling_interval)),
                +abs(int(self.time_diff_threshold / self.interpolation_sampling_interval)),
            )
        for s in other_sats:
            # roll through the accepted time window through the lons and lats
            for i in acceptable_bin_shifts:
                s2_lat = np.roll(orbit.orbits[s]["lat"], i)
                s2_lon = np.roll(orbit.orbits[s]["lon"], i)

                position = np.array([s1_lon, s1_lat, s2_lon, s2_lat])[
                    :, [j for j in np.arange(len(s1_lon))]  # if j in match_peak]
                ]

                distance = get_distance(*tuple(position))

                # check distance is within the c2c_dist (centre to centre)
                for item, dist in enumerate(distance):
                    if dist <= self.space_diff_threshold:
                        if (
                            match[f"{sat1}_{s}"]["delay"][item] == -68787
                            or match[f"{sat1}_{s}"]["delay"][item]
                            > i * self.interpolation_sampling_interval
                        ):
                            match[f"{sat1}_{s}"]["lat1"][item] = s1_lat[item]
                            match[f"{sat1}_{s}"]["lon1"][item] = s1_lon[item]
                            match[f"{sat1}_{s}"]["lat2"][item] = s2_lat[item]
                            match[f"{sat1}_{s}"]["lon2"][item] = s2_lon[item]
                            match[f"{sat1}_{s}"]["delay"][item] = (
                                i * self.interpolation_sampling_interval
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
        self.matchups = match
        return

    def land_ocean_mask(self):
        pass

    def to_netcdf(
            self,
            output_path:str)->None:
        # Construct filename
        sat_part = "_".join(self.satellites)

        date_part = f"{start_time:%Y%m%d}_{end_time:%Y%m%d}"
        sampling_part = (
            f"psi{propagation_sampling_interval}_isi{interpolation_sampling_interval}"
        )
        matchup_part = f"c2c{cntr2cntr_dist}_tdt{time_diff_threshold}"
        filename = f"{date_part}_{sampling_part}_matchups_{sat_part}_{matchup_part}.nc"

        matchup_output_copy = matchup_output.copy()

        # Add seconds since 2000 for altimetry applications.
        ref_time = np.datetime64("2000-01-01T00:00:00", "ns")
        seconds_since_2000 = (matchup_output["time"].values - ref_time) / np.timedelta64(1, "s")
        matchup_output_copy["seconds_since_2000"] = xr.DataArray(
            seconds_since_2000,
            dims=["time"],
            coords={"time": matchup_output["time"]},
            attrs={"description": "Seconds since 2000-01-01T00:00:00 UTC"}
        )

        matchup_output_copy.to_netcdf(os.path.join(output_path_matchups, filename))


    def to_ds(self) -> xr.Dataset:
        """
        Convert matchup dictionary to xarray dataset. For matchup events between more than two satellites, matchups
        are filtered to only those where all satellites are within the desired time threshold (specified in attrs).

        The input matchup information dictionary is generated in Matchups.matchup and is of form:

        .. code-block:: bash

            matchup_info = {"S2A_LS8":
                                {"lat1": npt.NDArray,
                                 "lon1": npt.NDArray,
                                 "lat2": npt.NDArray,
                                 "lon2": npt.NDArray,
                                 "delay": npt.NDArray,
                                 "time": npt.NDArray,
                                 "distance": npt.NDArray,
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
                        for k, v in self.matchups[key].items()
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
            for key in self.matchups.keys()
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
                < self.time_threshold
            )[0]
        )
    
    def plot(
            self,
            projection=ccrs.PlateCarree()
            ) -> None:
        """
        Plot the matchup dataset generated from orbitx.interface.return_matchups

        :param ds: matchup dataset containing latitude, latitude and time information for matchup events
        :param projection: cartopy.crs projection to use to plot, defaults to cartopy.crs.PlateCarree()
        """
        cm = 1 / 2.54
        fig = plt.figure(figsize=(16 * cm, 9 * cm), dpi=400)
        ax = fig.add_subplot(1, 1, 1, projection=projection)
        ax.coastlines()
        ax.add_feature(cfeature.LAND)
        sat_no = len([i for i in ds if "lat" in i])
        if sat_no == 2:
            delay = ds["delay"]
        else:
            delay = get_range(*[ds[i] for i in ds if "delay" in str(i)])
        for i in range(sat_no):
            ax.scatter(
                ds[f"lon{i + 1}"],
                ds[f"lat{i + 1}"],
                s=(ds.attrs["time_threshold"] - delay) ** 2
                / (ds.attrs["time_threshold"] / 2) ** 2,
                label=SATELLITE_DICT[ds.attrs[f"sat{i + 1}"]],
                transform=ccrs.PlateCarree(),
            )
        ax.legend(loc="lower right")
        plt.show()


    @property
    def satellites(self):
        return self._satellites
    
    @property
    def time_diff_threshold(self):
        return self._time_diff_threshold
    
    @property
    def space_diff_threshold(self):
        return self._space_diff_threshold
    
    @property
    def interpolation_sampling_interval(self):
        return self._interpolation_sampling_interval

    @property
    def has_land_ocean_mask(self):
        return self._has_land_ocean_mask
