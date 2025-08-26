"""A Python function to determine which two-line element to use when simulating orbits"""

"""___Third-Party Modules___"""
import numpy as np
from typing import Tuple

"""___NPL Modules___"""

"""__Built-In Modules__"""


"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"



def get_matching_indices(
    sim_time: np.ndarray,
    tle_time: np.ndarray
) -> Tuple[list, list]:
    """
    Locate the index of the closest two line element (at a time equal to or smaller than the simulation time) and
    return the matching pointers/indices.

    :param sim_time: a vector of time containing all the instances when we want to simulate the orbit
    :param tle_time: a vector of time containing all tle instances
    :return: tuple of lists containing corresponding indices between simulation space and tle references
    """

    idx_tle = np.array(range(len(tle_time)))
    idx_sim = np.empty(idx_tle.shape, int)
    idx_redundant = []

    # Find corresponding indices of tle and simulation time vectors
    for i in idx_tle:
        idx_sim[i] = np.argmax(
            sim_time >= tle_time[i]
        )  # idx_sim[i] contains the index of the smallest simulation time that is larger than tle_time[i]
        # If no such simulation time exists, it is set to 0

    # Find redundant tle time references
    idx_sim_unique = np.unique(idx_sim)
    for j in range(len(idx_sim_unique)):
        idx = idx_sim == idx_sim_unique[j]
        if sum(idx) > 1:
            loc = [i for i, val in enumerate(idx) if val]
            for k in range(len(loc) - 1):
                idx_redundant.append(loc[k])

    # Delete redundant tle time references
    idx_tle = np.delete(idx_tle, idx_redundant)
    idx_sim = np.delete(idx_sim, idx_redundant)

    # Force the idx_sim to include the start_time and end_time stamps
    idx_sim[0] = 0
    idx_sim[-1] = len(sim_time) - 1
    return idx_sim, idx_tle