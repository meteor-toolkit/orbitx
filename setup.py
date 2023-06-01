import io
import os
import re
import logging
import platform
import shlex
import subprocess as sp
import sys
from setuptools import find_packages
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
import versioneer


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type("")
    with io.open(filename, mode="r", encoding="utf-8") as fd:
        return re.sub(text_type(r":[a-z]+:`~?(.*?)`"), text_type(r"``\1``"), fd.read())

# installs orekit via conda
def post_install_commands():
    on_windows = platform.system() == "Windows"

    commands = [
        "conda install -c conda-forge orekit",
    ]
    commands = [shlex.split(c, posix=(not on_windows)) for c in commands]

    logging.debug(platform.system())
    logging.debug(commands)

    for cmd in commands:
        logging.debug(cmd)
        process = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT)

        for c in iter(lambda: process.stdout.read(1), b""):
            c_decoded = c.decode()
            sys.stdout.write(c_decoded)
            sys.stdout.flush()

        process.wait()
        if process.returncode != 0:
            err = "Command '{}' failed: aborting install".format(cmd)
            logging.error(err)
            raise RuntimeError(err)


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        post_install_commands()


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        post_install_commands()

cmdclass={
    "develop": PostDevelopCommand,
    "install": PostInstallCommand
}

cmdclass = versioneer.get_cmdclass(cmdclass=cmdclass)

setup(
    version=versioneer.get_version(),
    cmdclass=cmdclass,
    name="orbitx",
    url="https://gitlab.npl.co.uk/eco/tools/orbitx",
    license="None",
    author="Sajedeh Behnia",
    author_email="sajedeh.behnia@npl.co.uk",
    description="Propagate satellite orbits to identify matchups.",
    long_description=read("README.md"),
    packages=find_packages(exclude=("tests",)),
    package_data={
        "orbitx": [
            os.path.join("data", "orekit-data.zip"),
            os.path.join("data", "tle", "*")
        ]
    },
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
    ],
    extras_require={
        "dev": [
            "pre-commit",
            "sphinx",
            "sphinx_book_theme",
            "sphinx_design",
            "ipython",
            "pytest",
            "pytest-html",
            "pytest-cov"
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
