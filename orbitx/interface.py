"""orbitx.interface - file containing all interface functions"""

import os
import datetime
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from typing import List, Optional

from orbitx.orbit import Orbit
from orbitx.matchup import Matchups, get_range

__author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
]

__all__ = ["return_matchups", "plot_matchups"]


SATELLITE_DICT = {
    "LS8": "Landsat-8",
    "LS9": "Landsat-9",
    "S2A": "Sentinel-2A",
    "S2B": "Sentinel-2B",
    "S3A": "Sentinel-3A",
    "S3B": "Sentinel-3B",
    "S6": "Sentinel-6",
    "J3": "JASON-3",
    "SA": "Saral-AltiKa",
}


def return_matchups(
    sats: List[str],
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    propagation_sampling_interval: float,
    interpolation_sampling_interval: float,
    cntr2cntr_dist: float,
    time_diff_threshold: float,
    output_path_sim_orbits: Optional[str] = None,
    output_path_matchups: Optional[str] = None,
    output: bool = False
) -> Optional[xr.Dataset]:
    """
    Matchup event identification between multiple satellites. Creates an xr.Dataset
    containing position and time information for satellite matchups.

    If no output paths are specified, the dataset will be returned.
    If output paths are specified the data will be saved.
    If `output` is set to `True` the dataset will be returned regardless of whether or not it has been saved.

    Currently accepted satellites:
        * LS8 (Landsat-8)
        * S2A (Sentinel-2A)
        * S2B (Sentinel-2B)
        * S3A (Sentinel-3A)
        * S6 (Sentinel-6)

    :param sats: list of satellites
    :param start_time: start of time period of interest
    :param end_time: end of time period of interest
    :param propagation_sampling_interval: sampling rate of orbit propagation per sensor
    :param interpolation_sampling_interval: subsampling rate of orbit propagation per sensor by interpolation
    :param cntr2cntr_dist: matchup threshold for distance between the nadir position of the two satellites (kilometres)
    :param time_diff_threshold: matchup threshold for time difference between the two satellites (seconds)
    :param output_path_sim_orbits: path to write evaluated propagated orbits to
    :param output_path_matchups: path to write matchups to (as a netcdf file)
    :param output: whether or not to output the matchup dataset, if no output_path defined defaults to True else False
    """
    # simulate desired orbits
    orbit = Orbit()
    orbit_output = orbit.run(
        sats,
        start_time,
        end_time,
        propagation_sampling_interval,
        interpolation_sampling_interval,
    )

    if not output_path_sim_orbits is None:
        keys = list(orbit_output.keys())
        for i in range(len(keys)):

            # Construct filename
            sat = keys[i]
            date_part = f"{start_time:%Y%m%d}_{end_time:%Y%m%d}"
            sampling_part = f"psi{propagation_sampling_interval}_isi{interpolation_sampling_interval}"
            filename = f"{date_part}_{sampling_part}_orbit_{sat}.nc"

            # Save orbit as xr
            orbit_of_sat = xr.Dataset({
                'lat': orbit_output[sat]['lat'],
                'lon': orbit_output[sat]['lon'],
                'time': orbit_output[sat]['time'],
            #     Add time
            })
            orbit_of_sat.attrs['sat'] = sat

            # Save as netCDF4
            orbit_of_sat.to_netcdf(os.path.join(output_path_sim_orbits, filename))

    # find matchups between orbits
    matchup = Matchups()
    matchup_output = matchup.matchup(
        orbit_output,
        time_diff_threshold,
        cntr2cntr_dist)

    if output_path_sim_orbits is not None:
        # save orbital data
        # orbit.save(orbit_output, output_path_sim_orbits)
        pass

    if output_path_matchups is not None:
        # save matchup data
        # fname = f"matchup_{'_'.join(list(orbit_output.keys()))}_starttime_{start_time.strftime('%Y%m%d')}_endtime_{end_time.strftime('%Y%m%d')}_samplinginterval_{propagation_sampling_interval}_tmptol_{time_diff_threshold}.nc"

        # Construct filename
        sat_part = "_".join(sats)
        date_part = f"{start_time:%Y%m%d}_{end_time:%Y%m%d}"
        sampling_part = f"psi{propagation_sampling_interval}_isi{interpolation_sampling_interval}"
        matchup_part = f"c2c{cntr2cntr_dist}_tdt{time_diff_threshold}"
        filename = f"{date_part}_{sampling_part}_matchups_{sat_part}_{matchup_part}.nc"
     
        # Save as netCDF4
        matchup_output.to_netcdf(os.path.join(output_path_matchups, filename))
    else:
        output = True

    if output is True:
        return matchup_output
    else:
        return None


def plot_matchups(ds: xr.Dataset, projection=ccrs.PlateCarree()) -> None:
    """
    Plot the matchup dataset generated from orbitx.interface.return_matchups

    :param ds: matchup dataset containing latitude, latitude and time information for matchup events
    :param projection: cartopy.crs projection to use to plot, defaults to cartopy.crs.PlateCarree()
    """
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection=projection)
    ax.coastlines()
    ax.add_feature(cfeature.LAND)
    sat_no = len([i for i in ds if "lat" in i])
    if sat_no == 2:
        delay = ds["delay"]
    else:
        delay = get_range(*[ds[i] for i in ds if "delay" in str(i)])
    for i in range(sat_no):
        ax.scatter(
            ds[f"lon{i + 1}"],
            ds[f"lat{i + 1}"],
            s=(ds.attrs["time_threshold"] - delay) ** 2
            / (ds.attrs["time_threshold"] / 2) ** 2,
            label=SATELLITE_DICT[ds.attrs[f"sat{i + 1}"]],
            transform=ccrs.PlateCarree(),
        )
    ax.legend(loc="lower right")
    plt.show()
