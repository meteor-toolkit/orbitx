import orekit
vm = orekit.initVM()
from orekit.pyhelpers import setup_orekit_curdir
setup_orekit_curdir()
from org.orekit.frames import FramesFactory, TopocentricFrame
from org.orekit.bodies import OneAxisEllipsoid, GeodeticPoint, CelestialBodyFactory
from org.orekit.time import TimeScalesFactory, AbsoluteDate
from org.orekit.utils import IERSConventions, Constants, PVCoordinatesProvider
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator
from orekit.pyhelpers import absolutedate_to_datetime
from math import pi
import datetime

def propagate_orbit(tle_line1, tle_line2, start_time, end_time, propagation_sampling_interval):
    '''
    This function propagates satellite orbit given
    :param tle1_line1: first line of the reference two-line-element
    :param tle1_line2: first line of the reference two-line-element
    :param start_time: start time of orbit propagation
    :param end_time: end time of orbit propagation
    :param propagation_sampling_interval: sampling interval in seconds
    :return: vectore of orbit latitude, longitude, altitude, elevation, and azimuth angles
    *** Modified from Bernardo's code ***
    '''

    extrapDate = AbsoluteDate(start_time.year, start_time.month, start_time.day, start_time.hour, start_time.minute, float(start_time.second), TimeScalesFactory.getUTC())  # when you want to strat tracking
    finalDate = AbsoluteDate(end_time.year, end_time.month, end_time.day, end_time.hour, end_time.minute, float(end_time.second), TimeScalesFactory.getUTC())  # when you want to strat tracking
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
    earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS, Constants.WGS84_EARTH_FLATTENING, ITRF)
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

    while (extrapDate.compareTo(finalDate) <= 0.0):  # propagate orbit until it reaches it reaches the final date
        pv0 = propagator0.getPVCoordinates(extrapDate, inertialFrame)
        psun = sun.getPVCoordinates(extrapDate, inertialFrame)
        pos_tmp0 = pv0.getPosition()
        pos_sun = psun.getPosition()
        pos0 = earth.transform(pos_sun, inertialFrame, extrapDate)  # position of the sun on the earth surface
        poss0 = earth.transform(pos_tmp0, inertialFrame, extrapDate)  # position of the satellite on the earth surface

        pos_s0_lat.append((poss0.getLatitude()))  # satellite nadir position
        pos_s0_lon.append((poss0.getLongitude()))  # satellite nadir position
        pos_s0_alt.append((poss0.getAltitude()))  # satellite nadir position
        pos_lat.append((pos0.getLatitude()))  # sun nadir position
        pos_lon.append((pos0.getLongitude()))  # sun nadir position
        pos_alt.append((pos0.getAltitude()))  # sun nadir position
        station = GeodeticPoint(poss0.getLatitude(), poss0.getLongitude(), 0.0)  # set the satellite Nadir position as the reference from which to obtain the
        # observation and illumination values
        station_frame = TopocentricFrame(earth, station, "Esrange")

        saz_tmp = station_frame.getAzimuth(pos_sun, inertialFrame, extrapDate) * 180.0 / pi
        sel_tmp = station_frame.getElevation(pos_sun, inertialFrame, extrapDate) * 180.0 / pi

        sel.append(sel_tmp)
        saz.append(saz_tmp)

        date.append(absolutedate_to_datetime(extrapDate))
        julian_date.append((absolutedate_to_datetime(extrapDate) - datetime.datetime(2000, 1, 1, 0, 0, 0)).total_seconds())
        extrapDate = extrapDate.shiftedBy(propagation_sampling_interval)

    pos_s0_lat = [i * 180.0 / pi for i in pos_s0_lat]
    pos_s0_lon = [i * 180.0 / pi for i in pos_s0_lon]
    return(julian_date, pos_s0_lat, pos_s0_lon, pos_s0_alt, sel, saz)
