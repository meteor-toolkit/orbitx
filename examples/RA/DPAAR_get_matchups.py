import faulthandler
import datetime
import cartopy.crs as ccrs
import calendar
import os
import logging
import matplotlib
matplotlib.use('Agg')  # Prevent GUI (prevents plot showing)
import matplotlib.pyplot as plt
import orbitx


faulthandler.enable()
from orbitx.interface import return_matchups, plot_matchups

__author__ = "Sajedeh Behnia"

# This script outputs monthly matchup files for Sentinel-6 and Jason-3. Can be modified for other satellites and time periods.
# Please note - it does not stop when there are errors, but logs them in file error_log.txt


# Setting up error log - should save errors to error_log.txt

logging.basicConfig(
    filename='error_log.txt',     # File to log errors
    filemode='a',                 # Append mode
    level=logging.ERROR,          # Only log errors and above
    format='%(asctime)s - %(levelname)s - %(message)s'
)

sat1 = "J3"
sat2 = "S6"


for year in range(2022,2025):

    for month_number in range(1,2):

        #S6/J3 ONLY: skip first 4 months of 2022, and jan 2025 (S6 J3 tandem phases)
        if (year == 2022 and month_number in [1,2,3,4]) or (year == 2025 and month_number in [1, 7,8,9,10,11,12]):
            continue

        month_end_day = int(calendar.monthrange(year, month_number)[1])


        start_time_input = datetime.datetime(year, month_number, 1, 0, 0, 0)
        end_time_input = datetime.datetime(year, month_number, month_end_day, 23, 59, 59)

        try:

            ds = return_matchups(
                sats=[sat1, sat2],
                start_time=start_time_input,
                end_time=end_time_input,
                propagation_sampling_interval=60,
                interpolation_sampling_interval=5,
                cntr2cntr_dist=20,
                time_diff_threshold=1800, # 30 minutes
                # output_path_sim_orbits=r"T:\ECO\EOServer\data\satellite_simulated_orbits",
                # output_path_matchups=r"T:\ECO\EOServer\data\satellite_matchups",
            )
            print(ds)
            print('no. of matchups is:', len(ds['time']))
            print(f"Saving file with start date {start_time_input} and end date {end_time_input}")
            filename = f"{sat1}_{sat2}_{start_time_input.strftime('%d%m%Y')}_{end_time_input.strftime('%d%m%Y')}.nc"
            ds.to_netcdf(os.path.join('results', 'threshold_test', filename))

            # Create and save plot to same place as file
            # ds = xr.open_dataset(file)
            # filename = ds.encoding['source'][:-3]

            plot_matchups(ds, ccrs.Mollweide())

            fig = plt.gcf()  # Get current figure
            # fig.savefig(f"{filename}_plot.png", dpi=300, bbox_inches='tight')
            # Save plot
            fig.savefig(os.path.join('results', 'S6_J3', f"{filename[:-3]}_plot.png"), dpi=300, bbox_inches='tight')

            plt.close(fig)

        except Exception as e:
            logging.error(f"An error occurred for start date {start_time_input} and end date {end_time_input}", exc_info=True)  # Logs the full traceback

        # plot_matchups(ds, ccrs.Mollweide())


if __name__ == "__main__":
    pass
