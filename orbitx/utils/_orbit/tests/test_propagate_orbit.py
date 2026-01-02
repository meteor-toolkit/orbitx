"""Python function to simulate the orbit of a satellite at given dates     *** Modified from Bernardo's code ***"""

"""___Third-Party Modules___"""
import numpy as np

from math import pi
from typing import Tuple, List
import warnings
import numbers

import orekit
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

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._date_utils import (
    datetime64_to_sec_since,
    datetime_to_datetime64,
    datetime64_get_year,
    datetime64_get_month,
    datetime64_get_day,
    datetime64_get_hour,
    datetime64_get_minute,
    datetime64_get_second,
)

"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "26/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"


def propagate_orbit(
    tle_line1: str,
    tle_line2: str,
    start_date: np.datetime64,
    end_date: np.datetime64,
    propagation_sampling_interval: np.timedelta64,
    reference_date: np.datetime64 = np.datetime64("1970-01-01T00:00:00"),
) -> Tuple[
    List[float], List[float], List[float], List[float], List[float], List[float]
]:
    """
    Propagate satellite orbit for given two-line-elements and associated time

    :param tle_line1: first line of the reference two-line-element
    :param tle_line2: first line of the reference two-line-element
    :param start_date: start time of orbit propagation
    :param end_date: end time of orbit propagation
    :param propagation_sampling_interval: sampling interval in seconds
    :return: Tuple containing the date in seconds from 1970, the date in datetime, orbit latitude, longitude, altitude, elevation angle, and azimuth angle
    """
    orekit.getVMEnv().attachCurrentThread()
    extrap_date = AbsoluteDate(
        datetime64_get_year(start_date),
        datetime64_get_month(start_date),
        datetime64_get_day(start_date),
        datetime64_get_hour(start_date),
        datetime64_get_minute(start_date),
        datetime64_get_second(start_date),
        TimeScalesFactory.getUTC(),
    )  # when you want to start tracking
    final_date = AbsoluteDate(
        datetime64_get_year(end_date),
        datetime64_get_month(end_date),
        datetime64_get_day(end_date),
        datetime64_get_hour(end_date),
        datetime64_get_minute(end_date),
        datetime64_get_second(end_date),
        TimeScalesFactory.getUTC(),
    )  # when you want to stop tracking
    propagation_sampling_interval = propagation_sampling_interval.item().total_seconds()

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

    extrap_date_list = np.empty((1,), dtype=AbsoluteDate)
    extrap_date_list[0] = extrap_date
    while extrap_date.compareTo(final_date) < 0.0:
        extrap_date = extrap_date.shiftedBy(propagation_sampling_interval)
        extrap_date_list = np.append(extrap_date_list, extrap_date)

    sel = np.empty(extrap_date_list.shape, dtype=float)
    saz = np.empty(extrap_date_list.shape, dtype=float)
    pos_lat = np.empty(extrap_date_list.shape, dtype=float)
    pos_lon = np.empty(extrap_date_list.shape, dtype=float)
    pos_alt = np.empty(extrap_date_list.shape, dtype=float)
    pos_s0_lat = np.empty(extrap_date_list.shape, dtype=float)
    pos_s0_lon = np.empty(extrap_date_list.shape, dtype=float)
    pos_s0_alt = np.empty(extrap_date_list.shape, dtype=float)
    date = np.empty(extrap_date_list.shape, dtype="datetime64[s]")
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

        pos_s0_lat[extrap_date_ind] = poss0.getLatitude()  # satellite nadir lattitude
        pos_s0_lon[extrap_date_ind] = poss0.getLongitude()  # satellite nadir longitude
        alt_sat = poss0.getAltitude()
        if not isinstance(alt_sat, numbers.Number):
            warnings.warn("Satellite altitude is not a number: {}".format(alt_sat))
            pos_s0_alt[extrap_date_ind] = np.nan
        else:
            pos_s0_alt[extrap_date_ind] = alt_sat  # satellite nadir altitude

        pos_lat[extrap_date_ind] = pos0.getLatitude()  # sun nadir Lattitude
        pos_lon[extrap_date_ind] = pos0.getLongitude()  # sun nadir Longitude
        alt_sun = pos0.getAltitude()
        if not isinstance(alt_sun, numbers.Number):
            warnings.warn("Satellite altitude is not a number: {}".format(alt_sun))
            pos_alt[extrap_date_ind] = np.nan
        else:
            pos_alt[extrap_date_ind] = alt_sun  # Sun Nadir altitude

        station = GeodeticPoint(
            poss0.getLatitude(), poss0.getLongitude(), 0.0
        )  # set the satellite Nadir position as the reference from which to obtain the
        # observation and illumination values
        station_frame = TopocentricFrame(earth, station, "Esrange")

        saz_tmp = (
            station_frame.getAzimuth(pos_sun, inertial_frame, extrap_date) * 180.0 / pi
        )
        sel_tmp = (
            station_frame.getElevation(pos_sun, inertial_frame, extrap_date)
            * 180.0
            / pi
        )

        sel[extrap_date_ind] = sel_tmp
        saz[extrap_date_ind] = saz_tmp

        date[extrap_date_ind] = datetime_to_datetime64(
            absolutedate_to_datetime(extrap_date)
        )
        julian_date[extrap_date_ind] = datetime64_to_sec_since(
            date[extrap_date_ind], reference_date
        )

    pos_s0_lat = np.array([i * 180.0 / pi for i in pos_s0_lat])
    pos_s0_lon = np.array([i * 180.0 / pi for i in pos_s0_lon])
    return julian_date, date, pos_s0_lat, pos_s0_lon, pos_s0_alt, sel, saz
