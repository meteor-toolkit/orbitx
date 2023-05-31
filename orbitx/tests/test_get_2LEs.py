"""orbitx.test.test_get_2LEs - tests for orbitx.get_2LEs"""
import os.path
import random
import string
import shutil
import unittest
from orbitx.get_tle import return_tle_path, get_tle
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


class TestGetTLE(unittest.TestCase):
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
        self.assertEqual(
            return_tle_path("S2A"), os.path.abspath("../data/tle/TLEset_S2A.txt")
        )

    def test_return_tle_path_first(self):
        add_to_tle_path(self.tmp_tle_path1, prepend=True)
        add_to_tle_path(self.tmp_tle_path2, prepend=False)

        self.assertEqual(
            return_tle_path("S2A"),
            os.path.abspath(os.path.join(self.tmp_tle_path1, "TLEset_S2A.txt")),
        )
        self.assertEqual(
            return_tle_path("XXX"),
            os.path.abspath(os.path.join(self.tmp_tle_path2, "TLEset_XXX.txt")),
        )

    def test_get_tle(self):

        # define input parameters
        start_time = dt(2015, 6, 24, 0, 0, 0)
        end_time = dt(2015, 6, 26, 0, 0, 0)
        satellite_name = "S2A"

        # run code under test
        tles = get_tle(
            start_time=start_time,
            end_time=end_time,
            satellite_name=satellite_name
        )

        # define expected output
        exp_first_lines = [
            "1 40697U 15028A   15175.89500181 -.00000501  00000+0 -17382-3 0  9994",
            "1 40697U 15028A   15176.80399346 -.00024242  00000+0 -91643-2 0  9994"
        ]
        exp_second_lines = [
            "2 40697  98.5715 250.2152 0000954 179.7525 180.3523 14.30975526   266",
            "2 40697  98.5705 251.1120 0002131 229.6310 131.1858 14.31372223   391"
        ]
        exp_times = [12341234345.2, 3242345246.3]

        exp_tles = (
            exp_first_lines,
            exp_second_lines,
            exp_times
        )

        # compare expected and actual output
        for tle_elem, exp_tle_elem in zip(tles, exp_tles):
            self.assertCountEqual(tle_elem, exp_tle_elem)


if __name__ == "__main__":
    unittest.main()
