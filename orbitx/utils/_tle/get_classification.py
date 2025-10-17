"""orbitx.utils._tle.get_classification - """

"""___Third-Party Modules___"""
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
__all__ = ["get_classification"]

def get_classification(line1: str) -> str:
    r"""Finds the classification of the satellite in the first line of the TLE.
    The classification corresponds to character eight in the first line of the TLE.
    The possible values are
        - U: unclassified,
        - C: classified,
        - S: secret.

    Args:
        line1 (str): The first line of the considered TLE

    Returns:
        str: The classification of the satellite

    Example:
        .. code-block:: python3

            line1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
            classification = get_classification(line1)
            print(classification)
        
        .. code-block:: bash

            >>> Unclassified
    """
    short_classification = line1[7]
    if short_classification == 'U':
        return 'Unclassified'
    if short_classification == 'C':
        return 'Classified'
    if short_classification == 'S':
        return 'Secret'
    raise ValueError(f"""The classification character in the TLE was neither U, C, or S.
Character found: {short_classification}""")
