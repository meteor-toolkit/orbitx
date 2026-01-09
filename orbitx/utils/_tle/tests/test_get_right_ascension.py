"""orbitx.tests.test_tle - tests for orbitx.tle"""

import unittest

from orbitx.utils._tle import get_right_ascension

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


example_0 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
result_0 = 247.4627


class TestGetRightAscension(unittest.TestCase):
    def test_example_0(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """
        self.assertEqual(result_0, get_right_ascension(example_0))


if __name__ == "__main__":
    unittest.main()
