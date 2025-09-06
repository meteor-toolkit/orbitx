"""orbitx.tests.test_tle - tests for orbitx.tle"""

import numpy as np
import os.path
import random
import string
import shutil
import unittest
from orbitx.tle import TLEInfo
from orbitx import add_to_tle_path
from pathlib import Path
from datetime import datetime as dt


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


sample_S2A_tle_data = "SENTINEL-2A             \n\
1 40697U 15028A   15174.15999288 -.00000044  00000+0  00000+0 0  9998\n\
2 40697  98.5847 248.5254 0000798 283.7898 143.4888 14.31066438    11\n\
SENTINEL-2A             \n\
1 40697U 15028A   15174.21686542 -.00000044  00000+0  00000+0 0  9991\n\
2 40697  98.5822 248.5857 0001125  72.2447 287.8522 14.30945090    27\n\
SENTINEL-2A             \n\
1 40697U 15028A   15174.35671963 -.00000044  00000+0  00000+0 0  9997\n\
2 40697  98.5798 248.7128 0002400 151.8089 208.3654 14.30980662    45\n\
SENTINEL-2A             \n\
1 40697U 15028A   15174.84616994 -.00000044  00000+0  00000+0 0  9994\n\
2 40697  98.5727 249.1811 0001221 155.7341 204.3855 14.30973291   112\n\
SENTINEL-2A             \n\
1 40697U 15028A   15175.89500181 -.00000501  00000+0 -17382-3 0  9994\n\
2 40697  98.5715 250.2152 0000954 179.7525 180.3523 14.30975526   266\n\
SENTINEL-2A             \n\
1 40697U 15028A   15176.80399346 -.00024242  00000+0 -91643-2 0  9994\n\
2 40697  98.5705 251.1120 0002131 229.6310 131.1858 14.31372223   391\n\
SENTINEL-2A             \n\
1 40697U 15028A   15177.01356401  .00032839  00000+0  12341-1 0  9999\n\
2 40697  98.5716 251.3199 0001968 239.9584 120.1644 14.31404980   426"


