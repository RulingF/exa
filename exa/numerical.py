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


class _DataRepr:
    '''
    '''
    _indices = []       # Required index names (typically single valued list)
    _columns = []       # Required column entries
    _categories = {}    # Column name, original type pairs ('label', int) that can be compressed to a category

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

    def __repr__(self):
        name = self.__class__.__name__
        n = len(self)
        return '{0}(len: {1})'.format(name, n)

    def __str__(self):
        return self.__repr__()


class _HasTraits(_DataRepr):
    '''
    Base dataframe class providing trait support for :class:`~pandas.DataFrame`
    like objects.
    '''
    _precision = 4      # Default number of decimal places passed by traits
    _traits = []        # Trait names (as strings)
    _groupbys = []      # Column names by which to group the data


class Series(_HasTraits, pd.Series):
    '''
    Trait supporting analogue of :class:`~pandas.Series`.
    '''
    pass


class DataFrame(_HasTraits, pd.DataFrame):
    '''
    Trait supporting analogue of :class:`~pandas.DataFrame`.

    Note:
        Columns, indices, etc. are only enforced if the dataframe has non-zero
        length.
    '''
    @property
    def _fi(self):
        return self.index[0]

    @property
    def _li(self):
        return self.index[-1]

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

        Warning:
            The algorithm's performance could be improved: in the case where
            each group has *N* values that are the same to each other but
            unique with respect to other groups' values all values are sent to
            the frontend!

        .. _trait type: http://traitlets.readthedocs.org/en/stable/trait_types.html
        .. _Float: http://traitlets.readthedocs.org/en/stable/trait_types.html#traitlets.Float
        '''
        groups = None
        if self._groupbys:
            self._revert_categories()              # We cannot groupby category
            groups = self.groupby(self._groupbys)
        for name in self._traits:
            if name in self.columns:
                if np.all(np.isclose(self[name], self.ix[fi, name])):
                    value = self.ix[self._fi, name]
                    dtype = type(value)
                    if dtype is np.int64 or dtype is np.int32:
                        trait = Integer(value)
                    elif dtype is np.float64 or dtype is np.float32:
                        trait = Float(value)
                    else:
                        raise TypeError('Unknown type for {0} with type {1}'.format(name, dtype))

            elif all((t in self.columns for t in name.split())):
                trait = None
                # Name mangle to allow similar column in different data objects
                trait_name = '_'.join((self.__class__.__name__.lower(), name))
                if np.all(np.isclose(self[name], self.ix[fi, name])):    # Don't send duplicate data,
                    value = self.ix[fi, name]                            # rather send a single trait
                    dtype = type(value)                                  # that contains the value
                    if dtype is np.int64 or dtype is np.int32:           # representative of all objects.
                        trait = Integer(value)
                    elif dtype is np.float64 or dtype is np.float32:
                        trait = Float(value)
                    else:
                        raise TypeError('Unknown type for {0} with type {1}'.format(name, dtype))
                elif groups:

                    trait = Unicode(groups.apply(lambda g: g[name].values).to_json())
                else:
                    trait = self[name].to_json(orient='values')
                traits[trait_name] = trait.tag(sync=True)
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


class SparseFrame(_DataRepr, pd.SparseDataFrame):
    '''
    A sparse dataframe used to update it's corresponding
    :class:`~exa.ndframe.DataFrame` or a truly sparse data store.
    '''
    pass


#    _key = []   # This is both the index and the foreign DataFrame designation.
#
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        if len(self) > 0:
#            name = self.__class__.__name__
#            missing = set(self._key).difference(self.index.names)
#            if missing:
#                raise RequiredIndexError(missing, name)
#
#    def __repr__(self):
#        return '{0}'.format(self.__class__.__name__)
#
#    def __str__(self):
#        return self.__class__.__name__



#    def _as_raw(self, which=[]):
#        '''
#        Internal conversion from categories to raw types.
#
#        If no argument is provided, will convert all categories.
#
#        Args:
#            which: String or list of strings of column names to convert
#        '''
#        for name, dtype in self.__categories:
#            if which == [] or name in which or name == which:
#                self[col] = self[col].astype(dtype)
#
#    def _as_cat(self, which=[]):
#        '''
#        Internal conversion to categories from raw types.
#
#        If no argument is provided, will convert all categories.
#
#        Args:
#            which: String or list of strings of column names to convert
#        '''
#        for name, dtype in self._categories:
#            if which == [] or name in which or name == which:
#                self[col] = self[col].astype('category')
#
#    def get_trait_values(self):
#        '''
#        Returns:
#            traits (dict): Traits to be added to the DOMWidget (:class:`~exa.relational.container.Container`)
#        '''
#        traits = {}
#        if len(self) > 0:
#            self._prep_trait_values()
#            groups = None
#            if self._groupbys:
#                groups = self.groupby(self._groupbys)
#            for trait in self._traits:
#                name = '_'.join(('', self.__class__.__name__.lower(), trait))
#                if trait in self.columns:
#                    if self._groupbys:
#                        traits[name] = groups.apply(lambda group: group[trait].astype('O').values).to_json()
#                    else:
#                        traits[name] = self[trait].to_json(orient='values')
#                else:
#                    traits[name] = ''
#            self._post_trait_values()
#        return traits
#
#    def _get_column_values(self, *columns, dtype='f8'):
#        '''
#        '''
#        data = np.empty((len(columns), ), dtype='O')
#        for i, column in enumerate(columns):
#            data[i] = self[column]
#        return np.vstack(data).T.astype(dtype)
#
#    def _get_max_values(self, *columns, dtype='f8'):
#        '''
#        '''
#        data = np.empty((len(columns), ), dtype=dtype)
#        for i, column in enumerate(columns):
#            data[i] = self[column].max()
#        return data
#
#    def _get_min_values(self, *columns, dtype='f8'):
#        '''
#        '''
#        data = np.empty((len(columns), ), dtype=dtype)
#        for i, column in enumerate(columns):
#            data[i] = self[column].min()
#        return data
#
#    def _prep_trait_values(self):
#        '''
#        '''
#        pass
#
#    def _post_trait_values(self):
#        '''
#        '''
#        pass
#
#    def _get_by_index(self, index):
#        '''
#        '''
#        if len(self) > 0:
#            cls = self.__class__
#            if self._groupbys:
#                getter = self[self._groupbys].unique()[index]
#                return cls(self.groupby(self._groupbys).get_group(getter))
#            else:
#                return cls(self.ix[index:index, :])
#        else:
#            return self
#
#    def _get_by_indices(self, indices):
#        '''
#        '''
#        if len(self) > 0:
#            cls = self.__class__
#            if self._groupbys:
#                getters = self[self._groupbys].unique()[indices]
#                return cls(self[self[self._groupbys].isin(getters)])
#            else:
#                return cls(self.ix[indices, :])
#        else:
#            return self
#
#    def _get_by_slice(self, s):
#        '''
#        '''
#        if len(self) > 0:
#            cls = self.__class__
#            indices = self.index
#            if self._groupbys:
#                indices = self[self._groupbys].unique()
#            start = indices[0] if s.start is None else indices[s.start]
#            stop = indices[-1] if s.stop is None else indices[s.stop]
#            step = s.step
#            indices = indices[start:stop:step]
#            if self._groupbys:
#                return cls(self.ix[self[self._groupbys].isin(indices)])
#            return cls(self.ix[indices, :])
#        else:
#            return self
#
#class Updater(pd.SparseDataFrame):
#    '''
#    Sparse dataframe used to update a full :class:`~exa.dataframes.DataFrame`.
#    '''
#    _key = []   # This is both the index and the foreign DataFrame designation.
#
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        if len(self) > 0:
#            name = self.__class__.__name__
#            missing = set(self._key).difference(self.index.names)
#            if missing:
#                raise RequiredIndexError(missing, name)
#
#    def __repr__(self):
#        return '{0}'.format(self.__class__.__name__)
#
#    def __str__(self):
#        return self.__class__.__name__
#
#
#class ManyToMany(pd.DataFrame):
#    '''
#    A DataFrame with only two columns which enumerates the relationship information.
#    '''
#    _fkeys = []
#
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        if len(self) > 0:
#            if len(self._fkeys) != 2 or  not np.all([col in self._fkeys for col in self.columns]):
#                raise RequiredColumnError(self._fkeys, self.__class__.__name__)
#
#    def __repr__(self):
#        return '{0}'.format(self.__class__.__name__)
#
#    def __str__(self):
#        return self.__class__.__name__
#
