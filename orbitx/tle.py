"""orbitx.get_2LEs - module for accessing mission two line element data"""

import numpy as np
import os
import datetime
from typing import Tuple, List, Optional

__author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
]

__all__ = ["TLEInfo"]


class TLEInfo:
    """
    Class to retrieve satellite TLEs
    """

    @staticmethod
    def return_tle_path(satellite_name: str) -> Optional[str]:
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

        # TODO: Test the code with any TLE dated before 2000.
        # Create date time object at start of relevant year.
        # Notice that the reference year here has to do with the TLE conventions as explained in
        # 'celestrak.org/NORAD/documentation/tle-fmt.php' and not the reference year for OrbitX which is 1970.
        if tle_line_1[18] == "0" or tle_line_1[18] == "1" or tle_line_1[18] == "2":
            date = datetime.datetime(year=2000 + year_tens_and_units, month=1, day=1)
        else:
            date = datetime.datetime(year=1900 + year_tens_and_units, month=1, day=1)

        # Add the necessary number of days to get TLE
        date += datetime.timedelta(days=decimal_day - 1)

        return date

    @staticmethod
    def return_seconds_since_1970(date_time: datetime.datetime) -> float:
        """
        Returns seconds since 1970 to defined date time

        :param date_time: time of interest
        :returns: seconds since 1970
        """

        return (date_time - datetime.datetime(1970, 1, 1, 0, 0, 0)).total_seconds()

    def get_tle(
        self, satellite: str, start_time: datetime.datetime, end_time: datetime.datetime
    ) -> Tuple[List[str], List[str], np.ndarray]:
        """
        Returns two-line elements within defined time window, with seconds since 1970

        :param start_time: start of time window
        :param end_time: end of time window
        :param satellite: satellite short name as included in TLE file name ``TLEset_XXX``,
                where ``XXX`` may be ``S2A`` for the Sentinel-2A mission

        :return: tuple containing elements - first TLE lines, second TLE lines, times of TLEs in seconds since 1970
        """

        # region Read TLE file.
        tle_path = self.return_tle_path(satellite)
        if tle_path is None:
            raise ValueError(f"No TLE file found for '{satellite}'")
        with open(tle_path, "r") as f:
            lines = np.array(f.read().splitlines())
        # endregion

        # region Access indexes of line-1 and line-2
        length = len(lines)
        if len(lines[0]) < 69:
            line_1_indexes = np.arange(1, length, 3)
            line_2_indexes = np.arange(2, length, 3)
        else:
            line_1_indexes = np.arange(0, length, 2)
            line_2_indexes = np.arange(1, length, 2)

        tle_line_1 = lines[line_1_indexes]
        tle_line_2 = lines[line_2_indexes]
        # endregion

        # Get date times
        tle_time = np.array(
            [self.return_date_from_tle(tle_line_1_i) for tle_line_1_i in tle_line_1]
        )
        tle_time_s1970 = np.array([self.return_seconds_since_1970(d) for d in tle_time])
        start_time_s1970 = self.return_seconds_since_1970(start_time)
        end_time_s1970 = self.return_seconds_since_1970(end_time)

        # Filter time
        idx = [
            i
            for i, t_i in enumerate(tle_time_s1970)
            if (t_i >= start_time_s1970) and (t_i < end_time_s1970)
        ]

        if not idx:
            # If there is no TLE between start- and end-time, just get the one TLE which is closest to start_time
            closest_tle = np.argmin(np.abs(tle_time_s1970 - start_time_s1970))

            tle_line_1 = [tle_line_1[closest_tle]]
            tle_line_2 = [tle_line_2[closest_tle]]
            tle_time_s1970 = np.array([tle_time_s1970[closest_tle]])

        else:
            # Filter TLE set
            tle_line_1 = tle_line_1[idx]
            tle_line_2 = tle_line_2[idx]
            tle_time_s1970 = tle_time_s1970[idx]

        return list(tle_line_1), list(tle_line_2), tle_time_s1970


if __name__ == "__main__":
    pass
