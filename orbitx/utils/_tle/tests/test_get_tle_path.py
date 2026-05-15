"""orbitx.tests.test_tle - tests for orbitx.tle"""

import unittest
import os

from orbitx.utils._tle import get_tle_path

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


this_directory = os.path.dirname(__file__)
example_0 = "S2A"
result_0 = os.path.abspath(
    (os.path.join(this_directory, "../../../data/tle/TLEset_S2A.txt"))
)


class TestGetTLEPath(unittest.TestCase):
    def test_example_0(self):
        """"""
        self.assertEqual(result_0.lower(), get_tle_path(example_0).lower())


if __name__ == "__main__":
    unittest.main()
