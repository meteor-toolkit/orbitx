"""Test script showing example usage of orbitx.interface functions"""

import faulthandler
import datetime
import cartopy.crs as ccrs

faulthandler.enable()
from orbitx.interface import return_matchups, plot_matchups

__author__ = "Sajedeh Behnia"

ds = return_matchups(
    sats=["LS8", "S2A"],
    start_time=datetime.datetime(2023, 1, 5, 8, 49, 24),
    end_time=datetime.datetime(2023, 1, 7, 9, 39, 54),
    propagation_sampling_interval=60,
    interpolation_sampling_interval=5,
    cntr2cntr_dist=290,
    time_diff_threshold=900,
    output_path_sim_orbits=r"C:\Users\sb25\OneDrive - National Physical Laboratory\Desktop\newRepo\in review\outputFiles",
    output_path_matchups=r"C:\Users\sb25\OneDrive - National Physical Laboratory\Desktop\newRepo\in review\outputFiles",
)

# plot_matchups(ds, ccrs.Mollweide())

# print(ds)

# ds.to_netcdf("test.nc")

if __name__ == "__main__":
    pass
