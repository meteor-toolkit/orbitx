"""A File to generate SLURM scripts that execute python scripts"""

"""___Third-Party Modules___"""
from typing import List

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


def generate_slurm_content(sats: List[str]) -> str:
    res = """#!/bin/bash -l

#!#############################################################
#!#### Modify the options in this section as appropriate ######
#!#############################################################

#! This is an example sbatch script to run a Python program in a virtual environment as a job on minerva.

#! sbatch directives begin here ###############################
#! Name of the job:
#SBATCH -J orbitxs3aAltika
#SBATCH -p icelake
#! Which project should be charged:
#SBATCH -A NPL-GENERAL-CPU
#! How many whole nodes should be allocated?
#SBATCH --nodes=1
#! How many tasks will there be in total? (<=nodes*32)
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#! How much wallclock time will be required?
#SBATCH --time=36:00:00

#! What types of email messages do you wish to receive?
#SBATCH --mail-type=FAIL
#! Uncomment this to prevent the job from being requeued (e.g. if
#! interrupted by node failure or system downtime):
#SBATCH --no-requeue

#! sbatch directives end here (put any additional directives above this line)

#! Number of nodes and tasks per node allocated by SLURM (do not change):
numnodes=$SLURM_JOB_NUM_NODES
numtasks=$SLURM_NTASKS
mpi_tasks_per_node=$(echo "$SLURM_TASKS_PER_NODE" | sed -e  's/^\\([0-9][0-9]*\\).*$/\\1/')

#! ############################################################
#! PREPROCESSING PART
#! This section prepares the input files, output files, working directory
#! and working environment

#! Working environment: dependencies
#! Modify the settings below to specify the application's environment, location
#! and launch method:

#! Optionally modify the environment seen by the application
#! (note that SLURM reproduces the environment at submission
#! irrespective of ~/.bashrc):
. /etc/profile.d/modules.sh           # Leave this line (enables the module command)
module purge                          # Removes all modules still loaded
module load centos7/default-basic       # REQUIRED - loads the basic environment
#! Insert additional module load commands after this line if needed.
#! (FMB) Since we are using python, either choose between the python3 module or the anaconda one.
#! (FMB) Uncomment any of the two following lines:
# module load python-3.6.5-gcc-4.8.5-rgom2oq

RUNPATH=$HOME/projects/orbitx/examples/
cd $RUNPATH
echo -e "Changed directory to `pwd`.\\n"
ulimit -c unlimited
conda init
conda activate base
conda activate $HOME/environments/orbitx
python3 $HOME/projects/orbitx/examples/DPAAR/python/{}_{}.py
""".format(
        sats[0], sats[1]
    )
    return res


def generate_slurm_title(sats: List[str]) -> str:
    return "/home/xl3/projects/orbitx/examples/DPAAR/SLURM/slurm_submit.icelake.{}_{}.venv".format(
        sats[0], sats[1]
    )


for sats in sats_list:
    file_path = generate_slurm_title(sats)
    with open(file_path, "w") as file:
        file.write(generate_slurm_content(sats))
