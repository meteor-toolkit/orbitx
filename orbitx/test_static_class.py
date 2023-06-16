"""orbitx.get_2LEs - module for accessing mission two line element data"""

import numpy as np
import os
import datetime
from typing import Tuple, List, Union

from org.orekit.frames import FramesFactory, TopocentricFrame
from org.orekit.bodies import OneAxisEllipsoid, GeodeticPoint, CelestialBodyFactory
from org.orekit.time import TimeScalesFactory, AbsoluteDate
from org.orekit.utils import IERSConventions, Constants, PVCoordinatesProvider
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator
from orekit.pyhelpers import absolutedate_to_datetime
from math import pi
import datetime


__author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
]
__all__ = ["TLE"]


class TLEInfo:
    @staticmethod
    def return_tle_path(satellite_name: str) -> str:
        """
        Returns path for TLE file for defined satellite

        :param satellite_name: satellite short name as included in TLE file name ``TLEset_XXX``,
        where ``XXX`` may be ``S2A`` for the Sentinel-2A mission

        :return: satellite TLE file path
        """
        from orbitx import TLE_PATH

        path = None

        for tle_dir in TLE_PATH:
            path = os.path.abspath(
                os.path.join(tle_dir, "TLEset_" + satellite_name + ".txt")
            )
            if os.path.isfile(path):
                break

        return path

    @staticmethod
    def return_date_from_tle(tle_line_1: str) -> datetime.datetime:
        """
        Returns date time from TLE first line

        :param tle_line_1: TLE first line
        :returns: time of TLE
        """

        # Extract date time information from TLE line 1
        year_tens_and_units = int(tle_line_1[18:20])
        decimal_day = float(tle_line_1[20:32])

        # Create date time object at start of relevant year
        date = datetime.datetime(year=2000 + year_tens_and_units, month=1, day=1)

        # Add the necessary number of days to get TLE
        date += datetime.timedelta(days=decimal_day - 1)

        return date

    @staticmethod
    def return_seconds_since_2000(date_time: datetime) -> float:
        """
        Returns seconds since 2000 to defined date time

        :param data_time: time of interest
        :returns: seconds since 2000
        """

        return (date_time - datetime.datetime(2000, 1, 1, 0, 0, 0)).total_seconds()

    def get_tle(
        self, satellite: str, start_time: datetime.datetime, end_time: datetime.datetime
    ) -> Tuple[List[str], List[str], List[float]]:
        """
        Set two-line elements within defined time window, with seconds since 2000

        :param start_time: start of time window
        :param end_time: end of time window
        :param satellite: satellite short name as included in TLE file name ``TLEset_XXX``,
                where ``XXX`` may be ``S2A`` for the Sentinel-2A mission

        :return: tuple containing elements - first TLE lines, second TLE lines, times of TLEs in seconds since 2000
        """

        # region Read TLE file.
        tle_path = self.return_tle_path(satellite)
        with open(tle_path, "r") as f:
            lines = f.readlines()
        lines = np.array(lines)
        # endregion

        # region Access indexes of line-1 and line-2
        length = len(lines)
        if length % 3 == 0:
            number_of_TLEs = int(length / 3)
            line_1_indexes = 3 * np.linspace(0, number_of_TLEs - 1, number_of_TLEs) + 1
            line_2_indexes = 3 * np.linspace(0, number_of_TLEs - 1, number_of_TLEs) + 2
        elif length % 2 == 0:
            number_of_TLEs = int(length / 2)
            line_1_indexes = 2 * np.linspace(0, number_of_TLEs - 1, number_of_TLEs) + 0
            line_2_indexes = 2 * np.linspace(0, number_of_TLEs - 1, number_of_TLEs) + 1
        else:
            print("Error message")
        f = np.vectorize(int)
        line_1_indexes = f(line_1_indexes)
        line_2_indexes = f(line_2_indexes)
        tle_line_1 = lines[line_1_indexes]
        tle_line_2 = lines[line_2_indexes]
        # endregion

        # Get date times
        tle_time = np.array(
            [self.return_date_from_tle(tle_line_1_i) for tle_line_1_i in tle_line_1]
        )
        tle_time_s2000 = np.array([self.return_seconds_since_2000(d) for d in tle_time])
        start_time_s2000 = self.return_seconds_since_2000(start_time)
        end_time_s2000 = self.return_seconds_since_2000(end_time)

        # Filter time
        idx = [
            i
            for i, t_i in enumerate(tle_time_s2000)
            if (t_i >= start_time_s2000) and (t_i < end_time_s2000)
        ]

        # Filter TLE set
        tle_line_1 = tle_line_1[idx]
        tle_line_2 = tle_line_2[idx]
        tle_time_s2000 = tle_time_s2000[idx]

        return tle_line_1, tle_line_2, tle_time_s2000


