"""A python function that finds the matchups in orbits"""

"""___Third-Party Modules___"""
import numpy as np
import xarray as xr

import numpy.typing as npt
from typing import Dict
"""___NPL Modules___"""

"""__Built-In Modules__"""

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"

_get_range = np.vectorize(lambda *delay: max(delay) - min(delay))

def matchup_dict_to_xarray(matchups_dict:Dict[str, Dict[str, npt.NDArray]], attributes:Dict) -> xr.Dataset:
    """
    Convert matchup dictionary to xarray dataset. For matchup events between more than two satellites, matchups
    are filtered to only those where all satellites are within the desired time threshold (specified in attrs).

    The input matchup information dictionary is generated in Matchups.matchup and is of form:

    .. code-block:: bash

        matchup_info = {"S2A_LS8":
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
        xr.Dataset.from_dict(
            dict(
                [
                    (k, {"dims": "time", "data": v})
                    for k, v in matchups_dict[key].items()
                ]
            )
        ).assign_attrs(
            {
                **attributes,
                **dict(
                    [(s, key.split("_")[i]) for i, s in enumerate(["sat1", "sat2"])]
                ),
            }
        )
        for key in matchups_dict.keys()
    ]

    # if len(ds_list) == 1:
    #     return ds_list[0]

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
        ds_list[i].attrs.update(
            {f"sat{i + 2}": ds_list[i].attrs.pop("sat2")}
        )
    merged_ds = xr.merge(
        [ds.sel(time=times) for ds in ds_list], combine_attrs="no_conflicts"
    )

    return merged_ds.isel(
        time=np.where(
            _get_range(*[merged_ds[i] for i in merged_ds if "delay" in str(i)])
            < attributes["time_diff_threshold"]
        )[0]
    )