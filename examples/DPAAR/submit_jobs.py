"""A File to submit all the slurm jobs for this project"""

"""___Third-Party Modules___"""
import os

"""___NPL Modules___"""

"""__Built-In Modules__"""


"""___Authorship___"""
__author__ = "Zhav Loizeau"
__created__ = "10/08/2025"
__version__ = 1.0
__maintainer__ = "Zhav Loizeau"
__email__ = "xavier.loizeau@npl.co.uk"
__status__ = "Development"

sats_list = [
    ["CS2", "J2"],
    ["CS2", "S3A"],
    ["CS2", "S3B"],
    ["CS2", "S6"],
    ["CS2", "SA"],
    ["J2", "S3A"],
    ["J2", "SA"],
    ["J3", "CS2"],
    ["J3", "J2"],
    ["J3", "S3A"],
    ["J3", "S3B"],
    ["J3", "S6"],
    ["J3", "SA"],
    ["N20", "S6"],
    ["S3A", "SA"],
    ["S3B", "J2"],
    ["S3B", "S3A"],
    ["S3B", "SA"],
    ["S6", "S3A"],
    ["S6", "S3B"],
    ["S6", "SA"],
]

for sats in sats_list:
    os.system(
        "sbatch /home/xl3/projects/orbitx/examples/DPAAR/SLURM/slurm_submit.icelake.{}_{}.venv".format(
            sats[0], sats[1]
        )
    )
