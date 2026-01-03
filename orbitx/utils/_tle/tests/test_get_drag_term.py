"""orbitx.tests.test_tle - tests for orbitx.tle"""

import unittest

from orbitx.utils._tle import get_drag_term

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


example_0 = "1 25544U 98067A   08264.51782528 -.00002182  12345-5 -11606-4 0  2927"
result_0: float = -1.1606e-5
example_1 = "1 25544U 98067A   08264.51782528 -.00002182  12345-5 -11606+4 0  2927"
result_1: float = -1.1606e3
example_2 = "1 25544U 98067A   08264.51782528 -.00002182  12345-5  11606-4 0  2927"
result_2: float = 1.1606e-5
example_3 = "1 25544U 98067A   08264.51782528 -.00002182  12345-5  11606+4 0  2927"
result_3: float = 1.1606e3



class TestGetDragTerm(unittest.TestCase):
    def test_example_0(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_0, get_drag_term(example_0))

    def test_example_1(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_1, get_drag_term(example_1))
        
    def test_example_2(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_2, get_drag_term(example_2))
        
    def test_example_3(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_3, get_drag_term(example_3))

if __name__ == "__main__":
    unittest.main()
