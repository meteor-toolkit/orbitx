"""A python function to determine the times at which the orbits should be computed"""

"""___Third-Party Modules___"""
import datetime
import numpy as np
from typing import Tuple, Union

"""___NPL Modules___"""

"""__Built-In Modules__"""


"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"


def form_sample_space(
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    prop_smpl_interval: Union[float, int],
) -> Tuple[list, np.ndarray]:
    """
    Return a time vector containing desired orbit simulation timestamps

    :param start_time: start of time window
    :param end_time: end of time window
    :param prop_smpl_interval: propagation sampling interval in seconds
    :return: tuple containing elements - list of temporal sampling space in datetime, and list of temporal sampling
    space in 'seconds since 1970'
    """

    time_since = start_time - datetime.datetime(1970, 1, 1, 0, 0, 0)
    start_time_secs_since_1970 = time_since.total_seconds()

    time_since = end_time - datetime.datetime(1970, 1, 1, 0, 0, 0)
    end_time_secs_since_1970 = time_since.total_seconds()

    smpl_space_secs_since_1970 = np.arange(
        start_time_secs_since_1970,
        end_time_secs_since_1970 + prop_smpl_interval,
        prop_smpl_interval,
    )  # 'prop_smpl_interval' has been added to the second element to make the 'smpl_space_secs_since_1970' vector
    # long enough to contain 'end_time'.

    smpl_space = np.array(
        [
            datetime.datetime(1970, 1, 1, 0, 0, 0) + datetime.timedelta(seconds=i)
            for i in smpl_space_secs_since_1970
        ]
    )

    return smpl_space, smpl_space_secs_since_1970