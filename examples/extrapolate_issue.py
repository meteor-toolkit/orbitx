import faulthandler
import datetime
import cartopy.crs as ccrs
import calendar
import os

# This script will search for matchups for 2018-19, attempting to create a file for each month. 
#It will keep running when it encounters the ValueError, but will print out the error as well 
#as the time period in which the error occur. To see the full error and have it stop the script
# from running, remove the try except statement.

faulthandler.enable()
from orbitx.interface import return_matchups, plot_matchups

__author__ = "Sajedeh Behnia"

sat1  = "SA"
sat2 = "S3B"

for year in range(2018,2020):

    for month_number in range(1,12):

        month_end_day = int(calendar.monthrange(year, month_number)[1])

        print(month_end_day)

        start_time_input = datetime.datetime(year, month_number, 1, 0, 0, 0)
        end_time_input = datetime.datetime(year, month_number, month_end_day, 23, 59, 59)
        # end_time_input = datetime.datetime(year, month_number, 1, 23, 59, 59)

        try:

            ds = return_matchups(
                sats=[sat1, sat2],
                start_time=start_time_input,
                end_time=end_time_input,
                propagation_sampling_interval=60,
                interpolation_sampling_interval=5,
                cntr2cntr_dist=20,
                time_diff_threshold=3600*24*2,
                # output_path_sim_orbits=r"T:\ECO\EOServer\data\satellite_simulated_orbits",
                # output_path_matchups=r"T:\ECO\EOServer\data\satellite_matchups",
            )
            print(ds)
            print(f"Saving file with start date {start_time_input} and end date {end_time_input}")
            ds.to_netcdf("matchups_test.nc")
            plot_matchups(ds, ccrs.Mollweide())

            # ds.to_netcdf(os.path.join('results', f'{year}',f"SA_S3B_{start_time_input.strftime('%d%m%Y')}_{end_time_input.strftime('%d%m%Y')}.nc"))

        except ValueError as e:
            print(f"[Warning] ValueError occurred: {e} \n for start date {start_time_input} and end date {end_time_input}")
            result = None  


if __name__ == "__main__":
    pass
