import unittest

import numpy as np

from orbitx.matchup_test import matchup


class MyTestCase(unittest.TestCase):
    def test_matchup(self):
        input_orbits = {"S3A":
                            {"lat": np.arange(-10, 10), "lon": (np.arange(-10, 10)**2)-30, "time": [float(i) for i in np.arange(20)]},
                        "LS8":
                            {"lat": np.arange(-10, 10), "lon": -(np.arange(-10, 10)**2), "time": [float(i) for i in np.arange(20)]}
                        }

        self.assertEqual(matchup(input_orbits, 3, 1, 400), ())


if __name__ == "__main__":
    unittest.main()
