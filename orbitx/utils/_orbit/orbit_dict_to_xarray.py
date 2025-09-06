"""A python function to convert the temporary orbit dictionary to an xarray in the simulation pipeline"""

"""___Third-Party Modules___"""
import datetime
import numpy as np
import numpy.typing as npt
from typing import Tuple, Any, Dict
from scipy.interpolate import interp1d
import xarray as xr

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._date_utils import datetime_to_sec_since
"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "05/09/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"

def orbit_dict_to_xarray(
        orbit_dict:Dict[str, Dict[str, npt.NDArray]],
        start_date:datetime.datetime,
        end_date:datetime.datetime,
        propagation_sampling_interval:float,
        interpolation_sampling_interval:float,
        reference_date:datetime.datetime
        )->xr.Dataset:
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
    satellites = list(orbit_dict.keys())
    orbit_xarray = xr.Dataset(
        data_vars = {
            "reference_date": (datetime_to_sec_since(reference_date, datetime.datetime(1970, 1, 1, 0, 0, 0))),
            "time_datetime": ("time", orbit_dict[satellites[0]]["time_datetime"]),
        },
        coords = {"time": orbit_dict[satellites[0]]["time"]},
        attrs={
            "satellites": satellites,
            "start_date": datetime_to_sec_since(start_date, reference_date),
            "end_date": datetime_to_sec_since(end_date, reference_date),
            "propagation_sampling_interval": propagation_sampling_interval,
            "interpolation_sampling_interval": interpolation_sampling_interval
        }
    )
    for sat_index, satellite in enumerate(satellites):
        new_sat_df = xr.Dataset(
            data_vars = {
                f"lat{sat_index + 1}": ("time", np.array(orbit_dict[satellite]["lat"])),
                f"lon{sat_index + 1}": ("time", np.array(orbit_dict[satellite]["lon"]))
            },
            coords = {"time": orbit_dict[satellites[0]]["time"]}
        )
        orbit_xarray = orbit_xarray.merge(new_sat_df)

    orbit_xarray["time"].attrs["units"] = f"seconds since {reference_date:%Y-%m-%d}"
    orbit_xarray["reference_date"].attrs["units"] = "seconds since 1970-01-01"
    return orbit_xarray