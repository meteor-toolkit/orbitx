"""orbitx.tests.test_tle - tests for orbitx.tle"""

import unittest

from orbitx.utils._tle import get_classification

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


example_0 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
result_0 = "Unclassified"
example_1 = "1 25544C 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
result_1 = "Classified"
example_2 = "1 25544S 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
result_2 = "Secret"
example_error = "1 25544X 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"



class TestGetClassification(unittest.TestCase):
    def test_example_0(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_0, get_classification(example_0))
        
    def test_example_1(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_1, get_classification(example_1))

    def test_example_2(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_2, get_classification(example_2))

    def test_example_error(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertRaises(
            ValueError,
            lambda: get_classification(example_error)
        )

if __name__ == "__main__":
    unittest.main()
