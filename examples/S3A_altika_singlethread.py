"""Script to obtain matchups between Sentinel 3A and Altika"""

"""___Third-Party Modules___"""
import faulthandler
import datetime
import numpy as np
import calendar

import cartopy.crs as ccrs
import orekit
from orekit.pyhelpers import setup_orekit_curdir

"""__Built-In Modules__"""

faulthandler.enable()
from orbitx.interface import return_matchups

"""___NPL Modules___"""

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "01/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"


sats = ["S3A", "SA"]
years = range(2016, 2026)
output_path_sim_orbits = "../../../output/orbitx/S3A_SA/orbits/"
output_path_matchups = "../../../output/orbitx/S3A_SA/matchups/"
propagation_sampling_interval = 60
interpolation_sampling_interval = 5
cntr2cntr_dist = 290
time_diff_threshold = 900

arguments = np.empty((len(years), 2), dtype = object)

for idx_year, year in enumerate(years):
    start_date = datetime.datetime(year, 1, 1, 0, 0, 0)
    end_date = datetime.datetime(year, 12, 31, 0, 0, 0)
    arguments[idx_year, :] = [
        start_date,
        end_date
    ]


for arg_idx in range(arguments.shape[0]):
    arg = arguments[arg_idx, :]
    print(arg[0], arg[1])
    ds = return_matchups(
        sats = sats,
        start_time = arg[0],
        end_time = arg[1],
        propagation_sampling_interval = propagation_sampling_interval,
        interpolation_sampling_interval = interpolation_sampling_interval,
        cntr2cntr_dist = cntr2cntr_dist,
        time_diff_threshold = time_diff_threshold,
        output_path_sim_orbits = output_path_sim_orbits,
        output_path_matchups = output_path_matchups)


if __name__ == "__main__":
    pass
