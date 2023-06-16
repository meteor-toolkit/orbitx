"""orbitx.test.test___init__ - tests for orbitx.__init__"""
import os.path
import unittest
from orbitx import add_to_tle_path, setup_orekit_curdir

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


class TestInit(unittest.TestCase):
    def test_TLE_path(self):
        from orbitx import TLE_PATH

        self.assertCountEqual(TLE_PATH, [os.path.abspath("../data/tle")])

    def test_add_to_tle_path(self):
        add_to_tle_path("test")
        from orbitx import TLE_PATH

        self.assertCountEqual(TLE_PATH, ["test", os.path.abspath("../data/tle")])

        add_to_tle_path("test", prepend=False)
        from orbitx import TLE_PATH

        self.assertCountEqual(
            TLE_PATH, ["test", os.path.abspath("../data/tle"), "test"]
        )

    def test_setup_orekit_curdir(self):
        setup_orekit_curdir()


if __name__ == "__main__":
    unittest.main()
