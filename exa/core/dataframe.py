# -*- coding: utf-8 -*-
# Copyright (c) 2015-2017, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
DataFrame
########################
Dataframes are tabular like data objects with columns and indices. They can
represent multi-dimensional, multi-featured data. See `pandas DataFrame`_ for
more information.

In order to build data processing and visualization systems, a known and
systematic data structure is required. The :class:`~exa.core.dataframe.DataFrame`
provides this by enforcing minimum required columns. This allows for processing
and visualization algorithms to be built around dataframes containing known
data (such as coordinates or fields).

The :class:`~exa.core.dataframe.DataFrame` also provides support for additional
metadata using the ``meta`` attribute, similar to other data objects provided
within this framework. In all other aspects, this object behaves identically to
its `pandas DataFrame`_ counterpart.

.. _pandas DataFrame: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html
"""
import six
import numpy as np
import pandas as pd
from .base import Base


_ints = six.integer_types + (np.int8, np.int16, np.int32, np.int64)


class ColumnError(Exception):
    """Raised when a required dimension or feature (column) is missing."""
    @staticmethod
    def default(*columns):
        cols = ", ".join(columns)
        msg = "Missing required column(s): {}"
        return msg.format(cols)

    def __init__(self, *columns, **kwargs):
        msg = kwargs.pop("msg", None)
        msg = self.default(*columns) if msg is None else msg
        super(ColumnError, self).__init__(msg)


class DataFrame(pd.DataFrame, Base):
    """
    A dataframe like object with support for required columns.

    The attribute ``_required_columns`` may be used to enforce dataframe creation
    only when certain minimum requirements are satisfied. By convention this
    object should be a dictionary with key being the column names and values of
    3-tuples; the first entry in the tuple is the column description, the second
    contains valid dtypes, and the third containing aliases.

    .. code-block:: Python

        class MyDF(DataFrame):
            # Docstring describing purpose of this object
            _required_columns = {'col': ("description", int, ("Col", "COL"))

    In the above example, the required column is called ``col``. The tuple values
    first give a description, then the type(s), then the aliases. Multiple types
    can be given in the same way as multiple aliases are given above.
    """
    _metadata = ("name", "meta")
    _required_columns = None

    def info(self):
        """
        Display description, data type(s), and alias(es) of required columns.

        If no columns are required, none is returned.
        """
        if isinstance(self._required_columns, dict):
            cols = ["description", "types", "aliases"]
            rinf = pd.DataFrame.from_dict(self._required_columns, orient="index")
            rinf.columns = cols[:len(rinf.columns)]
            inf = pd.Series(self.columns).to_frame().set_index(0)
            return pd.concat((inf, rinf), axis=1, ignore_index=True)

    @property
    def _constructor(self):
        return DataFrame

    def _html_repr_(self):
        return super(DataFrame, self)._html_repr_()

    def __init__(self, *args, **kwargs):
        name = kwargs.pop("name", None)
        meta = kwargs.pop("meta", None)
        super(DataFrame, self).__init__(*args, **kwargs)
        if self._required_columns is not None:
            missing = set(self._required_columns.keys()).difference(self.columns)
            if len(missing) > 0:
                raise ColumnError(*missing)
        self.name = name
        self.meta = meta



class SectionDataFrame(DataFrame):
    """
    A dataframe that describes the sections given in the current parsing editor.
    """
    _section_name_prefix = "section"
    _required_columns = {'parser': ("Name of associated section or parser object", ),
                         'start': ("Section starting line number", _ints, ),
                         'end': ("Section ending (non-inclusive) line number", _ints, )}

    @classmethod
    def from_dct(cls, dct):
        """
        A helper method for creating this dataframe

        Args:
            dct (dict): Dictionary containing 'parser', 'start', and 'end' key-value pairs
        """
        df = cls.from_dict(dct)
        df['attribute'] = [cls._section_name_prefix+str(i).zfill(len(str(len(df)))) for i in df.index]
        df = df.loc[:, list(cls._required_columns) + list(set(df.columns).difference(cls._required_columns))]
        df.index.name = cls._section_name_prefix
        return df
