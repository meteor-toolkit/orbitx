"""orbitx.tests.test___init__ - tests for orbitx.__init__"""

import os.path
import unittest
import unittest.mock as mock
from orbitx import add_to_tle_path, setup_orekit

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


class TestInit(unittest.TestCase):
    def test_TLE_path(self):
        from orbitx import TLE_PATH

        self.assertCountEqual(
            TLE_PATH,
            [
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(os.path.dirname(__file__)), "data", "tle"
                    )
                )
            ],
        )

    def test_add_to_tle_path(self):
        add_to_tle_path("test")
        from orbitx import TLE_PATH

        self.assertCountEqual(
            TLE_PATH,
            [
                "test",
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(os.path.dirname(__file__)), "data", "tle"
                    )
                ),
            ],
        )

        add_to_tle_path("test", prepend=False)
        from orbitx import TLE_PATH

        self.assertCountEqual(
            TLE_PATH,
            [
                "test",
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(os.path.dirname(__file__)), "data", "tle"
                    )
                ),
                "test",
            ],
        )

    @mock.patch("orbitx.setup_orekit_curdir")
    def test_setup_orekit_none(self, mock_setup):
        setup_orekit()
        mock_setup.assert_called_with()

    @mock.patch("orbitx.setup_orekit_curdir")
    def test_setup_orekit_path(self, mock_setup):
        setup_orekit("path_to_file")
        mock_setup.assert_called_with(filename="path_to_file")


if __name__ == "__main__":
    unittest.main()
