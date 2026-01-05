"""orbitx.tests.test_orbit - tests for orbitx.orbit"""

import numpy as np
import unittest
from orbitx.utils._orbit.get_matching_indices import get_matching_indices

__author__ = "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>"


class TestGetMatchingIndices(unittest.TestCase):
    def test_get_matching_indices(self):
        # attention:
        # When testing this function, tle_time should not contain any value which is smaller than the smallest value of
        # sim_time, or greater than the greatest value of sim_time, because we force this onto the process. There is
        # only one exception to this rule, and that is when the [start-time, end-time] is so short, that there is no
        # TLE in between. In that case, we use the closest available TLE to propagate the orbit, and the case is handled
        # as an exception.

        tle_time = [1, 4, 7, 10, 15, 17]  # These are the TLE time stamps
        sim_time = [
            1,
            1.5,
            2,
            3,
            4.2,
            6.7,
            8,
            9,
            10,
            78,
        ]  # These are the simulation (propagation) time stamps

        exp_idx_tle = np.array(
            [
                0,
                1,
                2,
                3,
                5,
            ]
        )  # These are the indices of the corresponding time stamps in TLE time vector
        exp_idx_sim = np.array(
            [
                0,
                4,
                6,
                8,
                9,
            ]
        )  # These are the indices of the corresponding time stamps in simulation vector

        idx_sim, idx_tle = get_matching_indices(np.array(sim_time), np.array(tle_time))

        self.assertCountEqual(exp_idx_tle, idx_tle)
        self.assertCountEqual(exp_idx_sim, idx_sim)


if __name__ == "__main__":
    unittest.main()
