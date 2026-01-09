"""orbitx.get_2LEs - module for accessing mission two line element data"""

"""___Third-Party Modules___"""
import numpy as np
import numpy.typing as npt
from typing import List
import xarray as xr

"""___NPL Modules___"""

"""__Built-In Modules__"""
from orbitx.utils._tle.get_tle_path import get_tle_path
from orbitx.utils._tle.load_file import load_file
from orbitx.utils._tle.create_xarray import create_xarray
from orbitx.utils._tle.filter_xarray import filter_xarray
from orbitx.utils._constants import SATELLITE_DICT


__author__ = [
    "Sajedeh Behnia <sajedeh.behnia@npl.co.uk>",
    "Sam Hunt <sam.hunt@npl.co.uk>",
]

__all__ = ["TLE"]


class TLE:
    r"""
    Class to retrieve satellite TLEs.
    For more information on Two line elements, see the [Wikipedia page](https://en.wikipedia.org/wiki/Two-line_element_set)
    """

    def __init__(
        self,
        tle_xarray: xr.Dataset,
    ):
        self._tle_xarray = tle_xarray

    @classmethod
    def from_sat_shortname(
        cls,
        satellite_shortname: str,
        start_date: np.datetime64,
        end_date: np.datetime64,
        reference_date: np.datetime64 = np.datetime64("1970-01-01T00:00:00"),
    ):
        """Generates a TLE object from the satellite shortname

        If the shortname provided is not supported by OrbitX a ValueError is raised and the used is invited to use a TLE file of their own.

        Args:
            satellite_shortname (str): The shortname of the satellite. Supported shortnames are the following:
            .. code-block:: text

                "CS2": "CryoSat-2",
                "J2": "JASON-2",
                "J3": "JASON-3",
                "LS8": "Landsat-8",
                "LS9": "Landsat-9",
                "N20": "NOAA-20",
                "S2A": "Sentinel-2A",
                "S2B": "Sentinel-2B",
                "S3A": "Sentinel-3A",
                "S3B": "Sentinel-3B",
                "S6": "Sentinel-6",
                "SA": "Saral-AltiKa"
            
            start_date (np.datetime64): The date from which the orbit needs to be simulated
            end_date (np.datetime64): The date until which the orbit needs to be simulated
            reference_date (np.datetime64, optional): The reference date used to represent dates as "seconds since". Defaults to np.datetime64("1970-01-01T00:00:00").

        Raises:
            ValueError: When the shortname provided is not supported by OrbitX

        Returns:
            TLE: A TLE Object
        """
        if not satellite_shortname in SATELLITE_DICT.keys():
            raise ValueError(
                f"No TLE file found for '{satellite_shortname}'. Consider using the `from_filepath` method with your own TLE file."
            )
        satellite_name = SATELLITE_DICT[satellite_shortname]
        # Read TLE file.
        tle_filepath: str = get_tle_path(satellite_shortname)

        return cls.from_filepath(
            tle_filepath,
            satellite_shortname,
            satellite_name,
            start_date,
            end_date,
            reference_date,
        )

    @classmethod
    def from_filepath(
        cls,
        tle_filepath: str,
        satellite_shortname: str,
        satellite_name: str,
        start_date: np.datetime64,
        end_date: np.datetime64,
        reference_date: np.datetime64 = np.datetime64("1970-01-01T00:00:00"),
    ):
        """Generates a TLE object from a TLE file.

        Args:
            tle_filepath (str): The file containing the TLE
            satellite_shortname (str): The shortname of the satellite (e.g., S3A).
            satellite_name (str): The name of the satellite (e.g., Sentinel-3A).
            start_date (np.datetime64): The date from which the orbit needs to be simulated
            end_date (np.datetime64): The date until which the orbit needs to be simulated
            reference_date (np.datetime64, optional): The reference date used to represent dates as "seconds since". Defaults to np.datetime64("1970-01-01T00:00:00").
        """
        tle_line_1, tle_line_2 = load_file(tle_filepath)

        # endregion
        tle_xarray = create_xarray(
            tle_line_1,
            tle_line_2,
            reference_date,
            start_date,
            end_date,
            satellite_shortname,
            satellite_name,
        )

        tle_xarray = filter_xarray(tle_xarray)

        return cls(tle_xarray)

    def __str__(self):
        res = f"""TLE object for the satellite {self.satellite_name} with short name {self.satellite_shortname}.
Satellite catalog number: {self.satellite_catalog_number}.
Satellite classification: {self.classification}.
Launch year: {self.launch_year}.
Launch number: {self.launch_number}.
Launch piece: {self.launch_piece}.
Number of TLEs included: {len(self)}.
Reference date for dates in 'senconds since reference date': {self.reference_date}.
Start date for the orbit to simulate: {self.start_date}.
End date for the orbit to simulate: {self.end_date}.
Created on {self.creation_date} using the version {self.version} of orbitx.
"""
        return res

    def __len__(self):
        """The number of TLEs included in this object"""
        return len(self.tle_xarray.coords["tle_index"])

    @property
    def satellite_shortname(self) -> str:
        r"""The short name associated with the satellite (e.g., CS2)."""
        return self._tle_xarray.attrs["satellite_shortname"]

    @property
    def satellite_name(self) -> str:
        r"""The name associated with the satellite (e.g., Cryosat-2)."""
        return self._tle_xarray.attrs["satellite_name"]

    @property
    def satellite_catalog_number(self) -> str:
        r"""This is the catalog number USSPACECOM has designated for this object."""
        return self._tle_xarray.attrs["catalog_number"]

    @property
    def classification(self) -> str:
        r"""Classification (U: unclassified, C: classified, S: secret)"""
        return self._tle_xarray.attrs["classification"]

    @property
    def launch_year(self) -> int:
        r"""Year in which the satellite was launched"""
        return self._tle_xarray.attrs["launch_year"]

    @property
    def launch_number(self) -> int:
        r"""Number of this launch in the year (how many launches happened this year before this one, plus one)"""
        return self._tle_xarray.attrs["launch_number"]

    @property
    def launch_piece(self) -> str:
        r"""Index of this object in the launch (in a launch that results in three objects orbiting, the second one is indexed B)"""
        return self._tle_xarray.attrs["launch_piece"]

    @property
    def tle_date(self) -> npt.NDArray[np.datetime64]:
        r"""Date corresponding to this TLE"""
        return self._tle_xarray["tle_date"].values

    @property
    def ballistic_coefficient(self) -> npt.NDArray[np.float64]:
        r"""Also called the first derivative of mean motion, the ballistic coefficient is the daily rate of change in the number of revs the object completes each day, divided by 2.
        Units are :math:`revs \cdot day^{-1}`.
        This is "catch all" drag term used in the Simplified General Perturbations (SGP4) USSPACECOM predictor.

        Description adapted from `spaceflight.nasa`_

        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
        """
        return self._tle_xarray["ballistic_coefficient"].values

    @property
    def second_derivative(self) -> npt.NDArray[np.float64]:
        r"""The second derivative of mean motion is a second order drag term in the Simplified General Perturbations (SGP4) predictor used to model terminal orbit decay.
        It measures the second time derivative in daily mean motion, divided by 6.
        Units are :math:`revs\cdot day^{-3}`.

        Description adapted from `spaceflight.nasa`_

        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
        """
        return self._tle_xarray["second_derivative"].values

    @property
    def drag_term(self) -> npt.NDArray[np.float64]:
        r"""
        Also called the radiation pressure coefficient (or BSTAR), the parameter is another drag term in the SGP4 predictor.
        Units are earth radii^-1.
        The last two characters define an applicable power of 10.
        Do not confuse this parameter with "B-Term", the USSPACECOM special perturbations factor of drag coefficient, multiplied by reference area, divided by weight.
        Description adapted from `spaceflight.nasa`_

        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
        """
        return self._tle_xarray["drag_term"].values

    @property
    def element_set_number(self) -> npt.NDArray[np.uint8]:
        r"""
        The element set number is a running count of all 2 line element sets generated by USSPACECOM for this object (in this example, 529).
        Since multiple agencies perform this function, numbers are skipped on occasion to avoid ambiguities.
        The counter should always increase with time until it exceeds 999, when it reverts to 1.
        Description adapted from `spaceflight.nasa`_

        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
        """
        return self._tle_xarray["element_set_number"].values

    @property
    def inclination(self) -> npt.NDArray[np.float64]:
        r"""
        The angle between the equator and the orbit plane. The value provided is the TEME mean inclination.

        Description adapted from `spaceflight.nasa`_

        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
        """
        return self._tle_xarray["inclination"].values

    @property
    def right_ascension(self) -> npt.NDArray[np.float64]:
        r"""
        The angle between vernal equinox and the point where the orbit crosses the equatorial plane (going north).
        The value provided is the TEME mean right ascension of the ascending node.

        Description adapted from `spaceflight.nasa`_

        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
        """
        return self._tle_xarray["right_ascension"].values

    @property
    def eccentricity(self) -> npt.NDArray[np.float64]:
        r"""
        A constant defining the shape of the orbit (0=circular, Less than 1=elliptical).
        The value provided is the mean eccentricity.

        Description adapted from `spaceflight.nasa`_

        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
        """
        return self._tle_xarray["eccentricity"].values

    @property
    def argument_perigee(self) -> npt.NDArray[np.float64]:
        r"""
        The angle between the ascending node and the orbit's point of closest approach to the earth (perigee).
        The value provided is the TEME mean argument of perigee.

        Description adapted from `spaceflight.nasa`_

        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
        """
        return self._tle_xarray["argument_perigee"].values

    @property
    def mean_anomaly(self) -> npt.NDArray[np.float64]:
        r"""The angle, measured from perigee, of the satellite location in the orbit referenced to a circular orbit with radius equal to the semi-major axis.

        Description adapted from `spaceflight.nasa`_

        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
        """
        return self._tle_xarray["mean_anomaly"].values

    @property
    def mean_motion(self) -> npt.NDArray[np.float64]:
        r"""The value is the mean number of orbits per day the object completes.
        There are 8 digits after the decimal, leaving no trailing space(s) when the following element exceeds 9999.

        Description adapted from `spaceflight.nasa`_

        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
        """
        return self._tle_xarray["mean_motion"].values

    @property
    def revolution_number(self) -> npt.NDArray[np.uint16]:
        r"""The orbit number at Epoch Time.
        This time is chosen very near the time of true ascending node passage as a matter of routine.

        Description adapted from `spaceflight.nasa`_

        .. _spaceflight.nasa: https://web.archive.org/web/20000301052035/http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/SSOP_Help/tle_def.html
        """
        return self._tle_xarray["revolution_number"].values

    @property
    def reference_date(self) -> npt.NDArray[np.datetime64]:
        r"""The reference date used to compute the 'seconds since' representation of the TLE dates, represented as a numpy datetime64"""
        return self._tle_xarray["reference_date"].values

    @property
    def start_date(self) -> npt.NDArray[np.datetime64]:
        r"""The end date for this object, used to filter the TLEs when is was created, represented in numpy datetime64[s]"""
        return self._tle_xarray["start_date"].values

    @property
    def end_date(self) -> npt.NDArray[np.datetime64]:
        r"""The end date for this object, used to filter the TLEs when is was created, represented in numpy datetime64[s]"""
        return self._tle_xarray["end_date"].values

    @property
    def reference_date_seconds_since1970(self) -> npt.NDArray[np.float64]:
        r"""The reference date used to compute the 'seconds since' representation of the TLE dates, represented in seconds since 1970-01-01T00:00:00."""
        return self._tle_xarray["reference_date_seconds_since1970"].values

    @property
    def start_date_seconds_since(self) -> npt.NDArray[np.float64]:
        r"""The start date for this object, used to filter the TLEs when it was created, represented in seconds since the chosen reference date for this object."""
        return self._tle_xarray["start_date_seconds_since"].values

    @property
    def end_date_seconds_since(self) -> npt.NDArray[np.float64]:
        r"""The end date for this object, used to filter the TLEs when is was created, represented in seconds since the chosen reference date for this object."""
        return self._tle_xarray["end_date_seconds_since"].values

    @property
    def tle_date_seconds_since(self) -> npt.NDArray[np.float64]:
        r"""The list of the dates corresponding to each TLE in this object, in seconds since the chosen reference date of this object."""
        return self._tle_xarray["tle_date_seconds_since"].values

    @property
    def tle_xarray(self) -> xr.Dataset:
        r"""The xarray containing the information about all TLE's for this satellite"""
        return self._tle_xarray

    @property
    def tle_line_1(self) -> npt.NDArray[np.str_]:
        r"""The list of all first TLE lines"""
        return self._tle_xarray["line_1"].values

    @property
    def tle_line_2(self) -> npt.NDArray[np.str_]:
        r"""The list of all second TLE lines"""
        return self._tle_xarray["line_2"].values

    @property
    def version(self) -> str:
        r"""The orbitx version used to create this object"""
        return self._tle_xarray.attrs["version"]

    @property
    def creation_date(self) -> str:
        r"""The date when this object was created"""
        return self._tle_xarray.attrs["creation_date"]


if __name__ == "__main__":
    pass
