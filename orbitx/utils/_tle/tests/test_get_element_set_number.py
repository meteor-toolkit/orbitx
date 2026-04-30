"""orbitx.tests.test_tle - tests for orbitx.tle"""

import unittest

from orbitx.utils._tle import get_element_set_number

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


example_0 = "1 25544U 98067A   08264.51782528 -.00002182  12345-5 -11606-4 0  2927"
result_0 = 292


class TestGetElementSetNumber(unittest.TestCase):
    def test_example_0(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_0, get_element_set_number(example_0))


if __name__ == "__main__":
    unittest.main()
