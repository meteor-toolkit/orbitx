"""Test script showing example usage of orbitx.return_matchups"""

# from orbitx import return_matchups
# import datetime
#
#
# __author__ = "Sajedeh Behnia"
#
#
# def main():
#     """
#     Runs test example of orbitx.return_matchups
#     """
#
#     sat_1 = "S2A"
#     sat_2 = "LS8"
#
#     start_time = datetime.datetime(2021, 6, 1, 0, 0, 0)
#     end_time = datetime.datetime(2022, 9, 1, 0, 0, 0)
#
#     propagation_sampling_interval = 1 * 60  # time in seconds
#     interpolation_sampling_interval = 5  # time in second
#
#     cntr2cntr_dist = 500  # distance in meter
#     time_diff_threshold = 1 * 60 * 60  # time difference in seconds
#
#     output_path_sim_orbits = r"T:\ECO\EOServer\data\satellite_simulated_orbits"
#     output_path_matchups = r"T:\ECO\EOServer\data\satellite_matchups"
#
#     lonmin = -3
#     lonmax = -0.2
#     latmin = 50
#     latmax = 53
#
#     return_matchups(
#         sat_1=sat_1,
#         sat_2=sat_2,
#         start_time=start_time,
#         end_time=end_time,
#         propagation_sampling_interval=propagation_sampling_interval,
#         interpolation_sampling_interval=interpolation_sampling_interval,
#         cntr2cntr_dist=cntr2cntr_dist,
#         time_diff_threshold=time_diff_threshold,
#         latmin=latmin,
#         latmax=latmax,
#         lonmin=lonmin,
#         lonmax=lonmax,
#         output_path_sim_orbits=output_path_sim_orbits,
#         output_path_matchups=output_path_matchups,
#     )
#

if __name__ == "__main__":
    import faulthandler
    import datetime
    faulthandler.enable()
    from orbitx.interface import return_matchups

    return_matchups(
        sats=["S3A", "LS8"],
        start_time=datetime.datetime(2021, 6, 1, 0, 0, 0),
        end_time=datetime.datetime(2021, 7, 1, 0, 0, 0),
        propagation_sampling_interval=60,
        interpolation_sampling_interval=5,
        cntr2cntr_dist=500,
        time_diff_threshold=3600,
        latmin=40,
        latmax=50,
        lonmin=40,
        lonmax=50,
        output_path_sim_orbits=r"C:\Users\mg13\Documents\Projects\data\satellite_simulated_orbits",
        output_path_matchups=r"C:\Users\mg13\Documents\Projects\data\satellite_matchups",
    )
    # main()
