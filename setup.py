import io
import os
import re

from setuptools import find_packages
from setuptools import setup
import versioneer


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type("")
    with io.open(filename, mode="r", encoding="utf-8") as fd:
        return re.sub(text_type(r":[a-z]+:`~?(.*?)`"), text_type(r"``\1``"), fd.read())


setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    name="orbitx",
    url="https://gitlab.npl.co.uk/altimetry/orbitx",
    license="None",
    author="Sajedeh Behnia",
    author_email="sajedeh.behnia@npl.co.uk",
    description="Propagate satellite orbits to identify matchups.",
    long_description=read("README.md"),
    packages=find_packages(exclude=("tests",)),
    package_data={
        "orbitx": [
            os.path.join("data", "orekit-data.zip"),
            os.path.join("data", "tle", "*"),
        ]
    },
    install_requires=[
        "numpy==2.3.1",
        "scipy==1.16.0",
        "Cartopy==0.24.1",
        "matplotlib==3.10.3",
        "netCDF4==1.7.2",
        "xarray==2025.7.1",
    ],
    extras_require={
        "dev": [
            "mypy",
            "black",
            "pre-commit",
            "sphinx",
            "sphinx_book_theme",
            "sphinx_design",
            "ipython",
            "pytest",
            "pytest-html",
            "pytest-cov",
        ]
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
