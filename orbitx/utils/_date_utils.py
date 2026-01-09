"""Global Constants for orbits"""

"""___Third-Party Modules___"""
import datetime
import numpy as np
import numpy.typing as npt
import pandas as pd
from typing import List

"""___NPL Modules___"""

"""__Built-In Modules__"""

"""___Authorship___"""
__author__ = __author__ = ["Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>"]
__created__ = "05/09/2025"
__version__ = 1.0
__maintainer__ = ["Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>"]
__status__ = "Development"


def datetime_to_sec_since(
    date: datetime.datetime,
    ref_date: datetime.datetime = datetime.datetime(1970, 1, 1, 0, 0, 0),
) -> float:
    """datetime_to_sec_since Converts a datetime to number of seconds since reference date

    :param date: The datetime object to convert
    :type date: datetime.datetime
    :param ref_date: The reference date since which number of seconds is to be calculated, defaults to datetime.datetime(1970, 1, 1, 0, 0, 0)
    :type ref_date: datetime.datetime, optional
    :return: The number of seconds since the reference date
    :rtype: float
    """
    return (date - ref_date).total_seconds()


def sec_since_change_ref(
    date: float, ref_date_old: datetime.datetime, ref_date_new: datetime.datetime
) -> float:
    """sec_since_change_ref Converts a date in seconds since reference date format to a seconds since a different date

    :param date: The date to be converted, as a float representing the number of seconds since the former reference date
    :type date: float
    :param ref_date_old: The old reference date to be converted from
    :type ref_date_old: datetime.datetime
    :param ref_date_new: The new reference date to be converted to
    :type ref_date_new: datetime.datetime
    :return: The date converted, as a float representing the number of seconds since the new reference date
    :rtype: float
    """
    return date - (ref_date_new - ref_date_old).total_seconds()


def sec_since_to_datetime(
    date: float, ref_date: datetime.datetime = datetime.datetime(1970, 1, 1, 0, 0, 0)
) -> datetime.datetime:
    """sec_since_to_datetime Converts a date from seconds since reference date to datetime

    :param date: The date to be convertes, as a float representing the number of seconds since a reference date
    :type date: float
    :param ref_date: The reference date from which the input date counts seconds
    :type ref_date: datetime.datetime
    :return: The date converted to a datetime format
    :rtype: datetime.datetime
    """
    return ref_date + datetime.timedelta(seconds=date)


def datetime64_to_datetime(date64: np.datetime64 | npt.NDArray[np.datetime64]) -> datetime.datetime:
    timestamp = pd.Timestamp(date64)
    return pd.to_datetime(timestamp)


def datetime_to_datetime64(date: datetime.datetime) -> np.datetime64 | npt.NDArray[np.datetime64]:
    sec_since = datetime_to_sec_since(date, datetime.datetime(1970, 1, 1, 0, 0, 0))
    return sec_since_to_datetime64(
        sec_since=sec_since, reference_date=np.datetime64("1970-01-01T00:00:00")
    )


def datetime64_to_sec_since(
    date64: np.datetime64 | npt.NDArray[np.datetime64], reference_date: np.datetime64
) -> float | npt.NDArray[np.float64]:
    timedelta_value: np.timedelta64 | npt.NDArray[np.timedelta64] = date64 - reference_date
    return timedelta_value / np.timedelta64(1, "s")


def sec_since_to_datetime64(
    sec_since: float | npt.NDArray[np.float64], reference_date: np.datetime64
) -> np.datetime64 | npt.NDArray[np.datetime64]:
    return reference_date + np.array([int(sec_since)], dtype="timedelta64[s]")[0]


def datetime64_get_year(date: np.datetime64) -> int:
    return int(date.astype("datetime64[Y]").astype(int) + 1970)


def datetime64_get_month(date: np.datetime64) -> int:
    return int(date.astype("datetime64[M]").astype(int) % 12 + 1)


def datetime64_get_day(date: np.datetime64) -> int:
    return int(
        (date.astype("datetime64[D]") - date.astype("datetime64[M]")).astype(int) + 1
    )


def datetime64_get_hour(date: np.datetime64) -> int:
    return int(
        (date.astype("datetime64[h]") - date.astype("datetime64[D]")).astype(int)
    )


def datetime64_get_minute(date: np.datetime64) -> int:
    return int(
        (date.astype("datetime64[m]") - date.astype("datetime64[h]")).astype(int)
    )


def datetime64_get_second(date: np.datetime64) -> float:
    return float(
        (date.astype("datetime64[s]") - date.astype("datetime64[m]")).astype(float)
    )
