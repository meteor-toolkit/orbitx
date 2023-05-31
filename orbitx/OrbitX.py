import os
import numpy as np
import datetime as datetime
from orbitx.get_2LEs import get_2LEs
from orbitx.form_smpl_space import form_smpl_space
from orbitx.breakup_smpl_space import breakup_smpl_space
from orbitx.propagate_orbit import propagate_orbit
from scipy.interpolate import interp1d
from orbitx.cal_dist_d2m import cal_dist_d2m
import matplotlib.pyplot as plt


def return_matchups(
    sat_1: str,
    sat_2: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    propagation_sampling_interval: float,
    interpolation_sampling_interval: float,
    cntr2cntr_dist: float,
    time_diff_threshold: float,
    latmin: float,
    latmax: float,
    lonmin: float,
    lonmax: float,
    output_path_sim_orbits: str,
    output_path_matchups: str
) -> None:
    """

    :param sat_1: satellite 1 name
    :param sat_2: satellite 2 name
    :param start_time: start of time period of interest
    :param end_time: end of time period of interest
    :param propagation_sampling_interval: sampling rate of orbit propagation per sensor
    :param interpolation_sampling_interval: subsampling rate of orbit propagation per sensor by interpolation
    :param cntr2cntr_dist: matchup threshold for distance between the nadir position of the two satellites
    :param time_diff_threshold: matchup threshold for time difference between the two satellites
    :param latmin: minimum latitude for region of interest
    :param latmax: maximum latitude for region of interest
    :param lonmin: minimum longitude for region of interest
    :param lonmax: maximum longitude for region of interest
    :param output_path_sim_orbits: path to write evaluated propagated orbits to
    :param output_path_matchups: path to write matchups to
    """

    # region Get relevant TLE lines (and times)

    tle1_line1, tle1_line2, tle1_secs_since_2000 = get_2LEs(start_time, end_time, sat_1)
    tle2_line1, tle2_line2, tle2_secs_since_2000 = get_2LEs(start_time, end_time, sat_2)

    # endregion


    # region Form the sampling space

    smpl_space, smpl_space_secs_since_2000 = form_smpl_space(start_time, end_time, propagation_sampling_interval)

    # endregion


    # region Prepare inputs to simulation runs

    sat1_smpl_breakup_idx, tle1_ref_lines = breakup_smpl_space(smpl_space_secs_since_2000, tle1_secs_since_2000)
    sat2_smpl_breakup_idx, tle2_ref_lines = breakup_smpl_space(smpl_space_secs_since_2000, tle2_secs_since_2000)

    # endregion


    # region Simulate and append orbit sections

    sat1_lat_sim = []
    sat1_lon_sim = []
    sat1_secsince = []
    for i in range(len(tle1_ref_lines) - 1):
        secsince1, lat1, lon1, alt1, el1, az1 = propagate_orbit(tle1_line1[i], tle1_line2[i],
                                                                smpl_space[sat1_smpl_breakup_idx[i]],
                                                                smpl_space[sat1_smpl_breakup_idx[i + 1] - 1],
                                                                propagation_sampling_interval)
        sat1_lat_sim.append(lat1)
        sat1_lon_sim.append(lon1)
        sat1_secsince.append(secsince1)
    sat1_lat_sim = np.hstack(sat1_lat_sim)  # flatten the inhomogeneous list of lists
    sat1_lon_sim = np.hstack(sat1_lon_sim)  # flatten the inhomogeneous list of lists
    sat1_secsince = np.hstack(sat1_secsince)  # flatten the inhomogeneous list of lists

    sat2_lat_sim = []
    sat2_lon_sim = []
    sat2_secsince = []
    for i in range(len(tle2_ref_lines) - 1):
        secsince2, lat2, lon2, alt2, el2, az2 = propagate_orbit(tle2_line1[i], tle2_line2[i],
                                                                smpl_space[sat2_smpl_breakup_idx[i]],
                                                                smpl_space[sat2_smpl_breakup_idx[i + 1] - 1],
                                                                propagation_sampling_interval)
        sat2_lat_sim.append(lat2)
        sat2_lon_sim.append(lon2)
        sat2_secsince.append(secsince2)
    sat2_lat_sim = np.hstack(sat2_lat_sim)  # flatten the inhomogeneous list of lists
    sat2_lon_sim = np.hstack(sat2_lon_sim)  # flatten the inhomogeneous list of lists
    sat2_secsince = np.hstack(sat2_secsince)  # flatten the inhomogeneous list of lists

    # endregion


    # region Save the simulated orbits if needed

    fname1 = sat_1 + '_starttime' + str(start_time)[0:4] + str(start_time)[5:7] + str(start_time)[8:10] + '_endtime' + str(
        end_time)[0:4] + str(end_time)[5:7] + str(end_time)[8:10] + '_samplinginterval' + str(
        propagation_sampling_interval) + '.txt'
    fname2 = sat_2 + '_starttime' + str(start_time)[0:4] + str(start_time)[5:7] + str(start_time)[8:10] + '_endtime' + str(
        end_time)[0:4] + str(end_time)[5:7] + str(end_time)[8:10] + '_samplinginterval' + str(
        propagation_sampling_interval) + '.txt'

    orbit1 = [sat1_secsince, sat1_lat_sim, sat1_lon_sim]
    orbit2 = [sat2_secsince, sat2_lat_sim, sat2_lon_sim]

    with open(os.path.join(output_path_sim_orbits, fname1), 'w') as file:
        for x in zip(*orbit1):
            file.write("{0}\t{1}\t{2}\n".format(*x))

    with open(os.path.join(output_path_sim_orbits, fname2), 'w') as file:
        for x in zip(*orbit2):
            file.write("{0}\t{1}\t{2}\n".format(*x))

    # endregion


    # region Resample the simulated orbit by interpolation

    f1_lat_linear = interp1d(sat1_secsince, sat1_lat_sim, fill_value='extrapolate')
    f1_lon_linear = interp1d(sat1_secsince, sat1_lon_sim, fill_value='extrapolate')

    f2_lat_linear = interp1d(sat2_secsince, sat2_lat_sim, fill_value='extrapolate')
    f2_lon_linear = interp1d(sat2_secsince, sat2_lon_sim, fill_value='extrapolate')

    prop_smpl_space = np.arange(smpl_space_secs_since_2000[0],
                                smpl_space_secs_since_2000[len(smpl_space_secs_since_2000) - 1],
                                interpolation_sampling_interval)

    sat1_lat_sim_interp = f1_lat_linear(prop_smpl_space)
    sat1_lon_sim_interp = f1_lon_linear(prop_smpl_space)
    sat2_lat_sim_interp = f2_lat_linear(prop_smpl_space)
    sat2_lon_sim_interp = f2_lon_linear(prop_smpl_space)

    # endregion



    # region Search for match-ups

    sat1_inROI_idx = (sat1_lat_sim_interp > latmin) & (sat1_lat_sim_interp < latmax) & (sat1_lon_sim_interp > lonmin) & (sat1_lon_sim_interp < lonmax)
    sat2_inROI_idx = (sat2_lat_sim_interp > latmin) & (sat2_lat_sim_interp < latmax) & (sat2_lon_sim_interp > lonmin) & (sat2_lon_sim_interp < lonmax)

    sat1_inROI_time = prop_smpl_space[sat1_inROI_idx]
    sat2_inROI_time = prop_smpl_space[sat2_inROI_idx]
    sat1_inROI_lat = sat1_lat_sim_interp[sat1_inROI_idx]
    sat1_inROI_lon = sat1_lon_sim_interp[sat1_inROI_idx]
    sat2_inROI_lat = sat2_lat_sim_interp[sat2_inROI_idx]
    sat2_inROI_lon = sat2_lon_sim_interp[sat2_inROI_idx]

    sat1_time_dif = sat1_inROI_time[1:len(sat1_inROI_time)] - sat1_inROI_time[0:len(sat1_inROI_time)-1]
    sat1_jump_boolean = sat1_time_dif != interpolation_sampling_interval
    sat1_jump_stop_idx = [i for i, val in enumerate(sat1_jump_boolean) if val]
    sat1_jump_start_idx = [i + 1 for i in sat1_jump_stop_idx]
    if sat1_jump_stop_idx[0] < sat1_jump_start_idx[0]:
        sat1_jump_stop_idx.remove(sat1_jump_stop_idx[0])
        sat1_jump_start_idx = sat1_jump_start_idx[0:len(sat1_jump_stop_idx)]

    sat2_time_dif = sat2_inROI_time[1:len(sat2_inROI_time)] - sat2_inROI_time[0:len(sat2_inROI_time)-1]
    sat2_jump_boolean = sat2_time_dif != interpolation_sampling_interval
    sat2_jump_stop_idx = [i for i, val in enumerate(sat2_jump_boolean) if val]
    sat2_jump_start_idx = [i + 1 for i in sat2_jump_stop_idx]
    if sat2_jump_stop_idx[0] < sat2_jump_start_idx[0]:
        sat2_jump_stop_idx.remove(sat2_jump_stop_idx[0])
        sat2_jump_start_idx = sat2_jump_start_idx[0:len(sat2_jump_stop_idx)]


    match_event_idx = []
    if len(sat1_jump_start_idx) <= len(sat2_jump_start_idx):

        for i in range(len(sat1_jump_start_idx)):
            timevec1 = []
            timevec1 = sat1_inROI_time[sat1_jump_start_idx[i]: sat1_jump_stop_idx[i]]

            for j in range(len(sat2_jump_start_idx)):
                timevec2 = []
                timevec2 = sat2_inROI_time[sat2_jump_start_idx[j]: sat2_jump_stop_idx[j]]

                if np.abs(np.mean(timevec2) - np.mean(timevec1)) <= time_diff_threshold:
                    match_event_idx.append([i,j,np.abs(np.mean(timevec2) - np.mean(timevec1))])

    # endregion


    # region Save matchup information

    fname = 'matchup_' + sat_1 + '_' + sat_2 + '_T' + str(start_time)[0:4] + str(start_time)[5:7] + \
            str(start_time)[8:10] + '_' + str(end_time)[0:4] + str(end_time)[5:7] + str(end_time)[8:10] + \
            '_deltaT' + str(propagation_sampling_interval) + '_lat[' + str(int(latmin)) + '][' + \
            str(int(latmax)) + ']lon[' + str(int(lonmin)) + '][' + str(int(lonmax)) + ']_tmptol' + \
            str(time_diff_threshold) + '.txt'

    # Change time format before saving
    sat1_match_event_idx = [i[0] for i in match_event_idx]
    sat2_match_event_idx = [i[1] for i in match_event_idx]

    sat1_inROI_datetime = [datetime.datetime(2000, 1, 1, 0, 0, 0) + datetime.timedelta(seconds=i) for i in sat1_inROI_time]
    sat2_inROI_datetime = [datetime.datetime(2000, 1, 1, 0, 0, 0) + datetime.timedelta(seconds=i) for i in sat2_inROI_time]

    sat1_starttime  = [sat1_inROI_datetime[sat1_jump_start_idx[i]] for i in sat1_match_event_idx]
    sat1_stoptime   = [sat1_inROI_datetime[sat1_jump_stop_idx[i]] for i in sat1_match_event_idx]
    sat2_starttime  = [sat2_inROI_datetime[sat2_jump_start_idx[i]] for i in sat2_match_event_idx]
    sat2_stoptime   = [sat2_inROI_datetime[sat2_jump_stop_idx[i]] for i in sat2_match_event_idx]

    sat1_startlat  = [sat1_inROI_lat[sat1_jump_start_idx[i]] for i in sat1_match_event_idx]
    sat1_stoplat   = [sat1_inROI_lat[sat1_jump_stop_idx[i]] for i in sat1_match_event_idx]
    sat2_startlat  = [sat2_inROI_lat[sat2_jump_start_idx[i]] for i in sat2_match_event_idx]
    sat2_stoplat   = [sat2_inROI_lat[sat2_jump_stop_idx[i]] for i in sat2_match_event_idx]

    sat1_startlon  = [sat1_inROI_lon[sat1_jump_start_idx[i]] for i in sat1_match_event_idx]
    sat1_stoplon   = [sat1_inROI_lon[sat1_jump_stop_idx[i]] for i in sat1_match_event_idx]
    sat2_startlon  = [sat2_inROI_lon[sat2_jump_start_idx[i]] for i in sat2_match_event_idx]
    sat2_stoplon   = [sat2_inROI_lon[sat2_jump_stop_idx[i]] for i in sat2_match_event_idx]

    sat1_sat2_tmpdist = [i[2] for i in match_event_idx]

    matchup_info = [[sat_1]*len(match_event_idx), sat1_starttime, sat1_stoptime, sat1_startlat, sat1_stoplat, sat1_startlon, sat1_stoplon,\
                    [sat_2]*len(match_event_idx), sat2_starttime, sat2_stoptime, sat2_startlat, sat2_stoplat, sat2_startlon, sat2_stoplon,\
                    sat1_sat2_tmpdist]


    with open(os.path.join(output_path_matchups, fname), 'w') as file:
        file.write("sat1, starttime, stoptime, startlat, stoplat, startlon, stoplon, sat2, starttime, stoptime, startlat, stoplat, startlon, stoplon, temporal_distance\n")
        for x in zip(*matchup_info):
            file.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14}\n".format(*x))

    # endregion

    return None


if __name__ == "__main__":
    pass





