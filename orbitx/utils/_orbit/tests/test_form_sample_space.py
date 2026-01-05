"""orbitx.tests.test_orbit - tests for orbitx.orbit"""

import numpy as np
import unittest
from orbitx.utils._orbit.form_sample_space import form_sample_space

__author__ = "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>"

class TestFormSampleSpace(unittest.TestCase):
    def test_form_sample_space(self):
        # Start at 1st of Jan. 1970, and sample every 12 hours until 2nd of Jan. 1970, one o'clock am.
        start_date = np.datetime64("1970-01-01T00:00:00")
        end_date = np.datetime64("1970-01-02T01:00:00")
        prop_smpl_interval = 12 * 60 * 60

        # We are expecting 4 samples:
        exp_smpl_space = [
            np.datetime64("1970-01-01T00:00:00"),
            np.datetime64("1970-01-01T12:00:00"),
            np.datetime64("1970-01-02T00:00:00"),
            np.datetime64("1970-01-02T12:00:00"),
        ]
        exp_smpl_space_secs_since_1970 = np.array([0.0, 43200.0, 86400.0, 129600.0])

        smpl_space, smpl_space_secs_since_1970 = form_sample_space(
            start_date, end_date, prop_smpl_interval
        )

        self.assertCountEqual(exp_smpl_space, smpl_space)
        self.assertCountEqual(
            exp_smpl_space_secs_since_1970, smpl_space_secs_since_1970
        )

if __name__ == "__main__":
    unittest.main()
