"""orbitx.utils._tle.get_second_derivative -"""

"""___Third-Party Modules___"""
import re

"""___NPL Modules___"""
"""__Built-In Modules__"""

"""___Authorship___"""
__author__ = __author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>",
]
__created__ = "29/09/2025"
__version__ = 1.0
__maintainer__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
    "Mattea Goalen <mattea.goalen@npl.co.uk>",
    "Zhav (Xavier) Loizeau <xavier.loizeau@npl.co.uk>",
]
__status__ = "Development"
__all__ = ["get_second_derivative"]


def get_second_derivative(line1: str) -> float:
    r"""Finds the second derivative of the satellite mean motion from the first line of the TLE.
    The second derivative corresponds to the characters 45 to 52 of the first line.

    Args:
        line1 (str): The first line of the considered TLE

    Returns:
        float: The second derivative of the satellite mean motion

    Example:
        .. code-block:: python3

            line1 = "1 25544U 98067A   08264.51782528 -.00002182  12345-5 -11606-4 0  2927"
            ballistic_coefficient = get_ballistic_coefficient(line1)
            print(ballistic_coefficient)

        .. code-block:: text

            1.2345e-06
    """
    second_derivative_str = line1[44:52]

    second_derivative_str = re.sub(" ", "", second_derivative_str)

    positions_plus = [
        i for i, letter in enumerate(second_derivative_str) if letter == "+"
    ]
    number_plus = len(positions_plus)
    positions_minus = [
        i for i, letter in enumerate(second_derivative_str) if letter == "-"
    ]
    number_minus = len(positions_minus)
    if number_minus + number_plus == 1:
        if number_minus == 1:
            split_string = second_derivative_str.split("-")
            decimal_part = float(f"0.{split_string[0]}")
            order_magnitude = -int(split_string[1])
        else:
            split_string = second_derivative_str.split("+")
            decimal_part = float(f"0.{split_string[0]}")
            order_magnitude = int(split_string[1])
    elif number_minus + number_plus == 2:
        if number_minus == 2:
            split_string = second_derivative_str.split("-")
            decimal_part = float(f"-0.{split_string[1]}")
            order_magnitude = -int(split_string[2])
        elif number_minus == 1:
            if positions_minus[0] == 0:
                split_string = second_derivative_str.split("+")
                order_magnitude = int(split_string[1])
                split_string = split_string[0].split("-")
                decimal_part = float(f"-0.{split_string[1]}")
            else:
                split_string = second_derivative_str.split("-")
                order_magnitude = -int(split_string[1])
                split_string = split_string[0].split("+")
                decimal_part = float(f"0.{split_string[1]}")
        else:
            split_string = second_derivative_str.split("+")
            decimal_part = float(f"0.{split_string[1]}")
            order_magnitude = int(split_string[2])
    else:
        raise ValueError(
            f"Invalid string for second derivative: {second_derivative_str}"
        )
    return decimal_part * (10**order_magnitude)
