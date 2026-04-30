# orbitx

Propagate satellite orbits to identify matchups.

## For users
### Installation

To install `orbitx`, one needs to install `orekit` and `Cartopy` which are available on `conda-forge` and not on `PyPI`.
As a consequence, the easiest way to do this is using `miniforge`.

First, install `miniforge` as detailed [here](https://gist.github.com/AdrianBenson/f4d7419982e2ab483dc2b7a32f11534c).

Next, after having created and activated an environment for OrbitX, install the version of Cartopy specified in the `setup.py` file of this project, for example:
```bash
conda install Cartopy=0.22.0
```
and install `orekit`:

```bash
conda install orekit
```

You may then navigate to the root folder of this project and install `orbitx` with the following command:

```bash
pip install .
```

### Documentation
The documentation is available online at the [GitLab page](https://orbitx-d7410b.gitlab-docs.npl.co.uk/).

You may also visualise the documentation locally by opening `docs/_build/index.html` in your browser.

### Change requests
If you would like additional functionalities to be added or if you spotted a bug, please open an [issue](https://gitlab.npl.co.uk/altimetry/orbitx/-/issues) in the GitLab repository.

For any substantial amount of work you will need to provide a time code as the development of this software is currently unfunded.

## For developers
### Installation
For development it is recommended to install in editable mode with the optional developer dependencies, i.e.:

``
pip install -e ".[dev]"
``

### Quality and coding guidelines

Guilines to follow when developing this software can be found in the quality_documentation folder of this repository.

### Documentation

To compile locally your documentation, use the following command:
```
sphinx-build docs docs/_build -b html
```
To indicate which autodocumentation should be generated, indicate the modules' name in `docs/content/user/api.rst`.

You may visualise your documentation locally by opening `docs/_build/index.html` in your browser.

### Testing

Implement tests as you go in a subfolder `tests` for each module, containing files with names starting with `test_` (as demonstrated).
To run your test, either use VSCode's testing functionality, or run the following command in the terminal:
```bash
python -m unittest
```

## Acknowledgements

`orbitx` has been developed by [Sajedeh Behnia](mailto:sajedeh.behnia@npl.co.uk).

## Project status

`orbitx` is under active development. It is beta software.