class Orbit:
    """

    NB call the TLE class in here

    inputs:
        list of satellite names
        start and end time
        propagation interval

    attributes:


    methods:
        form_smpl_space
        breakup_smpl_space
        propagate_orbit
        sim_orbit
        interpolate_orbit
    """

    def __init__(self):
        pass

    @staticmethod
    def form_sample_space(
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        prop_smpl_interval: Union[float, int],
    ) -> Tuple[list, np.array]:
        """
        Return a time vector containing desired orbit simulation timestamps

        :param start_time:
        :param end_time:
        :param prop_smpl_interval:
        :return:
        """

        time_since = start_time - datetime.datetime(2000, 1, 1, 0, 0, 0)
        start_time_secs_since_2000 = time_since.total_seconds()

        time_since = end_time - datetime.datetime(2000, 1, 1, 0, 0, 0)
        end_time_secs_since_2000 = time_since.total_seconds()

        smpl_space_secs_since_2000 = np.arange(
            start_time_secs_since_2000, end_time_secs_since_2000, prop_smpl_interval
        )

        smpl_space = [
            datetime.timedelta(seconds=i) + datetime.datetime(2000, 1, 1, 0, 0, 0)
            for i in smpl_space_secs_since_2000
        ]

        return smpl_space, smpl_space_secs_since_2000

    @staticmethod
    def breakup_smpl_space(sim_time: np.array, tle_time: np.array) -> Tuple[list, list]:
        """
        Locate the index of the closest two line element (at a time equal to or smaller than the simulation time) and
        return the matching pointers/indices.

        :param sim_time: a vector of time containing all the instances when we want to simulate the orbit
        :param tle_time: a vector of time containing all tle instances
        :return: tuple of lists containing corresponding indices between simulation space and tle references
        """

        idx_tle = []
        idx_sim = []
        idx_redundant = []

        # Find corresponding indices of tle and simulation time vectors
        for i in range(len(tle_time)):
            idx_tle.append(i)
            idx_sim.append(np.argmax(sim_time > tle_time[i]))

        # Find redundant tle time references
        idx_sim_unique = np.unique(idx_sim)
        for j in range(len(idx_sim_unique)):
            idx = idx_sim == idx_sim_unique[j]
            if sum(idx) > 1:
                loc = [i for i, val in enumerate(idx) if val]
                for k in range(len(loc) - 1):
                    idx_redundant.append(loc[k])

        # Delete redundant tle time references
        idx_redundant.reverse()
        for i in idx_redundant:
            del idx_tle[i]
            del idx_sim[i]

        return idx_sim, idx_tle

    @staticmethod
    def propagate_orbit(
        tle_line1: str,
        tle_line2: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        propagation_sampling_interval: Union[float, int],
    ) -> Tuple[List[float], List[float], List[float], List[float], List[float], List[float]]:
        """
        Propagate satellite orbit for given two-line-elements and associated time

        :param tle_line1: first line of the reference two-line-element
        :param tle_line2: first line of the reference two-line-element
        :param start_time: start time of orbit propagation
        :param end_time: end time of orbit propagation
        :param propagation_sampling_interval: sampling interval in seconds
        :return: vector of orbit latitude, longitude, altitude, elevation, and azimuth angles
        *** Modified from Bernardo's code ***
        """

        extrapDate = AbsoluteDate(
            start_time.year,
            start_time.month,
            start_time.day,
            start_time.hour,
            start_time.minute,
            float(start_time.second),
            TimeScalesFactory.getUTC(),
        )  # when you want to strat tracking
        finalDate = AbsoluteDate(
            end_time.year,
            end_time.month,
            end_time.day,
            end_time.hour,
            end_time.minute,
            float(end_time.second),
            TimeScalesFactory.getUTC(),
        )  # when you want to strat tracking
        propagation_sampling_interval = float(propagation_sampling_interval)

        # CELLESTIAL BODIES
        sun = CelestialBodyFactory.getSun()
        sun = PVCoordinatesProvider.cast_(sun)

        # IMPORTANT CONSTANTS
        ae = Constants.WGS84_EARTH_EQUATORIAL_RADIUS
        fl = Constants.WGS84_EARTH_FLATTENING
        mu = Constants.WGS84_EARTH_MU
        utc = TimeScalesFactory.getUTC()

        # Preparing the Coordinate systems
        ITRF = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
        earth = OneAxisEllipsoid(
            Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
            Constants.WGS84_EARTH_FLATTENING,
            ITRF,
        )
        inertialFrame = FramesFactory.getEME2000()

        ### OPERATIONAL SATELLITE ###
        mytle = TLE(tle_line1, tle_line2)
        prop_Optsat = TLEPropagator.selectExtrapolator(mytle)
        propagator0 = prop_Optsat

        sel = []
        saz = []
        sze = []

        pos = []
        pos_lat = []
        pos_lon = []
        pos_alt = []
        pos_s0_lat = []
        pos_s0_lon = []
        pos_s0_alt = []
        date = []
        julian_date = []

        while (
            extrapDate.compareTo(finalDate) <= 0.0
        ):  # propagate orbit until it reaches it reaches the final date
            pv0 = propagator0.getPVCoordinates(extrapDate, inertialFrame)
            psun = sun.getPVCoordinates(extrapDate, inertialFrame)
            pos_tmp0 = pv0.getPosition()
            pos_sun = psun.getPosition()
            pos0 = earth.transform(
                pos_sun, inertialFrame, extrapDate
            )  # position of the sun on the earth surface
            poss0 = earth.transform(
                pos_tmp0, inertialFrame, extrapDate
            )  # position of the satellite on the earth surface

            pos_s0_lat.append((poss0.getLatitude()))  # satellite nadir position
            pos_s0_lon.append((poss0.getLongitude()))  # satellite nadir position
            pos_s0_alt.append((poss0.getAltitude()))  # satellite nadir position
            pos_lat.append((pos0.getLatitude()))  # sun nadir position
            pos_lon.append((pos0.getLongitude()))  # sun nadir position
            pos_alt.append((pos0.getAltitude()))  # sun nadir position
            station = GeodeticPoint(
                poss0.getLatitude(), poss0.getLongitude(), 0.0
            )  # set the satellite Nadir position as the reference from which to obtain the
            # observation and illumination values
            station_frame = TopocentricFrame(earth, station, "Esrange")

            saz_tmp = (
                station_frame.getAzimuth(pos_sun, inertialFrame, extrapDate)
                * 180.0
                / pi
            )
            sel_tmp = (
                station_frame.getElevation(pos_sun, inertialFrame, extrapDate)
                * 180.0
                / pi
            )

            sel.append(sel_tmp)
            saz.append(saz_tmp)

            date.append(absolutedate_to_datetime(extrapDate))
            julian_date.append(
                (
                    absolutedate_to_datetime(extrapDate)
                    - datetime.datetime(2000, 1, 1, 0, 0, 0)
                ).total_seconds()
            )
            extrapDate = extrapDate.shiftedBy(propagation_sampling_interval)

        pos_s0_lat = [i * 180.0 / pi for i in pos_s0_lat]
        pos_s0_lon = [i * 180.0 / pi for i in pos_s0_lon]
        return julian_date, pos_s0_lat, pos_s0_lon, pos_s0_alt, sel, saz

    def sim_orbit(self, line1, line2, seconds_since_2000, propagation_sampling_interval):
        """
        Return latitude, longitude and time arrays for full simulated orbit
        """
        smpl_space, smpl_space_secs_since_2000 = self.form_smpl_space(
            self.start_time, self.end_time, propagation_sampling_interval
        )
        sat_smpl_breakup_idx, tle_ref_lines = self.breakup_smpl_space(
            smpl_space_secs_since_2000, seconds_since_2000
        )
        sat_lat_sim = []
        sat_lon_sim = []
        sat_sec_since = []
        for i in range(len(tle_ref_lines) - 1):
            secsince1, lat1, lon1, alt1, el1, az1 = propagate_orbit(
                line1[tle_ref_lines[i]],
                line2[tle_ref_lines[i]],
                smpl_space[sat_smpl_breakup_idx[i]],
                smpl_space[sat_smpl_breakup_idx[i + 1] - 1],
                propagation_sampling_interval,
            )
            sat_lat_sim.append(lat1)
            sat_lon_sim.append(lon1)
            sat_sec_since.append(secsince1)
        # flatten the inhomogeneous list of lists
        return (
            np.hstack(sat_lat_sim),
            np.hstack(sat_lon_sim),
            np.hstack(sat_sec_since),
        )

    def run(self, satellites: List[str], start_time: datetime.datetime, end_time: datetime.datetime, propagation_sampling_interval: Union[float, int]):
        """

        """
        self.start_time = start_time
        self.end_time = end_time
        tle = TLEInfo()
        for sat in satellites:
            tle_line_1, tle_line_2, tle_time_s2000 = tle.get_tle(sat, start_time, end_time)
            self.sim_orbit(tle_line_1, tle_line_2, tle_time_s2000, propagation_sampling_interval)


if __name__ == "__main__":
    pass
    orbit = Orbit()
    orbit_output = orbit.run(satellites, nvpoiajdrmcpso\ecn idfc)

    find_matchups = Matchups()
    matchup_output = find_matchups.run(orbit_output, jivubosinxpaisdbv)