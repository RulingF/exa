# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Compilation Using `Numba`_
#############################
This module provides conversion between exa syntax and `Numba`_ syntax.

.. _Numba: http://numba.pydata.org/
"""
try:
    import numba as nb
except ImportError:
    pass


def jit(func, sig=None, nopython=False, nogil=False, cache=False):
    raise NotImplementedError()


def vectorize(func, signatures=None, identity=None, nopython=True, target='cpu'):
    raise NotImplementedError()


def guvectorize(func, signatures, layout, identity=None, nopython=True, target='cpu'):
    raise NotImplementedError()


def compiler(func, *itypes, **flags):
    """Convert generic arguments to numba specific arguments."""
    target = flags.pop("target", "cpu")
    core = flags.pop("core", "ram")
    mp = flags.pop("mp", "serial")
    return (target, core, mp), func
