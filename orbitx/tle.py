"""orbitx.get_2LEs - module for accessing mission two line element data"""

"""___Third-Party Modules___"""
import numpy as np
import os
from typing import Tuple, List, Optional
import warnings

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._date_utils import datetime64_to_sec_since



__author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
]

__all__ = ["TLEInfo"]


class TLEInfo:
    r"""
    Class to retrieve satellite TLEs.
    For more information on Two line elements, see the [Wikipedia page](https://en.wikipedia.org/wiki/Two-line_element_set)
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
    def return_date_from_tle(tle_line_1: str) -> np.datetime64:
        """
        Returns date time from TLE first line

        :param tle_line_1: TLE first line
        :returns: time of TLE
        """

        # Extract date time information from TLE line 1
        year_tens_and_units = int(tle_line_1[18:20])
        day_in_year = np.timedelta64(int(tle_line_1[20:23]), 'D') - 1
        microseconds_day = float(tle_line_1[23:32]) * 86400000000
        date_delta = np.timedelta64(int(microseconds_day), 'us')

        # TODO: Test the code with any TLE dated before 2000.
        # Create date time object at start of relevant year.
        # Notice that the reference year here has to do with the TLE conventions as explained in
        # 'celestrak.org/NORAD/documentation/tle-fmt.php' and not the reference year for OrbitX which is 1970.
        if tle_line_1[18] == "0" or tle_line_1[18] == "1" or tle_line_1[18] == "2":
            date = np.datetime64(f'20{year_tens_and_units}-01-01T00:00:00')
        else:
            date = np.datetime64(f'19{year_tens_and_units}-01-01T00:00:00')

        # Add the necessary number of days to get TLE
        date += day_in_year + np.array(date_delta, dtype='timedelta64[us]')
        return date

    def get_tle(
        self,
        satellite: str,
        start_date: np.datetime64,
        end_date: np.datetime64,
        reference_date: np.datetime64 = np.datetime64("1970-01-01T00:00:00")
    ) -> Tuple[List[str], List[str], np.ndarray]:
        """
        Returns two-line elements within defined time window, with seconds since reference date

        :param satellite: satellite short name as included in TLE file name ``TLEset_XXX``,
                where ``XXX`` may be ``S2A`` for the Sentinel-2A mission
        :param start_date: start of time window
        :param end_date: end of time window

        :return: tuple containing elements - first TLE lines, second TLE lines, times of TLEs in seconds since reference date
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
        if (
            len(lines[0]) < 69
        ):  # If the file includes the name of the mission at the beginning of each TLE, the name is at position 0, 3, ... (and we do not care about it)
            line_1_indexes = np.arange(
                1, length, 3
            )  # Line 1's are at position 1, 4, ...
            line_2_indexes = np.arange(
                2, length, 3
            )  # Line 2's are at position 2, 5, ...
        else:  # If the name is not included
            line_1_indexes = np.arange(
                0, length, 2
            )  # Line 1's are at position 0, 2, ...
            line_2_indexes = np.arange(
                1, length, 2
            )  # Line 2's are at position 1, 3, ...

        tle_line_1 = lines[line_1_indexes]  # list of all line 1s
        tle_line_2 = lines[line_2_indexes]  # list of all line 2s
        # endregion

        # Get date times
        tle_date = np.array(
            [self.return_date_from_tle(tle_line_1_i) for tle_line_1_i in tle_line_1]
        )
        tle_time_since = np.array([datetime64_to_sec_since(d, reference_date) for d in tle_date])
        start_time_since = datetime64_to_sec_since(start_date, reference_date)
        end_time_since = datetime64_to_sec_since(end_date, reference_date)

        # Filter time
        lower_bound_tle_time = [t for t in tle_time_since if t <= start_time_since]
        if len(lower_bound_tle_time) == 0:
            warnings.warn(
                "The oldest TLE file is more recent than the start time requested.\n Oldest TLE file: {}\n Start time requested: {}".format(
                    np.min(tle_date), start_date
                )
            )
        lower_bound_tle_time = (
            start_time_since
            if len(lower_bound_tle_time) == 0
            else np.max(lower_bound_tle_time)
        )
        upper_bound_tle_time = [t for t in tle_time_since if t >= end_time_since]
        if len(upper_bound_tle_time) == 0:
            warnings.warn(
                "The most recent TLE file is older than the end time requested.\n Oldest TLE file: {}\n Start time requested: {}".format(
                    np.max(tle_date), end_date
                )
            )
        upper_bound_tle_time = (
            end_time_since
            if len(upper_bound_tle_time) == 0
            else np.min(upper_bound_tle_time)
        )
        idx = [
            i
            for i, t_i in enumerate(tle_time_since)
            if (t_i >= lower_bound_tle_time) and (t_i < upper_bound_tle_time)
        ]

        if not idx:
            # If there is no TLE between start- and end-time, just get the one TLE which is closest to start_time
            closest_tle = np.argmin(np.abs(tle_time_since - start_time_since))

            tle_line_1 = [tle_line_1[closest_tle]]
            tle_line_2 = [tle_line_2[closest_tle]]
            tle_time_since = np.array([tle_time_since[closest_tle]])

        else:
            # Filter TLE set
            tle_line_1 = tle_line_1[idx]
            tle_line_2 = tle_line_2[idx]
            tle_time_since = tle_time_since[idx]
        return tle_line_1, tle_line_2, tle_time_since


if __name__ == "__main__":
    pass
