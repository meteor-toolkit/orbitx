.. currentmodule:: orbitx.utils

.. _backend:

#####################
Backend documentation
#####################

This page provides an auto-generated summary of **orbitx**'s Backend functionalities.
Those functionalities are stored in the `utils` sub-module.


.. autosummary::
   :toctree: generated/

   _date_utils.datetime_to_sec_since
   _date_utils.sec_since_change_ref
   _date_utils.sec_since_to_datetime
   _date_utils.datetime64_to_datetime
   _date_utils.datetime_to_datetime64
   _date_utils.datetime64_to_sec_since
   _date_utils.sec_since_to_datetime64

   _tle.create_xarray
   _tle.filter_xarray
   _tle.get_argument_perigee
   _tle.get_ballistic_coefficient
   _tle.get_catalog_number
   _tle.get_classification
   _tle.get_drag_term
   _tle.get_eccentricity
   _tle.get_element_set_number
   _tle.get_inclination
   _tle.get_launch_number
   _tle.get_launch_piece
   _tle.get_launch_year
   _tle.get_mean_anomaly
   _tle.get_mean_motion
   _tle.get_revolution_number
   _tle.get_right_ascension
   _tle.get_second_derivative
   _tle.get_tle_date
   _tle.get_tle_path
   _tle.load_file

   _orbit.form_sample_space.form_sample_space
   _orbit.get_matching_indices.get_matching_indices
   _orbit.interp_circ.interp_circ
   _orbit.interpolate_orbit.interpolate_orbit
   _orbit.orbit_dict_to_xarray.orbit_dict_to_xarray
   _orbit.propagate_orbit.propagate_orbit
   _orbit.simulate_orbit.simulate_orbit

   _matchups.find_matches.find_matches
   _matchups.get_delay.get_delay
   _matchups.get_dist.get_dist
   _matchups.get_land_ocean_mask.get_land_ocean_mask
   _matchups.is_land.is_land
   _matchups.land_mask.land_mask

.. autodata::
   orbitx.utils._constants.SATELLITE_DICT
   :annotation:

.. autodata::
   orbitx.utils._constants.EARTH_RADIUS
   :annotation:

.. autodata::
   orbitx.utils._constants.CM
   :annotation:
   