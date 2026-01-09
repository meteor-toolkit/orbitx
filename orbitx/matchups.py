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
from datetime import timedelta

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx import Orbit
from orbitx.utils._matchups.find_matches import find_matches
from orbitx.utils._matchups.get_land_ocean_mask import get_land_ocean_mask
from orbitx.utils._constants import SATELLITE_DICT, CM
from orbitx.utils._date_utils import (
    sec_since_to_datetime64,
    datetime64_to_sec_since,
    datetime64_get_second,
)

__author__ = [
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
]

__all__ = ["Matchups"]


class Matchups:
    """
    Class to find matchup events between multiple satellites
    """

    def __init__(self, data: xr.DataTree):
        self._data = data

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
        check_before: bool = False,
        check_after: bool = False,
        has_land_ocean_mask: bool = False,
        reference_date: np.datetime64 = np.datetime64("1970-01-01T00:00:00"),
        custom_satellites: List[Dict[str, str]] = [],
        dump_orbit: bool = False,
    ):
        """Main generator for Matchups object

        Finds matchups between the satellites specified, between the start and end times specified.

        Args:
            satellites (List[str]): List of satellites short names for which the matchups must be found. This variables can only be used for satellites that are natively supported by orbitx. For other satellites, use the custom_satellite argument.
            start_date (np.datetime64): Date from which matchups must be found
            end_date (np.datetime64): Date until which matchups must be found
            propagation_sampling_interval (np.timedelta64): The time resolution of the orbits simulation in seconds (the smaller, the more precise the simulation, but also the slower)
            interpolation_sampling_interval (np.timedelta64): The time resolution of the interpolation of the orbits (interpolating the simulated orbits)
            space_diff_threshold (float): The maximal distance between satellites centers for an event to be called a matchup
            time_diff_threshold (np.timedelta64): The maximal time interval between the passing of two satellites for an event to be called a matchup
            check_before (Optional[bool], optional): Whether matchups where one of the satellites passed before the start date should be considered (useful when running successive time spans in separate threads so bordering matchups are not lost). Defaults to False.
            check_after (Optional[bool], optional): Whether matchups where one of the satellites passed after the end date should be considered (useful when running successive time spans in separate threads so bordering matchups are not lost). Defaults to False.
            has_land_ocean_mask (Optional[bool], optional): Whether a variable informing whether the satellites are above ocean or land (or coast if not all satellites are about the same time of surface) should be added. Defaults to False.
            reference_date (_type_, optional): Time variables are provided as seconds from this reference date. Defaults to np.datetime64("1970-01-01T00:00:00").
            custom_satellites (List[Dict[str, str]], optional): Each dictionnary in the list should have the following keys: `tle_filepath`, `satellite_shortname`, `satellite_name`. `tle_filepath`is the path of a Two Line Element file for the satellite of interest, `satellite_shortname`is the shortname of the satellite of interest (e.g., J2) and `satellite_name` is the full name of the satellite of interest (e.g., Jason-2). Defaults to [].
            dump_orbit (bool, optional): Whether the orbits generated to find the matchups should be deleted (so the objects takes less space). Defaults to False.

        Returns:
            Matchup: A Matchups object containing information about all matchup events identified with the specified parameters.
        """
        data = xr.DataTree()
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
            custom_satellites=custom_satellites,
        )
        # Find the matches between generated orbits
        matchups: xr.Dataset = find_matches(
            orbit,
            time_diff_threshold,
            float(space_diff_threshold),
            check_before,
            check_after,
            has_land_ocean_mask,
        )

        # Add the land / ocean / coast masks
        if has_land_ocean_mask:
            matchups = get_land_ocean_mask(matchups)

        orbit_data: xr.Dataset = orbit._orbits
        if dump_orbit:
            orbit_data = xr.Dataset(
                attrs={
                    "satellite_shortname": matchups.attrs["satellite_shortname"],
                    "satellite_name": matchups.attrs["satellite_name"],
                    "start_date": orbit._orbits.attrs["start_date"],
                    "end_date": orbit._orbits.attrs["end_date"],
                    "propagation_sampling_interval": orbit._orbits.attrs[
                        "propagation_sampling_interval"
                    ],
                    "interpolation_sampling_interval": orbit._orbits.attrs[
                        "interpolation_sampling_interval"
                    ],
                    "version": orbit._orbits.attrs["version"],
                    "creation_date": orbit._orbits.attrs["creation_date"],
                }
            )
        # Create object instance
        data["matchups"] = xr.DataTree(dataset=matchups)
        data["orbits"] = xr.DataTree(orbit_data)
        result = cls(data)
        return result

    @classmethod
    def from_orbit(
        cls,
        orbit: Orbit,
        start_date: np.datetime64,
        end_date: np.datetime64,
        space_diff_threshold: float,
        time_diff_threshold: np.timedelta64,
        check_before: bool = False,
        check_after: bool = False,
        has_land_ocean_mask: bool = False,
        dump_orbit: bool = False,
    ):
        """Generator for Matchups object if orbits were already generated.

        Finds matchups within the orbits submitted.

        Args:
            orbit (Orbit): Orbits in which the matchups must be found
            start_date (np.datetime64): Date from which matchups must be found
            end_date (np.datetime64): Date until which matchups must be found
            space_diff_threshold (float): The maximal distance between satellites centers for an event to be called a matchup
            time_diff_threshold (np.timedelta64): The maximal time interval between the passing of two satellites for an event to be called a matchup
            check_before (Optional[bool], optional): Whether matchups where one of the satellites passed before the start date should be considered (useful when running successive time spans in separate threads so bordering matchups are not lost). Defaults to False.
            check_after (Optional[bool], optional): Whether matchups where one of the satellites passed after the end date should be considered (useful when running successive time spans in separate threads so bordering matchups are not lost). Defaults to False.
            has_land_ocean_mask (Optional[bool], optional): Whether a variable informing whether the satellites are above ocean or land (or coast if not all satellites are about the same time of surface) should be added. Defaults to False.
            dump_orbit (bool, optional): Whether the orbits generated to find the matchups should be deleted (so the objects takes less space). Defaults to False.

        Returns:
            Matchup: A Matchups object containing information about all matchup events identified with the specified parameters.
        """
        data = xr.DataTree()
        # simulate desired orbits
        needed_orbit_start_date = start_date
        needed_orbit_end_date = end_date
        if check_before:
            needed_orbit_start_date = needed_orbit_start_date - time_diff_threshold
        if check_after:
            needed_orbit_end_date = needed_orbit_end_date + time_diff_threshold

        if orbit.start_date > needed_orbit_start_date:
            raise ValueError(
                f"Orbit submitted starts after the requested start date. Orbit start: {orbit.start_date}, requested start date: {needed_orbit_start_date}"
            )
        if orbit.end_date < needed_orbit_end_date:
            raise ValueError(
                f"Orbit submitted ends beofre the requested end date. Orbit end: {orbit.end_date}, requested end date: {needed_orbit_end_date}"
            )

        # Find the matches between generated orbits
        matchups: xr.Dataset = find_matches(
            orbit,
            time_diff_threshold,
            float(space_diff_threshold),
            check_before,
            check_after,
            has_land_ocean_mask,
        )

        # Add the land / ocean / coast masks
        if has_land_ocean_mask:
            matchups = get_land_ocean_mask(matchups)

        orbit_data: xr.Dataset = orbit._orbits
        if dump_orbit:
            orbit_data = xr.Dataset(
                attrs={
                    "satellite_shortname": matchups.attrs["satellite_shortname"],
                    "satellite_name": matchups.attrs["satellite_name"],
                    "start_date": orbit._orbits.attrs["start_date"],
                    "end_date": orbit._orbits.attrs["end_date"],
                    "propagation_sampling_interval": orbit._orbits.attrs[
                        "propagation_sampling_interval"
                    ],
                    "interpolation_sampling_interval": orbit._orbits.attrs[
                        "interpolation_sampling_interval"
                    ],
                    "version": orbit._orbits.attrs["version"],
                    "creation_date": orbit._orbits.attrs["creation_date"],
                }
            )
        # Create object instance
        data["matchups"] = xr.DataTree(dataset=matchups)
        data["orbits"] = xr.DataTree(orbit_data)
        result = cls(data)
        return result

    @classmethod
    def from_netcdf(cls, input_path: str) -> "Matchups":
        """Loads a Matchup object from a netCDF4 file

        Imports an object from a file generated by the `to_netcdf()` method.

        Args:
            input_path (str): The full path of the file to be imported

        Returns:
            Matchups: A Matchups object with the same value as the one that generated the imported file
        """
        data: xr.DataTree = xr.open_datatree(
            input_path, engine="netcdf4", decode_times=True, decode_timedelta=True
        )
        matchups_xarray: xr.Dataset = data["matchups"].to_dataset()
        matchups_xarray["reference_date"] = np.array(
            matchups_xarray["reference_date"], dtype="datetime64[s]"
        )
        matchups_xarray = matchups_xarray.assign(
            time_datetime=(
                ["matchup_index", "satellite"],
                np.array(matchups_xarray["time_datetime"], dtype="datetime64[s]"),
            )
        )

        reference_date_matchups: np.datetime64 = matchups_xarray[
            "reference_date"
        ].values

        matchups_xarray = matchups_xarray.assign(
            time=(
                ["matchup_index", "satellite"],
                xr.apply_ufunc(
                    lambda datetime: datetime64_to_sec_since(
                        datetime, reference_date=reference_date_matchups
                    ),
                    matchups_xarray["time_datetime"],
                    vectorize=True,
                ).data,
            )
        )
        matchups_xarray["time"].attrs[
            "units"
        ] = f"seconds since {reference_date_matchups}"

        orbits_xarray: xr.Dataset = data["orbits"].to_dataset()

        if len(orbits_xarray.variables) > 0:
            orbits_xarray["reference_date"] = np.array(
                orbits_xarray["reference_date"], dtype="datetime64[s]"
            )
            reference_date_orbit: np.datetime64 = orbits_xarray["reference_date"].values
            orbits_xarray = orbits_xarray.assign_coords(
                {
                    "time": np.array(
                        [
                            datetime64_to_sec_since(
                                datetime, reference_date=reference_date_orbit
                            )
                            for datetime in orbits_xarray["time_datetime"].values
                        ],
                    )
                }
            )
            orbits_xarray = orbits_xarray.assign(
                time_datetime=(
                    ["time"],
                    np.array(orbits_xarray["time_datetime"], dtype="datetime64[s]"),
                )
            )

            orbits_xarray["time"].attrs[
                "units"
            ] = f"seconds since {reference_date_orbit}"
        data["orbits"] = xr.DataTree(orbits_xarray)
        data["matchups"] = xr.DataTree(matchups_xarray)

        loaded_matchup = Matchups(data)
        return loaded_matchup

    def to_netcdf(self, output_path: str) -> None:
        """Exports a matchup object to a netcdf file

        Saves the xarray.DataTree object containing the data about matchups and orbits.
        Such file can be loaded as a matchup object using the from_netcdf classmethod.

        :param output_path: The directory where the file should be created (make sure the directory already exists). The file name is generated automatically
        :type output_path: str
        """
        # Construct filename
        sat_part = "_".join(self.satellite_shortname)

        date_part = f"{np.datetime_as_string(self.start_date, unit = "D")}_{np.datetime_as_string(self.end_date, unit = "D")}"

        propagation_sampling_interval_datetime: timedelta = (
            self.orbit.propagation_sampling_interval.item()
        )
        propagation_sampling_interval_float: float = (
            propagation_sampling_interval_datetime.total_seconds()
        )
        interpolation_sampling_interval_datetime: timedelta = (
            self.orbit.interpolation_sampling_interval.item()
        )
        interpolation_sampling_interval_float: float = (
            interpolation_sampling_interval_datetime.total_seconds()
        )
        sampling_part = f"psi{int(propagation_sampling_interval_float)}_isi{int(interpolation_sampling_interval_float)}"
        matchup_part = f"c2c{int(self.space_diff_threshold)}_tdt{int(self.time_diff_threshold.item().total_seconds())}"
        filename = f"{date_part}_{sampling_part}_matchups_{sat_part}_{matchup_part}.nc"
        matchup_output_copy: xr.DataTree = self._data.copy()
        matchup_output_copy.to_netcdf(os.path.join(output_path, filename))

    def plot(self, projection=ccrs.PlateCarree()) -> plt.Figure:
        """
        Plot the matchup dataset generated from orbitx.interface.return_matchups

        :param projection: cartopy.crs projection to use to plot, defaults to cartopy.crs.PlateCarree()
        """
        fig: plt.Figure = plt.figure(figsize=(16 * CM, 9 * CM), dpi=400)
        ax = fig.add_subplot(1, 1, 1, projection=projection)
        ax.coastlines()
        ax.add_feature(cfeature.LAND)

        time_diff_threshold_seconds = self.time_diff_threshold.item().total_seconds()
        mean_delay = np.array(
            [
                m.item().total_seconds()
                for m in np.mean(self.matchups["delay"].values, axis=1)
            ]
        )

        for i_sat, sat in enumerate(self.matchups["satellite"]):
            ax.scatter(
                self.matchups[f"lon"].sel(satellite=sat),
                self.matchups[f"lat"].sel(satellite=sat),
                s=(time_diff_threshold_seconds - mean_delay) ** 2
                / (time_diff_threshold_seconds / 2) ** 2,
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
        result = f"""Matchup object with following attributes:
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
        return len(self.matchups["matchup_index"])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Matchups):
            return NotImplemented
        res: bool = True
        res = res and (self.satellite_name == other.satellite_name)
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
    def satellite_shortname(self) -> List[str]:
        """
        :return: Satellites which the orbits are computed for
        :rtype: List[str]
        """
        return self.matchups.attrs["satellite_shortname"]

    @property
    def orbit(self) -> Orbit:
        return Orbit(self._data["orbits"].dataset)

    @property
    def matchups(self) -> xr.Dataset:
        return self._data["matchups"].dataset

    @property
    def start_date(self):
        return np.array(
            sec_since_to_datetime64(
                self.matchups.attrs["start_date"], self.reference_date
            ),
            dtype="datetime64[s]",
        )

    @property
    def end_date(self):
        return np.array(
            sec_since_to_datetime64(
                self.matchups.attrs["end_date"], self.reference_date
            ),
            dtype="datetime64[s]",
        )

    @property
    def time_diff_threshold(self):
        return np.array(
            int(self.matchups.attrs["time_diff_threshold"]), dtype="timedelta64[s]"
        )

    @property
    def space_diff_threshold(self) -> float:
        return self.matchups.attrs["space_diff_threshold"]

    @property
    def check_before(self):
        return bool(self.matchups.attrs["check_before"])

    @property
    def check_after(self):
        return bool(self.matchups.attrs["check_after"])

    @property
    def has_land_ocean_mask(self):
        return bool(self.matchups.attrs["has_land_ocean_mask"])

    @property
    def reference_date(self):
        return self.matchups["reference_date"].values

    @property
    def creation_date(self):
        return self.matchups.attrs["creation_date"]

    @property
    def version(self):
        return self.matchups.attrs["version"]
