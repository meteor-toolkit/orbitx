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

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._orbit.simulate_orbit import simulate_orbit
from orbitx.utils._orbit.interpolate_orbit import interpolate_orbit
from orbitx.utils._orbit.orbit_dict_to_xarray import orbit_dict_to_xarray
from orbitx.utils._constants import CM, SATELLITE_DICT
from orbitx.utils._date_utils import datetime64_to_sec_since, sec_since_to_datetime64
from orbitx.tle import TLEInfo

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
        satellites: List[str],
        start_date: np.datetime64,
        end_date: np.datetime64,
        propagation_sampling_interval: np.timedelta64,
        interpolation_sampling_interval: np.timedelta64,
        reference_date: np.datetime64,
        orbit: Dict[str, Dict[str, npt.NDArray]],
    ):

        self._satellites = satellites
        self._start_date = start_date
        self._end_date = end_date
        self._propagation_sampling_interval = propagation_sampling_interval
        self._interpolation_sampling_interval = interpolation_sampling_interval
        self._reference_date = reference_date
        self._orbits = orbit

    @classmethod
    def simulate(
        cls,
        satellites: List[str],
        start_date: np.datetime64,
        end_date: np.datetime64,
        propagation_sampling_interval: np.timedelta64,
        interpolation_sampling_interval: np.timedelta64,
        reference_date: np.timedelta64 = np.datetime64("1970-01-01T00:00:00"),
    ):
        """simulate Main generator for the Orbit class

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

        The simulation starts by finding relevant Two Line Elements (TLE).
        The simulation then does a *Physics* simulation of the orbits (propagation step) from the TLEs at the requested resolution `propagation_sampling_interval`.
        Finally the simulation performs an interpolation of the propagated orbits at the requested resolution `interpolation_sampling_interval`

        :param satellites: List of short names for satellites.
        :type satellites: List[str]
        :param start_date: The date from which the orbits are to be simulated
        :type start_date: np.datetime64
        :param end_date: The date until which the orbits are to be simulated
        :type end_date: np.datetime64
        :param propagation_sampling_interval: The time interval in seconds between two successive physics simulations of the orbit
        :type propagation_sampling_interval: np.timedelta64
        :param interpolation_sampling_interval: The time interval in seconds between two successive interpolations
        :type interpolation_sampling_interval: np.timedelta64
        :param reference_date: The time variable of an orbit is given in seconds since a reference year. This variable let's you set this reference year, defaults to np.timedelta64('1970-01-01T00:00:00')
        :type reference_date: np.datetime64, optional
        :return: An Orbit object with the requested parameters. See the Orbit class documentation for details about their structure
        :rtype: Orbit
        """

        tle = TLEInfo()
        orbit_dict = {}
        for sat in satellites:
            line1, line2, tle_secs_since = tle.get_tle(sat, start_date, end_date)
            sat_secs_since, _, sat_lat_sim, sat_lon_sim = simulate_orbit(
                start_date,
                end_date,
                line1,
                line2,
                tle_secs_since,
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
                {sat: {"lat": lat, "lon": lon, "time": time, "time_datetime": date}}
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
            satellites,
            start_date,
            end_date,
            propagation_sampling_interval,
            interpolation_sampling_interval,
            reference_date,
            orbit,
        )

    @classmethod
    def from_netcdf(cls, input_path: str):

        orbit_xarray = xr.open_dataset(
            input_path, engine="netcdf4", decode_times=True, decode_timedelta=True
        )
        satellites = orbit_xarray.attrs["satellites"]
        reference_date = np.array(
            [orbit_xarray["reference_date"].values], dtype="datetime64[s]"
        )[0]
        time_datetime = np.array(
            orbit_xarray[f"time_datetime"].values, dtype="datetime64[s]"
        )
        orbit_xarray = orbit_xarray.assign_coords(
            coords={
                "time": [
                    datetime64_to_sec_since(date, reference_date)
                    for date in time_datetime
                ]
            }
        )

        orbit_xarray = orbit_xarray.assign(
            variables={
                "reference_date": (reference_date),
                "time_datetime": ("time", time_datetime),
            }
        )

        orbit_xarray["time"].attrs["units"] = f"seconds since {reference_date}"

        start_date = sec_since_to_datetime64(
            orbit_xarray.attrs["start_date"], reference_date=reference_date
        )
        end_date = sec_since_to_datetime64(
            orbit_xarray.attrs["end_date"], reference_date=reference_date
        )
        propagation_sampling_interval = np.array(
            [orbit_xarray.attrs["propagation_sampling_interval"]],
            dtype="timedelta64[s]",
        )[0]
        interpolation_sampling_interval = np.array(
            [orbit_xarray.attrs["interpolation_sampling_interval"]],
            dtype="timedelta64[s]",
        )[0]
        return cls(
            satellites,
            start_date,
            end_date,
            propagation_sampling_interval,
            interpolation_sampling_interval,
            reference_date,
            orbit_xarray,
        )

    def to_netcdf(self, output_path: str) -> None:
        """to_netcdf Export orbits to netCDF

        Saves the generated orbits to a netCDF file

        :param output_path: Path where to save the file
        :type output_path: str
        :return: None
        """
        satellites_part = "_".join(self.satellites)
        date_part = f"{np.datetime_as_string(self.start_date, unit = "D")}_{np.datetime_as_string(self.end_date, unit = "D")}"
        sampling_part = f"psi{self.propagation_sampling_interval.item().total_seconds()}_isi{self.interpolation_sampling_interval.item().total_seconds()}"
        filename = f"{date_part}_{sampling_part}_orbit_{satellites_part}.nc"

        # Save as netCDF4
        self.orbits.to_netcdf(os.path.join(output_path, filename))

    def plot(self, projection=ccrs.PlateCarree()) -> plt.Figure:
        """
        Plot the matchup dataset generated from orbitx.interface.return_matchups

        :param projection: cartopy.crs projection to use to plot, defaults to cartopy.crs.PlateCarree()
        """
        fig = plt.figure(figsize=(16 * CM, 9 * CM), dpi=400)
        ax = fig.add_subplot(1, 1, 1, projection=projection)
        ax.coastlines()
        ax.add_feature(cfeature.LAND)

        for sat_index, sat in enumerate(self.satellites):
            ax.scatter(
                self.orbits[f"lon{sat_index + 1}"],
                self.orbits[f"lat{sat_index + 1}"],
                label=SATELLITE_DICT[sat],
                transform=projection,
                s=0.5,
            )
        ax.legend(loc="lower right")
        return fig

    def __len__(self):
        """__len__
        :return: Number of times at which the orbits are simulated
        :rtype: int
        """
        return len(self.orbits["time"])

    def __eq__(self, value: "Orbit") -> bool:
        """__eq__ Checks if two orbit objects are identical

        :param value: Orbit object to be compared to
        :type value: Orbit
        :return: Whether the two orbits were simulated with the same parameters and contain the same values for the simulated orbits
        :rtype: bool
        """
        if not isinstance(value, Orbit):
            return False
        res = True
        res = res and (self.satellites == value.satellites)
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
Orbit object for satellites {[sat for sat in self.satellites]}.
Start date: {self.start_date}
End date: {self.end_date}
Propagation sampling interval: {self.propagation_sampling_interval}
Interpolation sampling interval: {self.interpolation_sampling_interval}
Reference date used to represent time in seconds since: {self.reference_date}
Number of simulated times: {len(self)}"""
        return res

    @property
    def satellites(self):
        return self._satellites

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    @property
    def propagation_sampling_interval(self):
        return self._propagation_sampling_interval

    @property
    def interpolation_sampling_interval(self):
        return self._interpolation_sampling_interval

    @property
    def orbits(self):
        return self._orbits

    @property
    def reference_date(self):
        return self._reference_date
