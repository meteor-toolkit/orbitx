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
import netCDF4 as nc

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


class Matchups:
    """
    Class to find matchup events between multiple satellites
    """
    def __init__(
            self,
            satellites: List[str],
            start_date: datetime.datetime,
            end_date: datetime.datetime,
            time_diff_threshold: float,
            space_diff_threshold: float,
            orbit:Orbit,
            matchups: Dict[str, Dict[str, npt.NDArray]],
            check_before: Optional[bool]=False,
            check_after: Optional[bool]=False,
            has_land_ocean_mask: bool = False,
            reference_date:datetime.datetime = datetime.datetime(1970, 1, 1, 0, 0, 0)):
        
        self._satellites = satellites
        self._start_date = start_date
        self._end_date = end_date
        self._time_diff_threshold = time_diff_threshold
        self._space_diff_threshold = space_diff_threshold
        self._check_before = check_before
        self._check_after = check_after
        self._has_land_ocean_mask = has_land_ocean_mask
        self._orbit = orbit
        self._matchups = matchups
        self._reference_date = reference_date

    @classmethod
    def find_matchups(
        cls,
        satellites: List[str],
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        propagation_sampling_interval: float,
        interpolation_sampling_interval: float,
        space_diff_threshold: float,
        time_diff_threshold: float,
        check_before:Optional[bool]=False,
        check_after:Optional[bool]=False,
        has_land_ocean_mask:Optional[bool]=False,
        reference_date:datetime.datetime = datetime.datetime(1970, 1, 1, 0, 0, 0)
    ):
        """find_matchups Main generator for Matchups object

        Finds matchups between the satellites specified, between the start and end times specified.

        :param satellites: List of satellites short names for which the matchups must be found
        :type satellites: List[str]
        :param start_date: Date from which matchups must be found
        :type start_date: datetime.datetime
        :param end_date: Date before which matchups must be found
        :type end_date: datetime.datetime
        :param propagation_sampling_interval: The time resolution of the orbits simulation in seconds (the smaller, the more precise the simulation, but also the slower)
        :type propagation_sampling_interval: float
        :param interpolation_sampling_interval: The time resolution of the interpolation of the orbits (interpolating the simulated orbits)
        :type interpolation_sampling_interval: float
        :param space_diff_threshold: The maximal distance between satellites centers for an event to be called a matchup
        :type space_diff_threshold: float
        :param time_diff_threshold: The maximal time interval between the passing of two satellites for an event to be called a matchup
        :type time_diff_threshold: float
        :param check_before: Whether matchups where one of the satellites passed before the start date should be considered (useful when running successive time spans in separate threads so bordering matchups are not lost), defaults to False
        :type check_before: Optional[bool], optional
        :param check_after: Whether matchups where one of the satellites passed after the end date should be considered (useful when running successive time spans in separate threads so bordering matchups are not lost), defaults to False
        :type check_after: Optional[bool], optional
        :param has_land_ocean_mask: Whether a variable informing whether the satellites are above ocean or land (or coast if not all satellites are about the same time of surface) should be added, defaults to False
        :type has_land_ocean_mask: Optional[bool], optional
        :param reference_date: Time variables are provided as seconds from this reference date, defaults to datetime.datetime(1970, 1, 1, 0, 0, 0)
        :type reference_date: datetime.datetime, optional
        :return: A Matchups object containing information about all matchup events identified with the specified parameters.
        :rtype: Matchup
        """
        # simulate desired orbits
        orbit_start_date = start_date
        orbit_end_date = end_date
        if check_before:
            orbit_start_date = orbit_start_date - datetime.timedelta(seconds=time_diff_threshold)
        if check_after:
            orbit_end_date = orbit_end_date + datetime.timedelta(seconds=time_diff_threshold)
        orbit = Orbit.simulate(
            satellites=satellites,
            start_date=orbit_start_date,
            end_date=orbit_end_date,
            propagation_sampling_interval=propagation_sampling_interval,
            interpolation_sampling_interval=interpolation_sampling_interval,
            reference_date = reference_date
        )

        # Find the matches between generated orbits
        matchups = find_matches(
            orbit,
            time_diff_threshold,
            space_diff_threshold,
            start_date,
            end_date)
        # Add the land / ocean / coast masks
        if has_land_ocean_mask:
            matchups = get_land_ocean_mask(matchups)

        # Convert the dictionary of matchups to an xarray 
        attributes = {
            "satellites": satellites,
            "start_date": start_date,
            "end_date": end_date,
            "time_diff_threshold": time_diff_threshold,
            "space_diff_threshold": space_diff_threshold,
            "check_before": check_before,
            "check_after": check_after,
            "has_land_ocean_mask": has_land_ocean_mask,
            "interpolation_sampling_interval": orbit.interpolation_sampling_interval,
            "propagation_sampling_interval": orbit.propagation_sampling_interval
        }
        matchups = matchup_dict_to_xarray(matchups, attributes)

        # Create object instance
        result = cls(satellites,
        start_date,
        end_date,
        time_diff_threshold,
        space_diff_threshold,
        orbit,
        matchups,
        check_before,
        check_after,
        has_land_ocean_mask)
        return result
    
    @classmethod
    def from_netcdf(
        cls,
        input_path:str)->"Matchups":
        """from_netcdf Loads a Matchup object from a netCDF4 file

        Imports an object from a file generated by the `to_netcdf()` method.

        :param input_path: The full path of the file to be imported
        :type input_path: str
        :return: A Matchups object with the same value as the one that generated the imported file
        :rtype: Matchups
        """
        with nc.Dataset(input_path, "r") as matchup_file:
            reference_date = sec_since_to_datetime(float(matchup_file["reference_date"][:]), datetime.datetime(1970, 1, 1, 0, 0, 0))

            satellites = getattr(matchup_file, "satellites")
            start_date = sec_since_to_datetime(getattr(matchup_file, "start_date"), reference_date)
            end_date = sec_since_to_datetime(getattr(matchup_file, "end_date"), reference_date)
            time_diff_threshold = float(getattr(matchup_file, "time_diff_threshold"))
            space_diff_threshold = float(getattr(matchup_file, "space_diff_threshold"))
            check_before = getattr(matchup_file, "check_before")
            check_after = getattr(matchup_file, "check_after")
            has_land_ocean_mask = getattr(matchup_file, "has_land_ocean_mask")
            propagation_sampling_interval = getattr(matchup_file, "propagation_sampling_interval")
            interpolation_sampling_interval = getattr(matchup_file, "interpolation_sampling_interval")

            time = np.array(matchup_file["time"][:])
            
            matchups = xr.Dataset(
                data_vars = {
                    "reference_date": (float(matchup_file["reference_date"][:])),
                    "lat1": ("time", np.array(matchup_file["lat1"][:])),
                    "lon1": ("time", np.array(matchup_file["lon1"][:])),
                    "land_mask_1": ("time", np.array(matchup_file["land_mask_1"][:])),
                    "time_datetime": ("time", [sec_since_to_datetime(t) for t in time]),
                    "matchup_type": ("time", np.array(matchup_file["matchup_type"][:]))},
                coords = {"time": time},
                attrs={
                    "satellites": satellites,
                    "start_date": start_date,
                    "end_date": end_date,
                    "propagation_sampling_interval": propagation_sampling_interval,
                    "interpolation_sampling_interval": interpolation_sampling_interval
                }
            )
            for sat_index, _ in enumerate(satellites[1:]):
                new_sat_df = xr.Dataset(
                    data_vars = {
                        f"lat{sat_index + 2}": ("time", np.array(matchup_file[f"lat{sat_index + 2}"][:])),
                        f"lon{sat_index + 2}": ("time", np.array(matchup_file[f"lon{sat_index + 2}"][:])),
                        f"distance{sat_index + 2}": ("time", np.array(matchup_file[f"distance{sat_index + 2}"][:])),
                        f"land_mask_{sat_index + 2}": ("time", np.array(matchup_file[f"land_mask_{sat_index + 2}"][:])),
                        f"time{sat_index + 2}": ("time", np.array(matchup_file[f"time{sat_index + 2}"][:])),
                        f"time_datetime{sat_index + 2}": ("time", np.array(matchup_file[f"time_datetime{sat_index + 2}"][:])),
                        f"delay{sat_index + 2}": ("time", np.array(matchup_file[f"delay{sat_index + 2}"][:]))
                    },
                    coords = {"time": time}
                )
                matchups = matchups.merge(new_sat_df)
        loaded_orbit_start_date = start_date
        loaded_orbit_end_date = end_date
        if check_before:
            loaded_orbit_start_date = loaded_orbit_start_date - datetime.timedelta(seconds=time_diff_threshold)
        if check_after:
            loaded_orbit_end_date = loaded_orbit_end_date + datetime.timedelta(seconds=time_diff_threshold)
        loaded_orbit = Orbit.simulate(
            satellites=satellites,
            start_date=loaded_orbit_start_date,
            end_date=loaded_orbit_end_date,
            propagation_sampling_interval=propagation_sampling_interval,
            interpolation_sampling_interval=interpolation_sampling_interval,
            reference_date = reference_date
        )
        loaded_matchup = Matchups(
            satellites=satellites,
            start_date=start_date,
            end_date=end_date,
            time_diff_threshold=time_diff_threshold,
            space_diff_threshold=space_diff_threshold,
            orbit=loaded_orbit,
            matchups=matchups,
            check_before=check_before,
            check_after=check_after,
            has_land_ocean_mask=has_land_ocean_mask,
            reference_date=reference_date
            )
        return loaded_matchup
    
    def to_netcdf(
            self,
            output_path:str,
            reference_date:datetime.datetime = datetime.datetime(1970, 1, 1, 0, 0, 0))->None:
        """to_netcdf Exports a matchup object to a netcdf file

        The exported file is structured as follows:

        :param output_path: The directory where the file should be created (make sure the directory already exists). The file name is generated automatically
        :type output_path: str
        :param reference_date: The time variables in this file are stored as a float representing the number of seconds from this reference date, defaults to datetime.datetime(1970, 1, 1, 0, 0, 0)
        :type reference_date: datetime.datetime, optional
        """
        # Construct filename
        sat_part = "_".join(self.satellites)

        date_part = f"{self.start_date:%Y%m%d}_{self.end_date:%Y%m%d}"
        sampling_part = (
            f"psi{self.orbit.propagation_sampling_interval}_isi{self.orbit.interpolation_sampling_interval}"
        )
        matchup_part = f"c2c{self.space_diff_threshold}_tdt{self.time_diff_threshold}"
        filename = f"{date_part}_{sampling_part}_matchups_{sat_part}_{matchup_part}.nc"

        matchup_output_copy = self.matchups.copy()

        matchup_output_copy = matchup_output_copy.assign(reference_date = (datetime_to_sec_since(self.reference_date, datetime.datetime(1970, 1, 1, 0, 0, 0))))
        
        matchup_output_copy["reference_date"].attrs["units"] = "seconds"
        matchup_output_copy["reference_date"].attrs["description"] = f"Seconds since {datetime.datetime(1970, 1, 1, 0, 0, 0)}"

        matchup_output_copy.attrs["start_date"] = datetime_to_sec_since(self.start_date, reference_date)
        matchup_output_copy.attrs["end_date"] = datetime_to_sec_since(self.end_date, reference_date)
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
        delay = np.mean([self.matchups[i] for i in self.matchups if "delay" in str(i)])
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


    def __str__(self)->str:
        """__str__ Gives a short summary of the characteristics of a Matchup object

        The information displayed is the following:
        Matchup object with following attributes:
        Satellites considered
        Date from which matchups are looked for
        Date until which matchups are looked for
        Maximum time difference between members of a matchup (seconds)
        Maximum distance between members of a matchup (km)
        Are matchups in which on of the satellites appears before the start date considered?
        Are matchups in which on of the satellites appears after the end date considered?
        Has this matchup a land/ocean mask?
        Number of matchups found
        """
        result = f"""
Matchup object with following attributes:
Satellites considered: {self.satellites}
Date from which matchups are looked for: {self.start_date}
Date until which matchups are looked for: {self.end_date}
Maximum time difference between members of a matchup: {self.time_diff_threshold} (seconds)
Maximum distance between members of a matchup: {self.space_diff_threshold} (km)
Are matchups in which on of the satellites appears before the start date considered? {self.check_before}
Are matchups in which on of the satellites appears after the end date considered? {self.check_after}
Has this matchup a land/ocean mask? {self.has_land_ocean_mask}
Number of matchups found: {len(self)}
"""
        return result
    
    def __len__(self)->int:
        """__len__ Number of matchups in this object

        :return: Number of matchups in this object
        :rtype: int
        """
        return len(self.matchups["time"])
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
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date
    
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
    
    @property
    def reference_date(self):
        return self._reference_date
