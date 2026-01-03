"""orbitx.tests.test_tle - tests for orbitx.tle"""

import unittest

from orbitx.utils._tle import get_launch_year

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


example_0 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
result_0 = 1998
example_1 = "1 25544U 24067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
result_1 = 2024


class TestGetLaunchYear(unittest.TestCase):
    def test_example_0(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_0, get_launch_year(example_0))
        
    def test_example_1(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_1, get_launch_year(example_1))

if __name__ == "__main__":
    unittest.main()
