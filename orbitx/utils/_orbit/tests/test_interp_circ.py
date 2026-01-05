"""orbitx.tests.test_orbit - tests for orbitx.orbit"""

import numpy as np
import unittest
from orbitx.utils._orbit.interp_circ import interp_circ

__author__ = "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>"



class TestInterpCirc(unittest.TestCase):
    def test_interp_circ(self):
        x = np.linspace(0, 86400, 33)
        y = np.concatenate(
            (
                np.linspace(-180, 180, 17, dtype=float)[:-1],
                np.linspace(-180, 180, 17, dtype=float)[:-1],
                [-180],
            )
        )
        
        x_new = np.arange(0, 86400 + 675, 675.)

        exp_res = np.concatenate(
            (
                np.linspace(-180, 180, 65, dtype=float)[:-1],
                np.linspace(-180, 180, 65, dtype=float)[:-1],
                [-180],
            )
        )

        f_interp = interp_circ(x, y)
        res = f_interp(x_new)

        self.assertCountEqual(exp_res, res)

if __name__ == "__main__":
    unittest.main()
