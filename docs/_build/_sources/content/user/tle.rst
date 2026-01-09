#############
Reading TLE's
#############

The `Orbit` class is used to simulate the orbits of satellites.
It relies on `orekit` to simulate the position of satellites based on Two Line Elements (TLE) and on a linear interpolation to obtain a sufficiently fine time resolution while keeping compute time low enough.

A basic use of this class is as follows:

.. code-block:: python3

    from orbitx import TLE
    import numpy as np

    tle = TLE.from_sat_shortname(
        "S6", np.datetime64("2020-02-01T00:00:00"), np.datetime64("2020-02-01T12:00:00")
    )
    print(tle)

.. code-block:: text

    TLE object for the satellite Sentinel-6 with short name S6.
    Satellite catalog number: 46984.
    Satellite classification: Unclassified.
    Launch year: 2020.
    Launch number: 87.
    Launch piece: A.
    Number of TLEs included: 1.
    Reference date for dates in 'senconds since reference date': 1970-01-01T00:00:00.
    Start date for the orbit to simulate: 2020-02-01T00:00:00.
    End date for the orbit to simulate: 2020-02-01T12:00:00.
    Created on 2026-01-06T13:20:26 using the version 1.0 of orbitx.
