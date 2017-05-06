.. Copyright (c) 2015-2017, Exa Analytics Development Team
.. Distributed under the terms of the Apache License 2.0

.. _api-label:

########################
User Docs
########################
The following sections describe syntax and usage of the functions and classes
provided by the Exa package. Documentation is organized for the typical use case;
a collection of structure text files need to be parsed into Pythonic data objects
and then organized into a container to facilitate visualization. Useful examples 
can be found at :ref:`examples-label` or via help::

    import exa
    help(exa)           # Package help
    help(exa.isotopes)  # Module help
    help(exa.Editor)    # Class help
    exa.Editor?         # In an IPython environment (including the Jupyter notebook)

.. automodule:: exa.__init__
    :members:
    
.. automodule:: exa._version
    :members:

.. toctree::
    :maxdepth: 2
    :caption: Editors

    api/editor.rst
    api/parsing.rst

.. toctree::
    :maxdepth: 2
    :caption: Data Objects

    api/container.rst

.. toctree::
    :maxdepth: 2
    :caption: Utilities

    api/mpl.rst
    api/tex.rst
    api/constants.rst
    api/units.rst
    api/isotopes.rst

.. toctree::
    :maxdepth: 1
    :caption: Unittests

    api/units_constants_isotopes_tests.rst
    api/editor_parser_tests.rst


########################
Dev Docs
########################

.. toctree::
    :maxdepth: 2

    api/special.rst
    api/base.rst
    api/dev_tests.rst
