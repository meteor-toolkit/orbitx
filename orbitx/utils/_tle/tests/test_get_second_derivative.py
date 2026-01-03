"""orbitx.tests.test_tle - tests for orbitx.tle"""

import unittest

from orbitx.utils._tle import get_second_derivative

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


example_0 = "1 25544U 98067A   08264.51782528 -.00002182 -12345-5 -11606-4 0  2927"
result_0 = -1.2345e-6
example_1 = "1 25544U 98067A   08264.51782528 -.00002182 -12345+5 -11606-4 0  2927"
result_1 = -1.2345e4
example_2 = "1 25544U 98067A   08264.51782528 -.00002182  12345-5 -11606-4 0  2927"
result_2 = 1.2345e-6
example_3 = "1 25544U 98067A   08264.51782528 -.00002182  12345+5 -11606-4 0  2927"
result_3 = 1.2345e4


class TestGetSecondDerivative(unittest.TestCase):
    def test_example_0(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertAlmostEqual(result_0, get_second_derivative(example_0))
        
    def test_example_1(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_1, get_second_derivative(example_1))
        
    def test_example_2(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertAlmostEqual(result_2, get_second_derivative(example_2))
        
    def test_example_3(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_3, get_second_derivative(example_3))

if __name__ == "__main__":
    unittest.main()
