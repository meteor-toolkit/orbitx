"""Script to obtain matchups between Sentinel 3A and Altika"""


"""___Third-Party Modules___"""
import faulthandler
import datetime
import numpy as np
import calendar
from functools import partial

import cartopy.crs as ccrs
import orekit

import multiprocessing
import concurrent.futures

"""___NPL Modules___"""

"""__Built-In Modules__"""
faulthandler.enable()
from orbitx.interface import return_matchups


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
        end_date,
    ]

orekit.initVM()
def return_matchups_(
    start_time,
    end_time,
    output_path_sim_orbits,
    output_path_matchups,
    sats,
    propagation_sampling_interval,
    interpolation_sampling_interval,
    cntr2cntr_dist,
    time_diff_threshold):
    return return_matchups(
        sats,
        start_time,
        end_time,
        propagation_sampling_interval,
        interpolation_sampling_interval,
        cntr2cntr_dist,
        time_diff_threshold,
        output_path_sim_orbits,
        output_path_matchups)

partial_matchup = partial(return_matchups_,
                          sats = sats,
                          propagation_sampling_interval = 60,
                          interpolation_sampling_interval = 5,
                          cntr2cntr_dist = 290,
                          time_diff_threshold = 900,
                          output_path_sim_orbits = output_path_sim_orbits,
                          output_path_matchups = output_path_matchups)

n_cores = multiprocessing.cpu_count()
res = []
with concurrent.futures.ThreadPoolExecutor(max_workers = n_cores) as pool:
    for arg in arguments:
        call = partial(partial_matchup,
                       start_time = arg[0],
                       end_time = arg[1],
                       )
        res.append(pool.submit(call))
    for r in res:
        print(r.result())

if __name__ == "__main__":
    pass
