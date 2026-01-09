########################
Using OrbitX in parallel
########################

To run OrbitX in parallel, one needs to import the `faulthandler` package and run the `faulthandler.enable()` command.
We also recommand using the `concurrent.futures.ThreadPoolExecutor` function to handle the CPU parallelisation.
The script bellow illustrate how to obtain matchups between Jason-3 and CryoSat-2 between 2016 and 2026 by running each year in parallel.
Note the use of the `check_before` and `check_after` arguments to ensure the matchups at the limit of two years are found only once.

First import the required packages:

.. code-block:: python3

    """Script to obtain matchups between J3 and CS2"""

    """___Third-Party Modules___"""
    import faulthandler
    import numpy as np
    import calendar
    from functools import partial

    import cartopy.crs as ccrs
    import orekit

    import multiprocessing
    import concurrent.futures
    import os

    """__Built-In Modules__"""
    faulthandler.enable()
    from orbitx import Matchups

Declare the arguments that are shared across all calls and create the folders to hold the results:

.. code-block:: python3

    satellites = ["J3", "CS2"]
    years = range(2016, 2026)
    output_path_sim_orbits = "/home/usr/Documents/output/orbitx/J3_CS2/orbits/"
    output_path_matchups = "/home/usr/Documents/output/orbitx/J3_CS2/matchups/"
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


Create a numpy array to hold the arguments that differ across the calls (here the limit dates):

.. code-block:: python3

    arguments = np.empty((len(years), 2), dtype = object)

    for idx_year, year in enumerate(years):
        start_date = np.datetime64(f"{year}-01-01T00:00:00")
        end_date = np.datetime64("{year + 1}-01-01T00:00:00")
        arguments[idx_year, :] = [
            start_date,
            end_date,
        ]


Create a function that generates the matchups and saves the results all at once:

.. code-block:: python3

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

Create a function that fixes the value of the shared arguments:

.. code-block:: python3

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


Declare the number of cores to be used and submit the calls:

.. code-block:: python3

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
