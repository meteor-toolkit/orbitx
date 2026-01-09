"""Example script to obtain matchups between S3A and SA"""

"""___Third-Party Modules___"""
import faulthandler
import numpy as np

import orekit

import os

"""___NPL Modules___"""

"""__Built-In Modules__"""
faulthandler.enable()
from orbitx import Matchups


<<<<<<< HEAD
"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "2025-09-11"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"


satellites: list[str] = ["S3A", "SA"]
start_date: np.datetime64 = np.datetime64("2018-01-01T00:00:00")
end_date: np.datetime64 = np.datetime64("2019-01-01T00:00:00")
output_path_sim_orbits = r".\examples\output"
output_path_matchups = r".\examples\output"
propagation_sampling_interval: np.timedelta64 = np.array(60, dtype="timedelta64[s]")
interpolation_sampling_interval: np.timedelta64 = np.array(5, dtype="timedelta64[s]")
space_diff_threshold = 290.0
time_diff_threshold: np.timedelta64 = np.array(900, dtype="timedelta64[s]")
check_before = False
check_after = True
has_land_ocean_mask = True
reference_date: np.datetime64 = np.datetime64("2000-01-01T00:00:00")

os.makedirs(output_path_sim_orbits, exist_ok=True)
os.makedirs(output_path_matchups, exist_ok=True)

orekit.initVM()

matchups = Matchups.find_matchups(
    satellites=satellites,
    start_date=start_date,
    end_date=end_date,
    propagation_sampling_interval=propagation_sampling_interval,
    interpolation_sampling_interval=interpolation_sampling_interval,
    space_diff_threshold=space_diff_threshold,
    time_diff_threshold=time_diff_threshold,
    check_before=check_before,
    check_after=check_after,
    has_land_ocean_mask=has_land_ocean_mask,
    reference_date=reference_date,
=======
ds = return_matchups(
    sats=["LS8", "EMIT"],
    start_time=datetime.datetime(2022, 1, 1, 0, 0, 0),
    end_time=datetime.datetime(2022, 2, 1, 0, 0, 0),
    propagation_sampling_interval=60,
    interpolation_sampling_interval=5,
    cntr2cntr_dist=290,
    time_diff_threshold=900,
    # output_path_sim_orbits=r"T:\ECO\EOServer\data\satellite_simulated_orbits",
    # output_path_matchups=r"T:\ECO\EOServer\data\satellite_matchups",
>>>>>>> 4a0d65e6400d8d9507abec2521e4b77f12cb2b65
)

matchups.orbit.to_netcdf(output_path_sim_orbits)
matchups.to_netcdf(output_path_matchups)

<<<<<<< HEAD
fig_matchup = matchups.plot()
fig_matchup.savefig(f"{output_path_matchups}matchup_plot.png")
fig_orbit = matchups.orbit.plot()
fig_orbit.savefig(f"{output_path_matchups}orbit_plot.png")
=======
print(ds)

ds.to_netcdf("/mnt/t/joe/misc/test.nc")
>>>>>>> 4a0d65e6400d8d9507abec2521e4b77f12cb2b65

if __name__ == "__main__":
    pass
