"""orbitx.tests.test_tle - tests for orbitx.tle"""

import unittest

from orbitx.utils._tle import get_mean_anomaly

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


example_0 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
result_0 = 325.0288


class TestGetMeanAnomaly(unittest.TestCase):
    def test_example_0(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_0, get_mean_anomaly(example_0))

if __name__ == "__main__":
    unittest.main()
