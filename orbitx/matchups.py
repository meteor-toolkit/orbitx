"""orbitx.matchup - class to find matchups between satellite orbits"""


"""___Third-Party Modules___"""
import numpy as np
import xarray as xr
import datetime
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from typing import Optional, List, Dict
import numpy.typing as npt
import os

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx import Orbit
from orbitx.utils._matchups.find_matches import find_matches
from orbitx.utils._matchups.get_land_ocean_mask import get_land_ocean_mask
from orbitx.utils._matchups.matchup_dict_to_xarray import matchup_dict_to_xarray
from orbitx.utils._constants import SATELLITE_DICT, CM
from orbitx.utils._date_utils import datetime_to_sec_since, sec_since_to_datetime

__author__ = [
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
]

__all__ = ["Matchups"]

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
            orbit:Orbit,
            matchups: Dict[str, Dict[str, npt.NDArray]],
            check_before: Optional[bool]=False,
            check_after: Optional[bool]=False,
            has_land_ocean_mask: bool = False):
        
        self._satellites = satellites
        self._start_time = start_time
        self._end_time = end_time
        self._time_diff_threshold = time_diff_threshold
        self._space_diff_threshold = space_diff_threshold
        self._check_before = check_before
        self._check_after = check_after
        self._has_land_ocean_mask = has_land_ocean_mask
        self._orbit = orbit
        self._matchups = matchups

    @classmethod
    def find_matchups(
        cls,
        satellites: List[str],
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        propagation_sampling_interval: float,
        interpolation_sampling_interval: float,
        space_diff_threshold: float,
        time_diff_threshold: float,
        check_before:Optional[bool]=False,
        check_after:Optional[bool]=False,
        has_land_ocean_mask:Optional[bool]=False
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
        """
        # simulate desired orbits
        orbit_start_time = start_time
        orbit_end_time = end_time
        if check_before:
            orbit_start_time = orbit_start_time - datetime.timedelta(seconds=time_diff_threshold)
        if check_after:
            orbit_end_time = orbit_end_time + datetime.timedelta(seconds=time_diff_threshold)
        orbit = Orbit.simulate(
            satellites=satellites,
            start_time=orbit_start_time,
            end_time=orbit_end_time,
            propagation_sampling_interval=propagation_sampling_interval,
            interpolation_sampling_interval=interpolation_sampling_interval
        )

        # Find the matches between generated orbits
        matchups = find_matches(
            orbit,
            time_diff_threshold,
            space_diff_threshold,
            start_time,
            end_time)
        # Add the land / ocean / coast masks
        if has_land_ocean_mask:
            matchups = get_land_ocean_mask(matchups)

        # Convert the dictionary of matchups to an xarray 
        attributes = {
            "satellites": satellites,
            "start_time": start_time,
            "end_time": end_time,
            "time_diff_threshold": time_diff_threshold,
            "space_diff_threshold": space_diff_threshold,
            "check_before": check_before,
            "check_after": check_after,
            "has_land_ocean_mask": has_land_ocean_mask,
            "interpolation_sampling_interval": orbit.interpolation_sampling_interval,
            "propagation_sample_interval": orbit.propagation_sampling_interval
        }
        matchups = matchup_dict_to_xarray(matchups, attributes)

        # Create object instance
        result = cls(satellites,
        start_time,
        end_time,
        time_diff_threshold,
        space_diff_threshold,
        orbit,
        matchups,
        check_before,
        check_after,
        has_land_ocean_mask)
        return result

    def __str__(self):
        result = f"""
Matchup object with following attributes:
Satellites considered: {self.satellites}
Date from which matchups are looked for: {self.start_time}
Date until which matchups are looked for: {self.end_time}
Maximum time difference between members of a matchup: {self.time_diff_threshold} (seconds)
Maximum distance between members of a matchup: {self.space_diff_threshold} (km)
Are matchups in which on of the satellites appears before the start date considered? {self.check_before}
Are matchups in which on of the satellites appears after the end date considered? {self.check_after}
Has this matchup a land/ocean mask? {self.has_land_ocean_mask}
Number of matchups found: {len(self)}
"""
        return result
    
    def __len__(self):
        return len(self.matchups["time"])
    
    def to_netcdf(
            self,
            output_path:str,
            reference_date:datetime.datetime = datetime.datetime(1970, 1, 1, 0, 0, 0))->None:
        # Construct filename
        sat_part = "_".join(self.satellites)

        date_part = f"{self.start_time:%Y%m%d}_{self.end_time:%Y%m%d}"
        sampling_part = (
            f"psi{self.orbit.propagation_sampling_interval}_isi{self.orbit.interpolation_sampling_interval}"
        )
        matchup_part = f"c2c{self.space_diff_threshold}_tdt{self.time_diff_threshold}"
        filename = f"{date_part}_{sampling_part}_matchups_{sat_part}_{matchup_part}.nc"

        matchup_output_copy = self.matchups.copy()

        matchup_output_copy.attrs["start_time"] = datetime_to_sec_since(self.start_time, reference_date)
        matchup_output_copy.attrs["end_time"] = datetime_to_sec_since(self.end_time, reference_date)
        matchup_output_copy.attrs['check_before'] = str(matchup_output_copy.attrs['check_before'])
        matchup_output_copy.attrs['check_after'] = str(matchup_output_copy.attrs['check_after'])
        matchup_output_copy.attrs['has_land_ocean_mask'] = str(matchup_output_copy.attrs['has_land_ocean_mask'])


        matchup_output_copy.to_netcdf(os.path.join(output_path, filename))
    
    def plot(
            self,
            projection=ccrs.PlateCarree()
            ) -> plt.Figure:
        """
        Plot the matchup dataset generated from orbitx.interface.return_matchups

        :param projection: cartopy.crs projection to use to plot, defaults to cartopy.crs.PlateCarree()
        """
        fig = plt.figure(figsize=(16 * CM, 9 * CM), dpi=400)
        ax = fig.add_subplot(1, 1, 1, projection=projection)
        ax.coastlines()
        ax.add_feature(cfeature.LAND)

        sat_no = len(self.satellites)
        if sat_no == 2:
            delay = self.matchups["delay"]
        else:
            delay = get_range(*[self.matchups[i] for i in self.matchups if "delay" in str(i)])
        for i in range(sat_no):
            ax.scatter(
                self.matchups[f"lon{i + 1}"],
                self.matchups[f"lat{i + 1}"],
                s=(self.time_diff_threshold - delay) ** 2
                / (self.time_diff_threshold / 2) ** 2,
                label=SATELLITE_DICT[self.satellites[i]],
                transform=projection,
                alpha=.7
            )
        ax.legend(loc="lower right")
        return fig

    @property
    def satellites(self):
        return self._satellites
    
    @property
    def orbit(self):
        return self._orbit
    
    
    @property
    def matchups(self):
        return self._matchups
    
    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time
    
    @property
    def time_diff_threshold(self):
        return self._time_diff_threshold
    
    @property
    def space_diff_threshold(self):
        return self._space_diff_threshold

    @property
    def check_before(self):
        return self._check_before

    @property
    def check_after(self):
        return self._check_after

    @property
    def has_land_ocean_mask(self):
        return self._has_land_ocean_mask

# for year in years:
#     df_y = df.where(df.year == year)
#     df_y = df_y.dropna()
#     for month in set(df_y["month"]):


#         df_m = df_y.where(df_y.month == month)
#         df_m = df_m.dropna()

#         projection = ccrs.Mollweide()
#         fig = plt.figure()
#         ax = fig.add_subplot(1, 1, 1, projection=projection)
#         ax.coastlines()
#         ax.add_feature(cfeature.LAND)
#         sat_no = len([i for i in ds if "lat" in i])
#         if sat_no == 2:
#             delay = df_m["delay"].values
#         else:
#             delay = get_range(*[df_m[i] for i in df_m if "delay" in str(i)])
#         for i in range(sat_no):
#             ax.scatter(
#                 df_m[f"lon{i + 1}"].values,
#                 df_m[f"lat{i + 1}"].values,
#                 s=((ds.attrs["time_threshold"] - delay) ** 2
#                 / (ds.attrs["time_threshold"] / 2) ** 2),
#                 label=SATELLITE_DICT[ds.attrs[f"sat{i + 1}"]],
#                 transform=ccrs.PlateCarree(),
#             )
#         ax.legend(loc="lower right")

#         fig_str = ds.attrs["sat1"] + "_" +ds.attrs["sat2"] + "_" + str(year) + "_" + str(month)
#         plt.title("Matchups " + ds.attrs["sat1"] + " and " + ds.attrs["sat2"] + " " + str(year) + "-" + str(month) + ", time threshold: " + str(ds.attrs["time_threshold"]) +" seconds")
#         plt.savefig(fig_str+".png")

# df.to_csv(outname)