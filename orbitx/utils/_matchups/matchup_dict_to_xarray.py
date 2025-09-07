"""A python function that finds the matchups in orbits"""

"""___Third-Party Modules___"""
import numpy as np
import numpy.typing as npt
import xarray as xr
from typing import Dict
"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._date_utils import datetime64_to_sec_since
"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"

_get_range = np.vectorize(lambda *delay: max(delay) - min(delay))

def matchup_dict_to_xarray(
        matchups_dict:Dict[str, Dict[str, npt.NDArray]],
        attributes:Dict,
        reference_date: np.datetime64) -> xr.Dataset:
    """
    Convert matchup dictionary to xarray dataset. For matchup events between more than two satellites, matchups
    are filtered to only those where all satellites are within the desired time threshold (specified in attrs).

    The input matchup information dictionary is generated in Matchups.matchup and is of form:

    .. code-block:: bash

        matchups_dict = {"S2A_LS8":
                            {
                                "lat1": npt.NDArray,
                                "lon1": npt.NDArray,
                                "lat2": npt.NDArray,
                                "lon2": npt.NDArray,
                                "delay": npt.NDArray,
                                "time": npt.NDArray,
                                "time_datetime": npt.NDArray,
                                "distance": npt.NDArray,
                            },
                        }

    where in this case "S2A" is the first satellite used for the comparison and "LS8" is the second
    satellite.
    Optionally, there can be entries for "land_mask_1", "land_mask_2", "matchup_type" if the land/ocean mask was requested.
    Matchups between multiple satellites would have matchup_info dictionaries that look like:

    .. code-block:: bash

        matchup_info = {"S2A_LS8":
                            {...},
                        "S2A_S3A":
                            {...},
                        }

    where the ellipse (...) contains the same keys as the example above.

    The input `attributes` dictionary provides metadata about how the matchups were generated and is of the form:

    .. code-block:: bash

        attributes = {
            "satellites": satellites,
            "start_date": start_date,
            "end_date": end_date,
            "time_diff_threshold": time_diff_threshold,
            "space_diff_threshold": space_diff_threshold,
            "check_before": check_before,
            "check_after": check_after,
            "has_land_ocean_mask": has_land_ocean_mask,
        }

    :param matchups_dict: matchup information dict containing lat, lon, distance and time info for matchup events
    :param attrs: dictionary of attributes to be added to the output dataset, must include "time_threshold"
    """

    ds_list = [
        xr.Dataset(
            data_vars = {
                "reference_date": (reference_date),
                "time_datetime": ("time", matchups_dict[key]["time_datetime"]),
                "lat1": ("time", matchups_dict[key]["lat1"]),
                "lon1": ("time", matchups_dict[key]["lon1"]),
                "lat2": ("time", matchups_dict[key]["lat2"]),
                "lon2": ("time", matchups_dict[key]["lon2"]),
                "distance": ("time", matchups_dict[key]["distance"]),
                "time2": ("time", matchups_dict[key]["time2"]),
                "time_datetime2": ("time", matchups_dict[key]["time_datetime2"]),
                "delay": ("time", matchups_dict[key]["delay"]),
            },
            coords = {"time": matchups_dict[key]["time"]},
            attrs={
                "satellites": attributes["satellites"],
                "start_date": datetime64_to_sec_since(attributes["start_date"], reference_date),
                "end_date": datetime64_to_sec_since(attributes["end_date"], reference_date),
                "propagation_sampling_interval": attributes["propagation_sampling_interval"].item().total_seconds(),
                "interpolation_sampling_interval": attributes["interpolation_sampling_interval"].item().total_seconds(),
                "time_diff_threshold": attributes["time_diff_threshold"].item().total_seconds(),
                "space_diff_threshold": attributes["space_diff_threshold"],
                "check_before": attributes["check_before"],
                "check_after": attributes["check_after"],
                "has_land_ocean_mask": attributes["has_land_ocean_mask"]
            }
        )
        for key in matchups_dict.keys()
    ]

    times = ds_list[0].time.data
    for i in range(len(ds_list)):
        times = list(set(ds_list[i].time.data).intersection(times))
        ds_list[i] = ds_list[i].rename(
            {
                "lat2": f"lat{i + 2}",
                "lon2": f"lon{i + 2}",
                "time2": f"time{i + 2}",
                "time_datetime2": f"time_datetime{i + 2}",
                "delay": f"delay{i + 2}",
                "distance": f"distance{i + 2}",
            }
        )
        ds_list[i][f"time{i + 2}"].attrs["units"] = f"seconds since {reference_date}"
        ds_list[i][f"time"].attrs["units"] = f"seconds since {reference_date}"
        ds_list[i][f"distance{i + 2}"].attrs["units"] = "km"
        ds_list[i][f"lat{i + 2}"].attrs["units"] = "degrees"
        ds_list[i][f"lon{i + 2}"].attrs["units"] = "degrees"

    merged_ds = xr.merge(
        [ds.sel(time=times) for ds in ds_list], combine_attrs="no_conflicts"
    )

    merged_ds = merged_ds.isel(
        time=np.where(
            _get_range(*[merged_ds[i] for i in merged_ds if "delay" in str(i)])
            < attributes["time_diff_threshold"]
        )[0]
    )
    for sat_index, _ in enumerate(merged_ds.attrs["satellites"][1:]):
        merged_ds[f"time{sat_index + 2}"].attrs["units"] = f"seconds since {reference_date}"

    merged_ds = merged_ds.assign(
        variables={
            "reference_date": (reference_date)
            }
        )

    merged_ds["time"].attrs["units"] = f"seconds since {reference_date}"
    
    merged_ds["lat1"].attrs["units"] = "degrees"
    merged_ds["lon1"].attrs["units"] = "degrees"
    
    merged_ds.attrs["start_date"] = datetime64_to_sec_since(attributes["start_date"], reference_date)
    merged_ds.attrs["end_date"] = datetime64_to_sec_since(attributes["end_date"], reference_date)
    merged_ds.attrs['check_before'] = str(merged_ds.attrs['check_before'])
    merged_ds.attrs['check_after'] = str(merged_ds.attrs['check_after'])
    merged_ds.attrs['has_land_ocean_mask'] = str(merged_ds.attrs['has_land_ocean_mask'])
    return merged_ds