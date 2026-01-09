###########
User Guide
###########

Installing OrbitX
##########################################

`orbitx` depends on Cartopy and Orekit, two packages that are more easily installed with a package manager that has access to conda forge (`miniforge`_, `pixi`_, `anaconda`_...) 

Once you have installed one of these package managers, create a virtual environment:

.. code-block:: bash

    conda create -p /path/to/venv python=3.12
    conda activate /path/to/venv

and install the Cartopy and Orekit packages:

.. code-block:: bash

    conda install Cartopy=0.24.1
    conda install orekit=13.0.1

you can now move on with the install of `orbitx` itself.

**Local installation**:

Clone this package

.. code-block:: bash

   git clone git@gitlab.npl.co.uk:eco/tools/orbitx.git

navigate with your terminal to the location where you cloned this package, and install it:

.. code-block:: bash

   cd ./orbitx
   pip install -e .

**Remote install**

First, you will need to create a GitLab personal access token.

Then, run the following command in your terminal

.. code-block:: bash

   pip install orbitx --index-url https://__token__:<your_personal_token>@gitlab.npl.co.uk/api/v4/projects/3075/packages/pypi/simple

.. add your user guide pages to this toctree

.. toctree::
   :hidden:
   
   Finding matchups <matchup>
   Generating orbits <orbit>
   Reading TLEs <tle>
   Parallel programming <parallel>



.. _miniforge: https://conda-forge.org/miniforge/
.. _pixi: https://prefix.dev/blog/uv_in_pixi
.. _anaconda: https://www.anaconda.com/download
