"""A python function to determine the times at which the orbits should be computed"""

"""___Third-Party Modules___"""
import numpy as np
from typing import Tuple, Union

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._date_utils import datetime64_to_sec_since, sec_since_to_datetime64

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"


def form_sample_space(
    start_date: np.datetime64,
    end_date: np.datetime64,
    propagation_sampling_interval: np.timedelta64,
    reference_date: np.datetime64 = np.datetime64("1970-01-01T00:00:00"),
) -> Tuple[list, np.ndarray]:
    """
    Return a time vector containing desired orbit simulation timestamps

    :param start_time: start of time window
    :param end_time: end of time window
    :param prop_smpl_interval: propagation sampling interval in seconds
    :return: tuple containing elements - list of temporal sampling space in datetime, and list of temporal sampling
    space in 'seconds since 1970'
    """
    end_date = end_date + propagation_sampling_interval
    sample_space_date = np.arange(
        start=start_date,
        stop=end_date,
        step=propagation_sampling_interval,
    )  # 'propagation_sampling_interval' has been added to the second element to make the 'smpl_space_secs_since_1970' vector
    # long enough to contain 'end_time'.

    sample_space_secs_since = np.array(
        [datetime64_to_sec_since(i, reference_date) for i in sample_space_date],
        dtype=float,
    )

    return sample_space_date, sample_space_secs_since
