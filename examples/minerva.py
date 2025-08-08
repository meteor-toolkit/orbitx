"""Script to obtain matchups between Sentinel 3A and Altika over 2017 with Minerva"""


"""__Built-In Modules__"""
from orbitx.interface import return_matchups

"""___Third-Party Modules___"""
import faulthandler
import datetime
import cartopy.crs as ccrs
from functools import partial
import orekit

import concurrent.futures
import multiprocessing

import numpy as np
import calendar

"""___NPL Modules___"""

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "01/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"

faulthandler.enable()

sats = ["S3A", "SA"]
years = [2017]
months = range(1, 13)
propagation_sampling_interval = 60
interpolation_sampling_interval = 5
cntr2cntr_dist = 290
time_diff_threshold = 900

arguments = np.empty((len(years) * 12, 4), dtype = object)

for year in years:
    idx_year = (year - np.min(years)) * 12
    for month in months:
        idx_month = idx_year + month - 1
        month_end_day = int(calendar.monthrange(year, month)[1])
        start_date = datetime.datetime(year, month, 1, 0, 0, 0)
        end_date = datetime.datetime(year, month, month_end_day, 0, 0, 0)
        output_path_sim = "../../../hpc-work/orbitx/S3A_SA/orbits"
        output_path_matchups = "../../../hpc-work/orbitx/S3A_SA/matchups"
        arguments[idx_month, :] = [
            start_date,
            end_date,
            output_path_sim,
            output_path_matchups
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
    orekit.getVMEnv().attachCurrentThread()
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
                          propagation_sampling_interval = propagation_sampling_interval,
                          interpolation_sampling_interval = interpolation_sampling_interval,
                          cntr2cntr_dist = cntr2cntr_dist,
                          time_diff_threshold = time_diff_threshold)


n_cores = multiprocessing.cpu_count()
res = []

with concurrent.futures.ThreadPoolExecutor(max_workers=n_cores) as pool:
    for arg in arguments:
        print("submitting {}".format(arg))
        call = partial(
            partial_matchup,
            start_time = arg[0],
            end_time = arg[1],
            output_path_sim_orbits = arg[2],
            output_path_matchups = arg[3])
        res.append(pool.submit(call))
    for r in res:
        print(r.result())


if __name__ == "__main__":
    pass
