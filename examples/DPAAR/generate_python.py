"""A File to generate python scripts that generate matchups"""

"""___Third-Party Modules___"""
from typing import List
import datetime

"""___NPL Modules___"""

"""__Built-In Modules__"""


"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "10/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"

sats_list = [
    ["CS2", "J2"],
    ["CS2", "S3A"],
    ["CS2", "S3B"],
    ["CS2", "S6"],
    ["CS2", "SA"],
    ["J2", "S3A"],
    ["J2", "SA"],
    ["J3", "CS2"],
    ["J3", "J2"],
    ["J3", "S3A"],
    ["J3", "S3B"],
    ["J3", "S6"],
    ["J3", "SA"],
    ["N20", "S6"],
    ["S3A", "SA"],
    ["S3B", "J2"],
    ["S3B", "S3A"],
    ["S3B", "SA"],
    ["S6", "S3A"],
    ["S6", "S3B"],
    ["S6", "SA"],
]

dates_list = [
    [2010, 2019],
    [2016, 2025],
    [2018, 2025],
    [2020, 2025],
    [2013, 2025],
    [2016, 2019],
    [2013, 2019],
    [2016, 2025],
    [2016, 2019],
    [2016, 2025],
    [2018, 2025],
    [2020, 2025],
    [2016, 2025],
    [2023, 2023],
    [2016, 2025],
    [2018, 2019],
    [2018, 2025],
    [2018, 2025],
    [2020, 2025],
    [2020, 2025],
    [2020, 2025],
]


def generate_python_content(sats: List[str], dates: List[int]) -> str:
    descrption = f'"""Script to obtain matchups between {sats[0]} and {sats[1]}"""'
    modules_import = """
\"\"\"___Third-Party Modules___\"\"\"
import faulthandler
import numpy as np
import calendar
from functools import partial

import cartopy.crs as ccrs
import orekit

import multiprocessing
import concurrent.futures
import os

\"\"\"___NPL Modules___\"\"\"

\"\"\"__Built-In Modules__\"\"\"
faulthandler.enable()
from orbitx import Matchups
"""
    authorship = f"""
\"\"\"___Authorship___\"\"\"
__author__ = "Zhav Loizeau"
__created__ = "{datetime.datetime.now():%Y-%m-%d}"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"
"""
    parameters = f"""
satellites = ["{sats[0]}", "{sats[1]}"]
years = range({dates[0]}, {dates[1] + 1})
output_path_sim_orbits = "/home/xl3/Documents/output/orbitx/{sats[0]}_{sats[1]}/orbits/"
output_path_matchups = "/home/xl3/Documents/output/orbitx/{sats[0]}_{sats[1]}/matchups/"
propagation_sampling_interval = np.array(60, dtype="timedelta64[s]")
interpolation_sampling_interval = np.array(5, dtype="timedelta64[s]")
space_diff_threshold = 290
time_diff_threshold = np.array(900, dtype="timedelta64[s]")
check_before = False
check_after = True
has_land_ocean_mask = True
reference_date=np.datetime64("2000-01-01T00:00:00")

os.makedirs(output_path_sim_orbits, exist_ok=True)
os.makedirs(output_path_matchups, exist_ok=True)
"""

    execute = """
arguments = np.empty((len(years), 2), dtype = object)

for idx_year, year in enumerate(years):
    start_date = np.datetime64(f"{year}-01-01T00:00:00")
    end_date = np.datetime64("{year + 1}-01-01T00:00:00")
    arguments[idx_year, :] = [
        start_date,
        end_date,
    ]

orekit.initVM()
def return_matchups_(
    start_date,
    end_date,
    satellites,
    propagation_sampling_interval,
    interpolation_sampling_interval,
    space_diff_threshold,
    time_diff_threshold,
    check_before,
    check_after,
    has_land_ocean_mask,
    reference_date
    ):
    matchups = Matchups.find_matchups(
        satellites=satellites,
        start_date=start_date,
        end_date=end_date,
        propagation_sampling_interval = propagation_sampling_interval,
        interpolation_sampling_interval = interpolation_sampling_interval,
        space_diff_threshold = space_diff_threshold,
        time_diff_threshold = time_diff_threshold,
        check_before = check_before,
        check_after = check_after,
        has_land_ocean_mask = has_land_ocean_mask,
        reference_date=reference_date
    )

    matchups.orbit.to_netcdf(output_path_sim_orbits)
    matchups.to_netcdf(output_path_matchups)

    fig_matchup = matchups.plot()
    fig_matchup.savefig(f"{output_path_matchups}matchup_plot.png")
    fig_orbit = matchups.orbit.plot()
    fig_orbit.savefig(f"{output_path_matchups}orbit_plot.png")

    return

partial_matchup = partial(
    return_matchups_,
    satellites = satellites,
    propagation_sampling_interval = propagation_sampling_interval,
    interpolation_sampling_interval = interpolation_sampling_interval,
    space_diff_threshold = space_diff_threshold,
    time_diff_threshold = time_diff_threshold,
    check_before = check_before,
    check_after = check_after,
    has_land_ocean_mask = has_land_ocean_mask,
    reference_date=reference_date
)

n_cores = multiprocessing.cpu_count()
res = []
with concurrent.futures.ThreadPoolExecutor(max_workers = n_cores) as pool:
    for arg in arguments:
        call = partial(
            partial_matchup,
            start_time = arg[0],
            end_time = arg[1],
        )
        res.append(pool.submit(call))
    for r in res:
        print(r.result())

if __name__ == "__main__":
    pass
"""
    return "\n".join((descrption, modules_import, authorship, parameters, execute))


def generate_python_title(sats: List[str]) -> str:
    return rf"C:\Users\xl3\Documents\projects\orbitx\examples\DPAAR\python/{sats[0]}_{sats[1]}.py"


for idx in range(len(sats_list)):
    sats = sats_list[idx]
    dates = dates_list[idx]
    file_path = generate_python_title(sats)
    with open(file_path, "w") as file:
        file.write(generate_python_content(sats, dates))
