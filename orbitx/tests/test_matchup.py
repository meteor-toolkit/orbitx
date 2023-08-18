import unittest
import unittest.mock as mock

import numpy as np

from orbitx.matchup import Matchups


class TestMatchups(unittest.TestCase):

    def test_get_distance(self):
        pass

    @mock.patch("orbitx.matchup.get_distance")
    def test_matchup(self, mock_get_distance):
        input_orbits = {
            "S3A": {
                "lat": np.arange(-10, 10),
                "lon": (np.arange(-10, 10) ** 2) - 30,
                "time": [float(i) for i in np.arange(20)],
            },
            "LS8": {
                "lat": np.arange(-10, 10),
                "lon": -(np.arange(-10, 10) ** 2),
                "time": [float(i) for i in np.arange(20)],
            },
        }
        matchup = Matchups()
        self.assertEqual(matchup.matchup(input_orbits, 3, 1, 400), ())

    def test_to_ds(self):
        pass

    def test_save(self):
        pass


if __name__ == "__main__":
    unittest.main()
