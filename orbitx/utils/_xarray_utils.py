import numpy as np
import xarray as xr


def ds_approx_equal(a: xr.Dataset, b: xr.Dataset) -> bool:
    """Compare two Datasets, using np.allclose for float variables and exact equality for all others."""
    if set(a.data_vars) != set(b.data_vars):
        return False
    for var in a.data_vars:
        av, bv = a[var].values, b[var].values
        if np.issubdtype(av.dtype, np.floating):
            if not np.allclose(av, bv, equal_nan=True):
                return False
        else:
            if not np.array_equal(av, bv):
                return False
    return True