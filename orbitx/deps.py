"""orbitx.deps - Lazy imports for optional dependencies."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import orekit  # noqa: F401

_DEFAULT_OREKIT_DATA = os.path.join(os.path.dirname(__file__), "data", "orekit-data.zip")
_initialised = False


def lazy_orekit():
    try:
        import orekit  # type: ignore
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "Dependency 'orekit' is required for this operation. "
            "Please see the 'orekit' instructions at: https://gitlab.orekit.org/orekit-labs/python-wrapper"
        )
    return orekit


def init_orekit(data_path: str | None = None) -> None:
    global _initialised
    if _initialised:
        return
    orekit = lazy_orekit()
    orekit.initVM()
    from orekit.pyhelpers import setup_orekit_curdir
    setup_orekit_curdir(filename=data_path or _DEFAULT_OREKIT_DATA)
    _initialised = True