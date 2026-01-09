"""A python function to convert the temporary orbit dictionary to an xarray in the simulation pipeline"""

"""___Third-Party Modules___"""
from datetime import timedelta
import numpy as np
import numpy.typing as npt
from numpy import datetime64
from typing import Dict
import xarray as xr

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._date_utils import datetime64_to_sec_since
from orbitx import __version__

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
    """orbit_dict_to_xarray convert the temporary orbit dictionary to an xarray in the simulation pipeline

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

    .. code-bloc:: text

        Dimensions:         (time: ...)
        Coordinates:
        * time            (time) float64 ...kB ...
        Data variables:
            reference_date  datetime64[ns] 8B ...
            time_datetime   (time) datetime64[ns] ...kB ...
            lat1            (time) float64 ...kB ...
            lon1            (time) float64 ...kB ...
            lat2            (time) float64 ...kB ...
            lon2            (time) float64 ...kB ...
            ...
        Attributes:
            satellites:                       ['S6', 'SA', ...]
            start_date:                       ...
            end_date:                         ...
            propagation_sampling_interval:    ...
            interpolation_sampling_interval:  ...

    where `lat1` and `lon1` correspond to the lattitude and longitude of the first satellite mentioned in the `satellites` attribute (here S6), and so on for the other satellites.

    :param orbit_dict: A dictionnary containing simulated orbits for different satellites
    :type orbit_dict: Dict[str, Dict[str, npt.NDArray]]
    :param start_date: The start date of the simulated orbit
    :type start_date: datetime.datetime
    :param end_date: The end date of the simulated orbit
    :type end_date: datetime.datetime
    :param propagation_sampling_interval: The time interval in seconds between two successive physics simulations of the orbit
    :type propagation_sampling_interval: float
    :param interpolation_sampling_interval: The time interval in seconds between two successive interpolations
    :type interpolation_sampling_interval: float
    :param reference_date: The time variable of an orbit is given in seconds since a reference year. This variable let's you set this reference year, defaults to datetime.datetime(1970, 1, 1, 0, 0, 0)
    :type reference_date: datetime.datetime
    :return: An xarray containing the simulated orbits and metadata
    :rtype: xr.Dataset
    """
    satellite_shortname = list(orbit_dict.keys())
    satellite_name = [orbit_dict[key]["satellite_name"] for key in satellite_shortname]

    propagation_sampling_interval_timedelta: timedelta = (
        propagation_sampling_interval.item()
    )
    propagation_sampling_interval_int: int = int(
        propagation_sampling_interval_timedelta.total_seconds()
    )
    interpolation_sampling_interval_timedelta: timedelta = (
        interpolation_sampling_interval.item()
    )
    interpolation_sampling_interval_int: int = int(
        interpolation_sampling_interval_timedelta.total_seconds()
    )
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
            "start_date": datetime64_to_sec_since(
                start_date, reference_date=reference_date
            ),
            "end_date": datetime64_to_sec_since(
                end_date, reference_date=reference_date
            ),
            "propagation_sampling_interval": propagation_sampling_interval_int,
            "interpolation_sampling_interval": interpolation_sampling_interval_int,
            "version": __version__,
            "creation_date": str(datetime64("now")),
        },
    )

    orbit_xarray[f"lat"].attrs["units"] = "degrees"
    orbit_xarray[f"lon"].attrs["units"] = "degrees"
    orbit_xarray["time"].attrs["units"] = f"seconds since {reference_date}"

    for sat_index, satellite in enumerate(satellite_shortname):
        orbit_xarray["lat"][:, sat_index] = np.array(orbit_dict[satellite]["lat"])
        orbit_xarray["lon"][:, sat_index] = np.array(orbit_dict[satellite]["lon"])

    return orbit_xarray
