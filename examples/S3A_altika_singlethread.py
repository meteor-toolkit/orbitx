"""Script to obtain matchups between Sentinel 3A and Altika"""


"""__Built-In Modules__"""
from orbitx.interface import return_matchups

"""___Third-Party Modules___"""
import faulthandler
import datetime
import cartopy.crs as ccrs
from functools import partial
from itertools import starmap
import numpy as np
import calendar
import orekit
from orekit.pyhelpers import setup_orekit_curdir

"""___NPL Modules___"""

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "01/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"

vm = orekit.initVM()

setup_orekit_curdir()
faulthandler.enable()

sats = ["S3A", "SA"]
# years = range(2016, 2026)
years=[2017]
months = range(1, 13)

arguments = np.empty((len(years) * 12, 4), dtype = object)

for year in years:
    idx_year = (year - np.min(years)) * 12
    for month in months:
        idx_month = idx_year + month - 1
        month_end_day = int(calendar.monthrange(year, month)[1])
        start_date = datetime.datetime(year, month, 1, 0, 0, 0)
        end_date = datetime.datetime(year, month, month_end_day, 0, 0, 0)
        output_path_sim = "orbits_S3A_J3_{}_{}".format(year, month)
        output_path_matchups = "matchups_S3A_J3_{}_{}".format(year, month)
        arguments[idx_month, :] = [
            start_date,
            end_date,
            output_path_sim,
            output_path_matchups
            ]


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
                          time_diff_threshold = 900)

res = list(starmap(partial_matchup, arguments))


if __name__ == "__main__":
    pass
