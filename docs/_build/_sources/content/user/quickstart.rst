.. _quickstart:

################
Quickstart Guide
################

Installing orbitx
#################

The Orbit class
###############

The `Orbit` class is used to simulate the orbits of satellites.
It relies on `orekit` to simulate the position of satellites based on Two Line Elements (TLE) and on a linear interpolation to obtain a sufficiently fine time resolution while keeping compute time low enough.

A basic use of this class is as follows:

.. code-block:: python3

    from orbitx import Orbit, Matchups
    import datetime

    orbit = Orbit.simulate(
        satellites=["S6", "SA"],
        start_time=datetime.datetime(2020, 2, 1, 0, 0, 0),
        end_time=datetime.datetime(2020, 2, 1, 12, 0, 0),
        propagation_sampling_interval=20,
        interpolation_sampling_interval=5
    )

    print(orbit)

.. code-block:: text

    Orbit object for satellites ['CS2', 'J2'].
    Start date: 2012-01-01 00:00:00
    End date: 2012-01-01 12:00:00
    Propagation sampling interval: 60
    Interpolation sampling interval: 5
    Number of simulated times: 8641

The `satellites` attribute is a list of satellite short names of arbitrary length.
The supported short names are currently the following ones:

.. code-block:: text

    "LS8": "Landsat-8",
    "LS9": "Landsat-9",
    "S2A": "Sentinel-2A",
    "S2B": "Sentinel-2B",
    "S3A": "Sentinel-3A",
    "S3B": "Sentinel-3B",
    "S6": "Sentinel-6",
    "J2": "JASON-2",
    "J3": "JASON-3",
    "SA": "Saral-AltiKa",
    "CS2": "CryoSat-2",
    "LINCS2": "Lin-CryoSat-2",
    "N20": "NOAA-20" 

An orbit object can simply be plotted with a call to the `plot` method of the class:

.. code-block:: python3

    orbit.plot()

.. image:: ../../_static/orbit_plot.png

The core of an `Orbit` class object is its `orbits` attribute.
It contains a nested dictionnary, with one entry per requested satellite.
Each satellite entry contains the `lat` (lattitude), `lon` (longitude), `time` (time of the simulated position in seconds since 1970), `time_datetime` (time of the simulated position in a `datetime` format).

.. code-block:: python3

    print(orbit.orbits)

.. code-block:: text
    
    {
        'CS2': {
            'lat': array([-74.15645752, -74.36682531, -74.5771931 , ..., -56.29122754, -58.33525305, -60.37927857], shape=(8641,)),
            'lon': array([  71.45679019,   81.22522576,   90.99366134, ..., -124.07410594, -123.42313735, -122.77216877], shape=(8641,)),
            'time': array([1.32537600e+09, 1.32537600e+09, 1.32537601e+09, ..., 1.32541919e+09, 1.32541920e+09, 1.32541920e+09], shape=(8641,)),
            'time_datetime': array([datetime.datetime(2012, 1, 1, 0, 0), datetime.datetime(2012, 1, 1, 0, 0, 5), datetime.datetime(2012, 1, 1, 0, 0, 10), ..., datetime.datetime(2012, 1, 1, 11, 59, 50), datetime.datetime(2012, 1, 1, 11, 59, 55), datetime.datetime(2012, 1, 1, 12, 0)], shape=(8641,), dtype=object)
        },
        'J2': {
            'lat': array([-44.56685663, -44.78376038, -45.00066412, ...,  13.63047882, 13.87435618,  14.11823355], shape=(8641,)),
            'lon': array([49.52344903, 49.72488617, 49.92632331, ..., 28.37651745, 28.46935208, 28.56218672], shape=(8641,)),
            'time': array([1.32537600e+09, 1.32537600e+09, 1.32537601e+09, ..., 1.32541919e+09, 1.32541920e+09, 1.32541920e+09], shape=(8641,)),
            'time_datetime': array([datetime.datetime(2012, 1, 1, 0, 0), datetime.datetime(2012, 1, 1, 0, 0, 5), datetime.datetime(2012, 1, 1, 0, 0, 10), ..., datetime.datetime(2012, 1, 1, 11, 59, 50), datetime.datetime(2012, 1, 1, 11, 59, 55), datetime.datetime(2012, 1, 1, 12, 0)], shape=(8641,), dtype=object)
        }
    }

.. code-block:: python3

    orbit.to_netcdf("./test_export/")

.. code-block:: python3

    new_orbit = Orbit.from_netcdf("./test_export/")


The Matchup class
#################

Running in parallel
###################