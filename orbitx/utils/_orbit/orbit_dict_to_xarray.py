"""A python function to convert the temporary orbit dictionary to an xarray in the simulation pipeline"""

"""___Third-Party Modules___"""
from datetime import timedelta
import numpy as np
import numpy.typing as npt
from numpy import datetime64
from typing import Dict, cast
import xarray as xr

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._date_utils import datetime64_to_sec_since

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "05/09/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"


def orbit_dict_to_xarray(
    orbit_dict: Dict[str, Dict[str, npt.NDArray]],
    start_date: np.datetime64,
    end_date: np.datetime64,
    propagation_sampling_interval: np.timedelta64,
    interpolation_sampling_interval: np.timedelta64,
    reference_date: np.datetime64 = np.datetime64("1970-01-01T00:00:00"),
) -> xr.Dataset:
    """convert the temporary orbit dictionary to an xarray in the simulation pipeline

    The input orbit dictionary should have a structure as follow:

    .. code-block:: text

        {
            "name_sat_1": {
                "lat": np.array([...], dtype= float)
                "lon": np.array([...], dtype= float)
                "time": np.array([...], dtype= float)
                "time_datetime": np.array([...], dtype= datetime.datetime)
            },
            "name_sat_2": {
                "lat": np.array([...], dtype= float)
                "lon": np.array([...], dtype= float)
                "time": np.array([...], dtype= float)
                "time_datetime": np.array([...], dtype= datetime.datetime)
            },
            ...
        }

    The variables `start_date`, `end_date`, `propagation_sampling_interval`, `interpolation_sampling_interval`, `reference_date` are provided for concervation of metadata.
    The returned xarray has the following structure:

    .. code-block:: text

        <xarray.Dataset> Size: 415kB
        Dimensions:         (time: 8641, satellite: 2)
        Coordinates:
        * time            (time) float64 69kB 6.338e+08 6.338e+08 ... 6.339e+08
        * satellite       (satellite) <U2 16B 'S6' 'SA'
        Data variables:
            reference_date  datetime64[s] 8B 2000-01-01
            time_datetime   (time) datetime64[s] 69kB 2020-02-01 ... 2020-02-01T12:00:00
            lat             (time, satellite) float64 138kB 13.25 -74.64 ... -46.37
            lon             (time, satellite) float64 138kB 171.5 -124.0 ... -81.99
        Attributes:
            satellite_shortname:              ['S6', 'SA']
            satellite_name:                   ['Sentinel-6', 'Saral-AltiKa']
            start_date:                       633830400.0
            end_date:                         633873600.0
            propagation_sampling_interval:    20
            interpolation_sampling_interval:  5
            version:                          1.0
            creation_date:                    2026-01-06T13:20:34

    Args:
        orbit_dict (Dict[str, Dict[str, npt.NDArray]]): A dictionnary containing simulated orbits for different satellites
        start_date (np.datetime64): The start date of the simulated orbit
        end_date (np.datetime64): The end date of the simulated orbit
        propagation_sampling_interval (np.timedelta64): The time interval in seconds between two successive physics simulations of the orbit
        interpolation_sampling_interval (np.timedelta64): The time interval in seconds between two successive interpolations
        reference_date (_type_, optional): The time variable of an orbit is given in seconds since a reference year. This variable let's you set this reference year. Defaults to np.datetime64("1970-01-01T00:00:00").

    Returns:
        xr.Dataset: An xarray containing the simulated orbits and metadata
    """
    satellite_shortname = list(orbit_dict.keys())
    satellite_name = [orbit_dict[key]["satellite_name"] for key in satellite_shortname]

    propagation_sampling_interval_timedelta: timedelta = cast(timedelta, propagation_sampling_interval.item())
    propagation_sampling_interval_int: int = int(propagation_sampling_interval_timedelta.total_seconds())
    interpolation_sampling_interval_timedelta: timedelta = cast(timedelta, interpolation_sampling_interval.item())
    interpolation_sampling_interval_int: int = int(interpolation_sampling_interval_timedelta.total_seconds())
    orbit_xarray = xr.Dataset(
        data_vars={
            "reference_date": (reference_date),
            "time_datetime": (
                ["time"],
                orbit_dict[satellite_shortname[0]]["time_datetime"],
            ),
            "lat": (
                ["time", "satellite"],
                np.empty(
                    (
                        len(orbit_dict[satellite_shortname[0]]["time"]),
                        len(satellite_shortname),
                    ),
                    dtype=float,
                ),
            ),
            "lon": (
                ["time", "satellite"],
                np.empty(
                    (
                        len(orbit_dict[satellite_shortname[0]]["time"]),
                        len(satellite_shortname),
                    ),
                    dtype=float,
                ),
            ),
        },
        coords={
            "time": orbit_dict[satellite_shortname[0]]["time"],
            "satellite": satellite_shortname,
        },
        attrs={
            "satellite_shortname": satellite_shortname,
            "satellite_name": satellite_name,
            "start_date": datetime64_to_sec_since(start_date, reference_date=reference_date),
            "end_date": datetime64_to_sec_since(end_date, reference_date=reference_date),
            "propagation_sampling_interval": propagation_sampling_interval_int,
            "interpolation_sampling_interval": interpolation_sampling_interval_int,
            "version": __version__,
            "creation_date": str(datetime64("now")),
        },
    )

    orbit_xarray["lat"].attrs["units"] = "degrees"
    orbit_xarray["lon"].attrs["units"] = "degrees"
    orbit_xarray["time"].attrs["units"] = f"seconds since {reference_date}"

    for sat_index, satellite in enumerate(satellite_shortname):
        orbit_xarray["lat"][:, sat_index] = np.array(orbit_dict[satellite]["lat"])
        orbit_xarray["lon"][:, sat_index] = np.array(orbit_dict[satellite]["lon"])

    return orbit_xarray
