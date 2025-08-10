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
    ["CS2", "J2"],  [2010, 2019],
    ["CS2", "S3A"], [2016, 2025],
    ["CS2", "S3B"], [2018, 2025],
    ["CS2", "S6"],  [2020, 2025],
    ["CS2", "SA"],  [2013, 2025],
    ["J2", "S3A"],  [2016, 2019],
    ["J2", "SA"],   [2013, 2019],
    ["J3", "CS2"],  [2016, 2025],
    ["J3", "J2"],   [2016, 2019],
    ["J3", "S3A"],  [2016, 2025],
    ["J3", "S3B"],  [2018, 2025],
    ["J3", "S6"],   [2020, 2025],
    ["J3", "SA"],   [2016, 2025],
    ["N20", "S6"],  [2023, 2023],
    ["S3A", "SA"],  [2016, 2025],
    ["S3B", "J2"],  [2018, 2019],
    ["S3B", "S3A"], [2018, 2025],
    ["S3B", "SA"],  [2018, 2025],
    ["S6", "S3A"],  [2020, 2025],
    ["S6", "S3B"],  [2020, 2025],
    ["S6", "SA"],   [2020, 2025],
]

dates_list = [
    
    
    
    
    
    
    

]


def generate_python_content(sats:List[str], dates:List[int])->str:
    descrption = "\"\"\"Script to obtain matchups between {} and {}\"\"\"".format(sats[0], sats[1])
    modules_import = """\"\"\"___Third-Party Modules___\"\"\"
        import faulthandler
        import datetime
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
        from orbitx.interface import return_matchups
        """
    authorship = f"""\"\"\"___Authorship___\"\"\"
        __author__ = "Zhav Loizeau"
        __created__ = "{datetime.datetime.now():%Y-%m-%d}"
        __version__ = 1.0
        __maintainer__ = "Zhav Loizeau"
        __email__ = "xavier.loizeau@npl.co.uk"
        __status__ = "Development"
        """
    parameters = """sats = ["{}", "{}"]
        years = range({}, {})
        output_path_sim_orbits = "/hpc-work/xl3/orbitx/CS2_J2/orbits/"
        output_path_matchups = "/hpc-work/xl3/orbitx/CS2_J2/matchups/"
        propagation_sampling_interval = 60
        interpolation_sampling_interval = 5
        cntr2cntr_dist = 290
        time_diff_threshold = 900

        os.makedirs(output_path_sim_orbits, exist_ok=True)
        os.makedirs(output_path_matchups, exist_ok=True)
        """.format(sats[0], sats[1], dates[0], dates[1] + 1)
    
    execute = """arguments = np.empty((len(years), 2), dtype = object)

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
    """
    return "\n".join(
        descrption,
        modules_import,
        authorship,
        parameters,
        execute)

def generate_python_title(sats:List[str])->str:
    return "/home/xl3/projects/orbitx/examples/DPAAR/python/{}_{}.py".format(sats[0], sats[1])

for idx in range(len(sats_list)):
    sats = sats_list[idx]
    dates = dates_list[idx]
    file_path = generate_python_title(sats)
    with open(file_path, "w") as file:
        file.write(generate_python_content(sats, dates))
