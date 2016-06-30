# -*- coding: utf-8 -*-
'''
Base Container
########################
The :class:`~exa.container.BaseContainer` class is the primary object for
data processing, analysis, and visualization. Containers are composed of
n-dimensional spreadsheet-like (see :mod:`~exa.numerical`) objects whose
columns contain data for 2D and 3D visualization.

The :class:`~exa.container.BaseContainer` is akin to a :class:`~pandas.HDFStore`
in that it is a container for dataframes (and saves to an HDF5 file). It is
different in that it provides visualization tools access to the data contained
via automated JSON strings, transferrable between languages.

See Also:
    :mod:`~exa.relational.container` and :mod:`~exa.widget`
'''
import os
import numpy as np
import pandas as pd
import networkx as nx
from sys import getsizeof
from copy import deepcopy
from collections import OrderedDict
from traitlets import Bool
from collections import defaultdict
from sqlalchemy.orm.attributes import InstrumentedAttribute
from exa import global_config, mpl
from exa.widget import ContainerWidget
from exa.numerical import Series, DataFrame, SparseSeries, SparseDataFrame, Field
from exa.utility import convert_bytes


edge_colors = mpl.sns.color_palette('viridis', 2)
edge_types = ['idx-idx', 'idx-col']
edge_color_map = dict(zip(edge_types, edge_colors))
node_colors = mpl.sns.color_palette('viridis', 9)
node_types = [Field, pd.Series, pd.DataFrame, pd.SparseSeries, pd.SparseDataFrame, Series, DataFrame, SparseSeries, SparseDataFrame]
node_color_map = list(zip(node_types, node_colors))
r_node_color_map = {v: '.'.join((k.__module__, k.__name__)) for k, v in node_color_map}
r_edge_color_map = {v: k for k, v in edge_color_map.items()}


class TypedMeta(type):
    '''
    A metaclass for automatically generating properties for statically typed
    class attributes. Useage is the following:

    .. code-block:: Python

        class TestMeta(TypedMeta):
            attr1 = int
            attr2 = DataFrame

        class TestClass(metaclass=TestMeta):
            def __init__(self, attr1, attr2):
                self.attr1 = attr1
                self.attr2 = attr2

    Under the covers, this class creates code that looks like the following:

    .. code-block:: Python

        class TestClass:
            @property
            def attr1(self):
                return self._attr1

            @attr1.setter
            def attr1(self, obj):
                if not isinstance(obj, int):
                    raise TypeError('attr1 must be int')
                self._attr1 = obj

            @attr1.deleter
            def attr1(self):
                del self._attr1

            @property
            def attr2(self):
                return self._attr2

            @attr2.setter
            def attr2(self, obj):
                if not isinstance(obj, DataFrame):
                    raise TypeError('attr2 must be DataFrame')
                self._attr2 = obj

            @attr2.deleter
            def attr2(self):
                del self._attr2

            def __init__(self, attr1, attr2):
                self.attr1 = attr1
                self.attr2 = attr2
    '''
    @staticmethod
    def create_property(name, ptype):
        '''
        Creates a custom property with a getter that performs computing
        functionality (if available) and raise a type error if setting
        with the wrong type.

        Note:
            By default, the setter attempts to convert the object to the
            correct type; a type error is raised if this fails.
        '''
        pname = '_' + name    # This will be where the data is store (e.g. self._name)
        def getter(self):
            '''
            This is the default property "getter" for container data objects.
            If the property value is None, this function will check for a
            convenience method with the signature, self.compute_name() and call
            it prior to returning the property value.
            '''
            if not hasattr(self, pname) and hasattr(self, '{}{}'.format(self._getter_prefix, pname)):
                self['{}{}'.format(self._getter_prefix, pname)]()
            if not hasattr(self, pname):
                raise AttributeError('Please compute or set {} first.'.format(name))
            return getattr(self, pname)

        def setter(self, obj):
            '''
            This is the default property "setter" for container data objects.
            Prior to setting a property value, this function checks that the
            object's type is correct.
            '''
            if not isinstance(obj, ptype):
                try:
                    obj = ptype(obj)
                except:
                    raise TypeError('Object {0} must instance of {1}'.format(name, ptype))
            setattr(self, pname, obj)

        def deleter(self):
            '''Deletes the property's value.'''
            del self[pname]

        return property(getter, setter, deleter)

    def __new__(metacls, name, bases, clsdict):
        '''
        This function modifies container class definitions (the class object
        itself is altered, not instances of the class).
        :func:`~exa.container.TypedMeta.create_property` is called on every
        statically defined class attributed, which creates corresponding
        property defined on the class object.
        '''
        for k, v in metacls.__dict__.items():
            if isinstance(v, type) and k[0] != '_':
                clsdict[k] = metacls.create_property(k, v)
        return super().__new__(metacls, name, bases, clsdict)


