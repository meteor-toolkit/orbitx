"""orbitx.utils._tle.get_tle_date - """

"""___Third-Party Modules___"""
import numpy as np
"""___NPL Modules___"""
"""__Built-In Modules__"""

"""___Authorship___"""
__author__ = __author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>",
]
__created__ = "22/09/2025"
__version__ = 1.0
__maintainer__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>",
]
__status__ = "Development"
__all__ = ["get_tle_date"]

def get_tle_date(tle_line_1: str) -> np.datetime64:
    r"""
    Date corresponding to this TLE computed from Epoch Date and Julian Date Fraction

    Example of Epoch date and Julian date fraction: 86 50.28438588
    The Julian day fraction is just the number of days passed in the particular year.
    For example, the date above shows "86" as the epoch year (1986) and 50.28438588 as the Julian day fraction meaning a little over 50 days after January 1, 1986.
    This was computed as follows:
    Start with 50.28438588 days (Days = 50)
    50.28438588 days - 50 = 0.28438588 days
    0.28438588 days x 24 hours/day = 6.8253 hours (Hours = 6)
    6.8253 hours - 6 = 0.8253 hours
    0.8253 hours x 60 minutes/hour = 49.5157 minutes (Minutes = 49)
    49.5157 - 49 = 0.5157 minutes
    0.5157 minutes x 60 seconds/minute = 30.94 seconds (Seconds = 30.94)
    
    Description adapted from `spaceflight.nasa`_
    
    .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html

    :param tle_line_1: TLE first line
    :returns: time of TLE
    """

    # Extract date time information from TLE line 1
    year_tens_and_units = int(tle_line_1[18:20])
    day_in_year = np.timedelta64(int(tle_line_1[20:23]), "D") - 1
    microseconds_day = float(tle_line_1[23:32]) * 86400000000
    date_delta = np.timedelta64(int(microseconds_day), "us")

    # TODO: Test the code with any TLE dated before 2000.
    # Create date time object at start of relevant year.
    # Notice that the reference year here has to do with the TLE conventions as explained in
    # 'celestrak.org/NORAD/documentation/tle-fmt.php' and not the reference year for OrbitX which is 1970.
    if year_tens_and_units > 70:
        date = np.datetime64(f"19{year_tens_and_units}-01-01T00:00:00")
    else:
        date = np.datetime64(f"20{year_tens_and_units}-01-01T00:00:00")

    # Add the necessary number of days to get TLE
    date += day_in_year + date_delta
    return date
