# orbitx

Propagate satellite orbits to identify matchups.

`orbitx` computes satellite ground-track positions from TLE data and identifies
instances where two satellite swaths overlap in space and time.

> **Warning:** This software is in beta. Results should be used with
> caution. Please share any feedback via the issue tracker.

## Usage

### Virtual environment

It is always recommended to use a virtual environment for each Python project.
Use your preferred environment manager, or create one with:

```bash
python -m venv venv
```

Activate it on Windows with `venv\Scripts\activate`, or on macOS/Linux with
`source venv/bin/activate`.

### Installation

Install the package and its core dependencies:

```bash
pip install orbitx
```

Or in editable mode when working from source:

```bash
pip install -e .
```

Optional extras are available depending on your use case:

```bash
pip install -e ".[dev]"   # Development tools (ruff, mypy, pytest, …)
pip install -e ".[docs]"  # Documentation build (sphinx, …)
```

#### Orekit (optional)

Orbit propagation using the Orekit library requires `orekit`, which is available
on `conda-forge` but not on PyPI. Install it separately if needed:

```bash
conda install -c conda-forge orekit
```

### Development

Install the pre-commit hooks after cloning:

```bash
pre-commit install
```

When you commit, `ruff` will lint and format your code. If it makes
corrections the commit will be aborted so you can review the changes — just
commit again once you are happy.

Run the test suite with:

```bash
pytest
```

### Documentation

Build the docs locally with:

```bash
sphinx-build docs docs/_build -b html
```

The documentation is also available online at the
[GitHub pages site](https://meteor-toolkit.github.io/orbitx/).

### Change requests

If you would like additional functionality or have spotted a bug, please open an
[issue](https://github.com/meteor-toolkit/orbitx/issues) in the GitHub
repository.

## Compatibility

`orbitx` requires Python 3.11 or later and is tested on Python 3.11, 3.12,
and 3.13.

## Licence

`orbitx` is released under the GNU Lesser General Public License v3 (LGPLv3).
See the [LICENSE](https://github.com/meteor-toolkit/orbitx/blob/main/LICENSE) file for the full licence text.

## Authors

`orbitx` is developed and maintained by the
[MetEOR Toolkit Team](mailto:team@comet-toolkit.org).
