# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Compilers enable automatic compilation of Python functions upon dispatch.

See Also:
    :mod:`~exa.compute.dispatch`
"""
# Import modules
from exa.compute.compilers import wrapper, nb

# Import sub-packages
from exa.compute.compilers import tests

# Import user/dev API
from exa.compute.compilers.wrapper import available_compilers, compile_function
