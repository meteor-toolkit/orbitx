"""Script to obtain matchups between Sentinel 3A and Altika"""


"""__Built-In Modules__"""
from orbitx.interface import return_matchups, plot_matchups

"""___Third-Party Modules___"""
import faulthandler
import datetime
import cartopy.crs as ccrs

"""___NPL Modules___"""

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "01/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"

faulthandler.enable()

ds = return_matchups(
    sats=["S3A", "SA"],
    start_time=datetime.datetime(2016, 1, 1, 0, 0, 0),
    end_time=datetime.datetime(2025, 1, 1, 0, 0, 0),
    propagation_sampling_interval=60,
    interpolation_sampling_interval=5,
    cntr2cntr_dist=290,
    time_diff_threshold=900,
    output_path_sim_orbits=r"..\..\satellite_simulated_orbits",
    output_path_matchups=r"..\..\satellite_matchups",
)

# plot_matchups(ds, ccrs.Mollweide())

# print(ds)

ds.to_netcdf("test.nc")

if __name__ == "__main__":
    pass
