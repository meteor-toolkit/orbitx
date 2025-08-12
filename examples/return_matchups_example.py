"""Test script showing example usage of orbitx.interface functions"""

import faulthandler
import datetime
import cartopy.crs as ccrs
import time
import time

faulthandler.enable()
from orbitx.interface import return_matchups, plot_matchups

__author__ = "Sajedeh Behnia"

start = time.time()
ds = return_matchups(
    sats=["S3A", "SA"],
    start_time=datetime.datetime(2022, 1, 1, 0, 0, 0),
    end_time=datetime.datetime(2022, 1, 31, 0, 0, 0),
    end_time=datetime.datetime(2022, 1, 31, 0, 0, 0),
    propagation_sampling_interval=60,
    interpolation_sampling_interval=5,
    cntr2cntr_dist=290,
    time_diff_threshold=900,
    output_path_sim_orbits=r"../../../output/orbitx/S3A_SA/orbits",
    output_path_matchups=r"../../../output/orbitx/S3A_SA/matchups"
)
end = time.time()
print(end - start)
# plot_matchups(ds, ccrs.Mollweide())

# print(ds)

# ds.to_netcdf("test.nc")
# ds.to_netcdf("test.nc")

if __name__ == "__main__":
    pass
