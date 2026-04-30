.. _quickstart:

################
Finding matchups
################

The `Matchups` is used to find the time and location of matchup events (that is two or more satellites passing through the same location window within a short time-frame).
A typical use example is as follows:

.. code-block:: python3

    from orbitx import Matchups
    import numpy as np

    matchups = Matchups.find_matchups(
        satellites=["CS2", "J3"],
        start_date=np.datetime64("2012-01-01T00:00:00"),
        end_date=np.datetime64("2012-01-01T12:00:00"),
        propagation_sampling_interval=np.array(60, dtype="timedelta64[s]"),
        interpolation_sampling_interval=np.array(5, dtype="timedelta64[s]"),
        space_diff_threshold=290,
        time_diff_threshold=np.array(900, dtype="timedelta64[s]"),
        check_before=True,
        check_after=True,
        has_land_ocean_mask=True,
        reference_date=np.datetime64("2000-01-01T00:00:00"),
    )
    print(matchups)

.. code-block:: text

    Matchup object with following attributes:
    Satellites considered: ['CryoSat-2', 'JASON-3']
    Date from which matchups are looked for: 2011-12-31T23:45:00
    Date until which matchups are looked for: 2012-01-01T12:15:00
    Maximum time difference between members of a matchup: 900 seconds (seconds)
    Maximum distance between members of a matchup: 290.0 (km)
    Are matchups in which on of the satellites appears before the start date considered? True
    Are matchups in which on of the satellites appears after the end date considered? True
    Has this matchup a land/ocean mask? True
    Number of matchups found: 53.
    Created on 2026-01-06T13:20:37 using the version 1.0 of orbitx.

The `satellites` attribute is a list of satellite short names of arbitrary length.
The supported short names are currently the following ones:

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
    
The `space_diff_threshold` argument represents the maximum accepted distance (in kilometers, projected on Earth surface from the satellites latitude and longitude) between two satellites for an event to be considered a matchup.
The `time_diff_threshold` argument represents the maximum time between the passing of any two satellites for an event to be called a matchup.
The `check_before` argument specifies whether a matchup where one of the satellites crossed before `start_date` should be considered
The `check_after` argument specifies whether a matchup where one of the satellites crossed after `end_date` should be considered.
`has_land_ocean_mask` specifies whether the result should indicate whether the satellites are above land or ocean or above different masks.

A `Matchups` object can be plotted simply using the `plot` method.

.. code-block:: python3

    matchups.plot()

.. image:: ../../_static/matchup_plot.png

The `matchups` attribute is at the core of the `Matchups` objects.
It contains an `xarray` with a `time` coordinate (`float64` in seconds since reference date) giving the time at which the first satellite in the `satellites` list got in the matchup.
For each satellite in the list the xarray contains the variables `lat<i>` and `lon<i>` which represent the latitude and longitude of the satellite at the time it joined the matchup.


.. code-block:: python3

    print(matchups.matchups)

.. code-block:: text

    <xarray.Dataset> Size: 5kB
    Dimensions:         (matchup_index: 53, satellite: 2, satellite_pair: 1)
    Coordinates:
    * satellite       (satellite) <U3 24B 'CS2' 'J3'
    * satellite_pair  (satellite_pair) <U6 24B 'CS2_J3'
    * matchup_index   (matchup_index) int64 424B 0 1 2 3 4 5 ... 47 48 49 50 51 52
    Data variables:
        reference_date  datetime64[s] 8B 2000-01-01
        time_datetime   (matchup_index, satellite) datetime64[s] 848B 2012-01-01T...
        time            (matchup_index, satellite) float64 848B 3.787e+08 ... 3.7...
        lat             (matchup_index, satellite) float64 848B 63.72 66.12 ... 66.1
        lon             (matchup_index, satellite) float64 848B -173.1 ... 159.0
        distance        (matchup_index, satellite_pair) float64 424B 279.4 ... 287.3
        delay           (matchup_index, satellite_pair) timedelta64[s] 424B 00:09...
        land_mask       (matchup_index, satellite) <U1 424B 'O' 'O' 'O' ... 'O' 'O'
        matchup_type    (matchup_index) <U1 212B 'O' 'O' 'O' 'O' ... 'O' 'O' 'O' 'O'
    Attributes: (12/13)
        satellite_shortname:              ['CS2', 'J3']
        satellite_name:                   ['CryoSat-2', 'JASON-3']
        start_date:                       378690300.0
        end_date:                         378735300.0
        propagation_sampling_interval:    60
        interpolation_sampling_interval:  5
        time_diff_threshold               900.0
        space_diff_threshold:             290.0
        check_before:                     1
        check_after:                      1
        has_land_ocean_mask:              1
        version:                          1.0
        creation_date:                    2026-01-06T13:20:37

Finally, a `Matchups` object can be exported to and loaded from netcdf4 files:

.. code-block:: python3

    matchups.to_netcdf("./test_export/")
    loaded_matchup = Matchups.from_netcdf("./test_export/2012-01-01_2012-01-01_psi60.0_isi5.0_matchups_CS2_J3_c2c290.0_tdt900.0.nc")
    print(matchups == loaded_matchup)

.. code-block:: text

    True

If you are looking for matchups involving satellites not included "natively" in OrbitX, you can use your own TLE file to obtain matchups.
To this effect, use the `custom_satellite` argument as demonstrated below:

.. code-block:: python3

    matchups_custom = Matchups.find_matchups(
        satellites=[],
        start_date=np.datetime64("2012-01-01T00:00:00"),
        end_date=np.datetime64("2012-01-01T12:00:00"),
        propagation_sampling_interval=np.array(60, dtype="timedelta64[s]"),
        interpolation_sampling_interval=np.array(5, dtype="timedelta64[s]"),
        space_diff_threshold=290,
        time_diff_threshold=np.array(900, dtype="timedelta64[s]"),
        check_before=True,
        check_after=True,
        has_land_ocean_mask=True,
        reference_date=np.datetime64("2000-01-01T00:00:00"),
        custom_satellites=[
            {
                "tle_filepath": r"..\orbitx\data\tle\TLEset_CS2.txt",
                "satellite_shortname": "CS2",
                "satellite_name": "CryoSat-2"
            },
            {
                "tle_filepath": r"..\orbitx\data\tle\TLEset_J3.txt",
                "satellite_shortname": "J3",
                "satellite_name": "Jason-3"
            }
        ]
    )
    print(matchups_custom == matchups)

.. code-block:: text

    True

Here we have used satellites included in OrbitX so we can demonstrate that the result is indeed the same.
