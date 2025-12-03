"""orbitx.matchup - class to find matchups between satellite orbits"""

"""___Third-Party Modules___"""
import numpy as np
import xarray as xr
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from typing import Optional, List, Dict
import numpy.typing as npt
import os
import netCDF4 as nc

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx import Orbit
from orbitx.utils._matchups.find_matches import find_matches
from orbitx.utils._matchups.get_land_ocean_mask import get_land_ocean_mask
from orbitx.utils._matchups.matchup_dict_to_xarray import matchup_dict_to_xarray
from orbitx.utils._constants import SATELLITE_DICT, CM
from orbitx.utils._date_utils import sec_since_to_datetime64, datetime64_to_sec_since

__author__ = [
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
]

__all__ = ["Matchups"]


class Matchups:
    """
    Class to find matchup events between multiple satellites
    """

    def __init__(
        self,
        matchups: xr.Dataset,
        orbit: Orbit
    ):
        self._matchups = matchups
        self._orbit = orbit

    @classmethod
    def find_matchups(
        cls,
        satellites: List[str],
        start_date: np.datetime64,
        end_date: np.datetime64,
        propagation_sampling_interval: np.timedelta64,
        interpolation_sampling_interval: np.timedelta64,
        space_diff_threshold: float,
        time_diff_threshold: np.timedelta64,
        check_before: Optional[bool] = False,
        check_after: Optional[bool] = False,
        has_land_ocean_mask: Optional[bool] = False,
        reference_date: np.datetime64 = np.datetime64("1970-01-01T00:00:00"),
        custom_satellites: List[Dict[str, str]] = []
    ):
        """Main generator for Matchups object

        Finds matchups between the satellites specified, between the start and end times specified.

        :param satellites: List of satellites short names for which the matchups must be found
        :type satellites: List[str]
        :param start_date: Date from which matchups must be found
        :type start_date: np.datetime64
        :param end_date: Date before which matchups must be found
        :type end_date: np.datetime64
        :param propagation_sampling_interval: The time resolution of the orbits simulation in seconds (the smaller, the more precise the simulation, but also the slower)
        :type propagation_sampling_interval: np.timedelta64
        :param interpolation_sampling_interval: The time resolution of the interpolation of the orbits (interpolating the simulated orbits)
        :type interpolation_sampling_interval: np.timedelta64
        :param space_diff_threshold: The maximal distance between satellites centers for an event to be called a matchup
        :type space_diff_threshold: float
        :param time_diff_threshold: The maximal time interval between the passing of two satellites for an event to be called a matchup
        :type time_diff_threshold: np.timedelta64
        :param check_before: Whether matchups where one of the satellites passed before the start date should be considered (useful when running successive time spans in separate threads so bordering matchups are not lost), defaults to False
        :type check_before: Optional[bool], optional
        :param check_after: Whether matchups where one of the satellites passed after the end date should be considered (useful when running successive time spans in separate threads so bordering matchups are not lost), defaults to False
        :type check_after: Optional[bool], optional
        :param has_land_ocean_mask: Whether a variable informing whether the satellites are above ocean or land (or coast if not all satellites are about the same time of surface) should be added, defaults to False
        :type has_land_ocean_mask: Optional[bool], optional
        :param reference_date: Time variables are provided as seconds from this reference date, defaults to np.datetime64("1970-01-01T00:00:00)
        :type reference_date: np.datetime64, optional
        :return: A Matchups object containing information about all matchup events identified with the specified parameters.
        :rtype: Matchup
        """
        # simulate desired orbits
        orbit_start_date = start_date
        orbit_end_date = end_date
        if check_before:
            orbit_start_date = orbit_start_date - time_diff_threshold
        if check_after:
            orbit_end_date = orbit_end_date + time_diff_threshold

        orbit = Orbit.simulate(
            satellites=satellites,
            start_date=orbit_start_date,
            end_date=orbit_end_date,
            propagation_sampling_interval=propagation_sampling_interval,
            interpolation_sampling_interval=interpolation_sampling_interval,
            reference_date=reference_date,
            custom_satellites=custom_satellites
        )
        # Find the matches between generated orbits
        matchups = find_matches(
            orbit,
            time_diff_threshold,
            float(space_diff_threshold),
            start_date,
            end_date,
            check_before,
            check_after,
            has_land_ocean_mask
        )

        # Convert the dictionary of matchups to an xarray
        attributes = {
            "satellite_shortname": orbit.satellite_shortname,
            "satellite_name": orbit.satellite_name,
            "start_date": start_date,
            "end_date": end_date,
            "time_diff_threshold": time_diff_threshold,
            "space_diff_threshold": float(space_diff_threshold),
            "check_before": check_before,
            "check_after": check_after,
            "has_land_ocean_mask": has_land_ocean_mask,
            "interpolation_sampling_interval": orbit.interpolation_sampling_interval,
            "propagation_sampling_interval": orbit.propagation_sampling_interval,
        }
        matchups = matchup_dict_to_xarray(matchups, attributes, reference_date)

        # Add the land / ocean / coast masks
        if has_land_ocean_mask:
            matchups = get_land_ocean_mask(matchups)

        # Create object instance
        result = cls(
            matchups,
            orbit
        )
        return result

    @classmethod
    def from_netcdf(cls, input_path: str) -> "Matchups":
        """from_netcdf Loads a Matchup object from a netCDF4 file

        Imports an object from a file generated by the `to_netcdf()` method.

        :param input_path: The full path of the file to be imported
        :type input_path: str
        :return: A Matchups object with the same value as the one that generated the imported file
        :rtype: Matchups
        """
        matchups_xarray = xr.open_dataset(
            input_path, engine="netcdf4", decode_times=True, decode_timedelta=True
        )

        satellites = matchups_xarray.attrs["satellites"]

        reference_date = np.array(
            [matchups_xarray["reference_date"].values], dtype="datetime64[s]"
        )[0]
        time_datetime = np.array(
            matchups_xarray[f"time_datetime"].values, dtype="datetime64[s]"
        )
        matchups_xarray = matchups_xarray.assign_coords(
            coords={
                "time": [
                    datetime64_to_sec_since(date, reference_date)
                    for date in time_datetime
                ]
            }
        )

        matchups_xarray = matchups_xarray.assign(
            variables={
                "reference_date": (reference_date),
                "time_datetime": ("time", time_datetime),
            }
        )

        matchups_xarray["time"].attrs["units"] = f"seconds since {reference_date}"

        start_date = sec_since_to_datetime64(
            matchups_xarray.attrs["start_date"], reference_date=reference_date
        )
        end_date = sec_since_to_datetime64(
            matchups_xarray.attrs["end_date"], reference_date=reference_date
        )
        propagation_sampling_interval = np.array(
            [matchups_xarray.attrs["propagation_sampling_interval"]],
            dtype="timedelta64[s]",
        )[0]
        interpolation_sampling_interval = np.array(
            [matchups_xarray.attrs["interpolation_sampling_interval"]],
            dtype="timedelta64[s]",
        )[0]
        time_diff_threshold = np.array(
            [matchups_xarray.attrs["time_diff_threshold"]], dtype="timedelta64[s]"
        )[0]
        space_diff_threshold = float(matchups_xarray.attrs["space_diff_threshold"])
        check_before = bool(matchups_xarray.attrs["check_before"])
        check_after = bool(matchups_xarray.attrs["check_after"])
        has_land_ocean_mask = bool(matchups_xarray.attrs["has_land_ocean_mask"])

        for sat_index, _ in enumerate(satellites[1:]):
            time_datetime_sat = np.array(
                matchups_xarray[f"time_datetime{sat_index + 2}"].values,
                dtype="datetime64[s]",
            )
            time_sat = np.array(
                [
                    datetime64_to_sec_since(date, reference_date)
                    for date in time_datetime_sat
                ],
                dtype=float,
            )
            matchups_xarray = matchups_xarray.assign(
                variables={
                    f"time_datetime{sat_index + 2}": ("time", time_datetime_sat),
                    f"time{sat_index + 2}": ("time", time_sat),
                }
            )

        loaded_orbit_start_date = start_date
        loaded_orbit_end_date = end_date

        if check_before:
            loaded_orbit_start_date = loaded_orbit_start_date - time_diff_threshold
        if check_after:
            loaded_orbit_end_date = loaded_orbit_end_date + time_diff_threshold

        loaded_orbit = Orbit.simulate(
            satellites=satellites,
            start_date=loaded_orbit_start_date,
            end_date=loaded_orbit_end_date,
            propagation_sampling_interval=propagation_sampling_interval,
            interpolation_sampling_interval=interpolation_sampling_interval,
            reference_date=reference_date,
        )
        loaded_matchup = Matchups(
            matchups=matchups_xarray,
            orbit=loaded_orbit
        )
        return loaded_matchup

    def to_netcdf(self, output_path: str) -> None:
        """to_netcdf Exports a matchup object to a netcdf file

        The exported file is structured as follows:

        :param output_path: The directory where the file should be created (make sure the directory already exists). The file name is generated automatically
        :type output_path: str
        :param reference_date: The time variables in this file are stored as a float representing the number of seconds from this reference date, defaults to np.datetime64("1970-01-01T00:00:00")
        :type reference_date: np.datetime64, optional
        """
        # Construct filename
        sat_part = "_".join(self.satellites)

        date_part = f"{np.datetime_as_string(self.start_date, unit = "D")}_{np.datetime_as_string(self.end_date, unit = "D")}"
        sampling_part = f"psi{self.orbit.propagation_sampling_interval.item().total_seconds()}_isi{self.orbit.interpolation_sampling_interval.item().total_seconds()}"
        matchup_part = f"c2c{self.space_diff_threshold}_tdt{self.time_diff_threshold.item().total_seconds()}"
        filename = f"{date_part}_{sampling_part}_matchups_{sat_part}_{matchup_part}.nc"

        matchup_output_copy = self.matchups.copy()

        matchup_output_copy.to_netcdf(os.path.join(output_path, filename))

    def plot(self, projection=ccrs.PlateCarree()) -> plt.Figure:
        """
        Plot the matchup dataset generated from orbitx.interface.return_matchups

        :param projection: cartopy.crs projection to use to plot, defaults to cartopy.crs.PlateCarree()
        """
        fig = plt.figure(figsize=(16 * CM, 9 * CM), dpi=400)
        ax = fig.add_subplot(1, 1, 1, projection=projection)
        ax.coastlines()
        ax.add_feature(cfeature.LAND)


        mean_delay = np.mean(self.matchups["delay"].values, axis=0)

        for i_sat, sat in enumerate(self.matchups["satellite"]):
            ax.scatter(
                self.matchups[f"lon"].sel(satellite = sat),
                self.matchups[f"lat"].sel(satellite = sat),
                # s=(self.time_diff_threshold.item().total_seconds() - mean_delay) ** 2
                # / (self.time_diff_threshold.item().total_seconds() / 2) ** 2,
                label=self.satellite_name[i_sat],
                transform=projection,
                alpha=0.7,
            )
        ax.legend(loc="lower right")
        return fig

    def __str__(self) -> str:
        """__str__ Gives a short summary of the characteristics of a Matchup object

        The information displayed is the following:
        Matchup object with following attributes:
        Satellites considered
        Date from which matchups are looked for
        Date until which matchups are looked for
        Maximum time difference between members of a matchup (seconds)
        Maximum distance between members of a matchup (km)
        Are matchups in which one of the satellites appears before the start date considered?
        Are matchups in which one of the satellites appears after the end date considered?
        Has this matchup a land/ocean mask?
        Number of matchups found
        """
        result = f"""
Matchup object with following attributes:
Satellites considered: {self.satellite_name}
Date from which matchups are looked for: {self.start_date}
Date until which matchups are looked for: {self.end_date}
Maximum time difference between members of a matchup: {self.time_diff_threshold} (seconds)
Maximum distance between members of a matchup: {self.space_diff_threshold} (km)
Are matchups in which on of the satellites appears before the start date considered? {self.check_before}
Are matchups in which on of the satellites appears after the end date considered? {self.check_after}
Has this matchup a land/ocean mask? {self.has_land_ocean_mask}
Number of matchups found: {len(self)}.
Created on {self.creation_date} using the version {self.version} of orbitx.
"""
        return result

    def __len__(self) -> int:
        """__len__ Number of matchups in this object

        :return: Number of matchups in this object
        :rtype: int
        """
        return len(self.matchups["time"])

    def __eq__(self, other: "Matchups") -> bool:
        res = True
        res = res and (self.satellites == other.satellites)
        res = res and (self.start_date == other.start_date)
        res = res and (self.end_date == other.end_date)
        res = res and (self.time_diff_threshold == other.time_diff_threshold)
        res = res and (self.space_diff_threshold == other.space_diff_threshold)
        res = res and (self.orbit == other.orbit)
        res = res and (self.matchups.equals(other.matchups))
        res = res and (self.check_before == other.check_before)
        res = res and (self.check_after == other.check_after)
        res = res and (self.has_land_ocean_mask == other.has_land_ocean_mask)
        res = res and (self.reference_date == other.reference_date)
        return res

    @property
    def satellite_name(self):
        return self.matchups.attrs["satellite_name"]

    @property
    def orbit(self):
        return self._orbit

    @property
    def matchups(self):
        return self._matchups

    @property
    def start_date(self):
        return self.matchups.attrs["start_date"]

    @property
    def end_date(self):
        return self.matchups.attrs["end_date"]

    @property
    def time_diff_threshold(self):
        return self.matchups.attrs["time_diff_threshold"]

    @property
    def space_diff_threshold(self):
        return self.matchups.attrs["space_diff_threshold"]

    @property
    def check_before(self):
        return self.matchups.attrs["check_before"]

    @property
    def check_after(self):
        return self.matchups.attrs["check_after"]

    @property
    def has_land_ocean_mask(self):
        return self.matchups.attrs["has_land_ocean_mask"]

    @property
    def reference_date(self):
        return self.matchups["reference_date"].values
    
    @property
    def creation_date(self):
        return self.matchups.attrs["creation_date"]
    
    @property
    def version(self):
        return self.matchups.attrs["version"]
