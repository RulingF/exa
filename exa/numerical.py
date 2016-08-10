# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Trait Supporting Data Objects
###################################
Data objects are used to store typed data coming from an external source (for
example a file on disk). There are three primary data objects provided by
this module, :class:`~exa.numerical.Series`, :class:`~exa.numerical.DataFrame`,
and :class:`~exa.numerical.Field`. The purpose of these objects is to facilitate
conversion of data into "traits" used in visualization and enforce relationships
between data objects in a given container. Any of the objects provided by this
module may be extended.

See Also:
    For information about traits and how they allow enable dynamic visualizations
    see :mod:`~exa.widget`. For usage in container objects, see :mod:`~exa.container`.
"""
import warnings
import numpy as np
import pandas as pd
from numbers import Integral, Real
from traitlets import Unicode, Integer, Float
from exa.error import RequiredColumnError


class Numerical:
    """
    Base class for :class:`~exa.numerical.Series`, :class:`~exa.numerical.DataFrame`,
    and :class:`~exa.numerical.Field` objects, providing default trait
    functionality and clean representations when present as part of containers.
    """
    def slice_naive(self, key):
        """
        Slice a data object based on its index, either by value (.ix) or
        position (.iloc).

        Args:
            key: Single index value, slice, tuple, or list of indices/positionals

        Returns:
            data: Slice of self
        """
        cls = self.__class__
        key = check_key(self, key)
        return cls(self.ix[key])

    def _custom_traits(self):
        """Placeholder for custom traits depending only on self."""
        return {}

    def __repr__(self):
        name = self.__class__.__name__
        return '{0}{1}'.format(name, self.shape)

    def __str__(self):
        return self.__repr__()


class BaseSeries(Numerical):
    """
    Base class for dense and sparse series objects (labeled arrays).

    Attributes:
        _sname (str): May have a required name (default None)
        _iname (str: May have a required index name
        _stype (type): May have a required value type
        _itype (type): May have a required index type
        _precision (int): Precision for traits (JSON values)
        _index_trait (bool): Index as trait (default false)
    """
    # These attributes may be set when subclassing Series
    _sname = None           # Series may have a required name
    _iname = None           # Series may have a required index name
    _stype = None           # Series may have a required value type
    _itype = None           # Series may have a required index type
    _precision = None       # Precision for JSON values
    _index_trait = False    # Set to true if the index should be a trait

    def _update_traits(self):
        """
        By default, the trait representation is a unicode string of the values.
        Series traits always have the format:

        - values: "classnamelowercase_values"
        - index: "classnamelowercase_index"
        """
        traits = self._custom_traits()
        s = self
        if isinstance(self.dtype, pd.types.dtypes.CategoricalDtype) and self._stype is not None:
            s = self.astype(self._stype)
        prefix = '_'.join((self.__class__.__name__.lower(), self._name))
        p = 10 if self._precision is None else self._precision
        values = s.to_json(orient='values', double_precision=p)
        up = {prefix + '_values': Unicode(values).tag(sync=True)}
        if self._index_trait:
            indices = pd.Series(s.index.values).to_json(orient='values')
            up[prefix + '_index'] = Unicode(indices).tag(sync=True)
        traits.update(up)
        return traits

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._sname is not None and self.name != self._sname:
            if self.name is not None:
                warnings.warn("Object's name changed")
            self.name = self._sname
        if self._iname is not None and self.index.name != self._iname:
            if self.index.name is not None:
                warnings.warn("Object's index name changed")
            self.index.name = self._iname


class BaseDataFrame(Numerical):
    """
    Base class for dense and sparse dataframe objects (labeled matrices).

    Note:
        If the _cardinal attribute is populated, it will automatically be added
        to the _categories and _columns attributes.

    Attributes:
        _cardinal (tuple): Tuple of column name and raw type that acts as foreign key to index of another table
        _index (str): Name of index (may be used as foreign key in another table)
        _columns (list): Required columns
        _categories (dict): Dict of column names, raw types that if present will be converted to and from categoricals automatically
        _traits (list): List of columns that may (if present) be converted to traits on call to _update_traits
        _precision (dict): Dict of column names, ints, that if present will have traits of the specified (float) precision
    """
    _cardinal = None     # Tuple of column name and raw type that acts as foreign key to index of another table
    _index = None      # Name of index (may be used as foreign key in another table)
    _columns = []      # Required columns
    _categories = {}   # Dict of column names, raw types that if present will be converted to and from categoricals automatically
    _traits = []       # List of columns that may (if present) be converted to traits on call to _update_traits
    _precision = {}    # Dict of column names, ints, that if present will have traits of the specified (float) precision

    def cardinal_groupby(self):
        """
        Group this object on it cardinal dimension (_cardinal).

        Returns:
            grpby: Pandas groupby object (grouped on _cardinal)
        """
        g, t = self._cardinal
        self[g] = self[g].astype(t)
        grpby = self.groupby(g)
        self[g] = self[g].astype('category')
        return grpby

    def slice_cardinal(self, key):
        """
        Get the slice of this object by the value or values of the cardinal
        dimension.
        """
        cls = self.__class__
        key = check_key(self, key, cardinal=True)
        return cls(self[self[self._cardinal[0]].isin(key)])


class Series(BaseSeries, pd.Series):
    """
    Trait supporting analogue of :class:`~pandas.Series`.

    .. code-block:: Python

        class MySeries(exa.numerical.Series):
            _sname = 'data'        # series default name
            _iname = 'data_index'  # series default index name
            _precision = 2         # series precision for generating traits (of values)

        seri = MySeries(np.random.rand(10**5))
        traits = seri._update_traits()   # dict of traits generated from seri's values
    """
    def copy(self, *args, **kwargs):
        """
        Make a copy of this object.

        See Also:
            For arguments and description of behavior see `pandas docs`_.

        .. _pandas docs: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.copy.html
        """
        cls = self.__class__    # Note that type conversion does not perform copy
        return cls(pd.Series(self).copy(*args, **kwargs))


class DataFrame(BaseDataFrame, pd.DataFrame):
    """
    Trait supporting analogue of :class:`~pandas.DataFrame`.

    .. code-block:: Python

        class MyDF(exa.numerical.DataFrame):
            _cardinal = ('cardinal', int)
            _index = 'mydf_index'
            _columns = ['x', 'y', 'z', 'symbol']
            _traits = ['x', 'y', 'z']
            _categories = {'symbol': str}
            _precision = {'x': 2, 'y': 2, 'z': 3}
    """
    def copy(self, *args, **kwargs):
        """
        Make a copy of this object.

        See Also:
            For arguments and description of behavior see `pandas docs`_.

        .. _pandas docs: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.copy.html
        """
        cls = self.__class__    # Note that type conversion does not perform copy
        return cls(pd.DataFrame(self).copy(*args, **kwargs))

    def _revert_categories(self):
        """
        Inplace conversion to categories.
        """
        for column, dtype in self._categories.items():
            if column in self.columns:
                self[column] = self[column].astype(dtype)

    def _set_categories(self):
        """
        Inplace conversion from categories.
        """
        for column, dtype in self._categories.items():
            if column in self.columns:
                self[column] = self[column].astype('category')

    def _update_traits(self):
        """
        Generate trait objects from column data.

        This function will group columns (if applicable) and form JSON object strings
        from columns which have been declared as traits (using the _traits attribute).

        Note:
            This function decides what `trait type`_ to use. This will almost always
            be a JSON (unicode) string formatted to be parsed into an array like
            structure in Javascript.

        .. _trait type: http://traitlets.readthedocs.org/en/stable/trait_types.html
        """
        traits = self._custom_traits()
        self._revert_categories()
        prefix = self.__class__.__name__.lower()
        fi = self.index[0]
        grpby = None
        if self._cardinal is not None:
            grpby = self.cardinal_groupby()
        for name in self._traits:
            trait_name = '_'.join((prefix, str(name)))    # Name mangle to ensure uniqueness
            p = self._precision[name] if name in self._precision else 10
            if name in self:
                if np.all(np.isclose(self[name], self.ix[fi, name])):
                    value = self.ix[fi, name]          # If all the entries are the same
                    if isinstance(value, Integral):    # only send a single entry to JS.
                        trait = Integer(int(value))
                    elif isinstance(value, Real):
                        trait = Float(float(value))
                    elif isinstance(value, str):
                        trait = Unicode(str(value))
                    else:
                        raise TypeError("Unknown type for {0} with type {1}".format(name, dtype))
                elif grpby:    # If groups exist, make a list of list(s)
                    series = grpby.apply(lambda g: g[name].values)    # Creats a "Series" of array like records
                    trait = Unicode(series.to_json(orient='values', double_precision=p))
                else:           # Otherwise, just send the flattened values
                    string = self[name].to_json(orient='values', double_precision=p)
                    trait = Unicode(string)
                traits[trait_name] = trait.tag(sync=True)
            elif name == self.index.names[0]:   # If not in columns, but is index name, send index
                trait_name = '_'.join((prefix, str(name)))
                string = pd.Series(self.index.values).to_json(orient='values')
                traits[trait_name] = Unicode(string).tag(sync=True)
        self._set_categories()
        return traits

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._cardinal is not None:
            self._categories[self._cardinal[0]] = self._cardinal[1]
            self._columns.append(self._cardinal[0])
        self._set_categories()
        if len(self) > 0:
            name = self.__class__.__name__
            if self._columns:
                missing = set(self._columns).difference(self.columns)
                if missing:
                    raise RequiredColumnError(missing, name)
            if self.index.name != self._index and self._index is not None:
                if self.index.name is not None:
                    warnings.warn("Object's index name changed from {} to {}".format(self.index.name, self._index))
                self.index.name = self._index


class Field(DataFrame):
    """
    A field is defined by field data and field values. Field data defines the
    discretization of the field (i.e. its origin in a given space, number of
    steps/step spaceing, and endpoint for example). Field values can be scalar
    (series) and/or vector (dataframe) data defining the magnitude and/or direction
    at each given point.

    Note:
        The convention for generating the discrete field data and ordering of
        the field values must be the same (e.g. discrete field points are
        generated x, y, then z and scalar field values are a series object
        ordered looping first over x then y, then z).

    In addition to the :class:`~exa.numerical.DataFrame` attributes, this object
    has the following:

    Attributes:
        _values_precision (int): Precision in values passed as traits
    """
    _values_precision = 10    # Floating point precision for values as traits

    def copy(self, *args, **kwargs):
        """
        Make a copy of this object.

        Note:
            Copies both field data and field values.

        See Also:
            For arguments and description of behavior see `pandas docs`_.

        .. _pandas docs: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.copy.html
        """
        cls = self.__class__    # Note that type conversion does not perform copy
        data = pd.DataFrame(self).copy(*args, **kwargs)
        values = [field.copy() for field in self.field_values]
        return cls(data, field_values=values)

    def memory_usage(self):
        """
        Get the combined memory usage of the field data and field values.
        """
        data = pd.DataFrame(self).memory_usage()
        values = 0
        for value in self.field_values:
            values += value.memory_usage()
        data['field_values'] = values
        return data

    def slice_naive(self, key):
        """
        Naively (on index) slice the field data and values.

        Args:
            key: Int, slice, or iterable to select data and values

        Returns:
            field: Sliced field object
        """
        cls = self.__class__
        key = check_key(self, key)
        enum = pd.Series(range(len(self)))
        enum.index = self.index
        values = self.field_values[enum[key].values]
        data = self.ix[key]
        return cls(data, field_values=values)

    def slice_cardinal(self, key):
        """
        """
        cls = self.__class__
        grpby = self.cardinal_groupby()


    def _custom_traits(self):
        """
        Obtain field values using the custom trait getter (called automatically
        by :func:`~exa.numerical.Numerical._update_traits`).
        """
        self._revert_categories()
        traits = {}
        if self._cardinal is not None:
            grpby = self.cardinal_groupby()
            string = str(list(grpby.groups.values())).replace(' ', '')
            traits['field_indices'] = Unicode(string).tag(sync=True)
        else:
            string = pd.Series(self.index.values).to_json(orient='values')
            traits['field_indices'] = Unicode(string).tag(sync=True)
        s = pd.Series({i: field.values for i, field in enumerate(self.field_values)})
        json_string = s.to_json(orient='values', double_precision=self._values_precision)
        traits['field_values'] = Unicode(json_string).tag(sync=True)
        self._set_categories()
        return traits

    def __init__(self, *args, field_values=None, **kwargs):
        # The following check allows creation of a single field (whose field data
        # comes from a series object and field values from another series object).
        if isinstance(args[0], pd.Series):
            args = (args[0].to_frame().T, )
        super().__init__(*args, **kwargs)
        if isinstance(field_values, (list, tuple, np.ndarray)):
            self.field_values = [Series(v) for v in field_values]    # Convert type for nice repr
        elif field_values is None:
            self.field_values = []
        elif isinstance(field_values, pd.Series):
            self.field_values = [Series(field_values)]
        else:
            raise TypeError("Wrong type for field_values with type {}".format(type(field_values)))
        for i in range(len(self.field_values)):
            self.field_values[i].name = i


class Field3D(Field):
    """
    Dataframe for storing dimensions of a scalar or vector field of 3D space.

    +-------------------+----------+-------------------------------------------+
    | Column            | Type     | Description                               |
    +===================+==========+===========================================+
    | nx                | int      | number of grid points in x                |
    +-------------------+----------+-------------------------------------------+
    | ny                | int      | number of grid points in y                |
    +-------------------+----------+-------------------------------------------+
    | nz                | int      | number of grid points in z                |
    +-------------------+----------+-------------------------------------------+
    | ox                | float    | field origin point in x                   |
    +-------------------+----------+-------------------------------------------+
    | oy                | float    | field origin point in y                   |
    +-------------------+----------+-------------------------------------------+
    | oz                | float    | field origin point in z                   |
    +-------------------+----------+-------------------------------------------+
    | xi                | float    | First component in x                      |
    +-------------------+----------+-------------------------------------------+
    | xj                | float    | Second component in x                     |
    +-------------------+----------+-------------------------------------------+
    | xk                | float    | Third component in x                      |
    +-------------------+----------+-------------------------------------------+
    | yi                | float    | First component in y                      |
    +-------------------+----------+-------------------------------------------+
    | yj                | float    | Second component in y                     |
    +-------------------+----------+-------------------------------------------+
    | yk                | float    | Third component in y                      |
    +-------------------+----------+-------------------------------------------+
    | zi                | float    | First component in z                      |
    +-------------------+----------+-------------------------------------------+
    | zj                | float    | Second component in z                     |
    +-------------------+----------+-------------------------------------------+
    | zk                | float    | Third component in z                      |
    +-------------------+----------+-------------------------------------------+

    Note:
        Each field should be flattened into an N x 1 (scalar) or N x 3 (vector)
        series or dataframe respectively. The orientation of the flattening
        should have x as the outer loop and z values as the inner loop (for both
        cases). This is sometimes called C-major order, C-style order, and has
        the last index changing the fastest and the first index changing the
        slowest.

    See Also:
        :class:`~exa.numerical.Field`
    """
    _columns = ['nx', 'ny', 'nz', 'ox', 'oy', 'oz', 'xi', 'xj', 'xk',
                'yi', 'yj', 'yk', 'zi', 'zj', 'zk']
    _traits = ['nx', 'ny', 'nz', 'ox', 'oy', 'oz', 'xi', 'xj', 'xk',
               'yi', 'yj', 'yk', 'zi', 'zj', 'zk']


class SparseSeries(BaseSeries, pd.SparseSeries):
    """Sparse implementation of :class:`~exa.numerical.Series`."""
    def copy(self, *args, **kwargs):
        """Make a copy of this object."""
        cls = self.__class__
        return cls(pd.SparseSeries(self).copy(*args, **kwargs))

    def _custom_traits(self):
        """Placeholder for custom traits."""
        return {}

    def _update_traits(self):
        """Sparse values can be traits."""
        traits = self._custom_traits()
        return traits


class SparseDataFrame(BaseDataFrame, pd.SparseDataFrame):
    """Trait supporting sparse dataframe."""
    def copy(self, *args, **kwargs):
        """Make a copy of this object."""
        cls = self.__class__
        return cls(pd.SparseDataFrame(self).copy(*args, **kwargs))

    def _custom_traits(self):
        """Placeholder for custom traits."""
        return {}

    def _update_traits(self):
        """Sparse columns that act as traits."""
        traits = self._custom_traits()
        return traits

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(self) > 0:
            name = self.__class__.__name__
            if self._columns:
                missing = set(self._columns).difference(self.columns)
                if missing:
                    raise RequiredColumnError(missing, name)
            if self.index.name != self._index and self._index is not None:
                if self.index.name is not None:
                    warnings.warn("Object's index name changed from {} to {}".format(self.index.name, self._index))
                self.index.name = self._index

def check_key(data_object, key, cardinal=False):
    """
    Update the value of an index key by matching values or getting positionals.
    """
    itype = (int, np.int32, np.int64)
    if not isinstance(key, itype + (slice, tuple, list, np.ndarray)):
        raise KeyError("Unknown key type {} for key {}".format(type(key), key))
    keys = data_object.index.values
    if cardinal and data_object._cardinal is not None:
        keys = data_object[data_object._cardinal[0]].unique()
    elif isinstance(key, itype) and key in keys:
        key = [data_object.index.values[key]]
    elif isinstance(key, itype) and key < 0:
        key = [data_object.index.values[key]]
    elif isinstance(key, itype):
        key = [key]
    elif isinstance(key, slice):
        key = data_object.index.values[key]
    elif isinstance(key, (tuple, list)) and not np.all(k in keys for k in key):
        key = data_object.index.values[key]
    return key