class TestTLE(unittest.TestCase):
    def setUp(self) -> None:
        tmp_dir_name1 = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        tmp_dir_name2 = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))

        self.tmp_tle_path1 = os.path.join(os.path.dirname(__file__), tmp_dir_name1)
        self.tmp_tle_path2 = os.path.join(os.path.dirname(__file__), tmp_dir_name2)

        os.makedirs(self.tmp_tle_path1)
        os.makedirs(self.tmp_tle_path2)

        with open(os.path.join(self.tmp_tle_path1, "TLEset_S2A.txt"), "w") as f:
            f.write(sample_S2A_tle_data)

        Path(os.path.join(self.tmp_tle_path2, "TLEset_XXX.txt")).touch()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_tle_path1)
        shutil.rmtree(self.tmp_tle_path2)

    def test_return_tle_path(self):
        tle = TLEInfo()
        self.assertEqual(
            tle.return_tle_path("S2A"),
            os.path.abspath(
                os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "data",
                    "tle",
                    "TLEset_S2A.txt",
                )
            ),
        )

    def test_return_tle_path_first(self):
        add_to_tle_path(self.tmp_tle_path1, prepend=True)
        add_to_tle_path(self.tmp_tle_path2, prepend=False)

        tle = TLEInfo()
        self.assertEqual(
            tle.return_tle_path("S2A"),
            os.path.abspath(os.path.join(self.tmp_tle_path1, "TLEset_S2A.txt")),
        )
        self.assertEqual(
            tle.return_tle_path("XXX"),
            os.path.abspath(os.path.join(self.tmp_tle_path2, "TLEset_XXX.txt")),
        )

    def test_date_from_TLE(self):
        tle_line_1 = (
            "1 40697U 15028A   15174.15999288 -.00000044  00000+0  00000+0 0  9998"
        )

        tle = TLEInfo()
        date = tle.return_date_from_tle(tle_line_1)

        exp_date = dt(2015, 6, 23, 3, 50, 23, 384832)

        self.assertEqual(date.year, exp_date.year)
        self.assertEqual(date.month, exp_date.month)
        self.assertEqual(date.day, exp_date.day)
        self.assertEqual(date.hour, exp_date.hour)
        self.assertEqual(date.minute, exp_date.minute)
        self.assertEqual(date.second, exp_date.second)

    def test_get_tle(self):
        # define input parameters
        start_date = dt(2015, 6, 24, 0, 0, 0)
        end_date = dt(2015, 6, 26, 0, 0, 0)
        satellite_name = "S2A"

        # run code under test
        tle = TLEInfo()
        tles = tle.get_tle(
            start_date=start_date, end_date=end_date, satellite=satellite_name
        )
        # define expected output
        exp_first_lines = [
            "1 40697U 15028A   15174.84616994 -.00000044  00000+0  00000+0 0  9994",
            "1 40697U 15028A   15175.89500181 -.00000501  00000+0 -17382-3 0  9994",
            "1 40697U 15028A   15176.80399346 -.00024242  00000+0 -91643-2 0  9994",
        ]
        exp_second_lines = [
            "2 40697  98.5727 249.1811 0001221 155.7341 204.3855 14.30973291   112",
            "2 40697  98.5715 250.2152 0000954 179.7525 180.3523 14.30975526   266",
            "2 40697  98.5705 251.1120 0002131 229.6310 131.1858 14.31372223   391",
        ]

        # The expected time since 1970 for each relevant TLE cab be calculated as follows. Take line 1 of
        # "1 40697U 15028A   15175.89500181 -.00000501  00000+0 -17382-3 0  9994\n" for instance;
        # Day 175 of year 2015 is June 24. The decimal days .89500181 equals hour 21, minute 28 and second 48.156384 of
        # same day. Below the decimal seconds are added up separately.
        # 1435181328.156384 = (dt(2015, 6, 24, 21, 28, 48) - dt(1970, 1, 1, 0, 0, 0)).total_seconds() + .156384
        # 1435259865.034944 = (dt(2015, 6, 25, 19, 17, 45) - dt(1970, 1, 1, 0, 0, 0)).total_seconds() + .034943999999996
        exp_times = [1435090709.082816, 1435181328.156384, 1435259865.034944]

        # compare expected and actual output
        for l1, exp_l1 in zip(tles[0], exp_first_lines):
            self.assertEqual(l1, exp_l1)

        for l2, exp_l2 in zip(tles[1], exp_second_lines):
            self.assertEqual(l2, exp_l2)

        np.testing.assert_array_almost_equal(tles[2], exp_times)

    def test_get_tle_(self):
        """
        This is to test a situation when there is no TLE within the [start_date, end_date]
        """

        # define input parameters
        start_date = dt(2015, 6, 24, 22, 0, 0)
        end_date = dt(2015, 6, 24, 23, 0, 0)
        satellite_name = "S2A"

        # run code under test
        tle = TLEInfo()
        tles = tle.get_tle(
            start_date=start_date, end_date=end_date, satellite=satellite_name
        )

        # define expected output
        exp_first_lines = [
            "1 40697U 15028A   15175.89500181 -.00000501  00000+0 -17382-3 0  9994",
        ]
        exp_second_lines = [
            "2 40697  98.5715 250.2152 0000954 179.7525 180.3523 14.30975526   266",
        ]

        exp_times = [1435181328.156384]

        # compare expected and actual output
        for l1, exp_l1 in zip(tles[0], exp_first_lines):
            self.assertEqual(l1, exp_l1)

        for l2, exp_l2 in zip(tles[1], exp_second_lines):
            self.assertEqual(l2, exp_l2)

        np.testing.assert_array_almost_equal(tles[2], exp_times)


if __name__ == "__main__":
    unittest.main()
