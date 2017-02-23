.. Copyright (c) 2015-2017, Exa Analytics Development Team
.. Distributed under the terms of the Apache License 2.0

########################
Introduction
########################
The application program interface (API) is the syntax by which a user or developer
interacts with the code. The API is presented in order of dependencies and/or
requirements. Low level functionality (objects that make up the foundation of the
framework) are presented first. High level functionality is presented later. Users
may want to start with the :ref:`examples-label` page or get additional information 
interactively.

.. code-block:: python

    help(exa.Editor)
    exa.Editor?      # In Jupyter notebook

.. automodule:: exa.__init__
    :members:

.. toctree::
    :maxdepth: 1

    root/01_init.rst
    root/02_err.rst
    root/03_mcs.rst
    root/04_util.rst
    root/05_tests.rst
