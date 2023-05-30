"""orbitx.test.test_get_2LEs - tests for orbitx.get_2LEs"""
import os.path
import random
import string
import shutil
import unittest
from orbitx.get_2LEs import return_tle_path
from orbitx import add_to_tle_path
from pathlib import Path


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


class TestGet2LEs(unittest.TestCase):
    def setUp(self) -> None:
        tmp_dir_name1 = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        tmp_dir_name2 = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))

        self.tmp_tle_path1 = os.path.join(os.path.dirname(__file__), tmp_dir_name1)
        self.tmp_tle_path2 = os.path.join(os.path.dirname(__file__), tmp_dir_name2)

        os.makedirs(self.tmp_tle_path1)
        os.makedirs(self.tmp_tle_path2)

        Path(os.path.join(self.tmp_tle_path1, 'TLEset_S2A.txt')).touch()
        Path(os.path.join(self.tmp_tle_path2, 'TLEset_XXX.txt')).touch()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_tle_path1)
        shutil.rmtree(self.tmp_tle_path2)

    def test_return_tle_path(self):
        self.assertEqual(return_tle_path("S2A"), os.path.abspath("../data/tle/TLEset_S2A.txt"))

    def test_return_tle_path_first(self):
        add_to_tle_path(self.tmp_tle_path1, prepend=True)
        add_to_tle_path(self.tmp_tle_path2, prepend=False)

        self.assertEqual(return_tle_path("S2A"), os.path.abspath(os.path.join(self.tmp_tle_path1, "TLEset_S2A.txt")))
        self.assertEqual(return_tle_path("XXX"), os.path.abspath(os.path.join(self.tmp_tle_path2, "TLEset_XXX.txt")))


if __name__ == "__main__":
    unittest.main()
