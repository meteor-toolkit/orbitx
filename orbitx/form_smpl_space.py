import datetime
import numpy as np


def form_smpl_space(start_time, end_time, prop_smpl_interval):
    """
    This function receives the start and end time of propagation, and the sampling interval for propagation and
    generates a vector of time of all instances when we want to simulate the orbit.
    """

    time_since = start_time - datetime.datetime(2000, 1, 1, 0, 0, 0)
    start_time_secs_since_2000 = time_since.total_seconds()

    time_since = end_time - datetime.datetime(2000, 1, 1, 0, 0, 0)
    end_time_secs_since_2000 = time_since.total_seconds()

    smpl_space_secs_since_2000 = np.arange(
        start_time_secs_since_2000, end_time_secs_since_2000, prop_smpl_interval
    )

    smpl_space = [
        datetime.timedelta(seconds=i) + datetime.datetime(2000, 1, 1, 0, 0, 0)
        for i in smpl_space_secs_since_2000
    ]

    return (smpl_space, smpl_space_secs_since_2000)
