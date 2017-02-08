# -*- coding: utf-8 -*-
# Copyright (c) 2015-2017, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Exa is a framework for data management, computation, analytics, and
visualization. It leverages the Python data stack (`PyData`_) and uses the
`Jupyter Notebook`_ as a frontend. Data specific applications can be built
atop the exa package.

- :mod:`~exa.app.__init__`: Jupyter notebook frontend
- :mod:`~exa.cms.__init__`: Content management system
- :mod:`~exa.compute.__init__`: Dispatching and support for computation
- :mod:`~exa.core.__init__`: Core classes - Editor and Container
- :mod:`~exa.__main__`: Application launchers
- :mod:`~exa._config`: Configuration
- :mod:`~exa._version`: Version information
- :mod:`~exa.errors`: Base error handling
- :mod:`~exa.mpl`: Wrappers for static plotting
- :mod:`~exa.tester`: Support for unit and doc tests
- :mod:`~exa.tex`: LaTeX support
- :mod:`~exa.typed`: Strongly typed abstract base class

.. _PyData: http://pydata.org/
.. _Jupyter notebook: http://jupyter.org/
"""
# Import base modules
from exa import _version, _config, tester, errors, typed, mpl, tex, units

# Import sub-packages
from exa import cms, compute, core, tests, app

# Import user/dev API
from exa._version import __version__, version_info
from exa._config import print_config
from exa.mpl import sequential, diverging, qualitative
from exa.cms import File, Job, Project#, db
from exa.core import Editor, CSV#, DataSeries

from exa.app.threejs import Renderer, SubRenderer


def _jupyter_nbextension_paths():
    """
    Automatically generated by the `cookiecutter`_.

    .. _cookiecutter: https://github.com/jupyter/widget-cookiecutter
    """
    return [{
        'section': 'notebook',
        'src': '../build/widgets',
        'dest': 'jupyter-exa',
        'require': 'jupyter-exa/extension'
    }]
