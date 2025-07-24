"""orbitx.orbit - class to simulate satellite orbits"""

import datetime
import numpy as np

from math import pi
from typing import Tuple, List, Union, Any

from scipy.interpolate import interp1d
from org.orekit.frames import FramesFactory, TopocentricFrame
from org.orekit.bodies import (
    OneAxisEllipsoid,
    GeodeticPoint,
    CelestialBodyFactory,
    FieldGeodeticPoint,
)
from org.orekit.time import TimeScalesFactory, AbsoluteDate
from org.orekit.utils import (
    IERSConventions,
    Constants,
    PVCoordinatesProvider,
    TimeStampedFieldPVCoordinates,
)
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
    Class to simulate satellite orbits
    """

    def __init__(self):
        self.start_time = None
        self.end_time = None

    @staticmethod
    def form_sample_space(
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        prop_smpl_interval: Union[float, int],
    ) -> Tuple[list, np.ndarray]:
        """
        Return a time vector containing desired orbit simulation timestamps

        :param start_time: start of time window
        :param end_time: end of time window
        :param prop_smpl_interval: propagation sampling interval in seconds
        :return: tuple containing elements - list of temporal sampling space in datetime, and list of temporal sampling
        space in 'seconds since 1970'
        """

        time_since = start_time - datetime.datetime(1970, 1, 1, 0, 0, 0)
        start_time_secs_since_1970 = time_since.total_seconds()

        time_since = end_time - datetime.datetime(1970, 1, 1, 0, 0, 0)
        end_time_secs_since_1970 = time_since.total_seconds()

        smpl_space_secs_since_1970 = np.arange(
            start_time_secs_since_1970,
            end_time_secs_since_1970 + prop_smpl_interval,
            prop_smpl_interval,
        )  # 'prop_smpl_interval' has been added to the second element to make the 'smpl_space_secs_since_1970' vector
        # long enough to contain 'end_time'.

        smpl_space = [
            datetime.datetime(1970, 1, 1, 0, 0, 0) + datetime.timedelta(seconds=i)
            for i in smpl_space_secs_since_1970
        ]

        return smpl_space, smpl_space_secs_since_1970

    @staticmethod
    def get_matching_indices(
        sim_time: np.ndarray, tle_time: np.ndarray
    ) -> Tuple[list, list]:
        """
        Locate the index of the closest two line element (at a time equal to or smaller than the simulation time) and
        return the matching pointers/indices.

        :param sim_time: a vector of time containing all the instances when we want to simulate the orbit
        :param tle_time: a vector of time containing all tle instances
        :return: tuple of lists containing corresponding indices between simulation space and tle references
        """

        idx_tle = np.array(range(len(tle_time)))
        idx_sim = np.empty(idx_tle.shape, int)
        idx_redundant = []

        # Find corresponding indices of tle and simulation time vectors
        for i in idx_tle:
            idx_sim[i] = np.argmax(sim_time >= tle_time[i])

        # Find redundant tle time references
        idx_sim_unique = np.unique(idx_sim)
        for j in range(len(idx_sim_unique)):
            idx = idx_sim == idx_sim_unique[j]
            if sum(idx) > 1:
                loc = [i for i, val in enumerate(idx) if val]
                for k in range(len(loc) - 1):
                    idx_redundant.append(loc[k])

        # Delete redundant tle time references
        idx_tle = np.delete(idx_tle, idx_redundant)
        idx_sim = np.delete(idx_sim, idx_redundant)
            

        # Force the idx_sim to include the start_time and end_time stamps
        idx_sim[0] = 0
        idx_sim[-1] = len(sim_time) - 1
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

        extrap_date = AbsoluteDate(
            start_time.year,
            start_time.month,
            start_time.day,
            start_time.hour,
            start_time.minute,
            float(start_time.second),
            TimeScalesFactory.getUTC(),
        )  # when you want to start tracking
        final_date = AbsoluteDate(
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

        # Preparing the Coordinate systems
        itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
        earth = OneAxisEllipsoid(
            Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
            Constants.WGS84_EARTH_FLATTENING,
            itrf,
        )
        inertial_frame = FramesFactory.getEME2000()

        # OPERATIONAL SATELLITE
        mytle = TLE(tle_line1, tle_line2)
        propagator0 = TLEPropagator.selectExtrapolator(mytle)
        propagator0 = PVCoordinatesProvider.cast_(propagator0)

        extrap_date_list = []
        while extrap_date.compareTo(final_date) <= 0.0:
            extrap_date_list.append(extrap_date)
            extrap_date = extrap_date.shiftedBy(propagation_sampling_interval)
        extrap_date_list = np.array(extrap_date_list)
        sel = np.empty(extrap_date_list.shape, dtype=float)
        saz = np.empty(extrap_date_list.shape, dtype=float)
        pos_lat = np.empty(extrap_date_list.shape, dtype=float)
        pos_lon = np.empty(extrap_date_list.shape, dtype=float)
        pos_alt = np.empty(extrap_date_list.shape, dtype=float)
        pos_s0_lat = np.empty(extrap_date_list.shape, dtype=float)
        pos_s0_lon = np.empty(extrap_date_list.shape, dtype=float)
        pos_s0_alt = np.empty(extrap_date_list.shape, dtype=float)
        date = np.empty(extrap_date_list.shape, dtype=datetime.datetime)
        julian_date = np.empty(extrap_date_list.shape, dtype=float)

        for extrap_date_ind, extrap_date in enumerate(extrap_date_list):
            pv0 = propagator0.getPVCoordinates(extrap_date, inertial_frame)
            psun: TimeStampedFieldPVCoordinates = sun.getPVCoordinates(
                extrap_date, inertial_frame
            )
            pos_tmp0 = pv0.getPosition()
            pos_sun = psun.getPosition()
            pos0 = earth.transform(
                pos_sun, inertial_frame, extrap_date
            )  # position of the sun on the earth surface
            poss0: FieldGeodeticPoint = earth.transform(
                pos_tmp0, inertial_frame, extrap_date
            )  # position of the satellite on the earth surface

            pos_s0_lat[extrap_date_ind] = (
                poss0.getLatitude()
            )  # satellite nadir position
            pos_s0_lon[extrap_date_ind] = (
                poss0.getLongitude()
            )  # satellite nadir position
            pos_s0_alt[extrap_date_ind] = (
                poss0.getAltitude()
            )  # satellite nadir position
            pos_lat[extrap_date_ind] = pos0.getLatitude()  # sun nadir position
            pos_lon[extrap_date_ind] = pos0.getLongitude()  # sun nadir position
            pos_alt[extrap_date_ind] = pos0.getAltitude()  # sun nadir position
            station = GeodeticPoint(
                poss0.getLatitude(), poss0.getLongitude(), 0.0
            )  # set the satellite Nadir position as the reference from which to obtain the
            # observation and illumination values
            station_frame = TopocentricFrame(earth, station, "Esrange")

            saz_tmp = (
                station_frame.getAzimuth(pos_sun, inertial_frame, extrap_date)
                * 180.0
                / pi
            )
            sel_tmp = (
                station_frame.getElevation(pos_sun, inertial_frame, extrap_date)
                * 180.0
                / pi
            )

            sel[extrap_date_ind] = sel_tmp
            saz[extrap_date_ind] = saz_tmp

            date[extrap_date_ind] = absolutedate_to_datetime(extrap_date)
            julian_date[extrap_date_ind] = (
                absolutedate_to_datetime(extrap_date)
                - datetime.datetime(1970, 1, 1, 0, 0, 0)
            ).total_seconds()

        pos_s0_lat = [i * 180.0 / pi for i in pos_s0_lat]
        pos_s0_lon = [i * 180.0 / pi for i in pos_s0_lon]
        return julian_date, pos_s0_lat, pos_s0_lon, pos_s0_alt, sel, saz

    def simulate_orbit(
        self,
        line1: List[str],
        line2: List[str],
        seconds_since_1970: np.ndarray,
        propagation_sampling_interval: Union[float, int],
    ) -> Tuple[List[float], List[float], List[float]]:
        """
        Return latitude, longitude and time arrays for full simulated orbit

        :param line1: first lines of TLE set
        :param line2: second lines of TLE set
        :param seconds_since_1970: timing of TLE set in seconds since 1970
        :param propagation_sampling_interval: propagation sampling interval in seconds
        :return: tuple containing elements - time of simulation, simulated latitude, simulated longitude
        """
        smpl_space, smpl_space_secs_since_1970 = self.form_sample_space(
            self.start_time, self.end_time, propagation_sampling_interval
        )
        sat_smpl_breakup_idx, tle_ref_lines = self.get_matching_indices(
            smpl_space_secs_since_1970, seconds_since_1970
        )
        sat_lat_sim: list = []
        sat_lon_sim: list = []
        sat_sec_since: list = []

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
            # Change the second-to-last timestamp of the sampling step, to the last one (the end_time). This is to
            # simulate orbit for the exact end-time without handling exceptions outside the loop for a single time
            # stamp.
            smpl_space[-2] = smpl_space[-1]
            for i in range(len(tle_ref_lines) - 1):
                secsince1, lat1, lon1, alt1, el1, az1 = self.propagate_orbit(
                    line1[tle_ref_lines[i]],
                    line2[tle_ref_lines[i]],
                    smpl_space[sat_smpl_breakup_idx[i]],
                    smpl_space[sat_smpl_breakup_idx[i + 1] - 1],
                    propagation_sampling_interval,
                )
                sat_lat_sim.extend(lat1)
                sat_lon_sim.extend(lon1)
                sat_sec_since.extend(secsince1)

        return (
            sat_sec_since,
            sat_lat_sim,
            sat_lon_sim,
        )

    def interpolate_orbit(
        self, sat_sec_since, sat_lat_sim, sat_lon_sim, interpolation_sampling_interval
    ) -> Tuple[Any, Any, np.ndarray]:
        """
        Interpolate the propagated orbit for a higher spatiotemporal sampling rate.

        :param sat_sec_since: time of simulated/propagated orbit
        :param sat_lat_sim: latitude of simulated/propagated orbit
        :param sat_lon_sim: longitude of simulated/propagated orbit
        :param interpolation_sampling_interval: interpolation sampling interval
        :return: tuple containing latitude, longitude, and time of the simulated/interpolated orbit
        """
        f1_lat_linear = interp1d(sat_sec_since, sat_lat_sim)
        f1_lon_linear = interp1d(sat_sec_since, sat_lon_sim)

        interp_smpl_space = np.arange(
            (self.start_time - datetime.datetime(1970, 1, 1, 0, 0, 0)).total_seconds(),
            (self.end_time - datetime.datetime(1970, 1, 1, 0, 0, 0)).total_seconds()
            + interpolation_sampling_interval,
            interpolation_sampling_interval,
        )

        return (
            f1_lat_linear(interp_smpl_space),
            f1_lon_linear(interp_smpl_space),
            interp_smpl_space,
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

        :param satellites: short name of satellites, e.g., S3A, LS8, etc.
        :param start_time: start time of simulation
        :param end_time: end time of simulation
        :param propagation_sampling_interval: propagation sampling interval in seconds
        :param interpolation_sampling_interval: interpolation sampling interval in seconds
        :return: dictionary containing lat, lon, and time of simulated orbit for the satellite of interest
        """
        self.start_time = start_time
        self.end_time = end_time
        tle = TLEInfo()
        sat_interp_dict = {}
        for sat in satellites:
            line1, line2, secs_since = tle.get_tle(sat, start_time, end_time)
            sat_secs_since, sat_lat_sim, sat_lon_sim = self.simulate_orbit(
                line1, line2, secs_since, propagation_sampling_interval
            )
            lat, lon, time = self.interpolate_orbit(
                sat_secs_since,
                sat_lat_sim,
                sat_lon_sim,
                interpolation_sampling_interval,
            )
            sat_interp_dict.update({sat: {"lat": lat, "lon": lon, "time": time}})
        return sat_interp_dict
