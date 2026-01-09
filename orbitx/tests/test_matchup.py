"""orbitx.tests.test_matchup - tests for orbitx.matchup"""

import unittest
import unittest.mock as mock
import os

import numpy as np
import xarray as xr

from orbitx import Matchups
from orbitx.utils._matchups.get_dist import get_dist
from orbitx import Orbit

__author__ = "Mattea Goalen <mattea.goalen@npl.co.uk>"


class TestMatchups(unittest.TestCase):
    def test_from_orbit(self):
        satellites = ["CS2", "J3"]
        start_date = np.datetime64("2012-01-01T00:00:00")
        end_date = np.datetime64("2012-01-01T12:00:00")
        propagation_sampling_interval = np.array(60, dtype="timedelta64[s]")
        interpolation_sampling_interval = np.array(5, dtype="timedelta64[s]")
        time_diff_threshold = np.array(900, dtype="timedelta64[s]")
        space_diff_threshold = 290
        check_before = False
        check_after = False
        has_land_ocean_mask = False
        orbit = Orbit.simulate(
            satellites=satellites,
            start_date=start_date,
            end_date=end_date,
            propagation_sampling_interval=propagation_sampling_interval,
            interpolation_sampling_interval=interpolation_sampling_interval,
            reference_date=np.datetime64("1970-01-01T00:00:00"),
        )
        orbit_ds = orbit.orbits

        matchups = Matchups.from_orbit(
            orbit=orbit,
            start_date=start_date,
            end_date=end_date,
            space_diff_threshold=space_diff_threshold,
            time_diff_threshold=time_diff_threshold,
            check_after=check_after,
            check_before=check_before,
            has_land_ocean_mask=has_land_ocean_mask,
        )
        matchups_ds = matchups.matchups

        for sat in satellites:
            matchup_sat = matchups_ds.sel(satellite=sat)
            orbit_sat = orbit_ds.sel(satellite=sat)
            match_time = matchup_sat["time"].values
            orbit_time = orbit_sat["time"].values
            self.assertTrue(np.all([mtime in orbit_time for mtime in match_time]))
            for matchup_index in matchups_ds["matchup_index"].values:
                time = match_time[matchup_index]
                lat_match = matchup_sat.sel(matchup_index=matchup_index)["lat"].values
                lon_match = matchup_sat.sel(matchup_index=matchup_index)["lon"].values

                lat_orbit = orbit_sat.sel(time=time)["lat"].values
                lon_orbit = orbit_sat.sel(time=time)["lon"].values
                np.testing.assert_almost_equal(lat_match, lat_orbit)
                np.testing.assert_almost_equal(lon_match, lon_orbit)


if __name__ == "__main__":
    unittest.main()
