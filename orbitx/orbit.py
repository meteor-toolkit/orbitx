"""orbitx.orbit - class to simulate satellite orbits"""

"""___Third-Party Modules___"""
import datetime
from typing import List
import numbers
import os
import xarray as xr

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._orbit import simulate_orbit, interpolate_orbit
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
            interpolation_sampling_interval: numbers):
        
        self._satellites = satellites
        self._start_time = start_time
        self._end_time = end_time
        self._propagation_sampling_interval = propagation_sampling_interval
        self._interpolation_sampling_interval = interpolation_sampling_interval
        self._orbits = dict()
        self.run()

    def __len__(self):
        return len(self.orbits[self.satellites[0]]['lat'])

    def run(
        self
    ) -> None:
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
        sat_interp_dict = {}
        for sat in self.satellites:
            line1, line2, secs_since = tle.get_tle(sat, self.start_time, self.end_time)
            sat_secs_since, sat_lat_sim, sat_lon_sim = simulate_orbit(
                self.start_time,
                self.end_time,
                line1,
                line2,
                secs_since,
                self.propagation_sampling_interval
            )
            lat, lon, time = interpolate_orbit(
                sat_secs_since,
                sat_lat_sim,
                sat_lon_sim,
                self.interpolation_sampling_interval,
            )
            sat_interp_dict.update({sat: {"lat": lat, "lon": lon, "time": time}})
        self._orbits = sat_interp_dict
        return
    
    def to_netcdf(self, output_path:str)->None:
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

            time_datetime = [datetime.datetime(1970, 1, 1 ) + datetime.timedelta(seconds=self.orbits[sat]["time"][j]) for j in range(len(self.orbits[sat]["time"]))]

            # Save orbit as xr
            orbit_of_sat = xr.Dataset(
                {
                    "lat": ("time", self.orbits[sat]["lat"]),
                    "lon": ("time", self.orbits[sat]["lon"]),
                },
                coords={
                    "time": time_datetime,
                },
                attrs={
                    "sat": sat,
                    "start_time": self.start_time,
                    "end_time": self.end_time,
                    "propagation_sampling_interval": self.propagation_sampling_interval,
                    "interpolation_sampling_interval": self.interpolation_sampling_interval,
                }
            )
            orbit_of_sat["time"].attrs["description"] = "UTC time from Unix timestamp"

            # Add seconds since 2000 for altimetry applications
            offset = (datetime.datetime(2000, 1, 1) - datetime.datetime(1970, 1, 1)).total_seconds()
            seconds_since_2000 = [t - offset for t in self.orbits[sat]["time"]]
            orbit_of_sat["seconds_since_2000"] = ("time", seconds_since_2000)
            orbit_of_sat["seconds_since_2000"].attrs["units"] = "seconds"
            orbit_of_sat["seconds_since_2000"].attrs["description"] = "Seconds since 2000-01-01T00:00:00 UTC"

            # Save as netCDF4
            orbit_of_sat.to_netcdf(os.path.join(output_path, filename))

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