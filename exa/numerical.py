# -*- coding: utf-8 -*-
'''
Custom DataFrame (and Related) Classes
=========================================
The :class:`~exa.dataframe.DataFrame` inherits :class:`~pandas.DataFrame` and
behaves just like it, but it provides special methods for extracting trait
data from the frame. The trait data is used by :class:`~exa.widget.ContainerWidget`
(and its subclasses) and the web gui to generate interactive data visualizations.
Because these dataframes have context about their data, they also provide
convience methods for in memory data compression (using `categories`_).

See Also:
    Modules :mod:`~exa.container` and :mod:`~exa.widget` may provide context.

.. _categories: http://pandas-docs.github.io/pandas-docs-travis/categorical.html
'''
import numpy as np
import pandas as pd
from traitlets import Unicode, Integer, Float
from exa.error import RequiredIndexError, RequiredColumnError


class NDBase:
    '''
    Base class for custom dataframe and series objects that have traits.
    '''
    _precision = 4      # Default number of decimal places passed by traits
    _traits = []        # Traits present as dataframe columns (or series values)

    def __repr__(self):
        name = self.__class__.__name__
        n = len(self)
        return '{0}(len: {1})'.format(name, n)

    def __str__(self):
        return self.__repr__()


class Series(NDBase, pd.Series):
    '''
    Trait supporting analogue of :class:`~pandas.Series`.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DataFrame(NDBase, pd.DataFrame):
    '''
    Trait supporting analogue of :class:`~pandas.DataFrame`.

    Note:
        Columns, indices, etc. are only enforced if the dataframe has non-zero
        length.
    '''
    _groupbys = []      # Column names by which to group the data
    _indices = []       # Required index names (typically single valued list)
    _columns = []       # Required column entries
    _categories = {}    # Column name, original type pairs ('label', int) that can be compressed to a category

    @property
    def _fi(self):
        return self.index[0]

    @property
    def _li(self):
        return self.index[-1]

    def _revert_categories(self):
        '''
        Change all columns of type category to their native type.
        '''
        for column, dtype in self._categories.items():
            self[column] = self[column].astype(dtype)

    def _set_categories(self):
        '''
        Change all category like columns from their native type to category type.
        '''
        for column, dtype in self._categories.items():
            self[column] = self[column].astype('category')

    def _get_custom_traits(self):
        '''
        Placeholder function to be overwritten when custom trait creation is
        required

        Returns:
            traits (dict): Dictionary of traits to be added
        '''
        return {}

    def _get_traits(self):
        '''
        Generate trait objects from column data.

        This function will group columns by the :class:`~exa.numerical.DataFrame`'s
        **_groupbys** attribute, select the column (or columns) that specify a
        single trait, and package that up as a trait to be used by the frontend.

        Note:
            This function decides what `trait type`_ to use. Typically, a
            column (or columns) containing unique data is sent as a (grouped)
            json string. If the column contains non-unique data, this function
            will send a single value of the appropriate type (e.g. `Float`_) so
            as to duplicate the least amount of data possible (and have the least
            communication overhead possible).

        See Also:
            The collecting function of the JavaScript side of things is the
            **get_trait** method in **container.js**.

        Tip:
            The algorithm's performance could be improved: in the case where
            each group has *N* values that are the same to each other but
            unique with respect to other groups' values all values are sent to
            the frontend!

        .. _trait type: http://traitlets.readthedocs.org/en/stable/trait_types.html
        .. _Float: http://traitlets.readthedocs.org/en/stable/trait_types.html#traitlets.Float
        '''
        traits = self._get_custom_traits()
        groups = None
        prefix = self.__class__.__name__.lower()
        if self._groupbys:
            self._revert_categories()                    # Category dtype can't be used
            groups = self.groupby(self._groupbys)        # for grouping.
        for name in self._traits:
            if name in self.columns:
                trait_name = '_'.join((prefix, name))    # Name mangle to ensure uniqueness
                if np.all(np.isclose(self[name], self.ix[self._fi, name])):
                    value = self.ix[self._fi, name]
                    dtype = type(value)
                    if dtype is np.int64 or dtype is np.int32:
                        trait = Integer(value)
                    elif dtype is np.float64 or dtype is np.float32:
                        trait = Float(value)
                    else:
                        raise TypeError('Unknown type for {0} with type {1}'.format(name, dtype))
                elif groups:                              # Else send grouped traits
                    trait = Unicode(groups.apply(lambda g: g[name].values).to_json(orient='values'))
                else:                                     # Else send flat values
                    trait = self[name].to_json(orient='values')
                traits[trait_name] = trait.tag(sync=True)
            elif name == self.index.names[0]:             # Otherwise, if index, send flat values
                trait_name = '_'.join((prefix, name))
                traits[trait_name] = Unicode(pd.Series(self.index).to_json(orient='values')).tag(sync=True)
        if self._groupbys:
            self._set_categories()
        return traits

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(self) > 0:
            name = self.__class__.__name__
            if self._columns:
                missing = set(self._columns).difference(self.columns)
                if missing:
                    raise RequiredColumnError(missing, name)
            if self._indices:
                missing = set(self._indices).difference(self.index.names)
                if missing:
                    raise RequiredIndexError(missing, name)


class Field(DataFrame):
    '''
    A dataframe for storing field (meta)data along with the actual field values.

    The storage of field values may be in the form of a scalar field (via
    :class:`~exa.numerical.Series`) or vector field (via
    :class:`~exa.numerical.DataFrame`). The field index (of this dataframe)
    corresponds to the index in the list of field value data.

    +-------------------+----------+-------------------------------------------+
    | Column            | Type     | Description                               |
    +===================+==========+===========================================+
    | nx                | int      | number of dimensionsin x                  |
    +-------------------+----------+-------------------------------------------+
    | ny                | int      | number of dimensionsin y                  |
    +-------------------+----------+-------------------------------------------+
    | nz                | int      | number of dimensionsin z                  |
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
    '''
    _indices = ['field']
    _columns = ['nx', 'ny', 'nz', 'ox', 'oy', 'oz', 'xi', 'xj', 'xk',
                'yi', 'yj', 'yk', 'zi', 'zj', 'zk']
    @property
    def fields(self):
        '''
        List of fields with order matching that of the field table.

        Returns:
            fields (list): List of fields
        '''
        return self._fields

    def field(self, which):
        '''
        Select a specific field from the list of fields.
        '''
        return self.fields[which]

    def __init__(self, *args, fields=None, **kwargs):
        '''
        Args:
            fields (dict): Dictionary of field
        '''
        super().__init__(*args, **kwargs)
        self._fields = fields
