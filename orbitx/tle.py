"""orbitx.get_2LEs - module for accessing mission two line element data"""

import numpy as np
import os
import datetime
from typing import Tuple, List


__author__ = ["Sajedeh Behnia <sajedeh.behnia@npl.co.uk>", "Sam Hunt <sam.hunt@npl.co.uk>"]
__all__ = ["TLE"]


class TLE:

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
            path = os.path.abspath(os.path.join(tle_dir, 'TLEset_' + satellite_name + '.txt'))
            if os.path.isfile(path):
                break

        return path

    @staticmethod
    def return_date_from_tle(
            tle_line_1: str
    ) -> datetime.datetime:
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
        date += datetime.timedelta(days=decimal_day-1)

        return date

    @staticmethod
    def return_seconds_since_2000(
            date_time: datetime
    ) -> float:
        """
        Returns seconds since 2000 to defined date time

        :param data_time: time of interest
        :returns: seconds since 2000
        """

        return (date_time - datetime.datetime(2000, 1, 1, 0, 0, 0)).total_seconds()


    def get_tle(
            self,
            start_time: datetime.datetime,
            end_time: datetime.datetime,
            satellite_name: str
    ) -> Tuple[List[str], List[str], List[float]]:
        """
        Returns two-line elements within defined time window, with seconds since 2000

        :param start_time: start of time window
        :param end_time: end of time window
        :param satellite_name: satellite short name as included in TLE file name ``TLEset_XXX``,
        where ``XXX`` may be ``S2A`` for the Sentinel-2A mission

        :return: tuple containing elements - first TLE lines, second TLE lines, times of TLEs in seconds since 2000
        """

        # region Read TLE file.
        tle_path = TLE.return_tle_path(satellite_name)
        with open(tle_path, 'r') as f:
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
            print('Error message')
        f = np.vectorize(int)
        line_1_indexes = f(line_1_indexes)
        line_2_indexes = f(line_2_indexes)
        tle_line_1 = lines[line_1_indexes]
        tle_line_2 = lines[line_2_indexes]
        # endregion

        # Get date times
        tle_time = np.array([TLE.return_date_from_tle(tle_line_1_i) for tle_line_1_i in tle_line_1])
        tle_time_s2000 = np.array([TLE.return_seconds_since_2000(d) for d in tle_time])
        start_time_s2000 = TLE.return_seconds_since_2000(start_time)
        end_time_s2000 = TLE.return_seconds_since_2000(end_time)

        # Filter time
        idx = [i for i, t_i in enumerate(tle_time_s2000) if (t_i >= start_time_s2000) and (t_i < end_time_s2000)]

        # Filter TLE set
        tle_line_1 = tle_line_1[idx]
        tle_line_2 = tle_line_2[idx]
        tle_time_s2000 = tle_time_s2000[idx]

        return (tle_line_1, tle_line_2, tle_time_s2000)


if __name__ == "__main__":
    pass
