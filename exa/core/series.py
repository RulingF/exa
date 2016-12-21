# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Exa Series
###################################
The :class:`~exa.core.series.Series` object supports index aliases and units.

See Also:
    http://pandas.pydata.org/
"""
import six
import pandas as pd
from exa.core.base import Meta, Alias
from exa.core.indexing import indexers


class Series(six.with_metaclass(Meta, pd.Series)):
    """
    A series is a single valued n dimensional array.

    Single valued means that a series only carries a single type or column of
    data (of a specific kind). Each element of the array is labeled by an index.
    The index can be a single dimension (e.g. an array of integers) or
    multidimensional. The dimensions of a series are determined by its index.
    """
    _getter_prefix = "compute"
    _metadata = ['name', 'units', 'aliases']

    @property
    def _constructor(self):
        return Series

    def __init__(self, *args, **kwargs):
        units = kwargs.pop("units", None)
        aliases = kwargs.pop("aliases", None)
        super(Series, self).__init__(*args, **kwargs)
        self.units = units
        self.aliases = aliases


for name, indexer in indexers():          # Calls pandas machinery
    setattr(Series, name, None)           # Need to unreference existing indexer
    Series._create_indexer(name, indexer) # Prior to instantiation new indexer
