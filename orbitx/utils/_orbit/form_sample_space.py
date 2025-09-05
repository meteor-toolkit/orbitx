"""A python function to determine the times at which the orbits should be computed"""

"""___Third-Party Modules___"""
import datetime
import numpy as np
from typing import Tuple, Union

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._date_utils import datetime_to_sec_since, sec_since_to_datetime

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"


def form_sample_space(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    prop_smpl_interval: Union[float, int],
    reference_date:datetime.datetime = datetime.datetime(1970, 1, 1, 0, 0, 0)
) -> Tuple[list, np.ndarray]:
    """
    Return a time vector containing desired orbit simulation timestamps

    :param start_time: start of time window
    :param end_time: end of time window
    :param prop_smpl_interval: propagation sampling interval in seconds
    :return: tuple containing elements - list of temporal sampling space in datetime, and list of temporal sampling
    space in 'seconds since 1970'
    """

    start_time = datetime_to_sec_since(start_date, reference_date)

    end_time = datetime_to_sec_since(end_date, reference_date)

    smpl_space_secs_since = np.arange(
        start_time,
        end_time + prop_smpl_interval,
        prop_smpl_interval,
    )  # 'prop_smpl_interval' has been added to the second element to make the 'smpl_space_secs_since_1970' vector
    # long enough to contain 'end_time'.

    smpl_space = np.array(
        [
            sec_since_to_datetime(i, reference_date) for i in smpl_space_secs_since
        ]
    )

    return smpl_space, smpl_space_secs_since