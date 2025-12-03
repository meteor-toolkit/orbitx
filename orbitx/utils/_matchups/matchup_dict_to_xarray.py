"""A python function that finds the matchups in orbits"""

"""___Third-Party Modules___"""
import numpy as np
import xarray as xr
from typing import Dict, List

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._date_utils import datetime64_to_sec_since
from orbitx.utils._matchups.get_dist import get_distance

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"

_get_range = np.vectorize(lambda *delay: max(delay) - min(delay))


def matchup_dict_to_xarray(
    matchups_list: List[xr.Dataset],
    attributes: Dict,
    reference_date: np.datetime64,
) -> xr.Dataset:
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
    indices = matchups_list[0]["matchup_index"].values
    for i in range(len(matchups_list)):
        indices = list(set(matchups_list[i]["matchup_index"].values).intersection(indices))


    merged_ds = xr.merge(
        [ds.sel(matchup_index=indices) for ds in matchups_list], combine_attrs="no_conflicts"
    )
    satellite_shortnames = merged_ds["satellite"]
    num_sats = len(satellite_shortnames)
    for sat_0_ind in range(num_sats - 1):
        sat_0 = merged_ds["satellite"][sat_0_ind].values
        for sat_1_ind in range(sat_0_ind + 1, num_sats):
            sat_1 = merged_ds["satellite"][sat_1_ind].values
            satellite_pair = f"{sat_0}_{sat_1}"
            s0_lat = merged_ds["lat"].sel(satellite = sat_0).values
            s0_lon = merged_ds["lon"].sel(satellite = sat_0).values
            s1_lat = merged_ds["lat"].sel(satellite = sat_1).values
            s1_lon = merged_ds["lon"].sel(satellite = sat_1).values
            position = np.array([s0_lat, s0_lon, s1_lat, s1_lon]).transpose()
            
            distance = get_distance(*tuple(position.transpose()))
            merged_ds["delay"].loc[dict(satellite_pair = satellite_pair)] = merged_ds["time"].sel(satellite = sat_0) - merged_ds["time"].sel(satellite = sat_1)
            merged_ds["distance"].loc[dict(satellite_pair = satellite_pair)] = distance

    # merged_ds = merged_ds.assign(variables={"reference_date": (reference_date)})

    # merged_ds["time"].attrs["units"] = f"seconds since {reference_date}"

    # merged_ds["lat1"].attrs["units"] = "degrees"
    # merged_ds["lon1"].attrs["units"] = "degrees"

    # merged_ds.attrs["start_date"] = datetime64_to_sec_since(
    #     attributes["start_date"], reference_date
    # )
    # merged_ds.attrs["end_date"] = datetime64_to_sec_since(
    #     attributes["end_date"], reference_date
    # )
    # merged_ds.attrs["check_before"] = str(merged_ds.attrs["check_before"])
    # merged_ds.attrs["check_after"] = str(merged_ds.attrs["check_after"])
    # merged_ds.attrs["has_land_ocean_mask"] = str(merged_ds.attrs["has_land_ocean_mask"])
    return merged_ds
