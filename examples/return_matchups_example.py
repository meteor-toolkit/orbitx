"""Test script showing example usage of orbitx.interface functions"""

import faulthandler
import datetime
import cartopy.crs as ccrs
import time
import time
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import cartopy.feature as cfeature

faulthandler.enable()
from orbitx.interface import return_matchups
from orbitx.utils._constants import SATELLITE_DICT

__author__ = "Sajedeh Behnia"


get_range = np.vectorize(lambda *delay: max(delay) - min(delay))

ds = return_matchups(
    sats=["S3A", "SA"],
    start_time=datetime.datetime(2022, 1, 1, 0, 0, 0),
    end_time=datetime.datetime(2022, 1, 31, 0, 0, 0),
    propagation_sampling_interval=60,
    interpolation_sampling_interval=5,
    cntr2cntr_dist=290,
    time_diff_threshold=900,
    # output_path_sim_orbits=r"../../../output/orbitx/S3A_SA/orbits",
    # output_path_matchups=r"../../../output/orbitx/S3A_SA/matchups"
    output=True
)
# plot_matchups(ds, ccrs.Mollweide())

# print(ds)

# ds.to_netcdf("test.nc")
# ds.to_netcdf("test.nc")

df = ds.to_dataframe()
years = set(df.index.values.astype('datetime64[Y]').astype(int) + 1970)
df['month'] = df.index.values.astype('datetime64[M]').astype(int) % 12 + 1
df['year'] = df.index.values.astype('datetime64[Y]').astype(int) + 1970


land_mask_1 = []
land_mask_2 = []
matchup_type = []
# df["land_mask_1"] = [landmask(df["lon1"].iloc[i],df["lat1"].iloc[i]) for i in range(len(df.index))]
# df["land_mask_2"] = [landmask(df["lon2"].iloc[i],df["lat2"].iloc[i]) for i in range(len(df.index))]

for i in range(len(df.index)):
    land_mask_1.append(landmask(df["lon1"].iloc[i], df["lat1"].iloc[i]))
    land_mask_2.append(landmask(df["lon2"].iloc[i], df["lat2"].iloc[i]))
    if land_mask_1[i] == land_mask_2[i]:
        matchup_type.append(land_mask_1[i])
    else:
        matchup_type.append("COAST")

df["land_mask_1" ] = land_mask_1
df["land_mask_2" ] = land_mask_2
df["matchup_type"] = matchup_type

for year in years:
    df_y = df.where(df.year == year)
    df_y = df_y.dropna()
    for month in set(df_y["month"]):
        df_m = df_y.where(df_y.month == month)
        df_m = df_m.dropna()

        projection = ccrs.Mollweide()
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1, projection=projection)
        ax.coastlines()
        ax.add_feature(cfeature.LAND)
        sat_no = len([i for i in ds if "lat" in i])
        if sat_no == 2:
            delay = df_m["delay"].values
        else:
            delay = get_range(*[df_m[i] for i in df_m if "delay" in str(i)])
        for i in range(sat_no):
            ax.scatter(
                df_m[f"lon{i + 1}"].values,
                df_m[f"lat{i + 1}"].values,
                s=((ds.attrs["time_threshold"] - delay) ** 2
                    / (ds.attrs["time_threshold"] / 2) ** 2),
                label=SATELLITE_DICT[ds.attrs[f"sat{i + 1}"]],
                transform=ccrs.PlateCarree(),
            )
        ax.legend(loc="lower right")

        fig_str = ds.attrs["sat1"] + "_" +ds.attrs["sat2"] + "_" + str(year) + "_" + str(month)
        plt.title("Matchups " + ds.attrs["sat1"] + " and " + ds.attrs["sat2"] + " " + str(year) + "-" + str(month) + ", time threshold: " + str(ds.attrs["time_threshold"]) +" seconds")
        plt.savefig(fig_str+".png")


if __name__ == "__main__":
    pass
