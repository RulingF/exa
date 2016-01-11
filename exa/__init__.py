# -*- coding: utf-8 -*-
'''
exa
==============
This package provides the core functionality required for the
'''
import sys as _sys
import re as _re
import os as _os
import atexit as _ae
import numpy as _np
import pandas as _pd
import scipy as _sp
import seaborn as _sns
import json as _json


_sns.set_context('poster', font_scale=1.3)
_sns.set_palette('colorblind')
_sns.set_style('white')


__exa_version__ = (0, 1, 0)    # Version number is defined here!
__version__ = '.'.join((str(v) for v in __exa_version__))
_idx = _pd.IndexSlice


from exa.config import Config
_ae.register(Config.save)
from exa.log import log_tail, log_head, setup
setup()
from exa.testers import run_unittests, run_doctests
from exa.tools import install_notebook_widgets, initialize_database
from exa.relational import commit as _commit
from exa.relational import _cleanup_anon_sessions
from exa.relational import (
    Force, Dose, Angle, Mass, Length, Frequency, Energy, Dipole, Temperature,
    Charge, MolarMass, Luminosity, Current, Acceleration, Amount, Time,
    Isotope, Constant, Dashboard
)
_ae.register(_cleanup_anon_sessions)
_ae.register(_commit)
from exa.container import Container

# API cleanup
del setup, config, testers, log
