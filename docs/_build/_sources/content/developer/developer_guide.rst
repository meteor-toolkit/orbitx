###############
Developer Guide
###############

Setting-up the development environment
######################################

To contribute to this project, start by cloning it and navigate with your terminal to the location where you cloned this package

.. code-block:: bash

   git clone git@gitlab.npl.co.uk:eco/tools/orbitx.git
   cd ./orbitx

create a new branch to make your contributions and switch to it:

.. code-block:: bash

   git branch new-branch-name
   git checkout -b new-branch-name
   git push --set-upstream origin new-branch-name

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
To use the software development tools necessary to contribute to `orbitx`, install it with the developer optional requirements:

.. code-block:: bash
    
   pip install -e .[dev]

Before you push
###############

`orbitx` uses GitLab Continuous Integration - Continuous Deployment (CI-CD) functionalities to ensure it is bug-free (as much as possible), and developed to a good quality standard.
This means that when you push, some automatic processes will be activated, checking your code base.
When you open a merge request to the main branch, more through checks are done.

So, to avoid the bad surprise of receiving fail messages, we encourage you to check your code locally before pushing.
If you have installed `orbitx` with the developer optional dependences, you already have all the necessary tools to test it.

Compiling documentation
-----------------------

`orbitx` uses `sphinx`_ to build its documentation (that you are reading right now!).
Its source code is in the `docs` folder of the package (at the exception of the `api` which is, indeed in the docs folder but automatically pulls the docstring of the specified classes and functions to build its documentation).

Hence, you might want to make sure that:
    - your contributions are documented in the `user_guide` file,
    - your classes and functions are listed in the API (just follow the example), 
    - you update as necessary the different flow charts and class diagrams, 
    - you update Algorith Theoretical Basis Document (ATBD).

Once you have done all this, check that the documentation compiles properly, and looks as you intended it to.
To do that, just run the following command in your terminal:

.. code-block:: bash

    sphinx-build docs docs/_build -b html

and check the documentation by opening `docs/_build/index.html`.

Code formatting
---------------

`orbitx` uses black for code formatting.
To format your code, just run

.. code-block:: bash

    black .

Syntax checking
---------------

`orbitx` uses `mypy` for syntax static analysis checking.
Just run the following command in your terminal:

.. code-block:: bash
    
    mypy ./orbitx

`orbitx` will not accept merge requests into main if this does not pass.

Running unit-test
-----------------

`orbitx` uses unit testing for validation and verification.
Tests are stored in the `orbitx/tests` folder and use the `unittest` package.

Once you have implemented tests for your functions, just run them locally by running the following command in your terminal:

.. code-block:: bash

    tox

This will create a `test_report` folder with an `html` file detailing the tests restults.
No merge request containing a failing test will be accepted.

This folder also contains a `cov_report` sub-folder. If contains an `index.html` file, if you open it, it will tell you which fraction of the code has been run during testing.
To be merged into `main` a branch should have a minimum of 85 % coverage for all modules.

.. _sphinx: https://www.sphinx-doc.org/en/master/index.html
.. _miniforge: https://conda-forge.org/miniforge/
.. _pixi: https://prefix.dev/blog/uv_in_pixi
.. _anaconda: https://www.anaconda.com/download