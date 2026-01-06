"""orbitx.orbit - class to simulate satellite orbits"""

"""___Third-Party Modules___"""
from typing import List, Dict
import os
import xarray as xr
import numpy.typing as npt
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from datetime import timedelta

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._orbit.simulate_orbit import simulate_orbit
from orbitx.utils._orbit.interpolate_orbit import interpolate_orbit
from orbitx.utils._orbit.orbit_dict_to_xarray import orbit_dict_to_xarray
from orbitx.utils._constants import CM, SATELLITE_DICT
from orbitx.utils._date_utils import datetime64_to_sec_since, sec_since_to_datetime64
from orbitx.tle import TLE

"""___Authorship___"""
__author__ = __author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>",
]
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>",
]
__status__ = "Development"


__all__ = ["Orbit"]


class Orbit:
    """Class to simulate satellite orbits"""

    def __init__(
        self,
        orbit: xr.Dataset,
    ):
        self._orbits = orbit

    @classmethod
    def simulate(
        cls,
        satellites: List[str],
        start_date: np.datetime64,
        end_date: np.datetime64,
        propagation_sampling_interval: np.timedelta64,
        interpolation_sampling_interval: np.timedelta64,
        reference_date: np.datetime64 = np.datetime64("1970-01-01T00:00:00"),
        custom_satellites: List[Dict[str, str]] = [],
    ):
        """Main generator for the Orbit class

        Simulates the orbit of requested satellites between `start_date` and `end_date`.
        The supported names for satellites are the following:

        .. code-block:: bash

            "LS8": "Landsat-8",
            "LS9": "Landsat-9",
            "S2A": "Sentinel-2A",
            "S2B": "Sentinel-2B",
            "S3A": "Sentinel-3A",
            "S3B": "Sentinel-3B",
            "S6": "Sentinel-6",
            "J2": "JASON-2",
            "J3": "JASON-3",
            "SA": "Saral-AltiKa",
            "CS2": "CryoSat-2",
            "LINCS2": "Lin-CryoSat-2",
            "N20": "NOAA-20"

        If the satellite you are interested in is not in this list, you may use the `custom_satellites` argument.

        The simulation starts by finding relevant Two Line Elements (TLE).
        The simulation then does a *Physics* simulation of the orbits (propagation step) from the TLEs at the requested resolution `propagation_sampling_interval`.
        Finally the simulation performs an interpolation of the propagated orbits at the requested resolution `interpolation_sampling_interval`

        Args:
            satellites (List[str]): List of short names for satellites.
            start_date (np.datetime64): The date from which the orbits are to be simulated
            end_date (np.datetime64): The date until which the orbits are to be simulated
            propagation_sampling_interval (np.timedelta64): The time interval in seconds between two successive physics simulations of the orbit
            interpolation_sampling_interval (np.timedelta64): The time interval in seconds between two successive interpolations
            reference_date (_type_, optional): The time variable of an orbit is given in seconds since a reference year. This variable let's you set this reference year. Defaults to np.datetime64("1970-01-01T00:00:00").
            custom_satellites (List[Dict[str, str]], optional): A list of dictionaries used for the satellites that are not natively covered in OrbitX. Each element of the list needs to be a dictionary with the following entries: tle_filepath (the path to the TLE file for the satellite), satellite_shortname (the short name of the satellite), satellite_name (the full name of the satellite). Defaults to [].

        Returns:
            Orbit: An Orbit object with the requested parameters. See the Orbit class documentation for details about their structure
        """
        orbit_dict = {}
        for sat in satellites:
            tle = TLE.from_sat_shortname(sat, start_date, end_date, reference_date)
            sat_secs_since, _, sat_lat_sim, sat_lon_sim = simulate_orbit(
                start_date,
                end_date,
                tle,
                propagation_sampling_interval,
                reference_date,
            )

            time, date, lat, lon = interpolate_orbit(
                start_date,
                end_date,
                sat_secs_since,
                sat_lat_sim,
                sat_lon_sim,
                interpolation_sampling_interval,
                reference_date,
            )
            orbit_dict.update(
                {
                    sat: {
                        "lat": lat,
                        "lon": lon,
                        "time": time,
                        "time_datetime": date,
                        "satellite_name": tle.satellite_name,
                    }
                }
            )

        for sat_dict in custom_satellites:
            tle = TLE.from_filepath(
                sat_dict["tle_filepath"],
                sat_dict["satellite_shortname"],
                sat_dict["satellite_name"],
                start_date,
                end_date,
                reference_date,
            )
            sat_secs_since, _, sat_lat_sim, sat_lon_sim = simulate_orbit(
                start_date,
                end_date,
                tle,
                propagation_sampling_interval,
                reference_date,
            )

            time, date, lat, lon = interpolate_orbit(
                start_date,
                end_date,
                sat_secs_since,
                sat_lat_sim,
                sat_lon_sim,
                interpolation_sampling_interval,
                reference_date,
            )
            orbit_dict.update(
                {
                    sat_dict["satellite_shortname"]: {
                        "lat": lat,
                        "lon": lon,
                        "time": time,
                        "time_datetime": date,
                        "satellite_name": tle.satellite_name,
                    }
                }
            )

        orbit = orbit_dict_to_xarray(
            orbit_dict,
            start_date,
            end_date,
            propagation_sampling_interval,
            interpolation_sampling_interval,
            reference_date,
        )

        return cls(
            orbit,
        )

    @classmethod
    def from_netcdf(cls, input_path: str):
        """Loads an Orbit object from a netcdf file. This file should have the appropriate structure, as exported by the `to_netcdf` method.

        :param input_path: The path of the file to load
        :type input_path: str
        :return: An orbit object with data corresponding to the content of the file.
        :rtype: Orbit
        """
        orbit_xarray = xr.open_dataset(
            input_path, engine="netcdf4", decode_times=True, decode_timedelta=True
        )
        orbit_xarray["reference_date"] = np.array(
            orbit_xarray["reference_date"], dtype="datetime64[s]"
        )
        orbit_xarray["time_datetime"][:] = np.array(
            orbit_xarray["time_datetime"], dtype="datetime64[s]"
        )
        reference_date: np.datetime64 = orbit_xarray["reference_date"].values
        orbit_xarray = orbit_xarray.assign_coords(
            time=np.array(
                [
                    datetime64_to_sec_since(
                        datetime, reference_date=reference_date
                    )
                    for datetime in orbit_xarray["time_datetime"].values
                ],
                dtype=np.float64,
            )
        )
        return cls(
            orbit_xarray,
        )

    def to_netcdf(self, output_path: str) -> None:
        """Saves the generated orbits to a netCDF file

        :param output_path: Path where to save the file
        :type output_path: str
        :return: None
        """
        satellites_part = "_".join(self.satellite_shortname)
        date_part = f"{np.datetime_as_string(self.start_date, unit = "D")}_{np.datetime_as_string(self.end_date, unit = "D")}"

        propagation_sampling_interval_timedelta: timedelta = self.propagation_sampling_interval.item()
        propagation_sampling_interval_float: float = propagation_sampling_interval_timedelta.total_seconds()

        interpolation_sampling_interval_timedelta: timedelta = self.interpolation_sampling_interval.item()
        interpolation_sampling_interval_float: float = interpolation_sampling_interval_timedelta.total_seconds()

        sampling_part = f"psi{propagation_sampling_interval_float}_isi{interpolation_sampling_interval_float}"
        filename = f"{date_part}_{sampling_part}_orbit_{satellites_part}.nc"

        # Save as netCDF4
        self.orbits.to_netcdf(os.path.join(output_path, filename))

    def plot(self, projection=ccrs.PlateCarree()) -> plt.Figure:
        """
        Plots the simulated orbits

        :param projection: cartopy.crs projection to use to plot, defaults to cartopy.crs.PlateCarree()
        """
        fig = plt.figure(figsize=(16 * CM, 9 * CM), dpi=400)
        ax = fig.add_subplot(1, 1, 1, projection=projection)
        ax.coastlines()
        ax.add_feature(cfeature.LAND)

        for sat_index, sat in enumerate(self.satellite_shortname):
            ax.scatter(
                self.orbits["lon"].isel(satellite=sat_index),
                self.orbits["lat"].isel(satellite=sat_index),
                label=SATELLITE_DICT[sat],
                transform=projection,
                s=0.5,
            )
        ax.legend(loc="lower right")
        return fig

    def __len__(self):
        """
        Number of positions simulated in the orbits

        :return: Number of times at which the orbits are simulated
        :rtype: int
        """
        return len(self.orbits["time"])

    def __eq__(self, value: object) -> bool:
        """Checks if two orbit objects are identical

        :param value: Orbit object to be compared to
        :type value: Orbit
        :return: Whether the two orbits were simulated with the same parameters and contain the same values for the simulated orbits
        :rtype: bool
        """
        if not isinstance(value, Orbit):
            return NotImplemented
        res = True
        res = res and bool(np.all(self.satellite_name == value.satellite_name))
        res = res and (self.start_date == value.start_date)
        res = res and (self.end_date == value.end_date)
        res = res and (
            self.propagation_sampling_interval == value.propagation_sampling_interval
        )
        res = res and (
            self.interpolation_sampling_interval
            == value.interpolation_sampling_interval
        )
        res = res and (self.orbits.equals(value.orbits))
        return res

    def __str__(self):
        res = f"""
Orbit object for satellites {[sat for sat in self.satellite_name]}.
Start date: {self.start_date}
End date: {self.end_date}
Propagation sampling interval: {self.propagation_sampling_interval}
Interpolation sampling interval: {self.interpolation_sampling_interval}
Reference date used to represent time in seconds since: {self.reference_date}
Number of simulated times: {len(self)}.
Created on {self.creation_date} using the version {self.version} of orbitx."""
        return res

    @property
    def satellite_name(self) -> List[str]:
        """
        :return: Satellites which the orbits are computed for
        :rtype: List[str]
        """
        return self._orbits.attrs["satellite_name"]

    @property
    def satellite_shortname(self) -> List[str]:
        """
        :return: Satellites which the orbits are computed for
        :rtype: List[str]
        """
        return self._orbits.attrs["satellite_shortname"]

    @property
    def start_date(self) -> npt.NDArray[np.datetime64]:
        """
        :return: Date from which the orbits are computed
        :rtype: np.datetime64
        """
        return np.array(
            sec_since_to_datetime64(
                self._orbits.attrs["start_date"], self.reference_date
            ),
            dtype="datetime64[s]",
        )

    @property
    def end_date(self) -> npt.NDArray[np.datetime64]:
        """
        :return: Date until which the orbits are computed
        :rtype: np.datetime64
        """
        return np.array(
            sec_since_to_datetime64(
                self._orbits.attrs["end_date"], self.reference_date
            ),
            dtype="datetime64[s]",
        )

    @property
    def propagation_sampling_interval(self) -> npt.NDArray[np.timedelta64]:
        """The time delta between each physics-based simulations of the satellite orbit"""
        return np.array(
            self._orbits.attrs["propagation_sampling_interval"], dtype="timedelta64[s]"
        )

    @property
    def interpolation_sampling_interval(self) -> npt.NDArray[np.timedelta64]:
        """The time delta between each interpolated position of the satellite orbit"""
        return np.array(
            self._orbits.attrs["interpolation_sampling_interval"],
            dtype="timedelta64[s]",
        )

    @property
    def version(self) -> str:
        """The version of orbitx used to create this object"""
        return self._orbits.attrs["version"]

    @property
    def creation_date(self) -> str:
        """The date when this object was created"""
        return self._orbits.attrs["creation_date"]

    @property
    def orbits(self) -> xr.Dataset:
        """The xarray containing all the satellite orbits.
        The structure of the array is as follows:

        .. code-block::

            <xarray.Dataset> Size: 415kB
            Dimensions:         (time: 8641, satellites: 2)
            Coordinates:
            * time            (time) float64 69kB 6.338e+08 6.338e+08 ... 6.339e+08
            * satellites      (satellites) <U2 16B 'S6' 'SA'
            Data variables:
                reference_date  datetime64[s] 8B 2000-01-01
                time_datetime   (time) datetime64[s] 69kB 2020-02-01 ... 2020-02-01T12:00:00
                lat             (time, satellites) float64 138kB 13.25 -74.64 ... -46.37
                lon             (time, satellites) float64 138kB 171.5 -124.0 ... -81.99
            Attributes:
                satellites:                       ['S6', 'SA']
                start_date:                       633830400.0
                end_date:                         633873600.0
                propagation_sampling_interval:    20
                interpolation_sampling_interval:  5

        """
        return self._orbits

    @property
    def reference_date(self) -> npt.NDArray[np.datetime64]:
        """The reference date used for the representation of time in seconds since reference date"""
        return self._orbits["reference_date"].values
