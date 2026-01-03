"""orbitx.tests.test_tle - tests for orbitx.tle"""

import unittest
import numpy as np

from orbitx.utils._tle import get_tle_date

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


example_0 = "1 25544U 98067A   08264.51782528 -.00002182  12345-5 -11606-4 0  2927"
result_0 = np.array("2008-09-20T12:25:40.104192", dtype="datetime64[us]")
example_1 = "1 25544U 98067A   86 50.28438588 -.00002182  12345-5 -11606-4 0  2927"
result_1 = np.array("1986-02-19T06:49:30.940032", dtype="datetime64[us]")


class TestGetTLEDate(unittest.TestCase):
    def test_example_0(self):
        """
        The line is
        1 25544U 98067A   08264.51782528 -.00002182  12345-5 -11606-4 0  2927
                          ^^^^^^^^^^^^^^
        The year string is 08 hence the year is 2008
        The number of days is 264.51782528 days (Days = 264)
        264.51782528 days - 264 = 0.51782528 days
        0.51782528 days x 24 hours/day = 12.427806720000001 hours (Hours = 12)
        12.427806720000001 hours - 12 = 0.427806720000001 hours
        0.427806720000001 hours x 60 minutes/hour = 25.668403200000057 minutes (Minutes = 25)
        25.668403200000057 - 25 = 0.668403200000057 minutes
        0.668403200000057 minutes x 60 seconds/minute = 40.10419200000342 seconds (Seconds = 30.94)
        """
        self.assertEqual(result_0, get_tle_date(example_0))
        
    def test_example_1(self):
        """
        The line is
        1 25544U 98067A   86 50.28438588 -.00002182  12345-5 -11606-4 0  2927
                          ^^^^^^^^^^^^^^
        The year string is 86 hence the year is 1986
        The number of days is 50.28438588 days (Days = 50)
        50.28438588 days - 50 = 0.28438588 days
        0.28438588 days x 24 hours/day = 6.8253 hours (Hours = 6)
        6.8253 hours - 6 = 0.8253 hours
        0.8253 hours x 60 minutes/hour = 49.5157 minutes (Minutes = 49)
        49.5157 - 49 = 0.5157 minutes
        0.5157 minutes x 60 seconds/minute = 30.94 seconds (Seconds = 30.94)
        """
        self.assertEqual(result_1, get_tle_date(example_1))

if __name__ == "__main__":
    unittest.main()
