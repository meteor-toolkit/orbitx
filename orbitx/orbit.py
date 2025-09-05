"""orbitx.orbit - class to simulate satellite orbits"""

"""___Third-Party Modules___"""
import datetime
from typing import List, Dict
import numbers
import os
import xarray as xr
import numpy.typing as npt
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import netCDF4 as nc

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._orbit.simulate_orbit import simulate_orbit
from orbitx.utils._orbit.interpolate_orbit import interpolate_orbit
from orbitx.utils._constants import CM, SATELLITE_DICT
from orbitx.utils._date_utils import datetime_to_sec_since, sec_since_to_datetime
from orbitx.tle import TLEInfo

"""___Authorship___"""
__author__ = __author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>"
]
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>"
]
__status__ = "Development"



__all__ = ["Orbit"]


class Orbit:
    """
    Class to simulate satellite orbits
    """

    def __init__(
            self,
            satellites: List[str],
            start_time: datetime.datetime,
            end_time: datetime.datetime,
            propagation_sampling_interval: numbers,
            interpolation_sampling_interval: numbers,
            orbit: Dict[str, Dict[str, npt.NDArray]]):
        
        self._satellites = satellites
        self._start_time = start_time
        self._end_time = end_time
        self._propagation_sampling_interval = propagation_sampling_interval
        self._interpolation_sampling_interval = interpolation_sampling_interval
        self._orbits = orbit

    def __len__(self):
        return len(self.orbits[self.satellites[0]]['lat'])
    
    def __eq__(self, value):
        if not isinstance(value, Orbit):
            return False
        res = True
        res = res and (self.satellites == value.satellites)
        res = res and (self.start_time == value.start_time)
        res = res and (self.end_time == value.end_time)
        res = res and (self.propagation_sampling_interval == value.propagation_sampling_interval)
        res = res and (self.interpolation_sampling_interval == value.interpolation_sampling_interval)
        res = res and (self.orbits == value.orbits)
        return res

    @classmethod
    def simulate(
        cls,
        satellites: List[str],
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        propagation_sampling_interval: numbers,
        interpolation_sampling_interval: numbers
    ):
        """
        Calculate the interpolated satellite orbits

        :param satellites: short name of satellites, e.g., S3A, LS8, etc.
        :param start_time: start time of simulation
        :param end_time: end time of simulation
        :param propagation_sampling_interval: propagation sampling interval in seconds
        :param interpolation_sampling_interval: interpolation sampling interval in seconds
        :return: dictionary containing lat, lon, and time of simulated orbit for the satellite of interest
        """
        tle = TLEInfo()
        orbit = {}
        for sat in satellites:
            line1, line2, tle_secs_since = tle.get_tle(sat, start_time, end_time)
            sat_secs_since, _, sat_lat_sim, sat_lon_sim = simulate_orbit(
                start_time,
                end_time,
                line1,
                line2,
                tle_secs_since,
                propagation_sampling_interval
            )

            lat, lon, time, date = interpolate_orbit(
                start_time,
                end_time,
                sat_secs_since,
                sat_lat_sim,
                sat_lon_sim,
                interpolation_sampling_interval,
            )
            orbit.update({sat: {"lat": lat, "lon": lon, "time": time, "time_datetime" : date}})
        return cls(
            satellites,
            start_time,
            end_time,
            propagation_sampling_interval,
            interpolation_sampling_interval,
            orbit)
    
    def to_netcdf(self, output_path:str, reference_date:datetime.datetime = datetime.datetime(1970, 1, 1, 0, 0, 0))->None:
        """to_netcdf Export orbits to netCDF

        Saves the generated orbits to a netCDF file

        :param output_path: Path where to save the file
        :type output_path: str
        :return: None
        """
        keys = list(self.orbits.keys())
        for i in range(len(keys)):

            # Construct filename
            sat = keys[i]
            date_part = f"{self.start_time:%Y%m%d}_{self.end_time:%Y%m%d}"
            sampling_part = f"psi{self.propagation_sampling_interval}_isi{self.interpolation_sampling_interval}"
            filename = f"{date_part}_{sampling_part}_orbit_{sat}.nc"

            # Save orbit as xr
            orbit_of_sat = xr.Dataset(
                {
                    "lat": ("time", self.orbits[sat]["lat"]),
                    "lon": ("time", self.orbits[sat]["lon"]),
                },
                coords={
                    "time": self.orbits[sat]["time"],
                },
                attrs={
                    "sat": sat,
                    "start_time": datetime_to_sec_since(self.start_time, reference_date),
                    "end_time": datetime_to_sec_since(self.end_time, reference_date),
                    "propagation_sampling_interval": self.propagation_sampling_interval,
                    "interpolation_sampling_interval": self.interpolation_sampling_interval,
                }
            )
            orbit_of_sat["time"].attrs["units"] = "seconds"
            orbit_of_sat["time"].attrs["description"] = f"Seconds since {reference_date}"

            # Save as netCDF4
            orbit_of_sat.to_netcdf(os.path.join(output_path, filename))
    
    @classmethod
    def from_netcdf(cls, input_path: str):

        satellites
        start_time
        end_time
        propagation_sampling_interval
        interpolation_sampling_interval
        orbits
        return orbit
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

        for sat in self.satellites:
            ax.scatter(
                self.orbits[sat]["lon"],
                self.orbits[sat]["lat"],
                label=SATELLITE_DICT[sat],
                transform=projection,
                s=.5
            )
        ax.legend(loc="lower right")
        return fig
    
    def __len__(self):
        return len(self.orbits[self.satellites[0]]["time"])

    def __str__(self):
        res = f"""
Orbit object for satellites {[sat for sat in self.satellites]}.
Start date: {self.start_time}
End date: {self.end_time}
Propagation sampling interval: {self.propagation_sampling_interval}
Interpolation sampling interval: {self.interpolation_sampling_interval}
Number of simulated times: {len(self)}"""
        return res

    @property
    def satellites(self):
        return self._satellites
    
    @property
    def start_time(self):
        return self._start_time
    
    @property
    def end_time(self):
        return self._end_time
    
    @property
    def propagation_sampling_interval(self):
        return self._propagation_sampling_interval
    
    @property
    def interpolation_sampling_interval(self):
        return self._interpolation_sampling_interval
    
    @property
    def orbits(self):
        return self._orbits