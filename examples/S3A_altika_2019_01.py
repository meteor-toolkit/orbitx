"""Script to obtain matchups between Sentinel 3A and Altika"""


"""__Built-In Modules__"""
from orbitx.interface import return_matchups

"""___Third-Party Modules___"""
import faulthandler
import datetime
import cartopy.crs as ccrs
from functools import partial
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
# years = range(2016, 2026)
years=[2019]
months = range(1,13)

arguments = np.empty((len(years) * 12, 4), dtype = object)

for year in years:
    idx_year = (year - np.min(years)) * 12
    for month in months:
        idx_month = idx_year + month - 1
        month_end_day = int(calendar.monthrange(year, month)[1])
        start_date = datetime.datetime(year, month, 1, 0, 0, 0)
        end_date = datetime.datetime(year, month, month_end_day, 0, 0, 0)
        output_path_sim = "orbits_S3A_J3"
        output_path_matchups = "matchups_S3A_J3"
        arguments[idx_month, :] = [
            start_date,
            end_date,
            output_path_sim,
            output_path_matchups
            ]

for i in range(arguments.shape[0]):
    return_matchups(
        sats=sats,
        start_time=arguments[i][0],
        end_time=arguments[i][1],
        propagation_sampling_interval=60,
        interpolation_sampling_interval=5,
        cntr2cntr_dist=290,
        time_diff_threshold=900,
        output_path_sim_orbits=arguments[i][2],
        output_path_matchups=arguments[i][3]
    )

if __name__ == "__main__":
    pass
