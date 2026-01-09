"""orbitx.utils._tle.get_drag_term -"""

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
__all__ = ["get_drag_term"]


def get_drag_term(line1: str) -> float:
    r"""Finds the drag term of the satellite from the first line of the TLE.
    The drag term corresponds to the characters 54 to 61 of the first line.
    The drag term is also known as .. math`B^\star` or radiation pressure coefficient (units of 1/(Earth radii))

    Args:
        line1 (str): The first line of the considered TLE

    Returns:
        float: The drag term

    Example:
        .. code-block:: python3

            line1 = "1 25544U 98067A   08264.51782528 -.00002182  12345-5 -11606-4 0  2927"
            drag_term = get_drag_term(line1)
            print(drag_term)

        .. code-block:: text

            -1.1606e-5
    """
    drag_term_str: str = line1[53:61]
    drag_term_str = re.sub(" ", "", drag_term_str)

    positions_plus: list[int] = [
        i for i, letter in enumerate(drag_term_str) if letter == "+"
    ]
    number_plus: int = len(positions_plus)
    positions_minus: list[int] = [
        i for i, letter in enumerate(drag_term_str) if letter == "-"
    ]
    number_minus: int = len(positions_minus)
    if number_minus + number_plus == 1:
        if number_minus == 1:
            split_string = drag_term_str.split("-")
            decimal_part = float(f"0.{split_string[0]}")
            order_magnitude = -int(split_string[1])
        else:
            split_string = drag_term_str.split("+")
            decimal_part = float(f"0.{split_string[0]}")
            order_magnitude = int(split_string[1])
    elif number_minus + number_plus == 2:
        if number_minus == 2:
            split_string = drag_term_str.split("-")
            decimal_part = float(f"-0.{split_string[1]}")
            order_magnitude = -int(split_string[2])
        elif number_minus == 1:
            if positions_minus[0] == 0:
                split_string = drag_term_str.split("+")
                order_magnitude = int(split_string[1])
                split_string = split_string[0].split("-")
                decimal_part = float(f"-0.{split_string[1]}")
            else:
                split_string = drag_term_str.split("-")
                order_magnitude = -int(split_string[1])
                split_string = split_string[0].split("+")
                decimal_part = float(f"0.{split_string[1]}")
        else:
            split_string = drag_term_str.split("+")
            decimal_part = float(f"0.{split_string[1]}")
            order_magnitude = int(split_string[2])
    else:
        raise ValueError(f"Invalid string for drag term: {drag_term_str}")
    return decimal_part * (10**order_magnitude)
