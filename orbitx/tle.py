"""orbitx.get_2LEs - module for accessing mission two line element data"""

"""___Third-Party Modules___"""
import numpy as np
import os
from typing import Tuple, List, Optional
import warnings
import xarray as xr
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._date_utils import datetime64_to_sec_since
from orbitx.utils._tle import (
    get_argument_perigee,
    get_ballistic_coefficient,
    get_catalog_number,
    get_classification,
    get_drag_term,
    get_eccentricity,
    get_element_set_number,
    get_inclination,
    get_launch_number,
    get_launch_piece,
    get_launch_year,
    get_mean_anomaly,
    get_mean_motion,
    get_revolution_number,
    get_right_ascension,
    get_second_derivative,
    get_tle_date,
    get_tle_path
) 
from orbitx.utils._constants import SATELLITE_DICT, CM



__author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
]

__all__ = ["TLE"]


class TLE:
    r"""
    Class to retrieve satellite TLEs.
    For more information on Two line elements, see the [Wikipedia page](https://en.wikipedia.org/wiki/Two-line_element_set)
    """
    def __init__(
            self,
            tle_xarray: xr.Dataset
        ):
        self._tle_xarray = tle_xarray
    
    @classmethod
    def from_sat_shortname(
        cls,
        satellite_shortname: str,
        start_date: np.datetime64,
        end_date: np.datetime64,
        reference_date: np.datetime64 = np.datetime64("1970-01-01T00:00:00")):
        """Generates a TLE object from the satellite shortname

        If the shortname provided is not supported by OrbitX a ValueError is raised and the used is invited to use a TLE file of their own.

        Args:
            satellite_shortname (str): The shortname of the satellite. Supported shortnames are the following:
            .. code-block:: text

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
            start_date (np.datetime64): The date from which the orbit needs to be simulated
            end_date (np.datetime64): The date until which the orbit needs to be simulated
            reference_date (np.datetime64, optional): The reference date used to represent dates as "seconds since". Defaults to np.datetime64("1970-01-01T00:00:00").

        Raises:
            ValueError: When the shortname provided is not supported by OrbitX

        Returns:
            TLE: A TLE Object
        """
        if not satellite_shortname in SATELLITE_DICT.keys():
            raise ValueError(f"No TLE file found for '{satellite_shortname}'. Consider using the `from_filepath` method with your own TLE file.")
        satellite_name = SATELLITE_DICT[satellite_shortname]
        # region Read TLE file.
        tle_filepath = get_tle_path(satellite_shortname)
            
        return cls.from_filepath(
            tle_filepath,
            satellite_shortname,
            satellite_name,
            start_date,
            end_date,
            reference_date
        )

    @classmethod
    def from_filepath(
        cls,
        tle_filepath: str,
        satellite_shortname: str,
        satellite_name: str,
        start_date: np.datetime64,
        end_date: np.datetime64,
        reference_date: np.datetime64 = np.datetime64("1970-01-01T00:00:00")
    ):
        """Generates a TLE object from a TLE file.

        Args:
            tle_filepath (str): The file containing the TLE
            satellite_shortname (str): The shortname of the satellite (e.g., S3A).
            satellite_name (str): The name of the satellite (e.g., Sentinel-3A).
            start_date (np.datetime64): The date from which the orbit needs to be simulated
            end_date (np.datetime64): The date until which the orbit needs to be simulated
            reference_date (np.datetime64, optional): The reference date used to represent dates as "seconds since". Defaults to np.datetime64("1970-01-01T00:00:00").
        """
        with open(tle_filepath, "r") as f:
            lines = np.array(f.read().splitlines())
        # endregion

        # region Access indexes of line-1 and line-2
        length = len(lines)
        if (
            len(lines[0]) < 69
        ):  # If the file includes the name of the mission at the beginning of each TLE, the name is at position 0, 3, ... (and we do not care about it)
            line_1_indexes = np.arange(
                1, length, 3
            )  # Line 1's are at position 1, 4, ...
            line_2_indexes = np.arange(
                2, length, 3
            )  # Line 2's are at position 2, 5, ...
        else:  # If the name is not included
            line_1_indexes = np.arange(
                0, length, 2
            )  # Line 1's are at position 0, 2, ...
            line_2_indexes = np.arange(
                1, length, 2
            )  # Line 2's are at position 1, 3, ...

        tle_line_1 = lines[line_1_indexes]  # list of all line 1s
        tle_line_2 = lines[line_2_indexes]  # list of all line 2s
        # endregion
        tle_dates = np.array([get_tle_date(line1) for line1 in tle_line_1], dtype = "datetime64[s]")
        tle_dates_seconds_since = np.array(
            [datetime64_to_sec_since(d, reference_date) for d in tle_dates]
        )
        tle_xarray = xr.Dataset(
            data_vars={
                "reference_date": (reference_date),
                "start_date": (start_date),
                "end_date": (end_date),
                "tle_date": ("tle_index", tle_dates),
                "reference_date_seconds_since1970": (datetime64_to_sec_since(reference_date, np.datetime64("1970-01-01T00:00:00"))),
                "start_date_seconds_since": (datetime64_to_sec_since(start_date, reference_date)),
                "end_date_seconds_since": (datetime64_to_sec_since(end_date, reference_date)),
                "tle_date_seconds_since": ("tle_index", tle_dates_seconds_since),
                "argument_perigee": ("tle_index", np.array([get_argument_perigee(line2) for line2 in tle_line_2], dtype = float)),
                "balistic_coefficient": ("tle_index", np.array([get_ballistic_coefficient(line1) for line1 in tle_line_1], dtype = float)),
                "drag_term": ("tle_index", np.array([get_drag_term(line1) for line1 in tle_line_1], dtype = float)),
                "eccentricity": ("tle_index", np.array([get_eccentricity(line2) for line2 in tle_line_2], dtype = float)),
                "element_set_number": ("tle_index", np.array([get_element_set_number(line1) for line1 in tle_line_1], dtype = float)),
                "inclination": ("tle_index", np.array([get_inclination(line2) for line2 in tle_line_2], dtype = float)),
                "mean_anomaly": ("tle_index", np.array([get_mean_anomaly(line2) for line2 in tle_line_2], dtype = float)),
                "mean_motion": ("tle_index", np.array([get_mean_motion(line2) for line2 in tle_line_2], dtype = float)),
                "revolution_number": ("tle_index", np.array([get_revolution_number(line2) for line2 in tle_line_2], dtype = float)),
                "right_ascension": ("tle_index", np.array([get_right_ascension(line2) for line2 in tle_line_2], dtype = float)),
                "second_derivative": ("tle_index", np.array([get_second_derivative(line1) for line1 in tle_line_1], dtype = float)),
            },
            coords={"tle_index": np.arange(len(tle_line_1))},
            attrs={
                "satellite_shortname": satellite_shortname, 
                "satellite_name": satellite_name,
                "catalog_number": get_catalog_number(tle_line_1[0]),
                "classification": get_classification(tle_line_1[0]),
                "launch_number": get_launch_number(tle_line_1[0]),
                "launch_piece": get_launch_piece(tle_line_1[0]),
                "launch_year": get_launch_year(tle_line_1[0]),
            },
        )

        # Filter time
        lower_bound_tle_time = [t for t in tle_xarray["tle_date"].values if t <= tle_xarray["start_date"].values]
        if len(lower_bound_tle_time) == 0:
            warnings.warn(
                f"""The oldest TLE file is more recent than the start time requested.
Oldest TLE file: {np.min(tle_xarray["start_date"].values)}
Start time requested: {tle_xarray["start_date"].values}"""
            )
        lower_bound_tle_time = (
            tle_xarray["start_date"].values
            if len(lower_bound_tle_time) == 0
            else np.max(lower_bound_tle_time)
        )

        upper_bound_tle_time = [t for t in tle_xarray["tle_date"].values if t >= tle_xarray["end_date"].values]
        if len(upper_bound_tle_time) == 0:
            warnings.warn(
                f"""The most recent TLE file is older than the end time requested.
Oldest TLE file: {np.max(tle_xarray["tle_date"].values)}
Start time requested: {tle_xarray["end_date"]}"""
            )
        upper_bound_tle_time = (
            tle_xarray["end_date"].values
            if len(upper_bound_tle_time) == 0
            else np.min(upper_bound_tle_time)
        )
        idx = [
            i
            for i, t_i in enumerate(tle_xarray["tle_date"])
            if (t_i >= lower_bound_tle_time) and (t_i < upper_bound_tle_time)
        ]

        if not idx:
            # If there is no TLE between start- and end-time, just get the one TLE which is closest to start_time
            closest_tle = np.argmin(np.abs(tle_xarray["tle_date"].values - tle_xarray["start_date"].values))

            tle_xarray = tle_xarray.isel(tle_index = closest_tle)

        else:
            # Filter TLE set
            tle_xarray = tle_xarray.isel(tle_index = idx)
            
        return cls(tle_xarray)


    @property
    def satellite_shortname(self)->str:
        r"""The short name associated with the satellite (e.g., CS2)."""
        return self._tle_xarray.attrs["satellite_name"]

    @property
    def satellite_name(self)->str:
        r"""The name associated with the satellite (e.g., Cryosat-2)."""
        return self._tle_xarray.attrs["satellite_name"]
    
    @property
    def satellite_catalog_number(self)->str:
        r"""This is the catalog number USSPACECOM has designated for this object."""
        return self._tle_xarray.attrs["catalog_number"]

    @property
    def classification(self)->str:
        r"""Classification (U: unclassified, C: classified, S: secret)"""
        return self._tle_xarray.attrs["classification"]
    
    @property
    def launch_year(self)->int:
        r"""Year in which the satellite was launched"""
        return self._tle_xarray.attrs["launch_year"]
    
    @property
    def launch_number(self)->int:
        r"""Number of this launch in the year (how many launches happened this year before this one, plus one)"""
        return self._tle_xarray.attrs["launch_number"]
    
    @property
    def launch_piece(self)->str:
        r"""Index of this object in the launch (in a launch that results in three objects orbiting, the second one is indexed B)"""
        return self._tle_xarray.attrs["launch_piece"]

    @property
    def tle_date(self)->List[np.datetime64]:
        r"""Date corresponding to this TLE"""
        return self._tle_xarray["tle_date"].values

    @property
    def ballistic_coefficient(self)->List[float]:
        r"""Also called the first derivative of mean motion, the ballistic coefficient is the daily rate of change in the number of revs the object completes each day, divided by 2.
        Units are :math:`revs \cdot day^{-1}`.
        This is "catch all" drag term used in the Simplified General Perturbations (SGP4) USSPACECOM predictor.

        Description adapted from `spaceflight.nasa`_
        
        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html"""
        return self._tle_xarray["ballistic_coefficient"].values
    
    @property
    def second_derivative(self)->List[float]:
        r"""The second derivative of mean motion is a second order drag term in the Simplified General Perturbations (SGP4) predictor used to model terminal orbit decay.
        It measures the second time derivative in daily mean motion, divided by 6.
        Units are :math:`revs\cdot day^{-3}`.

        Description adapted from `spaceflight.nasa`_
        
        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html"""
        return self._tle_xarray["second_derivative"].values
    
    @property
    def drag_term(self)->List[float]:
        r"""
        Also called the radiation pressure coefficient (or BSTAR), the parameter is another drag term in the SGP4 predictor.
        Units are earth radii^-1.
        The last two characters define an applicable power of 10.
        Do not confuse this parameter with "B-Term", the USSPACECOM special perturbations factor of drag coefficient, multiplied by reference area, divided by weight.
        Description adapted from `spaceflight.nasa`_
        
        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html"""
        return self._tle_xarray["drag_term"].values
    
    @property
    def element_set_number(self)->List[int]:
        r"""
        The element set number is a running count of all 2 line element sets generated by USSPACECOM for this object (in this example, 529).
        Since multiple agencies perform this function, numbers are skipped on occasion to avoid ambiguities.
        The counter should always increase with time until it exceeds 999, when it reverts to 1.
        Description adapted from `spaceflight.nasa`_
        
        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html"""
        return self._tle_xarray["element_set_number"].values
    
    
    @property
    def inclination(self)->List[float]:
        r"""
        The angle between the equator and the orbit plane. The value provided is the TEME mean inclination. 

        Description adapted from `spaceflight.nasa`_
        
        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html"""
        return self._tle_xarray["inclination"].values
    
    @property
    def right_ascension(self)->List[float]:
        r"""
        The angle between vernal equinox and the point where the orbit crosses the equatorial plane (going north).
        The value provided is the TEME mean right ascension of the ascending node. 

        Description adapted from `spaceflight.nasa`_
        
        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html"""
        return self._tle_xarray["right_ascension"].values
    
    @property
    def eccentricity(self)->List[float]:
        r"""
        A constant defining the shape of the orbit (0=circular, Less than 1=elliptical).
        The value provided is the mean eccentricity.

        Description adapted from `spaceflight.nasa`_
        
        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html"""
        return self._tle_xarray["eccentricity"].values
    
    @property
    def argument_perigee(self)->List[float]:
        r"""
        The angle between the ascending node and the orbit's point of closest approach to the earth (perigee).
        The value provided is the TEME mean argument of perigee. 

        Description adapted from `spaceflight.nasa`_
        
        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html"""
        return self._tle_xarray["argument_perigee"].values
    
    @property
    def mean_anomaly(self)->List[float]:
        r"""The angle, measured from perigee, of the satellite location in the orbit referenced to a circular orbit with radius equal to the semi-major axis. 

        Description adapted from `spaceflight.nasa`_
        
        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html"""
        return self._tle_xarray["mean_anomaly"].values
    
    @property
    def mean_motion(self)->List[float]:
        r"""The value is the mean number of orbits per day the object completes.
        There are 8 digits after the decimal, leaving no trailing space(s) when the following element exceeds 9999. 
        
        Description adapted from `spaceflight.nasa`_
        
        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html"""
        return self._tle_xarray["mean_motion"].values
    
    @property
    def revolution_number(self)->List[int]:
        r"""The orbit number at Epoch Time.
        This time is chosen very near the time of true ascending node passage as a matter of routine.
        
        Description adapted from `spaceflight.nasa`_
        
        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html"""
        return self._tle_xarray["revolution_number"].values
    
    
    @property
    def reference_date(self)->np.datetime64:
        r"""The xarray containing the information about all TLE's for this satellite"""
        return self._tle_xarray["reference_date"].values
    
    
    @property
    def start_date(self)->np.datetime64:
        r"""The xarray containing the information about all TLE's for this satellite"""
        return self._tle_xarray["start_date"].values
    
    
    @property
    def end_date(self)->np.datetime64:
        r"""The xarray containing the information about all TLE's for this satellite"""
        return self._tle_xarray["end_date"].values
    
    
    @property
    def reference_date_seconds_since1970(self)->int:
        r"""The xarray containing the information about all TLE's for this satellite"""
        return self._tle_xarray["reference_date_seconds_since1970"].values
    
    
    @property
    def start_date_seconds_since(self)->int:
        r"""The xarray containing the information about all TLE's for this satellite"""
        return self._tle_xarray["start_date_seconds_since"].values
    
    
    @property
    def end_date_seconds_since(self)->int:
        r"""The xarray containing the information about all TLE's for this satellite"""
        return self._tle_xarray["end_date_seconds_since"].values
    
    
    @property
    def tle_date_seconds_since(self)->List[int]:
        r"""The xarray containing the information about all TLE's for this satellite"""
        return self._tle_xarray["tle_date_seconds_since"].values
    
    
    @property
    def tle_xarray(self)->xr.Dataset:
        r"""The xarray containing the information about all TLE's for this satellite"""
        return self._tle_xarray
    
if __name__ == "__main__":
    pass
