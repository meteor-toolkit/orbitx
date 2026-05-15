"""orbitx.tests.test_matchup - tests for orbitx.matchup"""

import unittest

import numpy as np
import xarray as xr

from orbitx import Matchups
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


class TestMatchupsEvents(unittest.TestCase):
    """Tests for Matchups.events — uses synthetic data, no orekit required."""

    _ATTRS = {
        "satellite_name": ["Sat1", "Sat2"],
        "satellite_shortname": ["S1", "S2"],
        "start_date": 0.0,
        "end_date": 86400.0,
        "time_diff_threshold": 900,
        "space_diff_threshold": 290.0,
        "check_before": 0,
        "check_after": 0,
        "has_land_ocean_mask": 0,
        "creation_date": "2024-01-01",
        "version": "test",
    }

    def _make_matchups(self, times_sat1, times_sat2, lats, lons):
        n = len(times_sat1)
        time_datetime = np.stack([times_sat1, times_sat2], axis=1)
        ds = xr.Dataset(
            {
                "time_datetime": (["matchup_index", "satellite"], time_datetime),
                "lat": (["matchup_index", "satellite"], lats),
                "lon": (["matchup_index", "satellite"], lons),
                "reference_date": np.datetime64("1970-01-01T00:00:00"),
            },
            coords={"matchup_index": np.arange(n), "satellite": ["S1", "S2"]},
            attrs=self._ATTRS,
        )
        data = xr.DataTree()
        data["matchups"] = xr.DataTree(dataset=ds)
        data["orbits"] = xr.DataTree()
        return Matchups(data)

    def _make_empty_matchups(self):
        ds = xr.Dataset(
            {
                "time_datetime": (
                    ["matchup_index", "satellite"],
                    np.empty((0, 2), dtype="datetime64[s]"),
                ),
                "lat": (["matchup_index", "satellite"], np.empty((0, 2))),
                "lon": (["matchup_index", "satellite"], np.empty((0, 2))),
                "reference_date": np.datetime64("1970-01-01T00:00:00"),
            },
            coords={"matchup_index": np.arange(0), "satellite": ["S1", "S2"]},
            attrs=self._ATTRS,
        )
        data = xr.DataTree()
        data["matchups"] = xr.DataTree(dataset=ds)
        data["orbits"] = xr.DataTree()
        return Matchups(data)

    def test_events_empty(self):
        m = self._make_empty_matchups()
        self.assertEqual(m.events, [])

    def test_events_single_event(self):
        t0 = np.datetime64("2020-01-01T00:00:00")
        times_sat1 = np.array([t0, t0 + np.timedelta64(2, "m"), t0 + np.timedelta64(4, "m")])
        times_sat2 = np.array([t0 + np.timedelta64(5, "m"), t0 + np.timedelta64(7, "m"), t0 + np.timedelta64(9, "m")])
        lats = np.array([[40.0, 41.0], [41.0, 42.0], [42.0, 43.0]])
        lons = np.array([[10.0, 11.0], [11.0, 12.0], [12.0, 13.0]])
        m = self._make_matchups(times_sat1, times_sat2, lats, lons)

        events = m.events
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["start_time"], t0)
        self.assertEqual(events[0]["stop_time"], t0 + np.timedelta64(9, "m"))
        self.assertEqual(events[0]["bbox"], (10.0, 40.0, 13.0, 43.0))
        self.assertEqual(events[0]["n_matchups"], 3)
        self.assertFalse(events[0]["crosses_antimeridian"])

    def test_events_crosses_antimeridian(self):
        t0 = np.datetime64("2020-01-01T00:00:00")
        times_sat1 = np.array([t0, t0 + np.timedelta64(2, "m")])
        times_sat2 = np.array([t0 + np.timedelta64(5, "m"), t0 + np.timedelta64(7, "m")])
        lats = np.array([[10.0, 11.0], [11.0, 12.0]])
        lons = np.array([[-179.0, 179.0], [-178.0, 178.0]])
        m = self._make_matchups(times_sat1, times_sat2, lats, lons)

        self.assertTrue(m.events[0]["crosses_antimeridian"])

    def test_events_multiple_events(self):
        t0 = np.datetime64("2020-01-01T00:00:00")
        t1 = t0 + np.timedelta64(2, "h")
        times_sat1 = np.array([t0, t0 + np.timedelta64(5, "m"), t1, t1 + np.timedelta64(5, "m")])
        times_sat2 = np.array(
            [
                t0 + np.timedelta64(3, "m"),
                t0 + np.timedelta64(8, "m"),
                t1 + np.timedelta64(3, "m"),
                t1 + np.timedelta64(8, "m"),
            ]
        )
        lats = np.array([[40.0, 41.0], [41.0, 42.0], [50.0, 51.0], [51.0, 52.0]])
        lons = np.array([[10.0, 11.0], [11.0, 12.0], [20.0, 21.0], [21.0, 22.0]])
        m = self._make_matchups(times_sat1, times_sat2, lats, lons)

        events = m.events
        self.assertEqual(len(events), 2)

        self.assertEqual(events[0]["start_time"], t0)
        self.assertEqual(events[0]["stop_time"], t0 + np.timedelta64(8, "m"))
        self.assertEqual(events[0]["bbox"], (10.0, 40.0, 12.0, 42.0))
        self.assertEqual(events[0]["n_matchups"], 2)
        self.assertFalse(events[0]["crosses_antimeridian"])

        self.assertEqual(events[1]["start_time"], t1)
        self.assertEqual(events[1]["stop_time"], t1 + np.timedelta64(8, "m"))
        self.assertEqual(events[1]["bbox"], (20.0, 50.0, 22.0, 52.0))
        self.assertEqual(events[1]["n_matchups"], 2)
        self.assertFalse(events[1]["crosses_antimeridian"])

    def test_events_cached(self):
        t0 = np.datetime64("2020-01-01T00:00:00")
        times_sat1 = np.array([t0, t0 + np.timedelta64(2, "m")])
        times_sat2 = np.array([t0 + np.timedelta64(5, "m"), t0 + np.timedelta64(7, "m")])
        lats = np.array([[40.0, 41.0], [41.0, 42.0]])
        lons = np.array([[10.0, 11.0], [11.0, 12.0]])
        m = self._make_matchups(times_sat1, times_sat2, lats, lons)

        self.assertIs(m.events, m.events)


if __name__ == "__main__":
    unittest.main()
