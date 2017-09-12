.. Copyright (c) 2015-2016, Exa Analytics Development Team
.. Distributed under the terms of the Apache License 2.0

#####################################
Installation
#####################################
Python's external libraries are maintained as packages in repositories.
There are two main repositories, `pypi`_ and `anaconda`_ and two corresponding
Python applications that interact with them (pip and conda respectively).

This project recommends using conda because it is both a package manager and
a Python virtual environment manager. Anaconda also provides better cross
platform support especially for Python packages that require compiled external
dependences.


Anaconda
#######################
Using anaconda or miniconda::

    conda install -c exaanalytics exa


Pypi
#######################
Using pip::

    sudo pip install exa


Repository
#########################
Manually (or for a development installation)::

    git clone https://github.com/exa-analytics/exa
    cd exa
    pip install .


What's Next?
#####################
- Users should check out the :ref:`started-label`
- Contributors should check out the :ref:`dev-label`
- The :ref:`api-label` contains usage and extension examples, and developer notes


.. _pypi: https://pypi.python.org/pypi
.. _anaconda: https://anaconda.org/anaconda/packages
