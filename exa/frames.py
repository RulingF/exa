# -*- coding: utf-8 -*-
'''
Custom DataFrame for exa Analytics
====================================
'''
from traitlets import Unicode, Dict
from exa import _np as np
from exa import _pd as pd
from exa.errors import RequiredIndexError, RequiredColumnError


class DataFrame(pd.DataFrame):
    '''
    Behaves just like a :py:class:`~pandas.DataFrame`, but enforces minimum
    column and index requirements and keeps track of relations (with other
    DataFrames). Contains logic for creating "traits" for use within the a
    JavaScript visualization system. Finally tracks physical units.
    '''
    _pkeys = []         # List of required column names
    _fkeys = []         # List of column names which correspond to another DataFrame's columns
    _traits = []        # List of column names that are passed to JavaScript
    _groupbys = []      # List of column names on which to group the data
    _categories = []    # List of category name, raw type pairs
    _column_units = {}  # Dictionary of column name, physical unit pairs

    def _as_raw(self, which=[]):
        '''
        Internal conversion from categories to raw types.

        If no argument is provided, will convert all categories.

        Args:
            which: String or list of strings of column names to convert
        '''
        for name, dtype in self.__categories:
            if which == [] or name in which or name == which:
                self[col] = self[col].astype(dtype)

    def _as_cat(self, which=[]):
        '''
        Internal conversion to categories from raw types.

        If no argument is provided, will convert all categories.

        Args:
            which: String or list of strings of column names to convert
        '''
        for name, dtype in self.__categories:
            if which == [] or name in which or name == which:
                self[col] = self[col].astype('category')

    def _get_trait_values(self):
        '''
        Returns:
            traits (dict): Traits to be added to the DOMWidget (:class:`~exa.relational.container.Container`)
        '''
        traits = {}
        if len(self) > 0:
            self._prep_trait_values()
            groups = None
            if self._groupbys:
                groups = self.groupby(self._groupbys)
            for trait in self.__traits__:
                name = '_'.join(('', self.__class__.__name__.lower(), trait))
                if trait in self.columns:
                    if self._groupbys:
                        traits[name] = groups.apply(lambda group: group[trait].values).to_json()
                    else:
                        traits[name] = self[trait].to_json(orient='values')
                else:
                    traits[name] = ''
            self._post_trait_values()
        return traits

    def _get_column_values(self, *columns, dtype='f8'):
        '''
        '''
        data = np.empty((len(columns), ), dtype=dtype)
        for i, column in enumerate(columns):
            data[i] = self[column]
        return np.vstack(data).T.astype(dtype)

    def _get_max_values(self, *columns, dtype='f8'):
        '''
        '''
        data = np.empty((len(columns), ), dtype=dtype)
        for i, column in enumerate(columns):
            data[i] = self[column].max()
        return data

    def _get_min_values(self, *columns, dtype='f8'):
        '''
        '''
        data = np.empty((len(columns), ), dtype=dtype)
        for i, column in enumerate(columns):
            data[i] = self[column].min()
        return data

    def _prep_trait_values(self):
        '''
        '''

    def _post_trait_values(self):
        '''
        '''
        pass

    def _get_by_index(self, index):
        '''
        '''
        if len(self) > 0:
            cls = self.__class__
            if self._groupbys:
                getter = self[self._groupbys].unique()[index]
                return cls(self.groupby(self._groupbys).get_group(getter))
            else:
                return cls(self.ix[index:index, :])
        else:
            return self

    def _get_by_indices(self, indices):
        '''
        '''
        if len(self) > 0:
            cls = self.__class__
            if self._groupbys:
                getters = self[self._groupbys].unique()[indices]
                return cls(self[self[self._groupbys].isin(getters)])
            else:
                return cls(self.ix[indices, :])
        else:
            return self

    def _get_by_slice(self, s):
        '''
        '''
        if len(self) > 0:
            cls = self.__class__
            indices = self.index
            if self._groupbys:
                indices = self[self._groupbys].unique()
            start = indices[0] if s.start is None else indices[s.start]
            stop = indices[-1] if s.stop is None else indices[s.stop]
            step = s.step
            indices = indices[start:stop:step]
            if self._groupbys:
                return cls(self.ix[self[self._groupbys].isin(indices)])
            return cls(self.ix[indices, :])
        else:
            return self

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(self) > 0:
            if self._pkeys:
                missing_pkeys = set(self._pkeys).difference(self.index.names)
                if missing_pkeys:
                    if list(missing_pkeys) == self._pkeys:
                        self.index.names = self._pkeys
                    else:
                        raise RequiredIndexError(missing_pkeys, self.__class__.__name__)
            if self._fkeys:
                missing_fkeys = set(self._fkeys).difference(self.columns)
                if missing_fkeys:
                    raise RequiredColumnError(missing_fkeys, self.__class__.__name__)

    def __repr__(self):
        return '{0}(rows: {1}, cols: {2})'.format(self.__class__.__name__,
                                                  len(self), len(self.columns))

    def __str__(self):
        return self.__repr__()


class Updater(pd.SparseDataFrame):
    '''
    Sparse dataframe used to update a full :class:`~exa.dataframes.DataFrame`.
    '''
    __key__ = []   # This is both the index and the foreign DataFrame designation.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(self) > 0:
            name = self.__class__.__name__
            missing = set(self.__key__).difference(self.index.names)
            if missing:
                raise RequiredIndexError(missing, name)

    def __repr__(self):
        return '{0}'.format(self.__class__.__name__)

    def __str__(self):
        return self.__class__.__name__


class ManyToMany(pd.DataFrame):
    '''
    A DataFrame with only two columns which enumerates the relationship information.
    '''
    __fkeys__ = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(self) > 0:
            if len(self.__fkeys__) != 2 or  not np.all([col in self.__fkeys__ for col in self.columns]):
                raise RequiredColumnError(self.__fkeys__, self.__class__.__name__)

    def __repr__(self):
        return '{0}'.format(self.__class__.__name__)

    def __str__(self):
        return self.__class__.__name__