class BaseContainer:
    '''
    Base container class responsible for all features related to data
    management; relational features are in :class:`~exa.relational.container.Container`.

    Note:
        Due to the requirements of mixing metaclasses, a metaclass is
        created in :mod:`~exa.relational.container` and assigned to the
        "master" container object, :class:`~exa.relational.container.Container`.
    '''
    _widget_class = ContainerWidget
    _getter_prefix = 'compute'

    def add_data(self, data, field_values=None):
        raise NotImplementedError()

    def copy(self, **kwargs):
        '''
        Create a copy of the current object.
        '''
        cls = self.__class__
        kws = self._rel(copy=True)
        dfs = self._data(copy=True)
        kws.update(dfs)             # We updates kws in this order because we
        kws.update(kwargs)          # want to respect the user's kwargs.
        return cls(**kws)

    def concat(self, *args, **kwargs):
        '''
        Concatenate any number of container objects with the current object into
        a single container object.

        See Also:
            For argument description, see :func:`~exa.container.concat`.
        '''
        raise NotImplementedError()

    def info(self):
        '''
        Display information about the container's objects.

        Note:
            Sizes are reported in bytes.
        '''
        names = []
        types = []
        sizes = []
        names.append('WIDGET')
        types.append('-')
        s = 0
        if self._widget is not None:
            for obj in self._widget._trait_values.values():
                s += getsizeof(obj)
        sizes.append(s)
        names.append('METADATA')
        types.append('-')
        s = 0
        for obj in self._rel().values():
            s += getsizeof(obj)
        sizes.append(s)
        for name, obj in self._data().items():
            names.append(name[1:] if name.startswith('_') else name)
            types.append('.'.join((obj.__module__, obj.__class__.__name__)))
            sizes.append(obj.memory_usage().sum())
        inf = pd.DataFrame.from_dict({'object': names, 'type': types, 'size': sizes})
        inf.set_index('object', inplace=True)
        return inf.sort_index()

    def network(self):
        '''
        Display information about the container's object relationships.
        '''
        def get_color(obj):
            '''Gets the color of a node based on the node's data type.'''
            for k, v in node_color_map:
                if isinstance(obj, k):
                    return v
            return 'gray'

        def legend(items, mapper, title, loc, ax):
            '''Legend creation helper'''
            proxies = []
            descriptions = []
            for k in set(items):
                if title == 'Data Type':
                    line = mpl.sns.mpl.lines.Line2D([], [], linestyle='none', color=k, marker='o')
                else:
                    line = mpl.sns.mpl.lines.Line2D([], [], linestyle='-', color=k)
                proxies.append(line)
                descriptions.append(mapper[k])
            leg = ax.legend(proxies, descriptions, title=title, loc=loc, frameon=True)
            leg_frame = leg.get_frame()
            leg_frame.set_facecolor('white')
            leg_frame.set_edgecolor('black')
            return leg, ax

        inf = self.info()
        inf = inf[inf['type'] != '-']
        nodes = inf.index.values
        node_sizes = inf['size']
        node_sizes *= 13000/node_sizes.max()
        node_sizes += 2000
        node_colors = {}
        edges = {}
        items = self._data().items()
        for k0, v0 in items:
            n0 = k0[1:] if k0.startswith('_') else k0
            node_colors[n0] = get_color(v0)
            for k1, v1 in items:
                if v0 is v1:
                    continue
                n1 = k1[1:] if k1.startswith('_') else k1
                for name in v0.index.names:
                    if name is None:
                        continue
                    if name in v1.index.names:
                        edges[(n0, n1)] = edge_color_map['idx-idx']
                        edges[(n1, n0)] = edge_color_map['idx-idx']
                    for col in v1.columns:
                        if name in col:
                            edges[(n0, n1)] = edge_color_map['idx-col']
                            edges[(n1, n0)] = edge_color_map['idx-col']
        g = nx.Graph()
        g.add_nodes_from(nodes)
        g.add_edges_from(edges.keys())
        node_size = [node_sizes[k] for k in g.nodes()]
        node_color = [node_colors[k] for k in g.nodes()]
        edge_color = [edges[k] for k in g.edges()]
        labels = {k: k for k in g.nodes()}
        fig, ax = mpl.sns.plt.subplots(1, figsize=(13, 8), dpi=300)
        ax.axis('off')
        pos = nx.spring_layout(g)
        f0 = nx.draw_networkx_nodes(g, pos=pos, ax=ax, alpha=0.8, node_size=node_size, node_color=node_color)
        f1 = nx.draw_networkx_labels(g, pos=pos, labels=labels, font_size=15, font_weight='bold', ax=ax)
        f2 = nx.draw_networkx_edges(g, pos=pos, edge_color=edge_color, width=2, ax=ax)
        l1, ax = legend(edge_color, r_edge_color_map, 'Connection', (1, 0), ax)
        l2, ax = legend(node_color, r_node_color_map, 'Data Type', (1, 0.3), ax)
        fig.gca().add_artist(l1)

    @classmethod
    def from_hdf(cls, path):
        '''
        Load a container object from an HDF5 file.

        Args:
            path (str): Full file path to the container hdf5 file.
        '''
        kwargs = {}
        with pd.HDFStore(path) as store:
            for key in store.keys():
                if 'kwargs' in key:
                    kwargs.update(store.get_storer(key).attrs.metadata)
                else:
                    name = str(key[1:])
                    kwargs[name] = store[key]
        # Process any fields
        n = [int(key.split('_')[0].replace('FIELD', '')) for key in kwargs.keys() if 'FIELD' in key]
        if len(n) != 0:
            n = max(n)
            to_del = []
            for i in range(n + 1):
                search = 'FIELD' + str(i)
                names = [key for key in kwargs.keys() if search in key]
                to_del += names
                arg = names[0].replace(search + '_', '').split('/')[0]
                field_values = [kwargs[key] for key in names if 'values' in key]
                dkey = None
                for name in names:
                    if 'data' in name:
                        dkey = name
                field_data = kwargs[dkey]
                kwargs[arg] = field_data
                kwargs[arg + '_values'] = field_values
            for name in to_del:
                del kwargs[name]
        return cls(**kwargs)

    @classmethod
    def load(cls, pkid_or_path=None):
        '''
        Load a container object from a persistent location or file path.

        Args:
            pkid_or_path: Integer pkid corresponding to the container table or file path

        Returns:
            container: The saved container object
        '''
        if isinstance(pkid_or_path, int):
            raise NotImplementedError('Support for persistent storage coming soon...')
        elif isinstance(pkid_or_path, str):
            return cls.from_hdf(pkid_or_path)
        else:
            raise TypeError('The argument should be int or str, not {}.'.format(type(pkid_or_path)))

    def _save_data(self, path=None, typ='hdf5'):
        '''
        Save the dataframe (and related series) data to a standard format
        (currently only HDF5 is supported). This file contains all of the
        data and metadata about the container.

        Args:
            path (str): Filename
            typ (str): Store type ('hdf5', )
        '''
        if typ != 'hdf5':
            raise NotImplementedError('Currently only hdf5 is supported')
        kwargs = self._rel()
        self._save_hdf(path, kwargs)

    def _save_hdf(self, path, kwargs):
        '''
        Save the container to an HDF5 file. Returns the saved file path upon
        completion.
        '''
        # Check the path
        if path is None:
            path = self.hexuid + '.hdf5'
        elif os.path.isdir(path):
            path += os.sep + self.hexuid + '.hdf5'
        elif not (path.endswith('.hdf5') or path.endswith('.hdf')):
            raise ValueError('File path must have a ".hdf5" or ".hdf" extension.')
        with pd.HDFStore(path) as store:
            store['kwargs'] = pd.Series()
            store.get_storer('kwargs').attrs.metadata = kwargs
            fc = 0
            for name, df in self._data().items():
                name = name[1:] if name.startswith('_') else name
                if isinstance(df, Field):
                    df._revert_categories()
                    fname = 'FIELD{}_'.format(fc) + name + '/'
                    store[fname + 'data'] = pd.DataFrame(df)
                    for i, field in enumerate(df.field_values):
                        ffname = fname + 'values' + str(i)
                        if isinstance(field, pd.Series):
                            store[ffname] = pd.Series(field)
                        else:
                            store[ffname] = pd.DataFrame(field)
                    df._set_categories()
                    fc += 1
                elif isinstance(df, Series):
                    store[name] = pd.Series(df)
                elif isinstance(df, SparseDataFrame):
                    store[name] = pd.SparseDataFrame(df)
                elif isinstance(df, DataFrame):
                    df._revert_categories()
                    store[name] = pd.DataFrame(df)
                    df._set_categories()
                else:
                    store[name] = df
        return path

    def _rel(self, copy=False):
        '''
        Get all (propagatable) relational and metadata data of the container.

        Warning:
            This function does not copy primary keys.
        '''
        rel = {}
        for key, obj in self.__dict__.items():
            if not isinstance(obj, (pd.Series, pd.DataFrame)) and not key.startswith('_'):
                if copy:
                    if 'id' not in key:
                        rel[key] = deepcopy(obj)
                else:
                    rel[key] = obj
        return rel

    def _data(self, copy=False):
        '''
        Get all data associated with the container as key value pairs.
        '''
        data = {}
        for key, obj in self.__dict__.items():
            if isinstance(obj, (pd.Series, pd.DataFrame)):
                if copy:
                    data[key] = obj.copy()
                else:
                    data[key] = obj
        return data


    def _custom_app_traits(self):
        raise NotImplementedError('Support for web app not yet implemented')

    def _update_app_traits(self):
        raise NotImplementedError('Support for web app not yet implemented')

    def _custom_widget_traits(self):
        return {}

    def _update_widget_traits(self):
        '''
        Jupyter notebook widgets require data to be available within a
        :class:`~exa.widget.Widget` object. This allows notebook extensions
        (nbextensions - written in JavaScript) to access backend (Python) data
        via `ipywidgets`_.

        .. _ipywidgets: https://ipywidgets.readthedocs.io/en/latest/
        '''
        if self._widget is not None:    # If a corresponding widget exists, build traits
            traits = {}
            if self._test:
                traits['test'] = Bool(True).tag(sync=True)
            else:
                traits['test'] = Bool(False).tag(sync=True)
                traits.update(self._custom_widget_traits())
                for obj in self._data().values():
                    if hasattr(obj, '_traits'):
                        if len(obj._traits) > 0 and len(obj) > 0:
                            traits.update(obj._update_widget_traits())
            self._widget.add_traits(**traits)    # Adding traits to the widget makes
            self._traits_need_update = False     # them accesible from nbextensions (JavaScript).

    def __delitem__(self, key):
        if key in self.__dict__:
            del self.__dict__[key]

    def __init__(self, name=None, description=None, meta=None, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.name = name
        self.description = description
        self.meta = meta
        self._test = False
        self._traits_need_update = True
        self._widget = self._widget_class(self) if global_config['notebook'] else None
        if meta is None and len(kwargs) == 0 and len(self._data()) == 0:
            self._test = True
            self.name = 'TestContainer'

    def _repr_html_(self):
        if self._widget is not None and self._traits_need_update:
            self._update_widget_traits()
        return self._widget._repr_html_()

#    def _slice_with_int_or_string(self, key):
#        '''
#        Slices the current container selecting data that matches the key (either on _groupbys or
#        by row index).
#        '''
#        cls = self.__class__
#        kws = del_keys(self._rel(copy=True))
#        for name, df in self._data(copy=True).items():
#            dfcls = df.__class__
#            if hasattr(df, '_groupbys'):
#                if len(df._groupbys) > 0:
#                    grps = df.groupby(df._groupbys)
#                    selector = sorted(grps.groups.keys())[key]
#                    kws[name] = dfcls(grps.get_group(selector))
#            if name not in kws:
#                selector = None
#                if isinstance(df, pd.SparseDataFrame) or isinstance(df, pd.SparseSeries):
#                    kws[name] = df
#                elif key > len(df.index):
#                    kws[name] = df
#                else:
#                    selector = df.index[key]
#                    kws[name] = dfcls(df.ix[[selector], :])
#        return cls(**kws)
#
#    def _slice_with_list_or_tuple(self, keys):
#        '''
#        Slices the current container selecting data that matches the keys (either on _groupbys or
#        by row index).
#        '''
#        cls = self.__class__
#        kws = del_keys(self._rel(copy=True))
#        for name, df in self._data(copy=True).items():
#            dfcls = df.__class__
#            if hasattr(df, '_groupbys'):
#                if len(df._groupbys) > 0:
#                    grps = df.groupby(df._groupbys)
#                    srtd = sorted(grps.groups.keys())
#                    selector = [srtd[key] for key in keys]
#                    kws[name] = dfcls(pd.concat([grps.get_group(key) for key in selector]))
#            if name not in kws:
#                if isinstance(df, pd.SparseDataFrame) or isinstance(df, pd.SparseSeries):
#                    kws[name] = df
#                elif max(keys) > len(df.index):
#                    kws[name] = df
#                else:
#                    selector = [df.index[key] for key in keys]
#                    kws[name] = dfcls(df.ix[selector, :])
#        return cls(**kws)
#
#    def _slice_with_slice(self, slce):
#        '''
#        Slices the current container selecting data that matches the range given
#        by the slice object.
#        '''
#        cls = self.__class__
#        kws = del_keys(self._rel(copy=True))
#        for name, df in self._data(copy=True).items():
#            dfcls = df.__class__
#            if hasattr(df, '_groupbys'):
#                if len(df._groupbys) > 0:
#                    grps = df.groupby(df._groupbys)
#                    srtd = sorted(grps.groups.keys())
#                    kws[name] = dfcls(pd.concat([grps.get_group(key) for key in srtd[slce]]))
#            if name not in kws:
#                if isinstance(df, pd.SparseDataFrame) or isinstance(df, pd.SparseSeries):
#                    kws[name] = df
#                elif slce == slice(None):
#                    kws[name] = df
#                else:
#                    keys = df.index.values[slce]
#                    kws[name] = dfcls(df.iloc[keys, :])
#        return cls(**kws)
#
#    def __getitem__(self, key):
#        '''
#        Containers can be sliced in a number of different ways and the slicing
#        of the data values depends on the characteristics of the individual
#        data objects (i.e. presence of _groupbys).
#        '''
#        if isinstance(key, int):
#            return self._slice_with_int_or_string(key)
#        elif isinstance(key, str) and not hasattr(self, key):
#            return self._slice_with_int_or_string(key)
#        elif isinstance(key, list) or isinstance(key, tuple):
#            return self._slice_with_list_or_tuple(key)
#        elif isinstance(key, slice):
#            return self._slice_with_slice(key)
#        elif hasattr(self, key):
#            return getattr(self, key)
#        else:
#            raise KeyError('No selection method for key {} of type {}'.format(key, type(key)))
