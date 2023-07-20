"""orbitx.orbit - class to simulate satellite orbits"""

import datetime
import numpy as np

from math import pi
from typing import Tuple, List, Union

from scipy.interpolate import interp1d
from org.orekit.frames import FramesFactory, TopocentricFrame
from org.orekit.bodies import OneAxisEllipsoid, GeodeticPoint, CelestialBodyFactory
from org.orekit.time import TimeScalesFactory, AbsoluteDate
from org.orekit.utils import IERSConventions, Constants, PVCoordinatesProvider
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator
from orekit.pyhelpers import absolutedate_to_datetime

from orbitx.tle import TLEInfo

__author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
]

__all__ = ["Orbit"]


class Orbit:
    """

    NB call the TLE class in here

    inputs:
        list of satellite names
        start and end time
        propagation interval

    attributes:


    methods:
        form_sample_space
        get_matching_indices # previously breakup_smpl_space
        propagate_orbit
        sim_orbit
        interpolate_orbit
        run
        save_orbits
    """

    def __init__(self):
        self.start_time = None
        self.end_time = None
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
            datetime.datetime(2000, 1, 1, 0, 0, 0) + datetime.timedelta(seconds=i)
            for i in smpl_space_secs_since_2000
        ]

        return smpl_space, smpl_space_secs_since_2000

    @staticmethod
    def get_matching_indices(
        sim_time: np.array, tle_time: np.array
    ) -> Tuple[list, list]:
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
            idx_sim.append(np.argmax(sim_time >= tle_time[i]))

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
    ) -> Tuple[
        List[float], List[float], List[float], List[float], List[float], List[float]
    ]:
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

    def simulate_orbit(
        self,
        line1: list[str],
        line2: list[str],
        seconds_since_2000: List[float],
        propagation_sampling_interval: Union[float, int],
    ):
        """
        Return latitude, longitude and time arrays for full simulated orbit
        """
        smpl_space, smpl_space_secs_since_2000 = self.form_sample_space(
            self.start_time, self.end_time, propagation_sampling_interval
        )
        sat_smpl_breakup_idx, tle_ref_lines = self.get_matching_indices(
            smpl_space_secs_since_2000, seconds_since_2000
        )
        sat_lat_sim = []
        sat_lon_sim = []
        sat_sec_since = []

        if len(tle_ref_lines) == 1:
            secsince1, lat1, lon1, alt1, el1, az1 = self.propagate_orbit(
                line1[tle_ref_lines[0]],
                line2[tle_ref_lines[0]],
                self.start_time,
                self.end_time,
                propagation_sampling_interval,
            )
            sat_lat_sim = lat1
            sat_lon_sim = lon1
            sat_sec_since = secsince1

        else:
            for i in range(len(tle_ref_lines) - 1):
                secsince1, lat1, lon1, alt1, el1, az1 = self.propagate_orbit(
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
            sat_sec_since = np.hstack(sat_sec_since)
            sat_lat_sim = np.hstack(sat_lat_sim)
            sat_lon_sim = np.hstack(sat_lon_sim)

        return (
            sat_sec_since,
            sat_lat_sim,
            sat_lon_sim,
        )

    def interpolate_orbit(
        self, sat_sec_since, sat_lat_sim, sat_lon_sim, interpolation_sampling_interval
    ):
        """ """
        f1_lat_linear = interp1d(sat_sec_since, sat_lat_sim, fill_value="extrapolate")
        f1_lon_linear = interp1d(sat_sec_since, sat_lon_sim, fill_value="extrapolate")

        prop_smpl_space = np.arange(
            (self.start_time - datetime.datetime(2000, 1, 1, 0, 0, 0)).total_seconds(),
            (self.end_time - datetime.datetime(2000, 1, 1, 0, 0, 0)).total_seconds(),
            interpolation_sampling_interval,
        )

        return (
            f1_lat_linear(prop_smpl_space),
            f1_lon_linear(prop_smpl_space),
            prop_smpl_space,
        )

    def run(
        self,
        satellites: List[str],
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        propagation_sampling_interval: Union[float, int],
        interpolation_sampling_interval: Union[float, int],
    ) -> dict:
        """
        Calculate the interpolated satellite orbits

        :param satellites:
        :param start_time:
        :param end_time:
        :param propagation_sampling_interval:
        :param interpolation_sampling_interval:
        :return:
        """
        self.start_time = start_time
        self.end_time = end_time
        tle = TLEInfo()
        sat_interp_dict = {}
        for sat in satellites:
            tle_info = tle.get_tle(sat, start_time, end_time)
            orbit = self.simulate_orbit(*tle_info, propagation_sampling_interval)
            lat, lon, time = self.interpolate_orbit(
                *orbit, interpolation_sampling_interval
            )
            sat_interp_dict.update({sat: {"lat": lat, "lon": lon, "time": time}})
        return sat_interp_dict
