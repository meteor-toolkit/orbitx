import numpy as np
from math import pi


def cal_dist_d2m(lat1, lon1, lat2, lon2):
    """
    Get lat and lon pairs in degree and return distance in meter
    :param lat1:
    :param lon1:
    :param lat2:
    :param lon2:
    :return:
    """
    lon1 = lon1 * pi / 180.0
    lat1 = lat1 * pi / 180.0
    lon2 = lon2 * pi / 180.0
    lat2 = lat2 * pi / 180.0

    R = 6373.0  # radius of the Earth [kms] meaning that the result will also be in kms
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c  # Haversine formula
    return distance
